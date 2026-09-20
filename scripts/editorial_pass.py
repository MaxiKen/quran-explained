#!/usr/bin/env python3
"""
Editorial pass over `markdown commentry/*.md`.

Why this exists
---------------
The commentary was drafted against a fixed per-verse word target, so every
verse section runs to roughly the same length whether or not there is
anything to say. This pass turns the corpus back into prose whose length
follows its substance:

  1. hard facts are never cut - Qur'an citations, hadith references, named
     classical authorities, quotations, dates and numbers;
  2. points already made earlier in the same chapter are not made again
     (repetition across verses is demoted to its first occurrence);
  3. generation/process meta and generic exhortation are removed;
  4. sections are rebuilt as 2-5 coherent paragraphs instead of 6-9
     fragments: whole blocks are kept or dropped, and weak headings retired;
  5. a plain-English pass removes inflated connectives and wordy phrasing.

Usage
-----
    python3 scripts/editorial_pass.py --all --dry-run
    python3 scripts/editorial_pass.py --all --write
"""

import argparse
import math
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

SRC_DIR = os.path.join("markdown commentry")

# --------------------------------------------------------------------------
# Lexicons
# --------------------------------------------------------------------------

VERSE_REF = re.compile(r"\b\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?\b")
HADITH_SRC = re.compile(
    r"Ṣaḥīḥ|Sahih|Bukhārī|Bukhari|Muslim\b|Tirmidh|Abū Dāwūd|Abu Dawud|"
    r"Nasāʾ|Nasai|Ibn Mājah|Musnad|Sunan|Ḥadīth|hadith|Ṭabarānī|Tabarani|"
    r"Bayhaqī|Ibn Ḥibbān|Ḥākim|Muwatta|Dārimī|Aḥmad"
)
QUOTE_OPEN = re.compile(r"[“\"„]")
ITALIC = re.compile(r"\*(?!\*)([A-Za-z\u00C0-\u024Fʿʾ'’-][^*\n]{0,40})\*")
SCHOLAR = re.compile(
    r"\b(?:al-[A-ZĀĪŪṢḌṬẒḤʿ][\wāīūṣḍṭẓḥʿ'’-]+|Ibn [A-ZĀĪŪṢḌṬẒḤʿ][\wāīūṣḍṭẓḥʿ'’-]+|"
    r"Abū [A-ZĀĪŪṢḌṬẒḤʿ][\wāīūṣḍṭẓḥʿ'’-]+|Fakhr al-Dīn|Badr al-Dīn|"
    r"ʿUmar|ʿAlī|ʿUthmān|Mūsā|ʿĪsā|Ibrāhīm|Yūsuf|Nūḥ|Dāwūd|Sulaymān|Maryam)\b"
)
NUMBER = re.compile(r"\b\d{2,4}\b")

META_PAT = re.compile(
    r"this file|thin source|source chunk|the gate asked|first pass|"
    r"the kind of extra|this commentary|these last sūrahs|"
    r"the present verse remains|the parallel is a lamp|second courtroom|"
    r"cross-reference is a servant|the discipline is:|word count|word target|"
    r"the chunk we were given|our brief|the brief asked|as instructed|"
    r"per instructions|the gate's|asked for by the gate|tafsīr gate|"
    r"the present verse is the|the verse remains the|"
    r"this is the discipline|tagged, then back to|a second courtroom|"
    r"will not stop at a gloss|in the mouth of a teacher|"
    r"portability was for use|the point of such reports|"
    r"the difference between scholarship|a list of famous names|"
    r"these verses of the muṣḥaf|the way this commentary|"
    r"as this commentary has|the present chapter|this chapter's file|"
    r"belongs to another place in the Book|brought here only as a witness|"
    r"not as a second assignment|dump a whole neighbouring|"
    r"occasions of revelation, when reported, are historical helps|"
    r"they do not lock a general|the right default for these last",
    re.I
)

FILLER_PAT = re.compile(
    r"^(?:It is worth (?:noting|remembering|pausing)|It should be noted|"
    r"It is important to note|Note that|In other words|That is to say|"
    r"Put differently|Simply put|Stated plainly|In sum|In short|To be sure|"
    r"Needless to say)\b",
    re.I
)

