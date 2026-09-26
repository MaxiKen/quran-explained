#!/usr/bin/env python3
"""run.py — the fifty-verse run: plan it, map it from the eleven, finish it.

v7.2 organises the work in **runs of fifty verses** (``RUN_VERSE_TARGET``). A run
may span chapters; it starts at the first verse not yet written and takes the next
fifty in chapter order, so the first run is 1:1-1:7 followed by 2:1-2:43.

The point of the run is speed and coverage:

* **map once, at the start.** ``--build`` pulls all eleven works for the whole run
  in one pass — the sources are opened once for fifty verses, not once per verse —
  and writes the run's map plus the per-chapter digests the auditor reads.
* **finish before pausing.** ``--check`` exits 0 only when every verse of the run
  is written and clean. The run is the unit of work: it is not left half-done.

    python3 scripts/tafsir/run.py --plan                 # the next fifty verses
    python3 scripts/tafsir/run.py --build                # map them from the eleven
    python3 scripts/tafsir/run.py --slice 1:1 2:10       # read part of the map
    python3 scripts/tafsir/run.py --status               # words, floors, gate state
    python3 scripts/tafsir/run.py --check                # is the run finished?

The plan is derived from the chapter files themselves, so nothing is lost if
``tmp/`` is wiped: the run is always "the next fifty verses", and ``--build``
rebuilds the map.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402
import scaffold as S  # noqa: E402
import sources as SRC  # noqa: E402

RUN_VERSE_TARGET = 50
RUNS_DIR = C.TMP_DIR / "runs"


# ------------------------------------------------------------------- the plan

def written_verses():
    """``{(chapter, verse)}`` for sections that hold finished prose."""
    out = set()
    for n in C.chapter_numbers():
        if not C.output_path(n).exists():
            continue
        for section in C.load_chapter_doc(n).sections:
            if "TODO" not in section.body():
                out.add((n, section.verse))
    return out


def first_unwritten():
    for n in C.chapter_numbers():
        if not C.output_path(n).exists():
            return (n, 1)
        doc = C.load_chapter_doc(n)
        smap = doc.section_map()
        for v in range(1, C.verse_count(n) + 1):
            section = smap.get(v)
            if section is None or "TODO" in section.body():
                return (n, v)
    return None


def global_index(chapter: int, verse: int) -> int:
    before = sum(C.verse_count(n) for n in range(1, chapter))
    return before + verse - 1


def read_manifest(index: int):
    """The pinned run's verses, or None if this run was never planned."""
    path = RUNS_DIR / ("run-%03d.json" % index)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        verses = []
        for ref in data.get("verses", []):
            chapter, verse = str(ref).split(":")
            verses.append((int(chapter), int(verse)))
    except Exception:
        return None
    return verses or None


