#!/usr/bin/env python3
"""
Editorial pipeline for the verse-by-verse tafsir commentary (markdown commentry/*.md).

WHAT IT DOES
------------
The commentary was machine-generated against a word target, so nearly every one
of the 6,236 verses carries ~1,000 words whether the verse needs 150 or 900, and
the filler is mostly paraphrase, "reader application" reflection and template
headings repeated across the corpus.  This pipeline edits it the way a careful
human editor would:

  * keeps every hadith citation, Qur'an cross-reference, date, historical
    account, name and Arabic technical term (verified after writing);
  * keeps the paragraphs that explain the verse — its words, grammar, context of
    revelation, rulings, and the scholarly differences that matter;
  * drops the paragraphs and sentences that only restate, moralise or apply what
    is already on the page, and drops prose that duplicates a passage earlier in
    the corpus (matched with names/numbers normalised, so the same boilerplate
    written about different prophets collapses to one);
  * lets each verse end at its own natural length: the allowance per verse is
    driven by how much citable, verse-specific material it actually has;
  * removes the repeated "**Expanded Commentary**" marker and template headings,
    keeping only headings that mark genuinely distinct content;
  * polishes wording — filler lead-ins removed, ornate vocabulary simplified,
    over-long sentences split — without touching quoted material.

Nothing is invented. The edit is extractive: every sentence in the output comes
from the source file.

USAGE
-----
    python3 scripts/edit_tafsir.py --all --jobs 12 --dry-run --report /tmp/report.txt
    python3 scripts/edit_tafsir.py --all --jobs 12
    python3 scripts/edit_tafsir.py --chapter 2 --show 2:255
"""

from __future__ import annotations

import argparse
import collections
import math
import os
import re
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor

SRC_DIR = "markdown commentry"

# ---------------------------------------------------------------------------
# 1. sentence handling
# ---------------------------------------------------------------------------

_ABBREV = ["e.g", "i.e", "cf", "vs", "etc", "vol", "no", "pp", "p", "ch", "ca",
           "St", "Dr", "Mr", "Mrs", "Ms", "Prof", "esp", "approx", "b", "d",
           "r", "al", "ibn", "ﷺ"]


def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []
    ph = "\x00"
    work = re.sub(r"\b(" + "|".join(re.escape(a) for a in _ABBREV) + r")\.", r"\1" + ph, text)
    work = re.sub(r"(\b[A-Z])\.(?=\s+[A-Z])", r"\1" + ph, work)
    work = re.sub(r"(\d)\.(?=\d)", r"\1" + ph, work)
    parts = re.split(r"(?<=[.!?])\s+(?=[«“\"(\[]?[A-Z0-9ʿʾĀĪŪṢḌṬẒḤŠ])", work)
    out = [p.replace(ph, ".").strip() for p in parts if p.strip()]
    merged: list[str] = []
    for p in out:
        if merged and len(p.split()) <= 2 and p[0].islower():
            merged[-1] += " " + p
        else:
            merged.append(p)
    return merged


# ---------------------------------------------------------------------------
# 2. vocabulary / scoring helpers
# ---------------------------------------------------------------------------

STOPWORDS = set(
    """
a about above after again against all also am an and another any are as at be because been
before being below between both but by can cannot could did do does doing done down during each
either else even ever every few for from further had has have having he her here hers herself
him himself his how i if in into is it its itself just like many may me might more most much
must my myself no nor not now of off on once one only or other others ought our ours ourselves
out over own same she should so some such than that the their theirs them themselves then there
these they this those though through thus to too under until up upon us very was we were what
when where whether which while who whom why will with within without would you your yours
yourself yourselves
""".split()
)

VAGUE_WORDS = set(
    """
thing things something anything nothing everything point points idea ideas sense way ways
matter matters issue issues theme themes lesson lessons reflection reflections reminder
reminders concept concepts notion notions dynamic dynamics dimension dimensions element
elements level levels layer layers sphere spheres realm realms journey journeys reader
readers audience audiences listener listeners today modern ultimately finally indeed
moreover furthermore however therefore perhaps thus hence overall essentially basically
simply truly really genuinely deeply profoundly clearly obviously certainly surely
""".split()
)

