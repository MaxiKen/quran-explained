"""Check the imported Tafsir al-Tabari files.

Every surah file must carry one passage for each of its verses, the passages
must be plain text (no markup, no site furniture), and the length of each
passage must be plausible. Each verse must also carry the Arabic original
that sits below the English in the reader. Run it after an import, before the
data is used.

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
    "Show original Arabic",
]

TAG_RE = re.compile(r"<[a-zA-Z/][^>]*>")
ESCAPE_RE = re.compile(r"\\([\[\]\*_`])")
ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")


def check_file(path, surah, count):
    problems = []
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if payload.get("surah") != surah:
        problems.append("surah field is %r, expected %d" % (payload.get("surah"), surah))
    if payload.get("lang") != "en":
        problems.append("lang is %r, expected 'en'" % payload.get("lang"))
    if payload.get("primary") != "tabari":
        problems.append("primary is %r, expected 'tabari'" % payload.get("primary"))

    sources = payload.get("sources", [])
    if [s.get("id") for s in sources] != ["tabari"]:
        problems.append("sources are %r, expected only 'tabari'" % [s.get("id") for s in sources])

    sets = payload.get("sets", {})
    for name in ("tabari", "tabariAr"):
        if name not in sets:
            problems.append("no %r set" % name)
    if "tabari" not in sets:
        return problems
    block_set = sets["tabari"]
    blocks = block_set.get("blocks", [])
    ranges = block_set.get("ranges", [])
    if len(blocks) != len(ranges):
        problems.append("%d blocks but %d ranges" % (len(blocks), len(ranges)))

    arabic_blocks = []
    if "tabariAr" in sets:
        arabic_blocks = sets["tabariAr"].get("blocks", [])
        if len(arabic_blocks) != len(blocks):
            problems.append(
                "%d Arabic blocks but %d English blocks" % (len(arabic_blocks), len(blocks))
            )

    verses = payload.get("verses", {})
    missing = [a for a in range(1, count + 1) if str(a) not in verses]
    if missing:
        problems.append("%d verse(s) missing: %s" % (len(missing), missing[:10]))

    total_words = 0
    arabic_verses = 0
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

        # the Arabic original below the English
        arabic_index = entry.get("tabariAr") if isinstance(entry, dict) else None
        if not isinstance(arabic_index, int) or not (0 <= arabic_index < len(arabic_blocks)):
            problems.append("verse %d points at Arabic block %r" % (ayah, arabic_index))
            continue
        arabic = arabic_blocks[arabic_index]
        if not arabic.strip():
            problems.append("verse %d has no Arabic original" % ayah)
            continue
        if not ARABIC_RE.search(arabic):
            problems.append("verse %d has an Arabic block without Arabic script" % ayah)
        if TAG_RE.search(arabic):
            problems.append("verse %d has HTML markup in the Arabic" % ayah)
        for needle in FURNITURE:
            if needle in arabic:
                problems.append("verse %d has site furniture in the Arabic: %r" % (ayah, needle))
        arabic_verses += 1

    if not problems:
        print(
            "  %s ok: %d verses, %d words, %d with the Arabic original"
            % (os.path.basename(path), count, total_words, arabic_verses)
        )
    return problems


def corpus_summary(data_dir, surahs):
    """Report the figures the publisher publishes for the whole corpus.

    tafseerquran.com states that the canonical layer holds 6,226 passages
    for the 6,236 verses of the Qur'an, with a few short surahs whose slice
    runs into the neighbouring section. An import that lands on the same
    numbers has taken every verse, not a selection.
    """
    verses = 0
    seen = {}
    shared = 0
    words = 0
    arabic_verses = 0
    arabic_chars = 0
    for surah in surahs:
        path = os.path.join(data_dir, "tafsir_%03d.json" % surah)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        sets = payload.get("sets", {})
        blocks = sets.get("tabari", {}).get("blocks", [])
        arabic_blocks = sets.get("tabariAr", {}).get("blocks", [])
        for ayah, entry in payload.get("verses", {}).items():
            verses += 1
            index = entry["tabari"] if isinstance(entry, dict) else entry
            text = blocks[index]
            words += len(text.split())
            digest = hash(text)
            if digest in seen:
                shared += 1
            else:
                seen[digest] = (surah, int(ayah))
            if isinstance(entry, dict) and isinstance(entry.get("tabariAr"), int):
                arabic = arabic_blocks[entry["tabariAr"]]
                if arabic.strip():
                    arabic_verses += 1
                    arabic_chars += len(arabic)
    return verses, len(seen), shared, words, arabic_verses, arabic_chars


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
            if name.startswith("tafsir_") and name.endswith(".json")
        )

    failures = 0
    for surah in surahs:
        path = os.path.join(args.data, "tafsir_%03d.json" % surah)
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

    if len(surahs) == 114:
        verses, distinct, shared, words, arabic_verses, arabic_chars = corpus_summary(
            args.data, surahs
        )
        print(
            "corpus: %d verses, %d distinct passages, %d verses sharing a passage, %d words"
            % (verses, distinct, shared, words)
        )
        print(
            "arabic: %d verse(s) with the Arabic original, %d characters"
            % (arabic_verses, arabic_chars)
        )
        if verses != 6236:
            print("  expected 6,236 verses")
            failures += 1
        if distinct != 6226:
            print("  expected 6,226 distinct passages, as the publisher states")
            failures += 1
        if arabic_verses != verses:
            print("  expected the Arabic original on all %d verses" % verses)
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
