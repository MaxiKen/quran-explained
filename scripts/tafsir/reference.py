#!/usr/bin/env python3
"""reference.py — expand a Qur'an cross-reference with the wording it points to.

v7.2: every cross-reference in the commentary carries the clause it points to,
copied verbatim from ``data/chapter_NNN.js``:

    (2:255 — **“Allah! There is no god ˹worthy of worship˺ except Him”**)

The reference is bold only, the clause is bold inside curly quotes, and the
wording is never typed by hand — a typed clause is where REF-QUOTE failures come
from. This tool prints the exact text to paste:

    python3 scripts/tafsir/reference.py 2:255               # the verse and its ready-made citations
    python3 scripts/tafsir/reference.py 2:255 --words 12    # shorter clauses
    python3 scripts/tafsir/reference.py --find "and fear a Day" --chapter 2
    python3 scripts/tafsir/reference.py --find "the Day of Judgement"       # search the whole Qur'an
    python3 scripts/tafsir/reference.py --scan 2            # every bare citation in tafsir/002.md
    python3 scripts/tafsir/reference.py --scan 2 --from 1 --to 50
    python3 scripts/tafsir/reference.py --scan 2 --write    # expand them in place

``--scan`` is the audit's companion: ``REF-BARE`` warns once a section carries one
or two citations without wording and fails from three, and the scan prints the
replacement for each of them. ``--write`` applies those replacements in place
(the clause is copied from ``data/``, so it cannot break REF-QUOTE), and reports
what it changed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402

CURLY_O, CURLY_C = "\u201c", "\u201d"


def _segments(text: str):
    """The verse cut into verbatim segments: phrase units, then after `, ; : ? !`."""
    words = [m.group(0) for m in re.finditer(r"\S+", text)]
    if not words:
        return []
    bounds = set()
    consumed = 0
    for unit in (C.split_phrases(text) or [text]):
        consumed += len(unit.split())
        bounds.add(min(consumed, len(words)))
    for i, token in enumerate(words):
        if i + 1 < len(words) and re.search(r"[,;:?!]$", token):
            bounds.add(i + 1)
    cuts = sorted(b for b in bounds if 0 < b < len(words))
    out, prev = [], 0
    for cut in cuts + [len(words)]:
        seg = " ".join(words[prev:cut]).strip()
        if seg:
            out.append(seg)
        prev = cut
    return out


def candidates(text: str, max_words: int = A.REF_QUOTE_WARN):
    """Clauses of a verse, in order, each at most ``max_words`` words.

    Every clause is a run of consecutive words of the stored translation — a
    segment, or neighbouring segments joined, or a verbatim prefix when one
    segment runs past the cap — so it can be pasted into the prose and still
    compare byte-for-byte (REF-QUOTE). Nothing is retyped and nothing is
    re-punctuated: the words are the verse's own, in its own order.
    """
    out, buf = [], []
    for seg in _segments(text):
        words = seg.split()
        if len(words) > max_words:                    # a prefix is still the verse's wording
            if buf:
                out.append(" ".join(buf))
                buf = []
            out.append(" ".join(words[:max_words]))
            continue
        trial = buf + [seg]
        if len(" ".join(trial).split()) <= max_words:
            buf = trial
        else:
            if buf:
                out.append(" ".join(buf))
            buf = [seg]
    if buf:
        out.append(" ".join(buf))
    seen, unique = set(), []
    for clause in out:
        key = C.loose_norm(clause)
        if clause.strip() and key not in seen:
            seen.add(key)
            unique.append(clause)
    return unique


def expansion(s_chapter: int, s_verse: int, clause: str) -> str:
    return "(%d:%d \u2014 **%s%s%s**)" % (s_chapter, s_verse, CURLY_O, clause, CURLY_C)


def card(s_chapter: int, s_verse: int, max_words: int, pick: int) -> int:
    text = C.ayah_en(s_chapter, s_verse)
    if not text:
        raise SystemExit("%d:%d is not a verse of the Qur'an" % (s_chapter, s_verse))
    clauses = candidates(text, max_words)
    if not clauses:
        raise SystemExit("%d:%d carries no clause short enough; raise --words" % (s_chapter, s_verse))
    print("%d:%d" % (s_chapter, s_verse))
    print("  %s" % text)
    print("")
    print("ready-made citations (paste one; the gate warns past 22 words, fails past 34):")
    for i, clause in enumerate(clauses):
        mark = " <- pick %d" % pick if i == pick else ""
        print("  %-4s (%d words) %s%s"
              % ("[%d]" % i, len(clause.split()), expansion(s_chapter, s_verse, clause), mark))
    print("")
    print("the cut this verse is measured against: python3 scripts/tafsir/scaffold.py %d --phrases"
          % s_chapter)
    return 0


def find(text: str, chapters=None, limit: int = 20) -> int:
    needle = C.loose_norm(text)
    hits = 0
    scope = chapters or C.chapter_numbers()
    for n in scope:
        try:
            verses = C.verses(n)
        except Exception:
            continue
        for v in verses:
            if needle and needle in C.loose_norm(v["ayah_en"]):
                print("%d:%d  %s" % (n, v["ayah_no_surah"], v["ayah_en"]))
                hits += 1
                if hits >= limit:
                    print("... (more matches; raise --limit)")
                    return 0
    if not hits:
        print("no verse of the Qur'an carries that wording — check the phrasing before citing it")
        return 1
    return 0


# ------------------------------------------------------------------ scan / write

def _list_refs(inner: str):
    """The references a citation list carries: '(2:156, 245, 281)' -> its three verses."""
    inner = inner.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    first = re.match(r"\s*(?:see(?: also)?|cf\.?)?\s*(\d{1,3}):(\d{1,3})", inner)
    if not first:
        return []
    chapter = int(first.group(1))
    refs = [(first.group(0).strip(), chapter, int(first.group(2)))]
    rest = inner[first.end():]
    for m in re.finditer(r"[;,]\s*(\d{1,3})(\s*[\u2013\u2014-]\s*\d{1,3})?", rest):
        refs.append(("%d:%s%s" % (chapter, m.group(1), m.group(2) or ""),
                     chapter, int(m.group(1))))
    return refs


def scan(chapter: int, start=None, end=None, write=False, max_words=A.REF_QUOTE_WARN,
         pick=0) -> int:
    path = C.output_path(chapter)
    if not path.exists():
        raise SystemExit("%s does not exist — scaffold it first" % path.relative_to(C.REPO))
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    changes, found, missing = 0, 0, 0
    shown = path if path.is_absolute() else C.REPO / path
    try:
        shown = shown.relative_to(C.REPO)
    except ValueError:
        pass

    def clause_for(ch, v):
        options = candidates(C.ayah_en(ch, v), max_words)
        if not options:
            return None
        return options[min(pick, len(options) - 1)]

    for i, line in enumerate(lines, start=1):
        verse = None
        for j in range(i, 0, -1):
            m = re.match(r"^## Verse \d+:(\d+)", lines[j - 1])
            if m:
                verse = int(m.group(1))
                break
        if start is not None and (verse is None or verse < start):
            continue
        if end is not None and (verse is None or verse > end):
            continue

        def replace(m, list_form=False):
            nonlocal changes, found, missing
            inner = m.group(0)
            if list_form:
                refs = _list_refs(inner)
            else:
                ref_text = inner[1:-1]                       # '2:255' or '2:255-257'
                refs = [(ref_text, int(m.group(1)), int(m.group(2)))]
            parts = []
            for ref_text, ch, v in refs:
                clause = clause_for(ch, v)
                if not clause:
                    missing += 1
                    print("L%-5d %-24s no clause short enough — cite it without the parenthetical"
                          % (i, inner))
                    return inner
                parts.append("%s \u2014 **%s%s%s**" % (ref_text, CURLY_O, clause, CURLY_C))
            new = "(" + "; ".join(parts) + ")"
            found += 1
            if write:
                changes += 1
            print("L%-5d %-26s -> %s" % (i, inner, new))
            return new if write else inner

        line = A.BARE_REF_LIST.sub(lambda m: replace(m, True), line)
        line = A.BARE_REF.sub(lambda m: replace(m, False), line)
        lines[i - 1] = line
    if write:
        path.write_text("\n".join(lines), encoding="utf-8")
        print("")
        print("expanded %d citation(s) in %s" % (changes, shown))
        if changes:
            print("re-gate: python3 scripts/tafsir/batch.py %d --from %s --to %s"
                  % (chapter, start or 1, end or C.verse_count(chapter)))
    elif not found and not missing:
        print("no bare citations in %s %s" % (shown,
                                              ("verses %s-%s" % (start, end)) if start else ""))
    elif not write:
        print("")
        print("%d bare citation(s) listed; re-run with --write to expand them" % found)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("verse", nargs="?", help="a verse to expand, e.g. 2:255")
    ap.add_argument("--words", type=int, default=A.REF_QUOTE_WARN,
                    help="longest clause offered (default 22, the gate's warn line)")
    ap.add_argument("--pick", type=int, default=0, help="which clause to lead with")
    ap.add_argument("--find", help="which verse of the Qur'an carries this wording?")
    ap.add_argument("--chapter", type=int, help="limit --find to one chapter")
    ap.add_argument("--limit", type=int, default=20, help="how many --find hits to print")
    ap.add_argument("--scan", type=int, metavar="N", help="list bare citations in tafsir/NNN.md")
    ap.add_argument("--from", dest="start", type=int, help="first verse of the scan")
    ap.add_argument("--to", dest="end", type=int, help="last verse of the scan")
    ap.add_argument("--write", action="store_true",
                    help="with --scan: apply the expansions to the chapter file")
    args = ap.parse_args(argv)

    if args.find:
        return find(args.find, [args.chapter] if args.chapter else None, args.limit)
    if args.scan:
        return scan(args.scan, args.start, args.end, args.write, args.words, args.pick)
    if args.verse:
        m = re.match(r"^(\d{1,3}):(\d{1,3})$", args.verse.strip())
        if not m:
            raise SystemExit("give a verse as C:V, e.g. 2:255")
        return card(int(m.group(1)), int(m.group(2)), args.words, args.pick)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
