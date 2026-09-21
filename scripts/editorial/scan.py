import re, sys, pathlib
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
ch = int(sys.argv[1])
txt = (CORPUS / f"{ch:03d}.md").read_text(encoding="utf-8")
suspect = 0; lower = 0; heads = {}
spaces = 0
LAZY = re.compile(r"\(the sūrah (?:by this|so)|\(by this |\(REFS|\(see §")
for s in re.split(r"\n(?=## )", txt):
    m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
    if not m: continue
    body = []
    started = False
    for l in s.split("\n")[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip() == "---": continue
            started = True
        body.append(l)
    b = "\n".join(body)
    if LAZY.search(b): suspect += 1
    for h in re.findall(r"\*\*(.+?)\*\*", b):
        key = h.strip().lower()
        heads.setdefault(key, 0)
        heads[key] += 1
    for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", b)):
        sent = sent.strip()
        if sent and sent[0].islower() and not sent.startswith(("a ", "an ", "the ")):
            lower += 1
    spaces += len(re.findall(r"\s+[.,]", b))
dups = sum(1 for k, v in heads.items() if v > 0 and list(heads.values()).count(v) and False)
print(f"SUSPECT parentheticals: {suspect}")
print(f"lowercase starts: {lower}")
print(f"repeated headings: {sum(1 for k,v in heads.items() if list(heads.keys()).count(k)>0 and v>1 and False)}")
print(f"stray spaces: {spaces}")
