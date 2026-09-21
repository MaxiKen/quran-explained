import re, sys, pathlib
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REFc = re.compile(r"\((\d{1,3}:\d{1,3})(?:-\d{1,3})?\)")
HADc = re.compile(r"(Bukh[āa]r[īi]|Muslim\b|Tirmidh[īi]|Nas[āa]ʾ[īi]|Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah|Musnad|Aḥmad)")
def body_of(s):
    lines = s.split("\n"); out = []; started = False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip() == "---": continue
            started = True
        out.append(l)
    t = "\n".join(out).rstrip()
    if t.endswith("---"): t = t[:-3].rstrip()
    return t
targets = {}
for a in sys.argv[1:]:
    c, y = a.split(":")
    targets.setdefault(int(c), set()).add(int(y))
for ch in sorted(targets):
    for s in re.split(r"\n(?=## )", (CORPUS / f"{ch:03d}.md").read_text(encoding="utf-8")):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m or int(m.group(2)) not in targets[ch]: continue
        b = body_of(s)
        print(f"##### {ch}:{m.group(2)} ({len(b.split())} words) REFS={sorted(set(REFc.findall(b)))} HAD={sorted(set(HADc.findall(b)))}")
        print(re.sub(r"\s+", " ", b)); print()