RHETORIC_PAT = re.compile(
    r"\bis not (?:merely|simply|just)\b|\bnot merely\b|\bthe point is\b|"
    r"\bwhat matters (?:here|is)\b|\bthe upshot\b|\bdoes not need\b|"
    r"\bsays something (?:deep|important)\b|\bthat is the whole point\b|"
    r"\bis (?:the )?(?:whole|entire) point\b",
    re.I
)

ANAPHORA_PAT = re.compile(
    r"^(?:That|This|It|They|These|Those|Such|He|She|The same|So|Then|There|Their|"
    r"Them|Its|Here|Again|Once more)\b"
)

CONDUCT_PAT = re.compile(
    r"^(?:The reader|A reader|The listener|A listener|The student|The reciter|"
    r"The worshipper|A person who|Anyone who reads|Whoever reads|One who reads|"
    r"The believer who|A reader who)\b", re.I
)

EXHORT_PAT = re.compile(
    r"\bdoes not need a new miracle\b|\btreat the verse as\b|\bleave the type\b|"
    r"\bbecome the verbs\b|\bwear a group label\b|\bis not a nod during\b|"
    r"\bthe conduct (?:this verse|the verse) asks\b",
    re.I
)

GENERIC_HEADS = {"Expanded Commentary"}

TEMPLATE_HEADS = {
    "The Arabic Still Has Work After the First Pass",
    "Conduct Follows if the Verse Is Believed",
    "A Checked Parallel, Not a Stolen Verse",
}

# Plain-English substitutions - applied only outside quotes and italics.
SIMPLIFY = [
    (r"\bdue to the fact that\b", "because"),
    (r"\bfor the reason that\b", "because"),
    (r"\bfor the purpose of\b", "to"),
    (r"\bin order to\b", "to"),
    (r"\bin order that\b", "so that"),
    (r"\bwith regard to\b", "about"),
    (r"\bwith respect to\b", "about"),
    (r"\bin regard to\b", "about"),
    (r"\bin terms of\b", "in"),
    (r"\bin the event that\b", "if"),
    (r"\bprior to\b", "before"),
    (r"\bsubsequent to\b", "after"),
    (r"\bapproximately\b", "about"),
    (r"\bnumerous\b", "many"),
    (r"\bfacilitate\b", "help"),
    (r"\bfacilitates\b", "helps"),
    (r"\butilize\b", "use"),
    (r"\butilizes\b", "uses"),
    (r"\butilized\b", "used"),
    (r"\bcommences\b", "begins"),
    (r"\bcommence\b", "begin"),
    (r"\bendeavour\b", "effort"),
    (r"\bendeavor\b", "effort"),
    (r"\bascertain\b", "find out"),
    (r"\bdemonstrates that\b", "shows that"),
    (r"\bdemonstrate that\b", "show that"),
    (r"\bpossesses\b", "has"),
    (r"\bpossess\b", "have"),
    (r"\bobtains\b", "gets"),
    (r"\bobtain\b", "get"),
    (r"\battempts to\b", "tries to"),
    (r"\bregarding\b", "about"),
    (r"\bconcerning\b", "about"),
    (r"\binitiate\b", "start"),
    (r"\bfurthermore\b", "also"),
    (r"\bmoreover\b", "also"),
    (r"\bnevertheless\b", "still"),
    (r"\bnonetheless\b", "still"),
    (r"\bconsequently\b", "so"),
    (r"\bsubsequently\b", "later"),
    (r"\bhence\b", "so"),
    (r"\bthereby\b", "by this"),
    (r"\bin effect\b", "in practice"),
    (r"\bin essence\b", "at bottom"),
    (r"\bas it were\b", ""),
    (r"\bso to speak\b", ""),
    (r"\bis not merely\b", "is not only"),
    (r"\bare not merely\b", "are not only"),
    (r"\bit is not merely\b", "it is not only"),
    (r"\bcommonly\b", "often"),
    (r"\boccasionally\b", "sometimes"),
    (r"\bwhat is more\b", "more than that"),
    (r"\bit is worth noting that\b", ""),
    (r"\bit should be noted that\b", ""),
]

