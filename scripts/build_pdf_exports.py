#!/usr/bin/env python3
"""Render MASTER/VascQBank_10K_ALL_{QUESTIONS,EXPLANATIONS}.txt into two PDFs.

Read-only with respect to all TXT sources. Requires: reportlab, fonttools.
Usage: python scripts/build_pdf_exports.py --root . --out-dir MASTER/PDF
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.ttLib import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
QUESTION_RE = re.compile(r"(?m)^(\d+)\.\s+")
EXPLANATION_RE = re.compile(r"^(\d+)\.\s*([აბგდე])\)\s*(.+)$")
TOPIC_ROW_RE = re.compile(r"^\|\s*([A-Z][A-Z_]+)\s*\|\s*([^|]+?)\s*\|\s*([\d,]+)\s*\|", re.M)


def split_blocks(text: str) -> list[tuple[int, str]]:
    ms = list(QUESTION_RE.finditer(text))
    return [
        (int(m.group(1)), text[m.start(): ms[i + 1].start() if i + 1 < len(ms) else len(text)].strip())
        for i, m in enumerate(ms)
    ]


def check_glyph_coverage(texts: list[str]) -> None:
    needed = {ord(ch) for t in texts for ch in set(t) if ord(ch) > 31}
    for path in (FONT_REGULAR, FONT_BOLD):
        cmap = TTFont(path).getBestCmap()
        missing = sorted(c for c in needed if c not in cmap)
        if missing:
            raise SystemExit(f"{path} lacks glyphs: {[hex(c) + ' ' + chr(c) for c in missing]}")


class BookmarkDoc(BaseDocTemplate):
    def __init__(self, filename: str, title: str, footer: str, **kw):
        super().__init__(filename, pagesize=A4, title=title, author="VascQBank-10K",
                         subject=title, leftMargin=16 * mm, rightMargin=16 * mm,
                         topMargin=15 * mm, bottomMargin=16 * mm, **kw)
        self.footer = footer
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="main")
        self.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=self._decorate)])

    def _decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("DejaVu", 7.5)
        canvas.setFillColor(HexColor("#666666"))
        canvas.drawString(self.leftMargin, 9 * mm, self.footer)
        canvas.drawRightString(A4[0] - self.rightMargin, 9 * mm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        mark = getattr(flowable, "_bookmark", None)
        if mark:
            key, label, level = mark
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(label, key, level=level, closed=level > 0)


def styles():
    base = dict(fontName="DejaVu", fontSize=9.3, leading=12.4)
    return {
        "title": ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=20, leading=26,
                                alignment=TA_CENTER, spaceAfter=10),
        "subtitle": ParagraphStyle("subtitle", fontName="DejaVu", fontSize=11, leading=15,
                                   alignment=TA_CENTER, textColor=HexColor("#333333")),
        "toc": ParagraphStyle("toc", fontName="DejaVu", fontSize=10, leading=15, leftIndent=10),
        "topic": ParagraphStyle("topic", fontName="DejaVu-Bold", fontSize=13.5, leading=18,
                                textColor=HexColor("#7a1010"), spaceBefore=4, spaceAfter=8),
        "stem": ParagraphStyle("stem", spaceBefore=6, spaceAfter=2, **base),
        "opt": ParagraphStyle("opt", leftIndent=12, spaceAfter=0.5, **base),
        "optc": ParagraphStyle("optc", leftIndent=12, spaceAfter=0.5, textColor=HexColor("#0b5d1e"),
                               **{**base, "fontName": "DejaVu-Bold"}),
        "expl": ParagraphStyle("expl", spaceBefore=4, spaceAfter=3, **base),
    }


def load_topics(root: Path, manifest: dict) -> list[dict]:
    names = {m.group(1): m.group(2).strip() for m in TOPIC_ROW_RE.finditer(
        (root / "AGENTS.md").read_text(encoding="utf-8"))}
    return [{**t, "name": names.get(t["topic"], t["topic"])} for t in manifest["topics"]]


def cover(st, title: str, subtitle: str, topics: list[dict], head: str) -> list:
    flow = [Spacer(1, 45 * mm), Paragraph(escape(title), st["title"]),
            Paragraph(escape(subtitle), st["subtitle"]), Spacer(1, 6 * mm),
            Paragraph(escape(f"წყაროს commit: {head[:12]} · 12 თემა · 10 000 ერთეული"), st["subtitle"]),
            Spacer(1, 14 * mm)]
    for t in topics:
        flow.append(Paragraph(escape(f"{t['global_start']}–{t['global_end']}  ·  {t['topic']} — {t['name']}"),
                              st["toc"]))
    flow.append(PageBreak())
    return flow


def topic_header(st, t: dict, idx: int) -> Paragraph:
    p = Paragraph(escape(f"{t['topic']} — {t['name']} (№{t['global_start']}–{t['global_end']})"), st["topic"])
    p._bookmark = (f"topic{idx}", f"{t['topic']} — {t['name']} ({t['global_start']}–{t['global_end']})", 0)
    return p


def build_questions_pdf(blocks, topics, st, out: Path, head: str) -> None:
    doc = BookmarkDoc(str(out), "VascQBank-10K — კითხვები (10 000)",
                      "VascQBank-10K · კითხვები · * — სწორი პასუხი")
    flow = cover(st, "VascQBank-10K", "სისხლძარღვთა ქირურგიის 10 000 საგამოცდო კითხვა", topics, head)
    starts = {t["global_start"]: (i, t) for i, t in enumerate(topics)}
    for n, block in blocks:
        if n in starts:
            i, t = starts[n]
            if n != 1:
                flow.append(PageBreak())
            flow.append(topic_header(st, t, i))
        lines = block.splitlines()
        items = [Paragraph(f"<b>{escape(lines[0].split('.', 1)[0])}.</b>{escape(lines[0].split('.', 1)[1])}",
                           st["stem"])]
        for ln in lines[1:]:
            items.append(Paragraph(escape(ln), st["optc"] if ln.startswith("*") else st["opt"]))
        if (n - 1) % 100 == 0:
            items[0]._bookmark = (f"q{n}", f"№{n}–{min(n + 99, 10000)}", 1)
        flow.append(KeepTogether(items))
    doc.build(flow)


def build_explanations_pdf(blocks, topics, st, out: Path, head: str) -> None:
    doc = BookmarkDoc(str(out), "VascQBank-10K — პასუხები და განმარტებები (10 000)",
                      "VascQBank-10K · სწორი პასუხები და განმარტებები")
    flow = cover(st, "VascQBank-10K", "10 000 კითხვის სწორი პასუხი და განმარტება", topics, head)
    starts = {t["global_start"]: (i, t) for i, t in enumerate(topics)}
    for n, block in blocks:
        if n in starts:
            i, t = starts[n]
            if n != 1:
                flow.append(PageBreak())
            flow.append(topic_header(st, t, i))
        m = EXPLANATION_RE.match(block)
        if not m or int(m.group(1)) != n:
            raise SystemExit(f"Malformed explanation #{n}")
        p = Paragraph(f"<b>{n}. {m.group(2)})</b> {escape(m.group(3))}", st["expl"])
        if (n - 1) % 100 == 0:
            p._bookmark = (f"e{n}", f"№{n}–{min(n + 99, 10000)}", 1)
        flow.append(p)
    doc.build(flow)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out-dir", type=Path, default=Path("MASTER/PDF"))
    ap.add_argument("--only", choices=["questions", "explanations"])
    args = ap.parse_args()
    root = args.root.resolve()
    out_dir = args.out_dir if args.out_dir.is_absolute() else root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((root / "MASTER/VascQBank_10K_MANIFEST.json").read_text(encoding="utf-8"))
    qtext = (root / "MASTER/VascQBank_10K_ALL_QUESTIONS.txt").read_text(encoding="utf-8")
    etext = (root / "MASTER/VascQBank_10K_ALL_EXPLANATIONS.txt").read_text(encoding="utf-8")
    qblocks, eblocks = split_blocks(qtext), split_blocks(etext)
    total = manifest["total_questions"]
    assert [n for n, _ in qblocks] == list(range(1, total + 1)) == [n for n, _ in eblocks]
    check_glyph_coverage([qtext, etext])

    pdfmetrics.registerFont(RLTTFont("DejaVu", FONT_REGULAR))
    pdfmetrics.registerFont(RLTTFont("DejaVu-Bold", FONT_BOLD))
    pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                                  italic="DejaVu", boldItalic="DejaVu-Bold")
    st = styles()
    topics = load_topics(root, manifest)
    head = manifest["source_head_commit"]

    if args.only in (None, "questions"):
        build_questions_pdf(qblocks, topics, st, out_dir / "VascQBank_10K_QUESTIONS.pdf", head)
        print("questions PDF done")
    if args.only in (None, "explanations"):
        build_explanations_pdf(eblocks, topics, st, out_dir / "VascQBank_10K_EXPLANATIONS.pdf", head)
        print("explanations PDF done")


if __name__ == "__main__":
    main()
