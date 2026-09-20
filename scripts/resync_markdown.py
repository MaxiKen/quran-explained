#!/usr/bin/env python3
"""
Re-sync markdown commentry/XXX.md from the edited data/tafsir_XXX.json so the
markdown sources and the JSON the app loads stay consistent and
scripts/build_tafsir_json.py round-trips. The original title line (# ...) of
each markdown file is preserved.
"""

import json
import os
import re
import sys
from multiprocessing import Pool

def resync(ch):
    md_path = f"markdown commentry/{ch:03d}.md"
    with open(f"data/tafsir_{ch:03d}.json", encoding="utf-8") as f:
        data = json.load(f)

    title = f"# Sūrah {ch:03d} — Verse-by-Verse Commentary"
    if os.path.exists(md_path):
        with open(md_path, encoding="utf-8") as f:
            first = f.readline().strip()
        if first.startswith("# "):
            title = first

    out = [title, ""]
    out += ["## Introduction to the Sūrah", "", data["intro"].strip(), "", "---", ""]
    for vn in sorted(data["verses"], key=int):
        body = data["verses"][vn].strip()
        out += [f"## Verse {ch}:{vn}", "", body, "", "---", ""]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")
    return ch, len(data["verses"])

def main():
    surahs = [int(a) for a in sys.argv[1:]] or list(range(1, 115))
    with Pool(10) as p:
        done = p.map(resync, surahs)
    print(f"Resynced {len(done)} markdown files from edited JSON.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
