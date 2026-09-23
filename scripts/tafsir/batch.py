#!/usr/bin/env python3
"""batch.py — gate for a batch of verses inside an unfinished chapter.

    python3 scripts/tafsir/batch.py 2 --through 20        # audit verses 2:1-2:20
    python3 scripts/tafsir/batch.py 2 --from 21 --to 40   # audit a later batch
    python3 scripts/tafsir/batch.py 2 --through 20 --strict
    python3 scripts/tafsir/batch.py 2 --progress          # where the chapter stands

A long chapter is written in batches, and ``audit.py N`` cannot pass until the
last verse is written (the scaffold for the unwritten verses is TODO text, and
TODO fails the gate by design). This runs the same rule set but reports only
the findings that belong to the verses already written, so a batch can be
checked and corrected before the next one starts.

Exit status is 0 when no finding in the selected range is a FAIL (no WARN
either, under ``--strict``).
"""

from __future__ import annotations

import argparse
import types
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402
import audit as A  # noqa: E402


def verse_stats(doc, chapter, verses):
    rows = []
    for section in doc.sections:
        if section.verse not in verses:
            continue
        body = section.body()
        verse_words = len(C.words(C.ayah_en(chapter, section.verse)))
        floor = A.verse_floor(verse_words)
        heads = [h for _, h in section.headings() if h.startswith("\u201c")]
        verse_norm = C.loose_norm(C.ayah_en(chapter, section.verse))
        pos, covered = 0, 0
        for h in heads:
            phrase = C.loose_norm(h.strip("\u201c\u201d"))
            i = verse_norm.find(phrase, pos)
            if i >= 0:
                covered += len(phrase)
                pos = i + len(phrase)
        rows.append({
            "ref": section.ref,
            "words": doc.words(body),
            "floor": floor,
            "coverage": (covered / len(verse_norm)) if verse_norm else 0.0,
            "phrases": len(heads),
            "analogy": bool(A.ANALOGY.search(body)),
            "todo": "TODO" in body,
        })
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--to", dest="end", type=int)
    ap.add_argument("--through", type=int, help="audit verses 1..N (short for --from 1 --to N)")
    ap.add_argument("--progress", action="store_true", help="print where the chapter stands and exit")
    ap.add_argument("--strict", action="store_true", help="warnings fail the batch too")
    ap.add_argument("--no-grounding", action="store_true")
    args = ap.parse_args(argv)

    doc = C.load_chapter_doc(args.chapter)
    all_verses = [s.verse for s in doc.sections]
    if args.through:
        args.start, args.end = 1, args.through
    if args.end is None:
        args.end = max(all_verses)

    pending = [v for v in all_verses if v >= args.start and v <= args.end and "TODO" in doc.section_map()[v].body()]
    written = [v for v in all_verses if v >= args.start and v <= args.end and v not in pending]

    if args.progress:
        done = [v for v in all_verses if "TODO" not in doc.section_map()[v].body()]
        print("%s %s: %d of %d verses written (%d pending, %d in this range)"
              % (C.pad3(args.chapter), C.chapter_name(args.chapter), len(done), len(all_verses),
                 len(all_verses) - len(done), len(pending)))
        nxt = next((v for v in all_verses if v not in done), None)
        print("next verse to write: %s" % ("%d:%d" % (args.chapter, nxt) if nxt else "none — chapter complete"))
        return 0

    if not written:
        print("no written verses in %d:%d-%d — write a batch first" % (args.chapter, args.start, args.end))
        return 1

    opts = types.SimpleNamespace(no_grounding=args.no_grounding)
    findings = A.audit_chapter(args.chapter, opts)

    # which verse does a given file line belong to? (the introduction owns everything above 2:1)
    owner, intro_end = {}, 0
    for section in doc.sections:
        for ln in range(section.start, section.end + 1):
            owner[ln] = section.verse
        intro_end = min(intro_end or section.start, section.start)

    # chapter-level metrics (analogy share, sentence length, reading ease) describe the whole
    # sūrah, so they cannot be judged until it is finished; they are measured on the batch below.
    WHOLE_CHAPTER = {"STY-ANALOGY", "STY-SENTENCE", "STY-SENTENCE-LONG", "STY-READABILITY", "STY-LONGWORDS"}

    kept, seen = [], set()
    for f in findings:
        if ":" in f.ref:                       # a verse's own finding
            verse = int(f.ref.split(":")[-1])
            if verse in written:
                key = (f.code, f.ref, f.line, f.message)
                if key not in seen:
                    kept.append(f); seen.add(key)
            continue
        if f.code in WHOLE_CHAPTER and not f.line:
            continue                           # measured across the unfinished chapter: skip
        if f.line and f.code.startswith(("REP-", "DICTION")):
            verse = owner.get(f.line)
            if verse is not None and verse not in written:
                continue                       # the scaffold of an unwritten verse
        if f.code.startswith(("WRD-INTRO", "FMT-INTRO")) or (f.line and f.line <= intro_end):
            key = (f.code, f.ref, f.line, f.message)
            if key not in seen:
                kept.append(f); seen.add(key)

    order = {A.FAIL: 0, A.WARN: 1, A.INFO: 2}
    for f in sorted(kept, key=lambda f: (order[f.level], f.line, f.code)):
        line = "L%-5d" % f.line if f.line else "      "
        print("%-4s %-20s %-7s %s %s" % (f.level, f.code, f.ref, line, f.message))
    if not kept:
        print("clean")

    stats = verse_stats(doc, args.chapter, written)
    print("")
    print("%-7s %6s %6s %9s %8s %8s" % ("verse", "words", "floor", "coverage", "phrases", "analogy"))
    for r in stats:
        print("%-7s %6d %6d %8.0f%% %8d %8s"
              % (r["ref"], r["words"], r["floor"], r["coverage"] * 100, r["phrases"],
                 "yes" if r["analogy"] else "NO"))

    prose = "\n".join(A._prose_only(s.body()) for s in doc.sections if s.verse in written)
    m = C.style_metrics(prose)
    print("")
    print("batch style: mean sentence %.1f words | %d%% over 40 words | Flesch %.0f | long words %.2f%% | analogies %d/%d"
          % (m["mean_sentence"], 100 * m["long_sentence_share"], m["flesch"],
             100 * m["long_word_share"], sum(1 for r in stats if r["analogy"]), len(stats)))

    fails = sum(1 for f in kept if f.level == A.FAIL)
    warns = sum(1 for f in kept if f.level == A.WARN)
    bad = fails + (warns if args.strict else 0)
    print("")
    print("batch %d:%d-%d — %d verses written, %d pending | %d FAIL, %d WARN | RESULT: %s"
          % (args.chapter, args.start, args.end, len(written), len(pending), fails, warns,
             "PASS" if not bad else "FAIL"))
    if pending:
        nxt = pending[0]
        print("keep going: write %d:%d next, then re-run this gate" % (args.chapter, nxt))
    else:
        print("batch complete — run the chapter gate: python3 scripts/tafsir/audit.py %d" % args.chapter)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
