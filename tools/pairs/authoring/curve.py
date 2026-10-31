#!/usr/bin/env python3
"""The length curve: how long an explanation should be for the material it carries.

This is the arithmetic half of the length rule. `digest.py` measures what
Tafsīr al-Ṭabarī discusses for a piece of a verse and counts it in *points*:
a meaning is one point, a verdict is one, a disagreement is one, a reading is
0.8, a grammatical observation is 0.6, a piece of context is 0.6, and
everything else (chains of transmitters, poetry quoted as evidence, the
translator's apparatus) is 0.25 and is not substantive.

The rule the chapters are written under:

    target  = 15 words for every point Ṭabarī makes
    floor   = 40 words, or 60% of the target when the target is larger
    ceiling = none. There is no upper bound.

The curve below is the *working* figure a draft is written to. It is the
target plus a tenth, because a plain summary nearly always needs a little
more room than the raw ratio suggests, and it never goes below 110 words,
because a piece of the Qur'an is never worth less than that. It is a target,
not a cap: a phrase that runs long is reporting material Ṭabarī gave, and the
gate never rejects it for being long.

The tolerance around the curve is a working margin for drafting, not a rule
of the corpus. It is what the authoring tools use to say "this draft is on
the curve" or "this draft is off it", so that a batch can be checked before
it is written into the chapter.
"""

from __future__ import annotations

MIN_WORDS = 110          # the shortest explanation worth writing
POINT_WORDS = 15         # words of summary for every point Ṭabarī makes
WORKING_RATIO = 1.1      # the working target is the target plus a tenth
TOLERANCE_RATIO = 0.12   # the working margin around the curve
TOLERANCE_MIN = 12       # ... but never tighter than twelve words


def desired(points: float) -> int:
    """The word count a draft for this much material is written to."""
    return round(WORKING_RATIO * max(MIN_WORDS, round(POINT_WORDS * points)))


def tolerance(want: int) -> int:
    """How far from the curve a draft may sit and still count as on it."""
    return max(TOLERANCE_MIN, int(want * TOLERANCE_RATIO))


def band(want: int) -> tuple[int, int]:
    """The lowest and highest word count that count as on the curve."""
    return want - tolerance(want), want + tolerance(want)


def off_curve(words: int, want: int) -> bool:
    """True when a draft sits outside the working margin around the curve."""
    return abs(words - want) > tolerance(want)


def describe(points: float) -> dict:
    """Everything a writer needs to know about one piece of material."""
    want = desired(points)
    low, high = band(want)
    return {
        "points": round(points, 2),
        "want": want,
        "tolerance": tolerance(want),
        "low": low,
        "high": high,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(0)
    for raw in sys.argv[1:]:
        info = describe(float(raw))
        print("%6.2f points -> write %d words (on the curve between %d and %d)"
              % (info["points"], info["want"], info["low"], info["high"]))
