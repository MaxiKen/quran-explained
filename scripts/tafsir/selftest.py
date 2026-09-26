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
import lexicon as LEX

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


def _first_written(text, chapter):
    """The first verse with a real reading in it, or None while the chapter is scaffold."""
    blocks = list(re.finditer(r"(?m)^## Verse %d:(\d+)[ \t]*$" % chapter, text))
    for i, m in enumerate(blocks):
        end = blocks[i + 1].start() if i + 1 < len(blocks) else len(text)
        block = text[m.start():end]
        if (block.count("***\u201c") and _first_ref(block)
                and len(re.findall(r"(?m)^\*\*[^\n]+\*\*$", block)) >= 2):
            return int(m.group(1))
    return None


def _written_verse(text, chapter):
    """Number of the first verse with a real reading in it (else the last verse)."""
    return _first_written(text, chapter) or 1


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


def mut_sep_tight(text, ch):
    def fn(block):
        return re.sub(r"(?m)\n\n---[ \t]*$", "\n---", block, count=1)

    return _edit_verse(text, TARGET, fn)


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
    """Remove every analogy cue from the target verse, whatever word carries it."""
    def fn(block):
        lines = []
        for line in block.split("\n"):
            if not line.strip() or line.startswith("#") or line.strip().startswith("**") or line.startswith("> "):
                lines.append(line)
                continue
            kept = [s for s in C.sentence_split(line) if s.strip() and not audit.ANALOGY.search(s)]
            lines.append(" ".join(s.strip() for s in kept))
        return "\n".join(lines)

    return _edit_verse(text, TARGET, fn)


def mut_para_short(text, ch):
    """v7: a paragraph under the 120-word floor."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        return block[:b] + "\n\nOne short line only, standing where a paragraph belongs." + block[b:]

    return _edit_verse(text, TARGET, fn)


def mut_paraphrase(text, ch):
    """v7: the prose hands the point to a named work."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return (block[:a] + para + " Al-\u1e6cabari records that the reading here turns on the "
                "second clause, and the commentators say it is a warning." + block[b:])

    return _edit_verse(text, TARGET, fn)


def mut_source_quote(text, ch):
    """v7: a work of the eleven is quoted."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return (block[:a] + para + ' The words of al-Jal\u0101layn stand beside it: *"a brief '
                'enjoyment it is, and then it is gone."*' + block[b:])

    return _edit_verse(text, TARGET, fn)


def _edit_many(text, verses, fn):
    for v in sorted(set(verses), reverse=True):
        text = _edit_verse(text, v, fn)
    return text


def _verse_numbers(text):
    return [int(m.group(1)) for m in re.finditer(r"(?m)^## Verse \d+:(\d+)[ \t]*$", text)]


def mut_heading_reuse(text, ch):
    """v7.1: a heading of one verse used again in another verse."""
    nums = _verse_numbers(text)
    if len(nums) < 2:
        return text
    first = text.split("\n")[0]
    block = text[_find_verse(text, TARGET)[0]:_find_verse(text, TARGET)[1]]
    m = _first_heading(block)
    if not m:
        return text
    title = m.group(0)

    def fn(other):
        span = _first_heading(other)
        if not span:
            return other
        return other[:span.start()] + title + other[span.end():]

    return _edit_many(text, [nums[0], nums[1]], fn)


def mut_house_frame(text, ch):
    """v7.1: the same sentence frame and wording recurring in three verses."""
    nums = _verse_numbers(text)
    if len(nums) < 3:
        return text
    frame = (" The verse teaches the reader that mercy arrives on its own schedule, and the "
             "sentence is worth repeating here for the sake of the test.")

    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, _b = span
        return block[:a] + block[a:].rstrip("\n") + frame + "\n"

    return _edit_many(text, nums[:3], fn)


def mut_no_application(text, ch):
    """v7: the verse never reaches the reader's own world (warning)."""
    def fn(block):
        for rx, repl in ((r"\btoday\b", "then"), (r"\bnowadays\b", "then"),
                         (r"\bthese days\b", "at that time"),
                         (r"\bin our own time\b", "in that time")):
            block = re.sub(rx, repl, block, flags=re.I)
        return block

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


