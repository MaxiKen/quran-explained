#!/usr/bin/env python3
"""assemble.py — splice the verse drafts into the chapter file.

The drafting bench is ``tmp/work/``: one file per verse, holding the section body
(the UPPERCASE headings and the prose, nothing else), and one for the
introduction. The chapter file ``tafsir/NNN.md`` is generated from the scaffold
plus those drafts, so a chapter is never hand-edited and the verse quotes stay
byte-exact.

    tmp/work/c1_intro.md     the introduction's paragraphs
    tmp/work/c1_v001.md      the body of verse 1 (c1_v1.md also works)
    tmp/work/c2_v282.md      ... three digits keep the files sorted

    python3 scripts/tafsir/assemble.py 1              # splice every draft that exists
    python3 scripts/tafsir/assemble.py 1 --check      # what is drafted, what is not
    python3 scripts/tafsir/assemble.py 1 --verse 5    # splice one verse only
    python3 scripts/tafsir/assemble.py 1 --intro      # splice the introduction only

Splicing keeps the ``## Verse C:V`` heading, the ``> `` verse line and the ``---``
separator from the chapter file; only the body between them is replaced. After a
splice, gate the stretch: ``python3 scripts/tafsir/batch.py 1 --from A --to B``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

WORK_DIR = C.TMP_DIR / "work"


def part_path(chapter: int, verse: int):
    for name in ("c%d_v%03d.md" % (chapter, verse), "c%d_v%d.md" % (chapter, verse)):
        path = WORK_DIR / name
        if path.exists():
            return path
    return None


def intro_path(chapter: int):
    path = WORK_DIR / ("c%d_intro.md" % chapter)
    return path if path.exists() else None


def read_part(path):
    text = path.read_text(encoding="utf-8").strip()
    # a draft may carry the scaffold's own heading and quote line: keep the body
    lines = [l for l in text.split("\n")
             if not C.VERSE_HEADING_RE.match(l) and not l.startswith("> ")]
    text = "\n".join(lines).strip()
    return re.sub(r"\n{3,}", "\n\n", text) + "\n" if text else ""


def splice_section(lines, section, body):
    """Replace a section's body in ``lines`` (0-based list) with ``body``."""
    start = section.start - 1                      # '## Verse C:V'
    end = section.end                              # exclusive, one past the last line
    quote_at = None
    for i in range(start, end):
        if lines[i].startswith(">"):
            quote_at = i
            break
    if quote_at is None:
        raise SystemExit("section %s has no '> ' verse line — re-scaffold this chapter" % section.ref)
    sep_at = end
    for i in range(quote_at + 1, end):
        if lines[i].strip() == "---":
            sep_at = i
            break
    head = lines[start:quote_at + 1]
    tail = lines[sep_at:end]
    new = head + [""] + body.rstrip("\n").split("\n") + [""] + tail
    return lines[:start] + new + lines[end:], len(new) - (end - start)


def splice_intro(lines, doc, body):
    start = doc.intro_heading_line              # 1-based line of '## Introduction to the Sūrah'
    end = doc.sections[0].start - 1             # 1-based first line of the first verse heading
    new = lines[:start] + [""] + body.rstrip("\n").split("\n") + ["", "---", ""] + lines[end - 1:]
    return new


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--verse", type=int, action="append", dest="verses")
    ap.add_argument("--intro", action="store_true", help="splice the introduction only")
    ap.add_argument("--check", action="store_true", help="report the bench state, write nothing")
    args = ap.parse_args(argv)

    path = C.output_path(args.chapter)
    if not path.exists():
        raise SystemExit("%s does not exist — run: python3 scripts/tafsir/run.py --build"
                         % path.relative_to(C.REPO))
    doc = C.load_chapter_doc(args.chapter)
    lines = path.read_text(encoding="utf-8").split("\n")
    if lines and lines[-1] != "":
        lines.append("")

    drafted, missing, todo = [], [], []
    for section in doc.sections:
        if args.verses and section.verse not in args.verses:
            continue
        part = part_path(args.chapter, section.verse)
        done = "TODO" not in section.body()
        (drafted if part else (missing if done else todo)).append(section.verse)

    if args.check:
        print("chapter %d — bench %s" % (args.chapter, WORK_DIR.relative_to(C.REPO)))
        print("  drafted:      %s" % (", ".join(str(v) for v in drafted) or "none"))
        print("  not drafted:  %s" % (", ".join(str(v) for v in todo) or "none"))
        print("  intro:        %s" % ("c%d_intro.md" % args.chapter
                                      if intro_path(args.chapter) else "not drafted"))
        return 0

    spliced = []
    if not args.intro:
        for section in reversed(doc.sections):        # back to front: earlier spans stay valid
            if args.verses and section.verse not in args.verses:
                continue
            part = part_path(args.chapter, section.verse)
            if not part:
                continue
            body = read_part(part)
            if not body:
                continue
            lines, _ = splice_section(lines, section, body)
            spliced.append(section.ref)
    if args.intro or not args.verses:
        # the introduction sits above every verse: splicing it last keeps its line
        # numbers valid through all the verse splices
        ipath = intro_path(args.chapter)
        if ipath:
            body = read_part(ipath)
            if body:
                lines = splice_intro(lines, doc, body)
                spliced.append("introduction")

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    print("spliced %d draft(s) into %s: %s"
          % (len(spliced), path.relative_to(C.REPO), ", ".join(spliced) or "nothing"))
    if spliced:
        first = args.verses[0] if args.verses else C.load_chapter_doc(args.chapter).sections[0].verse
        print("gate the stretch: python3 scripts/tafsir/batch.py %d --from %d --to %d"
              % (args.chapter, min(args.verses) if args.verses else 1,
                 max(args.verses) if args.verses else C.verse_count(args.chapter)))
        print("then: python3 scripts/tafsir/run.py --status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
