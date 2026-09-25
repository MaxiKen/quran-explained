#!/usr/bin/env python3
"""extract_parts.py — rebuild the drafting bench from a written chapter.

Chapter 2 is written a verse at a time: the prose lives in `tmp/work/c2_vNN.md`
and `splice2.py` puts it into `tafsir/002.md`. The scratch directory has been
wiped by the sandbox more than once, so this script reads the chapter back out of
`tafsir/002.md` and rewrites every part file it can find — the written verses and
the introduction — leaving scaffold TODOs alone.

    python3 tmp/work/extract_parts.py            # write what is missing
    python3 tmp/work/extract_parts.py --force    # overwrite the bench from the chapter
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "tafsir" / "002.md"
WORK = ROOT / "tmp" / "work"
VERSE_RE = re.compile(r"^## Verse 2:(\d+)\s*$", re.M)


def blocks(doc):
    """(kind, number, body) for the introduction and every written verse."""
    head = "## Introduction to the Sūrah"
    i = doc.index(head) + len(head)
    j = doc.index("\n---\n", i)
    intro = doc[i:j]
    if "TODO:" not in intro:
        yield "intro", 0, intro.strip("\n").strip() + "\n"
    starts = list(VERSE_RE.finditer(doc))
    for k, m in enumerate(starts):
        start = m.end()
        end = starts[k + 1].start() if k + 1 < len(starts) else len(doc)
        chunk = doc[start:end]
        cut = chunk.find("\n---\n")
        if cut < 0:
            continue
        body = chunk[:cut]
        if "TODO:" in body:
            continue
        lines = [l for l in body.split("\n") if l.strip()]
        if lines and lines[0].startswith(">"):
            lines = lines[1:]
        yield "verse", int(m.group(1)), "\n".join(lines).strip("\n").strip() + "\n"


def main(argv):
    force = "--force" in argv
    doc = DOC.read_text(encoding="utf-8")
    WORK.mkdir(parents=True, exist_ok=True)
    written = 0
    for kind, num, body in blocks(doc):
        p = WORK / ("c2_intro.md" if kind == "intro" else "c2_v%02d.md" % num)
        if p.exists() and not force:
            continue
        p.write_text(body, encoding="utf-8")
        written += 1
        print("  wrote %s (%d words)" % (p.name, len(body.split())))
    print("bench rebuilt: %d file(s)%s" % (written, "" if written else " — nothing was missing"))


if __name__ == "__main__":
    main(sys.argv[1:])
