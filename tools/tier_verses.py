#!/usr/bin/env python3
"""Assign every verse a commentary tier and a word target.

Writes data/plan.json — the manifest the authoring step reads. Run from the
repo root:

    python3 tools/tier_verses.py            # write data/plan.json
    python3 tools/tier_verses.py --verify   # re-run the labelled validation set

How the tier is decided
-----------------------
Nothing here reads a human's opinion. Every signal comes from the six tafsirs
already in data/tafsir_NNN.json plus the verse text itself:

  tr_words    length of the app's own English translation
  ar_words    length of the Arabic verse
  mspec       longest *verse-specific* entry across the six sources, i.e. the
              longest block a scholar wrote about this verse alone rather than
              about a run of verses. This is the signal Ibn Kathir alone cannot
              give, because he writes in long runs.
  nspec       how many of the six sources treat this verse individually with
              60+ words — agreement across independent scholars
  sumd        sum of the six per-verse densities
  ruling      legal vocabulary in the verse text, or in substantial
              verse-specific prose
  narrative   prophet/tribe/place names in the verse text or its tafsir
  occasion    reason-for-revelation language in the verse-specific prose
  refrain     the same translation text repeats 3+ times in the surah
              (Sūrah 55's "which of your Lord's favours will you deny")

Weights were fitted by grid search against the labelled set below using 5-fold
cross-validation. Three deliberate safeguards, because a fitted score alone
misbehaves at the extremes:

  * a refrain is always Tier C
  * the score can never put a verse in C if it has 25+ translation words or
    400+ words of verse-specific tafsir
  * the score can never keep a verse in B if it has 40+ translation words or
    1,200+ words of verse-specific tafsir

Length is continuous inside each tier. The tier sets the band; the verse's own
score sets its position inside the band. This is deliberate — it means a verse
that is mis-tiered by one step still receives roughly the right length, so the
B/C boundary, which is the genuinely fuzzy one, does not produce visible
damage.
"""

import json
import glob
import os
import re
import sys
import math
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- fitted parameters (5-fold CV, 340-verse labelled set, see --verify) ---
P = dict(w_tr=2, w_ar=1, w_ms=6, w_ns=6, w_sd=4,
         b_rul=22, b_nar=26, b_occ=6, w_imp=3,
         tA=170, tC=85)

# --- word bands: tier sets the range, score sets the position inside it ---
# Word bands per tier. Raised by the maintainer on 2026-10-09 from
# A 900-1300 / B 450-700 / C 200-320, on the reasoning that the earlier bands
# were set against a pilot of ~50 verses and were too tight for the verses the
# sources actually weigh in on: 2:41-2:46 met the old floor while leaving the
# named evidences out. The 0.75 discount in verify_verse.py and style-check.js
# still applies on top, so the enforced minimums are 975 / 488 / 225.
BAND = {'A': (1300, 1900), 'B': (650, 1000), 'C': (300, 450)}

# --- thin verses are authored-only, never padded (maintainer, 2026-10-10) ---
# 168 verses hold less material than 0.75 x their own target (`avail`: every word the
# covering sets say about them, shared blocks counted in full because the compiler can
# splice them). A floor cannot be reached there by selection alone - it would take
# repeated sentences, connective padding, or invention, and the first two are exactly the
# quote-stacking that got the 2026-10-09 corpus cleared. The decision is NOT to lower the
# floor: these verses are marked `authored_only` and compile_guidance refuses them, so
# they get composed instead of spliced. Composed prose can weigh two readings, settle a
# disagreement, and explain a short source at length, which is how an entry reaches its
# floor honestly. It costs about 5-10 verses a run against 5 in a compiled batch.
# `avail` and the flag are the only new data; the floor stays 0.75 x words, and no
# floor is ever softened by a constant in this file.
LEAD_FLOOR = {'A': 240, 'B': 170, 'C': 110}   # verify_verse.py and style-check.js read plan['lead_floor']
# eight sets as of 2026-10-09; the classifier reads whatever covers the verse, so
# a selective set (al-Qushayrī 20.6%, al-Wāḥidī 6.9%) only ever adds signal
SRC = ('ibn-kathir', 'maarif', 'tazkirul', 'tanwir', 'jalalayn', 'mukhtasar',
       'qushayri', 'wahidi')

LEGAL = re.compile(r'\b(halal|haram|lawful|unlawful|forbidden|prohibited|prescribed|'
    r'obligat|divorce|inheritance|dowry|mahr|zakat|alms|fast(ing)?\b|pilgrimage|ablution|'
    r'wash|witness|testimony|contract|debt|write it down|penalty|retaliation|expiation|'
    r'punishment|cut off|flog|whip|guard your|do not approach|prohibited to you|'
    r'it is not lawful|marry|marriage|nursing|waiting period|ʿiddah|bequest)\b', re.I)
