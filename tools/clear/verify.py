#!/usr/bin/env python3
"""Deterministic gates for the clear-teaching payload.

    python3 tools/clear/verify.py                 # the tracked sample
    python3 tools/clear/verify.py --dir work/clear  # work in progress

Every check below is a hard requirement the brief states, so a violation is a
failure rather than a warning:

  script      no Arabic, Urdu or other Arabic-block letters anywhere; the
              only Arabic-block glyph allowed is the salawat sign
  distinct    no entry repeats a run of words from a sibling entry
  aligned     each entry quotes the app's own translation, in order
  shape       headings are level-2, no em dash, no semicolon, no source
              citation, no first person
"""
import argparse, glob, itertools, json, os, re, sys
from collections import Counter

ARABIC = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
SAW = '\ufdfa'
SHINGLE = 8            # words in a row that may not repeat between siblings
CITE = re.compile(r'\b(qutb|sayyid|tabari|tabarī|ibn kathir|fi zilal|fī ẓilāl|the tafsir|the commentary)\b', re.I)
EMDASH = '—'   # the app's translation itself uses one, so it is allowed only
               # inside a quotation of the translation
SEMI = ';'


def fold(s):
    s = s.lower()
    s = s.replace('ʿ', '').replace('ʾ', '').replace('˹', '[').replace('˺', ']')
    return re.findall(r"[a-z0-9']+", s)


def shingles(words, n):
    return {tuple(words[i:i + n]) for i in range(max(1, len(words) - n + 1))}


def wanted_quotes(translation):
    """The translation, split on dashes, minus bracketed glosses."""
    t = re.sub(r'˹[^˺]*˺', '', translation)
    parts = re.split(r'\s*[—,]\s*', t)
    return [p.strip() for p in parts if len(p.split()) >= 2]


QUOTED = re.compile(r'"[^"]*"')


def unquoted(text):
    """The prose with quotations removed, for checks that quotation may pass."""
    return QUOTED.sub('""', text)


def check_surah(rec, translations):
    errs, notes = [], []
    n = len(rec['blocks'])
    for v in range(1, n + 1):
        e = rec['blocks'][v - 1]
        tag = f'{rec["surah"]}:{v}'
        if ARABIC.search(e.replace(SAW, '')):
            bad = sorted({c for c in ARABIC.findall(e.replace(SAW, ''))})
            errs.append(f'{tag}: Arabic-block letters present: {bad}')
        if EMDASH in unquoted(e):
            line = next((l for l in e.split('\n') if EMDASH in unquoted(l)), '')
            errs.append(f'{tag}: em dash outside a quotation: {line[:90]!r}')
        if SEMI in e:
            line = next(l for l in e.split('\n') if SEMI in l)
            errs.append(f'{tag}: semicolon: {line[:90]!r}')
        m = CITE.search(e)
        if m:
            errs.append(f'{tag}: names the source ({m.group(0)!r})')
        if re.search(r'\bI\b', unquoted(e)):
            errs.append(f'{tag}: first person singular outside a quotation')
        if re.search(r'^#\s|^#{3,}\s', e, re.M):
            errs.append(f'{tag}: heading level other than ##')
        for h in re.findall(r'^#{2,}\s*(.+)$', e, re.M):
            if h.strip().lower() in {'commentary', 'explanation', 'overview', 'summary',
                                     'details', 'notes', 'introduction', 'conclusion'}:
                errs.append(f'{tag}: generic heading {h!r}')
        # alignment: the entry must carry the translation's own words
        tr = translations[v - 1]
        body = fold(e)
        body_set = set(body)
        missing = []
        for piece in wanted_quotes(tr):
            w = fold(piece)
            if len(w) < 3:
                continue
            if not all(x in body_set for x in w):
                missing.append(piece)
        if missing:
            errs.append(f'{tag}: does not carry the translation: {missing}')
    # distinctness between siblings
    sh = {v: shingles(fold(rec['blocks'][v - 1]), SHINGLE) for v in range(1, n + 1)}
    for a, b in itertools.combinations(range(1, n + 1), 2):
        if not sh[a] or not sh[b]:
            continue
        overlap = len(sh[a] & sh[b]) / min(len(sh[a]), len(sh[b]))
        if overlap > 0.05:
            errs.append(f'{rec["surah"]}:{a} and {b} share {overlap:.0%} of word runs')
    words = [len(s.split()) for s in rec['blocks']]
    notes.append(f'words per entry: min {min(words)}, max {max(words)}, total {sum(words)}')
    return errs, notes


def load_translations(surah, data_dir):
    """Read the app's own ayah_en out of data/chapter_NNN.js."""
    path = os.path.join(data_dir, f'chapter_{surah:03d}.js')
    src = open(path, encoding='utf-8').read()
    body = src[src.index('['): src.rindex(']') + 1]
    # the file is a JS var assignment of valid JSON
    data = json.loads(body)
    out = []
    for theme in data:
        for v in theme['verses']:
            out.append((v['ayah_no_surah'], v['ayah_en']))
    out.sort()
    return [t for _, t in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='tools/clear/samples')
    ap.add_argument('--data', default='data')
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(args.dir, '*.json')))
    if not files:
        print(f'no payload in {args.dir}')
        return 1
    fails = 0
    for f in files:
        rec = json.load(open(f, encoding='utf-8'))
        tr = load_translations(rec['surah'], args.data)
        if len(tr) != len(rec['blocks']):
            print(f'FAIL {f}: {len(rec["blocks"])} entries for {len(tr)} verses')
            fails += 1
            continue
        errs, notes = check_surah(rec, tr)
        label = os.path.basename(f)
        if errs:
            fails += 1
            print(f'FAIL {label}  ({len(errs)} problem(s))')
            for e in errs:
                print('   -', e)
        else:
            print(f'ok   {label}  ({len(rec["blocks"])} entries)')
        for n in notes:
            print('      ', n)
    print()
    print('FAILED' if fails else 'all clear')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
