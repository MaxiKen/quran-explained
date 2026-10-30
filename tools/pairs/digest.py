#!/usr/bin/env python3
"""Measure what Tafsīr al-Ṭabarī actually discusses, phrase by phrase.

The phrase-by-phrase layer used to require a fixed 45-85 words for every
explanation, whatever the source held. That band flattens the material: the
passage on 1:1 runs to 8,464 words and the one on 2:19 to a few hundred, and
both were squeezed into the same shape.

This module measures the source instead, so a length can be *derived* rather
than imposed. It is the single source of truth used by `assemble.py`'s gates
and by the authoring digest printed below.

How a passage is measured
-------------------------
1.  The verse's English commentary block is split into paragraphs.
2.  Every paragraph is classified by the kind of point it makes: a meaning
    gloss, Ṭabarī's own judgment, a disagreement among the exegetes, a
    recitation variant, a grammatical observation, historical context, or
    mere scaffolding (an isnād chain, a line of pre-Islamic poetry quoted as
    linguistic evidence). Each class carries a weight, because a chain of
    transmitters and a poem prove a point but do not add one for the reader.
3.  Each paragraph is located on the verse's own Arabic word sequence by the
    Arabic it quotes ("His word: لا تَأْخُذُهُ سِنَةٌ وَلا نَوْمٌ"). Paragraphs
    that quote nothing inherit the last located position, since Ṭabarī's
    reports follow the heading they support. Paragraphs before any located
    heading are a preface to the surah rather than to the verse, and are
    weighted down accordingly.
4.  The weighted points of the paragraphs falling inside a phrase's Arabic
    span become that phrase's budget: more points, more words. There is a
    floor and no ceiling, so depth is never truncated.

    python3 tools/pairs/digest.py SURAH [VERSE]   # authoring digest
    python3 tools/pairs/digest.py --stats 1-43    # corpus measurement
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import source  # noqa: E402

# --- Length rule -----------------------------------------------------------
#
# A phrase's target length grows with the points Ṭabarī makes about it. The
# floor keeps a one-line gloss from collapsing to nothing; there is no ceiling,
# because a passage that carries nine distinct opinions deserves the room to
# report them. The tolerance is proportional too, mirroring the gate the
# withdrawn guidance layer used (tools/guidance/verify.py): short means the
# material was not used, long means padding.

POINT_WORDS = 15          # words of summary per weighted point
FLOOR_WORDS = 40          # a phrase with almost no material still gets this
THIN_RATIO = 0.6          # below this share of target -> material not used
PADDING_BASE = 60         # words of structure every explanation may carry
PADDING_RATIO = 1.5       # above base + ratio x target -> padding
PREFACE_WEIGHT = 0.25     # a surah preface is context, not the verse's own words

# --- Arabic normalisation --------------------------------------------------
#
# The reader's verse text is a Qur'anic orthography full of annotation marks
# (alef wasla, superscript alef, small waw, the dotless-khāh sukun, the small
# high mīm of ʿan li-ghayrihī), while Ṭabarī quotes plain text and an author
# typing a span will type plainer text still. Fold the spelling variants first,
# then drop everything that is not a letter, so بِسۡمِ ٱللَّهِ and بسم الله and
# a hand-typed بسم الله all reduce to the same skeleton.

ARABIC_LETTERS = re.compile(r"[^\u0621-\u063A\u0641-\u064A]")
FOLD = {
    "ٱ": "ا", "أ": "ا", "إ": "ا", "آ": "ا", "ٮ": "ب", "ى": "ي",
    "ئ": "ي", "ؤ": "و", "ة": "ه",
}


def normalize_word(word: str) -> str:
    """Reduce one Arabic token to a comparable skeleton."""
    folded = "".join(FOLD.get(char, char) for char in word)
    return ARABIC_LETTERS.sub("", folded)


def arabic_words(text: str) -> list[str]:
    """The comparable Arabic word skeletons of a text, in order."""
    return [w for w in (normalize_word(t) for t in text.split()) if w]


HAS_ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")

# --- Transliteration -------------------------------------------------------
#
# This translation quotes the verse two ways: in Arabic script ("His word:
# اهْدِنَا") and in transliteration ('The exposition of His word: "Guide us"
# (ahdinā)'). Al-Fātiḥa is mostly the second, so locating a paragraph on the
# verse has to read both. Both sides are reduced to a consonant skeleton:
# Arabic letters through a fixed romanisation, Latin through NFD with the
# combining marks removed, and the vowel carriers (ا و ى ي, aeiouwy) dropped on
# both sides. Doubled letters from an assimilated article collapse, so
# "ar-Raḥmān" and ٱلرَّحۡمَٰنِ meet at "lrhmn".

ARABIC_TO_LATIN = {
    "ء": "'", "آ": "a", "أ": "a", "إ": "a", "ا": "a", "ب": "b", "ة": "t", "ت": "t",
    "ث": "th", "ج": "j", "ح": "h", "خ": "kh", "د": "d", "ذ": "dh", "ر": "r",
    "ز": "z", "س": "s", "ش": "sh", "ص": "s", "ض": "d", "ط": "t", "ظ": "z",
    "ع": "'", "غ": "gh", "ف": "f", "ق": "q", "ك": "k", "ل": "l", "م": "m",
    "ن": "n", "ه": "h", "و": "w", "ى": "a", "ي": "y", "ئ": "y", "ؤ": "w",
    "پ": "b", "چ": "j", "ژ": "z", "گ": "k",
}
VOWEL_CARRIERS = set("aeiouwy'- \t")


def fold_latin(text: str) -> str:
    """Strip transliteration diacritics: ḥ to h, ā to a, ʿayn to an apostrophe."""
    decomposed = unicodedata.normalize("NFD", text)
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    for char in ("ʿ", "ʾ", "’", "\u2019"):
        plain = plain.replace(char, "'")
    return plain.lower()


def latin_skeleton(text: str) -> str:
    """The consonant skeleton of a transliteration."""
    return "".join(c for c in fold_latin(text) if c not in VOWEL_CARRIERS)


def arabic_skeleton(word: str) -> str:
    """The consonant skeleton of one Arabic word, in the same alphabet."""
    romanized = "".join(ARABIC_TO_LATIN.get(c, c) for c in normalize_word(word))
    return "".join(c for c in romanized if c not in VOWEL_CARRIERS)


def verse_skeleton(verse_arabic: str) -> tuple[str, list[tuple[int, int]]]:
    """The verse as one consonant skeleton, plus each word's span inside it."""
    skeletons = [arabic_skeleton(w) for w in verse_arabic.split() if w.strip()]
    full = "".join(skeletons)
    offsets: list[tuple[int, int]] = []
    cursor = 0
    for skeleton in skeletons:
        offsets.append((cursor, cursor + len(skeleton)))
        cursor += len(skeleton)
    return full, offsets


