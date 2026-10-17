"""Check the imported Tafsir al-Tabari files.

Every surah file must carry one passage for each of its verses, the passages
must be plain text (no markup, no site furniture), and the length of each
passage must be plausible. Run it after an import, before the data is used.

    python3 tools/tabari/verify.py --data data
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import repo_root, surah_verse_counts  # noqa: E402

# Words that must never reach the reader: they belong to the site's chrome,
# not to the commentary.
FURNITURE = [
    "Full English translation of Tabari",
    "Read Tabari's full text",
    "Go to ayah",
    "The Arabic source text is always authoritative",
    "This translation is a study aid",
    "Tabari (1 passage)",
    "Show more",
    "Mushaf",
    "Tajweed",
]

TAG_RE = re.compile(r"<[a-zA-Z/][^>]*>")
ESCAPE_RE = re.compile(r"\\([\[\]\*_`])")


def check_file(path, surah, count):
    problems = []
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if payload.get("surah") != surah:
        problems.append("surah field is %r, expected %d" % (payload.get("surah"), surah))
    if payload.get("lang") != "en":
        problems.append("lang is %r, expected 'en'" % payload.get("lang"))

    sets = payload.get("sets", {})
    if "tabari" not in sets:
        problems.append("no 'tabari' set")
        return problems
    block_set = sets["tabari"]
    blocks = block_set.get("blocks", [])
    ranges = block_set.get("ranges", [])
    if len(blocks) != len(ranges):
        problems.append("%d blocks but %d ranges" % (len(blocks), len(ranges)))

    verses = payload.get("verses", {})
    missing = [a for a in range(1, count + 1) if str(a) not in verses]
    if missing:
        problems.append("%d verse(s) missing: %s" % (len(missing), missing[:10]))

    total_words = 0
    for ayah in range(1, count + 1):
        entry = verses.get(str(ayah))
        if entry is None:
            continue
        # the verse map names the source the block belongs to; a plain
        # number is accepted too, for a file written before the map was nested
        index = entry.get("tabari") if isinstance(entry, dict) else entry
        if not isinstance(index, int) or index < 0 or index >= len(blocks):
            problems.append("verse %d points at block %r" % (ayah, index))
            continue
        text = blocks[index]
        if not text.strip():
            problems.append("verse %d has empty text" % ayah)
            continue
        if TAG_RE.search(text):
            problems.append("verse %d contains HTML markup" % ayah)
        if ESCAPE_RE.search(text):
            problems.append("verse %d contains escaped markdown punctuation" % ayah)
        for needle in FURNITURE:
            if needle in text:
                problems.append("verse %d contains site furniture: %r" % (ayah, needle))
        words = len(text.split())
        total_words += words
        if words < 3:
            problems.append("verse %d is suspiciously short (%d words)" % (ayah, words))

    if not problems:
        print("  %s ok: %d verses, %d words" % (os.path.basename(path), count, total_words))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data")
    parser.add_argument("--surahs", default="")
    args = parser.parse_args()

    root = repo_root()
    os.chdir(root)
    counts = surah_verse_counts(root)

    if args.surahs.strip():
        from common import parse_surah_spec

        surahs = parse_surah_spec(args.surahs)
    else:
        surahs = sorted(
            int(name[7:10])
            for name in os.listdir(args.data)
            if name.startswith("tabari_") and name.endswith(".json")
        )

    failures = 0
    for surah in surahs:
        path = os.path.join(args.data, "tabari_%03d.json" % surah)
        if not os.path.exists(path):
            print("  %s MISSING" % os.path.basename(path))
            failures += 1
            continue
        problems = check_file(path, surah, counts[surah])
        for problem in problems:
            print("  %s: %s" % (os.path.basename(path), problem))
        if problems:
            failures += 1
    print("%d/%d surah file(s) passed" % (len(surahs) - failures, len(surahs)))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
