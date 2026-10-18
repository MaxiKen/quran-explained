#!/usr/bin/env python3
"""Validate and publish the hand-written phrase explanations.

    python3 tools/pairs/assemble.py --check   # validate, write nothing
    python3 tools/pairs/assemble.py           # publish all authored chapters

`tools/pairs/authored/NNN.json` contains exact pieces of the reader's own
English verse translation and one concise paragraph for each piece. This
script verifies that the phrases cover the verse in reading order, then
publishes the data consumed by the app as `data/pairs_NNN.json`.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import source  # noqa: E402

AUTHORED = os.path.join(HERE, "authored")
ARABIC = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
DASH = re.compile("[—–]")
LETTER_OR_NUMBER = re.compile(r"[A-Za-z0-9]")


def check_line(value: object, field: str, where: str, problems: list[str], minimum: int, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        problems.append("%s: empty %s" % (where, field))
        return ""

    text = value.strip()
    if ARABIC.search(text):
        problems.append("%s: %s contains Arabic script" % (where, field))
    if DASH.search(text):
        problems.append("%s: %s contains an em dash or en dash" % (where, field))
    if ";" in text:
        problems.append("%s: %s contains a semicolon" % (where, field))
    letters = [char for char in text if char.isalpha()]
    if not letters or not letters[0].isupper():
        problems.append("%s: %s should start with a capital letter" % (where, field))
    words = text.split()
    if len(words) < minimum:
        problems.append("%s: %s is too short" % (where, field))
    if len(words) > maximum:
        problems.append("%s: %s is too long to keep concise" % (where, field))
    return text


def check_phrase(phrase: object, where: str, problems: list[str]) -> dict[str, str]:
    if not isinstance(phrase, dict):
        problems.append("%s: phrase must be an object" % where)
        return {"translation": "", "explanation": ""}

    allowed = {"translation", "explanation"}
    extra = set(phrase) - allowed
    if extra:
        problems.append("%s: unexpected field(s): %s" % (where, ", ".join(sorted(extra))))

    translation = phrase.get("translation", "")
    if not isinstance(translation, str) or not translation.strip():
        problems.append("%s: empty translation phrase" % where)
        translation = ""
    else:
        translation = translation.strip()

    explanation = check_line(phrase.get("explanation"), "explanation", where, problems, 30, 85)
    if "\n" in explanation or "\r" in explanation:
        problems.append("%s: explanation must be a single paragraph" % where)
    return {
        "translation": translation,
        "explanation": explanation,
    }


def build_surah(surah: int) -> tuple[dict, list[str]]:
    """Return one published chapter payload and its validation problems."""
    problems: list[str] = []
    path = os.path.join(AUTHORED, "%03d.json" % surah)
    with open(path, encoding="utf-8") as handle:
        authored = json.load(handle)

    if authored.get("surah") != surah:
        problems.append("surah %d: authored file has a mismatched surah number" % surah)

    chapter = source.read_chapter(surah)
    verses: dict[str, dict] = {}
    authored_verses = authored.get("verses", {})
    if not isinstance(authored_verses, dict) or not authored_verses:
        problems.append("surah %d: no verses have been authored" % surah)
        return {"surah": surah, "verses": verses}, problems

    for ayah, verse in authored_verses.items():
        where_verse = "surah %d verse %s" % (surah, ayah)
        if ayah not in chapter:
            problems.append("%s: verse does not exist in the reader's chapter data" % where_verse)
            continue
        if not isinstance(verse, dict):
            problems.append("%s: verse entry must be an object" % where_verse)
            continue

        phrases_data = verse.get("phrases", [])
        if not isinstance(phrases_data, list) or not phrases_data:
            problems.append("%s: no phrases have been authored" % where_verse)
            continue

        modern = chapter[ayah].get("en", "")
        cursor = 0
        phrases = []
        for number, authored_phrase in enumerate(phrases_data, 1):
            where = "%s phrase %d" % (where_verse, number)
            phrase = check_phrase(authored_phrase, where, problems)
            translation = phrase["translation"]
            if translation:
                start = modern.find(translation, cursor)
                if start < 0:
                    problems.append("%s: translation phrase is missing or out of order" % where)
                else:
                    gap = modern[cursor:start]
                    if LETTER_OR_NUMBER.search(gap):
                        problems.append("%s: words are skipped between phrase parts" % where)
                    cursor = start + len(translation)
            phrases.append(phrase)

        if LETTER_OR_NUMBER.search(modern[cursor:]):
            problems.append("%s: the phrase parts do not cover the full verse translation" % where_verse)
        verses[ayah] = {"phrases": phrases}

    return {"surah": surah, "verses": verses}, problems


def main() -> int:
    check_only = "--check" in sys.argv
    names = sorted(name for name in os.listdir(AUTHORED) if name.endswith(".json"))
    if not names:
        print("nothing authored yet")
        return 0

    all_problems: list[str] = []
    written = 0
    for name in names:
        surah = int(name[:3])
        data, problems = build_surah(surah)
        all_problems.extend(problems)
        if problems:
            continue
        if not check_only:
            output = os.path.join(ROOT, "data", "pairs_%03d.json" % surah)
            with open(output, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
                handle.write("\n")
        written += 1

    print("%d surah(s) %s" % (written, "checked" if check_only else "written"))
    for problem in all_problems:
        print("  ! %s" % problem)
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
