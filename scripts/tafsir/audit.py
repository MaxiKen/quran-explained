#!/usr/bin/env python3
"""audit.py — the gate every generated chapter must pass.

    python3 scripts/tafsir/audit.py 1              # audit tafsir/001.md
    python3 scripts/tafsir/audit.py 1 --json       # machine-readable findings
    python3 scripts/tafsir/audit.py --all          # corpus overview + failures
    python3 scripts/tafsir/audit.py 1 --strict     # warnings become failures
    python3 scripts/tafsir/audit.py 1 --no-grounding

Exit status is 0 only when there are no FAIL findings (and, under ``--strict``,
no WARN either). The rule set is written out in TAFSIR_PROMPT.md; the codes
below are the same rules, mechanised:

  FMT-*   shape: title, intro, verse headings, quote line, separators, spacing,
          headings per verse, placeholders
  WRD-*   length: verse and introduction word floors/ceilings
  EVD-*   evidence: every verse carries at least one checkable anchor, and every
          prophetic attribution names its collection
  REF-*   references: citations resolve to real verses, every quoted Qur'an
          clause is verbatim from data/chapter_NNN.js, quoting style is kept
  REP-*   repetition: duplicate sentences, templated sections, filler/meta prose
  GRD-*   grounding (advisory): distinctive names in a section should appear in
          that verse's source digest (tmp/sources/NNN.json, built by sources.py)

Grounding is the only check that needs a generated file; all the others run on
the chapter alone, so the gate works in CI and on a chapter written from the
sources by hand.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"

# ------------------------------------------------------------------ thresholds

MIN_VERSE_WORDS = 150
MAX_VERSE_WORDS = 650          # soft: points at a section that has drifted long
MIN_HEADINGS = 2
MAX_HEADINGS = 6               # soft
MIN_INTRO_WORDS = 200
MAX_INTRO_WORDS = 900
MIN_SENTENCE_WORDS = 10        # shortest sentence that counts as a duplicate
TEMPLATE_FAIL = 0.30           # 8-gram overlap between two verse sections
TEMPLATE_WARN = 0.18
GROUNDING_MIN_TOKENS = 5
GROUNDING_MISS_RATIO = 0.50    # advisory only

# --------------------------------------------------------------- rule patterns

COLLECTIONS = re.compile(
    r"(Bukh[\u0101a]r[\u012bi]|Muslim|Tirmidh[\u012bi]|Nas[\u0101a][\u02be']?[\u012bi]|"
    r"Ab[\u016b] D[\u0101a]w[\u016b]d|Ibn M[\u0101a]jah|A[\u1e25h]mad|Muwa[\u1e6d\u1e6d]a|"
    r"D[\u0101a]rim[\u012bi]|Bayhaq[\u012bi]|[\u1e6cT]abar[\u0101a]n[\u012bi]|Ibn H[\u1e25i]bb[\u0101a]n|"
    r"Ibn Khuzaymah|[\u1e24H][\u0101a]kim|Ab[\u016b] Nu[\u02bf']aym|Sunan|Musnad|\u1e62a\u1e25\u012b\u1e25)",
    re.I)

SCHOLARS = re.compile(
    r"(Ibn Kath[\u012bi]r|Ibn Kathir|[\u1e6cT]abar[\u012bi]|Tabari|Qur[\u1e6d]ub[\u012bi]|Qurtubi|"
    r"al-R[\u0101a]z[\u012bi]|al-Razi|Baghaw[\u012bi]|Baghawi|Sa[\u02bf']d[\u012bi]|al-Saadi|"
    r"Zamakhshar[\u012bi]|Bay[\u1e0d][\u0101a]w[\u012bi]|Nasaf[\u012bi]|Ibn [\u02bf']Abb[\u0101a]s|Ibn Abbas|"
    r"Ibn [\u02bf']Umar|Ibn [\u02bf']Ubayd|Ibn Mas[\u02bf']\u016bd|Muj[\u0101a]hid|Qat[\u0101a]dah|"
    r"Sudd[\u012bi]|[\u02bf']Ikrimah|\u1e0ca[\u1e25h][\u1e25h][\u0101a]k|Jal[\u0101a]layn|Suy[\u016b][\u1e6d][\u012bi]|"
    r"Maud[\u016b]d[\u012bi]|Maududi|Y[\u016bs]uf [\u02bf']Al[\u012bi]|Qushayr[\u012bi]|Tustar[\u012bi]|"
    r"K[\u0101a]sh[\u0101a]n[\u012bi]|Ibn [\u02bf']Uthaym[\u012bn]n|Shawk[\u0101a]n[\u012bi]|W[\u0101a][\u1e25h]id[\u012bi]|"
    r"[\u1e24H]asan al-Ba[\u1e63]r[\u012bi]|M[\u0101a]lik|Ibn Taymiyyah|Ibn al-Qayyim|R[\u0101a]ghib|"
    r"the commentators|the exegetes|the scholars|commentators)",
    re.I)

LANGUAGE = re.compile(
    r"(\broot\b|\bthe word\b|\bArabic\b|\bliterally\b|\bgrammatically\b|\bgrammar\b|"
    r"\bthe (verb|noun|participle|plural|singular|dual)\b|\breading\b|\brecitation\b|"
    r"\bpronoun\b|\bpreposition\b|\btranslated\b|\btranslation\b|\bmeans\b)",
    re.I)

QURAN_QUOTE = re.compile(
    r"\((\d{1,3}):(\d{1,3})(?:\s*[\u2013\u2014-]\s*(\d{1,3}))?"
    r"(?:\s*,\s*(\d{1,3}):(\d{1,3}))?"
    r"\s*\u2014\s*\*[\u201c](.+?)[\u201d]\*\)",
    re.S)

BARE_REF = re.compile(r"\((\d{1,3}):(\d{1,3})(?:\s*[\u2013\u2014-]\s*(\d{1,3}))?(?:\s*,\s*\d{1,3}:\d{1,3})*\)")

CURLY_ONLY_QUOTE = re.compile(r"\*[\u201c]([^\u201d]{8,})[\u201d]\*")
STRAIGHT_IN_ITALIC = re.compile(r"\*\"([^\"]{8,})\"\*")

FILLER = [
    (FAIL, r"\bthis (section|file|document|draft|commentary|payload)\b", "process leakage: write about the verse, not the document"),
    (FAIL, r"\bin this chapter we\b", "process leakage"),
    (FAIL, r"\bas (we|I) (have )?(seen|said|noted|mentioned|discussed)\b", "cross-reference to our own text instead of the Qur'an"),
    (FAIL, r"\bthe (audit|prompt|generator|source digest|worklog)\b", "pipeline vocabulary in reader-facing prose"),
    (FAIL, r"\b(source digest|audit\.py|TAFSIR_PROMPT)\b", "pipeline vocabulary in reader-facing prose"),
    (FAIL, r"\bTODO\b|\bTBD\b|PLACEHOLDER|to be written|lorem ipsum", "placeholder text"),
    (FAIL, r"\bas an ai\b|\blanguage model\b", "machine voice"),
    (FAIL, r"\bit is worth noting\b|\bit'?s worth noting\b|\bit is important to note\b", "filler opener"),
    (FAIL, r"\bin conclusion\b|\bto sum up\b|\bto summarize\b", "filler closer"),
    (FAIL, r"\blet us (now )?(look|examine|consider|turn)\b|\bwe (will|shall) (now )?(see|explore|examine|look at)\b", "filler address to the reader"),
    (WARN, r"\bdelve[sd]? into\b|\brich tapestry\b|\bstands as a testament\b|\btestament to\b", "cliche"),
    (WARN, r"\bnavigate the complexities\b|\bunderscores the importance\b|\bplays a (crucial|vital) role\b", "cliche"),
    (WARN, r"\bthroughout history\b|\bsince time immemorial\b|\bcountless generations\b", "vague generality"),
]

PROPHET_REF = re.compile(
    r"(\bthe Prophet\b(?!s)|\uFDFA|\bthe Messenger of (?:Allah|God)\b|\bAllah[\u2019']s Messenger\b)")

GENERIC_HEADINGS = {
    "commentary", "explanation", "introduction", "overview", "summary",
    "lesson", "lessons", "note", "notes", "conclusion", "reflection",
    "reflections", "analysis", "discussion", "context", "background", "the verse",
}



class Finding:
    __slots__ = ("level", "code", "ref", "line", "message")

    def __init__(self, level, code, ref, line, message):
        self.level, self.code, self.ref, self.line, self.message = level, code, ref, line, message


def _strip_marks(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    for a, b in (("\u02bf", "'"), ("\u02be", "'"), ("\u2019", "'"), ("\u2018", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u1e6d", "t"), ("\u1e63", "s"),
                 ("\u1e25", "h"), ("\u1e0d", "d"), ("\u1e93", "z")):
        text = text.replace(a, b)
    return text


def _canon(text: str) -> str:
    return re.sub(r"\s+", " ", _strip_marks(text)).strip().lower()


# ------------------------------------------------------------------- the checks


def audit_chapter(chapter: int, opts) -> list:
    findings = []
    path = C.output_path(chapter)

    def fail(code, ref, line, msg):
        findings.append(Finding(FAIL, code, ref, line, msg))

    def warn(code, ref, line, msg):
        findings.append(Finding(WARN, code, ref, line, msg))

    def info(code, ref, line, msg):
        findings.append(Finding(INFO, code, ref, line, msg))

    if not path.exists():
        fail("FMT-FILE", "%d" % chapter, 0, "tafsir/%s.md does not exist" % C.pad3(chapter))
        return findings

    raw = path.read_text(encoding="utf-8")
    lines = raw.split("\n")
    doc = C.ChapterDoc(chapter, path, raw)

    # -------- shape of the file ------------------------------------------------
    if doc.title != C.title_line(chapter):
        fail("FMT-TITLE", "%d" % chapter, 1,
             "title must be exactly: %s (found: %s)" % (C.title_line(chapter), doc.title[:80]))

    if doc.intro_heading_line is None:
        fail("FMT-INTRO", "%d" % chapter, 0, "missing '%s'" % C.INTRO_HEADING)
    else:
        if doc.intro_heading_line != 3:
            fail("FMT-INTRO-POS", "%d" % chapter, doc.intro_heading_line,
                 "the introduction heading belongs on line 3, after the title and one blank line")
        intro_words = doc.words(doc.intro)
        if not doc.intro:
            fail("FMT-INTRO-EMPTY", "%d" % chapter, doc.intro_heading_line, "empty introduction")
        elif intro_words < MIN_INTRO_WORDS:
            fail("WRD-INTRO", "%d" % chapter, doc.intro_heading_line,
                 "introduction is %d words (floor %d)" % (intro_words, MIN_INTRO_WORDS))
        elif intro_words > MAX_INTRO_WORDS:
            warn("WRD-INTRO", "%d" % chapter, doc.intro_heading_line,
                 "introduction is %d words (soft ceiling %d)" % (intro_words, MAX_INTRO_WORDS))
        if re.search(r"(?m)^\*\*", doc.intro):
            warn("FMT-INTRO-HEADINGS", "%d" % chapter, doc.intro_heading_line,
                 "the introduction is plain paragraphs, with no **headings** inside it")
        if re.search(r"\n---", doc.intro):
            fail("FMT-INTRO-SEP", "%d" % chapter, doc.intro_heading_line,
                 "a '---' separator appears inside the introduction")

    # every verse present exactly once, in order
    expected = [v["ayah_no_surah"] for v in C.verses(chapter)]
    found = [s.verse for s in doc.sections]
    if found != expected:
        missing = [v for v in expected if v not in found]
        extra = [v for v in found if v not in expected]
        dupes = sorted({v for v in found if found.count(v) > 1})
        detail = []
        if missing:
            detail.append("missing %s" % ", ".join(map(str, missing[:12])))
        if extra:
            detail.append("not a verse of this chapter: %s" % ", ".join(map(str, extra[:12])))
        if dupes:
            detail.append("duplicated %s" % ", ".join(map(str, dupes[:12])))
        if found != sorted(found):
            detail.append("out of order")
        fail("FMT-VERSES", "%d" % chapter, 0,
             "verse headings must run 1..%d, ascending, one each (%s)" % (len(expected), "; ".join(detail)))

    # per-section checks
    all_sentences = defaultdict(list)          # normalised sentence -> [(ref, line, text)]
    quotes_seen = defaultdict(list)            # canonical wording -> refs

    for section in doc.sections:
        ref = section.ref
        anchor = section.start

        # heading line, quote line, spacing
        after_heading = section.lines[1] if len(section.lines) > 1 else ""
        if after_heading.strip() != "":
            fail("FMT-SPACING", ref, anchor + 1, "blank line required after the verse heading")
        quote_len = section.quote_lines()
        if quote_len == 0:
            fail("FMT-QUOTE", ref, anchor, "missing the '> ...' verse line")
        else:
            if quote_len > 1:
                fail("FMT-QUOTE-LINES", ref, anchor + 1,
                     "the verse quote is one line (found %d '>' lines)" % quote_len)
            canonical = C.ayah_en(chapter, section.verse)
            if C._norm_space(section.quote()) != C._norm_space(canonical):
                fail("FMT-QUOTE-VERBATIM", ref, anchor + 1,
                     "quote is not the canonical translation from data/chapter_%s.js: %r"
                     % (C.pad3(chapter), section.quote()[:90]))
            else:
                quotes_seen[C._norm_space(canonical)].append(ref)
            last_quote = max(i for i, l in enumerate(section.lines[1:], start=1) if l.startswith(">"))
            after_quote = section.lines[last_quote + 1] if last_quote + 1 < len(section.lines) else ""
            if after_quote.strip() != "":
                fail("FMT-SPACING", ref, anchor + last_quote + 1,
                     "blank line required after the verse quote")

        body = section.body()
        body_words = doc.words(body)
        if body_words < MIN_VERSE_WORDS:
            fail("WRD-FLOOR", ref, anchor, "verse tafsir is %d words (floor %d)" % (body_words, MIN_VERSE_WORDS))
        elif body_words > MAX_VERSE_WORDS:
            warn("WRD-CEILING", ref, anchor, "verse tafsir is %d words (soft ceiling %d)" % (body_words, MAX_VERSE_WORDS))
        if re.search(r"\bTODO\b|\bTBD\b|PLACEHOLDER", body):
            fail("FMT-PLACEHOLDER", ref, anchor, "placeholder text left in the section")

        paragraphs = C.split_paragraphs(body)
        if len(paragraphs) < 2:
            fail("FMT-PARAGRAPHS", ref, anchor, "a verse section is at least 2 paragraphs under at least 2 headings")

        # headings
        heads = section.headings()
        if len(heads) < MIN_HEADINGS:
            fail("FMT-HEADINGS", ref, anchor,
                 "%d **heading(s)**: every verse carries at least %d" % (len(heads), MIN_HEADINGS))
        elif len(heads) > MAX_HEADINGS:
            warn("FMT-HEADINGS-COUNT", ref, anchor, "%d headings (soft maximum %d)" % (len(heads), MAX_HEADINGS))

        for idx, (line_no, title) in enumerate(heads):
            i = line_no - 1                                  # 0-based in file
            if i > 0 and lines[i - 1].strip() != "":
                fail("FMT-HEADING-SHAPE", ref, line_no, "blank line required before '%s'" % title)
            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                fail("FMT-HEADING-SHAPE", ref, line_no,
                     "blank line required after '%s' (a heading is its own paragraph)" % title)
            nxt = next((h for h in heads if h[0] > line_no), None)
            end = (nxt[0] - 1) if nxt else section.end
            chunk = "\n".join(lines[line_no:end])
            if not re.search(r"[A-Za-z]", chunk):
                fail("FMT-ORPHAN-HEADING", ref, line_no, "'%s' has no prose under it" % title)
            if title.strip().strip("*").lower() in GENERIC_HEADINGS:
                fail("FMT-HEADING-GENERIC", ref, line_no,
                     "'%s' is a generic heading; make it say what the paragraph says" % title)
        titles = [t.lower() for _, t in heads]
        dupes = sorted({t for t in titles if titles.count(t) > 1})
        if dupes:
            warn("FMT-HEADING-DUP", ref, anchor, "heading repeated in the same section: %s" % ", ".join(dupes))

        # separators: exactly one '---' between sections, never a double blank
        body_lines = section.lines
        sep_count = sum(1 for l in body_lines if l.strip() == "---")
        is_last = section is doc.sections[-1]
        if is_last and sep_count:
            warn("FMT-SEP", ref, anchor, "trailing '---' after the final verse")
        if not is_last and sep_count != 1:
            fail("FMT-SEP", ref, anchor, "expected exactly one '---' before the next verse (found %d)" % sep_count)

        # references and quotations
        for m in QURAN_QUOTE.finditer(body):
            s_ch, s_v = int(m.group(1)), int(m.group(2))
            inner = m.group(5)
            if not _ref_ok(s_ch, s_v):
                fail("REF-RANGE", ref, anchor, "(%d:%d) is not a verse of the Qur'an" % (s_ch, s_v))
                continue
            canonical = _canon(C.ayah_en(s_ch, s_v))
            if _canon(inner) not in canonical:
                fail("REF-QUOTE", ref, anchor,
                     "quot(e) from %d:%d is not verbatim: %r" % (s_ch, s_v, inner[:70]))
            if s_ch == chapter and s_v == section.verse:
                warn("REF-SELF-QUOTE", ref, anchor,
                     "the verse's own wording is already in the line above; cite it without re-quoting")

        for m in BARE_REF.finditer(body):
            s_ch, s_v = int(m.group(1)), int(m.group(2))
            if not _ref_ok(s_ch, s_v):
                fail("REF-RANGE", ref, anchor, "(%d:%d) is not a verse of the Qur'an" % (s_ch, s_v))

        for m in CURLY_ONLY_QUOTE.finditer(body):
            before = body[max(0, m.start() - 45):m.start()]
            if not re.search(r"\d{1,3}:\d{1,3}\s*\u2014\s*$", before):
                warn("REF-UNANCHORED", ref, anchor,
                     "quoted Qur'an clause without its reference beside it: %r" % m.group(1)[:50])

        for m in STRAIGHT_IN_ITALIC.finditer(body):
            inner = _canon(m.group(1))
            if len(inner) > 18 and any(inner in _canon(v["ayah_en"]) for v in C.verses(chapter)):
                fail("REF-STRAIGHT-QUOTE", ref, anchor,
                     "Qur'an wording in hadith-style straight quotes: %r" % m.group(1)[:60])

        # evidence anchors
        kinds = []
        if BARE_REF.search(body):
            kinds.append("quran")
        if COLLECTIONS.search(body):
            kinds.append("hadith")
        if SCHOLARS.search(body):
            kinds.append("scholar")
        if LANGUAGE.search(body):
            kinds.append("language")
        if not kinds:
            fail("EVD-NONE", ref, anchor,
                 "no checkable anchor in the section (no Qur'an cross-reference, hadith, named authority or language note)")
        elif len(kinds) < 2:
            warn("EVD-THIN", ref, anchor, "only one kind of evidence (%s)" % kinds[0])

        # attribution honesty: a prophetic saying must name its collection
        for para in paragraphs:
            for sentence in C.sentence_split(para):
                if PROPHET_REF.search(sentence) \
                        and re.search(r"\b(said|says|reported|narrated|stated|declared|told)\b", sentence, re.I):
                    if not COLLECTIONS.search(sentence) and not COLLECTIONS.search(para):
                        fail("EVD-ATTRIBUTION", ref, anchor,
                             "prophetic report without its collection: %r" % sentence[:90])
                        break

        # grounding: distinctive names should exist in this verse's sources
        if not opts.no_grounding:
            missing = _ungrounded(body, chapter, section.verse, opts)
            if missing:
                warn("GRD-TOKENS", ref, anchor,
                     "%d named/foreign terms not found in this verse's sources (check them): %s"
                     % (len(missing), ", ".join(sorted(missing)[:8])))

        # repetition inside the chapter
        for para in paragraphs:
            for sentence in C.sentence_split(para):
                key = C.norm_key(sentence)
                if len(key.split()) >= MIN_SENTENCE_WORDS:
                    all_sentences[key].append((ref, anchor, sentence))

    for key, hits in all_sentences.items():
        if len(hits) > 1:
            refs = ", ".join(sorted({h[0] for h in hits}, key=lambda r: (r.split(":")[0], r.split(":")[1])))
            fail("REP-SENTENCE", hits[1][0], hits[1][1],
                 "the same sentence appears in %s: %r" % (refs, hits[0][2][:80]))

    # templated sections: shared 8-gram shingles between two verse sections
    shing = [(s.ref, s.start, C.shingles(s.body())) for s in doc.sections]
    for i in range(len(shing)):
        for j in range(i + 1, len(shing)):
            a, b = shing[i][2], shing[j][2]
            if not a or not b:
                continue
            overlap = len(a & b) / min(len(a), len(b))
            if overlap > TEMPLATE_FAIL:
                fail("REP-TEMPLATE", shing[j][0], shing[j][1],
                     "%.0f%% of this section's phrasing also appears in %s" % (overlap * 100, shing[i][0]))
            elif overlap > TEMPLATE_WARN:
                warn("REP-TEMPLATE", shing[j][0], shing[j][1],
                     "%.0f%% overlap with %s" % (overlap * 100, shing[i][0]))

    # filler / meta vocabulary, file-wide (so it is caught even in the intro)
    body_text = "\n".join(s.body() for s in doc.sections)
    for level, pattern, why in FILLER:
        for m in re.finditer(pattern, raw, re.I):
            line_no = raw[:m.start()].count("\n") + 1
            text = m.group(0)
            (fail if level == FAIL else warn)("REP-FILLER", str(chapter), line_no,
                                              "%s: %r" % (why, text))
            break            # one report per pattern is enough

    # whitespace and file hygiene
    if "\t" in raw:
        fail("FMT-WHITESPACE", str(chapter), raw[:raw.index("\t")].count("\n") + 1, "tab character")
    for i, line in enumerate(lines):
        if line != line.rstrip():
            fail("FMT-WHITESPACE", str(chapter), i + 1, "trailing whitespace")
            break
    m = re.search(r"\n{3,}", raw)
    if m:
        fail("FMT-WHITESPACE", str(chapter), raw[:m.start()].count("\n") + 2, "more than one blank line in a row")
    if not raw.endswith("\n"):
        fail("FMT-WHITESPACE", str(chapter), len(lines), "file must end with a single newline")
    elif raw.endswith("\n\n"):
        fail("FMT-WHITESPACE", str(chapter), len(lines), "file ends with a blank line")

    # a quote repeated many times is a sign of padding
    for wording, refs in quotes_seen.items():
        if len(refs) > 4:
            warn("REP-QUOTE", refs[4], 0, "the same wording is quoted %d times (%s)" % (len(refs), ", ".join(refs[:6])))

    return findings


def _ref_ok(chapter: int, verse: int) -> bool:
    if not (1 <= chapter <= 114) or verse < 1:
        return False
    try:
        return verse <= C.verse_count(chapter)
    except Exception:
        return False


_DIGESTS = {}


def _digest(chapter: int):
    if chapter not in _DIGESTS:
        p = C.TMP_DIR / "sources" / ("%s.json" % C.pad3(chapter))
        _DIGESTS[chapter] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    return _DIGESTS[chapter]


_STOP = {"the", "a", "an", "and", "but", "for", "with", "this", "that", "these", "those",
         "god", "allah", "quran", "qur'an", "verse", "surah", "surahs", "chapter", "he",
         "she", "they", "it", "his", "her", "their", "its", "who", "which", "when", "then",
         "so", "not", "no", "all", "one", "two", "day", "people"}


def _ungrounded(body: str, chapter: int, verse: int, opts):
    digest = _digest(chapter)
    if not digest:
        return set()
    sources = digest.get(str(verse)) or {}
    if not sources:
        return set()
    haystack = _canon("\n".join(sources.values()))

    tokens = set()
    for para in C.split_paragraphs(body):
        for m in re.finditer(r"\b[A-Z][A-Za-z\u0100-\u024f\u1e00-\u1eff'\u02bf-]{2,}\b", para):
            token = m.group(0)
            if para[max(0, m.start() - 2):m.start()].endswith((". ", "? ", "! ")):
                continue
            if token.lower() in _STOP:
                continue
            tokens.add(token)
        for m in re.finditer(r"\*([A-Za-z\u0100-\u024f\u1e00-\u1eff'\u02bf-]{4,})\*", para):
            tokens.add(m.group(1))
    if len(tokens) < GROUNDING_MIN_TOKENS:
        return set()
    absent = {t for t in tokens if _canon(t) not in haystack}
    if len(absent) / len(tokens) >= GROUNDING_MISS_RATIO:
        return absent
    return set()


# ----------------------------------------------------------------------- report


def report(chapter, findings, show_info=False, stream=sys.stdout):
    order = {FAIL: 0, WARN: 1, INFO: 2}
    findings = sorted(findings, key=lambda f: (order[f.level], f.line, f.code))
    counts = defaultdict(int)
    for f in findings:
        counts[f.level] += 1
    shown = 0
    for f in findings:
        if f.level == INFO and not show_info:
            continue
        loc = "L%-4d" % f.line if f.line else "     "
        print("%-4s %-18s %-6s %s %s" % (f.level, f.code, f.ref, loc, f.message), file=stream)
        shown += 1
    if not shown:
        print("clean", file=stream)
    print("", file=stream)
    print("chapter %s: %d FAIL, %d WARN, %d INFO"
          % (C.pad3(chapter), counts[FAIL], counts[WARN], counts[INFO]), file=stream)
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", nargs="?", type=int)
    ap.add_argument("--all", action="store_true", help="audit every chapter file that exists")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warnings fail the gate")
    ap.add_argument("--no-grounding", action="store_true")
    ap.add_argument("--show-info", action="store_true")
    args = ap.parse_args(argv)

    if args.json:
        args.show_info = True

    if args.all or args.chapter is None:
        total = defaultdict(int)
        bad = []
        rows = []
        for n in C.chapter_numbers():
            if not C.output_path(n).exists():
                rows.append((n, None, None))
                continue
            findings = audit_chapter(n, args)
            c = defaultdict(int)
            for f in findings:
                c[f.level] += 1
            for k, v in c.items():
                total[k] += v
            rows.append((n, c, findings))
        if args.json:
            out = []
            for n, c, findings in rows:
                if findings is None:
                    out.append({"chapter": n, "present": False})
                    continue
                out.append({"chapter": n, "present": True,
                            "fail": c[FAIL], "warn": c[WARN],
                            "findings": [f.__dict__ for f in findings]})
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            done = sum(1 for _, c, _ in rows if c is not None)
            for n, c, findings in rows:
                if c is None:
                    print("%s  \u2014 not written" % C.pad3(n))
                    continue
                marks = [f for f in findings if f.level == FAIL or (args.strict and f.level == WARN)]
                status = "PASS" if not marks else "FAIL"
                print("%s  %-4s  %2d fail  %2d warn  %s"
                      % (C.pad3(n), status, c[FAIL], c[WARN],
                         "" if not marks else "; ".join(sorted({f.code for f in marks})[:6])))
                bad.extend(marks)
            print("")
            print("chapters written: %d/114 | FAIL %d | WARN %d" % (done, total[FAIL], total[WARN]))
        failing = total[FAIL] + (total[WARN] if args.strict else 0)
        return 1 if failing else 0

    findings = audit_chapter(args.chapter, args)
    if args.json:
        print(json.dumps([f.__dict__ for f in findings], ensure_ascii=False, indent=2))
    else:
        counts = report(args.chapter, findings, args.show_info)
        if counts[FAIL] == 0:
            print("RESULT: PASS \u2014 chapter %s meets the format and evidence rules" % C.pad3(args.chapter))
            if counts[WARN]:
                print("        (%d warnings to read before committing)" % counts[WARN])
    bad = sum(1 for f in findings if f.level == FAIL or (args.strict and f.level == WARN))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
