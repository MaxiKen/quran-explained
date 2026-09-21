import re, sys, json, pathlib
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REF = re.compile(r"\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)")

def body_of(section):
    lines = section.split("\n"); out = []; started = False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip() == "---": continue
            started = True
        out.append(l)
    t = "\n".join(out).rstrip()
    return t[:-3].rstrip() if t.endswith("---") else t

def nrefs(p): return len(REF.findall(p))

def split_para(p, maxrefs=5):
    if nrefs(p) <= maxrefs: return [p]
    # sentence split that keeps italics/quotes intact (split on ". " followed by capital or **)
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z*\"'“])", p)
    chunks, cur, currefs = [], [], 0
    for s in sents:
        r = nrefs(s)
        if cur and currefs + r > maxrefs:
            chunks.append(" ".join(cur)); cur, currefs = [s], r
        else:
            cur.append(s); currefs += r
    if cur: chunks.append(" ".join(cur))
    return chunks

def rebuild(ch, y):
    txt = (CORPUS / f"{int(ch):03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", txt):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m or int(m.group(1)) != int(ch) or int(m.group(2)) != int(y): continue
        b = body_of(s)
        paras = [q for q in re.split(r"\n\s*\n", b) if q.strip()]
        out = []
        for p in paras:
            out.extend(split_para(p))
        return "\n\n".join(out)
    raise SystemExit(f"section {ch}:{y} not found")

specs = [(int(a.split(":")[0]), int(a.split(":")[1])) for a in sys.argv[1:]]
data = {}
for ch, y in specs:
    data.setdefault(str(ch), {})[str(y)] = rebuild(ch, y)
pathlib.Path("/home/user/.work/split_batch.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote split_batch.json for", specs)
