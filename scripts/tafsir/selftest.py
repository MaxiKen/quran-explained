#!/usr/bin/env python3
"""selftest.py — do the rules actually bite?

The prompt (TAFSIR_PROMPT.md) states a long list of rules, and audit.py claims to
mechanise them. This script proves the claim: it takes a written chapter, breaks
one rule at a time on a scratch copy, runs the auditor over it, and checks that
the code the rule promises is among the findings.

    python3 scripts/tafsir/selftest.py          # chapters that are written
    python3 scripts/tafsir/selftest.py 1        # one chapter

Every row is a rule from TAFSIR_PROMPT.md §4-§8 (and the v5 interweaving rule).
A row that reports MISSED is a rule the gate does not enforce; the exit status is
non-zero when anything is missed.
"""
import argparse
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit
import corpus as C

MD_DIR = Path("tafsir")

# The verse the mutations are applied to. run() picks the first verse that is fully
# written (headings, phrase quotes and a cross-reference); the fixed default only
# applies if the picker finds nothing.
TARGET = 3


# ------------------------------------------------------------------ utilities

def _find_verse(text, verse):
    """Span of the '## Verse C:V' block (up to the next verse heading)."""
    m = re.search(r"(?m)^## Verse \d+:%d[ \t]*$" % verse, text)
    if not m:
        return None
    nxt = re.search(r"(?m)^## Verse \d+:\d+[ \t]*$", text[m.end():])
    end = m.end() + nxt.start() if nxt else len(text)
    return m.start(), end


def _edit_verse(text, verse, fn):
    span = _find_verse(text, verse)
    if span is None:
        return text
    a, b = span
    return text[:a] + fn(text[a:b]) + text[b:]


def _first_heading(block):
    m = re.search(r"(?m)^\*\*[^\n]+\*\*$", block)
    return m


def _first_phrase_quote(block):
    return re.search(r"\*\*\*\u201c[^\u201d]+\u201d\*\*\*", block)


def _first_ref(block):
    return re.search(r"\(\d{1,3}:\d{1,3} \u2014 \*\*\u201c[^\u201d]+\u201d\*\*\)", block)


def _first_para(block):
    """Span of the first prose paragraph (after the first heading)."""
    m = re.search(r"(?m)^\*\*[^\n]+\*\*$\n\n", block)
    if not m:
        return None
    start = m.end()
    end = block.find("\n\n**", start)
    return (start, end if end != -1 else len(block))


def _sub_verse(text, verse, pattern, repl, count=1):
    def fn(block):
        return re.sub(pattern, repl, block, count=count, flags=re.M)

    return _edit_verse(text, verse, fn)


def _written_verse(text, chapter):
    """Number of the first verse with a real reading in it (else the last verse)."""
    blocks = list(re.finditer(r"(?m)^## Verse %d:(\d+)[ \t]*$" % chapter, text))
    last = 1
    for i, m in enumerate(blocks):
        last = int(m.group(1))
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        block = text[m.start():end]
        if (block.count("***\u201c") and _first_ref(block)
                and len(re.findall(r"(?m)^\*\*[^\n]+\*\*$", block)) >= 2):
            return last
    return last


# ------------------------------------------------------------------ mutations
# Each entry: (rule in the prompt, expected code, mutation).

def mut_title(text, ch):
    return re.sub(r"(?m)^# .+$", "# Chapter %d — Tafsir" % ch, text, count=1)


def mut_intro_pos(text, ch):
    return text.replace("## Introduction to the S\u016brah", "\n## Introduction to the S\u016brah", 1)


def mut_intro_short(text, ch):
    m = re.search(r"(?ms)^## Introduction to the S\u016brah\n\n.*?(?=\n---)", text)
    return text[:m.start()] + "## Introduction to the S\u016brah\n\nToo short." + text[m.end():]


def mut_intro_bold(text, ch):
    return text.replace("## Introduction to the S\u016brah\n\n",
                        "## Introduction to the S\u016brah\n\n**A HEADING IN THE INTRODUCTION**\n\n", 1)