NARR = re.compile(r'\b(Pharaoh|Mūsā|Moses|ʿĪsā|Jesus|Ibrāhīm|Abraham|Yūsuf|Joseph|'
    r'Sulaymān|Solomon|Dāwūd|David|Yūnus|Jonah|Nūḥ|Noah|Lūṭ|Lot|Hārūn|Aaron|Yaʿqūb|Jacob|'
    r'Madyan|Thamūd|ʿĀd\b|Children of Israel|People of the Cave|Dhul-Qarnayn|Nimrod|'
    r'Goliath|Ṭālūt|Saul|Belqīs|Sheba|ʿUzayr|Samiri|Qārūn|Korah|Hāmān|magicians?)\b')
OCC = re.compile(r'\b(reason for (?:the )?revelation|occasion of (?:its |the )?revelation|'
    r'revealed when|revealed about|revealed concerning|revealed regarding|asbāb al-nuzūl|'
    r'this (?:verse|sūrah|surah) was revealed|came down (?:concerning|about|regarding))\b', re.I)
IMPER = re.compile(r'\b(do not|O you who believe|O Prophet|Say|establish|fear Allah|beware|'
    r'give|spend|fight|judge|enjoin|forbid|obey)\b', re.I)


def verse_count(surah):
    p = os.path.join(ROOT, f'data/chapter_{surah:03d}.js')
    c = open(p, encoding='utf-8').read()
    J = json.loads(c[c.index('['):c.rindex(']') + 1])
    return (
        {v['ayah_no_surah']: v.get('ayah_en', '') for th in J for v in th['verses']},
        {v['ayah_no_surah']: v.get('ayah_ar', '') for th in J for v in th['verses']},
    )


def scan(surah):
    """Extract every classification signal for one surah."""
    tr, ar = verse_count(surah)
    d = json.load(open(os.path.join(ROOT, f'data/tafsir_{surah:03d}.json'), encoding='utf-8'))
    n = len(d['verses'])

    # refrain: identical translation text repeated 3+ times inside the surah
    seen = collections.defaultdict(list)
    for a, t in tr.items():
        k = re.sub(r'[^a-z ]', '', t.lower()).strip()
        if len(k) > 12:
            seen[k].append(a)
    refrains = {a for v in seen.values() if len(v) >= 3 for a in v}

    out = {}
    for a in range(1, n + 1):
        m = d['verses'][str(a)]
        spec = []
        dens = []
        avail = 0.0
        for sid in SRC:
            i = m.get(sid)
            if i is None:
                # a selective edition has nothing on this verse (al-Qushayrī covers
                # 1,287 verses, al-Wāḥidī 431). Absence is not density and not
                # verse-specific material, so it must not enter either measure.
                continue
            st = d['sets'][sid]
            run = sum(1 for x in d['verses'].values() if x.get(sid) == i)
            w = len(st['blocks'][i].split())
            dens.append(w / max(1, run))
            # A long block covering several verses IS selectable for each of them - that
            # is how the compiler works - so it counts in full. The cost is that adjacent
            # verses can end up quoting the same source sentences; --dry already flags an
            # overlap between a verse's own selections, and restatements are dropped, so
            # the exposure is visible at authoring time rather than hidden in the floor.
            # (Measuring only a verse's exclusive share instead would cap 5,516 verses,
            # i.e. quietly abolish the raised bands across the whole Qur'an. Wrong tool.)
            avail += w
            if run == 1:
                spec.append((w, st['blocks'][i]))
        blob = ' '.join(t for _, t in spec)[:8000]
        txt = tr.get(a, '')
        fl = []
        if LEGAL.search(txt) or (LEGAL.search(blob) and len(blob) > 400):
            fl.append('ruling')
        if NARR.search(txt) or NARR.search(blob):
            fl.append('narrative')
        if OCC.search(blob):
            fl.append('occasion')
        out[a] = dict(
            tr_words=len(txt.split()),
            ar_words=len(ar.get(a, '').split()),
            max_specific_raw=max((w for w, _ in spec), default=0),
            avail_raw=round(avail),           # every word the covering sets say on this verse
            n_specific_substantial=sum(1 for w, _ in spec if w >= 60),
            sum_density=sum(dens),
            refrain=a in refrains,
            imp=len(IMPER.findall(txt)),
            flags=fl,
        )
    return out


def score(v):
    return (v['tr_words'] * P['w_tr'] + v['ar_words'] * P['w_ar']
            + math.log1p(v['max_specific_raw']) * P['w_ms']
            + v['n_specific_substantial'] * P['w_ns']
            + math.log1p(v['sum_density']) * P['w_sd']
            + ('ruling' in v['flags']) * P['b_rul']
            + ('narrative' in v['flags']) * P['b_nar']
            + ('occasion' in v['flags']) * P['b_occ']
            + v['imp'] * P['w_imp'])


