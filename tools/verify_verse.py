#!/usr/bin/env python3
"""Pre-commit gates for one authored verse — the checks style-check.js cannot do.

    python3 tools/verify_verse.py 2 --range 21 --file draft.txt --draws maarif,ibn-kathir,...
    python3 tools/verify_verse.py 2 --range 21-28             # check what is stored
    python3 tools/verify_verse.py 2 --all                     # check every authored verse

Asserts, for one verse:
  * house layout — one plain intro, then 3-6 own-line `**Headings.**`
  * length meets 75% of the data/plan.json target (a floor, never a ceiling)
  * transliteration of Makkah / Madinah / Bayt al-Maqdis in prose only
  * no Cyrillic homoglyphs (U+0400-U+04FF)
  * the verse quotes the app's own ayah_en for at least 5 consecutive words
  * `draws_on` lists 4+ real source ids
  * ATTRIBUTION — every name passed with --names occurs in that verse's own
    source blocks, after folding diacritics and glottal marks and stripping
    spaces. Romanisation variants are expanded from a fixed, auditable list
    (sun-letter assimilation of al-, ibn/bin, gemination), never by a fuzzy
    matcher. See docs/pitfalls.md: an unasserted name is a check that never ran.

Exits 0 only when every check passed, and always prints the count.
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPAN = r'(\*\*[^*]+\*\*|\*[^*\n]+\*)'
SUN = ('ad', 'ab', 'ath', 'aj', 'ah', 'ak', 'am', 'an', 'as', 'at', 'az', 'al')


def canon(s):
    """Fold diacritics, glottal marks and punctuation to bare [a-z0-9]."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())


def degem(s):
    return re.sub(r'(.)\1+', r'\1', s)


def name_variants(nm):
    """Deterministic romanisation variants — auditable, unlike a fuzzy matcher."""
    out = {nm}
    for n in list(out):
        if n.lower().startswith('al-'):
            out |= {p + n[2:] for p in SUN}
        out.add(n.replace(' ibn ', ' bin '))
        out.add(n.replace(' bin ', ' ibn '))
    return out


def chapter(surah):
    p = os.path.join(ROOT, f'data/chapter_{surah:03d}.js')
    c = open(p, encoding='utf-8').read()
    J = json.loads(c[c.index('['):c.rindex(']') + 1])
    return {v['ayah_no_surah']: v for th in J for v in th['verses']}


def sources(surah):
    return json.load(open(os.path.join(ROOT, f'data/tafsir_{surah:03d}.json'), encoding='utf-8'))


def blob(d, ayah):
    """Every source block that covers this verse — the only place a name may come from."""
    return ' '.join(d['sets'][sid]['blocks'][idx] for sid, idx in d['verses'][str(ayah)].items())


def en_run(text, en):
    """Longest run of consecutive ayah_en words occurring verbatim in the text."""
    cw = canon(text)
    ws = [canon(w) for w in re.sub(r"[.,;:!?\u2013\u2014()\[\]{}\u02bb\u2019\"'\u02bf]", ' ', en).split()]
    best = 0
    for i in range(len(ws)):
        for j in range(i + 1, len(ws) + 1):
            if ''.join(ws[i:j]) in cw:
                best = max(best, j - i)
            else:
                break
    return best


