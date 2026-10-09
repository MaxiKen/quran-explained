#!/usr/bin/env python3
"""Number the source sentences of a verse range, so an editor can cite them.

    python3 tools/verse_packet.py 2 41-46 [--all] [--min 4]

Prints, per verse: the app translation, the plan tier/floor/flags, and a
ranked shortlist of sentences drawn from ALL SIX sets. Each sentence carries
a ref (SET:paragraph:sentence) and is the literal text stored in
data/tafsir_NNN.json — nothing here is composed, so a packet can be diffed
against the data. The shortlist is what a compiler reads: ~40 sentences
instead of the ~15k characters of raw blocks the six sets hold for a verse.

Ranking is deliberately dumb and auditable (see KEEP/CUT below): it prefers
lexical definitions, rationale, answered questions and the short gloss sets,
and drops isnad chains, editorial asides and cross-references. It is a
shortlist, not a summary — every sentence it rejects is still addressable by
number if an editor wants it.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))

SETS = {'jalalayn': 'J', 'maarif': 'M', 'ibn-kathir': 'K',
        'tazkirul': 'T', 'tanwir': 'D', 'mukhtasar': 'X'}
AR = re.compile(r'[\u0600-\u060F\u0610-\u06FF\u0750-\u077F\u08A0-\u08FF'
                r'\uFB50-\uFDFF\uFE70-\uFEFF]+')
# markers of a sentence worth putting in front of a reader
KEEP = [
    (r'\b(lexically|linguistically|in Arabic|the word|means|signifies|gloss)', 3),
    (r'\b(in the terminology|according to|the first|second sense|other? wise)', 2),
    (r'\b(why|what (does|is)|one may (well )?ask|the reason|this is because|hence)', 3),
    (r'\b(the verse|this (verse|sentence|phrase)|the command|the address|it refers)', 2),
    (r'\b(permitted|forbidden|obligatory|required|disliked|valid|invalid|must not)', 2),
    (r'\b(consensus|majority|the jurists|Ab[uū] ?Han[iī]fah|M[aā]lik|Sh[aā]fiʿ|Aḥmad)', 1),
    (r'\b(however|but |on the other hand|they differed|a second opinion)', 2),
]
CUT = [
    r'^\s*$',
    r'\[ar\]',
    r'see (the )?(Note|introduction|Appendix)',
    r'^\(\d+\)\s*$',
    r'narrated to us .* from .* from',
    r'\bit was reported on the authority of',
    r'^\s*(He said|They said|I heard)\b.{0,25}$',
    r'\bhappy is the one|wretched is the one\b.*^\s*$',
    r'^\s*[\u2018"].{0,20}[\u2019"]\s*:?\s*$',
    r'^\s*\d+[:.\u2013-]\d+\s*$',
]


def clean(s):
    s = AR.sub('', s)
    s = re.sub(r'\[\s*ar\s*\]', '', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def sentences(para):
    """Split on . ! ? : followed by a capital, sparing abbreviations."""
    para = re.sub(r'\b(pp?|no|vs|ie|eg|v|ch)\.', r'\1<DOT>', para)
    parts = re.split(r'(?<=[.!?:])\s+(?=[A-Z\u2018"(])', para)
    return [p.replace('<DOT>', '.').strip() for p in parts if p.strip()]


def load(surah):
    return json.load(open(os.path.join(ROOT, f'data/tafsir_{surah:03d}.json'), encoding='utf-8'))


def verse_sentences(d, ayah):
    """{set: [(para_i, sent_i, text, score)]} for the blocks covering this verse."""
    out = {}
    for sid, bidx in d['verses'].get(str(ayah), {}).items():
        blk = d['sets'][sid]['blocks'][bidx]
        rows = []
        for pi, para in enumerate([p for p in re.split(r'\n\s*\n', blk) if p.strip()]):
            for si, sent in enumerate(sentences(clean(para))):
                if len(sent) < 45:
                    continue
                if any(re.search(rx, sent, re.I) for rx in CUT):
                    continue
                score = 0
                for rx, w in KEEP:
                    if re.search(rx, sent, re.I):
                        score += w
                # short gloss sets are the spine of a compiled verse; long ones need selection
                if sid in ('jalalayn', 'mukhtasar', 'tanwir'):
                    score += 2
                if len(sent) > 520:
                    score -= 2
                rows.append((pi + 1, si + 1, sent, score))
        out[sid] = rows
    return out


def rank(rows, k):
    """Top-k by score, then restored to source order so the packet reads in sequence."""
    top = sorted(rows, key=lambda r: -r[3])[:k]
    return sorted(top, key=lambda r: (r[0], r[1]))


def main():
    surah = int(sys.argv[1])
    spec = sys.argv[2] if len(sys.argv) > 2 else '1-40'
    d = load(surah)
    ch = json.loads(re.search(r'\[.*\]', open(os.path.join(ROOT, f'data/chapter_{surah:03d}.js'),
                                              encoding='utf-8').read(), re.S).group(0))
    en = {v['ayah_no_surah']: v['ayah_en'] for th in ch for v in th['verses']}
    have = sorted(int(k) for k in d['verses'])
    if spec == '--all':
        want = have
    else:
        lo, _, hi = spec.partition('-')
        hi = int(hi or lo)
        want = [a for a in have if int(lo) <= a <= hi]
    cap = os.environ.get('PACKET_CAP', '')
    for ayah in want:
        vs = verse_sentences(d, ayah)
        pool = sum(len(v) for v in vs.values())
        n = sum(min(len(v), int(cap) if cap else 7) for v in vs.values())
        plan = PLAN.get(f'{surah}:{ayah}', {})
        print(f'\n=== {surah}:{ayah}  tier {plan.get("tier","-")} '
              f'target {plan.get("words","-")} floor {round((plan.get("words") or 0)*0.75) or "-"} '
              f'flags {",".join(plan.get("flags",[])) or "-"}  [{n} of {pool} sentences]')
        print('EN: ' + clean(en.get(ayah, '')))
        for sid in SETS:
            rows = vs.get(sid, [])
            picks = rank(rows, int(cap) if cap else 7)
            if not rows:
                print(f'\n-- {sid}: (no block for this verse)')
                continue
            print(f'\n-- {sid} ({SETS[sid]}) {len(rows)} available')
            for pi, si, sent, sc in picks:
                print(f'  {SETS[sid]}{ayah}.{pi}.{si} ({sc:+d}) {sent}')
    print()


if __name__ == '__main__':
    main()