def tier_of(v):
    if v['refrain']:
        return 'C'
    s = score(v)
    t = 'A' if s >= P['tA'] else ('C' if s < P['tC'] else 'B')
    if t == 'C' and (v['tr_words'] >= 25 or v['max_specific_raw'] >= 400):
        t = 'B'
    if t == 'B' and (v['tr_words'] >= 40 or v['max_specific_raw'] >= 1200):
        t = 'A'
    return t


def build():
    """Scan the whole corpus and return {(surah, ayah): signals}."""
    all_v = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'data/tafsir_*.json'))):
        s = int(os.path.basename(f)[7:10])
        for a, v in scan(s).items():
            all_v[(s, a)] = v
    return all_v


def targets(all_v):
    """Assign tier and word count; position inside the band follows the score."""
    scored = {k: (tier_of(v), score(v)) for k, v in all_v.items()}
    by_tier = {t: sorted(s for k, (tt, s) in scored.items() if tt == t) for t in 'ABC'}
    plan = {}
    for k, v in all_v.items():
        t, s = scored[k]
        lo, hi = BAND[t]
        band = by_tier[t]
        pos = sum(1 for x in band if x <= s) / len(band)
        words = int(round((lo + (hi - lo) * pos) / 10) * 10)
        want = round(words * 0.75)
        floor = want                      # the floor is not negotiable; the mode is
        thin = v['avail_raw'] < floor
        lead_floor = LEAD_FLOOR[t]
        plan[k] = dict(
            tier=t,
            words=words,
            avail=v['avail_raw'],
            floor=floor,
            lead_floor=lead_floor,
            authored_only=thin,
            score=round(s, 1),
            tr_words=v['tr_words'],
            ar_words=v['ar_words'],
            max_specific=v['max_specific_raw'],
            n_specific=v['n_specific_substantial'],
            flags=v['flags'],
            refrain=v['refrain'],
        )
    return plan


# --------------------------------------------------------------------------
# Labelled validation set. Tier expectations were set by reading the verses,
# not by reading the classifier's output.
# --------------------------------------------------------------------------
LABELS = {}
for x in ("2:282 2:275 2:255 2:183 2:187 2:196 2:228 2:233 2:258 2:259 2:67 2:222 4:11 4:12 "
          "4:34 4:176 4:3 5:3 5:6 5:32 5:38 5:90 7:103 9:5 12:4 12:23 12:30 17:23 18:9 18:32 "
          "18:60 24:2 24:4 24:11 24:31 24:35 26:10 33:4 33:32 33:53 47:4 48:29 58:1 60:8 65:1 "
          "3:7 16:90 2:177 2:1 1:1 2:221 8:41 49:9 59:7 62:9 66:1 25:68 6:151 17:31 4:92 2:229 "
          "2:236 2:240 5:89 5:95 5:106 24:6 24:22 33:49 33:59 65:4 2:237 2:283 3:97 4:23 4:24 "
          "5:5 5:87 7:31 16:115 24:27 33:35 49:11 58:22 60:10 65:6 2:158 2:184 2:197 2:203 3:83 "
          "4:119 5:4 5:96 6:118 7:87 8:60 9:60 16:67 17:33 22:27 23:5 24:30 24:58 24:60 25:72 "
          "28:7 31:14 34:14 42:15 44:19 48:15 49:13 57:4 63:9 65:2 76:7 4:1 4:2 5:1 5:2 8:1 "
          "9:2 10:2 13:1 14:1 6:1 2:6 2:7 3:4 1:7").split():
    LABELS[x] = 'A'
for x in ("103:1 103:2 103:3 108:1 108:2 108:3 111:1 111:2 111:3 87:1 93:1 94:1 96:1 112:3 "
          "112:4 114:1 114:6 105:1 105:2 106:1 107:1 109:1 109:6 110:1 1:3 55:13 55:16 55:18 "
          "55:21 55:23 55:25 77:15 77:19 26:8 26:67 54:17 54:22 54:32 113:1 113:2 102:1 102:2 "
          "99:1 99:2 97:1 101:1 101:2 101:3 104:1 104:2 105:3 105:4 106:2 106:3 106:4 107:2 "
          "107:3 107:7 109:2 109:3 110:2 110:3 111:4 111:5 113:3 113:4 113:5 114:2 114:3 114:4 "
          "114:5 89:1 89:2 90:1 91:1 91:2 92:1 93:2 93:3 95:1 95:2 96:2 96:3 97:2 98:1 98:2 "
          "100:1 100:2 101:4 101:5 101:6 101:7 102:3 102:4 102:5 102:6 102:7 102:8 104:3 104:4 "
          "104:5 104:6 104:7 104:8 104:9 105:5 107:4 107:5 107:6 109:4 109:5").split():
    LABELS[x] = 'C'
