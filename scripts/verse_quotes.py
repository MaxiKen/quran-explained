#!/usr/bin/env python3
"""
Shared helpers: the Qur'an translation that ships with this repo, plus the
sentence/clause picker used to attach the *actual* verse wording to every
cross-reference in the commentary.

The translation source is `ayah_en` in `data/chapter_NNN.js` — the same text the
app displays next to the Arabic, so a quote inserted in the commentary can never
disagree with the verse the reader is looking at.
"""

import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CORPUS = ROOT / "markdown commentry"

# (c:v), (c:v-v), (c:v–v)
# Biblical and extra-Quranic citations look identical to (2:13) but must never be
# given a Qur'an wording: "Mark 12:29", "Genesis 1:1", "John 20:17".
BOOKS = (r"Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|"
         r"Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|"
         r"Ecclesiastes|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|"
         r"Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|"
         r"Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|"
         r"Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|"
         r"Philemon|Hebrews|James|Peter|Jude|Revelation|Torah|Gospel|Inj[īi]l|"
         r"Tawr[āa]h|Zab[ūu]r|Bible|Scriptures?|Qumran|Talmud|Mishnah")
BOOK_REF = re.compile(r"\b(?:" + BOOKS + r")\s+\d{1,3}:\d{1,3}")

REF = re.compile(r"\((\d{1,3}):(\d{1,3})(?:([–-])(\d{1,3}))?\)")
# a citation that already carries its wording
ALREADY_QUOTED = re.compile(r'["”]\*{0,2}\s*$')

_AR_DIACRITICS = "".join(chr(c) for c in range(0x0610, 0x061B)) + "".join(
    chr(c) for c in range(0x064B, 0x0660)
)


def load_translation():
    """{surah: {ayah: english_text}} for all 114 chapters (6236 verses)."""
    out = {}
    for ch in range(1, 115):
        path = DATA / f"chapter_{ch:03d}.js"
        raw = path.read_text(encoding="utf-8")
        raw = re.sub(r"^\s*var\s+chapterData_\d+\s*=\s*", "", raw)
        raw = raw.rstrip().rstrip(";")
        themes = json.loads(raw)
        verses = {}
        for theme in themes:
            for v in theme["verses"]:
                verses[int(v["ayah_no_surah"])] = v["ayah_en"].strip()
        out[ch] = verses
    return out


# ---------------------------------------------------------------- normalising

_TRANSLIT = str.maketrans(
    {
        "ā": "a", "ī": "i", "ū": "u", "ṭ": "t", "ḥ": "h", "ṣ": "s", "ḍ": "d",
        "ẓ": "z", "ẓ": "z", "ʿ": "", "ʾ": "", "’": "'", "‘": "'", "ʼ": "'",
        "ā": "a", "ŏ": "o", "ë": "e", "ñ": "n", "š": "s", "č": "c",
    }
)

STOP = set(
    """a an the and or but of to in on for with from by as at is are was were be been
    being do does did not no nor so than that this these those it its his her their
    them they he she we you your our i will would shall should can could may might
    must has have had having who whom whose which what when where how why all any each
    every some both such then there here into onto upon over under again more most
    other others only own same too very just also about after before between during
    out up down off once while because if unless until against through against""".split()
)


