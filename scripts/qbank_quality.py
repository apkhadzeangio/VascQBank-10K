#!/usr/bin/env python3
"""Read-only structural quality gate for VascQBank-10K; never edits production data."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

LETTERS = "აბგდე"
QUESTION = re.compile(r"(?m)^(\d+)\.\s+")
OPTION = re.compile(r"^(\*?)([აბგდე])\)\s+(.+)$")
EXPLANATION = re.compile(r"(?m)^(\d+)\.\s*([აბგდე])\)\s*(.*)$")
TOPIC_ROW = re.compile(r"^\|\s*([A-Z][A-Z_]+)\s*\|[^|]+\|\s*([\d,]+)\s*\|", re.M)


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def issue(level, code, topic, file, number, message, action):
    return dict(level=level, code=code, topic=topic, file=file, number=number,
                message=message, action=action)


def split_numbered(text: str, pattern):
    matches = list(pattern.finditer(text))
    prefix = text[:matches[0].start()].strip() if matches else text.strip()
    blocks = [(int(m.group(1)), text[m.end():matches[i + 1].start()].strip()
               if i + 1 < len(matches) else text[m.end():].strip())
              for i, m in enumerate(matches)]
    return prefix, blocks


def validate_repository(root: Path):
    findings, details, seen_stems = [], {}, {}
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    targets = {m.group(1): int(m.group(2).replace(",", ""))
               for m in TOPIC_ROW.finditer(agents)}
    if len(targets) != 12 or sum(targets.values()) != 10000:
        findings.append(issue("error", "TARGETS", "PROJECT", "AGENTS.md", None,
                              "Expected 12 topic targets totalling 10,000.",
                              "Check the targets table in AGENTS.md."))
    try:
        index = json.loads((root / "AUTOMATION_CONTEXT.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        findings.append(issue("error", "INDEX_UNREADABLE", "PROJECT",
                              "AUTOMATION_CONTEXT.json", None, str(exc),
                              "Repair the index in a separate producer-safe change."))
        index = {}

    for code, filename, sourcekey in (("AGENTS", "AGENTS.md", "agents_md"),
                                       ("GLOSSARY", "GLOSSARY.md", "glossary_md")):
        p = root / filename
        if p.exists():
            sha = git_blob_sha(p.read_bytes())
            expected = index.get("source_sha", {}).get(sourcekey)
            if expected != sha:
                findings.append(issue("error", "SOURCE_SHA", code, filename, None,
                                      f"Index {expected} != actual {sha}.",
                                      "Reconcile the source SHA without overwriting agent progress."))

    def add(level, code, topic, filename, n, message, action):
        findings.append(issue(level, code, topic, filename, n, message, action))

    for topic, target in targets.items():
        qf, ef = f"{topic}_questions.txt", f"{topic}_explanations.txt"
        qp, ep = root / qf, root / ef
        if not qp.exists() or not ep.exists():
            add("error", "MISSING_FILE", topic, qf if not qp.exists() else ef, None,
                "Topic file is missing.", "Restore the missing file.")
            continue
        qtext, etext = qp.read_text(encoding="utf-8-sig"), ep.read_text(encoding="utf-8-sig")
        qpre, qs = split_numbered(qtext, QUESTION)
        epre, es = split_numbered(etext, EXPLANATION)
        if qpre:
            add("error", "QUESTION_PREFIX", topic, qf, None, "Unexpected text before question 1.",
                "Remove the unnumbered prefix in a reviewed data correction.")
        if epre:
            add("error", "EXPLANATION_PREFIX", topic, ef, None, "Unexpected text before explanation 1.",
                "Remove the unnumbered prefix in a reviewed data correction.")
        qnums = [n for n, _ in qs]
        enums = [n for n, _ in es]
        for kind, nums, filename in (("QUESTION", qnums, qf), ("EXPLANATION", enums, ef)):
            if nums != list(range(1, len(nums) + 1)):
                add("error", f"{kind}_SEQUENCE", topic, filename, None,
                    f"Expected 1..{len(nums)}; observed {nums[:12]}... last {nums[-5:]}.",
                    "Review missing, duplicated or out-of-order numbering.")
        if len(qs) > target:
            add("error", "TARGET_EXCEEDED", topic, qf, None,
                f"{len(qs)} questions exceed target {target}.", "Review target and excess questions.")
        if len(qs) != len(es):
            add("error", "EXPLANATION_COUNT", topic, ef, None,
                f"{len(qs)} questions vs {len(es)} explanations.", "Match explanations to questions.")
        correct = {}
        for n, body in qs:
            lines = body.splitlines()
            options = [OPTION.match(line.strip()) for line in lines[1:] if line.strip()]
            if len(options) != 5 or any(m is None for m in options):
                add("error", "OPTION_COUNT", topic, qf, n,
                    "Expected exactly five unbroken option lines.", "Check answer lines for extra or missing options.")
                continue
            letters = [m.group(2) for m in options]
            if letters != list(LETTERS):
                add("error", "OPTION_ORDER", topic, qf, n,
                    f"Observed order {''.join(letters)}.", "Use ა), ბ), გ), დ), ე) exactly once.")
            marked = [m.group(2) for m in options if m.group(1) == "*"]
            if len(marked) != 1:
                add("error", "CORRECT_COUNT", topic, qf, n,
                    f"Expected one *; observed {len(marked)}.", "Mark exactly one correct option.")
            else:
                correct[n] = marked[0]
            stem = re.sub(r"\s+", " ", lines[0]).strip().casefold() if lines else ""
            if not stem:
                add("error", "EMPTY_STEM", topic, qf, n, "Empty question stem.", "Write a question.")
            elif stem in seen_stems:
                other_topic, other_n = seen_stems[stem]
                add("error", "DUPLICATE_STEM", topic, qf, n,
                    f"Exact normalized question duplicate of {other_topic} #{other_n}.",
                    "Review duplicated text; do not modify questions automatically.")
            else:
                seen_stems[stem] = (topic, n)
        eanswers = {}
        for n, body in es:
            # split_numbered consumed "N. " and the explanation matcher also consumed answer letter.
            # Read the original explanation line by matching the numbered entry again.
            entry = re.search(r"(?m)^" + str(n) + r"\.\s*([აბგდე])\)\s*(.*)$", etext)
            if entry is None:
                add("error", "EXPLANATION_FORMAT", topic, ef, n,
                    "Missing explanation number and answer letter.", "Use 'N. ა) sentence. sentence.'.")
                continue
            answer, prose = entry.group(1), entry.group(2).strip()
            eanswers[n] = answer
            ends = re.findall(r"[.!?](?=\s|$)", prose)
            if len(ends) != 2 or not prose.endswith((".", "!", "?")):
                add("warning", "SENTENCE_REVIEW", topic, ef, n,
                    f"Found {len(ends)} likely sentence ends (heuristic; may include abbreviations).",
                    "Manually verify exactly two sentences; do not automatically rewrite.")
        for n in sorted(set(qnums) | set(enums)):
            if n in correct and n in eanswers and correct[n] != eanswers[n]:
                add("error", "ANSWER_MISMATCH", topic, ef, n,
                    f"Question marks {correct[n]}); explanation says {eanswers[n]}).",
                    "Correct the mismatched letter after human review.")

        state = index.get("topics", {}).get(topic, {})
        for field, actual in (("last_number", len(qs)),
                              ("question_blob_sha", git_blob_sha(qp.read_bytes())),
                              ("explanation_blob_sha", git_blob_sha(ep.read_bytes()))):
            if state.get(field) != actual:
                add("error", "INDEX_MISMATCH", topic, "AUTOMATION_CONTEXT.json", None,
                    f"{field}: stored {state.get(field)} vs actual {actual}.",
                    "Recheck latest main and reconcile atomically; do not auto-edit.")
        details[topic] = dict(questions=len(qs), explanations=len(es), target=target,
                              last_question=qnums[-1] if qnums else 0)
    return dict(summary=dict(topics=len(details), questions=sum(v["questions"] for v in details.values()),
                             errors=sum(f["level"] == "error" for f in findings),
                             warnings=sum(f["level"] == "warning" for f in findings)),
                topics=details, findings=findings)


def markdown(report):
    s = report["summary"]
    rows = [f"## VascQBank structural gate: {s['errors']} errors; {s['warnings']} warnings",
            f"Topics: {s['topics']}; questions: {s['questions']}. This is NOT independent clinical review.",
            "", "| Level | Topic | File | # | Type | Action |",
            "|---|---|---|---:|---|---|"]
    for f in report["findings"][:150]:
        rows.append(f"| {f['level']} | {f['topic']} | {f['file']} | {f['number'] or '—'} | "
                    f"{f['code']} | {f['action']} |")
    if len(report["findings"]) > 150:
        rows.append(f"\nOnly first 150 of {len(report['findings'])} findings displayed; see JSON artifact.")
    return "\n".join(rows) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--json-out", type=Path)
    p.add_argument("--markdown-out", type=Path)
    args = p.parse_args()
    report = validate_repository(args.root)
    if args.json_out:
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    for f in report["findings"][:20]:
        print(f"{f['level']}: {f['topic']} {f['file']} #{f['number']}: {f['code']} {f['message']}")
    raise SystemExit(1 if report["summary"]["errors"] else 0)


if __name__ == "__main__":
    main()