def manifest_meta(index: int):
    """The pinned run's record (``start``, ``end``, ``target``), or ``{}``."""
    path = RUNS_DIR / ("run-%03d.json" % index)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_manifest(verses, index: int):
    """Pin the run: once it is planned, its fifty verses do not shift under the writer."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / ("run-%03d.json" % index)
    old = {}
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    old.update({
        "index": index,
        "target": len(verses),
        "start": "%d:%d" % verses[0] if verses else None,
        "end": "%d:%d" % verses[-1] if verses else None,
        "chapters": sorted({c for c, _ in verses}),
        "verses": ["%d:%d" % (c, v) for c, v in verses],
    })
    path.write_text(json.dumps(old, indent=2), encoding="utf-8")
    (RUNS_DIR / CURRENT).write_text(str(index), encoding="utf-8")   # the run in flight
    return old


def resolve_start(start=None):
    """Turn what the author said into a verse reference.

    * ``None`` — the frontier: the first verse of the Book that is still unwritten.
    * ``"N"`` — that chapter's first verse that is still unwritten (verse 1 when the
      chapter has not been started). A complete chapter is a stop, not a guess: the
      author names the next chapter or a chapter:verse.
    * ``"N:M"`` — exactly that verse, written or not.

    The author's start is authoritative: it is never quietly moved to the frontier.
    """
    if start is None:
        return first_unwritten()
    chapter, _, verse = str(start).partition(":")
    chapter = int(chapter)
    if not 1 <= chapter <= 114:
        raise SystemExit("chapter out of range: %s" % start)
    if verse:
        verse = int(verse)
        if not 1 <= verse <= C.verse_count(chapter):
            raise SystemExit("verse out of range: %s" % start)
        return (chapter, verse)
    if not C.output_path(chapter).exists():
        return (chapter, 1)
    smap = C.load_chapter_doc(chapter).section_map()
    for v in range(1, C.verse_count(chapter) + 1):
        section = smap.get(v)
        if section is None or "TODO" in section.body():
            return (chapter, v)
    raise SystemExit(
        "chapter %d is already complete \u2014 name a chapter:verse, or the chapter you want next"
        % chapter)


CURRENT = "current"


def current_index():
    """The index of the run in flight — the one the author pinned last."""
    path = RUNS_DIR / CURRENT
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def pinned_run(target: int = RUN_VERSE_TARGET):
    """Return the run the author pinned last, until another start is named.

    This is what ``--check``, ``--status`` and ``--slice`` read when the author has
    not named a start in the same breath. Merely writing the fiftieth verse must not
    release the pin: the run can still have gate failures, and ``--check`` must judge
    these same fifty. A later explicit ``--start`` is what replaces the run in hand.
    """
    index = current_index()
    verses = read_manifest(index) if index else None
    if verses:
        return verses, index
    return None, 0


def read_manifest_file(path):
    """The verses pinned in one manifest file, or ``None``."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [tuple(int(x) for x in str(ref).split(":")) for ref in data.get("verses", [])] or None
    except Exception:
        return None


def plan(target: int = RUN_VERSE_TARGET, start=None):
    """The run in flight: the pinned fifty if one is planned, else the fifty from ``start``.

    A run is fixed when it is planned (``--plan`` pins it, ``--build`` fills its
    map). Writing verses inside it does not move its goalposts: the fifty are
    finished before the writer pauses, and only then does the next run begin.

    ``start`` is what the author named. Naming a start that differs from the pinned
    run re-cuts it from there; naming the same one returns the run already in hand.
    """
    given = start is not None
    if not given:
        verses, index = pinned_run(target)
        if verses:
            return verses, index          # the author's pinned run is the run in flight
    anchor = resolve_start(start)
    if anchor is None:
        return [], 0
    index = 1 + global_index(*anchor) // target
    pinned = read_manifest(index)
    if pinned and manifest_meta(index).get("start") == "%d:%d" % anchor:
        return pinned, index              # the author named this run again
    verses, chapter = [], anchor[0]
    while len(verses) < target and chapter <= 114:
        first = anchor[1] if chapter == anchor[0] else 1
        for verse in range(first, C.verse_count(chapter) + 1):
            if len(verses) >= target:
                break
            verses.append((chapter, verse))
        chapter += 1
    if given:
        save_manifest(verses, index)      # naming a start pins it, even outside --plan
    return verses, index


def ranges(verses):
    """Group a run into ``[(chapter, first, last, count)]`` per chapter."""
    out = []
    for chapter, verse in verses:
        if out and out[-1][0] == chapter and out[-1][2] == verse - 1:
            out[-1][2] = verse
            out[-1][3] += 1
        else:
            out.append([chapter, verse, verse, 1])
    return [tuple(r) for r in out]


def floor_of(chapter, verse):
    return A.verse_floor(len(C.words(C.ayah_en(chapter, verse))))


