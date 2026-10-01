#!/usr/bin/env python3
"""batch.py — gate for a batch of verses inside an unfinished chapter.

    python3 scripts/tafsir/batch.py 2 --through 20        # audit verses 2:1-2:20
    python3 scripts/tafsir/batch.py 2 --from 21 --to 40   # audit a later batch
    python3 scripts/tafsir/batch.py 2 --ranges 21-40,41-60,61-80
    python3 scripts/tafsir/batch.py 2 --through 20 --strict
    python3 scripts/tafsir/batch.py 2 --progress          # where the chapter stands

A long chapter is written in batches, and ``audit.py N`` cannot pass until the
last verse is written (the scaffold for the unwritten verses is TODO text, and
TODO fails the gate by design). This runs the same rule set but reports only
the findings that belong to the verses already written, so a batch can be
checked and corrected before the next one starts.

Batches have no dependency on one another, so several can be gated at once:
``--ranges A-B,C-D,...`` audits every range and runs them in parallel
(``--jobs``, default 4). The batch table shows, per verse, the words against its
floor, the share of the verse quoted in the prose, how many of its phrases are
quoted, how many quoted phrases are still missing evidence beside them, and
whether the verse carries a relatable analogy.

By default, exit status is 0 only when the mechanical gate and the independent
Chapter-1 parity gate both pass. That semantic gate compares every available source,
groups duplicate witnesses into distinct points, accounts for omissions, and checks
substantive claims, Qur'an citations, and transmitted evidence for support and
relevance. ``--draft`` runs the mechanical checks alone while prose is being assembled.
``--push-check`` additionally requires synchronized pending review scaffolds and is
used immediately before every review-candidate commit and push. Neither mode grants
acceptance. Independent review checkpoints contain no more than fifty newly written
verses; automatic quality alarms still use fifty-verse windows.
"""

from __future__ import annotations

import argparse
import sys
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402
import audit as A  # noqa: E402
import quality as Q  # noqa: E402


def verse_stats(doc, chapter, verses):
    rows = []
    smap = doc.section_map()
    for v in verses:
        section = smap[v]
        body = section.body()
        verse_words = len(C.words(C.ayah_en(chapter, v)))
        floor = A.verse_floor(verse_words)
        st = A.phrase_stats(chapter, section)
        phrases = C.split_phrases(C.ayah_en(chapter, v)) or [C.ayah_en(chapter, v)]
        rows.append({
            "ref": section.ref,
            "words": doc.words(body),
            "floor": floor,
            "coverage": st["coverage"],
            "quoted": len(phrases) - st["missing"],
            "phrases": len(phrases),
            "evidence_missing": st["evidence_missing"],
            "analogy": bool(A.ANALOGY.search(body)),
            "todo": "TODO" in body,
        })
    return rows