def mut_bold_elsewhere(text, ch):
    """Bold on a word that is none of the three markers (rule: bold is reserved)."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return block[:a] + para + " The **plain** emphasis is not allowed." + block[b:]

    return _edit_verse(text, TARGET, fn)


def mut_word_offverse(text, ch):
    """A word-study of a word the verse's translation does not carry."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return (block[:a] + para
                + " The word *quernstone* means a mill, which the verse does not say." + block[b:])

    return _edit_verse(text, TARGET, fn)


def mut_synonym(text, ch):
    """A word the verse does not carry, but which means one it does (adjust and continue)."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return block[:a] + para + " The word *salvation* means the rescue the verse names." + block[b:]

    return _edit_verse(text, TARGET, fn)


def mut_term_as_verse(text, ch):
    """Arabic offered as the verse's own wording."""
    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return block[:a] + para + " The verse says *k\u0101fir* of them." + block[b:]

    return _edit_verse(text, TARGET, fn)


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


# ------------------------------------------------- cases that must stay clean
# A rule that fires on the verse's own wording, or on a synonym of it, is a false
# alarm: these mutations must produce no match finding at all (an informational
# adjustment counts as a finding, which is why it is reported and not a failure).

def clean_own_word(text, ch, chapter):
    """Explain a word the verse's own translation carries."""
    verse = C.ayah_en(chapter, TARGET)
    words = [w for w in re.findall(r"[A-Za-z]{4,}", verse) if LEX.norm(w) not in LEX.STOP]
    if not words:
        raise RuntimeError("no usable word in the verse")
    word = words[0]

    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return block[:a] + para + " The word *%s* carries the point here." % word + block[b:]

    return _edit_verse(text, TARGET, fn)


def clean_synonym(text, ch, chapter):
    """Explain a synonym of a word the verse carries: adjusted, not failed."""
    verse = C.ayah_en(chapter, TARGET)
    index = LEX.verse_index(verse)
    pick = None
    for word in re.findall(r"[A-Za-z]{4,}", verse):
        for syn in sorted(LEX.synonyms(word)):
            if syn and syn not in LEX.STOP and LEX.lookup(syn, index)[0] == "synonym":
                pick = syn
                break
        if pick:
            break
    if not pick:
        raise RuntimeError("no synonym in the tables for this verse")

    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return block[:a] + para + " The word *%s* says the same thing." % pick + block[b:]

    return _edit_verse(text, TARGET, fn)


def clean_phrase_synonym(text, ch, chapter):
    """Hold up a *phrase* that means what a phrase of the verse means: adjusted, not failed."""
    verse = C.ayah_en(chapter, TARGET)
    index = LEX.verse_index(verse)
    variant = None
    for phrase in C.split_phrases(verse):
        words = LEX.content_words(phrase)
        if not words:
            continue
        for word in words:
            for syn in sorted(LEX.synonyms(word)):
                if syn and syn not in LEX.STOP and LEX.lookup(syn, index)[0] == "synonym":
                    variant = " ".join(syn if w == word else w for w in words)
                    break
            if variant:
                break
        if variant:
            break
    if not variant:
        raise RuntimeError("no phrase-level synonym for this verse")

    def fn(block):
        span = _first_para(block)
        if not span:
            return block
        a, b = span
        para = block[a:b].rstrip("\n")
        return block[:a] + para + " The phrase *%s* says it in other words." % variant + block[b:]

    return _edit_verse(text, TARGET, fn)


def mut_ref_none(text, ch):
    """§0.10 take every cross-reference out of the verse: REF-NONE (v7.3) must fire."""
    def fn(block):
        return re.sub(r"\(\d{1,3}:\d{1,3} \u2014 \*\*\u201c[^\u201d]+\u201d\*\*\)", "", block)

    return _edit_verse(text, TARGET, fn)


def mut_evd_tafsir(text, ch):
    """§0.10 take the transmitted reading out of the verse: EVD-TAFSIR (v7.3) must fire."""
    def fn(block):
        out = audit.FIRST_GEN.sub("the first readers", block)
        return audit.COLLECTIONS.sub("the report", out)

    return _edit_verse(text, TARGET, fn)


