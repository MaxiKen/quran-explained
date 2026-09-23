#!/usr/bin/env python3
"""Scaffold ``tafsir/NNN.md`` with the exact skeleton the auditor demands.

    python3 scripts/tafsir/scaffold.py 1            # create tafsir/001.md
    python3 scripts/tafsir/scaffold.py 2 --force    # overwrite
    python3 scripts/tafsir/scaffold.py 1 --titles   # also draft **headings**

There is no reason ever to type a verse's translation by hand: the quote line
is copied byte-for-byte from ``data/chapter_NNN.js`` here, which removes the
single most common way a generated chapter fails the audit (a quote that fails
verbatim comparison because of a non-breaking space or a paraphrase slip).

The skeleton it writes is deliberately invalid — it carries ``TODO`` markers,
which the auditor fails. Fill the prose in, then run the audit.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

TODO_INTRO = (
    "TODO: write the introduction from the source digest. What the s\u016brah is, "
    "where and when it was revealed, its names, its structure, its place in the "
    "Qur'an \u2014 200\u2013900 words, plain paragraphs, no headings. See TAFSIR_PROMPT.md."
)

TODO_VERSE = (
    "TODO: write this verse's tafsir from the source digest \u2014 150\u2013650 words in "
    "two or more **headed** paragraphs. Quote the Qur'an only from the line above, "
    "in the form (C:V \u2014 *\u201cclause\u201d*). Attribute every report to its collection or "
    "scholar. See TAFSIR_PROMPT.md, then run scripts/tafsir/audit.py %d."
)


def scaffold_text(chapter: int, titles=None) -> str:
    parts = [C.title_line(chapter), "", C.INTRO_HEADING, "", TODO_INTRO, "", "---", ""]
    for v in C.verses(chapter):
        num = v["ayah_no_surah"]
        parts.append("## Verse %d:%d" % (chapter, num))
        parts.append("")
        parts.append("> %s" % v["ayah_en"])
        parts.append("")
        part_titles = (titles or {}).get(num) or ["First Angle", "Second Angle"]
        for title in part_titles:
            parts.append("**%s**" % title)
            parts.append("")
            parts.append(TODO_VERSE % chapter)
            parts.append("")
        parts.append("---")
        parts.append("")
    while parts and parts[-1] == "":
        parts.pop()
    return "\n".join(parts) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)

    path = C.output_path(args.chapter)
    text = scaffold_text(args.chapter)
    if args.stdout:
        print(text)
        return 0
    if path.exists() and not args.force:
        raise SystemExit("%s already exists (use --force to overwrite)" % path.relative_to(C.REPO))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote %s \u2014 %d verses scaffolded" % (path.relative_to(C.REPO), C.verse_count(args.chapter)))
    print("fill the prose, then: python3 scripts/tafsir/audit.py %d" % args.chapter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
