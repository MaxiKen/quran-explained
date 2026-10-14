#!/usr/bin/env python3
"""A job's material prepared for fast, complete reading.

    python3 tools/guidance/digest.py 002-001-001              # part 1 of the digest (and how many parts there are)
    python3 tools/guidance/digest.py 002-001-001 --part 2     # the next part
    python3 tools/guidance/digest.py 002-001-001 --write      # whole digest to work/digest/<job>.md
    python3 tools/guidance/digest.py --quote 6:101            # the app's translation of any verse (or 19:88-95)

The digest loses no content that an entry may carry. It only removes what the
entry must not carry anyway or what is retrievable on demand:

- Arabic script (the English rendering always follows it) and honorific
  formulas, which the output never reproduces,
- long quotations of other verses when the source gives the reference: they
  are collapsed to `[Q 6:101 "first words …"]`, and `--quote 6:101` prints the
  app's own translation to quote from,
- paragraphs that repeat an earlier paragraph of the same job almost word for
  word (the same hadith copied twice, a repeated gloss): collapsed to
  `[≈ repeats ¶n]`, keeping the first words so the repetition can be checked,
- a source's sign-off lines.

Before the material comes a checklist per verse: the cited verses, collectors,
grades, names and terms that `verify.py`'s coverage gate will look for in the
entry (written in the entry's own words). Writing against the checklist is what
makes an entry complete at the first attempt.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import (ARABIC_RE, SAW, WORK, Job, chapter_meta, ensure_dir, fold, load_chapter,  # noqa: E402
                    strip_arabic_lines, word_count)
from generate import load_jobs  # noqa: E402
from verify import COLLECTORS, GRADES, extract_anchors, surah_names  # noqa: E402

CHUNK = 16_000          # a tool result shows about 20 K characters before it is truncated in the middle
SHINGLE = 8             # words per shingle for the repetition check
REPEAT_MIN_WORDS = 14   # shorter paragraphs are kept as they are
REPEAT_RATIO = 0.6      # share of a paragraph's shingles already seen -> collapsed
QUOTE_MIN_CHARS = 45    # shorter verse quotations stay inline (they are phrase-level)

_INLINE_AR_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDF9\uFDFB-\uFDFF\uFE70-\uFEFF]+')
_HONORIFIC_RE = re.compile(
    r"\(?\s*(?:may\s+All[aā]h\s+(?:be\s+pleased\s+with\s+(?:him|her|them|both(?:\s+of\s+them)?|all\s+of\s+them)"
    r"|have\s+mercy\s+(?:up)?on\s+(?:him|her|them))|(?:peace\s+(?:and\s+blessings\s+)?be\s+upon\s+him))\s*\)?,?", re.I)
_RA_RE = re.compile(r"\(\s*(?:R\.A\.|RA|r\.a\.|RAA)\s*\)")
_SIGNOFF_RE = re.compile(r"Al-?\s*Hamdulill[aā]h\s+The\s+Commentary\s+on\s+S[uū]rah\s+[^\n]*?\s+Ends\s+here\s*\.?", re.I | re.S)
# (quoted verse text)(S:N) and "quoted verse text" (S:N) / [S:N]
_QUOTE_PAREN_RE = re.compile(r'\(((?:[^()]|\([^()]*\)){%d,}?)\)\s*\((\d{1,3})\s*:\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?\)' % QUOTE_MIN_CHARS)
_QUOTE_DQ_RE = re.compile(r'[“"]([^“”"]{%d,}?)[”"]\s*[\(\[]\s*(\d{1,3})\s*:\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?\s*[\)\]]' % QUOTE_MIN_CHARS)
_WS_RE = re.compile(r'[ \t]{2,}')
_SPACE_PUNCT_RE = re.compile(r'\s+([,.;:!?)\]])')
_EMPTY_PAREN_RE = re.compile(r'\(\s*\)|\[\s*\]')


def _collapse_quote(m: re.Match) -> str:
    text, s, a, b = m.group(1).strip(), int(m.group(2)), int(m.group(3)), m.group(4)
    if not (1 <= s <= 114 and 1 <= a <= 286):
        return m.group(0)
    words = text.split()
    head = ' '.join(words[:7]) + (' …' if len(words) > 7 else '')
    ref = f'{s}:{a}' + (f'-{int(b)}' if b else '')
    return f'[Q {ref} "{head}"]'


def clean_for_reading(text: str) -> str:
    """Everything the digest removes from a block, in one place."""
    t = strip_arabic_lines(text)
    t = _INLINE_AR_RE.sub(' ', t)
    t = t.replace('\ufffd', "'")
    t = _SIGNOFF_RE.sub('', t)
    t = _HONORIFIC_RE.sub('', t)
    t = _RA_RE.sub('', t)
    t = _QUOTE_PAREN_RE.sub(_collapse_quote, t)
    t = _QUOTE_DQ_RE.sub(_collapse_quote, t)
    t = _EMPTY_PAREN_RE.sub('', t)
    t = _SPACE_PUNCT_RE.sub(r'\1', t)
    t = _WS_RE.sub(' ', t)
    t = re.sub(r' *\n *', '\n', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    # keep ﷺ attached to the word before it
    t = re.sub(r'\s+' + SAW, ' ' + SAW, t)
    return t.strip()


def _shingles(words: list[str], n: int = SHINGLE) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + n]) for i in range(0, max(0, len(words) - n + 1))}


class Repeats:
    """Collapses paragraphs that repeat earlier paragraphs of the same job."""

    def __init__(self) -> None:
        self.seen: set[tuple[str, ...]] = set()
        self.count = 0
        self.heads: list[tuple[int, str, str]] = []   # (paragraph id, source, first words)

    def process(self, source: str, paragraph: str) -> str:
        words = fold(paragraph).split()
        self.count += 1
        pid = self.count
        if len(words) < REPEAT_MIN_WORDS:
            return paragraph
        sh = _shingles(words)
        if sh and len(sh & self.seen) / len(sh) >= REPEAT_RATIO:
            first = ' '.join(paragraph.split()[:9])
            return f'[≈ repeats an earlier paragraph: "{first} …" ({word_count(paragraph)} words)]'
        self.seen |= sh
        self.heads.append((pid, source, ' '.join(paragraph.split()[:6])))
        return paragraph


def digest_block(source: str, text: str, repeats: Repeats) -> tuple[str, int, int]:
    raw_words = word_count(text)
    cleaned = clean_for_reading(text)
    out = []
    for para in re.split(r'\n\s*\n', cleaned):
        para = para.strip()
        if not para:
            continue
        out.append(repeats.process(source, para))
    body = '\n\n'.join(out)
    return body, raw_words, word_count(body)


def checklist(job: Job) -> str:
    """Per verse (or for the whole surah for an intro job): the anchors verify.py will look for."""
    own = surah_names(job.surah)
    lines = []
    targets = job.verses if job.kind == 'verses' else [None]
    for v in targets:
        blocks = [b for b in job.blocks if v is None or v in b.verses]
        anchors: dict[str, str] = {}
        for b in blocks:
            for k, d in extract_anchors(b.text).items():
                anchors.setdefault(k, d)
        xrefs, nums, cols, grades, names = [], [], [], [], []
        for k, d in anchors.items():
            if k.startswith('xref:'):
                if k.startswith(f'xref:{job.surah}:') and int(k.rsplit(':', 1)[1]) in job.verses:
                    continue
                xrefs.append(d)
            elif k.startswith('num:'):
                nums.append(d)
            elif k in COLLECTORS:
                cols.append(d)
            elif k in GRADES:
                grades.append(d)
            elif k in own:
                continue
            else:
                names.append(d)
        if v is None:
            head = f'### surah {job.surah} introduction ({sum(word_count(b.text) for b in blocks)} words of opening material)'
        else:
            mw = job.material_words.get(v, 0)
            head = f'### {job.surah}:{v}  (material ≈ {mw:.0f} words → entry ≈ {max(150, 0.6 * mw):.0f}+ words)'
        lines.append(head)
        if xrefs:
            lines.append('- verses cited (cite only these numbers): ' + ', '.join(sorted(set(xrefs), key=_xref_key)))
        if cols:
            lines.append('- collectors: ' + ', '.join(sorted(set(cols))))
        if grades:
            lines.append('- grades: ' + ', '.join(sorted(set(grades))))
        if nums:
            lines.append('- numbers: ' + ', '.join(sorted(set(nums), key=lambda x: int(x))))
        if names:
            lines.append('- names and terms: ' + ', '.join(sorted(set(names), key=lambda x: fold(x))))
        lines.append('')
    return '\n'.join(lines).rstrip()


def _xref_key(ref: str) -> tuple[int, int]:
    s, a = ref.split(':')
    return int(s), int(a.split('-')[0])


def translations_block(job: Job) -> str:
    lines = []
    for a in job.ayahs:
        lines.append(f'- {job.surah}:{a["n"]}  "{a["en"]}"')
    return '\n'.join(lines)


def build_digest(job: Job) -> str:
    repeats = Repeats()
    bodies, raw_total, out_total = [], 0, 0
    for b in job.blocks:
        body, rw, ow = digest_block(b.source, b.text, repeats)
        raw_total += rw
        out_total += ow
        extra = f'  shared with verses {b.shared_outside}' if b.shared_outside else ''
        bodies.append(f'===== {b.source} ({b.range})  {rw} → {ow} words{extra} =====\n{body}\n')
    saving = 0 if raw_total == 0 else 100 * (1 - out_total / raw_total)
    meta = chapter_meta()[job.surah]
    head = (f'# {job.id} · surah {job.surah} {meta["name_en"]} · {job.kind} {job.verses if job.kind == "verses" else ""}'
            f' · {len(job.blocks)} blocks · {raw_total} words of material → {out_total} words to read (−{saving:.0f}%)\n')
    parts = [head,
             '## Checklist (what verify.py will look for: say all of it, in your own words, each item once)\n' + checklist(job),
             '## The verses (quote the app\'s translation word for word in the opening)\n' + translations_block(job),
             '## Material (Arabic removed, honorifics removed, verse quotations with a reference collapsed to [Q S:N …], '
             'repeated paragraphs collapsed to [≈ repeats …])\n' + '\n'.join(bodies)]
    return '\n\n'.join(parts).rstrip() + '\n'


def split_parts(text: str, chunk: int = CHUNK) -> list[str]:
    parts, cur = [], ''
    for para in text.split('\n'):
        if len(cur) + len(para) + 1 > chunk and cur:
            parts.append(cur)
            cur = ''
        cur += para + '\n'
    if cur.strip():
        parts.append(cur)
    return parts


def quote(ref: str) -> str:
    m = re.fullmatch(r'\s*(\d{1,3})\s*:\s*(\d{1,3})(?:\s*-\s*(\d{1,3}))?\s*', ref)
    if not m:
        raise SystemExit('use S:N or S:N-M')
    s, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))
    ch = load_chapter(s)
    out = []
    for n in range(a, b + 1):
        v = ch['verses'].get(n)
        if v:
            out.append(f'{s}:{n}  "{v["en"]}"')
    return '\n'.join(out)


def find_job(job_id: str, jobs_dir: str) -> Job:
    surah = int(job_id.split('-')[0])
    path = os.path.join(jobs_dir, f'{surah:03d}.json')
    if not os.path.exists(path):
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, 'pack.py'), '--surahs', str(surah), '--out', jobs_dir],
                       check=True, capture_output=True, text=True)
    for j in load_jobs(jobs_dir, [surah]):
        if j.id == job_id:
            return j
    raise SystemExit(f'no job {job_id} in {path}')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('job', nargs='?', help='job id, e.g. 002-001-001 or 002-intro')
    ap.add_argument('--part', type=int, default=1)
    ap.add_argument('--chunk', type=int, default=CHUNK)
    ap.add_argument('--write', action='store_true', help='write the whole digest to work/digest/<job>.md')
    ap.add_argument('--quote', help='print the app translation of a verse or range, e.g. 6:101 or 19:88-95')
    ap.add_argument('--jobs-dir', default=os.path.join(WORK, 'jobs'))
    args = ap.parse_args()
    if args.quote:
        print(quote(args.quote))
        return 0
    if not args.job:
        ap.error('a job id or --quote is required')
    job = find_job(args.job, args.jobs_dir)
    text = build_digest(job)
    if args.write:
        out_dir = ensure_dir(os.path.join(WORK, 'digest'))
        path = os.path.join(out_dir, f'{job.id}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'wrote {os.path.relpath(path)} ({len(text)} chars, {word_count(text)} words)')
        return 0
    parts = split_parts(text, args.chunk)
    k = max(1, min(args.part, len(parts)))
    print(f'--- digest of {job.id}: part {k}/{len(parts)} ({len(parts[k - 1])} chars) ---')
    print(parts[k - 1])
    if k < len(parts):
        print(f'\n--- {len(parts) - k} more part(s): digest.py {job.id} --part {k + 1} ---')
    return 0


if __name__ == '__main__':
    sys.exit(main())
