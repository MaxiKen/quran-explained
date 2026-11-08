#!/usr/bin/env python3
"""Deterministic gates for the clear-teaching payload.

    python3 tools/clear/verify.py                      # tracked samples
    python3 tools/clear/verify.py --dir work/clear     # work in progress
    python3 tools/clear/verify.py --file data/clear_002.json

Every rule in tools/clear/STYLE.md is enforced here, and a violation is a
failure rather than a warning. A payload is not committed until this reports
"all clear" for it.

    words     420 per verse, band 400-440 (STYLE.md 2)
    script    Latin only; the salawat sign is the sole exception (3)
    aligned   every phrase of the app's ayah_en appears in the entry (4)
    distinct  no 8-word run shared between sibling entries (5)
    shape     house style and entry shape (6, 7)
    coverage  one entry per verse of the chapter (2.3)
"""
from __future__ import annotations

import argparse
import glob
import itertools
import json
import os
import re
import sys

# ---- STYLE.md 2 : volume -------------------------------------------------
WORD_TARGET = 420
WORD_TOLERANCE = 20
WORD_MIN = WORD_TARGET - WORD_TOLERANCE      # 400
WORD_MAX = WORD_TARGET + WORD_TOLERANCE      # 440

# ---- STYLE.md 5 : distinctness -------------------------------------------
SHINGLE = 8
SHINGLE_TOLERANCE = 0.05

# ---- STYLE.md 3 : script --------------------------------------------------
ARABIC = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
SAW = '\ufdfa'

# ---- STYLE.md 6 : house style ---------------------------------------------
EMDASH = '\u2014'
SEMI = ';'
FIRST_PERSON = re.compile(r"\b(I|me|my|mine|myself)\b")
CITATION = re.compile(
    r'\b(qutb|quṭb|sayyid|tabari|ṭabarī|tabarī|ibn kathir|kathīr|'
    r'fi zilal|fī ẓilāl|zilal|ẓilāl|'
    r'the tafsir|the tafsīr|the commentary|the commentators|the sources|'
    r'classical scholars (?:say|says|note|notes))\b', re.I)
GENERIC_HEADINGS = {
    'commentary', 'explanation', 'notes', 'overview', 'summary', 'details',
    'introduction', 'conclusion', 'background', 'context', 'analysis',
    'discussion', 'more', 'miscellaneous', 'general', 'meaning', 'lessons',
}
OTHER_MARKUP = re.compile(
    r'<[a-zA-Z/][^>]*>'            # HTML
    r'|\]\([^)]*\)'                # links
    r'|^```'                        # code fences
    r'|^\s*\|.*\|\s*$'             # tables
    r'|^\s*(?:-{3,}|\*{3,}|_{3,})\s*$'   # horizontal rules
    r'|[\U0001F300-\U0001FAFF\u2600-\u27BF]',  # emoji
    re.M)
QUOTED = re.compile(r'"[^"]*"')

# The app's translations contain nested speech, and some contain a semicolon or
# an em dash of their own. Rather than parse nesting (which the same delimiter
# cannot express), the writer marks the passage that quotes the translation:
#
#     ==In the Name of Allah—the Most Compassionate== is where the surah opens.
#
# Everything between == ... == is the translation speaking, and the house rules
# do not apply inside it. Ordinary quotations of a phrase still use " ... " and
# are subject to the rules as usual.
VERSE_SPAN = re.compile(r'==(.+?)==', re.S)

IN_SHORT = re.compile(r'^##\s+In short\s*$', re.M | re.I)


# --------------------------------------------------------------------------
# counting and normalisation
# --------------------------------------------------------------------------
def words(text: str) -> int:
    """Prose words, per STYLE.md 2.2: headings and bullets count, markup does not."""
    t = re.sub(r'^#{1,6}\s*', '', text, flags=re.M)   # keep heading words
    t = re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', t, flags=re.M)  # keep bullet words
    t = t.replace('**', '').replace('*', '')          # emphasis marks are not words
    # the salawat sign rides on the word before it ("the Prophet ﷺ" is two
    # words, "Muhammad\ufdfa" is one), so it must not inflate the count
    t = t.replace(' ' + SAW, SAW).replace(SAW, '')
    return len([w for w in t.split() if w.strip()])