def _append_to_first_para(block, sentence):
    span = _first_para(block)
    if not span:
        return block
    a, b = span
    para = block[a:b].rstrip("\n")
    return block[:a] + para + " " + sentence + block[b:]


def mut_ind_work(text, ch):
    """\u00a70.12 a work is named: IND-WORK must fire."""
    return _edit_verse(text, TARGET, lambda b: _append_to_first_para(
        b, "The reading is set out at length in al-Itqan."))


def mut_ind_quote(text, ch):
    """\u00a70.12 a quotation with no reference: IND-QUOTE must fire."""
    return _edit_verse(text, TARGET, lambda b: _append_to_first_para(
        b, 'The old writers put it this way, "the mercy of God has no limit that a '
           'creature can measure".'))


def mut_contraction(text, ch):
    """\u00a70.11 a contraction: STY-CONTRACTION must fire."""
    return _edit_verse(text, TARGET, lambda b: _append_to_first_para(
        b, "It doesn't matter how small the phrase looks."))


def mut_exclaim(text, ch):
    """\u00a70.11 an exclamation mark: STY-EXCLAIM must fire."""
    return _edit_verse(text, TARGET, lambda b: _append_to_first_para(
        b, "The reach of that mercy is one of the plainest facts in the sūrah!"))


def mut_hype(text, ch):
    """\u00a70.11 a hype word: STY-HYPE must fire."""
    return _edit_verse(text, TARGET, lambda b: _append_to_first_para(
        b, "The arrangement of the sentence is amazing in its detail."))


def mut_question(text, ch):
    """\u00a70.11 stacked questions: STY-QUESTION must fire."""
    return _edit_verse(text, TARGET, lambda b: _append_to_first_para(
        b, "Why would a person say that? What would he gain from it? How would he answer for it?"))


CLEAN_CASES = [
    ("\u00a75.1 the verse's own word may be explained", clean_own_word),
    ("\u00a75.1 a synonym is adjusted, not failed", clean_synonym),
    ("\u00a75.1 a phrase synonym is adjusted too", clean_phrase_synonym),
]


# A failure can be reported under a neighbouring code (a plainly quoted phrase is
# also "no phrase quoted"); the rule is enforced either way.
ALIASES = {
    "PHR-PHRASE-MISSING": {"PHR-PHRASE-MISSING", "PHR-PHRASE-NONE", "PHR-PHRASE-COVERAGE"},
    "PHR-QUOTE-STYLE": {"PHR-QUOTE-STYLE", "PHR-PHRASE-NONE", "PHR-PHRASE-COVERAGE"},
    "MTCH-WORD": {"MTCH-WORD", "MTCH-TERM"},
    "MTCH-TERM": {"MTCH-TERM", "MTCH-WORD"},
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
    ("\u00a74.8 separator is its own paragraph", "FMT-SEP", mut_sep_tight),
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
    ("v7 every paragraph runs past 120 words", "WRD-PARA-FLOOR", mut_para_short),
    ("v7 the prose never summarises a work", "STY-PARAPHRASE", mut_paraphrase),
    ("v7 the eleven are never quoted", "SRC-QUOTED", mut_source_quote),
    ("\u00a70.12 the book names no work", "IND-WORK", mut_ind_work),
    ("\u00a70.12 the book quotes no book", "IND-QUOTE", mut_ind_quote),
    ("\u00a70.11 no contractions in the register", "STY-CONTRACTION", mut_contraction),
    ("\u00a70.11 no exclamation marks", "STY-EXCLAIM", mut_exclaim),
    ("\u00a70.11 no hype words", "STY-HYPE", mut_hype),
    ("\u00a70.11 no stacked questions", "STY-QUESTION", mut_question),
    ("v7 the verse reaches the reader's world", "STY-APPLICATION", mut_no_application),
    ("v7.1 no heading reused across verses", "STY-UNIQUE-VERSE", mut_heading_reuse),
    ("v7.1 no house frame across verses", "STY-UNIQUE-VERSE", mut_house_frame),
    ("\u00a71 nothing outside the eleven is cited", "SRC-BANNED", mut_banned),
    ("\u00a77 a prophetic report names its collection", "EVD-ATTRIBUTION", mut_attribution),
    ("\u00a78 no duplicated sentences", "REP-SENTENCE", mut_rep_sentence),
    ("\u00a78 no pipeline vocabulary", "REP-FILLER", mut_filler),
    ("\u00a78 plain diction", "STY-DICTION", mut_diction),
    ("v5 the reading is interwoven, not per source", "STY-SOURCE-PARADE", mut_parade),
    ("v5 the reading analyses, not reports", "STY-ANALYSIS-FLOOR", mut_no_analysis),
    ("\u00a74.11 nothing is bold but the three markers", "MTCH-BOLD", mut_bold_elsewhere),
    ("\u00a75.1 words explained exist in the verse", "MTCH-WORD", mut_word_offverse),
    ("\u00a75.1 no Arabic as the verse's own wording", "MTCH-TERM", mut_term_as_verse),
    ("\u00a75.1 a synonym is not the verse's wording", "MTCH-TERM", mut_synonym),
    ("v7.3 every verse cites another verse", "REF-NONE", mut_ref_none),
    ("v7.3 every verse carries a transmitted reading", "EVD-TAFSIR", mut_evd_tafsir),
]


