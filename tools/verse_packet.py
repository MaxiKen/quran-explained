#!/usr/bin/env python3
"""Number the source sentences of a verse range, so an editor can cite them.

    python3 tools/verse_packet.py 2 41-46 [--all] [--min 4]

Prints, per verse: the app translation, the plan tier/floor/flags, and a
ranked shortlist of sentences drawn from ALL EIGHT sets (six since the corpus
landed; al-Qushayrī and al-Wāḥidī added 2026-10-09 — they cover 1,287 and 431
verses, so a Meccan short sūrah may show none of them, which is not an error). Each sentence carries
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
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))

# one letter per set, and it appears in every ref in every spec — adding or
# reordering a set here shifts every existing spec, so append only
SETS = {'jalalayn': 'J', 'maarif': 'M', 'ibn-kathir': 'K',
        'tazkirul': 'T', 'tanwir': 'D', 'mukhtasar': 'X',
        'qushayri': 'Q', 'wahidi': 'W'}
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
    # added with the two new sets (2026-10-09): al-Wāḥidī answers "why then", al-Qushayrī "besides"
    (r'\b(it was revealed|revealed about|when (they|the people|the Muslims|he) (said|asked|came)'
     r'|the reason for that|this is because)', 3),
    (r'\b(in terms of allusion|the allusion|it is said to mean|a second (meaning|sense)'
     r'|another reading of it)', 2),
    (r'\b(however|but |on the other hand|they differed|a second opinion)', 2),
]
CUT = [
    r'^\s*$',
    r'\[ar\]',
    r'see (the )?(Note|introduction|Appendix)',
    r'^\(\d+\)\s*$',
    r'narrated to us .* from .* from',
    r'\bit was reported on the authority of',
    # isnād lead-ins: an Asbāb entry whose "sentence" only introduces a chain
    # carries no meaning on its own and must never be spliced
    r'^\s*(?:said|narrated|reported|he said)\b[^.?!]{0,90}:\s*$',
    r'^\s*(He said|They said|I heard)\b.{0,25}$',
    r'\bhappy is the one|wretched is the one\b.*^\s*$',
    r'^\s*[\u2018"].{0,20}[\u2019"]\s*:?\s*$',
    r'\s:\s.*\s:\s',                      # stripped-Arabic debris, e.g. ": : : :"
    r'[\u00ab\u00bb]',
    r'>\s*[A-Z][a-z]{2,}',                 # isnad arrows left in a chain: 'authority>Abu X'
    r'^[^A-Za-z]{0,6}[A-Za-z]{1,4}\):',      # a fragment cut out of a bracketed gloss                     # guillemets around untranslated Arabic
    r'^\s*\d+[:.\u2013-]\d+\s*$',
    # an Asbāb entry opens by quoting the verse it explains; that sentence is the
    # translation the reader has already been shown, so it is never a pick
    r'^\s*\(.*\)\s*\[\d{1,3}:\d{1,4}(-\d{1,4})?\]\s*\.?\s*$',
    r'[\u00c0-\u00d6\u00d8-\u00de]',   # mojibake in some sets (Qur\u00ccn, \u1e63l\u02bfm): drop, don't quote
]


def clean(s):
    s = AR.sub('', s)
    s = re.sub(r'\[\s*ar\s*\]', '', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def sentences(para):
    """Split on . ! ? : followed by a capital — but only outside brackets, so a
    parenthetical gloss like "(Alif. Mim)" is not cut in half, and abbreviations
    keep their dots. Depth-aware because the tafsir texts nest translators'
    brackets heavily."""
    para = re.sub(r'\b(pp?|no|vs|ie|eg|v|ch)\.', r'\1<DOT>', para)
    out, buf, depth = [], '', 0
    i = 0
    while i < len(para):
        c = para[i]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            depth = max(0, depth - 1)
        buf += c
        if (depth == 0 and c in '..!?:\u2026'
                and re.match(r'[.!?:\u2026]["\u2019\u201d)\]]*[ \t]+[A-Z\u2018"(\u0600]', para[i:])
                ):
            out.append(buf.strip())
            buf = ''
        i += 1
    out.append(buf)
    return [p.replace('<DOT>', '.').strip() for p in out if p.strip()]


def load(surah):
    return json.load(open(os.path.join(ROOT, f'data/tafsir_{surah:03d}.json'), encoding='utf-8'))


def verse_sentences(d, ayah, hot=frozenset()):
    """{set: [(para_i, sent_i, text, score)]} for the blocks covering this verse.
    `hot` is the vocabulary of the verse's own translation: a long block that spans
    several verses is full of sentences that score well on definition markers but are
    answering a neighbour, so relevance to this verse's wording is what actually
    anchors a pick (see the shared K1/M1 blocks, which cover a whole chapter)."""
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
                # the two added sets are verse-specific but not terse; they earn a
                # smaller bonus so they surface without burying the gloss sets
                if sid in ('qushayri', 'wahidi'):
                    score += 1
                hits = sum(1 for w in re.findall(r"[A-Za-z]{4,}", sent) if canon(w) in hot)
                score += min(6, 2 * hits)
                score -= 3 if not hits and len(rows) > 12 else 0
                if len(sent) > 520:
                    score -= 2
                if len(sent) > 900:      # a monster paragraph is not a spliceable sentence
                    continue
                rows.append((pi + 1, si + 1, sent, score))
        out[sid] = rows
    return out


def canon(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s.lower())


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
    enwords = {a: frozenset(canon(w) for w in re.findall(r"[A-Za-z]{4,}", en.get(a, ''))) for a in want}
    for ayah in want:
        vs = verse_sentences(d, ayah, enwords.get(ayah, frozenset()))
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
            trunc = int(os.environ.get('PACKET_TRUNC', '0') or 0)
            for pi, si, sent, sc in picks:
                shown = (sent[:trunc].rsplit(' ', 1)[0] + ' \u2026') if trunc and len(sent) > trunc else sent
                print(f'  {SETS[sid]}{ayah}.{pi}.{si} ({sc:+d},{len(sent)}) {shown}')
    print()


if __name__ == '__main__':
    main()