def norm(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.translate(_TRANSLIT)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("˹", " ").replace("˺", " ")
    text = re.sub(r"[^\w\s']", " ", text.lower())
    return text


_SUFFIX = ("ingly", "edly", "ing", "ies", "ied", "es", "ed", "ly", "s")


def stem(w):
    """'testing'/'tests' -> 'test'; keeps short words intact."""
    for suf in _SUFFIX:
        if len(w) - len(suf) >= 3 and w.endswith(suf):
            return w[: -len(suf)] + ("y" if suf == "ies" else "")
    return w


def words(text):
    return [stem(w) for w in norm(text).split()
            if w and w not in STOP and len(w) > 1]


# --------------------------------------------------------------- sentence map

_SENT_SPLIT = re.compile(r"(?<=[.?!”])\s+(?=[“\"A-Z˹])")


def sentences(verse):
    """Split a verse into quotable sentences. Short verses stay whole."""
    verse = verse.strip()
    if len(verse) <= 170:
        return [verse]
    raw = [p.strip() for p in _SENT_SPLIT.split(verse) if p.strip()]
    # "The angels said, “O Lot!" must not stand alone — glue stubs forward
    parts = []
    for p in raw:
        if parts and len(parts[-1]) < 26:
            parts[-1] = parts[-1] + " " + p
        else:
            parts.append(p)
    if parts and len(parts[-1]) < 26 and len(parts) > 1:
        parts[-2] = parts[-2] + " " + parts[-1]
        parts.pop()
    return parts or [verse]


def _score(query_words, sent_words):
    """How strongly `sent_words` is the thing the paraphrase is talking about."""
    if not sent_words:
        return 0.0, 0
    qs = set(query_words)
    ss = set(sent_words)
    inter = qs & ss
    n = len(inter)
    if n == 0:
        return 0.0, 0
    recall = n / len(ss)
    if n == 1 and len(ss) > 2:
        recall *= 0.35          # a single shared word proves little
    return recall, n


def candidates(tr, surah, start, end=None, max_span=8):
    """Every quotable span a `start..end` citation could be pointing at."""
    verses = tr.get(surah, {})
    if not verses:
        return []
    end = start if not end or end <= start else min(end, max(verses))
    out = []
    run = list(range(start, min(end, start + max_span) + 1))
    for a in run:
        v = verses.get(a)
        if not v:
            continue
        if len(v) <= 260:
            out.append((v, a, a))
        for s in sentences(v):
            out.append((s, a, a))
    if len(run) > 1:
        whole = " ".join(verses.get(a, "") for a in run).strip()
        if len(whole) <= 400:
            out.append((whole, start, end))
    return out


MAX_SPAN = 8          # widest range citation we will try to quote from
MAX_QUOTE = 460       # a fallback longer than this is a dump, not a quote


def pick_quote(tr, surah, start, end, context, wide_context=None):
    """
    Choose the wording a citation is there for.

    `context` is the sentence the citation sits in; `wide_context` is the whole
    paragraph, tried when the tight sentence shares nothing with the verse.
    Returns (quote, score, from_ayah, to_ayah); score 0 means nothing narrower
    could be justified and the verse is quoted whole.
    """
    cands = candidates(tr, surah, start, end)
    if not cands:
        return None, 0.0, start, end

    # pass 1/2: a candidate the surrounding words actually name (2+ shared)
    for ctx in (context, wide_context):
        if not ctx:
            continue
        qw = set(words(ctx)[-70:])
        scored = [(len(qw & set(words(txt))) / len(set(words(txt))), -(b - a),
                   -len(txt), txt, a, b)
                  for txt, a, b in cands if len(qw & set(words(txt))) >= 2]
        if scored:
            scored.sort(key=lambda x: (-x[0], -x[1], -x[2]))
            sc, _, _, text, a, b = scored[0]
            return text, sc, a, b

    # pass 3: only one shared word — acceptable if the span is short and the
    # overlap is as good as it gets anywhere in the verse
    if context:
        qw = set(words(context)[-70:])
        weak = [(len(qw & set(words(txt))), -len(txt), txt, a, b)
                for txt, a, b in cands
                if len(qw & set(words(txt))) == 1 and len(txt) <= 300]
        if weak:
            weak.sort(key=lambda x: (-x[0], -x[1]))
            return weak[0][2], 0.1, weak[0][3], weak[0][4]

    run = list(range(start, min(end or start, start + MAX_SPAN) + 1))
    whole = " ".join(tr[surah][i] for i in run if i in tr[surah]).strip()
    if len(whole) <= MAX_QUOTE:
        return whole, 0.0, start, end
    # too long to dump: take the opening verse of the span, trimmed to a cap
    first = tr[surah].get(run[0], "")
    if len(first) <= MAX_QUOTE:
        return first, 0.0, run[0], run[0]
    return sentences(first)[0], 0.0, run[0], run[0]





BARE_NUM = re.compile(r"(?<=[\d:]),\s*(\d{1,3})(?![\d:])")


def expand_abbrev(inner):
    """`(5:17, 18, 40)` means 5:17, 5:18 and 5:40 — say so in full."""
    surah = None
    out, pos = [], 0
    for m in re.finditer(r"(\d{1,3}):(\d{1,3})", inner):
        out.append(inner[pos:m.start()])
        surah = m.group(1)
        out.append(m.group(0))
        pos = m.end()
        nxt = BARE_NUM.match(inner, pos)
        while nxt:
            out.append(f", {surah}:{nxt.group(1)}")
            pos = nxt.end()
            nxt = BARE_NUM.match(inner, pos)
    out.append(inner[pos:])
    return "".join(out)


def expand_end(a, b):
    """`7:148-55` means 148-155; `3:106-7` means 106-107."""
    if b is None:
        return a
    if b >= a:
        return b
    s, u = str(a), str(b)
    return int(s[: len(s) - len(u)] + u)


def clean_quote(q):
    """Make a snippet safe to sit inside `*"…"*` markdown."""
    q = q.strip()
    q = q.replace("**", "")
    q = re.sub(r"\s+", " ", q)
    q = q.strip(" ").strip()
    if q.endswith((",", ";", "—", "-", "–")):
        q = q[:-1].rstrip()
    if q.startswith("”"):
        q = q.lstrip("”").lstrip()
    if q.startswith("˺"):
        q = q.lstrip("˺").lstrip()
    q = re.sub(r'([.!?])["”]{2,}$', r'\1”', q)   # no doubled closing marks
    return q
