#!/usr/bin/env python3
"""match.py — is the word you are about to explain in the verse?

The match rule (TAFSIR_PROMPT.md §5.1) lets the commentary explain the wording
the verse's translation carries — or a synonym of it, which is adjusted to the
verse's own word. Anything else fails the gate. This tool answers the question
for a single word, before the writing is done:

    python3 scripts/tafsir/match.py --chapter 1 --verse 1 "mercy" "rahmah" "orchard"
    python3 scripts/tafsir/match.py --chapter 2 --verse 255 "throne" "kursi"
    python3 scripts/tafsir/match.py 1:6 "path" "sirat" "street"

    word       verdict
    mercy      synonym   the verse says “Compassionate”
    rahmah     synonym   the verse says “Compassionate”
    orchard    FAIL      not in the verse, and no synonym of anything in it

Exit status is 0 when every word matches (as the verse's own wording or as a
synonym of it), 1 when any word does not.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402
import lexicon as LEX  # noqa: E402

VERDICTS = {"word": "the verse's own word", "synonym": "synonym"}


def check(chapter: int, verse: int, heads: list) -> list:
    """``[(head, kind, verse_wording, verse_phrase)]`` — kind is ``word``, ``synonym`` or ``None``.

    A head may be a single word or a whole phrase: *the day of reckoning* is judged
    against the verse as *reckoning* is.
    """
    verse_text = C.ayah_en(chapter, verse)
    index = LEX.verse_index(verse_text)
    return [(w, *LEX.match_head(w, verse_text, index)) for w in heads]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("ref", nargs="?", help="a verse reference like 1:1 (or use --chapter/--verse)")
    ap.add_argument("words", nargs="*", help="the words or phrases the prose would explain")
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--verse", type=int)
    args = ap.parse_args(argv)

    chapter, verse = args.chapter, args.verse
    if args.ref:
        try:
            c, v = args.ref.split(":")
            chapter, verse = int(c), int(v)
        except ValueError:
            ap.error("give a verse as C:V, e.g. 1:1")
    if not (chapter and verse):
        ap.error("give a verse: --chapter N --verse V, or a reference like 1:1")

    if not args.words:
        print("verse %d:%d \u2014 %s" % (chapter, verse, C.ayah_en(chapter, verse)))
        print("  the verse's own words:", ", ".join(w for w in LEX.content_words(C.ayah_en(chapter, verse))))
        return 0

    print("verse %d:%d \u2014 %s\n" % (chapter, verse, C.ayah_en(chapter, verse)))
    print("  %-32s %-9s %s" % ("word or phrase", "verdict", "the verse's own wording"))
    bad = 0
    for head, kind, wording, phrase in check(chapter, verse, args.words):
        if kind == "word":
            print("  %-32s %-9s %s" % (head, "own word", phrase or wording))
        elif kind == "synonym":
            tail = ("  (in \u201c%s\u201d)" % phrase) if phrase and phrase != wording else ""
            print("  %-32s %-9s %s%s" % (head, "synonym", wording, tail))
        else:
            print("  %-32s %-9s %s" % (head, "FAIL", "\u2014 not the verse's wording, and no way "
                                                     "of saying the same thing that is"))
            bad += 1
    print()
    if bad:
        print("%d word(s) the verse does not carry: re-write the point around the verse's own "
              "wording, or drop it." % bad)
    else:
        print("every word is the verse's own, or a synonym the gate will adjust to it.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
