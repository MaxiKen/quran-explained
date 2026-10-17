#!/usr/bin/env python3
"""Show the material for pairing, one verse at a time.

    python3 tools/pairs/show.py 1              # surah 1, every verse
    python3 tools/pairs/show.py 2 1-20         # surah 2, verses 1 to 20
    python3 tools/pairs/show.py 2 255 --full   # with the whole passage

For each verse it prints the reader's own translation, already broken into
the phrases a reader would call phrases, and Ṭabarī's paragraphs, numbered
as the passage numbers. The pairing is written against those numbers.

    python3 tools/pairs/show.py 2 255 --full
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import source  # noqa: E402


def verse_material(surah: int, ayah: int, full: bool = False) -> str:
    tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah), encoding='utf-8'))
    passage = tafsir['sets']['tabari']['blocks'][tafsir['verses'][str(ayah)]['tabari']]
    paragraphs = source.paragraphs_of(passage)
    modern = source.read_chapter(surah).get(str(ayah), {}).get('en', '')
    lines = ['=== %d:%d ===' % (surah, ayah)]
    lines.append('TRANSLATION:')
    for clause in source.split_clauses(modern):
        lines.append('  %s' % clause['text'])
    lines.append('TABARI:')
    for index, paragraph in enumerate(paragraphs):
        if full:
            lines.append('  [%d] %s' % (index, paragraph))
        else:
            label = source.quick_label(paragraph)
            lines.append('  [%d] %s' % (index, label))
    return '\n'.join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    surah = int(sys.argv[1])
    first = last = None
    if len(sys.argv) > 2 and '-' in sys.argv[2]:
        start, end = sys.argv[2].split('-')
        first, last = int(start), int(end)
    elif len(sys.argv) > 2:
        first = last = int(sys.argv[2])
    full = '--full' in sys.argv
    tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah), encoding='utf-8'))
    numbers = sorted(int(a) for a in tafsir['verses'])
    if first is None:
        first, last = numbers[0], numbers[-1]
    for ayah in numbers:
        if first <= ayah <= last:
            print(verse_material(surah, ayah, full))
            print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