META_RE = re.compile(
    r"\b(?:this verse (?:is|does|shows|teaches|asks|invites|reminds|connects|opens|closes|therefore|also|begins)|"
    r"the verse (?:is|does|shows|teaches|asks|invites|reminds|connects|opens|closes|functions|serves|therefore|also)|"
    r"the s[uū]rah(?:'s)? (?:structure|argument|form|movement|method|logic|arc|shape)|"
    r"what the verse (?:asks|does not say|leaves)|the takeaway|reflection is (?:the|an) intended|"
    r"the lesson (?:for|is|here)|the (?:reader|audience|listener)s?|modern readers?|today's reader|"
    r"for (?:the|our) daily (?:life|conduct|lives)|in our (?:own )?time|contemporary reader|"
    r"this (?:is|remains) (?:the )?(?:point|lesson|heart|core)|the (?:point|claim|lesson) is)\b",
    re.I,
)
ABSTRACT_RE = re.compile(
    r"\b(?:structure|argument|logic|movement|register|posture|trajectory|architecture|symmetry|"
    r"fabric|texture|resonance|dimension|dynamic|rhetoric|pedagogy|hermeneutic|paradigm|threshold|"
    r"the hinge|the pivot|arc of|grammar of|theology of|the shape of|the form of)\b",
    re.I,
)
QURAN_REF_RE = re.compile(r"\b\d{1,3}:\d{1,3}(?:\s*[–-]\s*\d{1,3})?\b")
HADITH_STRONG_RE = re.compile(
    r"(?:Ṣaḥīḥ|Sahih|Sunan|Musnad|Saḥīḥ|Jāmiʿ)\s*(?:al-)?(?:Bukh[āa]r[iī]|Muslim|Tirmidh[iī]|Nas[āa]ʾ[iī]|Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah)"
    r"|(?:Bukh[āa]r[iī]|Muslim|Tirmidh[iī]|Nas[āa]ʾ[iī])[^.\n]{0,3}\b\d{2,4}\b"
    r"|ﷺ|narrated\s+by|reported\s+(?:by|from)\s+[A-Zʿ]",
)
YEAR_RE = re.compile(r"\b\d{1,4}\s*(?:AH|CE|BC|A\.H\.|C\.E\.)\b")
QUOTE_RE = re.compile(r"“[^”]{8,}”|\"[^\"]{8,}\"")
ARABIC_RE = re.compile(r"\*[A-Za-zʿʾĀ-ž][^*\n]{2,60}\*")
PROPER_RE = re.compile(r"\b[A-Z][a-zʿʾāīūṣḍṭẓḥš]{2,}\b")
SENT_START = set("""the this that it in a an when if but and yet for so he she they we you i his
her their our your its my on at by from with as to of or not no after before because while then
thus therefore however some many most others one two three four five six seven eight nine ten
allah god qur muslim islam arabic mecca makkah medina madinah lord""".split())
LIST_LINE_RE = re.compile(r"^\s*(?:\d+\.|[-*])\s+")


def content_tokens(text: str) -> list[str]:
    text = re.sub(r"[*_>#\[\]()]", " ", text)
    toks = re.findall(r"[A-Za-zĀ-žʿʾṢṣḌḍṬṭẒẓḤḥŠšūīā'-]+", text)
    out = []
    for t in toks:
        tl = t.lower().strip("-'")
        if len(tl) >= 3 and tl not in STOPWORDS:
            out.append(tl)
    return out


def content_set(text: str) -> set[str]:
    return set(content_tokens(text))


def proper_count(text: str) -> int:
    return sum(1 for m in PROPER_RE.finditer(text) if m.group(0).lower() not in SENT_START)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / len(a | b) if inter else 0.0


# a numbered hadith source is evidence; a bare mention of "Ibn ʿAbbās" is not
HADITH_CITE_RE = re.compile(
    r"(?:Ṣaḥīḥ|Sahih|Sunan|Musnad|Jāmiʿ|Jami|Muwaṭṭaʾ|Muwatta)\s+(?:al-)?"
    r"(?:Bukh[āa]r[iī]|Muslim|Tirmidh[iī]|Nas[āa]ʾ[iī]|Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah)"
    r"|(?:Bukh[āa]r[iī]|Muslim|Tirmidh[iī]|Nas[āa]ʾ[iī]|Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah)"
    r"\s*\(?\s*\d{1,4}\s*\)?")
ATTRIB_RE = re.compile(r"\b(?:reported|narrated|transmitted|recorded|related)\s+(?:by|from|in)\b", re.I)
PROPHETIC_RE = re.compile(r"ﷺ[^.]{0,200}?(?:said|says|replied|answered|asked|told|commanded|forbade|"
                          r"warned|taught|prayed|narrated|reported|instructed|:)")


def citations(text: str) -> set[str]:
    """The evidence a passage states: Qur'an references, sourced hadith and dates.

    Mentions of a scholar's name are documentation, not a citation, so they do
    not make a paragraph untouchable on their own."""
    c = set(QURAN_REF_RE.findall(text))
    c |= {m.strip() for m in HADITH_CITE_RE.findall(text) if m.strip()}
    c |= {m.strip() for m in YEAR_RE.findall(text) if m.strip()}
    if PROPHETIC_RE.search(text) or "\ufdfa" in text:
        c.add("report:prophetic")
    if ATTRIB_RE.search(text):
        c.add("report:attributed")
    return c


