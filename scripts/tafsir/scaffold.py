#!/usr/bin/env python3
"""Scaffold ``tafsir/NNN.md`` with the exact skeleton the auditor demands.

    python3 scripts/tafsir/scaffold.py 1            # create tafsir/001.md
    python3 scripts/tafsir/scaffold.py 2 --force    # overwrite
    python3 scripts/tafsir/scaffold.py 1 --stdout   # print instead of writing
    python3 scripts/tafsir/scaffold.py 1 --phrases  # show each verse's phrase cut

The verse quote line is copied byte-for-byte from ``data/chapter_NNN.js`` — the
single most common way a chapter fails the audit is a quote that does not
compare verbatim (a paraphrase slip, a plain space where the stored text has a
non-breaking one).

The headings are **not** written for you, because they are not the verse's
phrases: a section heading is a descriptive title of its own (the setting, a
story, a ruling, the phrase being explained). What the auditor does demand is
that every phrase of the verse is *quoted in the prose* and explained with
evidence beside it, so ``--phrases`` prints the cut that ``corpus.split_phrases``
proposes for each verse, as a worked plan rather than as headings.

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

MIN_VERSE_WORDS = 500          # keep in step with audit.py
SCALE_FACTOR = 8.0
SCALE_CAP = 4000


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
        "TODO: write this verse from the source digest \u2014 at least %d words in all. Read all "
        "ten works for this verse first (python3 scripts/tafsir/sources.py %d --verse %d), and "
        "name at least five of them in the prose, never a work outside the ten. Plan the section "
        "as a set of descriptive headings (the setting, the story or report, the ruling, the "
        "phrases being explained); never use the verse's own words as a heading. Quote every "
        "phrase of the verse inside the prose in bold italics, explain it, and back each quoted "
        "phrase with evidence beside it \u2014 a cross-reference like (C:V \u2014 **\u201cclause\u201d**) "
        "from data/chapter_%s.js, a report with its collection, or a named authority. Aim for "
        "content that carries history, occasions, reports, cross-references, life application "
        "and one relatable analogy by itself; never label those elements (no \u201cLesson:\u201d, no "
        "\u201cModern application:\u201d) \u2014 write them into the flow. Short sentences and everyday "
        "words. See TAFSIR_PROMPT.md, then run scripts/tafsir/audit.py %d."
        % (floor_for(chapter, verse), chapter, verse, C.pad3(chapter), chapter)
    )


def scaffold_text(chapter: int) -> str:
    parts = [C.title_line(chapter), "", C.INTRO_HEADING, "", INTRO_TODO, "", "---", ""]
    for v in C.verses(chapter):
        num = v["ayah_no_surah"]
        parts.append("## Verse %d:%d" % (chapter, num))
        parts.append("")
        parts.append("> %s" % v["ayah_en"])
        parts.append("")
        parts.append("**TODO: descriptive heading \u2014 the setting, the story, or the phrase being explained**")
        parts.append("")
        parts.append(todo_for(chapter, num))
        parts.append("")
        parts.append("**TODO: descriptive heading \u2014 the next thing this verse needs said**")
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
    ap.add_argument("--phrases", action="store_true",
                    help="print the phrase cut the auditor measures every verse against")
    args = ap.parse_args(argv)

    if args.phrases:
        for v in C.verses(args.chapter):
            num = v["ayah_no_surah"]
            print("%d:%d  %s" % (args.chapter, num, v["ayah_en"]))
            for phrase in C.split_phrases(v["ayah_en"]) or [v["ayah_en"]]:
                print("    \u201c%s\u201d" % phrase)
            print("")
        return 0

    path = C.output_path(args.chapter)
    text = scaffold_text(args.chapter)
    if args.stdout:
        print(text)
        return 0
    if path.exists() and not args.force:
        raise SystemExit("%s already exists (use --force to overwrite)" % path.relative_to(C.REPO))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote %s \u2014 %d verses, each with its own word floor and its own headings to write"
          % (path.relative_to(C.REPO), C.verse_count(args.chapter)))
    print("the phrase cut each verse is measured against: python3 scripts/tafsir/scaffold.py %d --phrases | head -40"
          % args.chapter)
    print("fill the prose, then: python3 scripts/tafsir/audit.py %d" % args.chapter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