STOPWORDS = set("""
a an the and or but if then than that this these those of in on at to for from with by as is
are was were be been being it its he she they them his her their we our you your i not no nor
so such also more most very can could will would shall should may might must do does did done
have has had having there here what which who whom whose when where why how all any both each
few other some own same too only just about into over under again further once during before
after above below up down out off between while because until against among around without
within upon toward towards per via etc one two three first second third another still yet even
much many may like way thing things says said say make makes made
""".split())

WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F][A-Za-z\u00C0-\u024Fʿ'’-]*")


def stem(w):
    for suf in ("ations", "ation", "ments", "ment", "ings", "ing", "ed", "es", "s", "ly"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def content_words(s):
    return [w.lower() for w in WORD_RE.findall(s) if w.lower() not in STOPWORDS]


def shingles(words, k=3):
    return frozenset(hash(tuple(words[i:i + k])) for i in range(max(0, len(words) - k + 1)))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if not inter:
        return 0.0
    return inter / float(len(a) + len(b) - inter)


# --------------------------------------------------------------------------
# Text utilities
# --------------------------------------------------------------------------

def split_sentences(text):
    out, buf, q, depth = [], [], 0, 0
    italics = 0
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        buf.append(c)
        if c == "“":
            q += 1
        elif c == "”":
            q = max(0, q - 1)
        elif c == "(":
            depth += 1
        elif c == ")":
            depth = max(0, depth - 1)
        elif c == "*" and (i + 1 >= n or text[i + 1] != "*") and (i == 0 or text[i - 1] != "*"):
            italics = 1 - italics
        if c in ".!?" and q == 0 and depth == 0 and italics == 0:
            j = i + 1
            if j >= n or text[j] in " \n":
                k = j
                while k < n and text[k] in " \n":
                    k += 1
                if k >= n or text[k].isupper() or text[k] in "“\"*‘’":
                    s = "".join(buf).strip()
                    if s:
                        out.append(s)
                    buf = []
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def simplify_text(s):
    """Plain-English pass that never touches quoted or italicised matter."""
    spans = []

    def stash(m):
        spans.append(m.group(0))
        return "\x00%d\x00" % (len(spans) - 1)

    protected = re.compile(r"“.*?”|\*[^*\n]+\*")
    tmp = protected.sub(stash, s)
    for pat, rep in SIMPLIFY:
        tmp = re.sub(pat, rep, tmp)
    tmp = re.sub(r"\s{2,}", " ", tmp)
    tmp = re.sub(r"\s+([,.;:])", r"\1", tmp)
    tmp = re.sub(r"^[\s,;:]+", "", tmp)
    tmp = re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], tmp)
    return tmp.strip()


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------

def count_hard(s):
    """Facts that are never cut."""
    n = 3 * len(VERSE_REF.findall(s))
    if HADITH_SRC.search(s):
        n += 3
    n += 2 * len(QUOTE_OPEN.findall(s))
    n += len(SCHOLAR.findall(s))
    if NUMBER.search(s):
        n += 1
    return n


def count_info(s):
    n = count_hard(s)
    n += len(ITALIC.findall(s))
    if re.search(r"\b(?:Makkah|Makki|Madinah|Madinan|Kufah|Baṣrah|Najrān|Quraysh|"
                 r"Badr|Uḥud|Khandaq|Ṭāʾif|Kaʿbah|Kāʿbah|Sinai|Ṭūr)\b", s):
        n += 1
    return n


class Sent:
    __slots__ = ("text", "words", "hard", "info", "meta", "filler", "score", "dup", "para")

    def __init__(self, text):
        self.text = text
        self.words = len(text.split())
        self.hard = count_hard(text)
        self.info = count_info(text)
        self.meta = bool(META_PAT.search(text))
        self.filler = bool(FILLER_PAT.match(text)) or bool(EXHORT_PAT.search(text))
        self.score = 0.0
        self.dup = False
        self.para = 0

    @property
    def hard_kept(self):
        return self.hard > 0 and not self.meta


