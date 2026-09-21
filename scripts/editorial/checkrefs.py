import re, sys, json, pathlib

CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REF = re.compile(r"\((\d{1,3}:\d{1,3})(?:-\d{1,3})?\)")
HAD = re.compile(r"(Bukh[āa]r[īi]|Muslim\b|Tirmidh[īi]|Nas[āa]ʾ[īi]|Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah|Musnad|Aḥmad)")

def body_of(section):
    lines = section.split("\n"); out = []; started = False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip() == "---": continue
            started = True
        out.append(l)
    t = "\n".join(out).rstrip()
    if t.endswith("---"): t = t[:-3].rstrip()
    return t

data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
total = 0
for ch, verses in data.items():
    txt = (CORPUS / f"{int(ch):03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", txt):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m: continue
        new = verses.get(m.group(2))
        if not new: continue
        old = body_of(s)
        lost = [r for r in sorted(set(REF.findall(old))) if f"({r}" not in new]
        lh = sorted({h for h in HAD.findall(old) if h not in new})
        if lost or lh:
            total += 1
            print(f"{ch}:{m.group(2)} MISSING refs={lost} hadith={lh}")
print("sections missing anything:", total)