def run_range(chapter, start, end, opts):
    """Audit one range of verses; returns the report as a list of lines plus the verdict."""
    doc = C.load_chapter_doc(chapter)
    all_verses = [s.verse for s in doc.sections]
    smap = doc.section_map()
    pending = [v for v in all_verses if start <= v <= end and "TODO" in smap[v].body()]
    written = [v for v in all_verses if start <= v <= end and v not in pending]

    lines = []
    if not written:
        lines.append("no written verses in %d:%d-%d — write a batch first" % (chapter, start, end))
        return {"lines": lines, "fails": 1, "warns": 0, "pending": pending, "ok": False,
                "range": (start, end), "written": written}

    # Only the written verses of this range are reported below, so only they need the (costly,
    # advisory) grounding check. A per-call copy: ``--ranges`` runs ranges in parallel threads.
    scoped = types.SimpleNamespace(**vars(opts), only_verses=set(written))
    findings = A.audit_chapter(chapter, scoped)

    # which verse does a given file line belong to? (the introduction owns everything above 1)
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
        if f.line and f.code.startswith(("REP-", "STY-DICTION", "MTCH-")):
            verse = owner.get(f.line)
            if verse is not None and verse not in written:
                continue                       # the scaffold of an unwritten verse
            if verse is not None:              # a line inside a written verse: report it with its batch
                key = (f.code, f.ref, f.line, f.message)
                if key not in seen:
                    kept.append(f); seen.add(key)
                continue
        if f.code.startswith(("WRD-INTRO", "FMT-INTRO")) or (f.line and f.line <= intro_end):
            key = (f.code, f.ref, f.line, f.message)
            if key not in seen:
                kept.append(f); seen.add(key)

    order = {A.FAIL: 0, A.WARN: 1, A.INFO: 2}
    for f in sorted(kept, key=lambda f: (order[f.level], f.line, f.code)):
        line = "L%-5d" % f.line if f.line else "      "
        lines.append("%-4s %-20s %-7s %s %s" % (f.level, f.code, f.ref, line, f.message))
    if not kept:
        lines.append("mechanical gate clean")

    quality_findings = []
    if opts.draft:
        lines.append("DRAFT ONLY — all-source synthesis, Chapter-1 parity, claim and evidence review not yet applied")
    elif opts.push_check:
        checked_findings, _quality_metrics = Q.evaluate(
            chapter, written, require_reviews=False, push_check=True)
        quality_findings.extend(checked_findings)
        if quality_findings:
            lines.append("")
            lines.append("PUSH CHECK FAILED — REPAIR BEFORE COMMIT AND PUSH")
            lines.append("last independently accepted verse: %d:%d" %
                         (chapter, Q.accepted_frontier(chapter)))
            for finding in quality_findings:
                lines.append("BLOCK %-28s %-12s %s" %
                             (finding.code, finding.ref, finding.message))
        else:
            lines.append("PUSH CHECK PASS — pending review is allowed; this is not acceptance")
    else:
        if chapter != Q.BASELINE_CHAPTER and len(written) > Q.REVIEW_CHECKPOINT_SIZE:
            quality_findings.append(Q.Finding(
                "QTY-CHECKPOINT-SIZE", "%d:%d-%d" % (chapter, min(written), max(written)),
                "acceptance checkpoints contain at most %d verses; review them in order" %
                Q.REVIEW_CHECKPOINT_SIZE, tuple(written)))
        checked_findings, _quality_metrics = Q.evaluate(chapter, written, require_reviews=True)
        quality_findings.extend(checked_findings)
        if quality_findings:
            lines.append("")
            lines.append("QUALITY DRIFT — ACCEPTANCE AND PUBLICATION STOPPED")
            lines.append("last independently accepted verse: %d:%d" %
                         (chapter, Q.accepted_frontier(chapter)))
            for finding in quality_findings:
                lines.append("BLOCK %-28s %-12s %s" %
                             (finding.code, finding.ref, finding.message))
        else:
            lines.append("QUALITY PARITY PASS — independently reviewed against chapter 1")

    stats = verse_stats(doc, chapter, written)
    lines.append("")
    lines.append("%-7s %6s %6s %9s %8s %5s %8s" % ("verse", "words", "floor", "coverage", "phrases", "evid", "analogy"))
    for r in stats:
        lines.append("%-7s %6d %6d %8.0f%% %8s %5s %8s"
                     % (r["ref"], r["words"], r["floor"], r["coverage"] * 100,
                        "%d/%d" % (r["quoted"], r["phrases"]),
                        "0" if not r["evidence_missing"] else str(r["evidence_missing"]),
                        "yes" if r["analogy"] else "NO"))

    prose = "\n".join(A._prose_only(smap[v].body()) for v in written)
    m = C.style_metrics(prose)
    lines.append("")
    lines.append("batch style: mean sentence %.1f words | %d%% over 40 words | Flesch %.0f | long words %.2f%% | analogies %d/%d"
                 % (m["mean_sentence"], 100 * m["long_sentence_share"], m["flesch"],
                    100 * m["long_word_share"], sum(1 for r in stats if r["analogy"]), len(stats)))

    mechanical_fails = sum(1 for f in kept if f.level == A.FAIL)
    warns = sum(1 for f in kept if f.level == A.WARN)
    quality_blocks = len(quality_findings)
    fails = mechanical_fails + quality_blocks
    bad = fails + (warns if opts.strict else 0)
    lines.append("")
    lines.append("batch %d:%d-%d — %d verses written, %d pending | %d mechanical FAIL, "
                 "%d quality BLOCK, %d WARN | RESULT: %s"
                 % (chapter, start, end, len(written), len(pending), mechanical_fails,
                    quality_blocks, warns, "PASS" if not bad else "FAIL"))
    if pending:
        lines.append("keep going: write %d:%d next, then re-run this gate" % (chapter, pending[0]))
    elif opts.draft:
        lines.append("draft range complete — create or refresh its review template, complete the review pass, then run the full gate")
    elif opts.push_check:
        lines.append("checkpoint ready — commit and push now; finish the review pass, post the statistics, and carry on")
    else:
        lines.append("accepted range complete — run the chapter gate only when the whole chapter is written")
    if opts.draft:
        lines.append("if generation stops here, do not leave it local: scaffold review, push-check, commit, and push")
    return {"lines": lines, "fails": fails, "warns": warns, "pending": pending,
            "ok": not bad, "range": (start, end), "written": written}


