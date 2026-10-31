#!/usr/bin/env python3
"""Step three of authoring: check a chapter against the rules before it ships.

    python3 tools/pairs/authoring/audit.py SURAH [FIRST LAST]

The gate in `assemble.py` enforces the rules that must hold for every
published phrase: the floor, the structure, the house style. This audit
reports a chapter against those rules, and against the *working* rules used
while writing, which are stricter, so that a batch can be checked before it
is committed:

- the length curve, phrase by phrase, with the words written, the words the
  material deserves, and the margin around the curve;
- the house style, including the one-voice rule that no commentator,
  transmitter or companion is named;
- the floor, and the split rule that a piece of a verse must carry enough of
  Ṭabarī's own discussion to stand as a phrase of its own.

It exits 1 when a rule is broken, so it can be used as a gate in a pipeline.

The curve is a working target, not a published rule, so a phrase outside the
margin is reported as a warning and only fails the run with `--strict`. The
house style, the floor and the split rule always fail the run.
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = os.path.dirname(HERE)
sys.path.insert(0, PAIRS)

import assemble  # noqa: E402
import curve  # noqa: E402
import digest  # noqa: E402
import style  # noqa: E402

AUTHORED = os.path.join(PAIRS, "authored")


def policy_of(authored: dict, verse: dict) -> str:
    return (verse.get("split_policy")
            or authored.get("split_policy")
            or assemble.POLICY_LEGACY)


def audit(surah: int, first: int | None, last: int | None, verbose: bool,
          strict: bool = False) -> int:
    path = os.path.join(AUTHORED, "%03d.json" % surah)
    import json

    with open(path, encoding="utf-8") as handle:
        authored = json.load(handle)

    tafsir, verses, _ = digest.load_surah(surah)
    checked = 0
    words = 0
    off_curve: list[str] = []
    problems: list[str] = []

    for number in sorted(authored.get("verses", {}), key=lambda n: int(n)):
        ayah = int(number)
        if first is not None and not first <= ayah <= last:
            continue
        verse = authored["verses"][number]
        policy = policy_of(authored, verse)
        if policy != assemble.POLICY_TABARI:
            continue
        where = "%d:%s" % (surah, number)

        try:
            spans = digest.phrase_spans([p.get("ar", "") for p in verse["phrases"]],
                                         verses[number]["ar"])
        except ValueError as exc:
            problems.append("%s: %s" % (where, exc))
            continue

        measured = digest.measure(digest.verse_passage(tafsir, number), verses[number]["ar"])
        for index, (phrase, span) in enumerate(zip(verse["phrases"], spans), 1):
            label = "%s phrase %d" % (where, index)
            info = digest.budget(measured, span)
            want = curve.desired(info["points"])
            have = len(" ".join(phrase.get("explanation", "").split()).split())
            checked += 1
            words += have

            for message in style.style_problems(phrase.get("explanation", ""), label):
                problems.append(message)

            floor = digest.length_problem(have, info, label)
            if floor:
                problems.append(floor)

            if len(verse["phrases"]) > 1:
                split = digest.split_problem(info, label)
                if split:
                    problems.append(split)

            if curve.off_curve(have, want):
                off_curve.append("%s: %d words, the curve wants %d (margin %d)"
                                 % (label, have, want, curve.tolerance(want)))
            elif verbose:
                low, high = curve.band(want)
                print("  %-16s %4d words   curve %4d (%d-%d)   %.2f points"
                      % (label, have, want, low, high, info["points"]))

    print("%d:%s-%s   %d phrase(s), %d words" % (surah, first or 1, last or "end", checked, words))
    for message in off_curve:
        print("  ~ off the curve  %s" % message)
    for message in problems:
        print("  ! %s" % message)
    if not off_curve and not problems:
        print("  every phrase is on the curve and inside the house style")
    return 1 if (problems or (strict and off_curve)) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("surah", type=int)
    parser.add_argument("first", nargs="?", type=int)
    parser.add_argument("last", nargs="?", type=int)
    parser.add_argument("--quiet", action="store_true", help="print only the problems")
    parser.add_argument("--strict", action="store_true",
                        help="also fail when a phrase sits outside the working margin")
    args = parser.parse_args()
    last = args.last if args.last is not None else args.first
    return audit(args.surah, args.first, last, not args.quiet, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
