import re, pathlib
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
seen = 0; bad = 0
for ch in range(1, 115):
    txt = (CORPUS / f"{ch:03d}.md").read_text(encoding="utf-8")
    for s in re.split(r"\n(?=## )", txt):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", s.split("\n")[0].strip())
        if not m: continue
        seen += 1
        lines = s.split("\n")
        quote = []
        started = False
        for l in lines[1:]:
            if l.startswith(">"):
                quote.append(l); started = True
            elif started:
                break
        body = []
        started = False
        for l in lines[1:]:
            if not started:
                if l.startswith(">") or not l.strip() or l.strip() == "---": continue
                started = True
            body.append(l)
        b = "\n".join(body).rstrip()
        if b.endswith("---"): b = b[:-3].rstrip()
        if not quote or not b:
            bad += 1
            print("PROBLEM", ch, m.group(2), "quote", len(quote), "body", len(b))
print("sections seen:", seen, "quote mismatches:", bad)