def run(chapter):
    global TARGET
    src = MD_DIR / ("%s.md" % C.pad3(chapter))
    text = src.read_text(encoding="utf-8")
    if _first_written(text, chapter) is None:
        # nothing is written yet: every case would mutate scaffold text and prove nothing,
        # and a 286-verse scaffold makes each audit run expensive
        return [("the whole chapter", "\u2014", "SKIP", "no written verse yet")]
    TARGET = _written_verse(text, chapter)
    opts = argparse.Namespace(no_grounding=True)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / src.name
        # what the untouched chapter already reports: a clean case may only add nothing
        baseline = {f.code for f in audit.audit_chapter(chapter, opts, path=src)
                    if f.code.startswith("MTCH-") and f.level != audit.INFO}
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

        for name, fn in CLEAN_CASES:                 # rules that must NOT fire
            try:
                mutated = fn(text, chapter, chapter)
            except Exception as exc:                 # not applicable to this verse
                rows.append((name, "MTCH-*", "n/a", str(exc)[:60]))
                continue
            if mutated == text:
                rows.append((name, "MTCH-*", "n/a", "mutation did not change the file"))
                continue
            scratch.write_text(mutated, encoding="utf-8")
            findings = audit.audit_chapter(chapter, opts, path=scratch)
            fired = sorted({f.code for f in findings
                            if f.code.startswith("MTCH-") and f.level != audit.INFO
                            and f.code not in baseline})
            rows.append((name, "MTCH-*", "FIRED" if fired else "ok", ", ".join(fired)[:70]))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("chapters", nargs="*", type=int)
    args = ap.parse_args(argv)
    chapters = args.chapters or [n for n in C.chapter_numbers() if (MD_DIR / ("%s.md" % C.pad3(n))).exists()]
    missed = 0
    skipped = 0
    false_alarms = 0
    for chapter in chapters:
        print("=" * 78)
        print("chapter %s" % C.pad3(chapter))
        for name, code, status, note in run(chapter):
            mark = {"caught": "ok  ", "MISSED": "MISS", "SKIP": "skip",
                    "ok": "ok  ", "FIRED": "FIRE", "n/a": "n/a "}[status]
            print("  %-4s %-40s %-18s %s" % (mark, name, code, note))
            if status == "MISSED":
                missed += 1
            elif status == "SKIP":
                skipped += 1
            elif status == "FIRED":
                false_alarms += 1
    print()
    print("uncaught rules: %d | rules not exercised: %d | false alarms: %d"
          % (missed, skipped, false_alarms))
    if skipped:
        print("a skip means the rule was never tested: write the chapter, or point the "
              "selftest at a chapter with a written verse")
    if false_alarms:
        print("a false alarm means the rule fired where it must not: the verse's own wording, "
              "or a synonym of it, was reported")
    return 1 if (missed or skipped or false_alarms) else 0


if __name__ == "__main__":
    raise SystemExit(main())
