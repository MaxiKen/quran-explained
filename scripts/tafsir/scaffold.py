#!/usr/bin/env python3
"""Scaffold ``tafsir/NNN.md`` with the exact skeleton the auditor demands.

    python3 scripts/tafsir/scaffold.py 1            # create tafsir/001.md
    python3 scripts/tafsir/scaffold.py 2 --force    # overwrite
    python3 scripts/tafsir/scaffold.py 1 --stdout   # print instead of writing

Two things are copied rather than typed:

* the verse quote line, byte-for-byte from ``data/chapter_NNN.js`` — the single
  most common way a chapter fails the audit is a quote that does not compare
  verbatim (a paraphrase slip, a plain space where the stored text has a
  non-breaking one);
* the phrase headings, cut from the verse's own translation by
  ``corpus.split_phrases``, each one wrapped in quotes and already in verse
  order — so the phrase-coverage rule passes by construction. Re-cut them if a
  better phrasing boundary exists, as long as every phrase is still quoted and
  in order.

The skeleton it writes is deliberately invalid: every block carries a ``TODO``
marker, which the auditor fails. Fill the prose in, then run the audit.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

MIN_VERSE_WORDS = 550
SCALE_FACTOR = 7.0
SCALE_CAP = 3500


def floor_for(chapter: int, verse: int) -> int:
    """Words this verse's section must carry (same rule as the auditor)."""
    words = len(C.words(C.ayah_en(chapter, verse)))
    return max(MIN_VERSE_WORDS, min(SCALE_CAP, int(math.ceil(SCALE_FACTOR * words))))


INTRO_TODO = (
    "TODO: write the introduction from the source digest. What the s\u016brah is, where and "
    "when it was revealed, its names, its structure, its place in the Qur'an, what the "
    "classical commentators say about it as a whole \u2014 250\u20131,500 words, plain "
    "paragraphs, no headings. See TAFSIR_PROMPT.md."
)


def todo_for(chapter: int, verse: int) -> str:
    return (
        "TODO: explain this phrase from the source digest \u2014 this verse needs at least "
        "%d words in all. Say what the phrase means, what its words carry, the story or "
        "report behind it, the rule or lesson it holds, how it fits the verses around it, "
        "and give one relatable analogy where one fits. Short sentences, everyday words. "
        "Quote the Qur'an only as (C:V \u2014 *\u201cclause\u201d*) from data/chapter_%s.js; name the "
        "collection for every hadith. See TAFSIR_PROMPT.md, then run "
        "scripts/tafsir/audit.py %d."
        % (floor_for(chapter, verse), C.pad3(chapter), chapter)
    )


def scaffold_text(chapter: int) -> str:
    parts = [C.title_line(chapter), "", C.INTRO_HEADING, "", INTRO_TODO, "", "---", ""]
    for v in C.verses(chapter):
        num = v["ayah_no_surah"]
        parts.append("## Verse %d:%d" % (chapter, num))
        parts.append("")
        parts.append("> %s" % v["ayah_en"])
        parts.append("")
        phrases = C.split_phrases(v["ayah_en"]) or [v["ayah_en"]]
        for phrase in phrases:
            parts.append("**\u201c%s\u201d**" % phrase)
            parts.append("")
            parts.append(todo_for(chapter, num))
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
    phrases = sum(len(C.split_phrases(v["ayah_en"]) or [1]) for v in C.verses(args.chapter))
    print("wrote %s \u2014 %d verses, %d phrase headings"
          % (path.relative_to(C.REPO), C.verse_count(args.chapter), phrases))
    print("fill the prose (each verse has its own word floor), then: "
          "python3 scripts/tafsir/audit.py %d" % args.chapter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