def parse_ranges(spec, chapter):
    """'21-40,41-60,61' -> [(21, 40), (41, 60), (61, 61)]"""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.append((int(a), int(b)))
        else:
            out.append((int(part), int(part)))
    for a, b in out:
        if a < 1 or b < a:
            raise SystemExit("bad range %d-%d for chapter %d" % (a, b, chapter))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--to", dest="end", type=int)
    ap.add_argument("--through", type=int, help="audit verses 1..N (short for --from 1 --to N)")
    ap.add_argument("--ranges", help="several independent batches at once, e.g. 21-40,41-60,61-80")
    ap.add_argument("--jobs", type=int, default=4, help="how many ranges to audit in parallel (default 4)")
    ap.add_argument("--progress", action="store_true", help="print where the chapter stands and exit")
    ap.add_argument("--strict", action="store_true", help="mechanical warnings fail the batch too")
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument("--draft", action="store_true",
                       help="run mechanical checks only while drafting; never counts as quality acceptance")
    modes.add_argument("--push-check", action="store_true",
                       help="validate synchronized pending review scaffolds before a required checkpoint push")
    ap.add_argument("--no-grounding", action="store_true")
    args = ap.parse_args(argv)

    doc = C.load_chapter_doc(args.chapter)
    all_verses = [s.verse for s in doc.sections]
    if not args.ranges:
        if args.through:
            args.start, args.end = 1, args.through
        if args.end is None:
            args.end = max(all_verses)

    if args.progress:
        pending = [v for v in all_verses if "TODO" in doc.section_map()[v].body()]
        done = [v for v in all_verses if v not in pending]
        print("%s %s: %d of %d verses written (%d pending)"
              % (C.pad3(args.chapter), C.chapter_name(args.chapter), len(done), len(all_verses),
                 len(pending)))
        nxt = next((v for v in all_verses if v not in done), None)
        print("next verse to write: %s" % ("%d:%d" % (args.chapter, nxt) if nxt else "none — chapter complete"))
        return 0

    ranges = parse_ranges(args.ranges, args.chapter) if args.ranges else [(args.start, args.end)]
    opts = types.SimpleNamespace(no_grounding=args.no_grounding, strict=args.strict,
                                 draft=args.draft, push_check=args.push_check)

    if len(ranges) == 1:
        report = run_range(args.chapter, ranges[0][0], ranges[0][1], opts)
        print("\n".join(report["lines"]))
        return 0 if report["ok"] else 1

    jobs = max(1, min(args.jobs, len(ranges)))
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        reports = list(pool.map(lambda r: run_range(args.chapter, r[0], r[1], opts), ranges))

    for report in reports:
        print("#" * 72)
        print("## batch %d:%d-%d" % (args.chapter, report["range"][0], report["range"][1]))
        print("\n".join(report["lines"]))
        print("")
    fails = sum(r["fails"] for r in reports)
    warns = sum(r["warns"] for r in reports)
    bad = [r for r in reports if not r["ok"]]
    print("#" * 72)
    print("%d batches in parallel (%d jobs): %d FAIL, %d WARN | RESULT: %s"
          % (len(reports), jobs, fails, warns, "PASS" if not bad else "FAIL"))
    if bad:
        print("failing batches: %s" % ", ".join("%d:%d-%d" % (args.chapter, r["range"][0], r["range"][1])
                                                for r in bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