def skeleton_word_range(offsets: list[tuple[int, int]], start: int, end: int) -> tuple[int, int] | None:
    """Which verse words a span of the skeleton covers."""
    low = high = None
    for index, (word_start, word_end) in enumerate(offsets):
        if word_end > start and word_start < end:
            if low is None:
                low = index
            high = index
    return (low, high) if low is not None else None


QUOTED = (re.compile(r"\(([^)]{3,})\)"), re.compile(r'"([^"]{3,})"'), re.compile(r"“([^”]{3,})”"))
ARABIC_RUN = re.compile(r"[^\s]*[\u0621-\u064A][^\s]*(?:\s+[^\s]*[\u0621-\u064A][^\s]*)*")

# --- Paragraph classification ---------------------------------------------
#
# First match wins, so the order is the priority: scaffolding is recognised
# before substance, and a recitation or disagreement heading is recognised
# before the generic meaning gloss inside it.

CLASSES: tuple[tuple[str, float, re.Pattern], ...] = (
    # the translator's own editorial apparatus: footnote numbers, references to
    # the printed edition, to Lisān al-ʿArab, to Sībawayh's page numbers, and
    # criticism of the chains. It is scholarship about Ṭabarī, not Ṭabarī, and
    # the reader is not being given a summary of it, so it is worth nothing
    # here. 3.3% of the corpus's paragraphs, 193,754 words.
    ("apparatus", 0.0, re.compile(
        r"^\(\d{1,4}\)\s|^\[\d{1,4}\]\s|\bLisān al-ʿArab\b|\bthe Lisān\b"
        r"|\bDīwān al-Hudhaliyyīn\b|\bMajāz al-Qurʾān\b|\bTahdhīb\b"
        r"|\bprinted edition\b|\bIbn Ḥajar\b|\bthe Ḥāfiẓ\b|\bsee the earlier narration\b"
        r"|\bSībawayh \d|\bvol\.\s*\d|\bed\.\s*\d|\bḥadīth \d", re.I)),
    # a numbered report, or a paragraph that is essentially a chain of
    # transmitters: it supports a point already made and adds none
    ("chain", 0.03, re.compile(
        r"^\s*\d{3,6}\s*[—-]\s|related (?:to us|to me|this to us)|inform(?:ed|s) us"
        r"|on the authority of|he said:|they said:", re.I)),
    # a line of poetry or a morphological curiosity quoted as evidence
    ("evidence", 0.1, re.compile(
        r"^he means:|^thus he (?:exhorted|meant)|\bsaid:\s*$|the saying of another"
        r"|\bverse of\b|\bpoem\b|\bpoet\b", re.I)),
    # how the word was read: the recitations of the cities
    ("qiraat", 0.8, re.compile(
        r"\breciters?\b|\brecitation\b|\bread (?:this|it)\b|\bwith a vocalized\b"
        r"|\btashdīd\b|\btakhfīf\b|\bqirāʾa\b", re.I)),
    # the exegetes differed, and here is one side of it
    ("disagreement", 0.7, re.compile(
        r"\bsome of them said\b|\bothers said\b|\band others\b|\bthe exegetes"
        r" (?:differed|have differed|disagreed)\b|\bthere is (?:no )?disagreement\b"
        r"|\bmention of (?:who|those) (?:said|said that)\b|\bit is also possible\b"
        r"|\btwo possibilities\b|\bthe first of them is\b|\bthe other possibility\b", re.I)),
    # Ṭabarī's own weighing and verdict
    ("judgment", 1.0, re.compile(
        r"ab[uū] jaʿfar (?:said|says)|\bthe correct (?:view|of the two|exposition)\b"
        r"|\bthe most correct\b|\bindicates the correctness\b|\bhe is answered\b"
        r"|\bit is answered\b|\bif someone (?:says|said)\b|\bsince, then, what we have said\b"
        r"|\bthe correct view is\b|\bis not incorrect\b", re.I)),
    # grammar, morphology and what the sentence leaves out
    ("grammar", 0.6, re.compile(
        r"\bomitted\b|\bsuperfluous\b|\bform \"?faʿ(?:lān|īl|al)\"?\b|\bverbal noun\b"
        r"|\bpassive participle\b|\bactive participle\b|\bthe \"?bāʾ\"?\b|\brequires a verb\b"
        r"|\bgrammatically\b|\biʿrāb\b|\bdeclension\b|\bnominative\b|\baccusative\b"
        r"|\bgenitive\b|\bderivative\b|\bderived from\b", re.I)),
    # the plain sense: what the words mean
    ("meaning", 1.0, re.compile(
        r"\bthat is to say\b|\bmeans\b|\bthe meaning of\b|\bis a clarification\b"
        r"|\bin the language of the arabs\b|\bsignifies\b|\bdenotes\b|\brefers to\b"
        r"|\bexplanation of\b|\bexposition of\b", re.I)),
    # occasion, history and narrative setting
    ("context", 0.6, re.compile(
        r"\bwas revealed\b|\brevealed (?:concerning|about)\b|\boccasion\b|\bwhen the"
        r" prophet\b|\bmount(?:ed)? a riding horse\b|\bhijra\b|\bbadr\b|\bthe story of\b"
        r"|\bhistor(?:y|ical)\b", re.I)),
)
OTHER_CLASS = ("other", 0.25, None)


