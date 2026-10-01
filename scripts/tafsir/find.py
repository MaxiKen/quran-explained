#!/usr/bin/env python3
"""Find the verse that says a thing, and print the citation ready to paste.

    python3 scripts/tafsir/find.py "no god but He"          # English wording
    python3 scripts/tafsir/find.py --ar "الصمد"             # Arabic wording
    python3 scripts/tafsir/find.py "the Straight Path" --limit 6 --words 8

The output is the exact shape the chapter files quote cross-references in —
``(2:255 — **"the clause"**)`` — copied from ``data/chapter_NNN.js``, so no
Qur'an wording is ever typed by hand.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402


def clause(text: str, wanted: int, anchor: str) -> str:
    """A contiguous slice of the verse around the searched words.

    The slice is always the verse's own wording, with `…` where it was cut, so
    the printed citation can be checked against ``data/chapter_NNN.js``.
    """
    low = text.lower()
    i = low.find(anchor.lower())
    if i < 0:
        i = 0
    # token boundaries
    start = text.rfind(" ", 0, i) + 1
    tokens = text.split()
    # how many tokens sit before the match
    before = len(text[:start].split())
    match_len = max(1, len(anchor.split()))
    half = max(1, (wanted - match_len) // 2)
    lo = max(0, before - half)
    hi = min(len(tokens), lo + wanted)
    lo = max(0, hi - wanted)
    # prefer a clean break at punctuation on either side
    for edge in (hi, lo):
        pass
    if hi < len(tokens):
        for back in range(hi, max(hi - 4, lo), -1):
            if tokens[back - 1][-1] in ",;:.!?":
                hi = back
                break
    piece = " ".join(tokens[lo:hi])
    return ("…" if lo > 0 else "") + piece + ("…" if hi < len(tokens) else "")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("query")
    ap.add_argument("--ar", action="store_true", help="search the Arabic text")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--words", type=int, default=10, help="words in the printed clause")
    ap.add_argument("--chapters", help="restrict, e.g. 1-20")
    args = ap.parse_args(argv)

    key = C.normalise(args.query)
    lo, hi = 1, 114
    if args.chapters:
        a, _, b = args.chapters.partition("-")
        lo, hi = int(a), int(b or a)
    hits = 0
    for n in range(lo, hi + 1):
        try:
            rows = C.verses(n)
        except Exception:
            continue
        for row in rows:
            text = row["ayah_ar"] if args.ar else row["ayah_en"]
            if key.lower() in C.normalise(text).lower():
                v = row["ayah_no_surah"]
                quoted = clause(C.normalise(text), args.words, key)
                print(f'({n}:{v} — **“{quoted}”**)')
                hits += 1
                if hits >= args.limit:
                    print(f"… stopped at {args.limit} hits")
                    return 0
    if not hits:
        print("no verse contains that wording", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