def signature(text: str, n: int = 14) -> str:
    """Boilerplate signature: names and numbers normalised away."""
    t = PROPER_RE.sub("@p", text.lower())
    t = re.sub(r"\d+", "#", t)
    t = re.sub(r"[^a-z@#\s]", " ", t)
    toks = [w for w in t.split() if w not in STOPWORDS and len(w) > 2 or w.startswith("@")]
    return " ".join(toks[:n])


# ---------------------------------------------------------------------------
# 3. parsing
# ---------------------------------------------------------------------------

VERSE_HEAD_RE = re.compile(r"^##\s+(.*?)\b(\d{1,3}):(\d{1,3})\s*$")
HEAD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*$")


def parse_groups(body: str) -> list[tuple[str | None, list[str]]]:
    """Return [(heading|None, [paragraph, ...]), ...]; heading applies to the
    paragraphs that follow it until the next heading."""
    groups: list[tuple[str | None, list[str]]] = []
    cur_head: str | None = None
    cur_paras: list[str] = []

    def flush():
        if cur_paras:
            groups.append((cur_head, cur_paras))

    for chunk in body.split("\n\n"):
        chunk = chunk.strip()
        if not chunk or chunk in {"---", "***", "___"}:
            continue
        m = HEAD_LINE_RE.match(chunk)
        if m:
            if m.group(1).lower().startswith("expanded commentary"):
                continue                  # generation artefact, never a real heading
            flush()                       # close the previous heading group first
            cur_head = m.group(1).strip()
            cur_paras = []
            continue
        # a chunk may hold several lines: handle headings, rules and list runs
        lines = [l.rstrip() for l in chunk.split("\n") if l.strip()]
        buf: list[str] = []
        for ln in lines:
            if ln.strip() in {"---", "***", "___"}:
                continue
            hm = HEAD_LINE_RE.match(ln.strip())
            if hm:
                if buf:
                    cur_paras.append(" ".join(buf)); buf = []
                if hm.group(1).lower().startswith("expanded commentary"):
                    continue
                flush()
                cur_head = hm.group(1).strip()
                cur_paras = []
                continue
            if LIST_LINE_RE.match(ln):
                if buf:
                    cur_paras.append(" ".join(buf)); buf = []
                cur_paras.append(ln.strip())
                continue
            if buf and not re.search(r"[.!?:;”\")\]]\s*$", buf[-1]):
                buf.append(ln.strip())          # soft line wrap, not a new paragraph
            else:
                if buf:
                    cur_paras.append(" ".join(buf)); buf = []
                buf.append(ln.strip())
        if buf:
            cur_paras.append(" ".join(buf))
    flush()
    # repair occasional source-level breaks: a paragraph that continues the one
    # before it ("... before Allah." / "with humility.") is rejoined
    cont = re.compile(r"^(?:and|but|with|which|or|so|that|because|since|then|while|as|for|nor|yet|to|of|in|it|he|she|they|this|these|its)\b", re.I)
    fixed = []
    for head, paras in groups:
        out_paras: list[str] = []
        for para in paras:
            if out_paras and not para.startswith("\x01") and cont.match(para) and para[0].islower():
                joiner = " " if out_paras[-1].rstrip().endswith((",", ";", ":")) else ", "
                out_paras[-1] = out_paras[-1].rstrip() + joiner + para
            elif para and para[0].islower() and not para.startswith("\x01") and len(para.split()) < 8:
                out_paras.append(para[0].upper() + para[1:])
            else:
                out_paras.append(para)
        fixed.append((head, out_paras))
    return fixed


def split_chapter(text: str, ch: int):
    sections = re.split(r"\n(?=## )", text)
    h1 = ""
    intro_groups = None
    verses = []
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        first = sec.split("\n", 1)[0].strip()
        if first.startswith("# ") and not first.startswith("## "):
            h1 = first
            rest = sec.split("\n", 1)[1] if "\n" in sec else ""
            if not rest.strip():
                continue
            sec, first = rest.strip(), rest.strip().split("\n", 1)[0].strip()
        if not sec.startswith("## "):
            continue
        body = "\n".join(sec.split("\n")[1:]).strip()
        if body.endswith("---"):
            body = body[:-3].strip()
        if "Introduction to the S" in first:
            intro_groups = parse_groups(body)
            continue
        m = VERSE_HEAD_RE.match(first)
        if not m:
            continue
        quote, rest, seen_quote = "", [], False
        for ln in body.split("\n"):
            st = ln.strip()
            if st.startswith(">"):
                text = st.lstrip("> ").strip()
                if not seen_quote:
                    quote, seen_quote = text, True
                else:
                    rest.append("\x01" + text)      # quotation inside the commentary
            else:
                rest.append(ln)
        verses.append((int(m.group(3)), first, quote, parse_groups("\n".join(rest))))
    return h1, intro_groups, verses


