#!/usr/bin/env python3
"""Sample bare citations and print the quote the picker chose, for eyeballing."""
import random
import re
import sys
import statistics
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from verse_quotes import REF, ALREADY_QUOTED, CORPUS, load_translation, pick_quote, clean_quote

tr = load_translation()
sites = []
for ch in range(1, 115):
    t = (CORPUS / f"{ch:03d}.md").read_text(encoding="utf-8")
    for m in REF.finditer(t):
        pre = t[max(0, m.start() - 320):m.start()]
        if ALREADY_QUOTED.search(pre):
            continue
        s, a = int(m.group(1)), int(m.group(2))
        b = int(m.group(4)) if m.group(4) else None
        if s not in tr or a not in tr[s]:
            continue
        ctx = re.sub(r"\s+", " ", pre)[-240:]
        para = t[:m.start()].split("\n\n")[-1]
        wide = re.sub(r"\s+", " ", para)[-1400:]
        q, sc, fa, ta = pick_quote(tr, s, a, b, ctx, wide)
        sites.append((sc, f"{s}:{a}" + (f"-{b}" if b else ""), ctx, clean_quote(q or ""), fa, ta))

scores = [x[0] for x in sites]
print(f"sites={len(sites)} median={statistics.median(scores):.2f} "
      f"zero={sum(1 for x in scores if x == 0)} below.45={sum(1 for x in scores if x < 0.45)} "
      f"quote_len_median={statistics.median(len(x[3]) for x in sites):.0f}")

random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
band = sys.argv[2] if len(sys.argv) > 2 else "rand"
pool = sites if band == "rand" else [x for x in sites if x[0] < 0.45]
for sc, ref, ctx, q, fa, ta in random.sample(pool, min(25, len(pool))):
    tag = "" if fa == ta else f"  [chosen {fa}-{ta} of {ref}]"
    print(f"\n[{sc:.2f}] ({ref}){tag}\n  ctx: …{ctx[-150:]}\n  → “{q}”")
