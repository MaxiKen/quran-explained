import re, sys, json, pathlib
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REF = re.compile(r"\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)")

def body_of(section):
    lines=section.split("\n"); out=[]; started=False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip()=="---": continue
            started=True
        out.append(l)
    t="\n".join(out).rstrip()
    return t[:-3].rstrip() if t.endswith("---") else t

def in_quote(t, pos):
    return t[:pos].count("“") - t[:pos].count("”") > 0

def split_para(p, maxrefs=5):
    if len(REF.findall(p)) <= maxrefs: return [p]
    sents=[]; start=0
    cands=[m.start() for m in re.finditer(r"(?<=[.!?])\s+(?=[A-Z*\"'“])", p)]
    cands=[i for i in cands if not in_quote(p, i)]
    for i in cands:
        seg=p[start:i]
        if seg.strip(): sents.append(seg)
        start=i
        while start < len(p) and p[start] in " \n\t": start+=1
    sents.append(p[start:])
    chunks=[]; cur=[]; refs=0
    for s in sents:
        n=len(REF.findall(s))
        if cur and refs+n > maxrefs:
            chunks.append(" ".join(x.strip() for x in cur)); cur=[s]; refs=n
        else:
            cur.append(s); refs+=n
    if cur: chunks.append(" ".join(x.strip() for x in cur))
    return chunks

target = sys.argv[1] if len(sys.argv)>1 else "/home/user/.work/bulksplit.json"
thr = int(sys.argv[2]) if len(sys.argv)>2 else 6
cap = int(sys.argv[3]) if len(sys.argv)>3 else 5
data={}; touched=0; after=0
for ch in range(1,115):
    txt=(CORPUS/f"{ch:03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", txt):
        m=re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m: continue
        ps=[p for p in re.split(r"\n\s*\n", body_of(s)) if p.strip()]
        if max((len(REF.findall(p)) for p in ps), default=0) < thr: continue
        out=[]
        for p in ps: out.extend(split_para(p, cap))
        if len(out) != len(ps):
            data.setdefault(str(ch), {})[m.group(2)]="\n\n".join(out)
            touched+=1
            if max((len(REF.findall(p)) for p in out), default=0) < thr: after+=1
pathlib.Path(target).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"split {touched} sections | {after} of them leave the queue entirely | wrote {target}")
