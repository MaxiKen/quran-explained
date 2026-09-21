import re, pathlib, json, sys
CORPUS=pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
def sect(ch,y):
    for s in re.split(r"\n(?=## )", (CORPUS/f"{ch:03d}.md").read_text(encoding="utf-8")):
        if re.match(rf"## Verse {ch}:{y}\s*$", s.split("\n")[0].strip()): return s
    raise SystemExit(f"not found {ch}:{y}")
def body_ps(s):
    b=s.split("\n",1)[1].strip("\n")
    if b.rstrip().endswith("---"): b=b.rstrip()[:-3].rstrip("\n")
    return [p for p in re.split(r"\n\s*\n", b) if p.strip()]
def build(spec_path, out_path):
    spec=json.load(open(spec_path,encoding="utf-8"))
    R={}
    for item in spec:
        ch,y=item["verse"]; idx=item.get("idx",-1); new=item["text"]
        ps=body_ps(sect(ch,y))
        if item.get("whole"):
            newps=[new]
        elif idx==-1:
            newps=ps[:-1]+[new]
        else:
            newps=ps[:idx]+[new]+ps[idx+1:]
        R.setdefault(str(ch),{})[str(y)]="\n\n".join(newps)
    json.dump(R, open(out_path,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", out_path, "sections:", sum(len(v) for v in R.values()))
if __name__=="__main__": build(sys.argv[1], sys.argv[2])