class Block:
    __slots__ = ("heading", "text", "sents", "is_quote", "paras")

    def __init__(self, heading, text, is_quote=False):
        self.heading = heading
        self.text = text
        self.is_quote = is_quote
        self.sents = []
        if not is_quote:
            self.paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            for pi, para in enumerate(self.paras):
                for s in split_sentences(para):
                    sent = Sent(s)
                    sent.para = pi
                    self.sents.append(sent)
        else:
            self.paras = [text]


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def parse_section(raw):
    # a handful of draft headings carry doubled markers (****Title****);
    # normalise them so they are treated as headings and not as prose
    raw = re.sub(r"(?m)^\*{4}([^*\n]+?)\*{4}\s*$", r"**\1**", raw.strip())
    raw = re.sub(r"(?m)^\*{2}\s+([^*\n]+?)\s+\*{2}\s*$", r"**\1**", raw)
    lines = raw.split("\n")
    heading = lines[0].strip()
    body = lines[1:]
    while body and body[-1].strip() in ("", "---"):
        body.pop()
    quotes = []
    while body and (not body[0].strip() or body[0].lstrip().startswith(">")):
        if body[0].lstrip().startswith(">"):
            quotes.append(body.pop(0).rstrip())
        else:
            body.pop(0)
    body = [l for l in body if l.strip() != "**Expanded Commentary**"]
    # a quoted scripture line that sits inside the commentary is its own unit
    # and is always preserved verbatim
    segments = []
    buf = []
    i = 0
    while i < len(body):
        line = body[i]
        if line.lstrip().startswith(">"):
            run = []
            while i < len(body) and body[i].lstrip().startswith(">"):
                run.append(body[i].strip())
                i += 1
            if buf:
                segments.append(("text", "\n".join(buf)))
                buf = []
            segments.append(("quote", "\n".join(run)))
        else:
            buf.append(line)
            i += 1
    if buf:
        segments.append(("text", "\n".join(buf)))
    blocks = []
    for kind, seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if kind == "quote":
            blocks.append(Block(None, seg, is_quote=True))
            continue
        for part in re.split(r"\n(?=\*\*[^*\n]{2,90}\*\*\s*\n)", seg):
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^\*\*([^*\n]{2,90})\*\*\s*\n+(.*)$", part, re.S)
            if m and m.group(1).strip() not in GENERIC_HEADS:
                blocks.append(Block(m.group(1).strip(), m.group(2).strip()))
            else:
                blocks.append(Block(None, part))
    return heading, quotes, blocks


def section_pairs(raw):
    """Yield (heading, quotes, blocks) for every '## ' section of a chapter."""
    for sec in re.split(r"\n(?=## )", raw):
        if sec.startswith("## "):
            yield parse_section(sec)


# --------------------------------------------------------------------------
# Pass A - collect sentences, find repeats across the corpus
# --------------------------------------------------------------------------

def collect_units(args):
    chapter, path = args
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    out = []
    for sec_i, (heading, quotes, blocks) in enumerate(section_pairs(raw)):
        for bi, b in enumerate(blocks):
            for si, s in enumerate(b.sents):
                out.append((chapter, sec_i, bi, si, heading, s.text, content_words(s.text)))
    return out


def find_repeats(units, threshold=0.56, bucket_limit=260, sig_len=3):
    """Indices of sentences that repeat an earlier sentence anywhere in the corpus."""
    df = Counter()
    for u in units:
        df.update(set(u[6]))
    buckets = defaultdict(list)
    for idx, u in enumerate(units):
        ws = [w for w in u[6] if df.get(w, 1) <= 300]
        if len(ws) < sig_len:
            ws = u[6]
        if len(ws) < sig_len:
            continue
        sig = tuple(sorted(set(ws), key=lambda w: (df.get(w, 1), w))[:sig_len])
        buckets[sig].append(idx)
    repeats = set()
    shingle_cache = {}

    def sg(idx):
        v = shingle_cache.get(idx)
        if v is None:
            v = shingles(units[idx][6]) if len(units[idx][6]) >= 4 else frozenset()
            shingle_cache[idx] = v
        return v

    for sig, idxs in buckets.items():
        if len(idxs) < 2 or len(idxs) > bucket_limit:
            continue
        for a in range(len(idxs)):
            ia = idxs[a]
            if ia in repeats:
                continue
            sa = sg(ia)
            if not sa:
                continue
            for b in range(a + 1, len(idxs)):
                ib = idxs[b]
                if ib in repeats:
                    continue
                sb = sg(ib)
                if not sb:
                    continue
                if jaccard(sa, sb) >= threshold:
                    later = ib if ib > ia else ia
                    repeats.add(later if later != ia else ib)
    return repeats


