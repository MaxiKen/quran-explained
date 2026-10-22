#!/usr/bin/env python3
"""Source-first review view: print the full English commentary before phrase drafts.

    python3 tools/pairs/review.py SURAH VERSE

Read and digest the complete SOURCE section before reading the DRAFT section.
This display supports the required human workflow; it cannot prove that the
reader has read or understood the source.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    surah, ayah = int(sys.argv[1]), str(int(sys.argv[2]))
    pad = "%03d" % surah
    with open(os.path.join(ROOT, "data", "tafsir_%s.json" % pad), encoding="utf-8") as f:
        tafsir = json.load(f)
    verse_map = tafsir.get("verses", {}).get(ayah)
    if not isinstance(verse_map, dict):
        print("No English commentary mapping for %d:%s" % (surah, ayah), file=sys.stderr)
        return 1
    source_id = tafsir.get("primary", "tabari")
    index = verse_map.get(source_id)
    if index is None:
        print("No primary English commentary for %d:%s" % (surah, ayah), file=sys.stderr)
        return 1
    blocks = tafsir.get("sets", {}).get(source_id, {}).get("blocks", [])
    if not isinstance(index, int) or index < 0 or index >= len(blocks):
        print("Invalid commentary block mapping for %d:%s" % (surah, ayah), file=sys.stderr)
        return 1

    chapter_path = os.path.join(ROOT, "data", "chapter_%s.js" % pad)
    import re
    text = open(chapter_path, encoding="utf-8").read()
    match = re.match(r"^\s*var\s+chapterData_\d+\s*=\s*(\[.*\])\s*;\s*$", text, re.S)
    if not match:
        print("Could not read chapter translation", file=sys.stderr)
        return 1
    chapter = json.loads(match.group(1))
    translation = next((v.get("ayah_en", "") for theme in chapter for v in theme.get("verses", [])
                        if str(v.get("ayah_no_surah")) == ayah), "")
    print("=== %d:%s TRANSLATION ===\n%s" % (surah, ayah, translation))
    print("\n=== COMPLETE ENGLISH COMMENTARY (read this whole section first) ===\n%s" % blocks[index])

    authored_path = os.path.join(HERE, "authored", "%s.json" % pad)
    if os.path.exists(authored_path):
        with open(authored_path, encoding="utf-8") as f:
            authored = json.load(f)
        entry = authored.get("verses", {}).get(ayah)
        if entry:
            print("\n=== EXISTING DRAFT (read only after the source above) ===")
            for i, phrase in enumerate(entry.get("phrases", []), 1):
                print("%d. %s\n   %s" % (i, phrase.get("translation", ""), phrase.get("explanation", "")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
