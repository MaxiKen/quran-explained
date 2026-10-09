# -*- coding: utf-8 -*-
"""Restore verses that were trimmed down to fit a band.

The rule is a FLOOR, not a band: a verse may run long, it must not run short.
Each authoring script defines a V dict of the verses it wrote. We exec the
script with file writes suppressed and read V, so we only ever take a verse
from the script that actually authored it.
"""
import io, json, os, sys

ROOT = '/home/user/quran-explained'
GUID = os.path.join(ROOT, 'data/guidance_002.json')
PLAN = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))

TRIMMED = {18: '/tmp/g002d.py', 31: '/tmp/g002g.py', 45: '/tmp/g002j.py'}

real_open = open


def patched_open(f, mode='r', *a, **k):
    if isinstance(mode, str) and 'w' in mode:
        return io.StringIO()
    return real_open(f, mode, *a, **k)


originals = {}
for a, script in TRIMMED.items():
    src = real_open(script, encoding='utf-8').read()
    g = {'__name__': '__main__', 'open': patched_open, 'json': json, 'os': os,
         'unicodedata': __import__('unicodedata')}
    exec(compile(src, script, 'exec'), g)
    V = g.get('V')
    if not V or a not in V:
        sys.exit(f'  !! {script} does not define verse 2:{a}')
    draws, text = V[a]
    if isinstance(draws, tuple):
        draws, text = draws
    text = '\n'.join(ln.rstrip() for ln in text.strip('\n').split('\n'))
    originals[a] = {'range': f'2:{a}', 'draws_on': list(draws), 'text': text}
    print(f'  recovered 2:{a} original from {os.path.basename(script)}: '
          f'{len(text.split())}w')

doc = json.load(real_open(GUID, encoding='utf-8'))
print()
for a in sorted(originals):
    old = len(doc['verses'][str(a)]['text'].split())
    new = len(originals[a]['text'].split())
    tgt = PLAN[f'2:{a}']['words']
    bad = [c for c in originals[a]['text'] if 0x0400 <= ord(c) <= 0x04FF]
    assert not bad, f'2:{a} Cyrillic homoglyphs: {bad}'
    doc['verses'][str(a)] = originals[a]
    floor = tgt * 0.75
    status = 'RESTORED' if new > old else ('unchanged' if new == old else 'REGRESSED')
    print(f'  2:{a}  Tier {PLAN[f"2:{a}"]["tier"]}  target {tgt}  floor {floor:.0f}'
          f'  |  {old}w -> {new}w  {status}  floor met: {new >= floor}')

with real_open(GUID, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
    fh.write('\n')

print()
short = [f'2:{a} ({len(v["text"].split())}w vs floor '
         f'{PLAN[f"2:{a}"]["words"]*0.75:.0f})'
         for a, v in sorted(doc['verses'].items(), key=lambda x: int(x[0]))
         if len(v['text'].split()) < PLAN[f'2:{a}']['words'] * 0.75]
print(f'  verses under their floor: {short or "none"}')
print(f'  file: {len(doc["verses"])} verses, '
      f'{sum(len(v["text"].split()) for v in doc["verses"].values()):,} words, '
      f'{os.path.getsize(GUID):,} bytes')
