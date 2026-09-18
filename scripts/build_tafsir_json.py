#!/usr/bin/env python3
"""
Extract structured JSON tafsir data from markdown commentry/*.md for all 114 chapters.
Output format for each chapter (data/tafsir_XXX.json):
{
  "surah": 1,
  "intro": "...markdown intro...",
  "verses": {
    "1": "...markdown commentary...",
    "2": "...markdown commentary...",
    ...
  }
}
"""

import os
import re
import json

def extract_chapter(ch_num):
    fpath = f"markdown commentry/{ch_num:03d}.md"
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"File not found: {fpath}")

    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"\n(?=## )", content)
    intro = ""
    verses = {}

    for sec in sections:
        sec = sec.strip()
        if not sec.startswith("## "):
            continue
        first_line = sec.split("\n")[0].strip()
        body = "\n".join(sec.split("\n")[1:]).strip()
        if body.endswith("---"):
            body = body[:-3].strip()

        if "Introduction to the Sūrah" in first_line:
            cleaned_intro = re.sub(r"^\s*\*\*Expanded Commentary\*\*\s*", "", body).strip()
            intro = cleaned_intro
        else:
            m = re.search(r":(\d+)", first_line)
            if m:
                ayah_no = m.group(1)
                # Clean redundant **Expanded Commentary**
                cleaned_body = re.sub(r"\n+\*\*Expanded Commentary\*\*\s*\n+", "\n\n", body)
                cleaned_body = re.sub(r"^\s*\*\*Expanded Commentary\*\*\s*\n*", "", cleaned_body).strip()
                verses[ayah_no] = cleaned_body

    return {
        "surah": ch_num,
        "intro": intro,
        "verses": verses
    }

def main():
    os.makedirs("data", exist_ok=True)
    total_verses = 0
    total_bytes = 0

    for ch in range(1, 115):
        data = extract_chapter(ch)
        out_path = f"data/tafsir_{ch:03d}.json"
        
        # Save compact yet readable JSON
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        file_size = os.path.getsize(out_path)
        total_bytes += file_size
        total_verses += len(data["verses"])

        if ch in [1, 2, 5, 10, 50, 100, 114]:
            print(f"Surah {ch:3d}: {len(data['verses'])} verses, intro: {len(data['intro'])} chars, size: {file_size/1024:.1f} KB")

    print("--------------------------------------------------")
    print(f"Successfully processed all 114 chapters.")
    print(f"Total verses extracted: {total_verses}")
    print(f"Total payload size: {total_bytes / (1024 * 1024):.2f} MB")

if __name__ == "__main__":
    main()
