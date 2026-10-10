#!/usr/bin/env python3
"""Ingest an upstream tafsīr edition into data/tafsir_NNN.json as a new set.

    python3 tools/build_sets.py qushayri wahidi          # write
    python3 tools/build_sets.py qushayri --dry           # report only
    python3 tools/build_sets.py qushayri --src /tmp/up/tafsir

The six original sets arrived with the corpus; this is the reproducible path for
the two added on 2026-10-09 (al-Qushayrī's Laṭāʾif al-ishārāt, and al-Wāḥidī's
Asbāb al-nuzūl), so a later session can rebuild the payload without a human
re-pasting anything. It writes nothing to the guidance layer.

Layout mirrors what is already stored, so the reader and the packet need no
special case:

    sets[id] = { "ranges": ["2:2-5", ...], "blocks": ["text", ...] }
    verses[ayah][id] = <index into blocks>

A block is one run of commentary; several consecutive verses may point at the
same index, and `ranges[i]` records what that block covers. Verses an edition
does not cover get no index at all — `getVerseCommentaryAll` skips empty text,
so the reader simply shows one fewer card rather than a stub claiming absence.

**Upstream damage, verified 2026-10-09, guarded here on purpose.** The file
served as `en-asbab-al-nuzul-by-al-wahidi` is polluted: 693 of its 1,089 entries
open with text that belongs to `en-al-qushairi-tafsir`, and 120 are duplicates
inside the same file. Only an entry that carries the book's OWN bracketed
[surah:ayah] reference into this surah and matches no Qushayrī entry here is
ingested — 395 of 1,089 survive, and those are the only ones this repo will
attribute to al-Wāḥidī. Do not relax the guard to raise coverage: the discarded
entries are not asbāb, and ingesting them would put al-Qushayrī's words under
al-Wāḥidī's name, which is the one thing the whole pipeline exists to prevent.

Two upstream shapes are handled:

  per-ayah   one entry = one verse (al-Qushayrī).
  occasion   one entry = the occasion of a verse or a run of verses (al-Wāḥidī).
             Each entry is attached to the verses its own bracketed [s:a] /
             [s:a-b] references name, never to a range invented here, and only
             within OCCASION_WINDOW verses of where the file files it. An entry
             that names nothing is attached to its own ayah alone.

Text is normalised for the packet, not rewritten: replacement characters left by
the upstream's own bad decoding are dropped, and quotation marks and dashes are
folded to the ones the rest of the corpus uses. Nothing is paraphrased or
translated — every word stored here is verbatim from the edition.
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser('~/.cache/tafsir_api/tafsir')

SETS = {
    'qushayri': {
        'slug': 'en-al-qushairi-tafsir',
        'label': 'Laṭāʾif al-Ishārāt',
        'author': 'Abū al-Qāsim al-Qushayrī (d. 465 AH)',
        'mode': 'per-ayah',
    },
    'wahidi': {
        'slug': 'en-asbab-al-nuzul-by-al-wahidi',
        'label': 'Asbāb al-Nuzūl',
        'author': 'al-Wāḥidī (d. 468 AH)',
        'mode': 'occasion',
    },
}

# [2:104] or [2:102-104]; sometimes written [2:102, 103]
REF = re.compile(r'\[(\d{1,3})\s*:\s*(\d{1,3})'
                 r'(?:\s*[-,\u2013]\s*(\d{1,3}))?\]')
OCCASION_WINDOW = 25      # how far from the filed ayah a reference may sit
MAX_SPREAD = 25           # an occasion is not allowed to cover a whole sūrah

# the corpus's own punctuation, so the packet's canon() and the app's renderer
# see one convention instead of three
DASH = re.compile(r'\s*[\u2010\u2011\u2012\u2013]\s*')

def normalise(text):
    # Upstream lost some bytes to a bad decode. Where the lost character sat
    # between two letters it was a hamza or a quote, so it becomes an apostrophe
    # ("Sa'd", "ra'ina") rather than a space ("Sa d"); anywhere else it is
    # dropped to a space. Nothing else about the wording is touched, and the
    # packet's canon() folds apostrophes away, so traceability is unaffected.
    text = re.sub(r'(?<=[a-zA-Z])\ufffd(?=[a-zA-Z])', "'", text)
    text = text.replace('\ufffd', ' ')                 # remaining decode damage
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u00ad', '').replace('\u200b', '')   # soft hyphen, ZWSP
    text = re.sub(r'([a-z])-\s+([a-z])', r'\1 \2', text)      # 'con- duct' line break
    text = DASH.sub(' - ', text)
    text = text.replace('\u060c', ',').replace('\u061b', ';').replace('\u061f', '?')
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r' ?\n ?', '\n\n', text.strip())            # keep paragraph breaks
    return text


def entries(src, slug, surah):
    p = os.path.join(src, slug, f'{surah}.json')
    if not os.path.exists(p):
        return []
    data = json.load(open(p, encoding='utf-8'))
    out, seen = [], set()
    for a in data.get('ayahs') or []:
        if not isinstance(a, dict):
            continue
        t = normalise(a.get('text') or '')
        if len(t.split()) < 4:
            continue
        # key on the verse too: the same text filed at 2:1 and 2:2 is a run of
        # commentary, which belongs in one shared block, not dropped. Only an
        # exact repeat at the SAME verse is upstream noise (120 of those).
        key = (int(a['ayah']), t[:160])
        if key in seen:
            continue
        seen.add(key)
        out.append((int(a['ayah']), t))
    out.sort()
    return out


def qushayri_texts(src, surah):
    """Everything al-Qushayrī's file says for this surah, for the pollution test."""
    p = os.path.join(src, SETS['qushayri']['slug'], f'{surah}.json')
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding='utf-8'))
    return [normalise(a.get('text') or '') for a in d.get('ayahs') or []]