def mut_intro_sep(text, ch):
    m = re.search(r"(?ms)^## Introduction to the S\u016brah\n\n.*?(?=\n---)", text)
    block = text[m.start():m.end()]
    cut = block.find("\n\n", block.find("\n\n") + 2)
    return text[:m.start()] + block[:cut] + "\n\n---\n" + block[cut:] + text[m.end():]


def mut_verse_drop(text, ch):
    span = _find_verse(text, TARGET)
    return text[:span[0]] + text[span[1]:]


def mut_quote_verbatim(text, ch):
    verse = C.ayah_en(ch, TARGET)
    words = verse.split()
    broken = " ".join(words[:3] + ["WRONGWORD"] + words[4:]) if len(words) > 4 else verse + " WRONGWORD"
    return text.replace("> " + verse, "> " + broken, 1)


def mut_quote_lines(text, ch):
    def fn(block):
        return re.sub(r"(?m)^> (.{6,}?) (.+)$", r"> \1\n> \2", block, count=1)

    return _edit_verse(text, TARGET, fn)


def mut_quote_missing(text, ch):
    return _sub_verse(text, TARGET, r"^> .+$", "", 1)


def mut_heading_shape(text, ch):
    def fn(block):
        m = _first_heading(block)
        return block[:m.end() + 1] + block[m.end() + 2:]

    return _edit_verse(text, TARGET, fn)


def mut_heading_case(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*(.+?)\*\*$",
                      lambda m: "**%s**" % m.group(1).lower(), 1)