def unquoted(text: str) -> str:
    """The writer's own prose (§6).

    Removes the marked translation span and any plain quotation, so that a
    style rule only judges what the writer actually wrote.
    """
    return QUOTED.sub('""', VERSE_SPAN.sub('""', text))


def fold(s: str) -> list[str]:
    s = s.lower()
    for a, b in (('ʿ', ''), ('ʾ', ''), ('˹', '['), ('˺', ']')):
        s = s.replace(a, b)
    return re.findall(r"[a-z0-9']+", s)


def shingles(ws: list[str], n: int) -> set[tuple]:
    return {tuple(ws[i:i + n]) for i in range(max(1, len(ws) - n + 1))}


def translation_phrases(translation: str) -> list[str]:
    """The app's translation, split into the pieces an entry must carry (§4)."""
    t = re.sub(r'˹[^˺]*˺', '', translation)           # drop ˹alone˺ glosses
    return [p.strip() for p in re.split(r'\s*[\u2014,]\s*', t) if len(p.split()) >= 2]


def load_translations(surah: int, data_dir: str) -> list[str]:
    """ayah_en for a chapter, straight out of data/chapter_NNN.js."""
    path = os.path.join(data_dir, f'chapter_{surah:03d}.js')
    with open(path, encoding='utf-8') as fh:
        src = fh.read()
    body = src[src.index('['): src.rindex(']') + 1]
    data = json.loads(body)                            # the file is valid JSON
    out = []
    for theme in data:
        for v in theme['verses']:
            out.append((v['ayah_no_surah'], v['ayah_en']))
    out.sort()
    return [t for _, t in out]


# --------------------------------------------------------------------------
# the checks
# --------------------------------------------------------------------------
def check_shape(tag: str, entry: str) -> list[str]:
    errs = []
    body = unquoted(entry)

    if EMDASH in body:
        line = next((l for l in body.split('\n') if EMDASH in l), '')
        errs.append(f'{tag}: em dash outside a quotation: {line[:80]!r}')
    if SEMI in body:
        line = next(l for l in body.split('\n') if SEMI in l)
        errs.append(f'{tag}: semicolon: {line[:80]!r}')
    m = FIRST_PERSON.search(body)
    if m:
        errs.append(f'{tag}: first person {m.group(0)!r}')
    m = CITATION.search(body)
    if m:
        errs.append(f'{tag}: names or alludes to the source ({m.group(0)!r})')

    if re.search(r'^#\s', entry, re.M) or re.search(r'^#{3,}\s', entry, re.M):
        errs.append(f'{tag}: heading level other than ##')
    if re.search(r'^\s*#{2,}\s*$', entry, re.M):
        errs.append(f'{tag}: empty heading')
    for h in re.findall(r'^##\s+(.+)$', entry, re.M):
        if h.strip().lower().rstrip('.:') in GENERIC_HEADINGS:
            errs.append(f'{tag}: generic heading {h.strip()!r}')

    if OTHER_MARKUP.search(entry):
        errs.append(f'{tag}: markup other than ##, **, * and - ')
    # The renderer splits an entry on blank lines and nothing else, so a
    # heading or the first bullet of a list that trails a line of prose on a
    # single newline is never parsed: '## In short' is then printed as literal
    # text inside a paragraph. Only a bullet directly after a bullet is fine.
    lines = entry.split('\n')
    for i, line in enumerate(lines):
        if i == 0 or not lines[i - 1].strip():
            continue
        glued = line.startswith('## ') or (
            line.startswith('- ') and not lines[i - 1].startswith('- '))
        if glued:
            errs.append(f'{tag}: {line[:2]!r} needs a blank line before it, '
                        f'or it renders as literal text inside a paragraph')
            break
    if not re.search(r'^##\s+In short\s*$', entry, re.M | re.I):
        errs.append(f'{tag}: no "## In short" section')
    else:
        tail = entry[entry.rindex('##'):] if 'In short' in entry else ''
        n = len(re.findall(r'^\s*-\s+', tail, re.M))
        if not 3 <= n <= 5:
            errs.append(f'{tag}: In short has {n} bullets, expected 3-5')
    heads = [h.strip() for h in re.findall(r'^##\s+(.+)$', entry, re.M)]
    if heads and not heads[0].lower().startswith('what the verse does'):
        errs.append(f'{tag}: first heading is {heads[0]!r}, expected the '
                    f'opening "## What the verse does" section')
    headings = re.findall(r'^##\s+', entry, re.M)
    if len(headings) < 2:
        errs.append(f'{tag}: only {len(headings)} heading(s); an opening '
                    f'section and "In short" are required')
    return errs


