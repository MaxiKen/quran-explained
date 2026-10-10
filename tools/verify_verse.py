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
  * THE LEAD WALKS THE VERSE (maintainer, 2026-10-10): every phrase of the
    translation is quoted in order in the opening paragraph and explained there,
    the lead carries >= 20% of the verse and the tier floor in LEAD_FLOOR, and the
    paragraph may not open by quoting the whole verse in one line
  * `draws_on` lists real source ids, 5+ at tiers A and B and 4+ at C, never
    more than the sets that actually cover the verse
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


# The lead has to WALK the verse: every meaningful phrase of the translation
# quoted in order, each one explained where it stands (maintainer, 2026-10-10).
# Punctuation is what makes a phrase in this translation, so the split is on
# punctuation only — no clause parser, nothing that could drift.
PHRASE_SPLIT = r'[,;:.!?…\u2013\u2014\u201c\u201d\u2018\u2019]'
# The ˹…˺ brackets in this translation are editorial marks and not phrase edges —
# "they are not ˹truly˺ guided" is one phrase — so they are removed before splitting.
EDITORIAL = r'[\u02f9\u02fa\u02bb]'
LEAD_FLOOR = {'A': 240, 'B': 170, 'C': 110}
LEAD_SHARE = 0.20          # the lead does the most work, so it carries 1/5 of the verse
# ... and the budget it may spend doing it, which is where compile_guidance caps it
LEAD_CAP = {'A': 620, 'B': 460, 'C': 320}


def phrases(en, min_words=3):
    """The verse cut into the chunks a lead must quote; short ones merge sideways."""
    parts = [x.strip() for x in re.split(PHRASE_SPLIT, re.sub(EDITORIAL, '', en)) if canon(x.strip())]
    out = []
    for p in parts:
        n = len([w for w in p.split() if canon(w)])
        if out and n < min_words:
            out[-1] += ', ' + p
        else:
            out.append(p)
    if len(out) > 1 and len([w for w in out[0].split() if canon(w)]) < min_words:
        out[0] = out[0] + ', ' + out[1]
        out.pop(1)
    return out


def uncovered(lead, en):
    """Phrases the lead failed to quote verbatim, or quoted out of order."""
    cl, bad = canon(lead), []          # canon() drops the editorial marks from both sides
    at, order = 0, True
    for p in phrases(en):
        key = ''.join(canon(w) for w in p.split() if canon(w))
        i = cl.find(key)
        if i < 0:
            bad.append(p)
        elif i < at:
            order = False
        else:
            at = i + len(key)
    return bad, order


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
        # The plan carries the enforced floor (0.75x the target) so no gate re-derives it.
        # A verse whose material is below it is not exempted: plan['authored_only'] means
        # it must be composed, and compile_guidance.py refuses to splice it.
        floor = plan.get('floor', round(plan['words'] * 0.75))
        if n < floor:
            note = (' — this verse holds only %dw of source material, so it is AUTHORED-ONLY: '
                    'compose it, do not pad it' % plan['avail']) if plan.get('authored_only') else ''
            errs.append(f'{n}w is below the floor {floor}w (tier {plan["tier"]}, '
                        f'target {plan["words"]}w{note})')
    prose = ''.join(x for x in re.split(SPAN, text) if re.fullmatch(SPAN, x) is None)
    for bad, good in (('Mecca', 'Makkah'), ('Madinah', 'Madīnah'), ('Jerusalem', 'Bayt al-Maqdis')):
        if re.search(r'\b' + bad + r'\b', prose):
            errs.append(f'prose spelling "{bad}" must be "{good}" (quotations keep the source spelling)')
    if [c for c in text if '\u0400' <= c <= '\u04ff']:
        errs.append('Cyrillic homoglyph present — retype the transliteration')
    # HOW MANY SETS A VERSE HAS TO BE SEEN THROUGH. Raised with the bands on
    # 2026-10-09: a 975-word verse cannot be honest on four sets any more than a
    # 200-word one could. Capped by what actually covers the verse, because
    # al-Qushayrī and al-Wāḥidī are selective and a verse with six sets must not
    # be failed for wanting eight.
    d = sources(surah)
    ids = {s['id'] for s in d['sources']}
    have = d['verses'].get(str(ayah), {}) if isinstance(d.get('verses'), dict) else {}
    live = [sid for sid in ids if have.get(sid) is not None]
    need_sets = min(5 if (plan or {}).get('tier') in ('A', 'B') else 4, len(live))
    if draws is None:
        notes.append('draws_on not supplied — the 5+/4+ check is skipped; pass --draws when '
                     'checking an authored draft, and record the same ids in the payload')
        draws = []
    elif len(draws) < need_sets:
        errs.append(f'draws_on has {len(draws)} ids, needs {need_sets}+ '
                    f'(this verse is covered by {len(live)} of {len(ids)} sets)')
    bad = [x for x in draws if x not in ids] if draws else []
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
    min_intro = (plan or {}).get('lead_floor') or LEAD_FLOOR.get(tier, 170)
    if intro:
        nw = len(intro.split())
        if nw < min_intro:
            errs.append(f'opening paragraph is {nw}w; tier {tier} needs {min_intro}w of '
                        'phrase-by-phrase explanation, not a lead-in')
        elif n and nw < LEAD_SHARE * n:
            errs.append(f'opening paragraph is {nw}w of a {n}w verse; it has to do the most '
                        f'work, so it needs {int(LEAD_SHARE * n) + 1}w minimum')
        if en_run(intro, en) < need:
            errs.append('the opening paragraph must itself quote the translation '
                        f'({need}+ consecutive words) before it starts interpreting')
        # THE LEAD WALKS THE VERSE (maintainer, 2026-10-10): the verse is split
        # into its meaningful phrases and each one is quoted and explained where
        # it stands, in order. Evidence — hadith, cross-references, ruling,
        # occasion, theology — belongs under the headings, not here.
        miss, ordered = uncovered(intro, en)
        if miss:
            errs.append(f'lead does not quote these phrases of the translation: '
                        + ' | '.join(f'"{m}"' for m in miss[:4])
                        + (f' (+{len(miss) - 4} more)' if len(miss) > 4 else ''))
        if not ordered:
            errs.append('the lead quotes the verse out of order — walk it phrase by phrase')
        tot = len([w for w in en.split() if canon(w)])
        ital = re.match(r'^\s*\*([^*]+)\*', intro)
        if ital and en_run(ital.group(1), en) >= max(need, tot - 1):
            errs.append('the commentary must not open by quoting the whole verse in one line; '
                        'quote it phrase by phrase and explain each part where it stands')
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
    names, text_file, rng, draws = [], None, None, None
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
        if rng is None or rng == 'all':
            print('--file needs --range LO (or LO-HI with a single draft) to say which verse '
                  'this draft is: python3 tools/verify_verse.py 2 --range 53 --file draft.txt')
            return 2
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
