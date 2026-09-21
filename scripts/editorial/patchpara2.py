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

spec = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
out = {}
for key, item in spec.items():
    ch, y = key.split(":")
    txt = (CORPUS / f"{int(ch):03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", txt):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m or m.group(1) != ch or m.group(2) != y: continue
        ps = [p for p in re.split(r"\n\s*\n", body_of(s)) if p.strip()]
        keep = set(item.get("keep", range(len(ps))))
        repl = {int(k): v for k, v in item.get("replace", {}).items()}
        final = []
        for i, p in enumerate(ps):
            if i in repl: final.extend(repl[i].split("\n\n"))
            elif i in keep: final.append(p)
        out.setdefault(ch, {})[y] = "\n\n".join(final)
        break
pathlib.Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", sys.argv[2])
