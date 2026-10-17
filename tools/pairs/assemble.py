#!/usr/bin/env python3
"""Assemble the published pairing from the authored files.

    python3 tools/pairs/assemble.py            # every authored surah
    python3 tools/pairs/assemble.py --check    # check only, write nothing

`tools/pairs/authored/NNN.json` holds the pairing, written by reading
Tafsir al-Tabari in English against the reader's modern translation. This
script checks it and turns it into `data/pairs_NNN.json`, which is what the
reader loads.

The checks are the house style of the reader and the two rules that keep the
pairing honest:

  * a phrase is plain modern English: no Arabic script, no em dash, no
    semicolon outside quotes, and a sentence of its own;
  * the words of the app's own translation that the phrase stands for are
    really in the verse, and the Arabic of the phrase is really in the
    verse;
  * a part is a paragraph that exists in the commentary, and the paragraphs
    of a phrase run in the order they are read. A paragraph may speak to
    more than one phrase, and then it is given to both;
  * the Arabic of a phrase, when given, is the Arabic of the verse.
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

AUTHORED = os.path.join(HERE, 'authored')

ARABIC = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
EM_DASH = re.compile('[—–]')


def check_phrase(phrase: dict, where: str, problems: list) -> None:
    text = phrase.get('text', '')
    if not text.strip():
        problems.append('%s: empty phrase' % where)
        return
    if ARABIC.search(text):
        problems.append('%s: the phrase carries Arabic script' % where)
    if EM_DASH.search(text):
        problems.append('%s: the phrase carries an em dash' % where)
    if ';' in text:
        problems.append('%s: the phrase carries a semicolon' % where)
    letters = [c for c in text if c.isalpha()]
    if not letters or not letters[0].isupper():
        problems.append('%s: the phrase does not start a sentence' % where)
    if len(text.split()) < 3:
        problems.append('%s: the phrase is too short to carry a meaning' % where)
    if len(text.split()) > 60:
        problems.append('%s: the phrase is too long to read at a glance' % where)


def build_surah(surah: int) -> tuple[dict, list]:
    """The published pairing for one surah, and what is wrong with it."""
    problems: list[str] = []
    path = os.path.join(AUTHORED, '%03d.json' % surah)
    with open(path, encoding='utf-8') as handle:
        authored = json.load(handle)

    tafsir_path = os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah)
    with open(tafsir_path, encoding='utf-8') as handle:
        tafsir = json.load(handle)
    chapter = source.read_chapter(surah)

    verses: dict = {}
    for ayah, verse in authored.get('verses', {}).items():
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses'][ayah]['tabari']]
        count = len(source.paragraphs_of(passage))
        phrases = []
        last = -1
        for number, phrase in enumerate(verse.get('phrases', [])):
            where = 'surah %d verse %s phrase %d' % (surah, ayah, number + 1)
            check_phrase(phrase, where, problems)
            if 'range' in phrase:
                start, end = phrase['range']
                parts = list(range(start, end + 1))
            else:
                parts = list(phrase.get('parts', []))
            if not parts:
                problems.append('%s: no part of the commentary is attached' % where)
            for index in parts:
                if not 0 <= index < count:
                    problems.append('%s: paragraph %d does not exist' % (where, index))
            if parts and parts != sorted(parts):
                problems.append('%s: the paragraphs run backwards' % where)
            if parts and parts[0] < last:
                problems.append('%s: the phrases do not follow the order of the passage' % where)
            last = parts[0] if parts else last
            arabic_piece = phrase.get('ar', '')
            if arabic_piece:
                if ARABIC.search(arabic_piece) and chapter.get(ayah, {}).get('ar', ''):
                    if not source.arabic_in(arabic_piece, chapter.get(ayah, {}).get('ar', '')):
                        problems.append('%s: the Arabic given is not in the verse' % where)
            translation = phrase.get('translation', '')
            if translation:
                modern = chapter.get(ayah, {}).get('en', '')
                if translation not in modern:
                    problems.append('%s: the translation given is not in the verse' % where)
            phrases.append({
                'translation': translation,
                'text': phrase.get('text', ''),
                'ar': arabic_piece,
                'parts': parts,
            })
        verses[ayah] = {'phrases': phrases}
    return {'surah': surah, 'verses': verses}, problems


def coverage(surah: int, authored: dict) -> list:
    """The passages of the commentary that no phrase speaks of."""
    tafsir_path = os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah)
    with open(tafsir_path, encoding='utf-8') as handle:
        tafsir = json.load(handle)
    gaps = []
    for ayah, verse in authored.get('verses', {}).items():
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses'][ayah]['tabari']]
        count = len(source.paragraphs_of(passage))
        covered = set()
        for phrase in verse.get('phrases', []):
            covered.update(range(*_span(phrase)))
        missing = [i for i in range(count) if i not in covered]
        if missing:
            gaps.append((ayah, count, missing))
    return gaps


def _span(phrase: dict) -> tuple:
    if 'range' in phrase:
        start, end = phrase['range']
        return start, end + 1
    parts = phrase.get('parts', [])
    return (min(parts), max(parts) + 1) if parts else (0, 0)


def main() -> int:
    check_only = '--check' in sys.argv
    names = sorted(name for name in os.listdir(AUTHORED) if name.endswith('.json'))
    if not names:
        print('nothing authored yet')
        return 0
    all_problems = []
    written = 0
    for name in names:
        surah = int(name[:3])
        data, problems = build_surah(surah)
        all_problems.extend(problems)
        if problems:
            continue
        if not check_only:
            out = os.path.join(ROOT, 'data', 'pairs_%03d.json' % surah)
            with open(out, 'w', encoding='utf-8') as handle:
                json.dump(data, handle, ensure_ascii=False, separators=(',', ':'))
        written += 1
    print('%d surah(s) %s' % (written, 'checked' if check_only else 'written'))
    for problem in all_problems:
        print('  ! %s' % problem)
    if '--gaps' in sys.argv:
        for name in names:
            surah = int(name[:3])
            with open(os.path.join(AUTHORED, name), encoding='utf-8') as handle:
                authored = json.load(handle)
            for ayah, count, missing in coverage(surah, authored):
                print('  - surah %d verse %s: %d of %d passages are not spoken of by any phrase'
                      % (surah, ayah, len(missing), count))
    return 1 if all_problems else 0


if __name__ == '__main__':
    sys.exit(main())