def mut_heading_generic(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$", "**COMMENTARY**", 1)


def mut_heading_quoted(text, ch):
    def fn(block):
        q = re.search(r"(?m)^> (.+)$", block).group(1)
        return re.sub(r"(?m)^\*\*.+?\*\*$", '**\u201c%s\u201d**' % q.split(",")[0], block, count=1)

    return _edit_verse(text, TARGET, fn)


def mut_heading_verse(text, ch):
    def fn(block):
        q = re.search(r"(?m)^> (.+)$", block).group(1)
        words = re.sub(r"[\u0300-\u06ff\u02f9\u02fa]", "", q).split()
        return re.sub(r"(?m)^\*\*.+?\*\*$", ("**%s**" % " ".join(words[:7])).upper(), block, count=1)

    return _edit_verse(text, TARGET, fn)


def mut_heading_orphan(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^---$", "**AN EMPTY TITLE**\n\n---", 1)


def mut_paragraphs(text, ch):
    def fn(block):
        q = re.search(r"(?m)^> .+$", block)
        return block[:q.end()] + "\n\n**A SINGLE POINT**\n\nOne paragraph only, and no more.\n\n"

    return _edit_verse(text, TARGET, fn)


def mut_sep_dup(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^---$", "---\n\n---", 1)


def mut_sep_trailing(text, ch):
    return text.rstrip("\n") + "\n\n---\n"


def mut_whitespace_tab(text, ch):
    return text.replace("\n\n## Verse", "\n\t\n## Verse", 1)


def mut_whitespace_trailing(text, ch):
    return text.replace("\n\n## Verse", "  \n\n## Verse", 1)


def mut_whitespace_double_blank(text, ch):
    return text.replace("\n\n**", "\n\n\n**", 1)


def mut_placeholder(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$", "**TODO: WRITE THIS**", 1)


def mut_floor(text, ch):
    def fn(block):
        q = re.search(r"(?m)^> .+$", block)
        return block[:q.end()] + "\n\n**A TITLE**\n\nA short paragraph only.\n\n---\n"

    return _edit_verse(text, TARGET, fn)


def mut_phrase_missing(text, ch):
    def fn(block):
        m = _first_phrase_quote(block)
        return block[:m.start()] + m.group(0).strip("*") + block[m.end():]

    return _edit_verse(text, TARGET, fn)


def mut_phrase_style(text, ch):
    def fn(block):
        m = _first_phrase_quote(block)
        inner = m.group(0).strip("*")
        return block[:m.start()] + inner + block[m.end():]

    return _edit_verse(text, TARGET, fn)


def mut_ref_range(text, ch):
    return _sub_verse(text, TARGET, r"\(\d{1,3}:\d{1,3} \u2014", "(2:300 \u2014", 1)


def mut_ref_quote(text, ch):
    def fn(block):
        m = _first_ref(block)
        if not m:
            return block
        bad = m.group(0).replace("the", "teh", 1)
        return block[:m.start()] + bad + block[m.end():]

    return _edit_verse(text, TARGET, fn)


def mut_ref_style(text, ch):
    def fn(block):
        m = re.search(r"\(\d{1,3}:\d{1,3} \u2014 \*\*\u201c([^\u201d]+)\u201d\*\*\)", block)
        if not m:
            return block
        return block[:m.start()] + "(%s \u2014 *\u201c%s\u201d*)" % (
            m.group(0).split(" \u2014")[0].lstrip("("), m.group(1)) + block[m.end():]

    return _edit_verse(text, TARGET, fn)


def mut_straight_quote(text, ch):
    # a clause of another verse, in hadith-style straight quotes
    return _sub_verse(text, TARGET, r"(?m)^(\*\*[^\n]+\*\*)$",
                      '\\1\n\nThe report says that the Book calls it *"guide us along the straight path"*.', 1)


def mut_labels(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$",
                      "**LESSON FOR TODAY**\n\nLesson: patience is required of every reader.", 1)


def mut_analogy(text, ch):
    return re.sub(r"Imagine[^.]*\.", "The point is clear.", text)


def mut_spread(text, ch):
    def fn(block):
        for rx in list(audit.AUTHORITY.values()):
            block = rx.sub("a commentator", block)
        return audit.FIRST_GEN.sub("a commentator", block)

    return _edit_verse(text, TARGET, fn)


def mut_banned(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$",
                      "**THE READING OF AL-SHAWK\u0100N\u012a**\n\nThe reading follows al-Shawk\u0101n\u012b here.", 1)


def mut_attribution(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$",
                      "**A REPORT**\n\nThe Prophet \u2e3a said that the road of the mindful is short.", 1)


def mut_rep_sentence(text, ch):
    def fn(block):
        para = _first_para(block)
        sentence = C.sentence_split(block[para[0]:para[1]])[0].strip()
        return block + "\n\n" + sentence + "\n\n"

    return _edit_verse(text, TARGET, fn)


def mut_filler(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$",
                      "**THE SECTION**\n\nThis section has been written from the source digest for the audit.", 1)


def mut_diction(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^\*\*.+?\*\*$",
                      "**THE POINT**\n\nNotwithstanding the aforementioned, the verse obtains.", 1)


def mut_parade(text, ch):
    def fn(block):
        run = ("Al-Qur\u1e6dub\u012b notes that the verse settles the question. "
               "Al-Baghaw\u012b notes that the wording carries the weight. "
               "Al-Sa\u02bfd\u012b notes that the meaning is plain.")
        return block.rstrip("\n") + "\n\n" + run + "\n\n"

    return _edit_verse(text, TARGET, fn)


def mut_no_analysis(text, ch):
    def fn(block):
        for word in (" because ", " since ", " which means ", " so that ", " the point ",
                     " in other words ", " this is why ", " that is why ", " which is why "):
            block = block.replace(word, " and ")
        return block

    return _edit_verse(text, TARGET, fn)



def mut_ref_long(text, ch):
    def fn(block):
        m = _first_ref(block)
        if not m:
            return block
        ch_, v_ = m.group(0).split(" \u2014")[0].lstrip("(").split(":")
        whole = C.ayah_en(int(ch_), int(v_)).split()
        words = (whole * 8)[:40]                    # longer than the 34-word ceiling
        long_clause = "(%s:%s \u2014 **\u201c%s\u201d**)" % (ch_, v_, " ".join(words))
        return block[:m.start()] + long_clause + block[m.end():]

    return _edit_verse(text, TARGET, fn)


def mut_quote_style_hadith(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^(\*\*[^\n]+\*\*)$",
                      '\\1\n\nAn-Nasa\u02bei records in his collection that the Prophet \u2e3a said '
                      '\u201cthe believer who reads this s\u016brah in his house is protected from harm\u201d.', 1)


def mut_number(text, ch):
    return _sub_verse(text, TARGET, r"(?m)^(\*\*[^\n]+\*\*)$",
                      '\\1\n\n\u1e62a\u1e25\u012b\u1e25 al-Bukh\u0101r\u012b 987654 records the same point.', 1)


def mut_ref_repeat(text, ch):
    def fn(block):
        m = _first_ref(block)
        if not m:
            return block
        return block[:m.end()] + " The same clause is quoted again " + m.group(0) + block[m.end():]

    return _edit_verse(text, TARGET, fn)


# A failure can be reported under a neighbouring code (a plainly quoted phrase is
# also "no phrase quoted"); the rule is enforced either way.
ALIASES = {
    "PHR-PHRASE-MISSING": {"PHR-PHRASE-MISSING", "PHR-PHRASE-NONE", "PHR-PHRASE-COVERAGE"},
    "PHR-QUOTE-STYLE": {"PHR-QUOTE-STYLE", "PHR-PHRASE-NONE", "PHR-PHRASE-COVERAGE"},
}

CASES = [
    ("\u00a74.1 title line is exact", "FMT-TITLE", mut_title),
    ("\u00a74.2 introduction on line 3", "FMT-INTRO-POS", mut_intro_pos),
    ("\u00a74.2 introduction 250+ words", "WRD-INTRO", mut_intro_short),
    ("\u00a74.2 introduction has no headings", "FMT-INTRO-HEADINGS", mut_intro_bold),
    ("\u00a74.2 no separator inside the introduction", "FMT-INTRO-SEP", mut_intro_sep),
    ("\u00a74.3 every verse once, ascending", "FMT-VERSES", mut_verse_drop),
    ("\u00a74.4 quote is byte-exact", "FMT-QUOTE-VERBATIM", mut_quote_verbatim),
    ("\u00a74.4 quote is one line", "FMT-QUOTE-LINES", mut_quote_lines),
    ("\u00a74.4 quote line present", "FMT-QUOTE", mut_quote_missing),
    ("\u00a74.5 heading on its own line", "FMT-HEADING-SHAPE", mut_heading_shape),
    ("\u00a74.5 headings UPPERCASE", "FMT-HEADING-CASE", mut_heading_case),
    ("\u00a74.5 no generic headings", "FMT-HEADING-GENERIC", mut_heading_generic),
    ("\u00a74.5 heading is not a quote", "FMT-HEADING-QUOTED", mut_heading_quoted),
    ("\u00a74.5 heading is not the verse", "FMT-HEADING-VERSE", mut_heading_verse),
    ("\u00a74.5 every heading has prose", "FMT-ORPHAN-HEADING", mut_heading_orphan),
    ("\u00a74.5 a verse is several paragraphs", "FMT-PARAGRAPHS", mut_paragraphs),
    ("\u00a74.8 one separator between verses", "FMT-SEP", mut_sep_dup),
    ("\u00a74.8 no separator at the end", "FMT-SEP", mut_sep_trailing),
    ("\u00a74.9 no tabs", "FMT-WHITESPACE", mut_whitespace_tab),
    ("\u00a74.9 no trailing spaces", "FMT-WHITESPACE", mut_whitespace_trailing),
    ("\u00a74.9 no double blank lines", "FMT-WHITESPACE", mut_whitespace_double_blank),
    ("\u00a74.10 no placeholders", "FMT-PLACEHOLDER", mut_placeholder),
    ("\u00a74.7 the verse floor", "WRD-FLOOR", mut_floor),
    ("\u00a75 every phrase is quoted", "PHR-PHRASE-MISSING", mut_phrase_missing),
    ("\u00a75 phrases are bold italics", "PHR-QUOTE-STYLE", mut_phrase_style),
    ("\u00a76 citations are real verses", "REF-RANGE", mut_ref_range),
    ("\u00a76 cross-references are verbatim", "REF-QUOTE", mut_ref_quote),
    ("\u00a76 cross-references are bold only", "REF-QUOTE-STYLE", mut_ref_style),
    ("\u00a76 Qur'an wording is not in straight quotes", "REF-STRAIGHT-QUOTE", mut_straight_quote),
    ("\u00a74.2 elements are never labelled", "STY-LABELS", mut_labels),
    ("\u00a76 quote a clause, not a whole verse", "REF-LONG", mut_ref_long),
    ("\u00a76 reports are quoted in *\"...\"*", "EVD-QUOTE-STYLE", mut_quote_style_hadith),
    ("\u00a77 a hadith number exists in the sources", "EVD-NUMBER", mut_number),
    ("\u00a76 a verse is quoted once per section", "REF-QUOTE-REPEAT", mut_ref_repeat),
    ("\u00a78 every verse carries an analogy", "STY-ANALOGY", mut_analogy),
    ("\u00a71 at least five of the ten are named", "SRC-SPREAD", mut_spread),
    ("\u00a71 nothing outside the ten is cited", "SRC-BANNED", mut_banned),
    ("\u00a77 a prophetic report names its collection", "EVD-ATTRIBUTION", mut_attribution),
    ("\u00a78 no duplicated sentences", "REP-SENTENCE", mut_rep_sentence),
    ("\u00a78 no pipeline vocabulary", "REP-FILLER", mut_filler),
    ("\u00a78 plain diction", "STY-DICTION", mut_diction),
    ("v5 the reading is interwoven, not per source", "STY-SOURCE-PARADE", mut_parade),
    ("v5 the reading analyses, not reports", "STY-ANALYSIS-FLOOR", mut_no_analysis),
]


def run(chapter):
    global TARGET
    src = MD_DIR / ("%s.md" % C.pad3(chapter))
    text = src.read_text(encoding="utf-8")
    TARGET = _written_verse(text, chapter)
    opts = argparse.Namespace(no_grounding=True)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / src.name
        for name, code, fn in CASES:
            try:
                mutated = fn(text, chapter)
            except Exception as exc:                      # mutation not applicable
                rows.append((name, code, "SKIP", str(exc)[:60]))
                continue
            if mutated == text:
                rows.append((name, code, "SKIP", "mutation did not change the file"))
                continue
            scratch.write_text(mutated, encoding="utf-8")
            findings = audit.audit_chapter(chapter, opts, path=scratch)
            codes = {f.code for f in findings}
            want = ALIASES.get(code, {code})
            hit = bool(codes & want)
            rows.append((name, code, "caught" if hit else "MISSED",
                         "" if hit else ", ".join(sorted(codes))[:70]))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("chapters", nargs="*", type=int)
    args = ap.parse_args(argv)
    chapters = args.chapters or [n for n in C.chapter_numbers() if (MD_DIR / ("%s.md" % C.pad3(n))).exists()]
    missed = 0
    skipped = 0
    for chapter in chapters:
        print("=" * 78)
        print("chapter %s" % C.pad3(chapter))
        for name, code, status, note in run(chapter):
            mark = {"caught": "ok  ", "MISSED": "MISS", "SKIP": "skip"}[status]
            print("  %-4s %-34s %-18s %s" % (mark, name, code, note))
            if status == "MISSED":
                missed += 1
            elif status == "SKIP":
                skipped += 1
    print()
    print("uncaught rules: %d | rules not exercised: %d" % (missed, skipped))
    if skipped:
        print("a skip means the rule was never tested: write the chapter, or point the "
              "selftest at a chapter with a written verse")
    return 1 if (missed or skipped) else 0


if __name__ == "__main__":
    raise SystemExit(main())
