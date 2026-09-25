#!/usr/bin/env python3
"""inject.py — fill a part file's placeholders with byte-exact text.

    {{P:v:i}}            this verse's own phrase i (bold italics, quoted)
    {{X:c:v:clause}}     a clause of another verse (bold, inside its reference)

Every phrase and clause is copied straight out of the chapter data, so nothing in
the part file can drift from data/chapter_002.js. Anything that does not verify is
reported and left alone, which is why a spliced part file should be injected
before it goes into tafsir/002.md:

    python3 tmp/work/inject.py tmp/work/c2_v14.md …
    python3 tmp/work/inject.py tmp/work/c2_v*.md
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "scripts/tafsir")
import corpus as C  # noqa: E402

P = re.compile(r"\{\{P:(\d+):(\d+)\}\}")
X = re.compile(r"\{\{X:(\d+):(\d+):(.+?)\}\}")


def fill(path: Path, quiet: bool = False) -> int:
    text = path.read_text(encoding="utf-8")
    bad = []

    def sub_p(m):
        verse, i = int(m.group(1)), int(m.group(2))
        phrases = C.split_phrases(C.ayah_en(2, verse)) if verse else []
        if i >= len(phrases):
            bad.append("no phrase %d in 2:%d" % (i, verse))
            return m.group(0)
        return "***\u201c%s\u201d***" % phrases[i]

    def sub_x(m):
        ch, v, clause = int(m.group(1)), int(m.group(2)), m.group(3)
        if clause not in C.ayah_en(ch, v):
            bad.append("clause not byte-exact in %d:%d: %r" % (ch, v, clause[:60]))
            return m.group(0)
        return "(%d:%d \u2014 **\u201c%s\u201d**)" % (ch, v, clause)

    text = X.sub(sub_x, text)
    text = P.sub(sub_p, text)
    path.write_text(text, encoding="utf-8")

    if not quiet:
        if bad:
            print("  INJECT PROBLEMS in %s:" % path.name)
            for b in bad:
                print("   -", b)
        for block in re.split(r"\n\s*\n", text):
            block = block.strip()
            if not block or block.startswith("**"):
                continue
            print("  %-24s %4d words" % (path.name, len(block.split())))
    return len(bad)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    quiet = "-q" in sys.argv
    problems = 0
    for arg in args:
        for path in sorted(Path().glob(arg)) if any(ch in arg for ch in "*?") else [Path(arg)]:
            problems += fill(path, quiet=quiet or len(args) > 1)
    if problems:
        print("inject: %d problem(s) — fix the part file and run again" % problems)
        sys.exit(1)
