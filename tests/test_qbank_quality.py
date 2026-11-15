"""Synthetic positive and intentionally damaged fixtures for the quality gate."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qbank_quality import git_blob_sha, validate_repository

TARGETS = {
    "PAD_CLTI": 1500, "ALI": 900, "AAA_EVAR": 1200, "THORACIC_AORTA": 700,
    "CAROTID_VERTEBRAL": 900, "VENOUS": 900, "DIALYSIS_ACCESS": 650,
    "MESENTERIC_RENAL": 600, "VASCULAR_TRAUMA": 650, "VGEI": 500,
    "ANATOMY_IMAGING": 900, "PERIOPERATIVE": 600,
}


class QBankQualityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        agents = "# AGENTS\n| Code | Topic | Target |\n|---|---|---|\n"
        for topic, target in TARGETS.items():
            agents += f"| {topic} | Example | {target} |\n"
        (self.root / "AGENTS.md").write_text(agents, encoding="utf-8")
        (self.root / "GLOSSARY.md").write_text("# Glossary\n", encoding="utf-8")
        idx = dict(source_sha={f: git_blob_sha((self.root / p).read_bytes())
                               for f, p in (("agents_md", "AGENTS.md"),
                                            ("glossary_md", "GLOSSARY.md"))},
                   topics={})
        for i, topic in enumerate(TARGETS):
            q = (f"1. უნიკალური კლინიკური კითხვა {i + 1}?\n"
                 "ა) პირველი არჩევანი\n*ბ) მეორე არჩევანი\nგ) მესამე არჩევანი\n"
                 "დ) მეოთხე არჩევანი\nე) მეხუთე არჩევანი\n")
            e = "1. ბ) პირველი განმარტებითი წინადადება. მეორე განმარტებითი წინადადება.\n"
            (self.root / f"{topic}_questions.txt").write_text(q, encoding="utf-8")
            (self.root / f"{topic}_explanations.txt").write_text(e, encoding="utf-8")
            idx["topics"][topic] = {
                "last_number": 1,
                "question_blob_sha": git_blob_sha(q.encode()),
                "explanation_blob_sha": git_blob_sha(e.encode()),
            }
        (self.root / "AUTOMATION_CONTEXT.json").write_text(
            json.dumps(idx, ensure_ascii=False), encoding="utf-8")

    def codes(self):
        return {f["code"] for f in validate_repository(self.root)["findings"]
                if f["level"] == "error"}

    def test_valid_baseline(self):
        report = validate_repository(self.root)
        self.assertEqual(report["summary"]["errors"], 0, report["findings"])
        self.assertEqual(report["summary"]["questions"], 12)

    def test_missing_option(self):
        p = self.root / "ALI_questions.txt"
        p.write_text(p.read_text().replace("ე) მეხუთე არჩევანი\n", ""), encoding="utf-8")
        self.assertIn("OPTION_COUNT", self.codes())

    def test_answer_mismatch(self):
        p = self.root / "ALI_explanations.txt"
        p.write_text(p.read_text().replace("1. ბ)", "1. გ)"), encoding="utf-8")
        self.assertIn("ANSWER_MISMATCH", self.codes())

    def test_index_staleness(self):
        p = self.root / "ALI_questions.txt"
        p.write_text(p.read_text() + "\n", encoding="utf-8")
        self.assertIn("INDEX_MISMATCH", self.codes())

    def test_duplicate_question_number(self):
        p = self.root / "ALI_questions.txt"
        p.write_text(p.read_text() + "\n" + p.read_text(), encoding="utf-8")
        self.assertIn("QUESTION_SEQUENCE", self.codes())

    def test_duplicate_text_across_topics(self):
        p = self.root / "ALI_questions.txt"
        q = (self.root / "VENOUS_questions.txt").read_text()
        p.write_text(q, encoding="utf-8")
        self.assertIn("DUPLICATE_STEM", self.codes())

    def test_sentence_warning_does_not_fail(self):
        p = self.root / "ALI_explanations.txt"
        p.write_text("1. ბ) ერთი წინადადება.\n", encoding="utf-8")
        report = validate_repository(self.root)
        self.assertIn("SENTENCE_REVIEW", {f["code"] for f in report["findings"]})
        self.assertTrue(any(f["level"] == "warning" for f in report["findings"]))


if __name__ == "__main__":
    unittest.main()
