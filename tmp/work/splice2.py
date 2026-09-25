#!/usr/bin/env python3
"""splice2.py — put the chapter-2 part files into tafsir/002.md.

Each verse of the scaffold looks like

    ## Verse 2:N

    > the verse line

    **TODO: descriptive heading — …**

    TODO: write this verse from the source digest …

    ---

and the drafting bench keeps one file per verse (`tmp/work/c2_vNN.md`, N padded to
two digits) holding the finished body. This script replaces the TODO block of every
verse whose part file exists, keeps the title, the `## Verse 2:N` line and the quote
line exactly as they are, and leaves the rest of the scaffold alone.

    python3 tmp/work/splice2.py --intro      # the introduction, then every verse
    python3 tmp/work/splice2.py 14 15 16     # only these verses
    python3 tmp/work/splice2.py              # every verse with a part file

`--intro` uses `tmp/work/c2_intro.md` for the block under `## Introduction to the
Sūrah`. A part file is spliced as-is; a TODO block is recognised by its `TODO:`
first line, so a verse that has been written will not be touched twice unless its
part file is passed again — which is exactly how a rewrite works.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "tafsir" / "002.md"
WORK = ROOT / "tmp" / "work"
VERSE_RE = re.compile(r"^## Verse 2:(\d+)\s*$", re.M)


def part(verse: int) -> Path:
    return WORK / ("c2_v%02d.md" % verse)


def body_of(text: str) -> str:
    """The part file with a trailing newline normalised away."""
    return text.strip("\n").strip() + "\n"


def splice_intro(doc: str) -> str:
    p = WORK / "c2_intro.md"
    if not p.exists():
        return doc
    head = "## Introduction to the Sūrah"
    i = doc.index(head) + len(head)
    j = doc.index("\n---\n", i)
    return doc[:i] + "\n\n" + body_of(p.read_text(encoding="utf-8")) + doc[j:]


def splice_verse(doc: str, verse: int) -> str:
    p = part(verse)
    if not p.exists():
        return doc
    m = None
    for m in VERSE_RE.finditer(doc):
        if int(m.group(1)) == verse:
            break
    if m is None or int(m.group(1)) != verse:
        print("  no section for 2:%d" % verse)
        return doc
    start = m.end()
    nxt = VERSE_RE.search(doc, start)
    end = nxt.start() if nxt else len(doc)
    chunk = doc[start:end]
    cut = chunk.find("\n---\n")
    if cut < 0:
        print("  no separator after 2:%d" % verse)
        return doc
    quote = chunk[:cut]
    ql = quote.split("\n")
    # keep a blank line + the quote line + a blank line, drop the TODO block
    kept = [l for l in ql if l.strip()]
    if kept and kept[0].startswith(">"):
        head = "\n\n" + kept[0] + "\n\n"
    else:
        head = "\n\n"
    return doc[:start] + head + body_of(p.read_text(encoding="utf-8")) + doc[start + cut:]


def main(argv):
    doc = DOC.read_text(encoding="utf-8")
    want = [int(a) for a in argv if a.isdigit()]
    if "--intro" in argv or not want:
        doc = splice_intro(doc)
        print("spliced the introduction")
    verses = want or sorted(int(p.name[4:6]) for p in WORK.glob("c2_v??.md"))
    for v in verses:
        before = doc
        doc = splice_verse(doc, v)
        print("%s 2:%d" % ("spliced" if doc != before else "skipped", v))
    DOC.write_text(doc, encoding="utf-8")
    print("wrote tafsir/002.md — %d words" % len(doc.split()))


if __name__ == "__main__":
    main(sys.argv[1:])