def show_plan(verses, index, target: int, start=None) -> None:
    if not verses:
        print("corpus complete — every verse of every chapter is written")
        return
    print("run %d \u2014 %d verses in chapter order, %d chapter(s)%s"
          % (index, len(verses), len({c for c, _ in verses}),
             " \u2014 from %d:%d (the author's start)" % verses[0] if start else ""))
    total = 0
    for chapter, first, last, count in ranges(verses):
        floors = [floor_of(chapter, v) for v in range(first, last + 1)]
        total += sum(f for f in floors if f)
        print("  %d:%-8s %3d verses   floors %d\u2013%d words   total %6d"
              % (chapter, "%d\u2013%d" % (first, last) if first != last else str(first),
                 count, min(floors), max(floors), sum(floors)))
    print("  the run's word floor: %d words (material may carry more)" % total)
    manifest = RUNS_DIR / ("run-%03d.json" % index)
    print("  plan written to %s" % manifest.relative_to(C.REPO) if manifest.exists()
          else "  next: python3 scripts/tafsir/run.py --build")


# ------------------------------------------------------------------- the map

def build_map(verses, index, cap_en, cap_ar, cap_json, quiet=False):
    """Digest the eleven works for the run's chapters, then write the run map.

    The run map (``tmp/runs/run-NNN.txt``) is the reading material, capped so it
    stays readable. The per-chapter digests (``tmp/sources/NNN.json``) are what
    the auditor's grounding check reads — names, not length — so they are capped
    hard as well, which is what keeps a whole 286-verse chapter cheap to build.
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = C.TMP_DIR / "sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    chapters = sorted({c for c, _ in verses})
    catalog = C.source_catalog()
    data = {}                                # 'C:V' -> {slug: text}
    for chapter in chapters:
        catalog, chapter_data = SRC.build(chapter)
        txt = SRC.digest_text(chapter, catalog, chapter_data, cap_en, cap_ar)
        (out_dir / ("%s.txt" % C.pad3(chapter))).write_text(txt, encoding="utf-8")
        if cap_json:
            capped = {}
            for ref, per_source in chapter_data.items():
                capped[ref] = {}
                for slug, text in per_source.items():
                    lang = (C.source_by_slug(slug) or {}).get("lang")
                    cap = cap_json if lang == "en" else max(600, cap_json // 3)
                    capped[ref][slug] = text[:cap]
            chapter_data = capped
        (out_dir / ("%s.json" % C.pad3(chapter))).write_text(
            json.dumps(chapter_data, ensure_ascii=False), encoding="utf-8")
        for chapter_verse, per_source in chapter_data.items():
            data["%d:%s" % (chapter, chapter_verse)] = per_source
        if not quiet:
            missing = [s["slug"] for s in catalog
                       if not any(per.get(s["slug"]) for per in chapter_data.values())]
            print("  chapter %d: %d verses digested from %d works%s"
                  % (chapter, len(chapter_data), len(catalog),
                     (" \u2014 no text at all: " + ", ".join(missing)) if missing else ""))

    lines = []
    lines.append("=" * 78)
    lines.append("RUN %d MAP \u2014 %d verses, all %d works, opened once" % (index, len(verses), len(catalog)))
    lines.append("=" * 78)
    lines.append("")
    lines.append("Read a slice at a time:  python3 scripts/tafsir/run.py --slice 2:1 2:5")
    lines.append("One verse, full text:    python3 scripts/tafsir/run.py --slice 2:5 2:5 --cap-ar 4000")
    lines.append("The verse to quote is the CANONICAL TRANSLATION; the works below say what may be learned.")
    lines.append("")
    for chapter, verse in verses:
        ref = "%d:%d" % (chapter, verse)
        lines.append("-" * 78)
        lines.append("VERSE %s \u2014 FLOOR %d WORDS \u2014 CANONICAL TRANSLATION" % (ref, floor_of(chapter, verse)))
        lines.append(C.ayah_en(chapter, verse))
        lines.append("-" * 78)
        for source in catalog:
            text = data.get(ref, {}).get(source["slug"])
            if not text:
                continue
            cap = cap_ar if source["lang"] == "ar" else cap_en
            body = text if len(text) <= cap else text[:cap].rstrip() + "\n[...truncated]"
            lines.append("")
            lines.append("### %s [%s]" % (source["slug"], source["lang"]))
            lines.append(body)
        lines.append("")
    map_path = RUNS_DIR / ("run-%03d.txt" % index)
    map_path.write_text("\n".join(lines), encoding="utf-8")
    manifest = save_manifest(verses, index)
    manifest["map"] = str(map_path.relative_to(C.REPO))
    manifest["caps"] = {"en": cap_en, "ar": cap_ar}
    (RUNS_DIR / ("run-%03d.json" % index)).write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest, data


def chapter_data(chapter: int):
    path = C.TMP_DIR / "sources" / ("%s.json" % C.pad3(chapter))
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def slice_map(verses, index, start, end, cap_en, cap_ar) -> int:
    """Print the map for the verses between two refs (inclusive)."""
    wanted = [(c, v) for c, v in verses
              if global_index(c, v) >= global_index(start[0], start[1])
              and global_index(c, v) <= global_index(end[0], end[1])]
    if not wanted:
        raise SystemExit("no verse of run %d lies between %d:%d and %d:%d"
                         % (index, start[0], start[1], end[0], end[1]))
    catalog = C.source_catalog()
    for chapter, verse in wanted:
        data = chapter_data(chapter)
        if data is None:
            raise SystemExit("no map for chapter %d \u2014 run: python3 scripts/tafsir/run.py --build"
                             % chapter)
        per_source = data.get(str(verse)) or {}
        print("-" * 78)
        print("VERSE %d:%d \u2014 FLOOR %d WORDS \u2014 CANONICAL TRANSLATION"
              % (chapter, verse, floor_of(chapter, verse)))
        print(C.ayah_en(chapter, verse))
        print("-" * 78)
        for source in catalog:
            text = per_source.get(source["slug"])
            if not text:
                continue
            cap = cap_ar if source["lang"] == "ar" else cap_en
            body = text if len(text) <= cap else text[:cap].rstrip() + "\n[...truncated]"
            print("")
            print("### %s [%s]" % (source["slug"], source["lang"]))
            print(body)
        print("")
    return 0


# ------------------------------------------------------------------- status

def run_findings(verses, no_grounding=False):
    """Findings for the run's verses, keyed by ref, plus chapter-level ones."""
    opts = argparse.Namespace(no_grounding=no_grounding, strict=False)
    per_verse, chapter_level = {}, []
    for chapter in sorted({c for c, _ in verses}):
        if not C.output_path(chapter).exists():
            continue
        wanted = {v for c, v in verses if c == chapter}
        findings = A.audit_chapter(chapter, opts)
        for f in findings:
            ref = (f.ref or "")
            if ":" in ref and ref.split(":")[0].isdigit():
                verse = int(ref.split(":")[-1])
                if verse in wanted:
                    per_verse.setdefault(ref, []).append(f)
            else:
                chapter_level.append(f)
    return per_verse, chapter_level


