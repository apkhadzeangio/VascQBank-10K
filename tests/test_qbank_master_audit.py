"""Unit tests for unified master QBank builder, revision overlay, and clinical audit validator."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_master_qbank import build_master, git_blob_sha, pair_fingerprint, verify_master
from validate_clinical_audit import validate_audit

TARGETS = {
    "PAD_CLTI": 1500, "ALI": 900, "AAA_EVAR": 1200, "THORACIC_AORTA": 700,
    "CAROTID_VERTEBRAL": 900, "VENOUS": 900, "DIALYSIS_ACCESS": 650,
    "MESENTERIC_RENAL": 600, "VASCULAR_TRAUMA": 650, "VGEI": 500,
    "ANATOMY_IMAGING": 900, "PERIOPERATIVE": 600,
}


class MasterAndAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

        agents = "# AGENTS\n| Code | Topic | Target |\n|---|---|---|\n"
        for topic, target in TARGETS.items():
            agents += f"| {topic} | Example | {target} |\n"
        (self.root / "AGENTS.md").write_text(agents, encoding="utf-8")

        qa_dir = self.root / "QA"
        qa_dir.mkdir(parents=True, exist_ok=True)
        batch_rows = []
        for idx, topic in enumerate(TARGETS, start=1):
            # Include intentional internal blank lines on topic 2 to test normalization
            sep = "\n\n" if idx == 2 else "\n"
            q = (
                f"1. უნიკალური კლინიკური შემთხვევა თემაზე {topic} #{idx}?{sep}"
                "ა) პირველი ვარიანტი\n"
                "*ბ) მეორე ვარიანტი\n"
                "გ) მესამე ვარიანტი\n"
                "დ) მეოთხე ვარიანტი\n"
                "ე) მეხუთე ვარიანტი\n"
            )
            e = f"1. ბ) პირველი წინადადება {topic}-ზე. მეორე წინადადება.\n"
            qp = self.root / f"{topic}_questions.txt"
            ep = self.root / f"{topic}_explanations.txt"
            qp.write_text(q, encoding="utf-8")
            ep.write_text(e, encoding="utf-8")
            batch_rows.append(
                {
                    "batch_id": f"{topic}-0001-0001",
                    "priority": "P0",
                    "topic": topic,
                    "first_question": 1,
                    "last_question": 1,
                    "expected_count": 1,
                    "source_question_blob_sha": git_blob_sha(qp.read_bytes()),
                    "auto_structural": "PASS",
                    "clinical_review": "NOT_STARTED",
                    "medical_verification": "NOT_STARTED",
                    "language_review": "NOT_STARTED",
                    "duplicate_review": "NOT_STARTED",
                    "human_approval": "NOT_STARTED",
                    "reviewed_count": 0,
                    "approved_count": 0,
                    "review_commit": "",
                }
            )

        with (qa_dir / "CLINICAL_REVIEW_BATCHES.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(batch_rows[0].keys()))
            writer.writeheader()
            writer.writerows(batch_rows)

    def _make_decision_record(self, topic="ALI", number=1, **overrides):
        qp = self.root / f"{topic}_questions.txt"
        ep = self.root / f"{topic}_explanations.txt"
        q_raw, e_raw = qp.read_bytes(), ep.read_bytes()
        rec = {
            "source_snapshot_sha": "9dd030de5d3be2b75226b58c78e7f77e56f1774b",
            "question_blob_sha": git_blob_sha(q_raw),
            "explanation_blob_sha": git_blob_sha(e_raw),
            "topic": topic,
            "number": number,
            "source_text_fingerprint": pair_fingerprint(
                q_raw.decode("utf-8"), e_raw.decode("utf-8")
            ),
            "clinical_verdict": "PASS",
            "answer_key_verdict": "PASS",
            "explanation_verdict": "PASS",
            "language_verdict": "PASS",
            "duplicate_candidates": [],
            "evidence": [
                {
                    "title": "ESVS 2020 Acute Limb Ischaemia Guidelines",
                    "year": 2020,
                    "url_or_doi": "https://doi.org/10.1016/j.ejvs.2019.09.006",
                    "accessed_at": "2026-11-20",
                }
            ],
            "severity": "NONE",
            "proposed_revision": None,
            "independent_review_status": "EVIDENCE_VERIFIED",
            "human_reviewer": None,
            "human_approval_at": None,
        }
        rec.update(overrides)
        return rec

    def _update_batch_csv(self, batch_id, **updates):
        csv_path = self.root / "QA" / "CLINICAL_REVIEW_BATCHES.csv"
        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        for r in rows:
            if r["batch_id"] == batch_id:
                for k, v in updates.items():
                    r[k] = str(v)
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def test_build_and_verify_master(self):
        out = self.root / "MASTER"
        manifest = build_master(self.root, out, allow_partial=True)
        self.assertEqual(manifest["total_questions"], 12)
        self.assertEqual(manifest["normalized_internal_blank_lines_count"], 1)
        ver = verify_master(self.root, out, expected_total=12)
        self.assertTrue(ver["verified"])

    def test_audit_validator_blocks_ai_human_approved(self):
        batch_dir = self.root / "QA" / "CLINICAL_BATCHES" / "ALI-0001-0001"
        batch_dir.mkdir(parents=True)
        bad_rec = self._make_decision_record(
            independent_review_status="HUMAN_APPROVED",
            human_reviewer=None,
            human_approval_at=None,
        )
        (batch_dir / "decisions.jsonl").write_text(
            json.dumps(bad_rec, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self._update_batch_csv("ALI-0001-0001", clinical_review="IN_PROGRESS", reviewed_count=1)
        report = validate_audit(self.root, allow_partial_source=True)
        self.assertFalse(report["valid"])
        self.assertTrue(any("HUMAN_APPROVED forbidden" in e for e in report["errors"]))

    def test_valid_human_approved_overlay_compiles_release(self):
        batch_dir = self.root / "QA" / "CLINICAL_BATCHES" / "ALI-0001-0001"
        batch_dir.mkdir(parents=True)
        rev_q = (
            "1. განახლებული კლინიკური შემთხვევა თემაზე ALI?\n"
            "ა) პირველი ვარიანტი\n"
            "ბ) მეორე ვარიანტი\n"
            "*გ) განახლებული სწორი ვარიანტი\n"
            "დ) მეოთხე ვარიანტი\n"
            "ე) მეხუთე ვარიანტი"
        )
        rev_e = "1. გ) განახლებული პირველი წინადადება. განახლებული მეორე წინადადება."
        good_rec = self._make_decision_record(
            independent_review_status="HUMAN_APPROVED",
            human_reviewer="Dr. Reviewer",
            human_approval_at="2026-11-20T10:00:00+04:00",
            proposed_revision={"question": rev_q, "explanation": rev_e},
        )
        (batch_dir / "decisions.jsonl").write_text(
            json.dumps(good_rec, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self._update_batch_csv(
            "ALI-0001-0001",
            clinical_review="COMPLETE",
            reviewed_count=1,
            approved_count=1,
        )
        audit_report = validate_audit(self.root, allow_partial_source=True)
        self.assertTrue(audit_report["valid"], audit_report["errors"])

        release_dir = self.root / "RELEASE"
        manifest = build_master(
            self.root,
            release_dir,
            allow_partial=True,
            overlay_batches_dir=self.root / "QA" / "CLINICAL_BATCHES",
        )
        self.assertEqual(manifest["applied_human_approved_overlays"], 1)
        ver = verify_master(self.root, release_dir, expected_total=12)
        self.assertTrue(ver["verified"])
        # Global #2 corresponds to ALI #1 in AGENTS.md order
        all_q = (release_dir / "VascQBank_10K_ALL_QUESTIONS.txt").read_text(encoding="utf-8")
        self.assertIn("2. განახლებული კლინიკური შემთხვევა თემაზე ALI?", all_q)


if __name__ == "__main__":
    unittest.main()
