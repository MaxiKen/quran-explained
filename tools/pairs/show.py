#!/usr/bin/env python3
"""Review the phrase explanations for one surah or verse.

    python3 tools/pairs/show.py 1        # every authored verse in Surah 1
    python3 tools/pairs/show.py 1 7      # only verse 7
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import source  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    surah = int(sys.argv[1])
    authored_path = os.path.join(HERE, "authored", "%03d.json" % surah)
    with open(authored_path, encoding="utf-8") as handle:
        authored = json.load(handle)
    chapter = source.read_chapter(surah)

    selected = {str(int(sys.argv[2]))} if len(sys.argv) > 2 else None
    for ayah in sorted(authored.get("verses", {}), key=int):
        if selected and ayah not in selected:
            continue
        verse = chapter.get(ayah, {})
        print("=== %d:%s ===" % (surah, ayah))
        print("VERSE: %s" % verse.get("en", ""))
        for index, phrase in enumerate(authored["verses"][ayah].get("phrases", []), 1):
            print("  %d. %s" % (index, phrase.get("translation", "")))
            print("     %s" % phrase.get("explanation", ""))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