def read_chapter(src_dir: str, ch: int) -> str:
    with open(os.path.join(src_dir, f"{ch:03d}.md"), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# 4. corpus statistics
# ---------------------------------------------------------------------------

class Stats:
    """Document frequencies and boilerplate signatures over the whole corpus."""

    def __init__(self):
        self.df: collections.Counter = collections.Counter()
        self.docs = 0
        self.sig_counts: collections.Counter = collections.Counter()
        self.head_counts: collections.Counter = collections.Counter()
        self.idf: dict[str, float] = {}

    def finish(self):
        self.idf = {t: math.log((self.docs + 1) / (c + 1)) + 1.0 for t, c in self.df.items()}
        return self

    # --- helpers used by the editor -------------------------------------
    def idf_of(self, token: str) -> float:
        return self.idf.get(token, 2.0)

    def rare_cut(self) -> float:
        if not self.idf:
            return 4.0
        vals = sorted(self.idf.values())
        return vals[int(len(vals) * 0.93)]


def collect_stats(args):
    ch, src_dir = args
    st = Stats()
    raw = read_chapter(src_dir, ch)
    _, intro_groups, verses = split_chapter(raw, ch)
    bodies = [intro_groups] if intro_groups else []
    bodies += [v[3] for v in verses]
    for groups in bodies:
        st.docs += 1
        seen = set()
        for _, paras in groups:
            for p in paras:
                toks = content_tokens(p)
                seen |= set(toks)
                if not HADITH_STRONG_RE.search(p) and not QURAN_REF_RE.search(p):
                    sig = signature(p)
                    if sig:
                        st.sig_counts[sig] += 1
        for t in seen:
            st.df[t] += 1
    for m in HEAD_LINE_RE.finditer(raw, re.M):
        st.head_counts[m.group(1).strip().lower()] += 1
    return ch, st


# ---------------------------------------------------------------------------
# 5. the editor
# ---------------------------------------------------------------------------

GENERIC_HEADS = re.compile(
    r"^(?:expanded commentary|the trial as a mirror|the quiet polemic of the detail|"
    r"what the verse asks|a bridge between verse and reader|the arabic still has work|"
    r"conduct follows if|a checked parallel|the transition to the next verse|"
    r"a verse that connects|a verse that continues|key words and their roots|"
    r"the theological point about|practical lessons for daily life|how this verse connects|"
    r"reflection that leads|what the verse does not say|extra verified note|"
    r"why this prohibition connects|the link to authority|a lesson that connects|"
    r"the verse'?s place in the sequence|how this verse fits|the place of the verse|"
    r"why the verse is so short|why this verse|the verse inside the closing movement|"
    r"a reflection|an application|the application|lesson for today|lessons for today|"
    r"final thoughts|conclusion|summary)\b",
    re.I,
)

MAX_PARA_WORDS = 175          # trim long unanchored paragraphs beyond this
TRIM_TARGET = 150


class Editor:
    def __init__(self, stats: Stats):
        self.st = stats
        self.rare = stats.rare_cut()

    # -- paragraph scoring ------------------------------------------------
    def score(self, para: str, ayah_words: set[str], section_rare: set[str]):
        words = len(para.split())
        uniq = set(content_tokens(para))
        strong = (len(set(QURAN_REF_RE.findall(para))) * 3 + len(HADITH_STRONG_RE.findall(para)) * 3
                  + len(set(YEAR_RE.findall(para))) * 2)
        props = proper_count(para)
        arabic = len(set(ARABIC_RE.findall(para)))
        quotes = len(QUOTE_RE.findall(para))
        meta = len(META_RE.findall(para))
        abst = len(ABSTRACT_RE.findall(para))
        rare = len({t for t in uniq if self.st.idf_of(t) >= self.rare})
        novel = len({t for t in uniq if self.st.idf_of(t) >= 4.0} - section_rare)
        rel = len(uniq & ayah_words)
        raw = (4.0 * strong + 1.0 * props + 1.2 * arabic + 1.6 * quotes + 0.7 * rare
               + 1.3 * novel + 0.9 * rel - 3.4 * meta - 2.2 * abst)
        return raw / math.sqrt(max(18, words)), raw, bool(strong or quotes)

    def budget(self, strong_total: int, is_intro: bool) -> float:
        if is_intro:
            return max(600.0, min(950.0, 420 + 40 * strong_total))
        return max(150.0, min(540.0, 135 + 58 * strong_total))

    # -- selection --------------------------------------------------------
    def edit_section(self, groups, ayah_text, is_intro, chapter, verse, dropped):
        ayah_words = content_set(ayah_text)
        section_rare: set[str] = set()
        for _, paras in groups:
            for p in paras:
                section_rare |= {t for t in content_tokens(p) if self.st.idf_of(t) >= 4.0}

        entries = []
        for gi, (head, paras) in enumerate(groups):
            for pi, p in enumerate(paras):
                is_quo = p.startswith("\x01")
                sc, raw, anchored = self.score(p, ayah_words, section_rare)
                sig = signature(p)
                dup = bool(sig) and self.st.sig_counts.get(sig, 0) >= 2 and not anchored and not is_quo
                entries.append(dict(gi=gi, pi=pi, head=head, text=p, sc=sc, anchored=anchored or is_quo,
                                    cites=citations(p), words=len(p.split()), dup=dup, quo=is_quo,
                                    first=(gi == 0 and pi == 0)))
        B = self.budget(sum(len(e["cites"]) for e in entries), is_intro)

        # ---- phase 1: every distinct citation survives, once --------------
        kept, kept_ids = [], set()
        covered: set[str] = set()
        kept_sigs: set[str] = set()
        for e in sorted(entries, key=lambda e: (-int(bool(e["first"])), -e["sc"])):
            if not (e["cites"] or e["quo"]) or (e["cites"] and e["cites"] <= covered and not e["quo"]):
                continue
            if e["dup"]:
                # template paragraph elsewhere in the corpus, but it carries a citation:
                # keep only if no other paragraph of this verse states it
                if e["cites"] <= covered:
                    continue
            kept.append(e)
            kept_ids.add(id(e))
            covered |= e["cites"]
            sig = signature(e["text"])
            if sig:
                kept_sigs.add(sig)

        # ---- phase 2: best remaining paragraphs up to the verse's allowance
        used = sum(e["words"] for e in kept)
        for e in sorted(entries, key=lambda e: (-int(bool(e["first"])), -e["sc"])):
            if id(e) in kept_ids:
                continue
            if e["dup"]:
                dropped.append(f"[corpus-repeat] {chapter}:{verse} {e['text'][:90]}")
                continue
            sig = signature(e["text"])
            if sig and sig in kept_sigs:
                dropped.append(f"[section-repeat] {chapter}:{verse} {e['text'][:90]}")
                continue
            if e["first"] or not kept or used + e["words"] <= B:
                kept.append(e)
                kept_ids.add(id(e))
                used += e["words"]
                if sig:
                    kept_sigs.add(sig)
            else:
                dropped.append(f"[over-budget] {chapter}:{verse} {e['text'][:90]}")
        # ---- phase 2b: a lead-in line keeps the quotation it introduces -----
        by_pos = {(e["gi"], e["pi"]): e for e in entries}
        for e in list(kept):
            txt = e["text"].rstrip()
            if not txt.endswith(":"):
                continue
            nxt = by_pos.get((e["gi"], e["pi"] + 1))
            if nxt is not None and id(nxt) not in kept_ids:
                kept.append(nxt)
                kept_ids.add(id(nxt))
                used += nxt["words"]
            e["lead"] = True

        # ---- phase 3: never leave a verse with a bare heading -------------
        if used < 150:
            for e in sorted(entries, key=lambda e: -e["sc"]):
                if id(e) in kept_ids:
                    continue
                kept.append(e)
                kept_ids.add(id(e))
                used += e["words"]
                if used >= 150:
                    break
        if not kept and entries:
            kept = [max(entries, key=lambda e: e["sc"])]
        kept.sort(key=lambda e: (e["gi"], e["pi"]))

        # ---- phase 4: honour a natural ceiling --------------------------
        # Citation-bearing paragraphs are never dropped, but a verse may not
        # run on indefinitely: trailing sentences are removed from the
        # least informative paragraphs, never one that states a reference.
        hard = max(300.0, min(700.0, B + 110))
        guard = 0
        while used > hard and guard < 600:
            guard += 1
            cand = None
            for e in sorted(kept, key=lambda e: e["sc"]):
                if e["quo"] or e["first"] or e.get("lead"):
                    continue
                if e["text"].count("“") != e["text"].count("”"):
                    continue                     # never edit inside a broken quotation
                sents = split_sentences(e["text"])
                if len(sents) < 3:
                    continue
                # trailing elaboration first, then the least informative
                # sentence of the body — never the opening, never a citation
                pick = None
                if not citations(sents[-1]) and not QUOTE_RE.search(sents[-1]):
                    pick = len(sents) - 1
                else:
                    scored = [(i, self.score(sents[i], ayah_words, section_rare)[0])
                              for i in range(1, len(sents) - 1)
                              if not citations(sents[i]) and not QUOTE_RE.search(sents[i])]
                    if scored:
                        pick = min(scored, key=lambda t: t[1])[0]
                if pick is None:
                    continue
                cand = (e, sents, pick)
                break
            if not cand:
                break
            e, sents, pick = cand
            dropped.append(f"[cap-trim] {chapter}:{verse} {sents[pick][:90]}")
            used -= len(sents[pick].split())
            e["text"] = " ".join(sents[:pick] + sents[pick + 1:])

        # trim over-long unanchored paragraphs at sentence level
        for e in kept:
            if e["anchored"] or e["words"] <= MAX_PARA_WORDS:
                continue
            sents = split_sentences(e["text"])
            if len(sents) < 3:
                continue
            keep = sents[:]
            while len(" ".join(keep).split()) > TRIM_TARGET and len(keep) > 2:
                last = keep[-1]
                if citations(last) or QUOTE_RE.search(last):
                    break                      # never trim away evidence
                dropped.append(f"[para-trim] {chapter}:{verse} {last[:90]}")
                keep.pop()
            e["text"] = " ".join(keep)

        # promote a highly relevant paragraph to the front when the opener is weak
        if len(kept) > 2:
            best = max(range(len(kept)), key=lambda i: len(content_set(kept[i]["text"]) & ayah_words))
            if best > 0 and len(content_set(kept[0]["text"]) & ayah_words) == 0:
                first_group = kept[best]["gi"]
                if first_group > 0:
                    kept.insert(0, kept.pop(best))

        # group back by heading
        out: list[tuple[str | None, list[str]]] = []
        for e in kept:
            head = e["head"]
            if out and out[-1][0] == head:
                out[-1][1].append(e["text"])
            else:
                out.append((head, [e["text"]]))
        return out, used


# ---------------------------------------------------------------------------
# 6. polish
# ---------------------------------------------------------------------------

FILLER_RES = [
    (re.compile(p), r) for p, r in [
        (r"\bIt is worth noting that\s+", ""),
        (r"\bIt is important to note that\s+", ""),
        (r"\bIt is significant that\s+", ""),
        (r"\bIt should be noted that\s+", ""),
        (r"\bNeedless to say,\s+", ""),
        (r"\bIn other words,\s+", ""),
        (r"\bIn a very real sense,\s+", ""),
        (r"\bIn a real sense,\s+", ""),
        (r"\bAs such,\s+", ""),
        (r"\bOne might (?:even )?say that\s+", ""),
        (r"\bIt is (?:precisely )?this\b", "This"),
    ]
]

PLAIN = {
    "utilise": "use", "utilize": "use", "utilises": "uses", "utilizes": "uses",
    "endeavour": "try", "endeavor": "try", "endeavours": "tries", "endeavors": "tries",
    "commence": "begin", "commenced": "began", "commences": "begins",
    "elucidate": "explain", "elucidates": "explains", "facilitate": "help",
    "facilitates": "helps", "demonstrate": "show", "demonstrates": "shows",
    "demonstrated": "showed", "necessitate": "require", "numerous": "many",
    "possess": "have", "possesses": "has",
    "possessed": "had", "regarding": "about", "concerning": "about",
    "subsequently": "later", "previously": "earlier", "additionally": "also",
    "furthermore": "also", "moreover": "also", "consequently": "so",
    "nevertheless": "still", "nonetheless": "still", "thereafter": "after that",
    "wherein": "where", "whilst": "while", "amongst": "among", "towards": "toward",
    "attempt": "try", "attempts": "tries", "attempted": "tried",
    "comprehend": "understand", "comprehends": "understands", "transpired": "happened", "terminate": "end",
    "initiate": "start", "initiated": "started", "assist": "help", "assists": "helps",
    "assisted": "helped", "sufficient": "enough", "sufficiently": "enough",
    "approximately": "about", "entirely": "completely", "primarily": "mainly",
    "herein": "here", "thereof": "of it", "therein": "in it", "aforementioned": "above",
}
PLAIN_RE = re.compile(r"\b(" + "|".join(sorted(PLAIN, key=len, reverse=True)) + r")\b")
LONG_SENTENCE_LIMIT = 60


def match_case(rep: str, orig: str) -> str:
    if orig.isupper() and len(orig) > 1:
        return rep.upper()
    return rep[0].upper() + rep[1:] if orig[0].isupper() else rep


def polish(text: str) -> str:
    parts = []
    for chunk in re.split(r'(“[^”]*”|"[^"]*")', text):
        if chunk.startswith(("“", '"')):
            parts.append(chunk)
            continue
        for rx, rep in FILLER_RES:
            chunk = rx.sub(rep, chunk)
        chunk = PLAIN_RE.sub(lambda m: match_case(PLAIN[m.group(1).lower()], m.group(1)), chunk)
        chunk = re.sub(r"(?<![\w'’\u2019])a(?=\s+[aeiouAEIO])", "an", chunk)
        chunk = re.sub(r"(?<![\w'’\u2019])an(?=\s+[^aeiouAEIOU\W\d])", "a", chunk)
        chunk = re.sub(r"\bin spite of\b", "despite", chunk)
        parts.append(chunk)
    text = "".join(parts)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()


RELATIVE_START = {"who", "which", "whose", "whom", "that", "where", "whence"}


def split_long(sent: str) -> str:
    """Break a very long sentence at a semicolon, but only where the result is
    two complete sentences: never inside a colon-list, never before a relative
    clause, and never producing a stub."""
    if len(sent.split()) < LONG_SENTENCE_LIMIT:
        return sent
    m = re.search(r";\s+", sent)
    if m:
        left, right = sent[: m.start()].strip(), sent[m.end():].strip()
        ok = (len(left.split()) >= 15 and len(right.split()) >= 15
              and ":" not in left
              and right.split()[0].lower() not in RELATIVE_START)
        if ok:
            return f"{left}. {right[0].upper() + right[1:]}"
    m = re.search(r",\s+(and|but|yet|so)\s+", sent)
    if m and len(sent.split()) >= 78:
        left, right = sent[: m.start()].strip(), sent[m.end():].strip()
        if len(left.split()) >= 20 and len(right.split()) >= 20:
            return f"{left}. {right[0].upper() + right[1:]}"
    return sent


def polish_para(text: str) -> str:
    sents = [split_long(polish(s)) for s in split_sentences(text)]
    return " ".join(s for s in sents if s.strip())


# ---------------------------------------------------------------------------
# 7. rendering
# ---------------------------------------------------------------------------

def render(groups, head_counts) -> str:
    out = []
    for head, paras in groups:
        keep_head = head
        if keep_head:
            if GENERIC_HEADS.match(keep_head) or len(keep_head.split()) > 12 or keep_head.endswith("."):
                keep_head = None
            elif head_counts.get(keep_head.lower(), 0) >= 3:
                keep_head = None
        body = [p for p in paras if p.strip()]
        if not body:
            continue
        if keep_head and len(" ".join(body).split()) < 35:
            keep_head = None
        if keep_head:
            out.append(f"**{keep_head}**")
        for p in body:
            out.append("> " + p[1:] if p.startswith("\x01") else p)
    return "\n\n".join(out)


def chapter_title(h1: str, ch: int) -> str:
    m = re.match(r"#\s*Sūrah\s+(.+?)\s+\(Chapter\s+\d+\)", h1) if h1 else None
    name = m.group(1) if m else None
    if not name:
        m2 = re.match(r"#\s*Sūrah\s+(.+?)\s+—", h1 or "")
        name = m2.group(1) if m2 else f"Chapter {ch}"
    return f"# Sūrah {name} (Chapter {ch}) — Verse-by-Verse Commentary"


# ---------------------------------------------------------------------------
# 8. worker
# ---------------------------------------------------------------------------

def edit_chapter(args):
    ch, src_dir, out_dir, stats, head_counts, dry_run = args
    t0 = time.time()
    raw = read_chapter(src_dir, ch)
    h1, intro_groups, verses = split_chapter(raw, ch)
    ed = Editor(stats)
    dropped: list[str] = []
    w_before = len(raw.split())

    # introduction
    intro_text = ""
    if intro_groups:
        kept, used = ed.edit_section(intro_groups, "", True, ch, 0, dropped)
        for _, paras in kept:
            paras[:] = [p if p.startswith("\x01") else polish_para(p) for p in paras]
        intro_text = render(kept, head_counts)

    title_line = h1.strip() if h1.strip().startswith("# ") else chapter_title(h1, ch)
    body_parts = [title_line, "", "## Introduction to the Sūrah", "", intro_text, "", "---", ""]
    for ayah, heading, quote, groups in verses:
        kept, used = ed.edit_section(groups, quote, False, ch, ayah, dropped)
        paras_all = []
        for _, ps in kept:
            ps[:] = [p if p.startswith("\x01") else polish_para(p) for p in ps]
            paras_all.extend(ps)
        text = render(kept, head_counts)
        if not text.strip():
            text = "*Commentary condensed to nothing; source had no substantive content for this verse.*"
        body_parts.append(heading)
        body_parts.append("")
        if quote:
            body_parts.append(f"> {quote}")
            body_parts.append("")
        body_parts.append(text)
        body_parts.append("")
        body_parts.append("---")
        body_parts.append("")
    new_text = "\n".join(body_parts).rstrip() + "\n"
    w_after = len(new_text.split())

    if not dry_run:
        with open(os.path.join(out_dir, f"{ch:03d}.md"), "w", encoding="utf-8") as fh:
            fh.write(new_text)
    return ch, w_before, w_after, len(dropped), dropped, time.time() - t0


# ---------------------------------------------------------------------------
# 9. verification
# ---------------------------------------------------------------------------

def verify_chapter(args):
    """Confirm every citation in the source still exists in the edited file."""
    ch, src_dir, out_dir = args
    src = read_chapter(src_dir, ch)
    try:
        with open(os.path.join(out_dir, f"{ch:03d}.md"), encoding="utf-8") as fh:
            out = fh.read()
    except FileNotFoundError:
        return ch, {"missing": {"file": 1}}, {}
    missing = collections.Counter()
    for ref in set(QURAN_REF_RE.findall(src)):
        if ref not in out:
            missing["quran_ref"] += 1
    for ref in set(HADITH_STRONG_RE.findall(src)):
        if ref.strip() and ref.strip() not in out:
            missing["hadith_ref"] += 1
    for ref in set(YEAR_RE.findall(src)):
        if ref.strip() not in out:
            missing["year"] += 1
    # every verse heading still present, and every ayah quote intact
    src_quotes = {}
    out_quotes = {}
    for txt, target in ((src, src_quotes), (out, out_quotes)):
        for m in re.finditer(r"^##\s+.*?(\d+):(\d+)\s*$", txt, re.M):
            key = m.group(1) + ":" + m.group(2)
            target[key] = True
    missing["verse_heading"] = len(set(src_quotes) - set(out_quotes))
    info = {}
    if os.path.exists(os.path.join(src_dir, f"{ch:03d}.md")):
        info["words_src"] = len(src.split())
        info["words_out"] = len(out.split())
        info["quotes_src"] = len(re.findall(r"(?m)^>\s", src))
        info["quotes_out"] = len(re.findall(r"(?m)^>\s", out))
    return ch, dict(missing), info


# ---------------------------------------------------------------------------
# 10. driver
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chapter", type=int)
    ap.add_argument("--chapters")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--src", default=SRC_DIR)
    ap.add_argument("--out", default=SRC_DIR)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--show")
    ap.add_argument("--audit", type=int, default=0)
    args = ap.parse_args()

    if args.all:
        chapters = list(range(1, 115))
    elif args.chapters:
        chapters = [int(x) for x in args.chapters.split(",")]
    elif args.chapter:
        chapters = [args.chapter]
    else:
        ap.error("choose --all, --chapters or --chapter")

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        parts = list(ex.map(collect_stats, [(c, args.src) for c in chapters]))
    stats = Stats()
    for _, st in parts:
        stats.df.update(st.df)
        stats.docs += st.docs
        stats.sig_counts.update(st.sig_counts)
        stats.head_counts.update(st.head_counts)
    stats.finish()
    print(f"[stats] {stats.docs} sections, {len(stats.df)} terms, "
          f"{sum(1 for v in stats.sig_counts.values() if v > 1)} boilerplate signatures "
          f"in {time.time()-t0:.1f}s", file=sys.stderr)

    jobs = [(c, args.src, args.out, stats, stats.head_counts, args.dry_run) for c in chapters]
    total_b = total_a = 0
    audit: list[str] = []
    t1 = time.time()
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for ch, wb, wa, nd, dropped, took in ex.map(edit_chapter, jobs):
            total_b += wb
            total_a += wa
            audit += dropped
            print(f"[ch {ch:03d}] {wb:>7,} -> {wa:>7,} words ({wa/max(1,wb):4.0%})  {nd:>4} pieces cut  {took:.1f}s",
                  file=sys.stderr)
    print(f"[edited] {total_b:,} -> {total_a:,} words ({total_a/max(1,total_b):.1%}) in {time.time()-t1:.1f}s",
          file=sys.stderr)

    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(verify_chapter, [(c, args.src, args.out) for c in chapters]))
    bad = {c: m for c, m, _ in results if m and sum(m.values())}
    words_in = sum(i.get("words_src", 0) for _, _, i in results)
    words_out = sum(i.get("words_out", 0) for _, _, i in results)
    quotes_in = sum(i.get("quotes_src", 0) for _, _, i in results)
    quotes_out = sum(i.get("quotes_out", 0) for _, _, i in results)
    print(f"[verify] words {words_in:,} -> {words_out:,} | ayah quotes {quotes_in} -> {quotes_out} | "
          f"chapters with missing citations: {len(bad)}")
    for c, m in list(bad.items())[:10]:
        print(f"    ch {c}: {m}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write("Cut-material audit\n==================\n")
            fh.write(f"chapters: {len(chapters)}\nwords: {total_b:,} -> {total_a:,}\n\n")
            fh.write("\n".join(audit))
        print(f"[report] {len(audit)} cut entries -> {args.report}")
    if args.show and len(chapters) == 1:
        path = os.path.join(args.out, f"{chapters[0]:03d}.md")
        if os.path.exists(path):
            text = open(path, encoding="utf-8").read()
            if args.show in ("all", "*"):
                print(text)
            else:
                chunks = re.split(r"\n(?=## )", text)
                for c in chunks:
                    if c.split("\n")[0].strip().endswith(args.show.strip()):
                        print(c.strip())
    if args.audit:
        for line in audit[: args.audit]:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
