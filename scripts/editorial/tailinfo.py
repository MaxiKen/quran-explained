import re, pathlib, sys
CORPUS=pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
RE=re.compile(r"\((\d+:\d+)[^)]*\)")
def body(s):
    b=s.split("\n",1)[1].strip("\n")
    if b.rstrip().endswith("---"): b=b.rstrip()[:-3].rstrip("\n")
    return [p for p in re.split(r"\n\s*\n", b) if p.strip()]
for name in sys.argv[1:]:
    c,y=[int(x) for x in name.split(":")]
    for s in re.split(r"\n(?=## )", (CORPUS/f"{c:03d}.md").read_text(encoding="utf-8")):
        if not re.match(rf"## Verse {c}:{y}\s*$", s.split("\n")[0].strip()): continue
        ps=body(s)
        idx=max(range(len(ps)), key=lambda i: len(RE.findall(ps[i])))
        earlier=set(RE.findall(" ".join(ps[:idx])))
        print("="*8, name, "| paras:", len(ps), "| worst idx:", idx, "| refs in it:", len(RE.findall(ps[idx])))
        print("ONLY-IN-WORST:", sorted(set(RE.findall(ps[idx]))-earlier))
        print("--- FULL WORST PARA ---")
        print(ps[idx])
        print()