def classify(paragraph: str) -> tuple[str, float]:
    """The kind of point a paragraph makes, and what it is worth."""
    for name, weight, pattern in CLASSES:
        if pattern and pattern.search(paragraph):
            return name, weight
    return OTHER_CLASS[0], OTHER_CLASS[1]


# --- Passage segmentation and placement -----------------------------------

def paragraphs(block: str) -> list[str]:
    """The paragraphs of a commentary block, in order."""
    return [p.strip() for p in re.split(r"\n\s*\n", block) if p.strip()]


def locate(paragraph: str, skeleton: tuple[str, list[tuple[int, int]]]) -> tuple[int, int] | None:
    """Where on the verse this paragraph is speaking, as (first word, last word).

    The paragraph is searched for anything it quotes from the verse, in Arabic
    script or in transliteration, and the widest quotation that matches wins.
    Returns None when the paragraph quotes nothing of the verse, which is what
    an isnād chain or a follow-on argument looks like.
    """
    full, offsets = skeleton
    if not full:
        return None
    best: tuple[int, int] | None = None

    def offer(span: tuple[int, int] | None) -> None:
        nonlocal best
        if span and (best is None or (span[1] - span[0]) > (best[1] - best[0])):
            best = span

    for match in ARABIC_RUN.finditer(paragraph):
        quoted = "".join(arabic_skeleton(w) for w in match.group(0).split())
        if len(quoted) < 3:
            continue
        start = full.find(quoted)
        if start >= 0:
            offer(skeleton_word_range(offsets, start, start + len(quoted)))

    for pattern in QUOTED:
        for match in pattern.finditer(paragraph):
            candidate = match.group(1)
            if HAS_ARABIC.search(candidate):
                continue
            quoted = latin_skeleton(candidate)
            if len(quoted) < 3:
                continue
            start = full.find(quoted)
            if start >= 0:
                offer(skeleton_word_range(offsets, start, start + len(quoted)))
    return best


