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
          UPPERCASE descriptive headings (never the verse's own phrases), placeholders
  WRD-*   length: verse floor (max(600, 8x the verse's words), capped 4,000), introduction
  PHR-*   phrases: every phrase of the verse is quoted inside the prose, in
          verse order, covering the whole verse, in workable units, and each
          quoted phrase is backed by evidence (a cross-reference, a hadith, a
          named authority) in its own paragraph
  EVD-*   evidence: every verse carries checkable anchors, and every prophetic
          attribution names its collection
  REF-*   references: citations resolve to real verses and every quoted Qur'an
          clause is verbatim from data/chapter_NNN.js
  REP-*   repetition: duplicate sentences, templated sections, filler/meta prose
  STY-*   style: simple diction, sentence length and readability, the relatable
          analogy the prompt asks each verse to carry, and no labelled
          scaffolding (STY-LABELS: "Lesson:", "Modern application:", ...)
  SRC-*   sources: the ten works of corpus.SOURCE_ALLOWLIST — the digest must
          hold every one of them for the verse before it is written
          (SRC-NOTCHECKED, SRC-NODIGEST), the prose must name at least five of
          the ten with at least one classical and one modern (SRC-SPREAD,
          SRC-FAMILY), no work outside the ten may be cited (SRC-BANNED), and a
          chapter that never names one of the ten is flagged (SRC-UNUSED)
  GRD-*   grounding (advisory): distinctive names in a section should appear in
          that verse's source digest (tmp/sources/NNN.json, built by sources.py)

Grounding is the only check that needs a generated file; all the others run on
the chapter alone, so the gate works in CI and on a chapter written from the
sources by hand.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"

# ------------------------------------------------------------------ thresholds

MIN_VERSE_WORDS = 600          # hard floor for every verse, however short
SCALE_FACTOR = 8.0             # ... and the floor climbs with the verse
SCALE_CAP = 4000               # ... up to here (a long verse floors at four thousand)
MAX_VERSE_WORDS = 5000         # soft: above this, check for padding
MAX_HEADINGS = 30              # soft
MIN_INTRO_WORDS = 250
MAX_INTRO_WORDS = 1500         # soft
MIN_SENTENCE_WORDS = 10        # shortest sentence that counts as a duplicate
TEMPLATE_FAIL = 0.30           # 8-gram overlap between two verse sections
TEMPLATE_WARN = 0.18
GROUNDING_MIN_TOKENS = 5
GROUNDING_MISS_RATIO = 0.50    # advisory only

PHRASE_COVERAGE_MIN = 0.90     # share of the verse's words the prose must quote
PHRASE_GAP_MAX = 8             # words a single unquoted gap may run to
PHRASE_EDGE_MAX = 3            # words left unquoted at the start or end
PHRASE_RUN_FAIL = 0.65         # share of a >=12-word verse one quoted run may swallow
PHRASE_RUN_WARN = 0.40
PHRASE_RUN_MIN_WORDS = 12
HEADING_VERSE_RUN_FAIL = 6     # words a heading may repeat from the verse before it is a copy
HEADING_VERSE_RUN_WARN = 4
HEADING_MAX_WORDS = 12

ANALOGY_MIN_SHARE = 0.40       # chapter FAIL below this share of verses
ANALOGY_WARN_SHARE = 0.60

MEAN_SENTENCE_FAIL = 32.0
MEAN_SENTENCE_WARN = 26.0
LONG_SENTENCE_FAIL = 0.25
LONG_SENTENCE_WARN = 0.12
FLESCH_FAIL = 45.0
FLESCH_WARN = 55.0
LONG_WORD_WARN = 0.02

# --------------------------------------------------------------- rule patterns

COLLECTIONS = re.compile(
    r"(Bukh[\u0101a]r[\u012bi]|Muslim|Tirmidh[\u012bi]|Nas[\u0101a][\u02be']?[\u012bi]|"
    r"Ab[\u016b] D[\u0101a]w[\u016b]d|Ibn M[\u0101a]jah|A[\u1e25h]mad|Muwa[\u1e6d\u1e6d]a|"
    r"D[\u0101a]rim[\u012bi]|Bayhaq[\u012bi]|[\u1e6cT]abar[\u0101a]n[\u012bi]|Ibn H[\u1e25i]bb[\u0101a]n|"
    r"Ibn Khuzaymah|[\u1e24H][\u0101a]kim|Ab[\u016b] Nu[\u02bf']aym|Sunan|Musnad|\u1e62a\u1e25\u012b\u1e25|"
    r"Forty Hadith|al-Arba[\u02bf']\u016bn|J[\u0101a]mi[\u02bf']|Mu[\u02bf']jam|Kanz)",
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
    r"the commentators|the exegetes|the scholars|commentators|"
    r"al-Mukhta[\u1e63]ar|Mukhta[\u1e63]ar|Mukhtasar|Kash[\u0101a]n[\u012bi]|Kashani|"
    r"Ma[\u02bf']\u0101rif|Ma[\u02bf']arif|Tazkirul|Tazkir|tafsir_initial|Qushayr[\u012bi]|"
    r"Tustar[\u012bi]|R[\u016b]h al-Ma[\u02bf']\u0101n[\u012bi])",
    re.I)

LANGUAGE = re.compile(
    r"(\broot\b|\bthe word\b|\bArabic\b|\bliterally\b|\bgrammatically\b|\bgrammar\b|"
    r"\bthe (verb|noun|participle|plural|singular|dual)\b|\breading\b|\brecitation\b|"
    r"\bpronoun\b|\bpreposition\b|\btranslated\b|\btranslation\b|\bmeans\b)",
    re.I)

# ---- the ten sources (corpus.SOURCE_ALLOWLIST) ------------------------------
# Which name in the prose proves which work was consulted. The prose says
# "al-Tabari states", not "the source", and names are the only checkable trace.
AUTHORITY = {
    "tafsir-al-tabari": re.compile(r"(\b[T\u1e6c]abar[\u012bi]\b|\bTabari\b|J[\u0101a]mi[\u02bf'] al-Bay[\u0101a]n)", re.I),
    "tafsir-al-qurtubi": re.compile(r"(Qur[\u1e6d]ub[\u012bi]|Qurtubi)", re.I),
    "tafsir-al-baghawi": re.compile(r"(Baghaw[\u012bi]|Baghawi|Ma[\u02bf']\u0101lim al-Tanz[\u012bi]l)", re.I),
    "tafsir-ibn-kathir": re.compile(r"(Ibn Kath[\u012bi]r|Ibn Kathir)", re.I),
    "tafsir-al-alusi": re.compile(r"(al-[\u02be']?Al[\u016bs]i|R[\u016b]h al-Ma[\u02bf']\u0101n[\u012bi])", re.I),
    "tafsir-al-jalalayn": re.compile(r"(al-Jal[\u0101a]layn|Jal[\u0101a]layn|al-Ma[\u1e25h]all[\u012bi] and al-Suy[\u016b][\u1e6d][\u012bi])", re.I),
    "tafsir-ibn-abbas": re.compile(r"(Ibn [\u02bf']Abb[\u0101a]s|Ibn Abbas)", re.I),
    "tafsir-as-saadi": re.compile(r"(al-Sa[\u02bf']d[\u012bi]|Sa[\u02bf']d[\u012bi]|Tays[\u012bi]r al-Kar[\u012bi]m)", re.I),
    "tafsir-ibn-uthaymeen": re.compile(r"(Ibn [\u02bf']Uthaym[\u012bi]n|Ibn Uthaymeen|Ibn 'Uthaymin)", re.I),
    "tafsir-maarif-ul-quran": re.compile(r"(Ma[\u02bf']\u0101rif al-Qur[\u02be']?[\u0101a]n|Maarif-ul-Quran|Ma[\u02bf']\u0101rif)", re.I),
}

# Works that are no longer part of the corpus: naming one means the writer is
# quoting outside the ten.
BANNED_WORKS = re.compile(
    r"(al-Mukhta[\u1e63]ar|Mukhta[\u1e63]ar|Mukhtasar|al-Was[\u012bi][\u1e6d]|Wasit al-Qur|"
    r"al-Bay[\u1e0d][\u0101a]w[\u012bi]|Baydawi|al-Shawk[\u0101a]n[\u012bi]|Shawkani|"
    r"Fat[\u1e25] al-Qad[\u012bi]r|Ab[\u016b] [\u1e24h]ayy[\u0101a]n|Bahr al-Mu[\u1e25]i[\u1e6d]|"
    r"Durr al-Manth[\u016b]r|al-Jaz[\u0101a][\u02be']ir[\u012bi]|Aysar al-Taf[\u0101a]s[\u012bi]r|"
    r"al-Qushayr[\u012bi]|Qushayri|al-Tustar[\u012bi]|Tustari|K[\u0101a]sh[\u0101a]n[\u012bi]|Kashani|"
    r"Kashf al-Asr[\u0101a]r|Tadabbur wa Amal|Tazkirul Qur[\u02be']?[\u0101a]n|Tazkir al-Qur[\u02be']?[\u0101a]n|"
    r"al-W[\u0101a][\u1e25h]id[\u012bi])",
    re.I)

SRC_MIN_CITED = 5              # distinct works of the ten a verse must name
SRC_MIN_CLASSICAL = 1          # ... of which at least one classical
SRC_MIN_MODERN = 1             # ... and at least one modern

# Reader-facing scaffolding: the elements are shown, never labelled.
LABELS = re.compile(
    r"(?:(?<=^)|(?<=[.!?]\s)|(?<=\*\*)|(?<=\n))\s*\**"
    r"(lesson[s]?|application[s]?|analog(?:y|ies)|histor(?:y|ical context|ical background)|"
    r"modern life|modern application|modern discovery|modern science|"
    r"cross[- ]reference[s]?|explanation|simple explanation|takeaway[s]?|"
    r"context|background|ruling[s]?|moral|insight[s]?|note[s]?|element[s]?)\**\s*:",
    re.I)

ANALOGY = re.compile(
    r"(\bimagine\b|\bthink of\b|\bpicture\b|\bis like\b|\blike a\b|\blike the\b|\bas if\b|\bas though\b|"
    r"\bcompare (?:it|this|them|that)\b|\bin the same way\b|\bthe way a\b|\bsimilar to\b|\bmuch like\b|"
    r"\bjust as a\b|\bit is as though\b|\ba good comparison\b|\bthink about\b|\bsuppose you\b)",
    re.I)

DICTION = re.compile(
    r"\b(utilis?e[ds]?|utiliz\w+|endeavour\w*|endeavor\w*|commence[sd]?|commencing|subsequent\w*|"
    r"notwithstanding|aforementioned|heretofore|thereof|wherein|thereby|whereby|elucidat\w+|explicat\w+|"
    r"paradigm\w*|juxtapos\w+|myriad\w*|plethora|facilitat\w+|cognizant|requisite|henceforth|"
    r"peruse[sd]?|ascertain\w*|albeit|hitherto|dichotom\w+|instantiate\w*|delineat\w+|promulgat\w+|"
    r"expound\w*|propound\w*|eschew\w*|imbue[sd]?|engender\w*|encapsulat\w+|vis-[\u00e0a]-vis|"
    r"inter alia|prima facie|de facto|a priori|ipso facto|erstwhile|veritable|multifaceted)\b",
    re.I)

# A cross-reference quotes the other verse's clause in bold only:
#     (C:V — **“the clause”**)
QURAN_QUOTE = re.compile(
    r"\((\d{1,3}):(\d{1,3})(?:\s*[\u2013\u2014-]\s*(\d{1,3}))?"
    r"(?:\s*,\s*(\d{1,3}):(\d{1,3}))?"
    r"\s*\u2014\s*\*\*[\u201c](.+?)[\u201d]\*\*\)",
    re.S)

# ... and the older italic-only marker, kept so the gate can name the mistake.
QURAN_QUOTE_ITALIC = re.compile(
    r"\(\d{1,3}:\d{1,3}(?:\s*[\u2013\u2014-]\s*\d{1,3})?"
    r"\s*\u2014\s*\*(?!\*)[\u201c][^\u201d]+[\u201d]\*\)")

# The verse being explained quotes its own phrase in bold italics:
#     ***“the phrase of this verse”***
PHRASE_QUOTE = re.compile(r"\*\*\*[\u201c](.+?)[\u201d]\*\*\*", re.S)
BOLD_ONLY_QUOTE = re.compile(r"(?<!\*)\*\*[\u201c](.+?)[\u201d]\*\*(?!\*)", re.S)

BARE_REF = re.compile(r"\((\d{1,3}):(\d{1,3})(?:\s*[\u2013\u2014-]\s*(\d{1,3}))?(?:\s*,\s*\d{1,3}:\d{1,3})*\)")

CURLY_ONLY_QUOTE = re.compile(r"(?<!\*)\*[\u201c]([^\u201d]{8,})[\u201d]\*(?!\*)")
STRAIGHT_IN_ITALIC = re.compile(r"\*+\"([^\"]{8,})\"\*+")

PHRASE_HEADING = re.compile(r"^\*\*[\u201c\"](.+?)[\u201d\"]\*\*[ \t]*$")

HEADING_LINE = re.compile(r"^\*\*.+\*\*[ \t]*$")
CURLY_QUOTE = re.compile(r"\u201c([^\u201d]{2,})\u201d", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

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

GENERIC_HEADINGS = {
    "commentary", "explanation", "introduction", "overview", "summary",
    "lesson", "lessons", "note", "notes", "conclusion", "reflection",
    "reflections", "analysis", "discussion", "the verse",
}

PROPHET_REPORT = re.compile(
    r"(?:\bthe Prophet\b(?!s)|\uFDFA|\bthe Messenger of (?:Allah|God)\b|\bAllah[\u2019']s Messenger\b)"
    r"[^.!?]{0,70}?\b(?:said|says|reported|narrated|stated|declared|instructed|warned|told(?! to\b))\b", re.I)

PROPHET_REF = re.compile(
    r"(\bthe Prophet\b(?!s)|\uFDFA|\bthe Messenger of (?:Allah|God)\b|\bAllah[\u2019']s Messenger\b)")


class Finding:
    __slots__ = ("level", "code", "ref", "line", "message")

    def __init__(self, level, code, ref, line, message):
        self.level, self.code, self.ref, self.line, self.message = level, code, ref, line, message


def verse_floor(verse_words: int) -> int:
    """Words a verse section must carry: 500, rising 6x with the verse."""
    return max(MIN_VERSE_WORDS, min(SCALE_CAP, int(math.ceil(SCALE_FACTOR * verse_words))))


def _strip_marks(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    for a, b in (("\u02bf", "'"), ("\u02be", "'"), ("\u2019", "'"), ("\u2018", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u1e6d", "t"), ("\u1e63", "s"),
                 ("\u1e25", "h"), ("\u1e0d", "d"), ("\u1e93", "z"),
                 ("\u2013", " "), ("\u2014", " ")):
        text = text.replace(a, b)
    return text


def _canon(text: str) -> str:
    return re.sub(r"\s+", " ", _strip_marks(text)).strip().lower()


def _loose(text: str) -> str:
    """Canonical form that also ignores the ˹…˺ brackets the translation supplies."""
    return C.loose_norm(text).strip()


def _prose_only(body: str) -> str:
    """Body text without the headings: headings are titles, not commentary."""
    return "\n".join(l for l in body.split("\n") if not HEADING_LINE.match(l))


def _has_anchor(text: str) -> bool:
    """Is there a checkable source anchor in this text?"""
    return bool(BARE_REF.search(text) or QURAN_QUOTE.search(text)
                or COLLECTIONS.search(text) or SCHOLARS.search(text) or LANGUAGE.search(text))


def _verse_run(title: str, verse_tokens: list) -> int:
    """Longest run of words a heading shares verbatim with the verse."""
    lt = C.loose_norm(title).split()
    grams = {" ".join(verse_tokens[i:i + k])
             for k in range(1, len(verse_tokens) + 1)
             for i in range(len(verse_tokens) - k + 1)}
    best = 0
    for i in range(len(lt)):
        for k in range(min(len(lt) - i, len(verse_tokens)), best, -1):
            if " ".join(lt[i:i + k]) in grams:
                best = k
                break
    return best


# ------------------------------------------------------------------- the checks


def audit_chapter(chapter: int, opts) -> list:
    findings = []
    path = C.output_path(chapter)

    def fail(code, ref, line, msg):
        findings.append(Finding(FAIL, code, ref, line, msg))

    def warn(code, ref, line, msg):
        findings.append(Finding(WARN, code, ref, line, msg))

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

    all_sentences = defaultdict(list)
    quotes_seen = defaultdict(list)
    analogy_sections = 0
    prose_chunks = []
    _spread_checked = set()
    _cited_by_verse = {}

    for section in doc.sections:
        ref = section.ref
        anchor = section.start

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
        verse_words = len(C.words(C.ayah_en(chapter, section.verse)))
        floor = verse_floor(verse_words)
        if body_words < floor:
            fail("WRD-FLOOR", ref, anchor,
                 "verse tafsir is %d words; this verse needs at least %d (floor = max(600, 8x the verse's %d words))"
                 % (body_words, floor, verse_words))
        elif body_words > MAX_VERSE_WORDS:
            warn("WRD-CEILING", ref, anchor,
                 "verse tafsir is %d words (soft ceiling %d \u2014 check for padding)" % (body_words, MAX_VERSE_WORDS))
        if re.search(r"\bTODO\b|\bTBD\b|PLACEHOLDER", body):
            fail("FMT-PLACEHOLDER", ref, anchor, "placeholder text left in the section")

        # ---- the ten sources: consulted (digest), named (prose), not exceeded
        prose = _prose_only(body)
        labelled = LABELS.search(prose)
        if labelled:
            fail("STY-LABELS", ref, anchor,
                 "the element is labelled instead of shown: %r \u2014 the history, the hadith, the lesson, "
                 "the cross-reference and the modern application are carried by the prose, never announced"
                 % labelled.group(0).strip()[:40])
        banned = BANNED_WORKS.search(prose)
        if banned:
            fail("SRC-BANNED", ref, anchor,
                 "cites a work outside the ten: %r \u2014 write from corpus.SOURCE_ALLOWLIST only"
                 % banned.group(0))

        cited = {slug for slug, rx in AUTHORITY.items() if rx.search(prose)}
        if section.verse not in _spread_checked:
            _spread_checked.add(section.verse)
            digest = _digest(chapter)
            if digest is None:
                fail("SRC-NODIGEST", ref, anchor,
                     "tmp/sources/%s.json is missing: every one of the ten must be pulled for this chapter "
                     "before a verse is written (python3 scripts/tafsir/sources.py %d)" % (C.pad3(chapter), chapter))
            else:
                held = digest.get(str(section.verse)) or {}
                unchecked = [s for s in C.SOURCE_ALLOWLIST
                             if s not in held and C.source_covers(s, chapter, section.verse)]
                if unchecked:
                    fail("SRC-NOTCHECKED", ref, anchor,
                         "%d of the ten were never pulled for this verse: %s"
                         % (len(unchecked), ", ".join(unchecked)))
                absent = [s for s in C.SOURCE_ALLOWLIST
                          if s not in held and not C.source_covers(s, chapter, section.verse)]
                if absent:
                    warn("SRC-ABSENT", ref, anchor,
                         "no text for this verse in the repo: %s (coverage gap upstream)" % ", ".join(absent))

        if len(cited) < SRC_MIN_CITED:
            fail("SRC-SPREAD", ref, anchor,
                 "only %d of the ten named (%s); a verse is written from at least %d, not from the two or three "
                 "that are easiest to read" % (len(cited), ", ".join(sorted(cited)) or "none", SRC_MIN_CITED))
        else:
            if not (cited & set(C.CLASSICAL_SLUGS)):
                fail("SRC-FAMILY", ref, anchor,
                     "no classical authority named (al-Tabari, al-Qurtubi, al-Baghawi, Ibn Kathir, al-Alusi)")
            if not (cited & set(C.MODERN_SLUGS)):
                warn("SRC-FAMILY", ref, anchor,
                     "no modern authority named (al-Sa'di, Ibn 'Uthaymin, Ma'arif al-Qur'an)")
        _cited_by_verse[section.verse] = cited

        paragraphs = C.split_paragraphs(body)
        if len(paragraphs) < 2:
            fail("FMT-PARAGRAPHS", ref, anchor, "a verse section is at least 2 paragraphs")

        heads = section.headings()
        verse_tokens = C.loose_norm(C.ayah_en(chapter, section.verse)).split()
        if not heads:
            fail("FMT-HEADINGS", ref, anchor,
                 "no **headings**: a verse is a set of titled paragraphs (context, history, the "
                 "phrase-by-phrase explanation, the ruling it carries)")
        elif len(heads) < 2:
            warn("FMT-HEADINGS-FEW", ref, anchor,
                 "one heading only: a verse usually needs several titled paragraphs")
        elif len(heads) > MAX_HEADINGS:
            warn("FMT-HEADINGS-COUNT", ref, anchor, "%d headings (soft maximum %d)" % (len(heads), MAX_HEADINGS))

        for line_no, title in heads:
            i = line_no - 1
            if i > 0 and lines[i - 1].strip() != "":
                fail("FMT-HEADING-SHAPE", ref, line_no, "blank line required before the heading")
            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                fail("FMT-HEADING-SHAPE", ref, line_no,
                     "blank line required after the heading (a heading is its own paragraph)")
            nxt = next((h for h in heads if h[0] > line_no), None)
            end = (nxt[0] - 1) if nxt else section.end
            chunk = "\n".join(lines[line_no:end])
            if not re.search(r"[A-Za-z]", chunk):
                fail("FMT-ORPHAN-HEADING", ref, line_no, "'%s' has no prose under it" % title)
            if PHRASE_HEADING.match(lines[i]) or title.strip().startswith("\u201c"):
                fail("FMT-HEADING-QUOTED", ref, line_no,
                     "'%s' is the verse's own wording: headings are descriptive titles \u2014 quote the "
                     "phrase inside the paragraph and explain it there" % title[:60])
                continue
            if re.search(r"[a-z]", title):
                fail("FMT-HEADING-CASE", ref, line_no,
                     "headings are written in UPPERCASE: '%s'" % title[:60])
            if title.strip().lower() in GENERIC_HEADINGS:
                fail("FMT-HEADING-GENERIC", ref, line_no,
                     "'%s' is a generic heading; say what the paragraph says" % title)
            run = _verse_run(title, verse_tokens)
            if run >= HEADING_VERSE_RUN_FAIL:
                fail("FMT-HEADING-VERSE", ref, line_no,
                     "heading repeats %d words of the verse verbatim: a heading names the paragraph, "
                     "the verse's own wording is quoted in the prose" % run)
            elif run >= HEADING_VERSE_RUN_WARN:
                warn("FMT-HEADING-VERSE", ref, line_no,
                     "heading repeats %d words of the verse: keep titles descriptive" % run)
            if len(C.words(title)) > HEADING_MAX_WORDS:
                warn("FMT-HEADING-LONG", ref, line_no,
                     "heading is %d words (keep titles under %d)" % (len(C.words(title)), HEADING_MAX_WORDS))
        titles = [t.lower() for _, t in heads]
        dupes = sorted({t for t in titles if titles.count(t) > 1})
        if dupes:
            warn("FMT-HEADING-DUP", ref, anchor, "heading repeated in the same section: %s" % ", ".join(dupes))

        # phrases: each one quoted inside the prose, in order, explained, and evidenced
        _phrase_rules(section, chapter, fail, warn)

        # separators
        sep_count = sum(1 for l in section.lines if l.strip() == "---")
        is_last = section is doc.sections[-1]
        if is_last and sep_count:
            warn("FMT-SEP", ref, anchor, "trailing '---' after the final verse")
        if not is_last and sep_count != 1:
            fail("FMT-SEP", ref, anchor, "expected exactly one '---' before the next verse (found %d)" % sep_count)

        # references and quotations (heading lines are titles, not citations)
        checkable = _prose_only(body)
        own_canon = _canon(C.ayah_en(chapter, section.verse))
        for m in QURAN_QUOTE.finditer(checkable):
            s_ch, s_v = int(m.group(1)), int(m.group(2))
            inner = m.group(5)
            if not _ref_ok(s_ch, s_v):
                fail("REF-RANGE", ref, anchor, "(%d:%d) is not a verse of the Qur'an" % (s_ch, s_v))
                continue
            if _canon(inner) not in _canon(C.ayah_en(s_ch, s_v)):
                fail("REF-QUOTE", ref, anchor,
                     "quote from %d:%d is not verbatim: %r" % (s_ch, s_v, inner[:70]))
            if s_ch == chapter and s_v == section.verse:
                warn("REF-SELF-QUOTE", ref, anchor,
                     "the verse's own wording is already in the line above; cite it without re-quoting")

        for m in BARE_REF.finditer(checkable):
            s_ch, s_v = int(m.group(1)), int(m.group(2))
            if not _ref_ok(s_ch, s_v):
                fail("REF-RANGE", ref, anchor, "(%d:%d) is not a verse of the Qur'an" % (s_ch, s_v))

        for m in QURAN_QUOTE_ITALIC.finditer(checkable):
            fail("REF-QUOTE-STYLE", ref, anchor,
                 "a cross-reference quote is italic: other references are quoted in bold only, "
                 "(C:V \u2014 **\u201cthe clause\u201d**)")

        cross = [m.span() for m in QURAN_QUOTE.finditer(checkable)]
        for m in PHRASE_QUOTE.finditer(checkable):
            if any(a <= m.start() and m.end() <= b for a, b in cross):
                continue                     # inside a cross-reference: that is a reference quote
            if _canon(m.group(1)) not in own_canon:
                warn("PHR-QUOTE-FOREIGN", ref, anchor,
                     "quoted in this verse's bold italics but it is not this verse's wording: %r"
                     % m.group(1)[:60])

        for m in CURLY_ONLY_QUOTE.finditer(checkable):
            if _canon(m.group(1)) in own_canon:
                continue                     # a phrase of this verse, quoted to be explained
            before = checkable[max(0, m.start() - 45):m.start()]
            if not re.search(r"\d{1,3}:\d{1,3}\s*\u2014\s*$", before):
                warn("REF-UNANCHORED", ref, anchor,
                     "quoted Qur'an clause without its reference beside it: %r" % m.group(1)[:50])

        for m in STRAIGHT_IN_ITALIC.finditer(checkable):
            inner = _canon(m.group(1))
            if inner in own_canon:
                continue                     # a phrase of this verse, quoted to be explained
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

        for para in paragraphs:
            for sentence in C.sentence_split(para):
                if PROPHET_REPORT.search(sentence):
                    if not COLLECTIONS.search(sentence) and not COLLECTIONS.search(para):
                        fail("EVD-ATTRIBUTION", ref, anchor,
                             "prophetic report without its collection: %r" % sentence[:90])
                        break

        # analogy, and its absence
        if ANALOGY.search(body):
            analogy_sections += 1
        else:
            warn("STY-ANALOGY", ref, anchor,
                 "no relatable analogy in this verse (the prompt asks for one where it fits)")

        # grounding
        if not opts.no_grounding:
            missing = _ungrounded(body, chapter, section.verse, opts)
            if missing:
                warn("GRD-TOKENS", ref, anchor,
                     "%d named/foreign terms not found in this verse's sources (check them): %s"
                     % (len(missing), ", ".join(sorted(missing)[:8])))

        prose_chunks.append(_prose_only(body))

        for para in paragraphs:
            if para.strip().startswith("**") and para.strip().endswith("**"):
                continue  # headings are titles; a repeated title is reported at section level
            for sentence in C.sentence_split(para):
                key = C.norm_key(sentence)
                if len(key.split()) >= MIN_SENTENCE_WORDS:
                    all_sentences[key].append((ref, anchor, sentence))

    for key, hits in all_sentences.items():
        if len(hits) > 1:
            refs = ", ".join(sorted({h[0] for h in hits}, key=lambda r: (r.split(":")[0], r.split(":")[1])))
            fail("REP-SENTENCE", hits[1][0], hits[1][1],
                 "the same sentence appears in %s: %r" % (refs, hits[0][2][:80]))

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

    # -------- chapter-level style ---------------------------------------------
    if doc.sections:
        share = analogy_sections / len(doc.sections)
        if share < ANALOGY_MIN_SHARE:
            fail("STY-ANALOGY", "%d" % chapter, 0,
                 "only %d of %d verses carry a relatable analogy (at least %.0f%% should)"
                 % (analogy_sections, len(doc.sections), ANALOGY_MIN_SHARE * 100))
        elif share < ANALOGY_WARN_SHARE:
            warn("STY-ANALOGY", "%d" % chapter, 0,
                 "%d of %d verses carry a relatable analogy" % (analogy_sections, len(doc.sections)))

    # -------- which of the ten this chapter actually used ----------------------
    if _cited_by_verse:
        used = set().union(*_cited_by_verse.values())
        unused = [s for s in C.SOURCE_ALLOWLIST if s not in used]
        if unused:
            warn("SRC-UNUSED", "%d" % chapter, 0,
                 "%d of the ten are never named in this chapter: %s"
                 % (len(unused), ", ".join(unused)))

    prose = "\n".join(prose_chunks)
    metrics = C.style_metrics(prose)
    if metrics["sentences"] >= 20 and metrics["words"] >= 800:
        if metrics["mean_sentence"] > MEAN_SENTENCE_FAIL:
            fail("STY-SENTENCE", "%d" % chapter, 0,
                 "mean sentence is %.1f words (keep it under %.0f): split the long ones"
                 % (metrics["mean_sentence"], MEAN_SENTENCE_WARN))
        elif metrics["mean_sentence"] > MEAN_SENTENCE_WARN:
            warn("STY-SENTENCE", "%d" % chapter, 0,
                 "mean sentence is %.1f words (target under %.0f)" % (metrics["mean_sentence"], MEAN_SENTENCE_WARN))
        if metrics["long_sentence_share"] > LONG_SENTENCE_FAIL:
            fail("STY-SENTENCE-LONG", "%d" % chapter, 0,
                 "%.0f%% of sentences run past 40 words (keep it under %.0f%%)"
                 % (metrics["long_sentence_share"] * 100, LONG_SENTENCE_WARN * 100))
        elif metrics["long_sentence_share"] > LONG_SENTENCE_WARN:
            warn("STY-SENTENCE-LONG", "%d" % chapter, 0,
                 "%.0f%% of sentences run past 40 words" % (metrics["long_sentence_share"] * 100))
        if metrics["flesch"] < FLESCH_FAIL:
            fail("STY-READABILITY", "%d" % chapter, 0,
                 "reading ease %.0f (plain English is 60+; %.0f is the floor)"
                 % (metrics["flesch"], FLESCH_WARN))
        elif metrics["flesch"] < FLESCH_WARN:
            warn("STY-READABILITY", "%d" % chapter, 0,
                 "reading ease %.0f (target 60+): shorter sentences, plainer words" % metrics["flesch"])
        if metrics["long_word_share"] > LONG_WORD_WARN:
            warn("STY-LONGWORDS", "%d" % chapter, 0,
                 "%.1f%% of words are 12+ letters (target under %.0f%%)"
                 % (metrics["long_word_share"] * 100, LONG_WORD_WARN * 100))

    hits = list(DICTION.finditer(prose))
    if hits:
        words = sorted({h.group(0).lower() for h in hits})
        level = fail if len(hits) >= 6 else warn
        level("STY-DICTION", "%d" % chapter, raw[:hits[0].start()].count("\n") + 1,
              "%d formal word(s) where plain English does: %s" % (len(hits), ", ".join(words[:8])))

    # -------- filler, whitespace, hygiene -------------------------------------
    for level, pattern, why in FILLER:
        for m in re.finditer(pattern, raw, re.I):
            line_no = raw[:m.start()].count("\n") + 1
            (fail if level == FAIL else warn)("REP-FILLER", "%d" % chapter, line_no,
                                              "%s: %r" % (why, m.group(0)))
            break

    if "\t" in raw:
        fail("FMT-WHITESPACE", "%d" % chapter, raw[:raw.index("\t")].count("\n") + 1, "tab character")
    for i, line in enumerate(lines):
        if line != line.rstrip():
            fail("FMT-WHITESPACE", "%d" % chapter, i + 1, "trailing whitespace")
            break
    m = re.search(r"\n{3,}", raw)
    if m:
        fail("FMT-WHITESPACE", "%d" % chapter, raw[:m.start()].count("\n") + 2, "more than one blank line in a row")
    if not raw.endswith("\n"):
        fail("FMT-WHITESPACE", "%d" % chapter, len(lines), "file must end with a single newline")
    elif raw.endswith("\n\n"):
        fail("FMT-WHITESPACE", "%d" % chapter, len(lines), "file ends with a blank line")

    for wording, refs in quotes_seen.items():
        if len(refs) > 4:
            warn("REP-QUOTE", refs[4], 0, "the same wording is quoted %d times (%s)" % (len(refs), ", ".join(refs[:6])))

    return findings


def _quoted_runs(body: str) -> list:
    """The verse's own wording quoted in the prose: the bold-italic ``***\u201cphrase\u201d***`` runs.

    Cross-reference citations (``(C:V \u2014 **\u201cclause\u201d**``) are other verses and are
    removed first, so what is left is the wording quoted to explain this verse.
    """
    text = HTML_COMMENT.sub(" ", body)
    kept, last = [], 0
    for m in QURAN_QUOTE.finditer(text):
        kept.append(text[last:m.start()])
        last = m.end()
    kept.append(text[last:])
    return [m.group(1).strip() for m in PHRASE_QUOTE.finditer(" ".join(kept))]


def _find_phrase(pool: str, phrase: str, pos: int):
    """Locate a phrase, or its leading words, at or after ``pos`` in the quoted pool."""
    if not phrase:
        return None
    i = pool.find(phrase, pos)
    if i >= 0:
        return i, i + len(phrase)
    words = phrase.split()
    for take in range(len(words) - 1, 2, -1):        # tolerate a different phrase boundary
        head = " ".join(words[:take])
        i = pool.find(head, pos)
        if i >= 0:
            return i, i + len(head)
    return None


def _longest_run_share(quotes: list, verse_tokens: list) -> float:
    """The most of the verse a single quoted stretch carries, as a share of its words.

    A writer who quotes a whole verse in one block and then writes around it fails this;
    a writer who quotes it phrase by phrase, each in the paragraph that explains it, does not.
    """
    if not verse_tokens:
        return 0.0
    best = 0
    for quote in quotes:
        qn = " ".join(C.loose_norm(quote).split())
        if not qn:
            continue
        for i in range(len(verse_tokens)):
            k = 0
            while (i + k < len(verse_tokens)
                   and " ".join(verse_tokens[i:i + k + 1]) in qn):
                k += 1
            best = max(best, k)
    return best / len(verse_tokens)


def _phrase_rules(section, chapter, fail, warn) -> dict:
    """Every phrase of the verse is quoted in the prose, in order, and backed by evidence.

    The verse's own wording is quoted inside the paragraphs (never as a heading), each
    quoted phrase is explained, and the paragraph carrying it\u2014or the one after it\u2014must
    hold a checkable anchor: a Qur'an cross-reference, a hadith collection, or a named
    authority. Coverage, gaps and edges are measured on those quotes; one quote may not
    swallow most of a long verse, because the verse is read as phrases.
    """
    ref = section.ref
    verse_text = C.ayah_en(chapter, section.verse)
    verse_norm = C.loose_norm(verse_text)
    word_spans = [(m.start(), m.end()) for m in re.finditer(r"[a-z0-9]+", verse_norm)]
    total = len(word_spans)
    stats = {"coverage": 0.0, "quotes": 0, "missing": 0, "evidence_missing": 0, "run_share": 0.0}
    if not total:
        return stats

    body = HTML_COMMENT.sub(" ", _prose_only(section.body()))
    quotes = _quoted_runs(body)
    stats["quotes"] = len(quotes)
    pool = " ".join(C.loose_norm(q) for q in quotes)
    if not pool.strip():
        fail("PHR-PHRASE-NONE", ref, section.start,
             "no phrase of the verse is quoted in the prose: quote each phrase as "
             "\u201cits words\u201d under a descriptive heading, then explain it")
        return stats

    phrases = C.split_phrases(verse_text) or [verse_text]
    covered = [False] * total
    quoted, unquoted = [], []
    pool_pos, verse_pos = 0, 0
    for phrase in phrases:
        pnorm = C.loose_norm(phrase)
        if not pnorm or _find_phrase(pool, pnorm, pool_pos) is None:
            unquoted.append(phrase)                 # never quoted in the prose
            continue
        quoted.append(phrase)
        pool_pos = _find_phrase(pool, pnorm, pool_pos)[1]
        # ... and mark the words of that phrase in the verse itself
        idx = verse_norm.find(pnorm, verse_pos)
        if idx < 0:
            words_ = pnorm.split()
            for take in range(len(words_) - 1, 2, -1):
                idx = verse_norm.find(" ".join(words_[:take]), verse_pos)
                if idx >= 0:
                    pnorm = " ".join(words_[:take])
                    break
        if idx < 0:
            continue
        end = idx + len(pnorm)
        for k, (wa, wb) in enumerate(word_spans):
            if wa >= idx and wb <= end:
                covered[k] = True
        verse_pos = end

    gaps, run_start = [], None
    for k in range(total + 1):
        if k < total and not covered[k]:
            if run_start is None:
                run_start = k
        elif run_start is not None:
            gaps.append((run_start, k))
            run_start = None

    uncovered = total - sum(covered)
    share = 1 - uncovered / total
    stats["coverage"] = share
    if uncovered:
        where = " / ".join(" ".join(verse_norm.split()[a:b]) for a, b in gaps[:4])[:160]
        if share < PHRASE_COVERAGE_MIN:
            fail("PHR-PHRASE-COVERAGE", ref, section.start,
                 "the prose quotes %.0f%% of the verse (floor %.0f%%); never quoted: %s"
                 % (share * 100, PHRASE_COVERAGE_MIN * 100, where))
        else:
            warn("PHR-PHRASE-COVERAGE", ref, section.start,
                 "the prose quotes %.0f%% of the verse; never quoted: %s" % (share * 100, where))
        for a, b in gaps:
            if b - a > PHRASE_GAP_MAX:
                fail("PHR-PHRASE-GAP", ref, section.start,
                     "%d words of the verse are passed over without being quoted: \u201c%s\u201d"
                     % (b - a, " ".join(verse_norm.split()[a:b])[:120]))
                break
        if gaps:
            if gaps[0][0] > PHRASE_EDGE_MAX:
                fail("PHR-PHRASE-EDGE", ref, section.start,
                     "the verse's first %d words are never quoted: \u201c%s\u201d"
                     % (gaps[0][0], " ".join(verse_norm.split()[:gaps[0][0]])[:80]))
            if total - gaps[-1][1] > PHRASE_EDGE_MAX:
                fail("PHR-PHRASE-EDGE", ref, section.start,
                     "the verse's last %d words are never quoted: \u201c%s\u201d"
                     % (total - gaps[-1][1], " ".join(verse_norm.split()[gaps[-1][1]:])[:80]))

    # quoting style: this verse's phrases bold+italic, other references bold only
    text = _prose_only(body)
    stripped = QURAN_QUOTE.sub(" ", HTML_COMMENT.sub(" ", text))
    stripped = PHRASE_QUOTE.sub(" ", stripped)
    for m in CURLY_QUOTE.finditer(stripped):
        inner = _canon(m.group(1))
        if len(inner) > 8 and inner in _canon(verse_text):
            fail("PHR-QUOTE-STYLE", ref, section.start,
                 "a phrase of this verse is quoted without bold italics: write it "
                 "***\u201c%s\u201d***" % m.group(1)[:60])
            break
    for m in BOLD_ONLY_QUOTE.finditer(stripped):
        inner = _canon(m.group(1))
        if len(inner) > 8 and inner in _canon(verse_text):
            fail("PHR-QUOTE-STYLE", ref, section.start,
                 "a phrase of this verse is quoted in bold only: this verse's own wording is "
                 "bold italics (***\u201c%s\u201d***), bold is for other references"
                 % m.group(1)[:60])
            break

    stats["missing"] = len(unquoted)
    if unquoted:
        for phrase in unquoted[:3]:
            fail("PHR-PHRASE-MISSING", ref, section.start,
                 "this phrase is never quoted in the prose: \u201c%s\u201d" % phrase[:110])
        if len(unquoted) > 3:
            fail("PHR-PHRASE-MISSING", ref, section.start,
                 "%d further phrases are never quoted" % (len(unquoted) - 3))

    run_share = _longest_run_share(quotes, verse_norm.split())
    stats["run_share"] = run_share
    longest_phrase = max((len(C.loose_norm(p).split()) for p in phrases), default=0)
    merged = run_share * total > longest_phrase + 2      # a quote that spans phrases, not one phrase
    if total >= PHRASE_RUN_MIN_WORDS and run_share >= PHRASE_RUN_FAIL and merged:
        fail("PHR-CHUNK", ref, section.start,
             "one quoted stretch carries %.0f%% of the verse: read the verse as phrases and quote "
             "each one where you explain it" % (run_share * 100))
    elif total >= PHRASE_RUN_MIN_WORDS and run_share >= PHRASE_RUN_WARN and merged:
        warn("PHR-CHUNK", ref, section.start,
             "one quoted stretch carries %.0f%% of the verse (aim for smaller phrases)" % (run_share * 100))

    # evidence: the paragraph holding a quoted phrase, or the one after it, carries an anchor
    paras = C.split_paragraphs(body)
    para_norms = [C.loose_norm(p) for p in paras]
    missing_ev = []
    for phrase in quoted:
        pnorm = C.loose_norm(phrase)
        j = next((i for i, pn in enumerate(para_norms) if pnorm and pnorm in pn), None)
        if j is None:
            continue                       # quoted across a boundary: nothing to anchor
        if not (_has_anchor(paras[j]) or (j + 1 < len(paras) and _has_anchor(paras[j + 1]))):
            missing_ev.append(phrase)
    stats["evidence_missing"] = len(missing_ev)
    for phrase in missing_ev[:3]:
        fail("PHR-EVIDENCE", ref, section.start,
             "the quoted phrase \u201c%s\u201d is explained with no evidence beside it: give the "
             "paragraph a cross-reference, a report with its collection, or a named authority" % phrase[:100])
    if len(missing_ev) > 3:
        fail("PHR-EVIDENCE", ref, section.start,
             "%d further quoted phrases carry no evidence" % (len(missing_ev) - 3))
    return stats


def phrase_stats(chapter: int, section) -> dict:
    """Quoting numbers for one verse, for batch.py's table (same rules, no output)."""
    bucket = []
    stats = _phrase_rules(section, chapter, lambda *a: bucket.append(a), lambda *a: bucket.append(a))
    stats["findings"] = len(bucket)
    return stats


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
    for para in C.split_paragraphs(_prose_only(body)):   # headings are titles, not claims

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
            # a chapter still written in batches carries TODO scaffolds: report progress, not failure
            doc = C.load_chapter_doc(n)
            pending = [s.verse for s in doc.sections if "TODO" in s.body()]
            c = defaultdict(int)
            if pending:
                done = len(doc.sections) - len(pending)
                rows.append((n, None, None, (done, len(doc.sections), pending[0])))
                continue
            for f in findings:
                c[f.level] += 1
            for k, v in c.items():
                total[k] += v
            rows.append((n, c, findings))
        if args.json:
            out = []
            for row in rows:
                n, c, findings = row[0], row[1], row[2]
                if findings is None:
                    prog = row[3] if len(row) > 3 else None
                    out.append({"chapter": n, "present": bool(prog) or prog is None,
                                "in_progress": bool(prog),
                                "written_verses": prog[0] if prog else 0,
                                "total_verses": prog[1] if prog else 0})
                    continue
                out.append({"chapter": n, "present": True,
                            "fail": c[FAIL], "warn": c[WARN],
                            "findings": [f.__dict__ for f in findings]})
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            done = sum(1 for row in rows if row[1] is not None)
            in_progress = 0
            for row in rows:
                n, c, findings = row[0], row[1], row[2]
                if c is None:
                    if len(row) > 3:                      # unfinished chapter, written in batches
                        in_progress += 1
                        wrote, total_v, nxt = row[3]
                        print("%s  \u2014 in progress: %d/%d verses written, next %d:%d"
                              % (C.pad3(n), wrote, total_v, n, nxt))
                    else:
                        print("%s  \u2014 not written" % C.pad3(n))
                    continue
                marks = [f for f in findings if f.level == FAIL or (args.strict and f.level == WARN)]
                status = "PASS" if not marks else "FAIL"
                print("%s  %-4s  %2d fail  %2d warn  %s"
                      % (C.pad3(n), status, c[FAIL], c[WARN],
                         "" if not marks else "; ".join(sorted({f.code for f in marks})[:6])))
                bad.extend(marks)
            print("")
            print("chapters written: %d/114 | in progress: %d | FAIL %d | WARN %d"
                  % (done, in_progress, total[FAIL], total[WARN]))
        failing = total[FAIL] + (total[WARN] if args.strict else 0)
        return 1 if failing else 0

    findings = audit_chapter(args.chapter, args)
    if args.json:
        print(json.dumps([f.__dict__ for f in findings], ensure_ascii=False, indent=2))
    else:
        counts = report(args.chapter, findings, args.show_info)
        if counts[FAIL] == 0:
            print("RESULT: PASS \u2014 chapter %s meets the format, evidence and style rules" % C.pad3(args.chapter))
            if counts[WARN]:
                print("        (%d warnings to read before committing)" % counts[WARN])
    bad = sum(1 for f in findings if f.level == FAIL or (args.strict and f.level == WARN))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
