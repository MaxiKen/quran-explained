#!/usr/bin/env python3
"""Template for authoring guidance. Copy, fill in, run.

    cp tools/author_template.py /tmp/g003.py
    $EDITOR /tmp/g003.py     # set SURAH and fill the VERSES dict
    python3 /tmp/g003.py

Keep the working copy OUTSIDE the repo (/tmp is fine) — only the JSON it
writes belongs in Git. What the script itself does belong in Git is any
reusable improvement to this template.

What it enforces for you:
  * every verse gets range + draws_on + text, in the payload's shape
  * a Cyrillic-homoglyph scan (this has bitten the project before)
  * merges into an existing guidance file instead of overwriting it, so a
    surah can be authored over several sessions
  * reports each verse against its plan target and flags any outside 25%
"""
import json
import os
import unicodedata

# ---- edit these two things ----
SURAH = 3
TITLE = "Ali 'Imran"

VERSES = {
    # 1: dict(range="3:1", draws_on=[...source ids...], text="""..."""),
    #
    # draws_on ids must come from the payload: ibn-kathir, maarif, tazkirul,
    # tanwir, jalalayn, mukhtasar.
    #
    # The text is the single-voice commentary. Write it as prose, not as a
    # source-by-source summary. Quote the app's own translation wording and
    # work through it. Name narrators and collectors inline, exactly as the
    # sources give them — never invent a hadith number.
}
# -------------------------------

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))

# --- integrity: no Cyrillic homoglyphs in transliterated Arabic ---
bad = []
for a, v in VERSES.items():
    for ch in v['text']:
        if 0x0400 <= ord(ch) <= 0x04FF:
            bad.append((a, ch, unicodedata.name(ch, '?')))
assert not bad, f'Cyrillic homoglyphs: {bad}'

path = os.path.join(ROOT, f'data/guidance_{SURAH:03d}.json')
out = dict(surah=SURAH, lang='en', dir='ltr', title=TITLE, verses={})
if os.path.exists(path):
    out = json.load(open(path, encoding='utf-8'))
    out['verses'] = out.get('verses', {})

for a, v in VERSES.items():
    out['verses'][str(a)] = dict(
        range=v['range'],
        draws_on=v['draws_on'],
        text=' '.join(v['text'].split()),
    )
out['verses'] = {k: out['verses'][k] for k in sorted(out['verses'], key=int)}

# guidance files are pretty-printed so they are reviewable in a diff;
# tafsir_*.json and plan.json are NOT (see .gitattributes)
with open(path, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
    fh.write('\n')

tot = 0
print(f'=== guidance_{SURAH:03d}.json ===')
for a in sorted((int(k) for k in out['verses'])):
    v = out['verses'][str(a)]
    w = len(v['text'].split())
    key = f'{SURAH}:{a}'
    tgt = PLAN[key]['words'] if key in PLAN else None
    tot += w
    if tgt:
        off = abs(w - tgt) / tgt
        flag = '' if off <= 0.25 else f'  <-- {off:.0%} off target'
        print(f'  {key}  Tier {PLAN[key]["tier"]}  {w:4d}w (target {tgt}){flag}')
    else:
        print(f'  {key}  {w:4d}w  (no plan entry)')
print(f'  {len(out["verses"])} verses, {tot:,} words, {os.path.getsize(path):,} bytes')