def show_status(verses, index, no_grounding=False) -> int:
    if not verses:
        print("corpus complete \u2014 nothing left to run")
        return 0
    doc = {}
    rows = []
    for chapter, verse in verses:
        if chapter not in doc and C.output_path(chapter).exists():
            doc[chapter] = C.load_chapter_doc(chapter)
        section = doc[chapter].section_map().get(verse) if chapter in doc else None
        if section is None or "TODO" in section.body():
            rows.append((chapter, verse, None))
            continue
        body = section.body()
        stats = A.phrase_stats(chapter, section)
        phrases = C.split_phrases(C.ayah_en(chapter, verse)) or [C.ayah_en(chapter, verse)]
        rows.append((chapter, verse, {
            "words": len(C.words(body)),
            "floor": floor_of(chapter, verse),
            "coverage": stats["coverage"],
            "quoted": len(phrases) - stats["missing"],
            "phrases": len(phrases),
            "evidence_missing": stats["evidence_missing"],
            "analogy": bool(A.ANALOGY.search(body)),
        }))
    per_verse, chapter_level = run_findings(verses, no_grounding)
    done = [r for r in rows if r[2]]
    print("run %d \u2014 %d/%d verses written" % (index, len(done), len(verses)))
    print("")
    print("%-8s %6s %6s %9s %8s %5s %8s %6s %6s"
          % ("verse", "words", "floor", "coverage", "phrases", "evid", "analogy", "FAIL", "WARN"))
    for chapter, verse, row in rows:
        ref = "%d:%d" % (chapter, verse)
        if not row:
            print("%-8s %6s %6s %9s %8s %5s %8s %6s %6s" % (ref, "-", floor_of(chapter, verse),
                                                            "-", "-", "-", "-", "-", "-"))
            continue
        findings = per_verse.get(ref, [])
        fails = sum(1 for f in findings if f.level == A.FAIL)
        warns = sum(1 for f in findings if f.level == A.WARN)
        print("%-8s %6d %6d %8.0f%% %8s %5s %8s %6d %6d"
              % (ref, row["words"], row["floor"], row["coverage"] * 100,
                 "%d/%d" % (row["quoted"], row["phrases"]),
                 "0" if not row["evidence_missing"] else str(row["evidence_missing"]),
                 "yes" if row["analogy"] else "NO", fails, warns))
    written_refs = {"%d:%d" % (c, v) for c, v, row in rows if row}
    fails = sum(1 for ref in written_refs for f in per_verse.get(ref, []) if f.level == A.FAIL)
    warns = sum(1 for ref in written_refs for f in per_verse.get(ref, []) if f.level == A.WARN)
    chapter_fails = [f for f in chapter_level if f.level == A.FAIL]
    print("")
    print("run %d: %d written, %d pending | %d FAIL, %d WARN on written verses"
          % (index, len(done), len(verses) - len(done), fails, warns))
    if chapter_fails and done:
        print("chapter-level findings (judged when the chapter is complete): %s"
              % ", ".join(sorted({f.code for f in chapter_fails})))
    for chapter, verse, row in rows:
        if not row:
            print("next verse to write: %d:%d" % (chapter, verse))
            break
    print("gate a written stretch with: python3 scripts/tafsir/batch.py <chapter> --from A --to B")
    return 1 if (fails or len(done) < len(verses)) else 0


