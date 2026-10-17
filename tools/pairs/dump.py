#!/usr/bin/env python3
"""Dump the material for a surah, in a form that can be read and paired.

    python3 tools/pairs/dump.py 112          # every verse of surah 112
    python3 tools/pairs/dump.py 112 1-2      # only those verses
    python3 tools/pairs/dump.py 112 --labels # only the headings, no bodies

For each verse it prints the reader's own translation, the Arabic, and
Ṭabarī's paragraphs, numbered as the passage numbers. The authored file
is written against those numbers.
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
    first = last = None
    if len(sys.argv) > 2 and '-' in sys.argv[2]:
        start, end = sys.argv[2].split('-')
        first, last = int(start), int(end)
    elif len(sys.argv) > 2 and sys.argv[2].isdigit():
        first = last = int(sys.argv[2])
    labels_only = '--labels' in sys.argv

    tafsir = json.load(open(os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah), encoding='utf-8'))
    chapter = source.read_chapter(surah)
    numbers = sorted(int(a) for a in tafsir['verses'])
    for ayah in numbers:
        if first is not None and not first <= ayah <= last:
            continue
        passage = tafsir['sets']['tabari']['blocks'][tafsir['verses'][str(ayah)]['tabari']]
        paragraphs = source.paragraphs_of(passage)
        verse = chapter.get(str(ayah), {})
        print('=== %d:%d  (%d passages) ===' % (surah, ayah, len(paragraphs)))
        print('EN: %s' % verse.get('en', ''))
        print('AR: %s' % verse.get('ar', ''))
        for index, paragraph in enumerate(paragraphs):
            mark = '>>' if source.is_phrase_opening(paragraph) else '  '
            if labels_only:
                if mark == '>>':
                    print('%s %3d | %s' % (mark, index, paragraph))
                continue
            print('%s %3d | %s' % (mark, index, paragraph))
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
