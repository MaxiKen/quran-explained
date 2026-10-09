#!/usr/bin/env python3
"""Compile authored guidance from source refs — the fast, no-invention path.

    python3 tools/compile_guidance.py 2 /home/user/proto/batch.md [--dry]
    python3 tools/compile_guidance.py 2 --check-only

Spec format (one block per verse):

    ### 2:43
    > Establish prayer, pay alms-tax, and bow down with those who bow down
    ~ The demand is concrete after three verses of belief.
    ## Why the bowing is named
    - J43.1.1
    - M43.19.2
    ~ The alms-tax comes next.
    - M43.14.5

`- REF`  a sentence spliced verbatim from data/tafsir_NNN.json (SET:para:sent,
         refs as printed by tools/verse_packet.py). Nothing else may paraphrase.
`~ text` a connective, written here. It is checked, not trusted: every content
         word must already occur in this verse's own selected source text or in
         the app's translation, and no attribution or ruling verb is allowed —
         so a connective can arrange but cannot assert.
`> text` a quote of the app's own translation; needs 5+ consecutive words.
`## text` section heading, under the same word-provenance rule.

The gate for each verse: every spliced sentence must be a canon-folded
substring of that verse's OWN source blocks (after the same normalizer is
applied to both sides), the connective vocabulary must be traceable, the
verse must draw on the number of sets the gate asks for at its tier, and the
length must reach the plan floor (75% of target) —
compiled verses are shorter by construction, since they are selections.
This is deliberately a different, looser length bar than authored prose gets;
data/plan.json stays the contract for authored text (see docs/voice.md).
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import verify_verse as VV  # noqa: E402  (the gate, not a copy of its rules)
from verse_packet import verse_sentences, clean, SETS  # noqa: E402
from verify_verse import canon, blob, chapter, en_run  # noqa: E402

LETTER = {v: k for k, v in SETS.items()}
# be-forms, arrangement verbs, structure words: what a connective may say
FUNC = set("""a an the and or but nor if then so as at by of in on to from with without
this that these those it its is are was were be been being has have had not no more most
other others same both either neither first second third fourth fifth opening closing end
ends begins line word words clause sentence sentences verse verses passage text here there
where when while which who whom what how why all any each every one two three four five six
seven eight nine ten eleven twelve also even just only very much many little few against
between among before after above below over under up down out off again once now new old
whole rest part parts order next last following preceding gives give take takes read reads
runs goes come comes follows follow sits lies falls turns stays remains matters belongs
means refer refers toward towards without within their they them he they my our you your""".split())
GLOSS = set("""opens open closes close begins ends emphasises stresses marks frames reads runs carries
follows turns returns points draws takes gives holds keeps sets puts lies sits falls stands makes take puts
single double middle first last following preceding next later earlier above below within without across
belief faith acts act deed deed posture gesture movement word wording phrase clause line lines passage
reading reciting recitation mixing mixing hiding concealment covering order sequence shape form sense
meaning meanings naming named mentioning naming argument arguing case point matter issue business
practice practising preacher preaching teaching learning knowledge understanding mind heart soul
world worldly here below above thereupon thereby therefore however moreover instead rather quite
rather fairly simply only just even also still yet already never always often sometimes
""".split())


def _stems(c):
    out = {c}
    for suf in ('ing', 'ings', 'ed', 'es', 's', 'tion', 'ly', 'ment', 'al', 'ity', 'ion', 'ed', 'er', 'ers'):
        if c.endswith(suf) and len(c) - len(suf) >= 4:
            out.add(c[:-len(suf)])
            out.add(c[:-len(suf)] + 'e')
    return out


BANNED = set("""says said reports reported relates related narrated mentions argues holds
ruled judged permits permitted allows allowed forbids forbade prohibits requires obligates
recommends dislikes declares deems concludes reasons notes adds transmits cites quotes
authentic sahih weak fatwa consensus majority hanafi hanafi shafi maliki ahmad abu imam
qadi sheikh mufti according""".split())
# house transliteration, applied to the spliced text AND to the blob the proof runs
# against, so "is this the source's own sentence?" still matches exactly
HOUSE = [(r'\bMadinah\b', 'Mad\u012bnah'), (r'\bMecca\b', 'Makkah'),
         (r'\bJerusalem\b', 'Bayt al-Maqdis')]
NORMAL = HOUSE + [(r'\s*\(\s*\)', ''), (r'\)\s*\)', ')'), (r'\s+\)', ')'),
          (r'\([^)]{0,3}\)', ''), (r'`', ''), (r'\(\d+\)\s*$', ''), (r'\((?:s|pbuh|PBUH|a\.?s\.?|ra\.?a\.?|r\.?a\.?)\)', 'ﷺ'),
          (r'\(peace be upon him\)', 'ﷺ'), (r'\(may Allah be pleased with (?:him|her)\)', '(ra)'),
          (r'\s+', ' ')]


def norm(s):
    for rx, rep in NORMAL:
        s = re.sub(rx, rep, s)
    return s.strip()


def _overlap(a, b):
    """Morphology is not a claim: argued/argue, holding/hold. Short words are."""
    n = min(len(a), len(b))
    return n <= 4 or a == b or (n >= 5 and (a.startswith(b) or b.startswith(a)))


def prov_ok(sent, allowed_src):
    """Every content word of my connective must exist in the sources I selected."""
    bad = []
    for w in re.findall(r"[A-Za-z][A-Za-zʿ’']{2,}", sent):
        lw = canon(w)
        if lw in FUNC or lw in GLOSS:
            continue
        if not any(_overlap(c, a) for c in _stems(lw) for a in allowed_src):
            bad.append(w)
    for w in re.findall(r"[A-Za-z]+", sent):
        if w.lower() in BANNED:
            bad.append('BANNED:' + w)
    return bad


def parse(spec):
    verses, cur = [], None
    for raw in spec.splitlines():
        ln = raw.rstrip()
        if ln.startswith('### '):
            s, _, a = ln[4:].strip().partition(':')
            cur = dict(surah=int(s), ayah=int(a), quote='', pre=[], secs=[])
            verses.append(cur)
        elif cur is None:
            continue
        elif ln.startswith('> '):
            cur['quote'] = ln[2:].strip()
        elif ln.startswith('## '):
            cur['secs'].append(dict(head=ln[3:].strip(), items=[]))
        elif ln.startswith('- '):
            item = ('ref', ln[2:].strip())
            (cur['secs'][-1]['items'] if cur['secs'] else cur['pre']).append(item)
        elif ln.startswith('+auto '):
            cur['auto'] = int(ln.split()[1])
        elif ln.startswith('~ '):
            item = ('own', ln[2:].strip())
            (cur['secs'][-1]['items'] if cur['secs'] else cur['pre']).append(item)
    return verses


def resolve(ref, rows):
    m = re.match(r'([JMKTDX])(\d+)\.(\d+)\.(\d+)$', ref)
    if not m:
        return None, f'bad ref "{ref}"'
    sid = LETTER[m.group(1)]
    for pi, si, sent, _ in rows.get(sid, []):
        if (pi, si) == (int(m.group(3)), int(m.group(4))):
            return sent, None
    return None, f'ref {ref} not in this verse\'s {sid} sentences'


def compile_verses(surah, spec, write=True, title=None):
    d = json.load(open(os.path.join(ROOT, f'data/tafsir_{surah:03d}.json'), encoding='utf-8'))
    plan = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))
    en = chapter(surah)
    out = {'surah': surah, 'lang': 'en', 'dir': 'ltr',
           'title': title or {1: 'Al-F\u0101ti\u1e25ah', 2: 'Al-Baqarah'}.get(surah, ''), 'verses': {}}
    gp = os.path.join(ROOT, f'data/guidance_{surah:03d}.json')
    if os.path.exists(gp):
        out = json.load(open(gp, encoding='utf-8'))
    out.setdefault('verses', {})
    fails = 0
    for v in parse(spec):
        a = v['ayah']
        errs, notes = [], []
        en_hot = frozenset(canon(w) for w in re.findall(r"[A-Za-z]{4,}", en[a]['ayah_en']))
        rows = verse_sentences(d, a, en_hot)
        bb = canon(norm(blob(d, a)))
        allowed = set(canon(w) for w in re.findall(r"[A-Za-zʿ']{2,}", en[a]['ayah_en']))
        picked, used, sel_texts = [], set(), []
        allowed |= set(canon(w) for w in re.findall(r"[A-Za-zʿ']{2,}", norm(blob(d, a))))
        blocks = [(None, v['pre'])]
        tr = set(canon(w) for w in re.findall(r"[A-Za-z]{4,}", en[a]['ayah_en']))
        dropped = 0
        for blk in [v['pre']] + [x['items'] for x in v['secs']]:
            keep = []
            for kind, val in blk:
                if kind == 'ref':
                    sent = resolve(val, rows)[0] or ''
                    ws = [canon(w) for w in re.findall(r"[A-Za-z]{4,}", sent)]
                    if ws and len(ws) < 22 and tr and len(set(ws) & tr) / len(set(ws)) > 0.5:
                        dropped += 1        # the translation, not commentary: the > line already says it
                        continue
                keep.append((kind, val))
            blk[:] = keep
        if dropped:
            notes_pre = [f'dropped {dropped} selected sentence(s) that only repeat the app translation']
        else:
            notes_pre = []
        used_refs = {val for _k, items in ([('', v['pre'])] + [(x['head'], x['items']) for x in v['secs']])
                     for kind, val in items if kind == 'ref'}
        for s in v['secs']:
            blocks.append((s['head'], s['items']))
        paras, text = [], []
        for head, items in blocks:
            buf = []
            for kind, val in items:
                if kind == 'ref':
                    sent, err = resolve(val, rows)
                    if err:
                        errs.append(err)
                        continue
                    if sent.strip()[:1] in ')].,:' or '>' in sent or len(sent.split()) < 3:
                        errs.append(f'{val} is a fragment, not a sentence — the segmentation '
                                    'shifted, re-read the packet')
                        continue
                    if canon(norm(sent)) not in bb:
                        errs.append(f'{val} not found in {surah}:{a}\'s own source blocks')
                        continue
                    used.add([k for k, L in SETS.items() if val.startswith(L)][0])
                    for w in re.findall(r"[A-Za-zʿ']{2,}", sent):
                        allowed.add(canon(w))
                    sent = norm(sent)
                    if not re.search(r'[.!?:\u2019\"\)]$', sent):
                        sent += '.'          # the gloss sets run on without terminal punctuation
                    buf.append(sent); sel_texts.append(sent)
                else:
                    # The opening paragraph is allowed to run long: the house rule is
                    # that it EXPLAINS the verse, which a 26-word join cannot do. Inside
                    # a section a connective is still only a join.
                    cap = 150 if head is None else 26
                    if len(val.split()) > cap:
                        errs.append(f'connective over the {cap}w budget for its position: '
                                    + val[:40])
                    bad = prov_ok(val, allowed)
                    if bad:
                        errs.append(f'connective not traceable to the sources: {bad[:6]}')
                        continue
                    buf.append(val.strip())
            body = ' '.join(buf).strip()
            if head:
                bad = prov_ok(head, allowed)
                if bad:
                    errs.append(f'heading not traceable: {head!r} {bad[:4]}')
                text.append('**%s**' % (head if head.endswith('.') else head + '.'))
            if body:
                text.append(body)
        if v.get('auto') is not None:
            # fill from the ranked shortlist, in source order, skipping what was picked
            extra = []
            for sid in SETS:
                cand = verse_sentences(d, a, en_hot)[sid]
                ranked = sorted(sorted(cand, key=lambda r: -r[3])[:v['auto'] * 3],
                                key=lambda r: (r[0], r[1]))
                for pi, si, sent, _sc in ranked:
                    if f'{SETS[sid]}{a}.{pi}.{si}' not in used_refs:
                        extra.append((pi, si, sid, sent))
            n = len(' '.join(text).split())
            floor = int(round((plan.get(f'{surah}:{a}', {}).get('words', 800)) * 0.75))
            chosen, seen_pairs = [], []
            for pi, si, sid, sent in sorted(extra, key=lambda x: -0)[:len(extra)]:
                if n >= floor:
                    break
                key = canon(norm(sent))
                if key not in bb or any(key == x or x in key or key in x for x in seen_pairs):
                    continue
                seen_pairs.append(key)
                chosen.append((pi, si, sent))
                n += len(sent.split())
            if chosen:
                text.append('**What else the same passage holds.**')
                text.append(' '.join(norm(x[2]) for x in sorted(chosen, key=lambda x: (x[0], x[1]))))
        # re-check: allowed grows as refs resolve, so validate connectives last
        if v['quote']:
            paras0 = [t for t in text if t]
            first = paras0[0] if paras0 else ''
            # open on the app's own wording, as the house style requires
            lead = f'*{v["quote"]}*'
            if paras0 and not paras0[0].startswith('**'):
                paras0[0] = lead + ' — ' + paras0[0] if not paras0[0].startswith('The ') else lead + '. ' + paras0[0]
            else:
                paras0.insert(0, lead)
            text = paras0
        paras = [t for t in text if t]
        body_text = '\n\n'.join(paras)
        n = len(body_text.split())
        body_text = body_text.replace('  ', ' ')
        if not v['quote']:
            errs.append('no > quote of the app translation')
        # the set-count rule lives in verify_verse.check() alone, which is called
        # below — a second copy here is how the two drifted apart once already
        # Layout, tier floor, and the opening-paragraph rule come from the same
        # checker the authored verses are gated by, so the two modes cannot drift
        # apart: one rule, one place. It reports its own messages as errors here.
        key = f'{surah}:{a}'
        _n, _run, gerrs, gnotes = VV.check(surah, a, body_text, sorted(used), [])
        errs.extend('from the house gate: ' + e for e in gerrs)
        notes.extend(gnotes)
        dupes = 0
        for i, t1 in enumerate(sel_texts):
            for t2 in sel_texts[i + 1:]:
                w1 = set(canon(w) for w in re.findall(r"[A-Za-z]{5,}", t1))
                w2 = set(canon(w) for w in re.findall(r"[A-Za-z]{5,}", t2))
                if len(t1) > 170 and len(t2) > 170 and w1 and w2 \
                        and len(w1 & w2) / min(len(w1), len(w2)) > 0.45:
                    dupes += 1
        notes.extend(notes_pre)
        if dupes:
            notes.append(f'{dupes} selected sentence pair(s) overlap heavily — drop one')
        status = 'FAIL' if errs else 'ok  '
        fails += bool(errs)
        print(f'  {status} {key}  {n:4d}w  sets={len(used)}  sentences={len(picked) or sum(1 for p in paras)}')
        for e in errs:
            print(f'       — {e}')
        if notes:
            for nt in notes:
                print(f'       note {nt}')
        if not errs and write:
            out['verses'][str(a)] = dict(range=key, draws_on=sorted(used), text=body_text)
    if write:
        out['verses'] = {k: out['verses'][k] for k in sorted(out['verses'], key=int)}
        with open(gp, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print(f'\nwrote {gp} — {len(out["verses"])} verses, {os.path.getsize(gp):,} bytes')
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    args = sys.argv[2:]
    title = None
    if '--title' in args:
        i = args.index('--title')
        title = args[i + 1]
        del args[i:i + 2]
    txt = open(args[0], encoding='utf-8').read()
    sys.exit(compile_verses(int(sys.argv[1]), txt, write='--dry' not in args, title=title))
