"""Read the reader's English verse translations for phrase authoring."""

from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


CHAPTER_DATA = re.compile(
    r"^\s*var\s+chapterData_\d+\s*=\s*(\[.*\])\s*;\s*$",
    re.S,
)


def read_chapter(surah: int) -> dict[str, dict[str, str]]:
    """Return the English and Arabic text for each verse in a chapter file."""
    path = os.path.join(ROOT, "data", "chapter_%03d.js" % surah)
    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    match = CHAPTER_DATA.match(text)
    if not match:
        raise ValueError("Could not read chapter data from %s" % path)

    themes = json.loads(match.group(1))
    verses = {}
    for theme in themes:
        for verse in theme.get("verses", []):
            number = str(verse["ayah_no_surah"])
            verses[number] = {"en": verse.get("ayah_en", "")}
    return verses
