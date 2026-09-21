import re, sys, json, pathlib

CORPUS = pathlib.Path(__file__).resolve().parents[2] / "markdown commentry"
REF = re.compile(r"\((\d{1,3}:\d{1,3})(?:-\d{1,3})?\)")
HAD = re.compile(r"(Bukh[āa]r[īi]|Muslim\b|Tirmidh[īi]|Nas[āa]ʾ[īi]|Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah|Musnad|Aḥmad)")


def body_of(section):
    lines = section.split("\n")
    out, started = [], False
    for l in lines[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip() == "---":
                continue
            started = True
        out.append(l)
    text = "\n".join(out).rstrip()
    if text.endswith("---"):
        text = text[:-3].rstrip()
    return text


def main(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    applied = refused = 0
    for ch, verses in data.items():
        ch = int(ch)
        f = CORPUS / f"{ch:03d}.md"
        txt = f.read_text(encoding="utf-8")
        # keep separators so the file round-trips exactly
        chunks = re.split(r"(\n)(?=## )", txt)
        for i, s in enumerate(chunks):
            if not s.startswith("## "):
                continue
            m = re.match(r"## Verse (\d+):(\d+)\s*\n?$", s.split("\n")[0].strip())
            if not m:
                continue
            ay = int(m.group(2))
            new = verses.get(str(ay)) or verses.get(ay)
            if not new:
                continue
            old = body_of(s)
            lost = [r for r in sorted(set(REF.findall(old))) if f"({r}" not in new]
            lh = sorted({h for h in HAD.findall(old) if h not in new})
            if lost or lh:
                print(f"  REFUSED {ch}:{ay} lost refs={lost} hadith={lh}")
                refused += 1
                continue
            header = s.split("\n")[0].strip()
            quote = []
            for l in s.split("\n")[1:]:
                if l.startswith(">"):
                    quote.append(l)
                elif quote:
                    break
            chunks[i] = header + "\n" + "\n".join(quote) + "\n\n" + new.rstrip() + "\n\n---"
            applied += 1
        f.write_text("".join(chunks), encoding="utf-8")
    print(f"applied {applied}, refused {refused}")


if __name__ == "__main__":
    main(sys.argv[1])