def check_run(verses, index, no_grounding=False) -> int:
    """Exit 0 only when every verse of the run is written and clean."""
    if not verses:
        print("run %d: nothing to write \u2014 corpus complete" % index)
        return 0
    pending = []
    for chapter, verse in verses:
        if not C.output_path(chapter).exists():
            pending.append("%d:%d" % (chapter, verse))
            continue
        section = C.load_chapter_doc(chapter).section_map().get(verse)
        if section is None or "TODO" in section.body():
            pending.append("%d:%d" % (chapter, verse))
    per_verse, chapter_level = run_findings(verses, no_grounding)
    pending_set = set(pending)
    fails = {ref: [f for f in per_verse[ref] if f.level == A.FAIL] for ref in per_verse}
    failing = sorted(ref for ref, fs in fails.items()
                     if fs and ref not in pending_set)   # a scaffold verse is pending, not failing
    print("run %d \u2014 %d verses" % (index, len(verses)))
    print("  written:   %d/%d" % (len(verses) - len(pending), len(verses)))
    print("  failing:   %d verse(s)%s" % (len(failing), (": " + ", ".join(failing[:8])) if failing else ""))
    if pending:
        print("  pending:   %s" % ", ".join(pending[:8]))
    complete_chapters = all(
        len([v for c, v in verses if c == chapter]) == C.verse_count(chapter)
        for chapter in {c for c, _ in verses})
    if complete_chapters:
        for f in chapter_level:
            print("  %-4s %-18s %s" % (f.level, f.code, f.message[:90]))
    if pending or failing:
        print("RUN INCOMPLETE \u2014 the run is finished before the writer pauses: write the rest, "
              "fix the failures, then re-run --check")
        return 1
    if complete_chapters and any(f.level == A.FAIL for f in chapter_level):
        print("RUN INCOMPLETE \u2014 the chapter gate still fails on the finished chapter")
        return 1
    print("RUN COMPLETE \u2014 all %d verses written and clean; wait for the author's next start"
          % len(verses))
    return 0