for x in ("1:2 1:4 1:5 1:6 112:2 55:1 55:2 55:3 2:3 2:4 2:5 2:8 3:1 3:2 3:3 4:2 6:2 7:1 7:2 "
          "8:1 9:1 10:1 11:1 11:2 12:1 12:2 15:1 16:1 17:1 18:1 21:1 22:1 23:1 24:1 25:1 27:1 "
          "28:1 29:1 33:1 34:1 35:1 37:1 38:1 39:1 40:1 41:1 43:1 45:1 47:1 49:1 50:1 51:1 "
          "52:1 53:1 54:1 56:1 57:1 59:1 60:1 61:1 62:1 63:1 64:1 67:1 68:1 69:1 70:1 71:1 "
          "72:1 73:1 74:1 75:1 76:1 78:1 79:1 80:1 81:1 82:1 83:1 84:1 85:1 86:1 88:1 89:3 "
          "90:2 92:2 94:5 94:6 94:7 94:8 96:4 96:5 99:7 99:8 98:6 98:7 99:3 99:4 99:5 99:6 "
          "100:6 100:7 100:8 100:9 100:10 100:11").split():
    LABELS[x] = 'B'


def verify(all_v):
    """Score the classifier against the labelled set. Excludes the muqatta'at,
    which are 1-2 letter sequences where B vs C is arbitrary by nature."""
    muq = {k for k, v in all_v.items()
           if v['tr_words'] <= 2 and v['ar_words'] <= 2 and k[1] == 1}
    lab = {}
    for s, e in LABELS.items():
        k = tuple(map(int, s.split(':')))
        if k in all_v and k not in muq:
            lab[k] = e
    cm = collections.Counter()
    for k, e in lab.items():
        cm[(e, tier_of(all_v[k]))] += 1
    n = len(lab)
    ok = sum(cm[(x, x)] for x in 'ABC')
    sev = cm[('A', 'C')] + cm[('C', 'A')]
    print(f"labelled verses scored: {n}  (muqatta'at excluded: {len(muq & set(lab))} ambiguous)")
    print(f"exact agreement: {ok}/{n} = {100 * ok / n:.1f}%")
    print(f"severe misses (A judged C, or C judged A): {sev} = {100 * sev / n:.1f}%\n")
    print("             gotA    gotB    gotC")
    for w in 'ABC':
        t = sum(cm[(w, x)] for x in 'ABC')
        print(f"  want {w}    {cm[(w,'A')]:5d}   {cm[(w,'B')]:5d}   {cm[(w,'C')]:5d}    ({100*cm[(w,w)]/t:.0f}%)")
    misses = [(k, e, tier_of(all_v[k])) for k, e in sorted(lab.items()) if tier_of(all_v[k]) != e]
    print(f"\n{len(misses)} disagreements:")
    for (s, a), e, g in misses:
        v = all_v[(s, a)]
        print(f"  {s}:{a:<4d} want {e} got {g}   tr={v['tr_words']:3d}w ar={v['ar_words']:3d}w "
              f"mspec={v['max_specific_raw']:5d} nspec={v['n_specific_substantial']} {v['flags']}")
    return ok / n, sev / n


if __name__ == '__main__':
    all_v = build()
    if '--verify' in sys.argv:
        acc, sev = verify(all_v)
        sys.exit(0 if (acc > 0.70 and sev < 0.03) else 1)
    plan = targets(all_v)
    out = {f"{k[0]}:{k[1]}": v for k, v in sorted(plan.items())}
    path = os.path.join(ROOT, 'data/plan.json')
    # Minified on purpose. Pretty-printed this manifest is 1.29 MB, which is
    # over GitHub's 1 MB inline-display limit and so renders as "too large to
    # show" — worse than one long line. This file is generated output of this
    # script and is reproducible; the reviewable artefacts are the guidance
    # files. Marked -diff linguist-generated in .gitattributes.
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False,
              separators=(',', ':'))
    c = collections.Counter(v['tier'] for v in plan.values())
    tot = sum(v['words'] for v in plan.values())
    print(f"wrote {path}")
    for t in 'ABC':
        ws = [v['words'] for v in plan.values() if v['tier'] == t]
        print(f"  Tier {t}: {c[t]:5d} verses ({100*c[t]/len(plan):4.1f}%)  "
              f"{min(ws)}-{max(ws)} words  = {sum(ws):9,} words")
    print(f"  TOTAL {len(plan)} verses  {tot:,} words  ({os.path.getsize(path):,} bytes)")
    nc = sum(1 for v in plan.values() if v['authored_only'])
    short = sum(v['words'] - v['floor'] for v in plan.values() if v['authored_only'])
    print(f"  authored-only (material below their own floor): {nc} verses, "
          f"{short:,} words of target above their floor - splicing them is refused")
