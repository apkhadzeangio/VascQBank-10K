#!/usr/bin/env python3
"""Build and verify unified 10,000-item VascQBank master files without modifying source TXT files.

Supports:
- Default mode: consolidates the 24 read-only <TOPIC>_questions.txt / <TOPIC>_explanations.txt into MASTER/.
- --overlay-revisions <dir>: overlays HUMAN_APPROVED revisions from QA/CLINICAL_BATCHES/*/decisions.jsonl
  into a separate target directory (e.g., RELEASE/) once clinical sign-off is complete.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

LETTERS = "აბგდე"
QUESTION_RE = re.compile(r"(?m)^(\d+)\.\s+")
OPTION_RE = re.compile(r"^(\*?)([აბგდე])\)\s+(.+)$")
EXPLANATION_RE = re.compile(r"(?m)^(\d+)\.\s*([აბგდე])\)\s*(.+)$")
TOPIC_ROW_RE = re.compile(r"^\|\s*([A-Z][A-Z_]+)\s*\|[^|]+\|\s*([\d,]+)\s*\|", re.M)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalize_source_text(text: str) -> str:
    cleaned = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n")).strip()
    return "\n".join(line.rstrip() for line in cleaned.split("\n"))


def pair_fingerprint(q_block: str, e_block: str) -> str:
    payload = json.dumps(
        {
            "question": normalize_source_text(q_block),
            "explanation": normalize_source_text(e_block),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def split_blocks(text: str, pattern: re.Pattern[str]) -> tuple[str, list[tuple[int, str]]]:
    matches = list(pattern.finditer(text))
    prefix = text[:matches[0].start()].strip() if matches else text.strip()
    blocks = [
        (
            int(m.group(1)),
            text[m.start():matches[i + 1].start()].strip()
            if i + 1 < len(matches)
            else text[m.start():].strip(),
        )
        for i, m in enumerate(matches)
    ]
    return prefix, blocks


def load_batch_lookup(root: Path) -> dict[tuple[str, int], tuple[str, str]]:
    csv_path = root / "QA" / "CLINICAL_REVIEW_BATCHES.csv"
    lookup: dict[tuple[str, int], tuple[str, str]] = {}
    if not csv_path.exists():
        return lookup
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            topic = row["topic"].strip()
            first_q = int(row["first_question"])
            last_q = int(row["last_question"])
            batch_id = row["batch_id"].strip()
            priority = row["priority"].strip()
            for qnum in range(first_q, last_q + 1):
                lookup[(topic, qnum)] = (batch_id, priority)
    return lookup


def load_approved_overlays(batches_dir: Path) -> dict[tuple[str, int], dict]:
    overlays: dict[tuple[str, int], dict] = {}
    if not batches_dir.exists():
        return overlays
    for jsonl_path in sorted(batches_dir.glob("*/decisions.jsonl")):
        for line_no, line in enumerate(jsonl_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("independent_review_status") != "HUMAN_APPROVED":
                continue
            if not rec.get("human_reviewer") or not rec.get("human_approval_at"):
                raise ValueError(
                    f"{jsonl_path}:{line_no}: HUMAN_APPROVED requires human_reviewer and human_approval_at"
                )
            rev = rec.get("proposed_revision")
            if rev and rev.get("question") and rev.get("explanation"):
                key = (rec["topic"], int(rec["number"]))
                if key in overlays:
                    raise ValueError(f"Duplicate overlay decision for {key}")
                overlays[key] = {
                    "source_text_fingerprint": rec["source_text_fingerprint"],
                    "question": rev["question"],
                    "explanation": rev["explanation"],
                    "human_reviewer": rec["human_reviewer"],
                    "human_approval_at": rec["human_approval_at"],
                }
    return overlays


def git_head_sha(root: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def build_master(
    root: Path,
    out_dir: Path,
    *,
    allow_partial: bool = False,
    overlay_batches_dir: Path | None = None,
) -> dict:
    agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
    topics = [
        (m.group(1), int(m.group(2).replace(",", "")))
        for m in TOPIC_ROW_RE.finditer(agents_text)
    ]
    if len(topics) != 12 or (not allow_partial and sum(target for _, target in topics) != 10000):
        raise ValueError(f"Expected 12 topics totalling 10,000 in AGENTS.md; got {topics}")

    batch_lookup = load_batch_lookup(root)
    overlays = load_approved_overlays(overlay_batches_dir) if overlay_batches_dir else {}
    applied_overlays = 0

    unified_questions: list[str] = []
    unified_explanations: list[str] = []
    crosswalk_rows: list[dict[str, str | int]] = []
    topic_manifest: list[dict] = []
    seen_stems: dict[str, tuple[str, int]] = {}
    internal_blank_line_items: list[str] = []
    answer_counts: Counter[str] = Counter()

    global_num = 0
    for topic, target in topics:
        q_path = root / f"{topic}_questions.txt"
        e_path = root / f"{topic}_explanations.txt"
        if not q_path.exists() or not e_path.exists():
            raise FileNotFoundError(f"Missing source TXT file for {topic}")

        q_raw = q_path.read_bytes()
        e_raw = e_path.read_bytes()
        q_text = q_raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        e_text = e_raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")

        q_prefix, q_blocks = split_blocks(q_text, QUESTION_RE)
        e_prefix, e_blocks = split_blocks(e_text, EXPLANATION_RE)
        if q_prefix or e_prefix:
            raise ValueError(f"Unexpected prefix before item 1 in {topic}")
        if len(q_blocks) != len(e_blocks):
            raise ValueError(f"{topic}: mismatched Q ({len(q_blocks)}) vs E ({len(e_blocks)})")
        if not allow_partial and len(q_blocks) != target:
            raise ValueError(f"{topic}: expected {target} pairs, got {len(q_blocks)}")

        global_start = global_num + 1
        for expected_local, ((q_num, q_block), (e_num, e_block)) in enumerate(
            zip(q_blocks, e_blocks), start=1
        ):
            if q_num != expected_local or e_num != expected_local:
                raise ValueError(
                    f"{topic}: sequence mismatch at {expected_local} (Q={q_num}, E={e_num})"
                )

            src_fp = pair_fingerprint(q_block, e_block)
            active_q = q_block
            active_e = e_block
            if (topic, q_num) in overlays:
                ov = overlays[(topic, q_num)]
                if ov["source_text_fingerprint"] != src_fp:
                    raise ValueError(
                        f"Overlay fingerprint mismatch for {topic}#{q_num}: "
                        f"{ov['source_text_fingerprint']} != {src_fp}"
                    )
                active_q = ov["question"]
                active_e = ov["explanation"]
                applied_overlays += 1

            raw_lines = active_q.splitlines()
            if any(not ln.strip() for ln in raw_lines):
                internal_blank_line_items.append(f"{topic}#{q_num}")
            nonempty_lines = [ln.strip() for ln in raw_lines if ln.strip()]
            if len(nonempty_lines) != 6:
                raise ValueError(
                    f"{topic}#{q_num}: expected 1 stem + 5 option lines, got {len(nonempty_lines)}"
                )

            stem_line = QUESTION_RE.sub("", nonempty_lines[0], count=1).strip()
            norm_stem = re.sub(r"\s+", " ", stem_line).casefold()
            if norm_stem in seen_stems:
                prev_topic, prev_num = seen_stems[norm_stem]
                raise ValueError(
                    f"Duplicate normalized stem: {topic}#{q_num} == {prev_topic}#{prev_num}"
                )
            seen_stems[norm_stem] = (topic, q_num)

            parsed_opts = [OPTION_RE.match(ln) for ln in nonempty_lines[1:]]
            if any(m is None for m in parsed_opts):
                raise ValueError(f"{topic}#{q_num}: malformed option line")
            letters = [m.group(2) for m in parsed_opts if m is not None]
            if letters != list(LETTERS):
                raise ValueError(f"{topic}#{q_num}: invalid option letters {letters}")
            marked = [m.group(2) for m in parsed_opts if m is not None and m.group(1) == "*"]
            if len(marked) != 1:
                raise ValueError(f"{topic}#{q_num}: expected 1 marked option, found {len(marked)}")
            correct_letter = marked[0]

            e_clean = active_e.strip()
            e_match = EXPLANATION_RE.match(e_clean)
            if e_match is None or "\n" in e_clean:
                raise ValueError(f"{topic}#{e_num}: malformed explanation block")
            e_letter, e_prose = e_match.group(2), e_match.group(3).strip()
            if e_letter != correct_letter:
                raise ValueError(
                    f"{topic}#{q_num}: Q marks {correct_letter}) vs E {e_letter})"
                )

            global_num += 1
            answer_counts[correct_letter] += 1

            rebuilt_q = "\n".join([f"{global_num}. {stem_line}"] + nonempty_lines[1:])
            rebuilt_e = f"{global_num}. {e_letter}) {e_prose}"
            unified_questions.append(rebuilt_q)
            unified_explanations.append(rebuilt_e)

            batch_id, priority = batch_lookup.get((topic, q_num), ("", ""))
            crosswalk_rows.append(
                {
                    "global_number": global_num,
                    "topic": topic,
                    "topic_number": q_num,
                    "batch_id": batch_id,
                    "priority": priority,
                    "correct_letter": correct_letter,
                    "question_sha256": sha256_bytes(
                        normalize_source_text(active_q).encode("utf-8")
                    ),
                    "explanation_sha256": sha256_bytes(
                        normalize_source_text(active_e).encode("utf-8")
                    ),
                    "source_pair_sha256": src_fp,
                }
            )

        topic_manifest.append(
            {
                "topic": topic,
                "count": len(q_blocks),
                "target": target,
                "global_start": global_start,
                "global_end": global_num,
                "source_question_file": q_path.name,
                "source_explanation_file": e_path.name,
                "source_question_blob_sha": git_blob_sha(q_raw),
                "source_explanation_blob_sha": git_blob_sha(e_raw),
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    q_out = out_dir / "VascQBank_10K_ALL_QUESTIONS.txt"
    e_out = out_dir / "VascQBank_10K_ALL_EXPLANATIONS.txt"
    csv_out = out_dir / "VascQBank_10K_CROSSWALK.csv"
    manifest_out = out_dir / "VascQBank_10K_MANIFEST.json"

    q_bytes = ("\n\n".join(unified_questions) + "\n").encode("utf-8")
    e_bytes = ("\n\n".join(unified_explanations) + "\n").encode("utf-8")
    q_out.write_bytes(q_bytes)
    e_out.write_bytes(e_bytes)

    with csv_out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "global_number",
                "topic",
                "topic_number",
                "batch_id",
                "priority",
                "correct_letter",
                "question_sha256",
                "explanation_sha256",
                "source_pair_sha256",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(crosswalk_rows)

    csv_bytes = csv_out.read_bytes()

    def rel_or_str(p: Path) -> str:
        try:
            return str(p.relative_to(root))
        except ValueError:
            return str(p)

    manifest = {
        "schema_version": 1,
        "source_head_commit": git_head_sha(root),
        "total_questions": global_num,
        "total_explanations": len(unified_explanations),
        "applied_human_approved_overlays": applied_overlays,
        "answer_distribution": {ch: answer_counts[ch] for ch in LETTERS},
        "normalized_internal_blank_lines_count": len(internal_blank_line_items),
        "normalized_internal_blank_lines_items": internal_blank_line_items,
        "outputs": {
            "questions_file": rel_or_str(q_out),
            "questions_bytes": len(q_bytes),
            "questions_git_blob_sha": git_blob_sha(q_bytes),
            "questions_sha256": sha256_bytes(q_bytes),
            "explanations_file": rel_or_str(e_out),
            "explanations_bytes": len(e_bytes),
            "explanations_git_blob_sha": git_blob_sha(e_bytes),
            "explanations_sha256": sha256_bytes(e_bytes),
            "crosswalk_file": rel_or_str(csv_out),
            "crosswalk_bytes": len(csv_bytes),
            "crosswalk_git_blob_sha": git_blob_sha(csv_bytes),
            "crosswalk_sha256": sha256_bytes(csv_bytes),
        },
        "topics": topic_manifest,
    }
    manifest_out.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def verify_master(root: Path, out_dir: Path, expected_total: int | None = None) -> dict:
    q_out = out_dir / "VascQBank_10K_ALL_QUESTIONS.txt"
    e_out = out_dir / "VascQBank_10K_ALL_EXPLANATIONS.txt"
    csv_out = out_dir / "VascQBank_10K_CROSSWALK.csv"
    manifest_out = out_dir / "VascQBank_10K_MANIFEST.json"

    manifest = json.loads(manifest_out.read_text(encoding="utf-8"))
    if expected_total is None:
        expected_total = manifest["total_questions"]

    q_raw = q_out.read_bytes()
    e_raw = e_out.read_bytes()
    csv_raw = csv_out.read_bytes()

    assert sha256_bytes(q_raw) == manifest["outputs"]["questions_sha256"]
    assert sha256_bytes(e_raw) == manifest["outputs"]["explanations_sha256"]
    assert sha256_bytes(csv_raw) == manifest["outputs"]["crosswalk_sha256"]

    q_prefix, q_blocks = split_blocks(q_raw.decode("utf-8"), QUESTION_RE)
    e_prefix, e_blocks = split_blocks(e_raw.decode("utf-8"), EXPLANATION_RE)
    assert not q_prefix and not e_prefix
    assert len(q_blocks) == expected_total == len(e_blocks)

    with csv_out.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == expected_total

    for idx, ((qn, qblk), (en, eblk), row) in enumerate(
        zip(q_blocks, e_blocks, rows), start=1
    ):
        assert qn == idx == en == int(row["global_number"])
        lines = qblk.splitlines()
        assert len(lines) == 6, f"Global #{idx} does not have 6 unbroken lines"
        opts = [OPTION_RE.match(ln) for ln in lines[1:]]
        assert all(m is not None for m in opts)
        assert [m.group(2) for m in opts if m] == list(LETTERS)
        corr = [m.group(2) for m in opts if m and m.group(1) == "*"]
        assert len(corr) == 1
        em = EXPLANATION_RE.match(eblk)
        assert em is not None and "\n" not in eblk
        assert em.group(2) == corr[0] == row["correct_letter"]

    for tmeta in manifest["topics"]:
        src_q = (root / tmeta["source_question_file"]).read_bytes()
        src_e = (root / tmeta["source_explanation_file"]).read_bytes()
        assert git_blob_sha(src_q) == tmeta["source_question_blob_sha"]
        assert git_blob_sha(src_e) == tmeta["source_explanation_blob_sha"]

    return {
        "verified": True,
        "total_questions": len(q_blocks),
        "total_explanations": len(e_blocks),
        "crosswalk_rows": len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("MASTER"))
    parser.add_argument("--overlay-revisions", type=Path, default=None)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    out_dir = (root / args.out_dir) if not args.out_dir.is_absolute() else args.out_dir
    overlay_dir = (
        ((root / args.overlay_revisions) if not args.overlay_revisions.is_absolute() else args.overlay_revisions)
        if args.overlay_revisions
        else None
    )

    expected = None
    if not args.verify_only:
        manifest = build_master(
            root,
            out_dir,
            allow_partial=args.allow_partial,
            overlay_batches_dir=overlay_dir,
        )
        expected = manifest["total_questions"]
        print(
            json.dumps(
                {
                    "built": True,
                    "total_questions": manifest["total_questions"],
                    "total_explanations": manifest["total_explanations"],
                    "applied_human_approved_overlays": manifest["applied_human_approved_overlays"],
                    "answer_distribution": manifest["answer_distribution"],
                },
                ensure_ascii=False,
            )
        )
    verification = verify_master(root, out_dir, expected_total=expected)
    print(json.dumps(verification, ensure_ascii=False))


if __name__ == "__main__":
    main()