def measure(block: str, verse_arabic: str) -> list[dict]:
    """Every paragraph of a passage: its class, weight and place on the verse.

    Paragraphs are returned in passage order. `position` is the located word
    span, `inherited` says whether the span came from an earlier heading, and
    `preface` marks the material Ṭabarī gives before he reaches the verse.
    """
    skeleton = verse_skeleton(verse_arabic)
    out: list[dict] = []
    last: tuple[int, int] | None = None
    reached_verse = False
    for text in paragraphs(block):
        position = locate(text, skeleton)
        if position:
            last = position
            reached_verse = True
        name, weight = classify(text)
        if not reached_verse:
            weight *= PREFACE_WEIGHT
        out.append({
            "text": text,
            "words": len(text.split()),
            "class": name,
            "weight": weight,
            "position": position or last,
            "inherited": position is None,
            "preface": not reached_verse,
        })
    return out


# --- Attribution to phrases ----------------------------------------------

def phrase_spans(arabic_spans: list[str], verse_arabic: str) -> list[tuple[int, int]]:
    """Turn each phrase's Arabic span into (start, end) verse word indices.

    The spans are exact, consecutive pieces of the verse's Arabic, so they
    walk the verse once in order. Raises ValueError when they do not, which is
    what the authoring gate reports.
    """
    verse_words = arabic_words(verse_arabic)
    cursor = 0
    spans: list[tuple[int, int]] = []
    for span in arabic_spans:
        wanted = arabic_words(span)
        if not wanted:
            raise ValueError("empty Arabic span")
        if verse_words[cursor:cursor + len(wanted)] != wanted:
            raise ValueError("Arabic span %r is not the next piece of the verse" % span)
        cursor += len(wanted)
        spans.append((cursor - len(wanted), cursor - 1))
    if cursor != len(verse_words):
        raise ValueError("the Arabic spans leave out %d word(s) of the verse"
                         % (len(verse_words) - cursor))
    return spans