def contaminated(text, others):
    """Is this 'asbāb' entry really al-Qushayrī? Two probes, because the
    pollution is not always at the very start of the entry."""
    head = text[:160]
    mid = text[400:560]
    for o in others:
        if head and head in o:
            return True
        if mid and len(mid) > 100 and mid in o:
            return True
    return False


def cover(es, mode, surah, last_ayah):
    """[(ayah, text)] -> {verse: entry index} — which verses each entry speaks for.

    An occasion entry is attached only to verses its OWN bracketed references
    name, so a run of commentary is never stretched over neighbours by guesswork.
    """
    assign = {}
    for i, (ayah, text) in enumerate(es):
        if mode == 'per-ayah':
            if 1 <= ayah <= last_ayah:
                assign.setdefault(ayah, i)
            continue
        hits = {ayah}
        for m in REF.finditer(text[:3000]):
            s, a = int(m.group(1)), int(m.group(2))
            end = int(m.group(3)) if m.group(3) else a
            if s != surah or abs(a - ayah) > OCCASION_WINDOW:
                continue
            for v in range(a, min(end, a + MAX_SPREAD) + 1):
                hits.add(v)
        for v in sorted(h for h in hits if 1 <= h <= last_ayah):
            assign.setdefault(v, i)
    return assign


def verse_count(surah):
    """Highest ayah number in the chapter data — the ceiling an entry may spread to."""
    p = os.path.join(ROOT, f'data/chapter_{surah:03d}.js')
    if not os.path.exists(p):
        return 0
    txt = open(p, encoding='utf-8', errors='ignore').read()
    return max([int(m.group(1)) for m in re.finditer(r'"ayah_no_surah"\s*:\s*(\d+)', txt)] or [0])


