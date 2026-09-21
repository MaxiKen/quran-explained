#!/usr/bin/env python3
"""
Chain-loop cleanup for the verse commentary.

The generator that produced the first draft of some chapters fell into a
"chain" habit: a short sentence that only echoes the tail of the sentence
before it, so paragraphs read as loops ("Weakness alleged, wickedness denied.
Denied wickedness persists in records. Records show invitations...").

The existing pass in scripts/edit_tafsir.py catches loops whose sentences
share most of their wording. This cleaner adds a second test — the leading
word of a sentence repeating the tail of the previous one — and removes the
runs it finds, never touching a sentence that carries a citation, a hadith
reference, a Qur'an reference, a quotation or a number.

Usage:
    python3 scripts/chain_cleanup.py --dir "markdown commentry" --dry-run
    python3 scripts/chain_cleanup.py --dir "markdown commentry"
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, ".")
try:                                        # reuse the shared helpers
    from scripts import edit_tafsir as T    # type: ignore
except Exception:                           # pragma: no cover
    T = None

STOP = set("""a an and or but to in on at by for with as is are was were be been being this that
these those it its he she they we you his her their our your not no if then than so such from
into over under of the there here what which who whom whose when where why how all any both each
few more most other some own same too very can will just should now""".split())

CITE_RE = re.compile(
    r"\b\d{1,3}:\d{1,3}\b|Ṣaḥīḥ|Sahih|Sunan|Musnad|Bukh[āa]r[iī]|Muslim|Tirmidh[iī]|Nas[āa]ʾ[iī]|"
    r"Ab[ūu] D[āa]w[ūu]d|Ibn M[āa]jah|ﷺ|\b\d{3,4}\b|“[^”]{15,}”")
VERSE_HEAD_RE = re.compile(r"^##\s+.*?\b(\d{1,3}):(\d{1,3})\s*$")


def tokens(sentence: str) -> list[str]:
    return [t.lower().strip(".,;:!?()[]\"“”'’—–-") for t in sentence.split()]


def content_words(sentence: str) -> list[str]:
    return [t for t in tokens(sentence) if len(t) > 3 and t not in STOP]


def key(word: str) -> str:
    return re.sub(r"[^a-z]", "", word)[:5]


def sent_split(paragraph: str) -> list[str]:
    if T is not None:
        return T.sents_of(paragraph)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()]


def lemma_overlap(a: str, b: str) -> float:
    ca, cb = set(map(key, content_words(a))), set(map(key, content_words(b)))
    if not ca or not cb:
        return 0.0
    return len(ca & cb) / len(ca | cb)


def echo_link(prev: str, cur: str) -> bool:
    """True when the sentence opens on the word the previous one ended with."""
    pw, cw = content_words(prev), content_words(cur)
    if not pw or not cw:
        return False
    return key(pw[-1]) == key(cw[0])


def chain_flags(sents: list[str]) -> list[bool]:
    n = len(sents)
    flags = [False] * n
    base_flags = T.chain_flags(sents) if T is not None else [False] * n
    for i in range(n):
        if base_flags[i]:
            flags[i] = True
            continue
        if i == 0:
            continue
        s = sents[i]
        words = len(s.split())
        if not (3 <= words <= 18) or CITE_RE.search(s):
            continue
        new_lemmas = {key(w) for w in content_words(s)}
        if len(new_lemmas) > 4:
            continue
        prev = sents[i - 1]
        nxt = sents[i + 1] if i + 1 < n else ""
        echo = echo_link(prev, s)
        if echo and (lemma_overlap(prev, s) >= 0.25 or (nxt and echo_link(s, nxt))):
            flags[i] = True
    return flags


def is_degenerate(sents: list[str]) -> bool:
    """A paragraph in which a large share of sentence transitions are word
    chains is generator loop text: the meaning has left the prose and the
    sentences only hand a word to the next one."""
    if len(sents) < 5:
        return False
    links = sum(1 for i in range(1, len(sents)) if echo_link(sents[i - 1], sents[i])
                or lemma_overlap(sents[i - 1], sents[i]) >= 0.5)
    return links / (len(sents) - 1) >= 0.30


def substantive(sentence: str) -> bool:
    """A sentence worth keeping out of a degenerate paragraph."""
    if CITE_RE.search(sentence):
        return True
    words = len(sentence.split())
    lemmas = {key(w) for w in content_words(sentence)}
    return words >= 11 and len(lemmas) >= 5


def clean_paragraph(para: str) -> tuple[str, int]:
    sents = sent_split(para)
    if len(sents) < 3:
        return para, 0
    if is_degenerate(sents):
        keep = [substantive(s) for s in sents]
        if not any(keep):
            keep[max(range(len(sents)), key=lambda k: len(content_words(sents[k])))] = True
        if kept := [s for s, k in zip(sents, keep) if k]:
            return " ".join(kept), len(sents) - len(kept)
        return para, 0
    flags = chain_flags(sents)
    if not any(flags):
        return para, 0
    dominated = sum(flags) >= 0.5 * len(sents)
    keep = [True] * len(sents)
    i = 0
    while i < len(sents):
        if flags[i]:
            j = i
            while j < len(sents) and flags[j]:
                j += 1
            run = list(range(i, j))
            if dominated or len(run) >= 2 or (j == len(sents) and run):
                for k in run:
                    keep[k] = False
            i = j
        else:
            i += 1
    if not any(keep):
        # keep the sentence with the most content rather than empty the page
        best = max(range(len(sents)), key=lambda k: len(content_words(sents[k])))
        keep[best] = True
    kept = [s for s, k in zip(sents, keep) if k]
    removed = sum(1 for k in keep if not k)
    # repair a stump left dangling on a colon or dash
    if kept and re.search(r"[:\u2014-]\s*$", kept[-1]) and len(kept[-1].split()) < 14 and len(kept) > 1:
        kept.pop()
    return " ".join(kept), removed


def clean_chapter(args):
    ch, src_dir, out_dir, dry_run = args
    t0 = time.time()
    path = f"{src_dir}/{ch:03d}.md"
    text = open(path, encoding="utf-8").read()
    before = sum(1 for _ in re.finditer(r"(?<=[.!?])\s", text))

    out_lines: list[str] = []
    removed_total = 0
    for chunk in text.split("\n\n"):
        stripped = chunk.strip()
        if not stripped or stripped.startswith(("#", ">", "**")) or stripped in {"---", "***"}:
            out_lines.append(chunk)
            continue
        if "\n" in stripped:                    # keep list blocks intact
            cleaned_any = False
            new_lines = []
            for line in stripped.split("\n"):
                c, n = clean_paragraph(line)
                removed_total += n
                cleaned_any = cleaned_any or bool(n)
                new_lines.append(c)
            out_lines.append("\n".join(new_lines) if cleaned_any else chunk)
            continue
        cleaned, n = clean_paragraph(stripped)
        removed_total += n
        out_lines.append(cleaned)

    new_text = "\n\n".join(out_lines)
    if not dry_run:
        with open(f"{out_dir}/{ch:03d}.md", "w", encoding="utf-8") as fh:
            fh.write(new_text)
    return ch, len(text.split()), len(new_text.split()), removed_total, time.time() - t0


def chain_density(text: str) -> tuple[float, int, int]:
    sents: list[str] = []
    for para in text.split("\n\n"):
        p = para.strip()
        if not p or p.startswith(("#", ">", "**")) or p in {"---", "***"}:
            continue
        sents.extend(sent_split(p))
    if len(sents) < 2:
        return 0.0, 0, len(sents)
    flags = chain_flags(sents)
    return (sum(flags) / (len(sents) - 1), sum(flags), len(sents))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="markdown commentry")
    ap.add_argument("--out", default=None)
    ap.add_argument("--chapters", default=None)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    out_dir = args.out or args.dir
    chapters = [int(x) for x in args.chapters.split(",")] if args.chapters else list(range(1, 115))

    jobs = [(c, args.dir, out_dir, args.dry_run) for c in chapters]
    tb = ta = removed = 0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        for ch, wb, wa, n, took in ex.map(clean_chapter, jobs):
            tb += wb
            ta += wa
            removed += n
            print(f"[ch {ch:03d}] {wb:>7,} -> {wa:>7,} words, {n:>4} chain sentences removed", file=sys.stderr)
    print(f"[chain cleanup] {tb:,} -> {ta:,} words ({ta/max(1,tb):.1%}); {removed:,} chain sentences removed "
          f"in {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