def check_script(tag: str, entry: str) -> list[str]:
    stripped = entry.replace(SAW, '')
    found = sorted(set(ARABIC.findall(stripped)))
    if found:
        return [f'{tag}: Arabic-block letters present: '
                + ', '.join(f'U+{ord(c):04X}' for c in found)]
    return []


def check_alignment(tag: str, entry: str, translation: str) -> list[str]:
    body = set(fold(entry))
    # the marked span, if present, must be the translation itself
    for span in VERSE_SPAN.findall(entry):
        if fold(span) != fold(translation.replace('\u02f9', '').replace('\u02fa', '')):
            return [f'{tag}: the == span does not match the app translation word for word']
    missing = [p for p in translation_phrases(translation)
               if not all(w in body for w in fold(p))]
    if missing:
        return [f'{tag}: does not carry the translation: {missing}']
    return []


def check_words(tag: str, entry: str) -> tuple[list[str], int]:
    n = words(entry)
    if n < WORD_MIN:
        return [f'{tag}: {n} words, under the {WORD_MIN}-word floor '
                f'({WORD_TARGET} \u00b1 {WORD_TOLERANCE}). Add {WORD_MIN - n} or more.'], n
    if n > WORD_MAX:
        return [f'{tag}: {n} words, over the {WORD_MAX}-word ceiling '
                f'({WORD_TARGET} \u00b1 {WORD_TOLERANCE}). Cut {n - WORD_MAX} or more.'], n
    return [], n


def check_coverage(rec: dict, n_verses: int, partial: bool = False) -> list[str]:
    """One entry per verse (STYLE.md 2.3).

    With partial=True the payload may cover verses 1..N only, which is how a
    long sūrah is written in blocks. The prefix must still be unbroken and every
    other rule still applies."""
    errs = []
    blocks = rec.get('blocks') or []
    if not partial and len(blocks) != n_verses:
        errs.append(f'{rec.get("surah")}: {len(blocks)} entries for {n_verses} verses')
    if partial and len(blocks) > n_verses:
        errs.append(f'{rec.get("surah")}: {len(blocks)} entries, more than the {n_verses} verses')
    ranges = rec.get('ranges') or []
    if len(ranges) != len(blocks):
        errs.append(f'{rec.get("surah")}: {len(ranges)} ranges for {len(blocks)} entries')
    verses = rec.get('verses') or {}
    if len(verses) != len(blocks):
        errs.append(f'{rec.get("surah")}: {len(verses)} verse mappings for {len(blocks)} entries')
    # one block per verse, in order, no shared block
    seen = set()
    written = len(blocks)
    for v in range(1, (written if partial else n_verses) + 1):
        idx = verses.get(str(v))
        if idx is None:
            errs.append(f'{rec.get("surah")}:{v}: no entry')
            continue
        if idx in seen:
            errs.append(f'{rec.get("surah")}:{v}: shares an entry with another verse '
                        f'(block {idx}); every verse needs its own (\u00a72.3)')
        seen.add(idx)
        expected_range = f'{rec.get("surah")}:{v}'
        if idx < len(ranges) and ranges[idx] != expected_range:
            errs.append(f'{rec.get("surah")}:{v}: range says {ranges[idx]!r}, '
                        f'expected {expected_range!r}')
    return errs


def check_payload_shape(rec: dict) -> list[str]:
    errs = []
    if rec.get('lang') != 'en':
        errs.append(f'lang is {rec.get("lang")!r}, expected "en"')
    if rec.get('dir') != 'ltr':
        errs.append(f'dir is {rec.get("dir")!r}, expected "ltr"')
    if not rec.get('source'):
        errs.append('no source label')
    if not rec.get('basedOn'):
        errs.append('no basedOn line')
    # STYLE.md 10: the source's caveat is stated once per chapter. The Urdu
    # payload carries one, so an English payload that replaces it must too.
    if not (rec.get('notice') or '').strip():
        errs.append('no notice: the chapter-level caveat from STYLE.md 10 is '
                    'missing, so the source is credited without it')
    return errs


