#!/usr/bin/env python3
"""Corpus status: what is written, how big, and whether it passes the gate.

    python3 scripts/tafsir/status.py              # one line per chapter
    python3 scripts/tafsir/status.py --md         # markdown table for TAFSIR_WORKLOG.md
    python3 scripts/tafsir/status.py --json       # machine-readable
    python3 scripts/tafsir/status.py 1 2 3        # selected chapters, with detail

Detail rows give words per verse, evidence kinds per verse and the audit
verdict, so a worklog entry can be filled from the tool's output rather than
from memory.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402


def chapter_stats(n: int):
    doc = C.load_chapter_doc(n)
    if doc is None:
        return None
    findings = A.audit_chapter(n, _Opts())
    fails = [f for f in findings if f.level == A.FAIL]
    warns = [f for f in findings if f.level == A.WARN]
    # a scaffold is not "written": sections still carrying TODO are reported as pending
    written = [s for s in doc.sections if "TODO" not in s.body()]
    todo = [s for s in doc.sections if "TODO" in s.body()]
    words = [doc.words(s.body()) for s in written]
    payload = C.DATA_DIR / ("tafsir_%s.json" % C.pad3(n))
    return {
        "chapter": n,
        "name": C.chapter_name(n),
        "verses": len(written),
        "scaffolded": len(todo),
        "expected": C.verse_count(n),
        "intro_words": doc.words(doc.intro),
        "words": sum(words),
        "min_words": min(words) if words else 0,
        "median_words": sorted(words)[len(words) // 2] if words else 0,
        "max_words": max(words) if words else 0,
        "fail": len(fails),
        "warn": len(warns),
        "codes": sorted({f.code for f in fails}) if not todo else ["unwritten verses"],
        "in_progress": bool(todo),
        "payload": payload.exists(),
        "payload_bytes": payload.stat().st_size if payload.exists() else 0,
    }


class _Opts:
    no_grounding = True          # status must stay fast: grounding is for audit runs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapters", nargs="*", type=int)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)

    nums = args.chapters or list(C.chapter_numbers())
    rows = [chapter_stats(n) for n in nums]
    done = [r for r in rows if r]

    if args.json:
        print(json.dumps(done, ensure_ascii=False, indent=2))
        return 0

    if args.md:
        print("| Ch | File | Verses | Words | Range (min/med/max) | Gate |")
        print("|---|---|---|---|---|---|")
        for r in done:
            if r["in_progress"]:
                gate = "in progress (%d verses still scaffold)" % r["scaffolded"]
            else:
                gate = "PASS" if r["fail"] == 0 else "FAIL (%s)" % ", ".join(r["codes"])
            print("| %d | `tafsir/%s.md` | %d/%d | %s | %d/%d/%d | %s |"
                  % (r["chapter"], C.pad3(r["chapter"]), r["verses"], r["expected"],
                     format(r["words"], ","), r["min_words"], r["median_words"], r["max_words"], gate))
        finished = [r for r in done if not r["in_progress"]]
        print("")
        print("| | | %d/114 | %s | | |"
              % (len(finished), format(sum(r["words"] for r in finished), ",")))
        return 0

    for r in done:
        gate = "PASS" if r["fail"] == 0 else "FAIL"
        print("%s  %-14s %3d/%-3d verses  %7s words  %4d/%4d/%4d  %s%s"
              % (C.pad3(r["chapter"]), r["name"][:14], r["verses"], r["expected"],
                 format(r["words"], ","), r["min_words"], r["median_words"], r["max_words"],
                 gate, ("  " + ", ".join(r["codes"])) if r["codes"] else ""))
    if len(done) > 1:
        finished = [r for r in done if not r["in_progress"]]
        print("")
        print("chapters written: %d/114 | words: %s | passing: %d"
              % (len(finished), format(sum(r["words"] for r in finished), ","),
                 sum(1 for r in finished if r["fail"] == 0)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
