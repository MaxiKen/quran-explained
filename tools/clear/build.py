#!/usr/bin/env python3
"""Assemble a clear-teaching payload from a plain-text draft.

Writing JSON by hand for 286 entries is a way to lose a brace and a day, so the
entries are written as prose in a text file and assembled here. The draft file
is the source of truth while a sūrah is being written; the JSON is generated.

    python3 tools/clear/build.py --surah 2 --from work/clear/002.txt
    python3 tools/clear/build.py --surah 2 --from work/clear/002.txt --to data

Draft format — one entry per verse, opened by a marker line:

    <<<2:1>>>
    ## What the verse does

    prose...

    ## In short

    - takeaway
    <<<2:2>>>
    ## ...

The marker is `<<<SURAH:VERSE>>>` on a line of its own. Anything before the
first marker is ignored, so notes at the top of the file are harmless.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

MARKER = re.compile(r'^<<<(\d{1,3}):(\d{1,3})>>>\s*$', re.M)

BASED_ON = ('Fī Ẓilāl al-Qurʾān — Sayyid Quṭb (1906-1966), '
            'read from the Urdu rendering')

# STYLE.md 10: the upstream caveat is stated once per chapter, not per entry.
# The Urdu payload carries it in `notice`; switching a chapter to the English
# payload must not lose it, so the same statement travels with this one.
NOTICE = ('Fī Ẓilāl al-Qurʾān is Sayyid Quṭb\u2019s work, first published '
          '1952\u20131966, read here from an Urdu rendering. The entries below '
          'are written from a reading of it as study material. They are not a '
          'translation of the Qur\u02bean and not a substitute for a qualified '
          'teacher, and the positions they report are the author\u2019s own.')


def parse(text: str, surah: int) -> list[tuple[int, str]]:
    """[(verse, entry), ...] in file order, validating markers as it goes."""
    marks = list(MARKER.finditer(text))
    if not marks:
        raise SystemExit('no <<<S:V>>> markers found')
    out = []
    for i, m in enumerate(marks):
        s, v = int(m.group(1)), int(m.group(2))
        if s != surah:
            raise SystemExit(f'marker {s}:{v} does not belong to sūrah {surah}')
        body = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        body = body.strip()
        if not body:
            raise SystemExit(f'{suhrah_label(s, v)}: marker with no entry')
        out.append((v, body))
    return out


def suhrah_label(s: int, v: int) -> str:
    return f'{s}:{v}'


def assemble(surah: int, entries: list[tuple[int, str]], *, partial: bool) -> dict:
    verses = [v for v, _ in entries]
    if verses != sorted(verses):
        raise SystemExit('entries are out of verse order')
    if len(set(verses)) != len(verses):
        dup = [v for v in verses if verses.count(v) > 1]
        raise SystemExit(f'duplicate entries for verses {sorted(set(dup))}')
    if not partial:
        if verses != list(range(1, len(verses) + 1)):
            missing = sorted(set(range(1, max(verses) + 1)) - set(verses))
            raise SystemExit(f'gap in the entries: missing verses {missing}. '
                             f'Use --partial while a prefix is being written.')
    else:
        if verses != list(range(1, len(verses) + 1)):
            raise SystemExit('a partial payload must cover verses 1..N with no gaps')
    return {
        'surah': surah,
        'lang': 'en',
        'dir': 'ltr',
        'source': 'Clear teaching',
        'basedOn': BASED_ON,
        'notice': NOTICE,
        'blocks': [b for _, b in entries],
        'ranges': [f'{surah}:{v}' for v, _ in entries],
        'verses': {str(v): i for i, (v, _) in enumerate(entries)},
    }


def sync_spans(entries, translations):
    """Rewrite each `==span==` from the app's own `ayah_en`.

    The translation contains curly quotes and nested speech that are easy to
    mistype and impossible to eyeball. The gate compares the span to `ayah_en`
    word for word, so the safe thing is to take the span from the data rather
    than from the draft. This reports what it changed.
    """
    import re
    changed = 0
    for i, entry in enumerate(entries):
        text = translations[i]
        new, n = re.subn(r'==(.+?)==', lambda m: '==' + text + '==', entry, count=1, flags=re.S)
        if n and new != entry:
            entries[i] = new
            changed += 1
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--surah', type=int, required=True)
    ap.add_argument('--from', dest='src', required=True, help='the draft .txt')
    ap.add_argument('--to', dest='dst', help='write NNN.json here instead of stdout')
    ap.add_argument('--partial', action='store_true',
                    help='the draft covers verses 1..N only')
    ap.add_argument('--data', default='data', help='where chapter_NNN.js lives')
    ap.add_argument('--no-sync', action='store_true',
                    help='leave the == translation spans exactly as drafted')
    args = ap.parse_args()

    with open(args.src, encoding='utf-8') as fh:
        text = fh.read()
    entries = parse(text, args.surah)
    payload = assemble(args.surah, entries, partial=args.partial)

    if not args.no_sync:
        # the span must equal ayah_en, so take it from the data rather than the
        # draft: curly quotes and nested speech are easy to mistype
        from verify import load_translations
        tr = load_translations(args.surah, args.data)[:len(entries)]
        changed = sync_spans(payload['blocks'], tr)
        if changed:
            print(f'synced {changed} translation span(s) from chapter_{args.surah:03d}.js')

    if args.dst:
        path = os.path.join(args.dst, f'clear_{args.surah:03d}.json')
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        print(f'wrote {path} ({len(entries)} entries)')
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=1)
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
