#!/usr/bin/env python3
"""Build the app payload ``data/tafsir_NNN.json`` from ``tafsir/NNN.md``.

    python3 scripts/tafsir/build_data.py 1        # one chapter
    python3 scripts/tafsir/build_data.py --all    # every chapter file that exists

Output shape (what the app reads):

    {"surah": 1, "intro": "<markdown>", "verses": {"1": "<markdown>", ...}}

``intro`` is the introduction prose, ``verses[M]`` is everything under
``## Verse N:M`` starting with the canonical ``> ...`` quote line — the app
strips that leading quote at render time, exactly as it did before.

The file is written with ``indent=2`` and no trailing newline, matching the
payload the app has always served. A build is a pure function of the markdown:
running it twice changes nothing, and ``--check`` fails if the committed JSON
no longer matches the markdown.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402


def unfinished(n: int):
    """How many of the chapter's verses are still scaffolds, and the first one. (0, None) if none."""
    doc = C.load_chapter_doc(n)
    if doc is None:
        return None
    pending = [s.verse for s in doc.sections if "TODO" in s.body()]
    return (len(pending), len(doc.sections), pending[0]) if pending else (0, len(doc.sections), None)


def build(n: int):
    doc = C.load_chapter_doc(n)
    if doc is None:
        return None
    # a chapter still written in batches must never reach the app: refuse to publish a scaffold
    pending, total, first = unfinished(n)
    if pending:
        raise SystemExit(
            "tafsir/%s.md is still being written: %d of %d verses are TODO scaffolds "
            "(first: %d:%d). Finish the chapter, then build the payload."
            % (C.pad3(n), pending, total, n, first))
    verses = {}
    for section in doc.sections:
        body = section.body()
        text = "> %s" % C.ayah_en(n, section.verse)
        if body.strip():
            text += "\n\n" + body.strip()
        verses[str(section.verse)] = text
    return {"surah": int(n), "intro": doc.intro.strip(), "verses": verses}


def payload(n: int) -> str:
    data = build(n)
    if data is None:
        raise SystemExit("tafsir/%s.md does not exist" % C.pad3(n))
    return json.dumps(data, ensure_ascii=False, indent=2)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", nargs="?", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="verify the committed JSON matches the markdown; write nothing")
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)

    chapters = [args.chapter] if args.chapter else list(C.chapter_numbers())
    if not args.all and not args.chapter:
        ap.error("give a chapter number or --all")

    written = unchanged = skipped = stale = progress = 0
    for n in chapters:
        if not C.output_path(n).exists():
            skipped += 1
            continue
        pending, total, first = unfinished(n)
        if pending:
            progress += 1
            if not args.all:
                print("tafsir/%s.md is still being written: %d of %d verses are TODO scaffolds "
                      "(first: %d:%d). Finish the chapter, then build the payload."
                      % (C.pad3(n), pending, total, n, first), file=sys.stderr)
                return 1
            continue
        text = payload(n)
        target = C.DATA_DIR / ("tafsir_%s.json" % C.pad3(n))
        if args.stdout:
            print(text)
            continue
        if args.check:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            if current == text:
                unchanged += 1
            else:
                stale += 1
                print("stale: data/tafsir_%s.json does not match tafsir/%s.md"
                      % (C.pad3(n), C.pad3(n)))
            continue
        if target.exists() and target.read_text(encoding="utf-8") == text:
            unchanged += 1
            continue
        target.write_text(text, encoding="utf-8")
        written += 1
        print("wrote data/tafsir_%s.json (%d verses, %d bytes)"
              % (C.pad3(n), len(build(n)["verses"]), len(text)))

    if args.check:
        print("check: %d up to date, %d stale, %d chapters not written yet, %d still being written"
              % (unchanged, stale, skipped, progress))
        return 1 if stale else 0
    if not args.stdout:
        print("build: %d written, %d already current, %d chapters not written yet, %d still being written"
              % (written, unchanged, skipped, progress))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
