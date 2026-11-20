#!/usr/bin/env python3
"""Deterministic validator for VascQBank-10K 55-batch clinical audit records."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from build_master_qbank import (
    EXPLANATION_RE,
    LETTERS,
    OPTION_RE,
    QUESTION_RE,
    git_blob_sha,
    pair_fingerprint,
    split_blocks,
)

VALID_STATUSES = {
    "NOT_STARTED",
    "AI_SCREENED",
    "EVIDENCE_VERIFIED",
    "NEEDS_REVISION",
    "DUPLICATE_CANDIDATE",
    "ADJUDICATION_REQUIRED",
    "HUMAN_APPROVED",
    "REJECTED",
}
VALID_SEVERITIES = {"NONE", "P2/MINOR", "P1/MAJOR", "P0/CRITICAL", "REVIEW_REQUIRED"}
REQUIRED_RECORD_FIELDS = {
    "source_snapshot_sha",
    "question_blob_sha",
    "explanation_blob_sha",
    "topic",
    "number",
    "source_text_fingerprint",
    "clinical_verdict",
    "answer_key_verdict",
    "explanation_verdict",
    "language_verdict",
    "duplicate_candidates",
    "evidence",
    "severity",
    "proposed_revision",
    "independent_review_status",
    "human_reviewer",
    "human_approval_at",
}


def validate_proposed_revision(rev: dict, ctx: str) -> list[str]:
    errs: list[str] = []
    q_txt = (rev.get("question") or "").strip()
    e_txt = (rev.get("explanation") or "").strip()
    if not q_txt or not e_txt:
        return [f"{ctx}: proposed_revision must include non-empty 'question' and 'explanation'"]

    lines = [ln.strip() for ln in q_txt.splitlines() if ln.strip()]
    if len(lines) != 6 or not QUESTION_RE.match(lines[0]):
        errs.append(f"{ctx}: proposed_revision.question must have 1 numbered stem + 5 options")
        return errs

    opts = [OPTION_RE.match(ln) for ln in lines[1:]]
    if any(m is None for m in opts) or [m.group(2) for m in opts if m] != list(LETTERS):
        errs.append(f"{ctx}: proposed_revision.question options must be ა)–ე) in order")
        return errs
    marked = [m.group(2) for m in opts if m and m.group(1) == "*"]
    if len(marked) != 1:
        errs.append(f"{ctx}: proposed_revision.question must mark exactly one * option")
        return errs

    em = EXPLANATION_RE.match(e_txt)
    if em is None or "\n" in e_txt:
        errs.append(f"{ctx}: proposed_revision.explanation must be single-line 'N. ა) ...'")
        return errs
    if em.group(2) != marked[0]:
        errs.append(
            f"{ctx}: proposed_revision answer mismatch (Q={marked[0]} vs E={em.group(2)})"
        )
    prose = em.group(3).strip()
    if re.search(r"(?<!\w)[აბგდე]\)", prose):
        errs.append(f"{ctx}: proposed_revision.explanation must not evaluate distractors")
    return errs


def validate_audit(root: Path, *, allow_partial_source: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    batches_csv = root / "QA" / "CLINICAL_REVIEW_BATCHES.csv"
    if not batches_csv.exists():
        return {
            "valid": False,
            "errors": ["Missing QA/CLINICAL_REVIEW_BATCHES.csv"],
            "warnings": [],
        }

    with batches_csv.open("r", encoding="utf-8", newline="") as fh:
        batch_rows = list(csv.DictReader(fh))

    expected_sum = sum(int(r["expected_count"]) for r in batch_rows)
    if not allow_partial_source and (len(batch_rows) != 55 or expected_sum != 10000):
        errors.append(
            f"Expected 55 batches summing to 10,000; found {len(batch_rows)} summing to {expected_sum}"
        )

    # Cache source blob SHAs and per-question fingerprints
    topic_cache: dict[str, dict] = {}
    for topic in sorted({r["topic"].strip() for r in batch_rows}):
        qp = root / f"{topic}_questions.txt"
        ep = root / f"{topic}_explanations.txt"
        if not qp.exists() or not ep.exists():
            errors.append(f"Missing source TXT files for {topic}")
            continue
        q_raw, e_raw = qp.read_bytes(), ep.read_bytes()
        _, q_blocks = split_blocks(q_raw.decode("utf-8-sig"), QUESTION_RE)
        _, e_blocks = split_blocks(e_raw.decode("utf-8-sig"), EXPLANATION_RE)
        fps = {
            qn: pair_fingerprint(qb, eb)
            for (qn, qb), (en, eb) in zip(q_blocks, e_blocks)
            if qn == en
        }
        topic_cache[topic] = {
            "q_sha": git_blob_sha(q_raw),
            "e_sha": git_blob_sha(e_raw),
            "fingerprints": fps,
        }

    status_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    total_decided = 0
    batches_dir = root / "QA" / "CLINICAL_BATCHES"

    for row in batch_rows:
        batch_id = row["batch_id"].strip()
        topic = row["topic"].strip()
        first_q = int(row["first_question"])
        last_q = int(row["last_question"])
        expected_count = int(row["expected_count"])
        csv_reviewed = int(row["reviewed_count"])
        csv_approved = int(row["approved_count"])

        if last_q - first_q + 1 != expected_count:
            errors.append(f"{batch_id}: range {first_q}..{last_q} != expected_count {expected_count}")

        tinfo = topic_cache.get(topic)
        if not tinfo:
            continue
        if row["source_question_blob_sha"].strip() != tinfo["q_sha"]:
            errors.append(
                f"{batch_id}: CSV source_question_blob_sha != actual {topic}_questions.txt blob SHA"
            )

        decisions_path = batches_dir / batch_id / "decisions.jsonl"
        if not decisions_path.exists():
            if csv_reviewed != 0 or row["clinical_review"].strip() not in {"NOT_STARTED", ""}:
                errors.append(
                    f"{batch_id}: CSV indicates progress ({csv_reviewed}), but {decisions_path} is missing"
                )
            continue

        seen_nums: set[int] = set()
        batch_human_approved = 0
        for line_no, line in enumerate(
            decisions_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            ctx = f"{batch_id}:{line_no}"
            try:
                rec = json.loads(line)
            except ValueError as exc:
                errors.append(f"{ctx}: invalid JSON ({exc})")
                continue

            missing = REQUIRED_RECORD_FIELDS - set(rec.keys())
            if missing:
                errors.append(f"{ctx}: missing fields {sorted(missing)}")
                continue

            qnum = int(rec["number"])
            if rec["topic"] != topic or not (first_q <= qnum <= last_q):
                errors.append(f"{ctx}: {rec['topic']}#{qnum} outside batch {topic} {first_q}..{last_q}")
                continue
            if qnum in seen_nums:
                errors.append(f"{ctx}: duplicate decision for #{qnum}")
                continue
            seen_nums.add(qnum)

            if rec["question_blob_sha"] != tinfo["q_sha"]:
                errors.append(f"{ctx}: question_blob_sha mismatch vs source")
            if rec["explanation_blob_sha"] != tinfo["e_sha"]:
                errors.append(f"{ctx}: explanation_blob_sha mismatch vs source")
            if rec["source_text_fingerprint"] != tinfo["fingerprints"].get(qnum):
                errors.append(f"{ctx}: source_text_fingerprint mismatch for {topic}#{qnum}")

            status = rec["independent_review_status"]
            if status not in VALID_STATUSES:
                errors.append(f"{ctx}: invalid independent_review_status {status!r}")
            status_counts[status] += 1

            sev = rec["severity"]
            if sev not in VALID_SEVERITIES:
                errors.append(f"{ctx}: invalid severity {sev!r}")
            severity_counts[sev] += 1

            if status == "HUMAN_APPROVED":
                if not rec.get("human_reviewer") or not rec.get("human_approval_at"):
                    errors.append(
                        f"{ctx}: HUMAN_APPROVED forbidden without human_reviewer and human_approval_at"
                    )
                else:
                    batch_human_approved += 1

            if status in {"EVIDENCE_VERIFIED", "HUMAN_APPROVED"}:
                ev = rec.get("evidence")
                if not isinstance(ev, list) or not ev:
                    errors.append(f"{ctx}: {status} requires non-empty evidence list")

            if rec.get("proposed_revision") is not None:
                errors.extend(validate_proposed_revision(rec["proposed_revision"], ctx))
            elif status == "NEEDS_REVISION":
                warnings.append(f"{ctx}: status is NEEDS_REVISION without proposed_revision draft")

        total_decided += len(seen_nums)
        if csv_reviewed != len(seen_nums):
            errors.append(
                f"{batch_id}: CSV reviewed_count={csv_reviewed} != JSONL records={len(seen_nums)}"
            )
        if csv_approved != batch_human_approved:
            errors.append(
                f"{batch_id}: CSV approved_count={csv_approved} != HUMAN_APPROVED={batch_human_approved}"
            )
        if row["clinical_review"].strip() == "COMPLETE" and len(seen_nums) != expected_count:
            errors.append(
                f"{batch_id}: marked COMPLETE with {len(seen_nums)}/{expected_count} records"
            )

    return {
        "valid": len(errors) == 0,
        "batches_total": len(batch_rows),
        "questions_expected": expected_sum,
        "decisions_recorded": total_decided,
        "status_counts": dict(status_counts),
        "severity_counts": dict(severity_counts),
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    report = validate_audit(args.root.resolve())
    if args.json_out:
        args.json_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "valid": report["valid"],
                "batches_total": report["batches_total"],
                "questions_expected": report["questions_expected"],
                "decisions_recorded": report["decisions_recorded"],
                "status_counts": report["status_counts"],
                "errors_count": report["errors_count"],
                "warnings_count": report["warnings_count"],
            },
            ensure_ascii=False,
        )
    )
    for err in report["errors"][:25]:
        print("ERROR:", err)
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
