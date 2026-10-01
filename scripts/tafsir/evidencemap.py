#!/usr/bin/env python3
"""evidencemap.py — Phase 1 of the two-phase approach: evidence first, commentary later.

The author's idea (2026-10-01): before any commentary is built, every verse gets its
*heads* and, under each head, a short summary of the evidence the eleven works carry for
it.  Nothing is written as commentary yet; the map says what will be built upon.  Later,
on the author's prompt, a chapter is built up from its map, and the length of each verse's
commentary is whatever its evidence needs — not a fixed range of words.

    python3 scripts/tafsir/evidencemap.py read 103 1            # survey one verse, all eleven works
    python3 scripts/tafsir/evidencemap.py read 103 1 --para tabari:3,4 qurtubi:7   # drill in
    python3 scripts/tafsir/evidencemap.py read 108 2 --find وانحر --only tabari,kathir   # where is it?
    python3 scripts/tafsir/evidencemap.py check 103             # validate evidence/103.md
    python3 scripts/tafsir/evidencemap.py check --all

A map declares its depth in its first comment, ``<!-- depth: survey -->`` or ``depth: full``.
*Survey* is the quick pass — highlights: at most 12 items a verse (8 in the introduction), each
at most 35 words — read from the capped passages and their tables of contents; the work it
leaves is the writer's to deepen when a chapter is built.  *Full* reads the passages through and
lists everything found (summaries up to 60 words).  The checker applies the limits of the depth
a map declares, and prints each verse's evidence weight (the distinct source text under it) beside
its item count.

``read`` is the reading method.  A passage can run to tens of thousands of characters, so it
prints each work's passage up to a cap, then a table of contents (paragraph sizes and
openings) for the rest, and says when a work attaches the same whole-sūrah text under every
verse.  ``--para`` prints chosen paragraphs in full.  What was read, and how deep, is the
writer's to judge; what was *found* is what the map records.

``check`` validates the map file ``evidence/NNN.md`` mechanically.  Format of a verse block::

    ## Verse 103:1

    > By the declining day!

    **Sources with text:** tabari, qurtubi, ...        (must equal what the digest holds)
    **Nothing further from:** jalalayn, abbas          (considered; nothing beyond what is above)

    ### A DESCRIPTIVE UPPERCASE HEAD                    (the future heading; unique in the chapter)

    - `103:1.1` · language · One-sentence summary of the evidence. [tabari, qurtubi@2]

A sūrah-level block comes first, headed ``## Introduction`` (items numbered ``N:0.k``): what the
works say about the whole sūrah — where and why it came, its merit, what it gathers — which is
the material of the commentary's introduction.  Its items cite the passages under verse 1 unless
they say ``@V``; it has no quoted line and no coverage requirement.

``kind`` is one of quran, hadith, athar, language, occasion, ruling, history, lesson.  The
bracket names the works that carry the point; ``@V`` says the passage sits under verse V of
the same sūrah.  Rules (ERROR fails, WARN is read): every one of the eleven works with text is
either cited or listed under "Nothing further from"; every cited passage exists in the
digest; item numbers run 1..n; heads are UPPERCASE and not reused; a cross-reference must be
a real verse; a hadith should name its collection and an athar its authority.  The map is a
working document, not the book: it may name the works (the independence law governs the
commentary built from it).  The digest it is checked against is ``tmp/sources/NNN.json``
(``sources.py N --cap-json 0``).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402

MAP_DIR = C.REPO / "evidence"

ALIASES = {
    "tabari": "tafsir-al-tabari", "qurtubi": "tafsir-al-qurtubi", "baghawi": "tafsir-al-baghawi",
    "kathir": "tafsir-ibn-kathir", "alusi": "tafsir-al-alusi", "jalalayn": "tafsir-al-jalalayn",
    "abbas": "tafsir-ibn-abbas", "saadi": "tafsir-as-saadi", "uthaymeen": "tafsir-ibn-uthaymeen",
    "maarif": "tafsir-maarif-ul-quran", "initial": "tafsir_initial",
}
SLUG_ALIAS = {slug: alias for alias, slug in ALIASES.items()}
KINDS = ("quran", "hadith", "athar", "language", "occasion", "ruling", "history", "lesson")
SUMMARY_WARN_WORDS = {"full": 60, "survey": 35}
ITEMS_WARN = {"full": None, "survey": 12}
INTRO_ITEMS_WARN = {"full": None, "survey": 8}
DEPTH_RE = re.compile(r"depth:\s*(survey|full)")

VERSE_RE = re.compile(r"^## Verse (\d+):(\d+)\s*$")
INTRO_RE = re.compile(r"^## Introduction\b.*$")
HEAD_RE = re.compile(r"^### (.+?)\s*$")
ITEM_RE = re.compile(r"^- `(\d+):(\d+)\.(\d+)` · (\w+) · (.+) \[([^\[\]]+)\]\s*$")
WITH_RE = re.compile(r"^\*\*Sources with text:\*\*\s*(.*?)\s*$")
NOTHING_RE = re.compile(r"^\*\*Nothing further from:\*\*\s*(.*?)\s*$")
XREF_RE = re.compile(r"\b(\d{1,3}):(\d{1,3})\b")
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")


def _digest(chapter: int):
    return A._digest(chapter)


def _need_digest(chapter: int) -> dict:
    digest = _digest(chapter)
    if not digest:
        raise SystemExit("tmp/sources/%s.json is missing — run: python3 scripts/tafsir/sources.py %d "
                         "--cap-json 0" % (C.pad3(chapter), chapter))
    return digest


def material_weights(chapter: int, digest) -> dict:
    """Distinct source text under each verse: a passage repeated from the previous verse counts once."""
    weights, prev = {}, {}
    for v in range(1, C.verse_count(chapter) + 1):
        chars = 0
        for slug, text in ((digest.get(str(v)) or {}).items()):
            text = (text or "").strip()
            if text and prev.get(slug) != text:
                chars += len(text)
            if text:
                prev[slug] = text
        weights[v] = chars
    return weights


def paragraphs(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


# ------------------------------------------------------------------------------ read

def cmd_read(args) -> int:
    chapter, verse = args.chapter, args.verse
    digest = _need_digest(chapter)
    entry = digest.get(str(verse)) or {}
    previous = digest.get(str(verse - 1)) or {}
    print("=== %d:%d  %s" % (chapter, verse, C.ayah_en(chapter, verse)))
    if args.para:
        for spec in args.para:
            alias, _, idx = spec.partition(":")
            slug = ALIASES.get(alias)
            if not slug or slug not in entry:
                print("[%s] no passage under %d:%d" % (alias, chapter, verse))
                continue
            paras = paragraphs(entry[slug])
            for i in [int(x) for x in idx.split(",") if x.strip().isdigit()]:
                if 0 <= i < len(paras):
                    print("\n[%s ¶%d of %d · %d chars]\n%s" % (alias, i, len(paras), len(paras[i]), paras[i]))
        return 0
    only = {s.strip() for s in args.only.split(",")} if args.only else None
    if args.find:
        for slug in C.SOURCE_ALLOWLIST:
            alias, text = SLUG_ALIAS[slug], (entry.get(slug) or "").strip()
            if (only and alias not in only) or not text:
                continue
            hits = [(i, p) for i, p in enumerate(paragraphs(text)) if args.find in p]
            print("\n[%s] %d of %d paragraphs contain %r" % (alias, len(hits), len(paragraphs(text)), args.find))
            for i, p in hits[: args.toc_lines]:
                at = p.index(args.find)
                print("  ¶%d (%s c) …%s…" % (i, "{:,}".format(len(p)), p[max(0, at - 50): at + 70].replace("\n", " ")))
        return 0
    for slug in C.SOURCE_ALLOWLIST:
        alias, text = SLUG_ALIAS[slug], (entry.get(slug) or "").strip()
        if only and alias not in only:
            continue
        if not text:
            print("\n[%s] no text for this verse" % alias)
            continue
        paras = paragraphs(text)
        lang = "ar" if len(ARABIC_RE.findall(text[:400])) > 40 else "en"
        head = "[%s %s · %s chars · %d paragraphs]" % (alias, lang, "{:,}".format(len(text)), len(paras))
        if verse > 1 and text == (previous.get(slug) or "").strip() and not args.force:
            print("\n%s  same text as %d:%d — a whole-sūrah passage attached to every verse; read there" %
                  (head, chapter, verse - 1))
            continue
        cap = args.cap_ar if lang == "ar" else args.cap_en
        print("\n" + head)
        print(text[:cap] + (" …" if len(text) > cap else ""))
        if len(text) > cap:
            pos, rows = 0, []
            for i, p in enumerate(paras):
                if pos >= cap and len(p) >= 150:
                    rows.append("  ¶%d (%s c) %s" % (i, "{:,}".format(len(p)), p[:80].replace("\n", " ")))
                pos += len(p) + 2
            print("  — beyond the cap: %d paragraphs of 150+ chars (--para %s:IDX to read one):" % (len(rows), alias))
            print("\n".join(rows[: args.toc_lines]))
            if len(rows) > args.toc_lines:
                print("  … %d more" % (len(rows) - args.toc_lines))
    return 0


# ----------------------------------------------------------------------------- parse

def parse(text: str, chapter: int):
    """``(verses, problems)``; verses maps verse number to its block."""
    verses, problems = {}, []
    cur = head = None
    for n, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if not line.strip() or line.startswith("# ") or line.strip() == "---" or line.startswith("<!--"):
            continue
        if INTRO_RE.match(line):
            if verses:
                problems.append(("ERROR", "%d:0" % chapter, n, "the introduction block comes first"))
            cur = verses[0] = {"line": n, "quote": None, "with": None, "nothing": [], "heads": []}
            head = None
            continue
        m = VERSE_RE.match(line)
        if m:
            c, v = int(m.group(1)), int(m.group(2))
            if c != chapter:
                problems.append(("ERROR", "%d:%d" % (c, v), n, "verse block belongs to chapter %d, not %d" % (c, chapter)))
            if v in verses:
                problems.append(("ERROR", "%d:%d" % (c, v), n, "verse appears twice"))
            expected = max(verses) + 1 if verses else 1
            if v != expected:
                problems.append(("ERROR", "%d:%d" % (c, v), n, "verses must run in order: %d comes next" % expected))
            cur = verses[v] = {"line": n, "quote": None, "with": None, "nothing": [], "heads": []}
            head = None
            continue
        if cur is None:
            problems.append(("WARN", "-", n, "text before the first verse block: %r" % line[:50]))
            continue
        if line.startswith("> "):
            cur["quote"] = line[2:].strip()
            continue
        m = WITH_RE.match(line)
        if m:
            cur["with"] = [s.strip() for s in m.group(1).split(",") if s.strip()]
            continue
        m = NOTHING_RE.match(line)
        if m:
            cur["nothing"] = [s.strip() for s in m.group(1).split(",") if s.strip() and s.strip() not in "—-"]
            continue
        m = HEAD_RE.match(line)
        if m:
            head = {"title": m.group(1), "line": n, "items": []}
            cur["heads"].append(head)
            continue
        if line.startswith("- "):
            m = ITEM_RE.match(line)
            if not m or head is None:
                problems.append(("ERROR", "%d" % chapter, n, "malformed item (or an item before any head): %r" % line[:70]))
                continue
            srcs = []
            for tok in m.group(6).split(","):
                tok = tok.strip()
                alias, _, loc = tok.partition("@")
                srcs.append((alias.strip(), int(loc) if loc.strip().isdigit() else (None if not loc.strip() else -1)))
            head["items"].append({"id": (int(m.group(1)), int(m.group(2)), int(m.group(3))), "kind": m.group(4),
                                  "summary": m.group(5).strip(), "sources": srcs, "line": n})
            continue
        problems.append(("WARN", "-", n, "unrecognised line: %r" % line[:60]))
    return verses, problems


# ----------------------------------------------------------------------------- check

def check_chapter(chapter: int):
    """``(problems, stats)`` for ``evidence/NNN.md``; problems are (level, ref, line, message)."""
    path = MAP_DIR / ("%s.md" % C.pad3(chapter))
    if not path.exists():
        return [("ERROR", str(chapter), 0, "evidence/%s.md does not exist" % C.pad3(chapter))], None
    raw = path.read_text(encoding="utf-8")
    verses, problems = parse(raw, chapter)
    depth_match = DEPTH_RE.search(raw[:1500])
    depth = depth_match.group(1) if depth_match else "full"
    digest = _digest(chapter)
    weights = material_weights(chapter, digest) if digest else {}
    if digest is None:
        problems.append(("INFO", str(chapter), 0, "tmp/sources/%s.json is missing, so source coverage and "
                         "locators were not checked (python3 scripts/tafsir/sources.py %d --cap-json 0)" % (C.pad3(chapter), chapter)))
    count = C.verse_count(chapter)
    pending = [v for v in range(1, count + 1) if v not in verses]
    if 0 not in verses:
        problems.append(("WARN", "%d:0" % chapter, 0, "no '## Introduction' block: the sūrah-level evidence (occasion, merit, what it gathers) is unmapped"))
    if pending and len(pending) < count:
        problems.append(("INFO", str(chapter), 0, "not yet mapped: %s" % ", ".join(
            "%d:%d" % (chapter, v) for v in pending[:8]) + (" …" if len(pending) > 8 else "")))
    heads_seen, prefixes = {}, {}
    stats = {"verses": {}, "kinds": {}, "sources": {}, "depth": depth}
    for v in sorted(verses):
        block = verses[v]
        ref = "%d:%d" % (chapter, v)
        if v < 0 or v > count:
            problems.append(("ERROR", ref, block["line"], "no such verse in the sūrah"))
            continue
        if v and (block["quote"] is None or C._norm_space(block["quote"]) != C._norm_space(C.ayah_en(chapter, v))):
            problems.append(("ERROR", ref, block["line"], "the quoted line is not the verse's translation from data/chapter_%s.js" % C.pad3(chapter)))
        for alias in (block["with"] or []) + block["nothing"]:
            if alias not in ALIASES:
                problems.append(("ERROR", ref, block["line"], "unknown work %r (use: %s)" % (alias, ", ".join(ALIASES))))
        have = None
        if digest is not None and v:
            have = sorted(SLUG_ALIAS[s] for s, t in (digest.get(str(v)) or {}).items() if s in SLUG_ALIAS and (t or "").strip())
            if block["with"] is None:
                problems.append(("ERROR", ref, block["line"], "missing the '**Sources with text:**' line (expected: %s)" % ", ".join(have)))
            elif sorted(block["with"]) != have:
                problems.append(("ERROR", ref, block["line"], "'Sources with text' lists %s but the digest holds text from %s" %
                                 (", ".join(sorted(block["with"])) or "none", ", ".join(have))))
        if not block["heads"]:
            problems.append(("ERROR", ref, block["line"], "no head: a verse needs at least one head with evidence under it"))
        used, n_items, words, expected_k = set(), 0, 0, 1
        for head in block["heads"]:
            title = head["title"]
            letters = re.sub(r"[^A-Za-z]", "", title)
            if not letters or title != title.upper():
                problems.append(("ERROR", ref, head["line"], "a head is an UPPERCASE descriptive title: %r" % title))
            if len(title.split()) > 12:
                problems.append(("WARN", ref, head["line"], "a head of %d words is a sentence, not a title" % len(title.split())))
            if title.lower() in heads_seen:
                problems.append(("ERROR", ref, head["line"], "head %r is also used under %s" % (title, heads_seen[title.lower()])))
            heads_seen.setdefault(title.lower(), ref)
            prefix = " ".join(title.lower().split()[:2])
            prefixes.setdefault(prefix, {}).setdefault(v, title)
            if not head["items"]:
                problems.append(("ERROR", ref, head["line"], "head %r has no evidence under it" % title))
            for it in head["items"]:
                n_items += 1
                cid, cv, k = it["id"]
                if (cid, cv) != (chapter, v) or k != expected_k:
                    problems.append(("ERROR", ref, it["line"], "item number should be %d:%d.%d, found %d:%d.%d" % (chapter, v, expected_k, cid, cv, k)))
                expected_k += 1
                if it["kind"] not in KINDS:
                    problems.append(("ERROR", ref, it["line"], "kind %r is not one of: %s" % (it["kind"], ", ".join(KINDS))))
                stats["kinds"][it["kind"]] = stats["kinds"].get(it["kind"], 0) + 1
                nwords = len(C.words(it["summary"]))
                words += nwords
                if nwords > SUMMARY_WARN_WORDS[depth]:
                    problems.append(("WARN", ref, it["line"], "%s is %d words: over the %d-word limit of a %s map" %
                                     (it["kind"], nwords, SUMMARY_WARN_WORDS[depth], depth)))
                for alias, loc in it["sources"]:
                    if alias not in ALIASES:
                        problems.append(("ERROR", ref, it["line"], "unknown work %r in the item's brackets" % alias))
                        continue
                    used.add(alias)
                    stats["sources"][alias] = stats["sources"].get(alias, 0) + 1
                    target = (v or 1) if loc is None else loc
                    if target < 1 or target > count:
                        problems.append(("ERROR", ref, it["line"], "%s@%s: no such verse in this sūrah" % (alias, loc)))
                    elif digest is not None and not ((digest.get(str(target)) or {}).get(ALIASES[alias]) or "").strip():
                        problems.append(("ERROR", ref, it["line"], "%s cites a passage under %d:%d, but that work has no text there" % (alias, chapter, target)))
                for c2, v2 in XREF_RE.findall(it["summary"]):
                    c2, v2 = int(c2), int(v2)
                    if not 1 <= c2 <= 114 or not 1 <= v2 <= C.verse_count(c2):
                        problems.append(("ERROR", ref, it["line"], "%d:%d is not a verse of the Qur'an" % (c2, v2)))
                if it["kind"] == "quran" and not XREF_RE.search(it["summary"]):
                    problems.append(("WARN", ref, it["line"], "a quran item should give the verse it cross-refers to (C:V)"))
                if it["kind"] == "hadith" and not A.COLLECTIONS.search(it["summary"]):
                    problems.append(("WARN", ref, it["line"], "a hadith names its collection (the commentary must) — none found; is it an athar or a lesson?"))
                if it["kind"] == "athar" and not (A.FIRST_GEN.search(it["summary"]) or A.SCHOLARS.search(it["summary"])):
                    problems.append(("WARN", ref, it["line"], "an athar names its authority — none found"))
        limit = (INTRO_ITEMS_WARN if v == 0 else ITEMS_WARN)[depth]
        if limit and n_items > limit:
            problems.append(("WARN", ref, block["line"], "%d items: a %s map keeps at most %d %s" %
                             (n_items, depth, limit, "in the introduction" if v == 0 else "a verse")))
        for alias in block["nothing"]:
            if alias in used:
                problems.append(("WARN", ref, block["line"], "%s is listed under 'Nothing further from' but an item cites it" % alias))
            if have is not None and alias not in have:
                problems.append(("WARN", ref, block["line"], "%s is listed under 'Nothing further from' but has no text for this verse" % alias))
        if have is not None and v:
            loose = [a for a in have if a not in used and a not in block["nothing"]]
            if loose:
                problems.append(("ERROR", ref, block["line"], "not accounted for: %s — cite each in an item, or list it under 'Nothing further from'" % ", ".join(loose)))
        stats["verses"][v] = {"heads": len(block["heads"]), "items": n_items, "words": words, "works": len(used),
                              "material": weights.get(v)}
    for prefix, by_verse in prefixes.items():
        if len(by_verse) >= 2:
            level = "ERROR" if len(by_verse) >= 3 else "WARN"
            problems.append((level, "%d" % chapter, 0, "%d verses open a head with %r: %s — keep the titles from falling into a template" %
                             (len(by_verse), prefix.upper(), ", ".join("%d:%d" % (chapter, x) for x in sorted(by_verse)))))
    stats["pending"] = pending
    return problems, stats


def cmd_check(args) -> int:
    chapters = [n for n in C.chapter_numbers() if (MAP_DIR / ("%s.md" % C.pad3(n))).exists()] if args.all else [args.chapter]
    if not chapters:
        print("no evidence maps exist yet")
        return 0
    bad = 0
    for n in chapters:
        problems, stats = check_chapter(n)
        errors = [p for p in problems if p[0] == "ERROR"]
        warns = [p for p in problems if p[0] == "WARN"]
        print("evidence/%s.md — %s (%d verses)" % (C.pad3(n), C.chapter_name(n), C.verse_count(n)))
        for level, ref, line, msg in sorted(problems, key=lambda p: ({"ERROR": 0, "WARN": 1, "INFO": 2}[p[0]], p[2])):
            print("  %-5s %-8s %s %s" % (level, ref, ("L%-4d" % line) if line else "     ", msg))
        if stats and stats["verses"]:
            rows = stats["verses"]
            print("\n  depth: %s     verse   heads  items  words  works  evidence weight (chars of source)" % stats["depth"])
            for v in sorted(rows):
                r = rows[v]
                print("  %d:%-4s %5d %6d %6d %6d  %s" % (n, v or "intro", r["heads"], r["items"], r["words"], r["works"],
                                                         "{:,}".format(r["material"]) if r["material"] is not None else "-"))
            tot_i = sum(r["items"] for r in rows.values())
            print("  total   %5d %6d %6d      — kinds: %s" % (
                sum(r["heads"] for r in rows.values()), tot_i, sum(r["words"] for r in rows.values()),
                ", ".join("%s %d" % kv for kv in sorted(stats["kinds"].items(), key=lambda kv: -kv[1]))))
        print("  RESULT: %s — %d error(s), %d warning(s)\n" % ("FAIL" if errors else "PASS", len(errors), len(warns)))
        bad += bool(errors) or (args.strict and bool(warns))
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read", help="survey one verse across the eleven works")
    r.add_argument("chapter", type=int)
    r.add_argument("verse", type=int)
    r.add_argument("--cap-en", type=int, default=3000)
    r.add_argument("--cap-ar", type=int, default=1500)
    r.add_argument("--toc-lines", type=int, default=40)
    r.add_argument("--force", action="store_true", help="print a whole-sūrah passage again under every verse")
    r.add_argument("--only", help="only these works, e.g. kathir,maarif")
    r.add_argument("--find", metavar="TEXT", help="list the paragraphs that contain TEXT (to locate a verse inside a whole-sūrah passage)")
    r.add_argument("--para", nargs="+", metavar="WORK:IDX[,IDX]", help="print chosen paragraphs in full, e.g. qurtubi:3,4")
    c = sub.add_parser("check", help="validate evidence/NNN.md")
    c.add_argument("chapter", type=int, nargs="?")
    c.add_argument("--all", action="store_true")
    c.add_argument("--strict", action="store_true", help="warnings fail too")
    args = ap.parse_args(argv)
    if args.cmd == "check" and not args.all and not args.chapter:
        ap.error("name a chapter or use --all")
    return cmd_read(args) if args.cmd == "read" else cmd_check(args)


if __name__ == "__main__":
    raise SystemExit(main())
