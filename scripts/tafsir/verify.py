#!/usr/bin/env python3
"""verify.py — confirm a claim exists in the sources before it is credited.

    python3 scripts/tafsir/verify.py "ÄmÄ«n"                 # every source, every chapter
    python3 scripts/tafsir/verify.py "Ø£Ø¹ÙØ§Ø¯Ù" --verse 2:187
    python3 scripts/tafsir/verify.py "Ruh al-Ma'ani" --list-sources
    python3 scripts/tafsir/verify.py "Ø¬Ø¹ÙØ±" --context 300

The attribution law in TAFSIR_PROMPT.md says a report may only be credited to a
source that actually carries it. This tool is how that is checked. It searches
the raw ``tafsir-*/NNN.txt`` files (and the ``tafsir_initial`` draft) for a term
and prints every hit with its source, chapter, verse and a snippet of context.

Search is diacritic-insensitive for Arabic and case-insensitive for Latin, so
"al-Qurtubi", "Qurtubi" and "ÙØ±Ø·Ø¨Ù" style searches behave as expected; the
transliterated spelling of an Arabic name will only hit the English sources,
which is itself useful information: a name that appears in no source at all is
a name you cannot attribute.

Exit status is 0 when there is at least one hit, 1 when there are none.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402


def fold(text: str) -> str:
    """Fold a string for searching: lower case, no diacritics, no punctuation."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed\u0640]", "", text)
    text = (text.replace("\u0671", "\u0627").replace("\u0622", "\u0627").replace("\u0623", "\u0627")
                .replace("\u0625", "\u0627").replace("\u0649", "\u064a").replace("\u0629", "\u0647")
                .replace("\u0624", "\u0648").replace("\u0626", "\u064a").replace("\u02be", "'")
                .replace("\u02bf", "'").replace("\u2019", "'"))
    text = text.lower()
    text = re.sub(r"[^0-9a-z\u0600-\u06ff' ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _context(text: str, start: int, end: int, width: int) -> str:
    piece = text[max(0, start - width): end + width].replace("\n", " ")
    return re.sub(r"\s+", " ", piece).strip()


def search(term: str, chapter: int | None, verse: int | None, width: int, limit: int):
    """Line-accurate search: fold each line, keep the verse marker that precedes it."""
    needle = fold(term)
    if not needle:
        raise SystemExit("nothing to search for")
    hits, truncated = [], False
    for src in C.source_catalog():
        pattern = "*.md" if src["kind"] == "study" else "*.txt"
        for path in sorted(src["path"].glob(pattern)):
            m = re.match(r"(\d{3})", path.name)
            if not m:
                continue
            n = int(m.group(1))
            if chapter is not None and n != chapter:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            current, lines = None, text.split("\n")
            for i, line in enumerate(lines):
                marker = re.match(r"^## \d+:(\d+)\s*$", line) or re.match(r"^\*\*(\d+)\*\*\s+", line)
                if marker:
                    current = int(marker.group(1))
                    continue
                if needle in fold(line):
                    if verse is not None and current != verse:
                        continue
                    # widen to neighbouring lines for context
                    lo = max(0, i - 2)
                    hi = min(len(lines), i + 3)
                    snippet = re.sub(r"\s+", " ", " ".join(lines[lo:hi])).strip()
                    if len(snippet) > width * 2:
                        k = fold(snippet).find(needle)
                        snippet = snippet[max(0, k - width): k + width]
                    hits.append((src["slug"], n, current, snippet))
                    if len(hits) >= limit:
                        return hits, needle, True
    return hits, needle, truncated


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("term", nargs="?", help="text to look for (Arabic or Latin)")
    ap.add_argument("--chapter", type=int, help="restrict to one chapter")
    ap.add_argument("--verse", help="restrict to one verse, written C:V (needs --chapter or full form)")
    ap.add_argument("--context", type=int, default=200, help="characters of context to show")
    ap.add_argument("--limit", type=int, default=40, help="stop after this many hits")
    ap.add_argument("--list-sources", action="store_true", help="print the source catalog and exit")
    args = ap.parse_args(argv)

    if args.list_sources:
        for s in C.source_catalog():
            print("%-26s %-3s %-6s %s" % (s["slug"], s["lang"], s["kind"], s["title"][:70]))
        return 0

    if not args.term:
        raise SystemExit("give a term to search for (or --list-sources)")

    chapter, verse = args.chapter, None
    if args.verse:
        if ":" in args.verse:
            c, v = args.verse.split(":", 1)
            chapter, verse = int(c), int(v)
        else:
            verse = int(args.verse)

    hits, needle, truncated = search(args.term, chapter, verse, args.context, args.limit)
    if not hits:
        print("no hits for %r%s" % (args.term, " in chapter %d" % chapter if chapter else ""))
        print("a claim that cannot be found in a source cannot be credited to it")
        return 1
    for slug, n, v, snippet in hits:
        print("%-24s %s:%s  %s" % (slug.replace("tafsir-", ""), C.pad3(n), v if v else "?", snippet))
    print("\n%d hit(s)%s" % (len(hits), " (stopped at --limit)" if truncated else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
