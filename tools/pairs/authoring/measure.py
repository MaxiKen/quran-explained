#!/usr/bin/env python3
"""Step one of authoring: read the source, and score the splits it suggests.

    python3 tools/pairs/authoring/measure.py SURAH VERSE [--full]

This prints what Tafsīr al-Ṭabarī holds for one verse, paragraph by
paragraph and classified, then every candidate piece of the verse measured
against the length curve. It is the reading step the writing step is based on,
and it answers three questions at once:

1. What does Ṭabarī actually discuss about this verse, and how much of it is
   substantive (points) as opposed to chains and quoted poetry?
2. Where does the material change topic? Every candidate boundary is scored,
   and a piece that holds less than `digest.MIN_SPLIT_POINTS` substantive
   points is marked for merging with a neighbour, because it has nothing of
   his own to stand as a phrase.
3. How long should each phrase be? The curve is `curve.desired(points)`, and
   the band around it is the working margin a draft is written inside.

`--full` prints the whole text of each paragraph, which is what a draft is
written from.
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = os.path.dirname(HERE)
sys.path.insert(0, PAIRS)

import curve  # noqa: E402
import digest  # noqa: E402


def print_material(surah: int, ayah: str, full: bool) -> None:
    tafsir, verses, _ = digest.load_surah(surah)
    block = digest.verse_passage(tafsir, ayah)
    measured = digest.measure(block, verses[ayah]["ar"])
    words = verses[ayah]["ar"].split()

    print("=" * 78)
    print("%d:%s   Ṭabarī: %d words in %d paragraphs, %d words in the verse"
          % (surah, ayah, len(block.split()), len(measured), len(words)))
    print("  AR  %s" % verses[ayah]["ar"])
    print("  EN  %s" % verses[ayah]["en"])
    print("  a piece stands alone from %.2f substantive points" % digest.MIN_SPLIT_POINTS)
    print("\n  --- what the source holds ---")
    for p in measured:
        where = "preface" if p["preface"] else ("inherited" if p["inherited"] else "located")
        print("  [%s %s %dw pts %.2f] %s"
              % (p["class"], where, p["words"], p["weight"],
                 p["text"][:200].replace("\n", " ") if not full else p["text"]))


def print_candidates(surah: int, ayah: str) -> None:
    tafsir, verses, _ = digest.load_surah(surah)
    block = digest.verse_passage(tafsir, ayah)
    words = verses[ayah]["ar"].split()
    measured = digest.measure(block, verses[ayah]["ar"])

    print("\n  --- candidate pieces ---")
    for width in (1, 2, 3):
        if len(words) < width:
            continue
        for start in range(len(words) - width + 1):
            span = (start, start + width - 1)
            info = digest.budget(measured, span)
            verdict = digest.split_problem(info, "piece")
            want = curve.desired(info["points"])
            print("  %2d-%-2d %-30s src %6dw  pts %5.2f  subst %5.2f  want %4d  %s"
                  % (span[0], span[1],
                     " ".join(words[span[0]:span[1] + 1])[:30],
                     info["material_words"], info["points"], info["substantive_points"],
                     want,
                     "merge with a neighbour" if verdict else "stands alone"))


def print_current(surah: int, ayah: str) -> None:
    tafsir, verses, authored = digest.load_surah(surah)
    entry = (authored or {}).get("verses", {}).get(ayah)
    if not entry or not entry.get("phrases"):
        return
    try:
        spans = digest.phrase_spans([p.get("ar", "") for p in entry["phrases"]], verses[ayah]["ar"])
    except ValueError as exc:
        print("\n  ! the authored spans do not fit the verse: %s" % exc)
        return
    block = digest.verse_passage(tafsir, ayah)
    measured = digest.measure(block, verses[ayah]["ar"])
    print("\n  --- the split as it stands ---")
    for number, (phrase, span) in enumerate(zip(entry["phrases"], spans), 1):
        info = digest.budget(measured, span)
        want = curve.desired(info["points"])
        have = len(" ".join(phrase.get("explanation", "").split()).split())
        low, high = curve.band(want)
        print("  %d. words %d-%d  pts %5.2f  want %4d (%d-%d)  draft %4d  %s"
              % (number, span[0], span[1], info["points"], want, low, high, have,
                 "on the curve" if not curve.off_curve(have, want) else "OFF the curve"))
        print("     EN  %s" % phrase.get("translation", "")[:100])
        print("     AR  %s" % phrase.get("ar", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("surah", type=int)
    parser.add_argument("verse")
    parser.add_argument("--full", action="store_true",
                        help="print the whole text of each paragraph")
    args = parser.parse_args()

    print_material(args.surah, args.verse, args.full)
    print_candidates(args.surah, args.verse)
    print_current(args.surah, args.verse)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
