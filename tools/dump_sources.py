#!/usr/bin/env python3
"""Dump everything needed to author a range of verses.

This is the read-before-you-write step. Run it for the range you are about to
author and read the output *before* writing a word — never after.

    python3 tools/dump_sources.py 2 8 20        # surah 2, verses 8-20
    python3 tools/dump_sources.py 2 8 20 --ik   # include Ibn Kathir's prose
    python3 tools/dump_sources.py 2 8 20 --all  # full text, nothing truncated

Without a flag the five concise sources are shown in full-ish and Ibn Kathir is
filtered down to the sentences carrying named authorities and definitions,
because his entries run to thousands of words per verse.

Arabic in the Ibn Kathir filter is replaced with [ar] to keep the output
readable; use --all when you need the actual Arabic.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCISE = ('mukhtasar', 'jalalayn', 'tanwir', 'maarif', 'tazkirul')
AUTH = re.compile(
    r'(Bukhari|Muslim|Ahmad|Tirmidhi|Abu Dawud|Nasa|Ibn Majah|Hakim|Tabarani|'
    r'Ibn Jarir|Darimi|Ibn Hibban|Marduwyah|recorded|reported|narrated|said:|'
    r'Ibn Abbas|Ibn Masud|Abu Hurairah|Anas|Aishah|Ubayy|Mujahid|Qatadah|'
    r'Ikrimah|As-Suddi|Abul Aliyah|consensus|means|meaning|it is said|'
    r'Scholars|Umar|Ali\b|Abdullah)')
ARABIC = re.compile(r'[\u0600-\u06FF\u0750-\u077F]+')


def chapter_verses(surah):
    p = os.path.join(ROOT, f'data/chapter_{surah:03d}.js')
    c = open(p, encoding='utf-8').read()
    J = json.loads(c[c.index('['):c.rindex(']') + 1])
    return {v['ayah_no_surah']: v for th in J for v in th['verses']}


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    surah, lo, hi = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    ik_mode = '--ik' in sys.argv or '--all' in sys.argv
    full = '--all' in sys.argv

    V = chapter_verses(surah)
    d = json.load(open(os.path.join(ROOT, f'data/tafsir_{surah:03d}.json'), encoding='utf-8'))
    plan_p = os.path.join(ROOT, 'data/plan.json')
    plan = json.load(open(plan_p, encoding='utf-8')) if os.path.exists(plan_p) else {}

    print(f"=== SURAH {surah}, VERSES {lo}-{hi} ===\n")
    print("--- THE APP'S OWN TRANSLATION (quote these words) ---")
    for a in range(lo, hi + 1):
        print(f"{surah}:{a}  {V[a].get('ayah_en', '')}")
        print(f"      {V[a].get('ayah_ar', '')}")

    print("\n--- PLAN (tier and word target) ---")
    tot = 0
    for a in range(lo, hi + 1):
        p = plan.get(f'{surah}:{a}')
        if not p:
            print(f"{surah}:{a}  NO PLAN ENTRY — run tools/tier_verses.py")
            continue
        tot += p['words']
        print(f"{surah}:{a}  Tier {p['tier']}  {p['words']}w  tr={p['tr_words']}w "
              f"ar={p['ar_words']}w mspec={p['max_specific']} nspec={p['n_specific']} "
              f"{p['flags']}{' REFRAIN' if p['refrain'] else ''}")
    print(f"  range total: {tot:,} words across {hi - lo + 1} verses")

    for a in range(lo, hi + 1):
        m = d['verses'][str(a)]
        print(f"\n\n===================== {surah}:{a} =====================")
        for sid in CONCISE:
            blk = d['sets'][sid]
            t = blk['blocks'][m[sid]]
            rng = blk['ranges'][m[sid]]
            lim = 100000 if full else 1400
            print(f"\n[{sid}] range {rng}, {len(t.split())}w")
            print('  ' + t[:lim].replace('\n', '\n  '))
        if ik_mode:
            blk = d['sets']['ibn-kathir']
            t = blk['blocks'][m['ibn-kathir']]
            rng = blk['ranges'][m['ibn-kathir']]
            print(f"\n[ibn-kathir] range {rng}, {len(t.split())}w")
            if full:
                print('  ' + t.replace('\n', '\n  '))
            else:
                sents = re.split(r'(?<=[.!?])\s+', ARABIC.sub('[ar]', t))
                keep = ' '.join(s for s in sents if AUTH.search(s))
                print('  ' + keep[:3000].replace('\n', '\n  '))
    return 0


if __name__ == '__main__':
    sys.exit(main())