def check_distinct(rec: dict, entries: dict[int, str]) -> list[str]:
    """STYLE.md 5, applied to the writer's own prose only.

    The == translation span == is mandated word for word by STYLE.md 4, so two
    verses the app happens to translate near-identically (2:134 and 2:141 are
    the same sentence) would otherwise fail through no choice of the writer's.
    The span is already validated against the translation by check_alignment.
    """
    errs = []
    sh = {v: shingles(fold(VERSE_SPAN.sub(' ', e)), SHINGLE)
          for v, e in entries.items()}
    for a, b in itertools.combinations(sorted(entries), 2):
        if not sh[a] or not sh[b]:
            continue
        overlap = len(sh[a] & sh[b]) / min(len(sh[a]), len(sh[b]))
        if overlap > SHINGLE_TOLERANCE:
            errs.append(f'{rec.get("surah")}:{a} and {b} share {overlap:.0%} of '
                        f'8-word runs (limit {SHINGLE_TOLERANCE:.0%})')
    return errs


def verify_file(path: str, data_dir: str, verbose: bool = True,
                partial: bool = False) -> tuple[bool, list[str]]:
    with open(path, encoding='utf-8') as fh:
        rec = json.load(fh)
    surah = rec.get('surah')
    label = os.path.basename(path)

    errs = check_payload_shape(rec)
    try:
        translations = load_translations(surah, data_dir)
    except Exception as exc:                              # noqa: BLE001
        errs.append(f'cannot read the translation for surah {surah}: {exc}')
        return False, errs

    errs += check_coverage(rec, len(translations), partial=partial)
    if partial and verbose:
        done = len(rec.get('blocks') or [])
        if done < len(translations):
            print(f'      partial: {done} of {len(translations)} verses '
                  f'written ({done / len(translations) * 100:.0f}%)')
    entries = {v + 1: b for v, b in enumerate(rec.get('blocks') or [])}

    counts = {}
    for v in sorted(entries):
        tag = f'{surah}:{v}'
        entry = entries[v]
        errs += check_script(tag, entry)
        errs += check_shape(tag, entry)
        if v <= len(translations):
            errs += check_alignment(tag, entry, translations[v - 1])
        e, n = check_words(tag, entry)
        errs += e
        counts[v] = n

    errs += check_distinct(rec, entries)

    if verbose:
        if errs:
            print(f'FAIL {label}  ({len(errs)} problem(s))')
            for e in errs:
                print('   -', e)
        else:
            print(f'ok   {label}  ({len(entries)} entries, all within '
                  f'{WORD_MIN}-{WORD_MAX} words)')
        if counts:
            lo, hi = min(counts.values()), max(counts.values())
            mean = sum(counts.values()) / len(counts)
            print(f'      words: min {lo}, mean {mean:.0f}, max {hi} '
                  f'(target {WORD_TARGET} \u00b1 {WORD_TOLERANCE})')
            off = [(v, c) for v, c in counts.items() if not WORD_MIN <= c <= WORD_MAX]
            if off and not errs:
                print(f'      outside the band: {off}')
    return (not errs), errs


def is_block(path: str) -> bool:
    """True for a `NNN-blockK.json` payload, a block of a longer sūrah."""
    return re.search(r'-block\d+\.json$', path) is not None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', default='tools/clear/samples',
                    help='directory of NNN.json payloads (default: tracked samples)')
    ap.add_argument('--file', help='a single payload to check')
    ap.add_argument('--data', default='data', help='where chapter_NNN.js lives')
    ap.add_argument('--partial', action='store_true',
                    help='accept a payload covering verses 1..N only (work in progress)')
    args = ap.parse_args()

    if args.file:
        files = [args.file]
    else:
        files = sorted(glob.glob(os.path.join(args.dir, '*.json')))
    if not files:
        print(f'no payload found in {args.file or args.dir}')
        return 1

    failed = 0
    for f in files:
        # A file named NNN-blockK.json is a block of a longer sūrah, so it is
        # checked as a prefix. One entry per verse is still required, as is
        # every other rule; only the coverage end is open.
        ok, _ = verify_file(f, args.data,
                            partial=args.partial or is_block(f))
        if not ok:
            failed += 1
    print()
    if failed:
        print(f'FAILED: {failed} of {len(files)} payload(s) do not meet STYLE.md')
        return 1
    print(f'all clear: {len(files)} payload(s) meet STYLE.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
