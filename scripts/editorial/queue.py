import re, pathlib, sys
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REF = re.compile(r"\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)")
BARE = re.compile(r"\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)")
OWN = re.compile(r"\((?:states?|gives?|records?|describes?|names?|asks?|promises?|commands?|orders?|permits?|warns?|calls?|holds?|tells?|shows?|begins?|adds?|follows?|lists?|marks?|opens?|refuses?|forbids?|carries?|confirms?|ends?|means?|makes?|describes?|gives?|states?)\b")

def body_of(section):
    lines=section.split("\n"); out=[]; started=False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip()=="---": continue
            started=True
        out.append(l)
    t="\n".join(out).rstrip()
    return t[:-3].rstrip() if t.endswith("---") else t

rows=[]
for ch in range(1,115):
    t=(CORPUS/f"{ch:03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", t):
        m=re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m: continue
        ps=[p for p in re.split(r"\n\s*\n", body_of(s)) if p.strip()]
        worst=max((len(REF.findall(p)) for p in ps), default=0)
        if worst<6: continue
        tot=sum(len(REF.findall(p)) for p in ps)
        bare=sum(1 for p in ps for _ in BARE.findall(p)) - sum(1 for p in ps for _ in OWN.findall(p))
        bare=max(bare,0)
        verb_share = 1 - (bare/tot if tot else 0)
        rows.append((worst, verb_share, f"{ch}:{m.group(2)}", tot, len(ps)))
hi=[r for r in rows if r[0]>=8]; mid=[r for r in rows if 6<=r[0]<8]
print("8+:", len(hi), "| 6-7:", len(mid), "| total:", len(rows))
for label, ss in (("8+", hi), ("6-7", mid)):
    read=[r for r in ss if r[1]>=0.7]; stiff=[r for r in ss if r[1]<0.7]
    print(f"{label}: already plain-prose paragraphs (only need splitting): {len(read)} | still old-style bare citations (need rewriting): {len(stiff)}")
print("READ-ONLY-SPLIT heads 8+:", [(r[2],r[0]) for r in sorted([r for r in hi if r[1]>=0.7], reverse=True)[:12]])
print("REWRITE heads 8+:", [(r[2],r[0]) for r in sorted([r for r in hi if r[1]<0.7], reverse=True)[:12]])