def budget(paragraphs_: list[dict], span: tuple[int, int]) -> dict:
    """The points and the word target for one phrase's slice of the passage."""
    start, end = span
    own = [p for p in paragraphs_
           if p["position"] and start <= p["position"][0] <= end]
    points = sum(p["weight"] for p in own)
    material = sum(p["words"] for p in own)
    classes: dict[str, int] = {}
    for p in own:
        classes[p["class"]] = classes.get(p["class"], 0) + 1
    target = max(FLOOR_WORDS, round(POINT_WORDS * points))
    return {
        "paragraphs": own,
        "points": round(points, 2),
        "material_words": material,
        "classes": classes,
        "target_words": target,
        "min_words": max(FLOOR_WORDS, round(THIN_RATIO * target)),
        "max_words": round(PADDING_BASE + PADDING_RATIO * target),
    }


def length_problem(words: int, target: dict, where: str) -> str | None:
    """Why an explanation's length does not match its material, or None."""
    if words < target["min_words"]:
        return ("%s: %d words is short for its material (%s points from Ṭabarī, "
                "about %d words expected, at least %d)"
                % (where, words, target["points"], target["target_words"], target["min_words"]))
    if words > target["max_words"]:
        return ("%s: %d words is long for its material (%s points from Ṭabarī, "
                "about %d words expected, at most %d) — check for padding"
                % (where, words, target["points"], target["target_words"], target["max_words"]))
    return None


# --- Loading --------------------------------------------------------------

def load_surah(surah: int) -> tuple[dict, dict[str, dict], dict]:
    """The tafsīr payload, the reader's verses, and the authored file."""
    with open(os.path.join(ROOT, "data", "tafsir_%03d.json" % surah), encoding="utf-8") as fh:
        tafsir = json.load(fh)
    verses = source.read_chapter_arabic(surah)
    authored_path = os.path.join(HERE, "authored", "%03d.json" % surah)
    authored = None
    if os.path.exists(authored_path):
        with open(authored_path, encoding="utf-8") as fh:
            authored = json.load(fh)
    return tafsir, verses, authored


def verse_passage(tafsir: dict, ayah: str) -> str:
    """The English Ṭabarī passage published for one verse."""
    mapping = tafsir.get("verses", {}).get(str(ayah))
    if not isinstance(mapping, dict):
        raise KeyError("no commentary mapping for verse %s" % ayah)
    source_id = tafsir.get("primary", "tabari")
    index = mapping.get(source_id)
    blocks = tafsir.get("sets", {}).get(source_id, {}).get("blocks", [])
    if not isinstance(index, int) or not 0 <= index < len(blocks):
        raise KeyError("bad block index for verse %s" % ayah)
    return blocks[index]


# --- Authoring digest ------------------------------------------------------

