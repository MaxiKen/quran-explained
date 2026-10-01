#!/usr/bin/env python3
"""Build the app payload ``data/tafsir_NNN.json`` from ``tafsir/NNN.md``.

    python3 scripts/tafsir/build_data.py 112        # one chapter
    python3 scripts/tafsir/build_data.py --all      # every chapter file that exists
    python3 scripts/tafsir/build_data.py 112 --check   # fail if the payload is stale

Payload shape (what ``js/app.js`` reads):

    {"surah": 112, "intro": "<markdown>", "verses": {"1": "> <ayah_en>\\n\\n<body>"}}

``intro`` is the introduction prose; ``verses[M]`` is everything under
``## Verse N:M`` starting with the canonical ``> …`` line — the app strips that
leading quote at render time, so the markdown keeps it.

The build is a pure function of the markdown: running it twice changes nothing.
The payload is written with ``indent=2`` and no trailing newline, exactly the
shape the app has always served.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

TITLE = re.compile(r"^#\s+(.+)$", re.M)
INTRO = re.compile(r"^##\s+Introduction to the Sūrah\s*$", re.M)
VERSE = re.compile(r"^##\s+Verse\s+(\d+):(\d+)\s*$", re.M)
SEP = re.compile(r"^\s*---\s*$", re.M)


class Doc:
    def __init__(self, n: int, text: str):
        self.n = n
        self.text = text
        m = TITLE.search(text)
        self.title = m.group(1).strip() if m else ""
        m = INTRO.search(text)
        if not m:
            raise ValueError("no '## Introduction to the Sūrah' heading")
        first = VERSE.search(text, m.end())
        if not first:
            raise ValueError("no '## Verse N:V' heading")
        self.intro = text[m.end() : first.start()]
        self.sections: list[tuple[int, str]] = []
        marks = list(VERSE.finditer(text))
        for i, mark in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            self.sections.append((int(mark.group(2)), text[mark.end() : end]))
        self.intro = SEP.split(self.intro)[0].strip()

    def bodies(self) -> list[tuple[int, str]]:
        out = []
        for verse, raw in self.sections:
            body = raw
            if SEP.search(body):
                body = body[: SEP.search(body).start()]
            out.append((verse, body.strip()))
        return out


def load(n: int) -> Doc | None:
    path = C.ROOT / "tafsir" / f"{C.pad3(n)}.md"
    if not path.exists():
        return None
    return Doc(n, path.read_text(encoding="utf-8"))


def todo_verses(doc: Doc) -> list[int]:
    return [v for v, body in doc.bodies() if "TODO" in body or not body]


def build(n: int) -> dict | None:
    doc = load(n)
    if doc is None:
        return None
    pending = todo_verses(doc)
    if pending:
        raise SystemExit(
            f"tafsir/{C.pad3(n)}.md is not finished: verse(s) {pending[:6]} still have no prose. "
            "Refusing to publish a half-written chapter."
        )
    total = C.verse_count(n)
    got = [v for v, _ in doc.bodies()]
    if got != list(range(1, total + 1)):
        raise SystemExit(
            f"tafsir/{C.pad3(n)}.md has verses {got}; the chapter has 1-{total}. "
            "Every verse must appear once, in order."
        )
    verses = {}
    for verse, body in doc.bodies():
        text = f"> {C.ayah_en(n, verse)}"
        if body:
            text += "\n\n" + body
        verses[str(verse)] = text
    return {"surah": int(n), "intro": doc.intro.strip(), "verses": verses}


def payload(n: int) -> str:
    data = build(n)
    if data is None:
        raise SystemExit(f"tafsir/{C.pad3(n)}.md does not exist")
    return json.dumps(data, ensure_ascii=False, indent=2)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", nargs="?", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check", action="store_true", help="fail if the committed payload no longer matches")
    args = ap.parse_args(argv)

    numbers = (
        [ch["number"] for ch in C.chapters() if (C.ROOT / "tafsir" / f"{C.pad3(ch['number'])}.md").exists()]
        if args.all
        else [args.chapter]
    )
    if numbers == [None]:
        ap.error("give a chapter number or --all")

    for n in numbers:
        target = C.ROOT / "data" / f"tafsir_{C.pad3(n)}.json"
        text = payload(n)
        if args.check:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            if current != text:
                print(f"{target.relative_to(C.ROOT)}: STALE (run build_data.py {n})")
                return 1
            print(f"{target.relative_to(C.ROOT)}: current ({len(text):,} bytes)")
            continue
        target.write_text(text, encoding="utf-8")
        print(f"{target.relative_to(C.ROOT)} written — {len(text):,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
