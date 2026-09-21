import re, sys, pathlib
CORPUS=pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REF=re.compile(r"\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)")
def body_of(section):
    lines=section.split("\n"); out=[]; started=False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip()=="---": continue
            started=True
        out.append(l)
    t="\n".join(out).rstrip()
    return t[:-3].rstrip() if t.endswith("---") else t
thr=int(sys.argv[1])
for name in sys.argv[2:]:
    ch,y=[int(x) for x in name.split(":")]
    t=(CORPUS/f"{ch:03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", t):
        m=re.match(rf"## Verse {ch}:{y}\s*$", s.split("\n")[0].strip())
        if not m: continue
        ps=[p for p in re.split(r"\n\s*\n", body_of(s)) if p.strip()]
        tot=sum(len(REF.findall(p)) for p in ps)
        print(f"##### {name} | paras {len(ps)} | words {sum(len(p.split()) for p in ps)} | refs {tot}")
        for i,p in enumerate(ps):
            n=len(REF.findall(p))
            if n>=thr:
                print(f"--- idx {i} refs {n} ---")
                print(p)
        break
