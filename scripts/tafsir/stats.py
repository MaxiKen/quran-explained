#!/usr/bin/env python3
"""stats.py — the statistics posted with every push.

The author's standing order (2026-10-01): the AI writes, reviews its own range, posts
the statistics, pushes to GitHub and carries on without waiting; the author reads the
result afterwards and asks for a change if it is not right.  This is the posting step.

    python3 scripts/tafsir/stats.py 2 --from 1 --to 50            # print the report
    python3 scripts/tafsir/stats.py 2 --from 1 --to 50 --write    # save quality/stats/002/001-050.md

Every number comes from the gate's own measurements (``quality.metrics``, the auditor's
word counter and floor), so the report cannot disagree with ``audit.py`` or ``quality.py``.

The report compares the range with three things, and keeps two kinds of measure apart:

* **Writing style — measured against Chapter 1.**  Mean sentence length, the share of
  sentences over forty words, and readability, each against the frozen alarm in
  ``quality/chapter-001-baseline.json``.  These are the only measures Chapter 1 sets.
* **Content and evidence — information only.**  Words per verse, the share of each
  verse's floor, Qur'an cross-references and named authorities per 1,000 words.  They
  are shown beside Chapter 1, the earlier verses of the same chapter and the other
  written chapters so the author can see how they compare, but Chapter 1 is *not* the
  yardstick for them and nothing here blocks anything.
* **Source coverage — from the review record, when one exists.**  Per work: how many of
  the range's verses had text, and how many material points were included or omitted.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402
import quality as Q  # noqa: E402

STATS_DIR = C.REPO / "quality" / "stats"


def written_sections(chapter: int):
    """``(doc, {verse: section})`` for the verses of ``chapter`` that hold finished prose."""
    doc = C.load_chapter_doc(chapter)
    if doc is None:
        return None, {}
    return doc, {s.verse: s for s in doc.sections if Q._written(s)}


def floor_for(chapter: int, verse: int) -> int:
    return A.verse_floor(len(C.words(C.ayah_en(chapter, verse))))


def summarise(chapter: int, doc, sections) -> dict:
    """Style metrics plus the content/evidence figures for a set of sections."""
    sections = list(sections)
    if not sections:
        return {}
    m = Q.metrics(sections)
    words = [doc.words(s.body()) for s in sections]
    floors = [floor_for(chapter, s.verse) for s in sections]
    share = [w / f for w, f in zip(words, floors)]
    return {
        "verses": len(sections),
        "mean_sentence": m["mean_sentence"],
        "long_sentence_share": m["long_sentence_share"],
        "flesch": m["flesch"],
        "words_per_verse": sum(words) / len(words),
        "min_words": min(words),
        "max_words": max(words),
        "floor_share": sum(share) / len(share),
        "min_floor_share": min(share),
        "refs_per_verse": m["quran_references"] / len(sections),
        "authorities_per_1000": m["authority_mentions_per_1000"],
        "refs_per_1000": m["quran_references_per_1000"],
        "evidence_per_1000": m["evidence_mentions_per_1000"],
    }


def pooled_other_chapters(skip: set) -> tuple:
    """Every written verse of every chapter except those in ``skip``, summarised together."""
    rows, chapters = [], 0
    for n in C.chapter_numbers():
        if n in skip:
            continue
        doc, smap = written_sections(n)
        if not smap:
            continue
        chapters += 1
        rows.append((n, doc, [smap[v] for v in sorted(smap)]))
    if not rows:
        return {}, 0
    # pool by recomputing over all sections; words/floors need each chapter's own doc
    all_sections = [s for _n, _doc, secs in rows for s in secs]
    m = Q.metrics(all_sections)
    words, floors = [], []
    for n, doc, secs in rows:
        for s in secs:
            words.append(doc.words(s.body()))
            floors.append(floor_for(n, s.verse))
    share = [w / f for w, f in zip(words, floors)]
    out = {
        "verses": len(all_sections),
        "mean_sentence": m["mean_sentence"],
        "long_sentence_share": m["long_sentence_share"],
        "flesch": m["flesch"],
        "words_per_verse": sum(words) / len(words),
        "min_words": min(words),
        "max_words": max(words),
        "floor_share": sum(share) / len(share),
        "min_floor_share": min(share),
        "refs_per_verse": m["quran_references"] / len(all_sections),
        "authorities_per_1000": m["authority_mentions_per_1000"],
        "refs_per_1000": m["quran_references_per_1000"],
        "evidence_per_1000": m["evidence_mentions_per_1000"],
    }
    return out, chapters


def fmt(value, kind: str) -> str:
    if value is None:
        return "—"
    if kind == "pct":
        return "%.1f%%" % (100 * value)
    if kind == "int":
        return "{:,.0f}".format(value)
    if kind == "f0":
        return "%.0f" % value
    return "%.1f" % value


def row(label: str, key: str, kind: str, cols) -> str:
    cells = [fmt(c.get(key) if c else None, kind) for c in cols]
    return "| %s | %s |" % (label, " | ".join(cells))


def source_coverage(chapter: int, verses) -> list:
    """Per-work coverage lines from the review record, or an explanatory line."""
    reviews, _errors = Q.load_reviews()
    items = [(v, reviews.get((chapter, v))) for v in verses]
    have = [(v, it) for v, it in items if it]
    if not have:
        return ["No review record exists for this range yet."]
    status = {}
    reviewers = set()
    for _v, (review, entry, _path) in have:
        status[entry.get("status", "?")] = status.get(entry.get("status", "?"), 0) + 1
        who = str(review.get("reviewer", "")).strip()
        if who:
            reviewers.add(who)
    lines = ["Review record: %s of %d verses%s." % (
        ", ".join("%d %s" % (n, s) for s, n in sorted(status.items())), len(verses),
        "; reviewer: " + ", ".join(sorted(reviewers)) if reviewers else "; no reviewer named yet")]
    per = {slug: {"verses": 0, "included": 0, "omitted": 0} for slug in C.SOURCE_ALLOWLIST}
    for _v, (_review, entry, _path) in have:
        synthesis = entry.get("source_synthesis") or {}
        for slug in synthesis.get("available_sources") or []:
            if slug in per:
                per[slug]["verses"] += 1
        for point in synthesis.get("distinct_material_evidence") or []:
            decision = point.get("decision")
            for slug in point.get("sources") or []:
                if slug in per and decision in ("included", "omitted"):
                    per[slug][decision] += 1
    lines += ["", "| Work | Verses with text | Points included | Points omitted |", "|---|---|---|---|"]
    for slug in C.SOURCE_ALLOWLIST:
        p = per[slug]
        lines.append("| %s | %d | %d | %d |" % (slug, p["verses"], p["included"], p["omitted"]))
    return lines


def report(chapter: int, start: int, end: int) -> str:
    doc, smap = written_sections(chapter)
    if doc is None:
        raise SystemExit("chapter %d has no file" % chapter)
    verses = [v for v in range(start, end + 1) if v in smap]
    if not verses:
        raise SystemExit("no written verses in %d:%d-%d" % (chapter, start, end))
    sections = [smap[v] for v in verses]
    this = summarise(chapter, doc, sections)

    baseline, _problems = Q.load_baseline()
    earlier = summarise(chapter, doc, [smap[v] for v in sorted(smap) if v < start])
    others, n_other = pooled_other_chapters({chapter, Q.BASELINE_CHAPTER})

    # Chapter 1 as it stands on disk (information columns) and as frozen (style alarms)
    c1_doc, c1_map = written_sections(Q.BASELINE_CHAPTER)
    c1 = summarise(Q.BASELINE_CHAPTER, c1_doc, [c1_map[v] for v in sorted(c1_map)]) if c1_map else {}

    title = "%s (chapter %d), verses %d–%d" % (C.chapter_name(chapter), chapter, verses[0], verses[-1])
    head = ("Chapter %d · verses %d–%d · %d verses · %s words (%s a verse, %s of floor) · "
            "mean sentence %.1f · Flesch %.0f · evidence %.1f per 1,000" % (
                chapter, verses[0], verses[-1], len(verses),
                fmt(this["words_per_verse"] * len(verses), "int"), fmt(this["words_per_verse"], "int"),
                fmt(this["floor_share"], "pct"), this["mean_sentence"], this["flesch"],
                this["evidence_per_1000"]))
    out = ["# Statistics — %s" % title, "", "*%s · generated by `scripts/tafsir/stats.py`*" %
           datetime.date.today().isoformat(), "", "> " + head, ""]

    out += ["## Writing style — measured against Chapter 1", ""]
    if baseline:
        t = baseline["thresholds"]
        bm = baseline["metrics"]
        out += ["| Measure | This range | Chapter 1 | Alarm | Status |", "|---|---|---|---|---|"]
        checks = [
            ("Mean sentence length (words)", this["mean_sentence"], bm["mean_sentence"],
             "above %.1f" % t["mean_sentence_max"], this["mean_sentence"] > t["mean_sentence_max"], "f1"),
            ("Sentences over 40 words", this["long_sentence_share"], bm["long_sentence_share"],
             "above %.1f%%" % (100 * t["long_sentence_share_max"]),
             this["long_sentence_share"] > t["long_sentence_share_max"], "pct"),
            ("Flesch reading ease", this["flesch"], bm["flesch"],
             "below %.0f" % t["flesch_min"], this["flesch"] < t["flesch_min"], "f0"),
        ]
        for label, mine, theirs, alarm, tripped, kind in checks:
            out.append("| %s | %s | %s | %s | %s |" % (
                label, fmt(mine, kind), fmt(theirs, kind), alarm, "**ALARM**" if tripped else "ok"))
    else:
        out.append("The Chapter-1 record could not be loaded, so no style comparison is possible.")
    out += ["", "The alarms are the gate's own, from `quality/chapter-001-baseline.json`; the gate applies them "
            "per fifty-verse window.", ""]

    cols = [this, c1, earlier, others]
    out += ["## Content and evidence — information only", "",
            "Chapter 1 is **not** the yardstick for these (owner's instruction, 2026-10-01); they are shown "
            "so the comparison can be seen. Nothing here blocks a push.", "",
            "| Measure | This range | Chapter 1 | Earlier verses of this chapter | Other written chapters |",
            "|---|---|---|---|---|",
            row("Verses written", "verses", "int", cols),
            row("Words per verse (mean)", "words_per_verse", "int", cols),
            row("Shortest verse (words)", "min_words", "int", cols),
            row("Longest verse (words)", "max_words", "int", cols),
            row("Share of the verse's floor (mean)", "floor_share", "pct", cols),
            row("Lowest share of floor", "min_floor_share", "pct", cols),
            row("Qur'an cross-references per verse", "refs_per_verse", "f1", cols),
            row("Qur'an cross-references per 1,000 words", "refs_per_1000", "f1", cols),
            row("Named authorities per 1,000 words", "authorities_per_1000", "f1", cols),
            row("Evidence mentions per 1,000 words", "evidence_per_1000", "f1", cols), "",
            "*Other written chapters: %s.*" % (
                "%d chapter%s, %d verses, Chapter 1 excluded" % (n_other, "" if n_other == 1 else "s",
                                                                  others["verses"]) if others
                else "none written yet"), ""]

    out += ["## Each verse", "",
            "| Verse | Words | Floor | Share of floor | Mean sentence | Flesch | Cross-refs | Authorities |",
            "|---|---|---|---|---|---|---|---|"]
    for v in verses:
        s = smap[v]
        m = Q.metrics([s])
        words = doc.words(s.body())
        floor = floor_for(chapter, v)
        out.append("| %d:%d | %s | %s | %s | %.1f | %.0f | %d | %d |" % (
            chapter, v, fmt(words, "int"), fmt(floor, "int"), fmt(words / floor, "pct"),
            m["mean_sentence"], m["flesch"], m["quran_references"], m["authority_mentions"]))
    out += ["", "## Source coverage", ""] + source_coverage(chapter, verses) + [""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--to", dest="end", type=int, default=0)
    ap.add_argument("--write", action="store_true",
                    help="save to quality/stats/NNN/AAA-BBB.md instead of printing")
    ap.add_argument("--out", help="save to this path instead of printing")
    args = ap.parse_args(argv)
    end = args.end or C.verse_count(args.chapter)
    text = report(args.chapter, args.start, end)
    target = None
    if args.out:
        target = Path(args.out)
    elif args.write:
        target = STATS_DIR / C.pad3(args.chapter) / ("%03d-%03d.md" % (args.start, end))
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
        print("wrote %s" % target)
        print(text.split("\n> ", 1)[1].split("\n", 1)[0] if "\n> " in text else "")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
