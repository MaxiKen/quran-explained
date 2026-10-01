#!/usr/bin/env python3
"""evidencemap.py — Phase 1 of the two-phase approach: evidence first, commentary later.

The author's idea (2026-10-01): before any commentary is built, every verse gets its
*heads* and, under each head, a summary of the evidence the eleven works carry for it.
Nothing is written as commentary yet; the map says what will be built upon.  Later, on the
author's prompt, a chapter is built up from its map, and the length of each verse's
commentary is whatever its evidence needs — not a fixed range of words.

    python3 scripts/tafsir/evidencemap.py read 103 1 --full     # every paragraph of every work, numbered
    python3 scripts/tafsir/evidencemap.py read 103 1 --para tabari:3,4 qurtubi:7   # chosen paragraphs
    python3 scripts/tafsir/evidencemap.py read 108 2 --find وانحر --only tabari,kathir   # where is it?
    python3 scripts/tafsir/evidencemap.py check 103             # validate evidence/103.md
    python3 scripts/tafsir/evidencemap.py check 103 --gaps      # list the paragraphs not yet accounted for
    python3 scripts/tafsir/evidencemap.py check --all

**Depth.**  A map declares its depth in its first comment, ``<!-- depth: full -->`` or
``depth: survey``.  The owner chose *full* on 2026-10-01 ("103 style … more evidence than what's
present"), so full is the standard; *survey* is kept for quick looks and is not accepted as a
finished map.  A full map reads every passage through and records everything found:

* one item for each distinct report, view, reading, ruling or argument, with every name that
  carries it, the chain or wording the source gives, the ground offered, and the verdict if the
  source passes one (summaries up to 100 words — split rather than squeeze);
* every citation points at paragraphs — ``tabari¶3-5``, ``qurtubi¶7+9``, ``alusi@2¶4`` (the
  passage under verse 2) — so the claim can be opened and the writer can go straight to it.  A paragraph
  longer than 2,500 characters (some run to 50,000: one discussion in one block) is pointed at in
  **chunks** of about 1,200 characters, numbered from 1 inside it: ``kathir¶1.17-1.19``, ``qurtubi¶12.3``.
  A long paragraph is never cited by its bare number, and a range may not run across one, so a pointer
  always says *where* in it; an item that points at more than 6,000 characters is warned;
* **no paragraph is left behind**: once the last verse is mapped, each unit — a paragraph, or a chunk
  of a long one — of each work's passage (a passage repeated under several verses counts once) is
  either cited by an item or listed on a ``**Set aside:**`` line with the reason in brackets.  Headings
  and separators (under 20 letters) are exempt.  The check prints, per work, how many units are cited,
  set aside and missing, so how much of the evidence the map carries is a number, not an impression.
  The chunking rule (``chunks()``) is part of the format: changing it renumbers every pointer into a
  long paragraph.

``read`` is the reading method.  It prints each work's passage with its paragraphs numbered
from 1 (``¶4.2`` is the second chunk of long paragraph 4).  ``--full`` prints every paragraph; without it a passage is cut at a cap and the rest is
listed in a table of contents (paragraph sizes and openings).  It says when a work attaches the
same whole-sūrah text under every verse.  ``--para`` prints chosen paragraphs in full.

``check`` validates the map file ``evidence/NNN.md`` mechanically.  Format of a verse block::

    ## Verse 103:1

    > By the ˹passage of˺ time

    **Sources with text:** tabari, qurtubi, ...        (must equal what the digest holds)
    **Nothing further from:** jalalayn, abbas          (considered here; every paragraph is already cited)
    **Set aside:** tabari¶7 (chain only), alusi¶4 (repeats ¶3)

    ### A DESCRIPTIVE UPPERCASE HEAD                    (the future heading; unique in the chapter)

    - `103:1.1` · language · Summary of the evidence. [tabari¶3-5, qurtubi¶7, alusi@2¶4]

A sūrah-level block comes first, headed ``## Introduction`` (items numbered ``N:0.k``): what the
works say about the whole sūrah — where and why it came, its merit, what it gathers — which is
the material of the commentary's introduction.  Its items cite the passages under verse 1 unless
they say ``@V``; it has no quoted line and no "Sources with text" line.

``kind`` is one of quran, hadith, athar, language, occasion, ruling, history, lesson.  Rules
(ERROR fails, WARN is read): every one of the eleven works with text is either cited or listed
under "Nothing further from"; every cited passage and paragraph exists in the digest; a full map
points at paragraphs and leaves none unaccounted; item numbers run 1..n; heads are UPPERCASE and
not reused; a cross-reference must be a real verse; a hadith should name its collection and an
athar its authority.  The map is a working document, not the book: it may name the works (the
independence law governs the commentary built from it).  The digest it is checked against is
``tmp/sources/NNN.json`` (``sources.py N --cap-json 0``).  While some verses are still unmapped the
paragraph count is reported but not enforced.
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
SUMMARY_WARN_WORDS = {"full": 100, "survey": 35}
SUMMARY_MIN_WORDS = {"full": 8, "survey": 0}
TRIVIAL_LETTERS = 20      # a paragraph of fewer letters is a heading or a separator, exempt from coverage
ASIDE_SHARE_WARN = 0.20   # a full map that sets aside more than this share of the source text is not carrying it
SPLIT_OVER = 2500         # a paragraph longer than this is pointed at in chunks (¶4.1, ¶4.2, …)
CHUNK_TARGET = 1200       # a chunk runs to about this many characters
CHUNK_MIN = 300           # …and is not cut shorter than this unless the paragraph ends
CITE_WARN_CHARS = 6000    # one item that cites more source text than this is not pointing at anything
ITEMS_WARN = {"full": None, "survey": 12}
INTRO_ITEMS_WARN = {"full": None, "survey": 8}
DEPTH_RE = re.compile(r"depth:\s*(survey|full)")

VERSE_RE = re.compile(r"^## Verse (\d+):(\d+)\s*$")
INTRO_RE = re.compile(r"^## Introduction\b.*$")
HEAD_RE = re.compile(r"^### (.+?)\s*$")
ITEM_RE = re.compile(r"^- `(\d+):(\d+)\.(\d+)` · (\w+) · (.+) \[([^\[\]]+)\]\s*$")
WITH_RE = re.compile(r"^\*\*Sources with text:\*\*\s*(.*?)\s*$")
NOTHING_RE = re.compile(r"^\*\*Nothing further from:\*\*\s*(.*?)\s*$")
ASIDE_RE = re.compile(r"^\*\*Set aside:\*\*\s*(.*?)\s*$")
_REF = r"\d+(?:\.\d+)?"                      # a paragraph (4) or a chunk of a long paragraph (4.2)
_SPEC = _REF + r"(?:-" + _REF + r")?(?:\+" + _REF + r"(?:-" + _REF + r")?)*"
CITE_RE = re.compile(r"^([A-Za-z]+)(?:@(\d+))?(?:¶(" + _SPEC + r"))?$")
ASIDE_TOKEN_RE = re.compile(r"([A-Za-z]+)(?:@(\d+))?¶(" + _SPEC + r")(?:\s*\(([^()]*)\))?")
REF_RE = re.compile(r"^(\d+)(?:\.(\d+))?$")
XREF_RE = re.compile(r"\b(\d{1,3}):(\d{1,3})\b")
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
# an athar names whom it comes from; beyond the audit's list, the Companions and Successors the maps meet
ATHAR_AUTHORITY = re.compile(r"(Compan|Successor|Ṣaḥābī|Tābiʿ|ʿAlī|Abū Bakr|ʿUmar|ʿUthmān|ʿĀʾishah|Ubayy|Ḥafṣah|Abū Ḥudhayfah|"
                             r"al-Ḥasan|Ibrāhīm|Maymūn|Zayd ibn Aslam|Ibn al-Zubayr|Ibn Zayd|al-Ḍaḥḥāk|Ibn Kaysān|Ibn ʿAwn)")


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


def is_trivial(paragraph: str) -> bool:
    """A heading, a separator or a bare verse quotation: too short to carry evidence."""
    return sum(1 for ch in paragraph if ch.isalpha()) < TRIVIAL_LETTERS


def chunks(paragraph: str):
    """The pieces a long paragraph is pointed at in: packed to about CHUNK_TARGET characters, cut at line
    breaks where it can, else at sentence ends, else at spaces.  The rule is part of the format — changing
    it renumbers every pointer into a long paragraph."""
    pieces = []
    for line in paragraph.split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) <= CHUNK_TARGET:
            pieces.append(line)
            continue
        for sentence in re.split(r"(?<=[.!?؟])\s+", line):
            while len(sentence) > CHUNK_TARGET:
                cut = sentence.rfind(" ", 0, CHUNK_TARGET)
                cut = cut if cut > CHUNK_MIN else CHUNK_TARGET
                pieces.append(sentence[:cut])
                sentence = sentence[cut:].lstrip()
            if sentence:
                pieces.append(sentence)
    out, cur = [], ""
    for piece in pieces:
        if cur and len(cur) + 1 + len(piece) > CHUNK_TARGET and len(cur) >= CHUNK_MIN:
            out.append(cur)
            cur = piece
        else:
            cur = (cur + "\n" + piece) if cur else piece
    if cur:
        if out and len(cur) < CHUNK_MIN:
            out[-1] += "\n" + cur
        else:
            out.append(cur)
    return out


def units(text: str):
    """The passage as the units pointers name: ``[(paragraph, chunk, text)]``.  A paragraph of up to SPLIT_OVER
    characters is one unit (chunk 0); a longer one is several, numbered from 1."""
    out = []
    for n, para in enumerate(paragraphs(text), start=1):
        if len(para) > SPLIT_OVER:
            out.extend((n, k, piece) for k, piece in enumerate(chunks(para), start=1))
        else:
            out.append((n, 0, para))
    return out


def label(unit) -> str:
    """4 for a paragraph, 4.2 for the second chunk of a long one."""
    return "%d" % unit[0] if not unit[1] else "%d.%d" % (unit[0], unit[1])


def parse_spec(spec: str):
    """``3-5+9`` or ``4.2-4.5`` -> a list of ((paragraph, chunk), (paragraph, chunk)) ranges; ``None`` if it
    cannot be read.  Paragraphs and chunks count from 1; chunk 0 means a bare paragraph."""
    parts = []
    for part in spec.split("+"):
        ends = part.split("-")
        if len(ends) > 2 or not all(ends):
            return None
        refs = []
        for e in ends:
            m = REF_RE.match(e)
            if not m or int(m.group(1)) < 1 or (m.group(2) is not None and int(m.group(2)) < 1):
                return None
            refs.append((int(m.group(1)), int(m.group(2) or 0)))
        parts.append((refs[0], refs[-1]))
    return parts


def resolve(parts, us, strict=True):
    """``(unit indices, problems)``: what a parsed spec covers in the units ``us`` of one passage.  Strictly (in
    a map), a long paragraph is only ever named by its chunks and a range may not run across one; leniently
    (when reading), a bare long paragraph means all its chunks."""
    first, last, pos, split = {}, {}, {}, set()
    for i, (n, k, _) in enumerate(us):
        first.setdefault(n, i)
        last[n] = i
        pos[(n, k)] = i
        if k:
            split.add(n)
    covered, problems = set(), []
    for a, b in parts:
        ends, bad = [], None
        for which, (n, k) in enumerate((a, b)):
            if n not in first:
                bad = "that passage has no paragraph %d (it has %d)" % (n, len(set(u[0] for u in us)))
            elif n in split and not k:
                if strict:
                    bad = "paragraph %d is long — name its chunks (%d.1 … %d.%d)" % (n, n, n, sum(1 for u in us if u[0] == n))
                else:
                    ends.append(first[n] if which == 0 else last[n])
                    continue
            elif n not in split and k:
                bad = "paragraph %d is not split into chunks" % n
            elif (n, k) not in pos:
                bad = "paragraph %d has no chunk %d (it has %d)" % (n, k, sum(1 for u in us if u[0] == n))
            if bad:
                break
            ends.append(pos[(n, k)])
        if bad:
            problems.append(bad)
            continue
        i, j = ends
        if j < i:
            problems.append("the range runs backwards")
            continue
        if strict:
            named = {a[0], b[0]}
            crossed = sorted({us[x][0] for x in range(i, j + 1) if us[x][1] and us[x][0] not in named})
            if crossed:
                problems.append("the range crosses long paragraph %d — name its chunks" % crossed[0])
                continue
        covered.update(range(i, j + 1))
    return covered, problems


def compress_units(labels) -> str:
    """[(index, label)] -> '¶1-3, ¶7, ¶9.2-9.5': runs of neighbouring units are written as ranges."""
    items, parts, i = sorted(labels), [], 0
    while i < len(items):
        j = i
        while j + 1 < len(items) and items[j + 1][0] == items[j][0] + 1:
            j += 1
        parts.append("¶" + (items[i][1] if i == j else "%s-%s" % (items[i][1], items[j][1])))
        i = j + 1
    return ", ".join(parts)


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
            us = units(entry[slug])
            parts = parse_spec(idx.replace(",", "+"))
            if parts is None:
                print("[%s] cannot read %r (write 3, 3-5, 3+7 or 4.2-4.5)" % (alias, idx))
                continue
            covered, problems = resolve(parts, us, strict=False)
            for msg in problems:
                print("[%s] %s" % (alias, msg))
            for i in sorted(covered):
                print("\n[%s ¶%s of %d · %d chars]\n%s" % (alias, label(us[i]), len(paragraphs(entry[slug])), len(us[i][2]), us[i][2]))
        return 0
    only = {s.strip() for s in args.only.split(",")} if args.only else None
    if args.find:
        for slug in C.SOURCE_ALLOWLIST:
            alias, text = SLUG_ALIAS[slug], (entry.get(slug) or "").strip()
            if (only and alias not in only) or not text:
                continue
            us = units(text)
            hits = [u for u in us if args.find in u[2]]
            print("\n[%s] %d of %d units contain %r" % (alias, len(hits), len(us), args.find))
            for u in hits[: args.toc_lines]:
                at = u[2].index(args.find)
                print("  ¶%s (%s c) …%s…" % (label(u), "{:,}".format(len(u[2])), u[2][max(0, at - 50): at + 70].replace("\n", " ")))
        return 0
    for slug in C.SOURCE_ALLOWLIST:
        alias, text = SLUG_ALIAS[slug], (entry.get(slug) or "").strip()
        if only and alias not in only:
            continue
        if not text:
            print("\n[%s] no text for this verse" % alias)
            continue
        us = units(text)
        n_paras = len(paragraphs(text))
        lang = "ar" if len(ARABIC_RE.findall(text[:400])) > 40 else "en"
        head = "[%s %s · %s chars · %d paragraphs%s]" % (alias, lang, "{:,}".format(len(text)), n_paras,
                                                         (" in %d units" % len(us)) if len(us) != n_paras else "")
        if verse > 1 and text == (previous.get(slug) or "").strip() and not args.force:
            print("\n%s  same text as %d:%d — a whole-sūrah passage attached to every verse; read there" %
                  (head, chapter, verse - 1))
            continue
        cap = 10 ** 9 if args.full else (args.cap_ar if lang == "ar" else args.cap_en)
        rendered = "\n\n".join("¶%s %s" % (label(u), u[2]) for u in us)
        print("\n" + head)
        print(rendered[:cap] + (" …" if len(rendered) > cap else ""))
        if len(rendered) > cap:
            pos, rows = 0, []
            for u in us:
                if pos >= cap and len(u[2]) >= 150:
                    rows.append("  ¶%s (%s c) %s" % (label(u), "{:,}".format(len(u[2])), u[2][:80].replace("\n", " ")))
                pos += len("¶%s " % label(u)) + len(u[2]) + 2
            print("  — beyond the cap: %d units of 150+ chars (--para %s:N to read one, or --full):" % (len(rows), alias))
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
            cur = verses[0] = {"line": n, "quote": None, "with": None, "nothing": [], "aside": [], "heads": []}
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
            cur = verses[v] = {"line": n, "quote": None, "with": None, "nothing": [], "aside": [], "heads": []}
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
        m = ASIDE_RE.match(line)
        if m:
            for alias, loc, spec, reason in ASIDE_TOKEN_RE.findall(m.group(1)):
                parts = parse_spec(spec)
                if parts is None:
                    problems.append(("ERROR", "-", n, "cannot read the paragraphs %r in 'Set aside'" % spec))
                    continue
                cur["aside"].append({"alias": alias, "loc": int(loc) if loc else None, "spec": parts,
                                     "raw": "%s%s¶%s" % (alias, ("@" + loc) if loc else "", spec),
                                     "reason": reason.strip(), "line": n})
            if not ASIDE_TOKEN_RE.search(m.group(1)):
                problems.append(("ERROR", "-", n, "'Set aside' names no paragraphs (write tabari¶7 (reason), …)"))
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
                cm = CITE_RE.match(tok)
                if not cm:
                    srcs.append({"alias": tok, "loc": None, "spec": None, "raw": tok, "bad": True})
                    continue
                alias, loc, spec = cm.groups()
                parts = parse_spec(spec) if spec else None
                srcs.append({"alias": alias, "loc": int(loc) if loc else None, "spec": parts, "raw": tok,
                             "bad": bool(spec) and parts is None})
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
    if depth == "survey":
        problems.append(("WARN", str(chapter), 0, "a survey map is not the chosen depth: the owner chose full depth on 2026-10-01 — "
                         "rebuild this chapter at full depth (pointers, every paragraph accounted for) before Phase 2"))
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
    cited, aside = {}, {}          # (work, passage text) -> unit indices cited / set aside
    unit_cache = {}

    def units_of(text):
        if text not in unit_cache:
            unit_cache[text] = units(text)
        return unit_cache[text]

    def passage(alias, target):
        return ((digest.get(str(target)) or {}).get(ALIASES[alias]) or "").strip() if digest else ""

    def note(bucket, alias, text, parts, ref, line, raw, item=False):
        us = units_of(text)
        covered, errs = resolve(parts, us)
        for msg in errs:
            problems.append(("ERROR", ref, line, "%s: %s" % (raw, msg)))
        bucket.setdefault((alias, text), set()).update(covered)
        chars = sum(len(us[i][2]) for i in covered)
        if item and chars > CITE_WARN_CHARS:
            problems.append(("WARN", ref, line, "%s points at %s characters — an item cites what it draws on; split it into items that each point at their own part" % (
                raw, "{:,}".format(chars))))

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
                    problems.append(("WARN", ref, it["line"], "%s is %d words: over the %d-word limit of a %s map — split it into one item for each claim" %
                                     (it["kind"], nwords, SUMMARY_WARN_WORDS[depth], depth)))
                elif nwords < SUMMARY_MIN_WORDS[depth]:
                    problems.append(("WARN", ref, it["line"], "%s is only %d words: an item says who, what, and on what ground" % (it["kind"], nwords)))
                unpointed = []
                for cite in it["sources"]:
                    alias, loc = cite["alias"], cite["loc"]
                    if cite["bad"]:
                        problems.append(("ERROR", ref, it["line"], "cannot read the citation %r (write work¶3-5, or work@V¶3-5 for the passage under verse V)" % cite["raw"]))
                        continue
                    if alias not in ALIASES:
                        problems.append(("ERROR", ref, it["line"], "unknown work %r in the item's brackets" % alias))
                        continue
                    used.add(alias)
                    stats["sources"][alias] = stats["sources"].get(alias, 0) + 1
                    target = (v or 1) if loc is None else loc
                    if target < 1 or target > count:
                        problems.append(("ERROR", ref, it["line"], "%s@%s: no such verse in this sūrah" % (alias, loc)))
                        continue
                    text = passage(alias, target)
                    if digest is not None and not text:
                        problems.append(("ERROR", ref, it["line"], "%s cites a passage under %d:%d, but that work has no text there" % (alias, chapter, target)))
                    elif text and cite["spec"]:
                        note(cited, alias, text, cite["spec"], ref, it["line"], cite["raw"], item=True)
                    if not cite["spec"]:
                        unpointed.append(cite["raw"])
                if unpointed and depth == "full":
                    problems.append(("ERROR", ref, it["line"], "a full map cites paragraphs — add ¶ to: %s" % ", ".join(unpointed)))
                for c2, v2 in XREF_RE.findall(it["summary"]):
                    c2, v2 = int(c2), int(v2)
                    if not 1 <= c2 <= 114 or not 1 <= v2 <= C.verse_count(c2):
                        problems.append(("ERROR", ref, it["line"], "%d:%d is not a verse of the Qur'an" % (c2, v2)))
                if it["kind"] == "quran" and not XREF_RE.search(it["summary"]):
                    problems.append(("WARN", ref, it["line"], "a quran item should give the verse it cross-refers to (C:V)"))
                if it["kind"] == "hadith" and not A.COLLECTIONS.search(it["summary"]):
                    problems.append(("WARN", ref, it["line"], "a hadith names its collection (the commentary must) — none found; is it an athar or a lesson?"))
                if it["kind"] == "athar" and not (A.FIRST_GEN.search(it["summary"]) or A.SCHOLARS.search(it["summary"]) or ATHAR_AUTHORITY.search(it["summary"])):
                    problems.append(("WARN", ref, it["line"], "an athar names its authority — none found"))
        for entry in block["aside"]:
            alias, loc = entry["alias"], entry["loc"]
            if alias not in ALIASES:
                problems.append(("ERROR", ref, entry["line"], "unknown work %r in 'Set aside'" % alias))
                continue
            target = (v or 1) if loc is None else loc
            if target < 1 or target > count:
                problems.append(("ERROR", ref, entry["line"], "%s@%s: no such verse in this sūrah" % (alias, loc)))
                continue
            text = passage(alias, target)
            if digest is not None and not text:
                problems.append(("ERROR", ref, entry["line"], "%s is set aside under %d:%d, but that work has no text there" % (alias, chapter, target)))
            elif text:
                note(aside, alias, text, entry["spec"], ref, entry["line"], entry["raw"])
            if not entry["reason"]:
                problems.append(("WARN", ref, entry["line"], "%s is set aside without a reason — say why in brackets" % entry["raw"]))
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
    if digest is not None:
        cov = {}
        seen = set()
        for v in range(1, count + 1):
            for slug, text in (digest.get(str(v)) or {}).items():
                alias, text = SLUG_ALIAS.get(slug), (text or "").strip()
                if not alias or not text or (alias, text) in seen:
                    continue
                seen.add((alias, text))
                row = cov.setdefault(alias, {"paras": 0, "trivial": 0, "cited": 0, "aside": 0, "missing": 0, "chars": 0,
                                             "cited_chars": 0, "aside_chars": 0, "gaps": []})
                got, put = cited.get((alias, text), set()), aside.get((alias, text), set())
                for i, unit in enumerate(units_of(text)):
                    body = unit[2]
                    if is_trivial(body):
                        row["trivial"] += 1
                        continue
                    row["paras"] += 1
                    row["chars"] += len(body)
                    if i in got:
                        row["cited"] += 1
                        row["cited_chars"] += len(body)
                        if i in put:
                            problems.append(("WARN", str(chapter), 0, "%s¶%s (the passage under %d:%d) is both cited and set aside" % (alias, label(unit), chapter, v)))
                    elif i in put:
                        row["aside"] += 1
                        row["aside_chars"] += len(body)
                    else:
                        row["missing"] += 1
                        row["gaps"].append((v, i, label(unit), body))
        stats["coverage"] = cov
        missing = sum(r["missing"] for r in cov.values())
        all_chars = sum(r["chars"] for r in cov.values())
        aside_chars = sum(r["aside_chars"] for r in cov.values())
        if missing and depth == "full" and not pending:
            for alias in sorted(cov):
                gaps = cov[alias]["gaps"]
                if gaps:
                    where = {}
                    for v0, i, lab, _ in gaps:
                        where.setdefault(v0, []).append((i, lab))
                    shown = "; ".join("%s%s" % (("under %d:%d " % (chapter, v0)) if len(where) > 1 else "", compress_units(labs))
                                      for v0, labs in sorted(where.items()))
                    problems.append(("ERROR", str(chapter), 0, "%s: %d unit(s) not accounted for — %s (cite them, or list them under 'Set aside' with a reason)" % (
                        alias, len(gaps), shown if len(shown) < 400 else shown[:400] + " …")))
        elif missing:
            problems.append(("INFO", str(chapter), 0, "%d unit(s) are not yet accounted for%s" % (
                missing, " (the chapter is still being mapped; the paragraph rule applies once the last verse is in)" if pending else " (a survey map does not carry the paragraph rule)")))
        if depth == "full" and all_chars and aside_chars / all_chars > ASIDE_SHARE_WARN:
            problems.append(("WARN", str(chapter), 0, "%.0f%% of the source text is set aside (limit %.0f%%): a full map carries the evidence, it does not shelve it" % (
                100 * aside_chars / all_chars, 100 * ASIDE_SHARE_WARN)))
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
        cov = (stats or {}).get("coverage")
        if cov:
            print("\n  coverage — each work's distinct passages, unit by unit (a unit is a paragraph, or a chunk of a paragraph over %d characters; under %d letters = heading, exempt)" % (SPLIT_OVER, TRIVIAL_LETTERS))
            print("  %-10s %6s %6s %6s %8s %9s %8s" % ("work", "units", "cited", "aside", "missing", "chars", "cited%"))
            tot = {"paras": 0, "cited": 0, "aside": 0, "missing": 0, "chars": 0, "cited_chars": 0, "aside_chars": 0}
            for alias in ALIASES:
                r = cov.get(alias)
                if not r:
                    continue
                for k in tot:
                    tot[k] += r[k]
                print("  %-10s %6d %6d %6d %8d %9s %7.0f%%" % (alias, r["paras"], r["cited"], r["aside"], r["missing"],
                                                              "{:,}".format(r["chars"]), 100.0 * r["cited_chars"] / r["chars"] if r["chars"] else 0))
            print("  %-10s %6d %6d %6d %8d %9s %7.0f%%   (set aside: %.1f%% of the text)" % (
                "all", tot["paras"], tot["cited"], tot["aside"], tot["missing"], "{:,}".format(tot["chars"]),
                100.0 * tot["cited_chars"] / tot["chars"] if tot["chars"] else 0,
                100.0 * tot["aside_chars"] / tot["chars"] if tot["chars"] else 0))
            if args.gaps:
                for alias in ALIASES:
                    for v0, i, lab, body in (cov.get(alias) or {}).get("gaps", []):
                        print("    %s¶%s (under %d:%d, %d c) %s" % (alias, lab, n, v0, len(body), body[:90].replace("\n", " ")))
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
    r.add_argument("--full", action="store_true", help="every paragraph of every work, no cap (paragraphs are numbered from 1)")
    r.add_argument("--force", action="store_true", help="print a whole-sūrah passage again under every verse")
    r.add_argument("--only", help="only these works, e.g. kathir,maarif")
    r.add_argument("--find", metavar="TEXT", help="list the paragraphs that contain TEXT (to locate a verse inside a whole-sūrah passage)")
    r.add_argument("--para", nargs="+", metavar="WORK:IDX[,IDX]", help="print chosen paragraphs in full, e.g. qurtubi:3,4")
    c = sub.add_parser("check", help="validate evidence/NNN.md")
    c.add_argument("chapter", type=int, nargs="?")
    c.add_argument("--all", action="store_true")
    c.add_argument("--strict", action="store_true", help="warnings fail too")
    c.add_argument("--gaps", action="store_true", help="list each paragraph not yet accounted for, with its opening")
    args = ap.parse_args(argv)
    if args.cmd == "check" and not args.all and not args.chapter:
        ap.error("name a chapter or use --all")
    return cmd_read(args) if args.cmd == "read" else cmd_check(args)


if __name__ == "__main__":
    raise SystemExit(main())