# ------------------------------------------------------------------- commands

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--target", type=int, default=RUN_VERSE_TARGET,
                    help="verses in the run (default %d)" % RUN_VERSE_TARGET)
    ap.add_argument("--start", metavar="REF",
                    help="where the run starts, as the author named it: a chapter (\"2\", meaning "
                         "that chapter's first unwritten verse) or a chapter:verse (\"2:1\")")
    ap.add_argument("--plan", action="store_true", help="print the next run and exit")
    ap.add_argument("--build", action="store_true", help="map the run from all eleven works")
    ap.add_argument("--slice", nargs=2, metavar=("FROM", "TO"),
                    help="print the map between two refs, e.g. --slice 2:1 2:5")
    ap.add_argument("--status", action="store_true", help="words, floors and gate state of the run")
    ap.add_argument("--check", action="store_true", help="exit 0 only when the run is finished")
    ap.add_argument("--scaffold", action="store_true", help="write the chapter files the run needs")
    ap.add_argument("--cap-en", type=int, default=2400, help="characters per English work per verse")
    ap.add_argument("--cap-ar", type=int, default=700, help="characters per Arabic work per verse")
    ap.add_argument("--cap-json", type=int, default=1600,
                    help="characters per work in the per-chapter digest the grounding check reads "
                         "(0 = uncapped)")
    ap.add_argument("--no-grounding", action="store_true")
    args = ap.parse_args(argv)

    verses, index = plan(args.target, args.start)

    if args.plan or (not (args.build or args.slice or args.status or args.check or args.scaffold)):
        show_plan(verses, index, args.target, args.start)
        if verses:
            save_manifest(verses, index)
            print("  run %d pinned: tmp/runs/run-%03d.json \u2014 the same fifty are finished before "
                  "the writer pauses" % (index, index))
            print("  verify it: python3 scripts/tafsir/run.py --check \u2014 RUN COMPLETE only when "
                  "all %d are written and clean: a call is not finished at %d/50"
                  % (len(verses), max(0, len(verses) - 1)))
        return 0

    if args.scaffold:
        for chapter in sorted({c for c, _ in verses}):
            path = C.output_path(chapter)
            if path.exists():
                print("kept %s" % path.relative_to(C.REPO))
            else:
                path.write_text(S.scaffold_text(chapter), encoding="utf-8")
                print("wrote %s \u2014 %d verses to fill" % (path.relative_to(C.REPO), C.verse_count(chapter)))
        return 0

    if args.build:
        print("run %d \u2014 mapping %d verses from the eleven works"
              % (index, len(verses)))
        manifest, _ = build_map(verses, index, args.cap_en, args.cap_ar, args.cap_json)
        print("  map: %s" % manifest["map"])
        for chapter in manifest["chapters"]:
            if not C.output_path(chapter).exists():
                C.output_path(chapter).write_text(S.scaffold_text(chapter), encoding="utf-8")
                print("  scaffolded tafsir/%s.md \u2014 %d verses to fill"
                      % (C.pad3(chapter), C.verse_count(chapter)))
        print("  read it in slices: python3 scripts/tafsir/run.py --slice %s:%d %s:%d"
              % (verses[0][0], verses[0][1], verses[min(4, len(verses) - 1)][0],
                 verses[min(4, len(verses) - 1)][1]))
        print("  cross-references: python3 scripts/tafsir/reference.py C:V")
        return 0

    if args.slice:
        def parse(ref):
            try:
                c, v = ref.split(":")
                return int(c), int(v)
            except Exception:
                raise SystemExit("give refs as C:V, e.g. 2:255")
        return slice_map(verses, index, parse(args.slice[0]), parse(args.slice[1]),
                         args.cap_en, args.cap_ar)

    if args.status:
        return show_status(verses, index, args.no_grounding)

    if args.check:
        return check_run(verses, index, args.no_grounding)

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
