#!/usr/bin/env python3
"""assemble.py — build evidence/NNN.md from the head-by-head drafts in evidence/_work/NNN/.

A long chapter cannot be written in one go: its evidence for one verse comes from eleven works read one
after another, but the map is organised by theme.  So each *head* is a draft file and items are appended to
it as each work is read; this script puts the heads in order and writes the map.

    python3 evidence/_work/assemble.py 1          # writes evidence/001.md from evidence/_work/001/

Layout of evidence/_work/NNN/ :

    0/NN-slug.md ...      the introduction's heads                (items numbered N:0.k)
    V/NN-slug.md ...      verse V's heads, in file-name order     (a head file: "### TITLE", a blank line, items)
    V/aside.txt           the verse's whole "**Set aside:** ..." line (optional)
    V/nothing.txt         the verse's whole "**Nothing further from:** ..." line (optional)
    V/done                an empty file: verse V is finished and goes into the map (a verse without it is left out)

Items are written with a placeholder number (`N:V.0`); this script numbers them 1..n in each block.  The
"Sources with text" line is taken from the digest (python3 scripts/tafsir/sources.py N --cap-json 0).
Nothing here is part of the format: the map file is what is checked (scripts/tafsir/evidencemap.py check N).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "tafsir"))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402
import evidencemap as E  # noqa: E402

ITEM = re.compile(r"^- `(\d+):(\d+)\.(\d+)` (.*)$")


def read_heads(directory: Path):
    """The head files of one block, in order, as text."""
    out = []
    for f in sorted(directory.glob("*.md")):
        text = f.read_text(encoding="utf-8").strip("\n")
        if text:
            out.append(text)
    return out


def number(lines, chapter, verse):
    k, out = 0, []
    for line in lines:
        m = ITEM.match(line)
        if m:
            k += 1
            line = "- `%s:%d.%d` %s" % (chapter, verse, k, m.group(4))
        out.append(line)
    return out


def main() -> int:
    chapter = int(sys.argv[1])
    work = REPO / "evidence" / "_work" / C.pad3(chapter)
    digest = A._digest(chapter)
    if not digest:
        raise SystemExit("tmp/sources/%s.json is missing — run: python3 scripts/tafsir/sources.py %d --cap-json 0" % (C.pad3(chapter), chapter))
    name = C.chapter_name(chapter)
    header = (work / "header.txt").read_text(encoding="utf-8").strip() if (work / "header.txt").exists() else (
        "<!-- depth: full. Phase 1 of the two-phase approach: evidence first, commentary later (TAFSIR_EVIDENCE_MAP.md). "
        "One item for each distinct claim; every citation points at paragraphs (work¶3-5) or, in a long paragraph, at "
        "chunks (work¶4.2-4.3); work@V¶n = the passage under verse V; every paragraph or chunk of the eleven works is "
        "either cited or set aside with a reason. Not the book: a working document that may name the works. "
        "Each item: id · kind · summary [works and paragraphs]. -->")
    out = ["# Evidence map — %s (chapter %d)" % (name, chapter), "", header, ""]

    intro = read_heads(work / "0") if (work / "0").exists() else []
    if intro and (work / "0" / "done").exists():
        block = ["## Introduction", ""]
        for head in intro:
            block += head.splitlines() + [""]
        out += number(block, chapter, 0)

    for v in range(1, C.verse_count(chapter) + 1):
        d = work / str(v)
        if not (d / "done").exists():
            continue
        have = [alias for slug, alias in ((s, E.SLUG_ALIAS[s]) for s in C.SOURCE_ALLOWLIST)
                if ((digest.get(str(v)) or {}).get(slug) or "").strip()]
        block = ["## Verse %d:%d" % (chapter, v), "", "> " + C.ayah_en(chapter, v), "",
                 "**Sources with text:** " + ", ".join(have)]
        for extra in ("nothing.txt", "aside.txt"):
            if (d / extra).exists():
                block.append((d / extra).read_text(encoding="utf-8").strip())
        block.append("")
        for head in read_heads(d):
            block += head.splitlines() + [""]
        out += number(block, chapter, v)

    path = REPO / "evidence" / ("%s.md" % C.pad3(chapter))
    path.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")
    items = sum(1 for line in out if line.startswith("- `"))
    print("wrote %s: %d items" % (path.relative_to(REPO), items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
