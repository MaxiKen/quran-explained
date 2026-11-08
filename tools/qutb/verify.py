#!/usr/bin/env python3
"""Verify the reader's Simple payload (data/qutb_NNN.json).

Checks, per surah:
  - the file exists and names the expected source and edition
  - every verse of the surah maps to a block, 1..N, with no gaps
  - blocks and ranges are the same length and ranges are contiguous, in order
  - each block's range names exactly the verses that point at it
  - a block occurs once per surah (the point of the collapse)
  - text is non-empty, Arabic-script (Urdu is written in the Arabic script),
    and keeps the paragraph breaks of the source

Usage:
    python3 tools/qutb/verify.py --data data
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
EDITION = "tafsir-fe-zalul-quran-syed-qatab"
ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def verse_counts(path=None):
    path = path or os.path.join(REPO_ROOT, "js", "chapters-meta.js")
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    counts = {}
    for block in re.split(r"\n\s*\{", src):
        num = re.search(r"number:\s*(\d+)", block)
        vers = re.search(r"\bverses:\s*(\d+)", block)
        if num and vers:
            counts[int(num.group(1))] = int(vers.group(1))
    return counts


def parse_range(surah, spec):
    m = re.fullmatch(r"(\d+):(\d+)(?:-(\d+))?", spec or "")
    if not m or int(m.group(1)) != surah:
        return None
    start = int(m.group(2))
    end = int(m.group(3) or m.group(2))
    if end < start:
        return None
    return list(range(start, end + 1))


def check_surah(path, surah, expected_verses):
    errors = []
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("surah") != surah:
        errors.append(f"surah field is {data.get('surah')!r}, expected {surah}")
    if data.get("edition") != EDITION:
        errors.append(f"edition is {data.get('edition')!r}")
    if data.get("lang") != "ur" or data.get("dir") != "rtl":
        errors.append("lang/dir must be 'ur'/'rtl'")

    blocks, ranges, verses = data.get("blocks"), data.get("ranges"), data.get("verses")
    if not isinstance(blocks, list) or not isinstance(ranges, list):
        return ["blocks/ranges missing"]
    if len(blocks) != len(ranges):
        errors.append(f"{len(blocks)} blocks vs {len(ranges)} ranges")

    # verse map: integers 1..N, all present
    mapped = {}
    for key, idx in (verses or {}).items():
        if not re.fullmatch(r"\d+", str(key)):
            errors.append(f"non-numeric verse key {key!r}")
            continue
        mapped[int(key)] = idx
    missing = [v for v in range(1, expected_verses + 1) if v not in mapped]
    if missing:
        errors.append(f"{len(missing)} verses unmapped, first {missing[:5]}")
    extra = [v for v in mapped if v < 1 or v > expected_verses]
    if extra:
        errors.append(f"verses outside the surah: {extra[:5]}")

    # ranges: contiguous, in order, matching the verse map
    expected_start = 1
    for i, spec in enumerate(ranges):
        covered = parse_range(surah, spec)
        if covered is None:
            errors.append(f"range {i} malformed: {spec!r}")
            continue
        if covered[0] != expected_start:
            errors.append(f"range {i} starts at {covered[0]}, expected {expected_start}")
        expected_start = covered[-1] + 1
        for v in covered:
            if mapped.get(v) != i:
                errors.append(f"verse {v} maps to {mapped.get(v)}, range {i} claims it")
    if expected_start != expected_verses + 1:
        errors.append(f"ranges cover to {expected_start - 1}, surah has {expected_verses}")

    # blocks: non-empty, Arabic script, unique within the surah, numbered in range
    seen = {}
    for i, text in enumerate(blocks):
        if not isinstance(text, str) or not text.strip():
            errors.append(f"block {i} is empty")
            continue
        if not ARABIC.search(text):
            errors.append(f"block {i} has no Arabic-script text")
        if text != text.strip():
            errors.append(f"block {i} has untrimmed edges")
        if "\r" in text:
            errors.append(f"block {i} carries CR line endings")
        key = text
        if key in seen:
            errors.append(f"block {i} repeats block {seen[key]}")
        seen[key] = i
        if not any(v == i for v in mapped.values()):
            errors.append(f"block {i} is unreferenced")
    for v, idx in mapped.items():
        if not isinstance(idx, int) or not 0 <= idx < len(blocks):
            errors.append(f"verse {v} points outside blocks ({idx!r})")
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=os.path.join(REPO_ROOT, "data"))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    counts = verse_counts()
    failures = 0
    total_blocks = total_verses = 0
    for surah in sorted(counts):
        path = os.path.join(args.data, f"qutb_{surah:03d}.json")
        if not os.path.exists(path):
            print(f"surah {surah}: missing {path}", file=sys.stderr)
            failures += 1
            continue
        errors = check_surah(path, surah, counts[surah])
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        total_blocks += len(data.get("blocks") or [])
        total_verses += len(data.get("verses") or {})
        if errors:
            failures += 1
            print(f"surah {surah}: {len(errors)} problem(s)", file=sys.stderr)
            for err in errors[:8]:
                print(f"   {err}", file=sys.stderr)
    if failures:
        print(f"FAILED — {failures} surah(s) with problems", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"OK — 114 surahs, {total_verses} verses, {total_blocks} blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