def print_digest(surah: int, ayah: str | None = None, show_text: bool = True,
                 full_text: bool = False) -> None:
    tafsir, verses, authored = load_surah(surah)
    ayahs = [ayah] if ayah else sorted(verses, key=lambda n: int(n))
    for number in ayahs:
        block = verse_passage(tafsir, number)
        measured = measure(block, verses[number]["ar"])
        print("=" * 78)
        print("%d:%s   Ṭabarī: %d words in %d paragraphs"
              % (surah, number, len(block.split()), len(measured)))
        print("  AR  %s" % verses[number]["ar"])
        print("  EN  %s" % verses[number]["en"])
        entry = (authored or {}).get("verses", {}).get(number, {})
        phrases = entry.get("phrases", [])
        if not phrases:
            print("\n  (not authored yet — the passage measured paragraph by paragraph:)")
            for p in measured:
                print("    %-12s %-9s pos=%-9s %5dw  %s"
                      % (p["class"], "preface" if p["preface"] else ("inherited" if p["inherited"] else "located"),
                         p["position"], p["words"], p["text"][:88].replace("\n", " ")))
            continue
        try:
            spans = phrase_spans([p.get("ar", "") for p in phrases], verses[number]["ar"])
        except ValueError as exc:
            print("\n  ! %s" % exc)
            continue
        preface = [p for p in measured if p["preface"]]
        if preface:
            print("  preface  : %d paragraph(s), %d words, before Ṭabarī reaches the verse"
                  % (len(preface), sum(p["words"] for p in preface)))
            if full_text:
                for p in preface:
                    print("    [%s %dw] %s" % (p["class"], p["words"], p["text"]))
        for phrase, span in zip(phrases, spans):
            info = budget(measured, span)
            words = len(" ".join(phrase.get("explanation", "").split()).split())
            verdict = length_problem(words, info, "draft")
            print("\n  --- words %d-%d of the verse  (%s points, %d source words) ---"
                  % (span[0], span[1], info["points"], info["material_words"]))
            print("  EN piece : %s" % phrase.get("translation", ""))
            print("  AR piece : %s" % phrase.get("ar", ""))
            print("  budget   : about %d words (accept %d-%d)  draft is %d%s"
                  % (info["target_words"], info["min_words"], info["max_words"], words,
                     "" if not verdict else "  ! " + verdict.split(": ", 1)[-1]))
            print("  points   : %s" % ", ".join("%s×%d" % kv for kv in sorted(info["classes"].items())))
            if show_text:
                for p in info["paragraphs"]:
                    if full_text and p["class"] not in ("chain", "evidence"):
                        print("    [%s %dw]\n%s" % (p["class"], p["words"], p["text"]))
                    elif full_text:
                        print("    [%s %dw] (scaffolding, omitted)" % (p["class"], p["words"]))
                    else:
                        print("    [%s%s %dw] %s"
                              % (p["class"], " (preface)" if p["preface"] else "", p["words"],
                                 p["text"][:400].replace("\n", " ")))


def print_stats(surahs: list[int]) -> None:
    totals = {"verses": 0, "phrases": 0, "target": 0, "material": 0}
    per_class: dict[str, int] = {}
    targets: list[int] = []
    for surah in surahs:
        tafsir, verses, authored = load_surah(surah)
        if not authored:
            continue
        for number, entry in authored.get("verses", {}).items():
            spans_text = [p.get("ar") for p in entry.get("phrases", [])]
            if not all(spans_text):
                continue
            block = verse_passage(tafsir, number)
            measured = measure(block, verses[number]["ar"])
            try:
                spans = phrase_spans(spans_text, verses[number]["ar"])
            except ValueError:
                continue
            totals["verses"] += 1
            for span in spans:
                info = budget(measured, span)
                totals["phrases"] += 1
                totals["target"] += info["target_words"]
                totals["material"] += info["material_words"]
                targets.append(info["target_words"])
                for name, count in info["classes"].items():
                    per_class[name] = per_class.get(name, 0) + count
    targets.sort()
    print("measured verses : %d" % totals["verses"])
    print("measured phrases: %d" % totals["phrases"])
    if targets:
        print("target words    : median %d  p90 %d  max %d  total %s"
              % (targets[len(targets) // 2], targets[int(len(targets) * 0.9)], targets[-1],
                 format(totals["target"], ",")))
    print("paragraph classes: %s" % ", ".join("%s %d" % kv for kv in sorted(per_class.items(), key=lambda x: -x[1])))


def parse_spec(spec: str) -> list[int]:
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            low, high = part.split("-", 1)
            out.extend(range(int(low), int(high) + 1))
        else:
            out.append(int(part))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("surah", nargs="?", type=int, help="surah to digest")
    parser.add_argument("verse", nargs="?", help="one verse of that surah")
    parser.add_argument("--stats", metavar="SURAH-SPEC", help="measure a range, e.g. 1-43")
    parser.add_argument("--quiet", action="store_true", help="omit the source paragraph text")
    parser.add_argument("--full", action="store_true",
                        help="print the whole source of each substantive paragraph, "
                             "for authoring from it")
    args = parser.parse_args()

    if args.stats:
        print_stats(parse_spec(args.stats))
        return 0
    if not args.surah:
        parser.error("give a surah, or --stats SURAH-SPEC")
    print_digest(args.surah, args.verse, show_text=not args.quiet, full_text=args.full)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
