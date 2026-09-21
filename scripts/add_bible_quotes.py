#!/usr/bin/env python3
"""
Give the Bible citations in the commentaries the same treatment the Qur'an
references already have: the wording of the verse, quoted next to the reference.

Text comes from data/bible_web.json — the World English Bible (public domain),
one entry per cited passage, keyed "Book c:v" or "Book c:v-c:v". Adding an entry
is all that is needed to cover another citation; passages with no entry are
counted and left alone, so this tool is safe to re-run as the data grows.

Like add_verse_quotes.py it is strictly additive: no citation is ever removed
or renumbered, and a citation that already carries wording is left untouched.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verse_quotes import (  # noqa: E402
    CORPUS, clean_quote, load_translation, norm, pick_phrase,
)

BOOKS = (r"Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|"
         r"Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Isaiah|"
         r"Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|"
         r"Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|"
         r"Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|"
         r"Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation")
CITE = re.compile(r"((?:\d\s)?(?:" + BOOKS + r"))\s+(\d{1,3}):(\d{1,3})"
                  r"(?:\s*[–-]\s*(?:\d{1,3}:)?(\d{1,3}))?")
# a bare "c:v" that follows a book citation inside the same parenthetical:
#   (Judges 6:21; 13:20)
FOLLOWER = re.compile(r"\s*[;,]\s*(\d{1,3}):(\d{1,3})(?:\s*[–-]\s*(\d{1,3}))?")
# a wording already sitting immediately before the parenthetical
PRE_QUOTED = re.compile(r"[”\"’]\*{0,2}\s*[–—-]?\s*$")
ALREADY = re.compile(r"^\s*[’']?\s*(?:—|–)\s*\*“")


QURAN = ()


class Report:
    def __init__(self):
        self.filled = self.skipped = self.no_text = self.whole = 0
        self.missing = []
        self.samples = []

    def show(self, applied):
        print(f"Bible citations given wording ......... {self.filled}")
        print(f"  ...of which the whole passage ...... {self.whole}")
        print(f"already carried wording .............. {self.skipped}")
        print(f"no text in data/bible_web.json ....... {self.no_text}")
        for k in sorted(set(self.missing)):
            print(f"    missing: {k}")
        print(f"applied: {applied}")


STOP = {"the","a","an","of","to","and","in","is","are","was","were","that","this","it",
        "for","on","with","be","he","she","they","i","you","his","her","their","my","your",
        "not","but","as","at","by","from","we","us","them","him","all","who","what","will"}


def content_words(text):
    return {w for w in norm(text).split() if w.isalpha() and len(w) > 2} - STOP


def quran_index(tr):
    """Every ayah wording, as content words, for telling a Qur'an quote from a Bible one."""
    return [content_words(v) for surah in tr.values() for v in surah.values()]


def overlap(q, words):
    """Fraction of the quote's own content words the candidate also has."""
    if not q:
        return 0.0
    return len(q & words) / len(q)


def is_bible_wording(q, verse):
    """True when the wording ahead of the parenthetical already IS this passage.

    Substring matching is not enough: the corpus also writes Qur'an verses by
    hand in its own words (“We drowned Pharaoh and his hosts”), and those must
    not be mistaken for the Bible passage and left without one.
    """
    best_q = max((overlap(q, ayah) for ayah in QURAN), default=0.0)
    best_b = overlap(q, content_words(verse)) if verse else 0.0
    return best_b >= best_q and best_b > 0.5


def key_of(book, chap, a, b):
    return f"{book} {chap}:{a}" + (f"-{chap}:{b}" if b else "")


def pseudo_translation(data):
    """Shape the passage table like load_translation() so pick_phrase applies."""
    tr = {}
    for k, text in data.items():
        if k.startswith("_"):
            continue
        m = re.match(r"(.+?) (\d+):(\d+)(?:-\d+:(\d+))?$", k)
        if not m:
            continue
        book, chap, a = m.group(1), int(m.group(2)), int(m.group(3))
        tr.setdefault(book, {}).setdefault(chap, text)
        tr[book]["_" + k] = (a, text)
    return tr


def process(text, data, tr, report, preview=0):
    edits = []
    for m in CITE.finditer(text):
        book = m.group(1).strip()
        chap, a = int(m.group(2)), int(m.group(3))
        b = int(m.group(4)) if m.group(4) else None
        if b and b < a:
            b = None
        st = text.rfind("(", 0, m.start())
        key = key_of(book, chap, a, b)
        verse = data.get(key)
        # The corpus writes both a Qur'an quote and a Bible quote as
        # *“…”* (ref), so shape alone cannot tell them apart: only skip when
        # the wording ahead of the parenthetical really is this passage.
        head = text[max(0, st - 320):st] if st != -1 else ""
        prior = PRE_QUOTED.search(head)
        if prior:
            said = re.findall(r"\*?“([^”]{8,})”\*?", head)
            if said:
                q = content_words(said[-1])
                # The wording ahead of the parenthetical is either this Bible
                # passage in another translation, or a Qur'an verse the sentence
                # happens to quote on the way to the Bible citation. Only the
                # second still needs the passage inserted.
                if q and is_bible_wording(q, verse):
                    report.skipped += 1
                    continue
        after = text[m.end():m.end() + 6]
        if ALREADY.match(after):
            report.skipped += 1
            continue
        if verse is None:
            report.no_text += 1
            report.missing.append(key)
            continue
        # the commentary around the citation says which part of it matters
        ctx = re.sub(r"\s+", " ", text[max(0, m.start() - 340):m.start()] + " "
                     + text[m.end():m.end() + 200])
        q, sc = pick_phrase(tr, book, chap, chap, ctx, ctx)
        q = clean_quote(q or verse)
        if not q:
            continue
        # a clause this short carries no meaning on its own — widen it
        if len(q) < 45:
            wide_q = clean_quote(verse)
            cut = 0
            for sm in re.finditer(r"[.;:!?”]\s", wide_q):
                if sm.end() >= 70:
                    cut = sm.start() + 1
                    break
            cand = wide_q[:cut] if cut else wide_q
            if len(cand) > len(q) and len(cand) <= 300:
                q = cand
                sc = 0
        # the wrapper supplies the quotation marks; a passage that already
        # opens or closes with them would give *“…””*
        if q.startswith("“"):
            q = q[1:].lstrip()
        if q.endswith("”"):
            q = q[:-1].rstrip()
        edits.append((m.end(), f' — *“{q}”*'))
        report.filled += 1
        if sc == 0:
            report.whole += 1
        if len(report.samples) < 200:
            report.samples.append((key, ctx[-90:], q))
    if preview:
        for pos, rep in edits[:preview]:
            print(f"  …{re.sub(r'[ ]+', ' ', text[max(0, pos - 130):pos])}")
            print(f"  →{rep}\n")
    for pos, rep in sorted(edits, reverse=True):
        text = text[:pos] + rep + text[pos:]
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--chapter", type=int, default=0)
    args = ap.parse_args()

    data = json.loads((CORPUS.parent / "data" / "bible_web.json")
                      .read_text(encoding="utf-8"))
    tr = pseudo_translation(data)
    global QURAN
    QURAN = quran_index(load_translation())
    report = Report()
    changed = 0
    for ch in ([args.chapter] if args.chapter else range(1, 115)):
        path = CORPUS / f"{ch:03d}.md"
        src = path.read_text(encoding="utf-8")
        new = process(src, data, tr, report, args.preview)
        if new != src:
            changed += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")
    print(f"\nchapters that change: {changed}\n")
    report.show(args.apply)


if __name__ == "__main__":
    main()