def check(surah, ayah, text, draws, names):
    errs, notes = [], []
    plan = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8')).get(f'{surah}:{ayah}')
    paras = [p for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]
    heads = [p for p in paras if re.fullmatch(r'\*\*[^*]+?\.\*\*', p.strip())]
    n = len(text.split())

    if len(heads) < 3 or len(heads) > 6:
        errs.append(f'{len(heads)} headings, need 3-6 own-line `**Like this.**`')
    if len(paras) < len(heads) + 1:
        errs.append('no plain introduction paragraph before the headings')
    if plan:
        floor = round(plan['words'] * 0.75)
        if n < floor:
            errs.append(f'{n}w is below the floor {floor}w (tier {plan["tier"]}, target {plan["words"]}w)')
    prose = ''.join(x for x in re.split(SPAN, text) if re.fullmatch(SPAN, x) is None)
    for bad, good in (('Mecca', 'Makkah'), ('Madinah', 'Madīnah'), ('Jerusalem', 'Bayt al-Maqdis')):
        if re.search(r'\b' + bad + r'\b', prose):
            errs.append(f'prose spelling "{bad}" must be "{good}" (quotations keep the source spelling)')
    if [c for c in text if '\u0400' <= c <= '\u04ff']:
        errs.append('Cyrillic homoglyph present — retype the transliteration')
    if len(draws) < 4:
        errs.append(f'draws_on has {len(draws)} ids, needs 4+')
    d = sources(surah)
    ids = {s['id'] for s in d['sources']}
    bad = [x for x in draws if x not in ids]
    if bad:
        errs.append(f'draws_on ids not in the payload: {bad}')
    bb, bbd = canon(blob(d, ayah)), degem(canon(blob(d, ayah)))
    for nm in names:
        cn = canon(nm)
        v = [canon(x) for x in name_variants(nm)]
        if cn in bb:
            pass
        elif any(x in bb for x in v):
            notes.append(f'"{nm}" matched {surah}:{ayah}\'s sources only via a romanisation variant')
        elif any(degem(x) in bbd for x in v):
            notes.append(f'"{nm}" matched {surah}:{ayah}\'s sources only with gemination collapsed')
        else:
            errs.append(f'{nm} is named but does not occur in {surah}:{ayah}\'s own sources')
    en = chapter(surah)[ayah]['ayah_en']
    run = en_run(text, en)
    # A 2- or 3-word verse (the disjoint letters) cannot yield a 5-word run, so
    # the bar scales down with the translation's own length.
    total = len([w for w in en.split() if canon(w)])
    need = 5 if total >= 8 else max(1, min(total, 3))

    # THE OPENING PARAGRAPH HAS TO EXPLAIN THE VERSE (maintainer, 2026-10-09).
    # A lead that only sets a mood or asks a question was passing while the
    # explaining happened under the first heading, so a reader who stops after
    # the first paragraph got no account of what the verse says. The opening
    # paragraph must therefore be substantive: long enough to state the verse's
    # subject, quoting the translation itself, and not made only of questions.
    tier = (plan or {}).get('tier', 'A')
    intro = '' if not paras or paras[0].startswith('**') else paras[0]
    min_intro = 90 if tier == 'A' else 60
    if intro:
        if len(intro.split()) < min_intro:
            errs.append(f'opening paragraph is {len(intro.split())}w; tier {tier} needs '
                        f'{min_intro}w that explains what the verse says, not a lead-in')
        if en_run(intro, en) < need:
            errs.append('the opening paragraph must itself quote the translation '
                        f'({need}+ consecutive words) before it starts interpreting')
        qs = [q.strip() for q in re.split(r'(?<=[.?!])\s+', intro) if q.strip()]
        if qs and all(q.endswith('?') for q in qs):
            errs.append('the opening paragraph is all questions — state the verse\'s subject first')
    elif paras:
        errs.append('no opening paragraph before the first heading')
    if run < need:
        errs.append(f"only {run} consecutive words of the app's ayah_en are quoted; need {need}+")
    return n, run, errs, notes


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    surah = int(sys.argv[1])
    names, text_file, rng = [], None, None
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == '--names' and i + 1 < len(args):
            names = [x for x in re.split(r'[|,]', args[i + 1]) if x]
        elif a == '--file' and i + 1 < len(args):
            text_file = args[i + 1]
        elif a == '--draws' and i + 1 < len(args):
            draws = [x for x in re.split(r'[|,]', args[i + 1]) if x]
        elif a == '--range' and i + 1 < len(args):
            lo, _, hi = args[i + 1].partition('-')
            rng = (int(lo), int(hi if hi else lo))
        elif a in ('--all', 'all'):
            rng = 'all'
    if rng is None and not text_file:
        print(__doc__)
        return 2
    gpath = os.path.join(ROOT, 'data', f'guidance_{surah:03d}.json')
    g = json.load(open(gpath, encoding='utf-8')) if os.path.exists(gpath) else {'verses': {}}
    if text_file:
        verses = {str(rng[0]): open(text_file, encoding='utf-8').read()}
        draws_by = {str(rng[0]): draws}
    else:
        keys = sorted(g['verses'], key=int)
        if rng != 'all':
            keys = [k for k in keys if rng[0] <= int(k) <= rng[1]]
        verses = {k: g['verses'][k]['text'] for k in keys}
        draws_by = {k: g['verses'][k].get('draws_on', []) for k in keys}
    if not verses:
        print(f'surah {surah}: no authored verses to check (a chapter in progress is legitimate)')
        return 0
    checked = fails = 0
    for k in sorted(verses, key=int):
        n, run, errs, notes = check(surah, int(k), verses[k], draws_by[k], names)
        checked += 1
        for msg in notes:
            print(f'  note  {surah}:{k} — {msg}')
        if errs:
            fails += 1
            for msg in errs:
                print(f'  FAIL  {surah}:{k} — {msg}')
        else:
            print(f'  ok    {surah}:{k}  {n}w  {run}w of ayah_en quoted')
    print(f'\n{checked - fails}/{checked} verses pass'
          + ('  (names checked against sources: %d)' % len(names) if names else ''))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