def build(src, sid, cfg, dry=False):
    covered = 0
    words = 0
    per_surah = {}
    guards = {}
    for s in range(1, 115):
        path = os.path.join(ROOT, f'data/tafsir_{s:03d}.json')
        if not os.path.exists(path):
            continue
        es = entries(src, cfg['slug'], s)
        if cfg['mode'] == 'occasion':
            others = qushayri_texts(src, s)
            kept, dropped = [], 0
            for ayah, text in es:
                refs_here = any(int(m.group(1)) == s for m in REF.finditer(text[:3000]))
                if not refs_here or contaminated(text, others):
                    dropped += 1
                    continue
                kept.append((ayah, text))
            guard = (len(kept), dropped)
            es = kept
        d = json.load(open(path, encoding='utf-8'))
        # rebuild, never merge: stale indices from an earlier run would point into
        # a blocks array that no longer exists, and a wrong index is a wrong quote
        for v in list(d['verses']):
            d['verses'][v].pop(sid, None)
        d['sets'].pop(sid, None)
        last = verse_count(s) or max([int(k) for k in d['verses']] or [0])
        assign = cover(es, cfg['mode'], s, last) if es else {}
        blocks, ranges = [], []
        idx = {}
        for ayah, i in sorted(assign.items()):
            text = es[i][1]
            if text not in idx:
                idx[text] = len(blocks)
                blocks.append(text)
                ranges.append([ayah, ayah])
            else:
                r = ranges[idx[text]]
                r[1] = ayah if ayah == r[1] + 1 else r[1]
        for bi, (a, b) in enumerate(ranges):
            for v in range(a, b + 1):
                d['verses'].setdefault(str(v), {})[sid] = bi
        d['sets'][sid] = {
            'ranges': [f"{s}:{a}" if a == b else f"{s}:{a}-{s}:{b}" for a, b in ranges],
            'blocks': blocks,
        }
        src_ids = [x['id'] for x in d['sources']]
        if sid not in src_ids:
            d['sources'].append({'id': sid, 'label': cfg['label'], 'author': cfg['author']})
        n = sum(1 for v in d['verses'] if sid in d['verses'][v])
        covered += n
        if cfg['mode'] == 'occasion':
            guards[s] = guard
        words += sum(len(b.split()) for b in blocks)
        per_surah[s] = n
        if not dry:
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(d, fh, ensure_ascii=False, separators=(',', ':'))
                fh.write('\n')
    print(f"{sid}: {covered} verses ({100*covered/6236:.1f}%), "
          f"{words} words, in {sum(1 for v in per_surah.values() if v)} sūrahs")
    if guards:
        kept = sum(g[0] for g in guards.values())
        drop = sum(g[1] for g in guards.values())
        print(f"  guard: kept {kept} asbāb entries, refused {drop} "
              f"(no [surah:ayah] of its own, or al-Qushayrī's text)")
    top = sorted(per_surah.items(), key=lambda k: -k[1])[:8]
    print(f"  heaviest: " + ', '.join(f'{s} ({n})' for s, n in top))


def fetch(dst):
    """Populate the cache from the API for the two slugs, 114 + 77 small files."""
    for cfg in SETS.values():
        slug = cfg['slug']
        os.makedirs(os.path.join(dst, slug), exist_ok=True)
        for s in range(1, 115):
            p = os.path.join(dst, slug, f'{s}.json')
            if os.path.exists(p) and os.path.getsize(p) > 2:
                continue
            url = f'repos/spa5k/tafsir_api/contents/tafsir/{slug}/{s}.json'
            r = subprocess.run(['gh', 'api', url, '-H', 'Accept: application/vnd.github.raw'],
                               capture_output=True, text=True)
            if r.returncode != 0:
                open(p, 'w').close()               # the edition has no file here
                continue
            open(p, 'w', encoding='utf-8').write(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sets', nargs='+', choices=sorted(SETS))
    ap.add_argument('--src', default=None, help='directory of upstream <slug>/<n>.json files')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--fetch', action='store_true', help='download the upstream files first')
    a = ap.parse_args()
    src = a.src or CACHE
    if a.fetch or not os.path.isdir(os.path.join(src, SETS['qushayri']['slug'])):
        if not a.src:
            print(f'fetching upstream into {src}')
            fetch(src)
        else:
            sys.exit(f'{src} has no {SETS["qushayri"]["slug"]} — pass --src or --fetch')
    for sid in a.sets:
        build(src, sid, SETS[sid], dry=a.dry)


if __name__ == '__main__':
    main()
