import re, sys, json, pathlib
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"

def body_of(section):
    lines=section.split("\n"); out=[]; started=False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip()=="---": continue
            started=True
        out.append(l)
    t="\n".join(out).rstrip()
    return t[:-3].rstrip() if t.endswith("---") else t

edits = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
cache = {}
out = {}
for e in edits:
    key = e["verse"]; ch, y = key.split(":")
    if ch not in cache:
        cache[ch] = (CORPUS/f"{int(ch):03d}.md").read_text(encoding="utf-8")
    txt = cache[ch]
    for s in re.split(r"\n(?=## )", txt):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m or m.group(1) != ch or m.group(2) != y: continue
        body = body_of(s)
        if e["old"] not in body:
            print("NO MATCH:", key, "|", e["old"][:80]); break
        body2 = body.replace(e["old"], e["new"], 1)
        out.setdefault(ch, {})[y] = body2
        break
pathlib.Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("sections edited:", sum(len(v) for v in out.values()), "->", sys.argv[2])