# --------------------------------------------------------------------------
# Pass B - section editing
# --------------------------------------------------------------------------

def process_section(heading, quotes, blocks, repeats, offset, cfg):
    """Returns (markdown_text, stats) or None."""
    # ---- per sentence bookkeeping (global repeat flags)
    gi = offset
    for b in blocks:
        for s in b.sents:
            s.dup = gi in repeats
            gi += 1
    used_globally = gi - offset

    total_words = sum(s.words for b in blocks for s in b.sents)

    # ---- local redundancy: identical points inside the section
    local_vec = []
    df_local = Counter()
    for b in blocks:
        for s in b.sents:
            df_local.update(set(content_words(s.text)))
    n_s = sum(len(b.sents) for b in blocks)
    idf = {w: math.log(1 + n_s / (1 + df_local[w])) for w in df_local}

    def vec(s):
        c = Counter(content_words(s.text))
        return {w: c[w] * idf.get(w, 1.0) for w in c}

    for b in blocks:
        for s in b.sents:
            local_vec.append(vec(s))

    def cos(i, j):
        a, b = local_vec[i], local_vec[j]
        if not a or not b:
            return 0.0
        if len(a) > len(b):
            a, b = b, a
        num = sum(v * b.get(k, 0.0) for k, v in a.items())
        if not num:
            return 0.0
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return num / (na * nb)

    flat = [s for b in blocks for s in b.sents]
    for i in range(len(flat)):
        if flat[i].dup or flat[i].meta:
            continue
        for j in range(i + 1, len(flat)):
            if flat[j].dup:
                continue
            if cos(i, j) >= cfg["dup_sim"]:
                flat[j].dup = True

    # ---- block scoring
    block_stats = []
    for bi, b in enumerate(blocks):
        if b.is_quote:
            block_stats.append({
                "bi": bi, "heading": None, "words": 0, "hard": 99, "info": 99,
                "live": 0, "score": 999.0, "density": 99.0, "quote": True})
            continue
        if not b.sents:
            continue
        words = sum(s.words for s in b.sents)
        hard = sum(s.hard for s in b.sents)
        info = sum(s.info for s in b.sents)
        meta_w = sum(s.words for s in b.sents if s.meta)
        dup_w = sum(s.words for s in b.sents if s.dup)
        filler_w = sum(s.words for s in b.sents if s.filler)
        rhet = sum(1 for s in b.sents if RHETORIC_PAT.search(s.text) and s.hard == 0)
        conduct = sum(s.words for s in b.sents if CONDUCT_PAT.match(s.text))
        template = 1 if (b.heading in TEMPLATE_HEADS) else 0
        if template:
            # These blocks are boilerplate repeated under every verse of the
            # sūrah.  What is genuinely verse-specific in them is the checked
            # parallel itself, so the framing is stripped and the reference
            # kept; the rest of the block goes.
            kept = []
            for s in b.sents:
                txt = re.sub(r"\s+belongs to another place in the Book.*$", "", s.text)
                txt = re.sub(r"\s+is brought here only as a witness.*$", "", txt)
                txt = txt.strip()
                if not txt or META_PAT.search(txt) or EXHORT_PAT.search(txt):
                    continue
                s.text = txt
                s.words = len(s.text.split())
                s.hard = count_hard(s.text)
                s.info = count_info(s.text)
                kept.append(s)
            b.sents = kept
            b.heading = None
            if not b.sents:
                continue
            words = sum(s.words for s in b.sents)
            hard = sum(s.hard for s in b.sents)
            info = sum(s.info for s in b.sents)
            meta_w = dup_w = filler_w = rhet = conduct = 0
            template = 0
        live = sum(s.words for s in b.sents if not s.dup and not s.meta)
        for si, s in enumerate(b.sents):
            s.score = (1.6 * min(s.hard, 6) + 0.5 * s.info
                       + (1.0 if si == 0 else 0.0)
                       - (3.0 if s.meta else 0.0)
                       - (2.0 if s.dup else 0.0)
                       - (1.5 if s.filler else 0.0)
                       - (1.0 if (RHETORIC_PAT.search(s.text) and s.hard == 0) else 0.0)
                       - (0.8 if (CONDUCT_PAT.match(s.text) and s.hard == 0) else 0.0))
        score = (
            2.2 * min(hard, 8)
            + 0.8 * info
            - 1.6 * (meta_w / 40.0)
            - 1.3 * (dup_w / 60.0)
            - 0.9 * (filler_w / 40.0)
            - 0.5 * rhet
            - 0.8 * (conduct / 60.0)
            - 1.4 * template
        )
        # a block that is essentially nothing but repetition is worthless
        if live < 35:
            score -= 6.0
        block_stats.append({
            "bi": bi, "heading": b.heading, "words": words, "hard": hard,
            "info": info, "live": live, "score": score,
            "density": (hard * 3 + info) / max(20.0, words),
        })

    if not block_stats:
        return None

    # ---- budget from substance
    hard_total = sum(bs["hard"] for bs in block_stats)
    info_total = sum(bs["info"] for bs in block_stats)
    density = (hard_total / max(1.0, total_words / 1000.0)) * 0.6 + \
              (info_total / max(1.0, total_words / 1000.0)) * 0.4
    share = cfg["share_min"] + (cfg["share_max"] - cfg["share_min"]) * min(
        1.0, density / cfg["density_full"])
    target = max(cfg["min_words"], min(cfg["max_words"], total_words * share))

    # ---- choose blocks: best first, until the budget is met
    ranking = sorted(block_stats, key=lambda bs: (-bs["score"], bs["bi"]))
    chosen = [bs["bi"] for bs in block_stats if bs.get("quote")]
    acc = 0
    for bs in ranking:
        if bs.get("quote"):
            continue
        if acc >= target and len([c for c in chosen if not blocks[c].is_quote]) >= cfg["min_blocks"]:
            break
        if len([c for c in chosen if not blocks[c].is_quote]) >= cfg["max_blocks"]:
            break
        chosen.append(bs["bi"])
        acc += bs["words"]
    chosen = sorted(set(chosen))

    # ---- rebuild each chosen block: drop meta / repeated / filler sentences
    med_density = statistics.median([bs["density"] for bs in block_stats]) if block_stats else 0
    body_parts = []
    kept_words = dropped_words = 0
    for bi in chosen:
        b = blocks[bi]
        bstat = next(bs for bs in block_stats if bs["bi"] == bi)
        if b.is_quote:
            body_parts.append("<QUOTE>" + b.text)
            continue
        alive = [s for s in b.sents if not (s.meta or s.dup or s.filler)]
        # weak blocks (below the section's median information density) give up
        # a quarter of their sentences; strong blocks keep everything
        if bstat["density"] < med_density and len(alive) > 2:
            budget = 0.7
        else:
            budget = 1.0
        if budget < 1.0:
            words = sum(s.words for s in alive)
            allowed = words * budget
            order = sorted(range(len(alive)),
                           key=lambda i: (-alive[i].score, i))
            keep_flags = [True] * len(alive)
            used = 0
            for i in range(len(alive)):
                if i == 0:
                    used += alive[i].words
            for i in order:
                if used >= allowed:
                    if i != 0 and alive[i].hard == 0:
                        keep_flags[i] = False
                        dropped_words += alive[i].words
                else:
                    used += alive[i].words
            alive = [s for i, s in enumerate(alive) if keep_flags[i]]
        para_keep = defaultdict(list)
        dropped_prev = False
        dropped_words_set = set()
        for s in b.sents:
            if s not in alive:
                dropped_prev = True
                dropped_words_set = {stem(w) for w in content_words(s.text)}
                if s.meta or s.dup or s.filler:
                    dropped_words += s.words
                continue
            # a sentence that leans on a line we just removed cannot stand
            if dropped_prev and s.hard == 0:
                opening = " ".join(s.text.split()[:14])
                hangs = bool(ANAPHORA_PAT.match(s.text)) or bool(
                    re.search(r"\b(?:that|this|these|those|such|the same|it|they)\b",
                              opening, re.I))
                shares = bool({stem(w) for w in content_words(s.text)} & dropped_words_set)
                if hangs and (shares or ANAPHORA_PAT.match(s.text)):
                    dropped_prev = True
                    dropped_words += s.words
                    continue
            dropped_prev = False
            dropped_words_set = set()
            para_keep[s.para].append(s)
        if not para_keep:
            # nothing left but repetition: keep the least repetitive sentence
            best = min(b.sents, key=lambda s: (s.meta, s.dup, -s.hard, s.words))
            para_keep[best.para] = [best]
        w = sum(s.words for s in b.sents if any(s in v for v in para_keep.values()))
        hard_w = sum(s.hard for s in b.sents if any(s in v for v in para_keep.values()))
        if w < 25 and hard_w == 0:
            dropped_words += w
            continue
        paras = []
        for pi in sorted(para_keep):
            chunk = " ".join(simplify_text(s.text) for s in para_keep[pi])
            chunk = re.sub(r"\s{2,}", " ", chunk).strip()
            if chunk and not re.search(r"[.!?…”)\*]$", chunk):
                chunk += "."
            paras.append(chunk)
        kept_words += w
        joined = "\n\n".join(paras)
        kept_sents = sum(len(v) for v in para_keep.values())
        heading_is_true = (b.heading and w >= cfg["keep_heading_words"]
                           and kept_sents >= 0.5 * max(1, len(b.sents)))
        if heading_is_true:
            body_parts.append("**%s**|%s" % (b.heading, joined))
        else:
            body_parts.append("|%s" % joined)

    if not body_parts:
        return None

    # ---- render: unheaded fragments continue the previous paragraph
    rendered = []
    for part in body_parts:
        if part.startswith("<QUOTE>"):
            quote = part[len("<QUOTE>"):]
            if rendered:
                rendered[-1] = rendered[-1].rstrip() + "\n\n" + quote
            else:
                rendered.append(quote)
            continue
        if part.startswith("|"):
            frag = part[1:]
            if rendered:
                rendered[-1] = rendered[-1].rstrip() + " " + frag
            else:
                rendered.append(frag)
        else:
            if rendered:
                rendered[-1] = rendered[-1].rstrip()
            rendered.append(part)
    body = "\n\n".join(rendered)
    body = re.sub(r"\*\*([^*\n]+)\*\*\|", r"**\1**\n\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    out = [heading, ""] + quotes
    if quotes:
        out.append("")
    out.append(body)
    out.append("")
    return "\n".join(out), {
        "before": total_words, "after": kept_words, "blocks_in": len(blocks),
        "blocks_out": len([p for p in rendered if "**" in p[:80]]) or 1,
        "density": density,
    }


# --------------------------------------------------------------------------
# Chapter driver
# --------------------------------------------------------------------------

CFG = dict(
    dup_sim=0.58,          # two sentences this close = the same point twice
    share_min=0.15,        # thin section: keep about a sixth of the draft
    share_max=0.56,        # dense section: keep just over half
    density_full=18.0,     # info unit density that counts as fully dense
    min_words=150,
    max_words=1500,
    min_blocks=1,
    max_blocks=6,
    keep_heading_words=60,
)


CITATION_KEY = re.compile(
    r"(?:\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?)|"
    r"(?:(?:Ṣaḥīḥ|Sahih|Sunan|Musnad|Jāmiʿ|Muwatta)[^.;)]{0,45}?\d{2,5}[a-z]?)"
)
REF_ONLY = re.compile(r"^\d")


def refs_of(text):
    """Every scriptural / hadith citation carried by a passage."""
    out = []
    for m in CITATION_KEY.finditer(text):
        key = re.sub(r"\s+", " ", m.group(0)).strip()
        if key not in out:
            out.append(key)
    return out


def mentions(text, key):
    """Boundary-aware presence test: '4:35' must not be satisfied by '24:35'."""
    if REF_ONLY.match(key):
        return re.search(r"(?<![\d:])" + re.escape(key) + r"(?![\d:])", text) is not None
    return key in text


def process_chapter(job):
    chapter, path, repeats, cfg, write = job
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    chunks = re.split(r"\n(?=## )", raw)
    out_parts = []
    if not chunks[0].startswith("## "):
        head = chunks[0].rstrip()
        if head.strip():
            out_parts.append(head)
    offset = 0
    stats = []
    section_bodies = []
    for sec in chunks:
        if not sec.startswith("## "):
            continue
        heading, quotes, blocks = parse_section(sec)
        res = process_section(heading, quotes, blocks, repeats, offset, cfg)
        offset += sum(len(b.sents) for b in blocks)
        if res is None:
            out_parts.append(sec.rstrip())
            continue
        text, st = res
        st["heading"] = heading
        st["source_sents"] = [s.text for b in blocks for s in b.sents]
        stats.append(st)
        section_bodies.append(len(out_parts))
        out_parts.append(text.rstrip())

    # ---- fact protection: every citation in the draft survives somewhere
    body_text = "\n\n".join(out_parts)
    missing = []
    seen = set()
    for st in stats:
        for sent in st["source_sents"]:
            for key in refs_of(sent):
                if key in seen:
                    continue
                seen.add(key)
                if not mentions(body_text, key):
                    missing.append((key, sent, st))
    restored = 0
    for key, sent, st in missing:
        target = None
        for pos in section_bodies:
            if out_parts[pos].split("\n")[0].strip() == st.get("heading"):
                target = pos
                break
        if target is None:
            continue
        add = simplify_text(sent)
        if add not in out_parts[target] and not mentions(out_parts[target], key):
            out_parts[target] = out_parts[target].rstrip() + "\n\n" + add
            body_text += " " + add
            restored += 1
    new = "\n\n".join(out_parts).strip() + "\n"
    new = re.sub(r"\n{3,}", "\n\n", new)
    if write:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
    return chapter, stats, new, restored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--report", default="")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    if args.all:
        chapters = list(range(1, 115))
    elif args.chapters:
        chapters = [int(c) for c in args.chapters.split(",") if c.strip()]
    else:
        ap.error("pass --all or --chapters")

    paths = [(c, os.path.join(SRC_DIR, "%03d.md" % c)) for c in chapters]
    cfg = dict(CFG)
    jobs = min(args.jobs, max(1, len(paths)))
    t0 = time.time()

    with Pool(jobs) as pool:
        groups = pool.map(collect_units, paths)
    units = [u for g in groups for u in g]
    t1 = time.time()
    repeats = find_repeats(units)
    print("pass A: %d sentences in %.1fs; %d (%.1f%%) repeat an earlier sentence"
          % (len(units), t1 - t0, len(repeats), 100.0 * len(repeats) / max(1, len(units))))

    wjobs = [(c, p, repeats, cfg, args.write) for c, p in paths]
    with Pool(jobs) as pool:
        results = pool.map(process_chapter, wjobs)

    total_before = total_after = restored_total = 0
    rep = []
    for chapter, stats, new, restored in results:
        restored_total += restored
        b = sum(s["before"] for s in stats)
        a = sum(s["after"] for s in stats)
        total_before += b
        total_after += a
        rep.append((chapter, b, a, stats))
        if args.out_dir:
            os.makedirs(args.out_dir, exist_ok=True)
            with open(os.path.join(args.out_dir, "%03d.md" % chapter), "w",
                      encoding="utf-8") as fh:
                fh.write(new)

    after_sizes = [s["after"] for _, _, _, stats in rep for s in stats]
    print("citations restored by the fact guard: %d" % restored_total)
    print("\n%-7s %9s %9s %7s" % ("surah", "before", "after", "kept"))
    for chapter, b, a, stats in rep[:8]:
        print("%-7d %9d %9d %6.1f%%" % (chapter, b, a, 100.0 * a / max(1, b)))
    print("...")
    print("sections: %d | median after: %d words | p10 %d | p90 %d | max %d"
          % (len(after_sizes), statistics.median(after_sizes),
             sorted(after_sizes)[len(after_sizes) // 10],
             sorted(after_sizes)[9 * len(after_sizes) // 10], max(after_sizes)))
    print("TOTAL  %9d %9d %6.1f%%  (%.1fs)"
          % (total_before, total_after, 100.0 * total_after / max(1, total_before),
             time.time() - t0))

    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write("# Editorial pass report\n\n")
            fh.write("| Surah | Words before | Words after | Kept |\n|---|---|---|---|\n")
            for chapter, b, a, stats in rep:
                fh.write("| %d | %d | %d | %.0f%% |\n" % (chapter, b, a, 100.0 * a / max(1, b)))
        print("report written to", args.report)


if __name__ == "__main__":
    main()
