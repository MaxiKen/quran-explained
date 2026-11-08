#!/usr/bin/env python3
"""Import Fī Ẓilāl al-Qurʾān (Urdu) into the reader's Simple payload.

Source: spa5k/tafsir_api, edition `tafsir-fe-zalul-quran-syed-qatab`, which
publishes one JSON per verse (`<surah>/<ayah>.json`) plus a per-surah array
(`<surah>.json`). The same passage is repeated for every verse it discusses, so
this importer collapses each run into a single block and records which verses
that block covers.

Output, one file per surah:

    data/qutb_NNN.json
    { "surah", "lang", "dir", "source", "edition", "sourceUrl", "notice",
      "blocks": [text, ...], "ranges": ["1:2-7", ...],
      "verses": { "1": 0, "2": 1, ... } }

Usage:

    python3 tools/qutb/importer.py --src <clone>/tafsir/tafsir-fe-zalul-quran-syed-qatab
    python3 tools/qutb/importer.py --src <dir> --out data --only 1,112-114
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))

EDITION = "tafsir-fe-zalul-quran-syed-qatab"
SOURCE = "Fī Ẓilāl al-Qurʾān — Sayyid Quṭb"
SOURCE_URL = "https://github.com/spa5k/tafsir_api"
LANG = "ur"
DIR = "rtl"

NOTICE = (
    "Fī Ẓilāl al-Qurʾān is Sayyid Quṭb's work (first published 1952–1966) in an "
    "Urdu rendering taken from the tafsir_api project. It is presented as the "
    "author wrote it, as study material: it is not a translation of the Qurʾān "
    "and not a substitute for a qualified teacher. Quṭb's positions are his own "
    "and have been criticised by scholars; the reader carries the text as a "
    "historical tafsīr, not as a statement of this project's creed."
)


def verse_counts(path=None):
    """The verse count per surah, read from the reader's own metadata."""
    path = path or os.path.join(REPO_ROOT, "js", "chapters-meta.js")
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    counts = {}
    for block in re.split(r"\n\s*\{", src):
        num = re.search(r"number:\s*(\d+)", block)
        vers = re.search(r"\bverses:\s*(\d+)", block)
        if num and vers:
            counts[int(num.group(1))] = int(vers.group(1))
    if len(counts) != 114:
        raise SystemExit(f"expected 114 surahs in {path}, found {len(counts)}")
    return counts


def read_source(src_root, surah):
    """Return [(ayah, text)] for one surah, in verse order.

    The per-verse files are the source of truth; the surah array is used only
    to confirm they agree.
    """
    folder = os.path.join(src_root, str(surah))
    if not os.path.isdir(folder):
        raise SystemExit(f"missing source folder: {folder}")
    rows = []
    for name in os.listdir(folder):
        m = re.fullmatch(r"(\d+)\.json", name)
        if not m:
            continue
        with open(os.path.join(folder, name), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        rows.append((int(m.group(1)), data.get("text") or ""))
    rows.sort()

    combined = os.path.join(src_root, f"{surah}.json")
    if os.path.exists(combined):
        with open(combined, "r", encoding="utf-8") as fh:
            listed = json.load(fh)
        if len(listed) != len(rows):
            raise SystemExit(
                f"surah {surah}: {len(rows)} verse files but {len(listed)} "
                f"entries in {surah}.json"
            )
        for (ayah, text), item in zip(rows, listed):
            if (item.get("text") or "") != text:
                raise SystemExit(
                    f"surah {surah} verse {ayah}: {surah}.json disagrees with "
                    f"{surah}/{ayah}.json"
                )
    return rows


def collapse(rows, surah):
    """Collapse consecutive verses that share a passage into blocks."""
    blocks, ranges, verses = [], [], {}
    current_text, start, last = None, None, None

    def flush():
        if current_text is None:
            return
        idx = len(blocks)
        blocks.append(current_text)
        ranges.append(
            f"{surah}:{start}" if start == last else f"{surah}:{start}-{last}"
        )
        for ayah in range(start, last + 1):
            verses[ayah] = idx

    for ayah, raw in rows:
        text = raw.strip()
        if not text:
            raise SystemExit(f"surah {surah} verse {ayah}: empty passage")
        if current_text is not None and text == current_text:
            last = ayah
            continue
        flush()
        current_text, start, last = text, ayah, ayah
    flush()
    return blocks, ranges, verses


def build_surah(src_root, surah, expected_verses):
    rows = read_source(src_root, surah)
    if [a for a, _ in rows] != list(range(1, expected_verses + 1)):
        got = [a for a, _ in rows]
        raise SystemExit(
            f"surah {surah}: expected verses 1..{expected_verses}, got "
            f"{got[:5]}…{got[-3:]} ({len(got)} files)"
        )
    blocks, ranges, verses = collapse(rows, surah)
    if len(verses) != expected_verses:
        raise SystemExit(
            f"surah {surah}: {len(verses)} verses mapped, expected {expected_verses}"
        )
    return {
        "surah": surah,
        "lang": LANG,
        "dir": DIR,
        "source": SOURCE,
        "edition": EDITION,
        "sourceUrl": SOURCE_URL,
        "notice": NOTICE,
        "blocks": blocks,
        "ranges": ranges,
        "verses": {str(k): v for k, v in sorted(verses.items())},
    }


def parse_selection(spec, counts):
    if not spec or spec == "all":
        return sorted(counts)
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True,
                    help="path to tafsir/tafsir-fe-zalul-quran-syed-qatab")
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "data"),
                    help="directory for qutb_NNN.json (default: data)")
    ap.add_argument("--only", default="all",
                    help="surah selection, e.g. '1,112-114' (default: all)")
    ap.add_argument("--check", action="store_true",
                    help="compare against the files on disk, write nothing")
    args = ap.parse_args(argv)

    counts = verse_counts()
    surahs = parse_selection(args.only, counts)
    written = unchanged = 0
    for surah in surahs:
        payload = build_surah(args.src, surah, counts[surah])
        text = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"
        target = os.path.join(args.out, f"qutb_{surah:03d}.json")
        if args.check:
            with open(target, "r", encoding="utf-8") as fh:
                if fh.read() != text:
                    print(f"DIFFERS {target}", file=sys.stderr)
                    return 1
            unchanged += 1
            continue
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as fh:
                if fh.read() == text:
                    unchanged += 1
                    continue
        os.makedirs(args.out, exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(text)
        written += 1
    if args.check:
        print(f"checked {len(surahs)} surahs — all current")
    else:
        print(f"wrote {len(surahs)} surahs — {written} changed, {unchanged} already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
