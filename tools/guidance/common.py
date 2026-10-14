"""Shared helpers: paths, corpus loading, text cleaning, range parsing,
clustering of verses into generation jobs, and name folding for the gates."""
from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Iterable


def read_text(path: str) -> str:
    with open(path, encoding='utf-8') as f:
        return f.read()


def read_json(path: str):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, 'data')
WORK = os.path.join(ROOT, 'work')
PROMPTS = os.path.join(HERE, 'prompts')

SOURCE_ORDER = ['ibn-kathir', 'maarif', 'tazkirul', 'tanwir', 'jalalayn',
                'mukhtasar', 'qushayri', 'wahidi']

# Generation job limits. A job is a run of consecutive verses whose source
# blocks overlap; it is split when it grows past either limit so that one
# request never has to write more than a model can return in one go.
MAX_JOB_VERSES = 8
MAX_JOB_CHARS = 60_000
MIN_JOB_VERSES = 1

ARABIC_RE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
SAW = '\ufdfa'  # ﷺ — the one Arabic-block glyph the output may contain


# --------------------------------------------------------------------------
# chapters
# --------------------------------------------------------------------------
_CHAPTER_META = None


def chapter_meta() -> dict[int, dict]:
    """number -> {name_en, name_ar, meaning, verses, type} from js/chapters-meta.js."""
    global _CHAPTER_META
    if _CHAPTER_META is not None:
        return _CHAPTER_META
    src = read_text(os.path.join(ROOT, 'js', 'chapters-meta.js'))
    out = {}
    for m in re.finditer(r'\{\s*number:\s*(\d+),\s*name_ar:\s*"([^"]*)",\s*name_en:\s*"([^"]*)",\s*meaning:\s*"([^"]*)",\s*verses:\s*(\d+),\s*type:\s*"([^"]*)"', src):
        out[int(m.group(1))] = {
            'number': int(m.group(1)), 'name_ar': m.group(2), 'name_en': m.group(3),
            'meaning': m.group(4), 'verses': int(m.group(5)), 'type': m.group(6),
        }
    if len(out) != 114:
        raise RuntimeError(f'chapters-meta.js parsed {len(out)} chapters, expected 114')
    _CHAPTER_META = out
    return out


def load_chapter(surah: int) -> dict:
    """data/chapter_NNN.js -> {'themes': [...], 'verses': {n: {ar, en, theme}}}."""
    path = os.path.join(DATA, f'chapter_{surah:03d}.js')
    txt = read_text(path)
    body = txt[txt.index('=') + 1:].strip().rstrip(';')
    themes = json.loads(body)
    verses = {}
    for t in themes:
        for v in t['verses']:
            verses[int(v['ayah_no_surah'])] = {
                'ar': v.get('ayah_ar', ''), 'en': v.get('ayah_en', ''),
                'theme_no': t.get('theme_no'), 'theme': t.get('theme_description', ''),
            }
    return {'themes': [{'no': t.get('theme_no'), 'description': t.get('theme_description', ''),
                        'verses': [int(v['ayah_no_surah']) for v in t['verses']]} for t in themes],
            'verses': verses}


def load_tafsir(surah: int) -> dict:
    return read_json(os.path.join(DATA, f'tafsir_{surah:03d}.json'))


def load_guidance(surah: int, data_dir: str | None = None) -> dict | None:
    path = os.path.join(data_dir or DATA, f'guidance_{surah:03d}.json')
    if not os.path.exists(path):
        return None
    try:
        return read_json(path)
    except json.JSONDecodeError:
        return None


# --------------------------------------------------------------------------
# ranges
# --------------------------------------------------------------------------
def parse_range(label: str) -> list[tuple[int, int]]:
    """'2:3' -> [(3,3)]; '2:2-5' -> [(2,5)]; '2:11-2:12' -> [(11,12)];
    '55:18,23,47' -> [(18,18),(23,23),(47,47)]; '8:12,63-65' -> [(12,12),(63,65)]."""
    _, rest = label.split(':', 1)
    spans = []
    for part in rest.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            a = int(a.split(':')[-1])
            b = int(b.split(':')[-1])
            if b < a:
                a, b = b, a
            spans.append((a, b))
        else:
            v = int(part.split(':')[-1])
            spans.append((v, v))
    return spans


def range_verses(label: str) -> list[int]:
    out = []
    for a, b in parse_range(label):
        out.extend(range(a, b + 1))
    return out


def fmt_range(surah: int, verses: list[int]) -> str:
    verses = sorted(set(verses))
    if not verses:
        return f'{surah}:?'
    if len(verses) == 1:
        return f'{surah}:{verses[0]}'
    # contiguous?
    if verses[-1] - verses[0] + 1 == len(verses):
        return f'{surah}:{verses[0]}-{verses[-1]}'
    return f'{surah}:' + ','.join(str(v) for v in verses)


# --------------------------------------------------------------------------
# text cleaning
# --------------------------------------------------------------------------
def clean_block(text: str) -> str:
    """Normalise a source block for the model: lost punctuation, broken ﷺ
    lines, runaway whitespace. Never rewrites a word."""
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    t = t.replace('\ufffd', "'")
    t = t.replace('\u00a0', ' ')
    # the ﷺ sign was split onto its own line in the upstream Ibn Kathīr file
    t = re.sub(r'\n[ \t]*' + SAW + r'[ \t]*\n', ' ' + SAW + '\n', t)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    return t.strip()


def strip_arabic_lines(text: str) -> str:
    """Drop lines that are mostly Arabic script (the quoted āyah/hadith text
    that Ibn Kathīr always follows with an English rendering)."""
    out = []
    for line in text.split('\n'):
        s = line.strip()
        if s and len(ARABIC_RE.findall(s)) > 0.5 * len(s):
            continue
        out.append(line)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()


def approx_tokens(text: str) -> int:
    ar = len(ARABIC_RE.findall(text))
    return int((len(text) - ar) / 4 + ar / 1.6)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z\u00C0-\u024F\u1E00-\u1EFF'ʿʾ’-]+", text))


# --------------------------------------------------------------------------
# folding (used by the gates to match names across spellings)
# --------------------------------------------------------------------------
_PREFIX_RE = re.compile(r"\b(?:al|at|ath|ad|adh|ar|az|as|ash|an|el)-", re.I)
_TRANSLIT_MAP = str.maketrans({
    'ʿ': '', 'ʾ': '', "'": '', '`': '', '‘': '', '’': '', 'ʼ': '', '´': '',
    'ḥ': 'h', 'ṣ': 's', 'ḍ': 'd', 'ṭ': 't', 'ẓ': 'z', 'ā': 'a', 'ī': 'i', 'ū': 'u',
    'Ḥ': 'h', 'Ṣ': 's', 'Ḍ': 'd', 'Ṭ': 't', 'Ẓ': 'z', 'Ā': 'a', 'Ī': 'i', 'Ū': 'u',
    'ġ': 'g', 'ğ': 'g', 'ḏ': 'dh', 'ṯ': 'th', 'š': 'sh',
})


def fold(text: str) -> str:
    """Lower-case, strip diacritics and hamza/ʿayn marks, drop the Arabic
    article, unify 'bin/ibn/b.' and common spelling variants, collapse
    whitespace. Used for matching, never for output."""
    t = text.translate(_TRANSLIT_MAP)
    t = unicodedata.normalize('NFKD', t)
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    t = _PREFIX_RE.sub('', t)
    t = re.sub(r'\b(?:bin|b\.|ibn|son of)\s+', 'ibn ', t)
    t = re.sub(r'\bmecca\b', 'makkah', t)
    t = re.sub(r'\bmedina\b', 'madinah', t)
    t = re.sub(r'\bmakka\b', 'makkah', t)
    t = re.sub(r'\bmadina\b', 'madinah', t)
    t = re.sub(r'\bquran\b', 'quran', t)
    t = re.sub(r'\bkoran\b', 'quran', t)
    t = re.sub(r'\bqur-?an\b', 'quran', t)
    t = re.sub(r'\bhadeeth\b', 'hadith', t)
    t = re.sub(r'\bsalat\b|\bsalaah\b|\bsalaat\b', 'salah', t)
    t = re.sub(r'\bzakat\b|\bzakaat\b', 'zakah', t)
    t = re.sub(r'\bmuhammed\b|\bmohammad\b|\bmohammed\b', 'muhammad', t)
    t = re.sub(r'[^a-z0-9:\s-]', ' ', t)
    # 'abd allah' / 'abdullah' / 'abd al-rahman' / 'abdur-rahman' -> one token
    t = re.sub(r'\babd[ -]?[aue]?l?lah\b', 'abdullah', t)
    t = re.sub(r'\babd(?!ullah\b)(?:[aue](?:sh|l|r|s|n|t|d|z)?[ -]?|[ -])(?=\w)', 'abd', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


# --------------------------------------------------------------------------
# jobs
# --------------------------------------------------------------------------
@dataclass
class Block:
    source: str          # payload source id (ibn-kathir, …)
    label: str           # neutral label shown to the model (Text 1 …)
    range: str           # the range label from the payload
    verses: list[int]    # verses of this surah the block covers
    text: str
    shared_outside: list[int] = field(default_factory=list)  # covered verses not in this job


@dataclass
class Job:
    id: str
    kind: str            # 'verses' | 'intro'
    surah: int
    verses: list[int]
    blocks: list[Block]
    ayahs: list[dict]    # [{n, ar, en, theme}]
    context_before: list[dict]
    context_after: list[dict]
    meta: dict
    themes: list[dict] = field(default_factory=list)
    chars: int = 0
    est_tokens: int = 0

    def to_json(self) -> dict:
        d = asdict(self)
        return d

    @staticmethod
    def from_json(d: dict) -> 'Job':
        blocks = [Block(**b) for b in d.pop('blocks')]
        return Job(blocks=blocks, **d)


def _surah_clusters(tafsir: dict, n_verses: int) -> list[list[int]]:
    """Consecutive verses joined wherever any source block spans both."""
    parent = list(range(n_verses + 2))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for sid, s in tafsir['sets'].items():
        for label in s['ranges']:
            for a, b in parse_range(label):
                for v in range(max(1, a), min(n_verses, b)):
                    union(v, v + 1)
    groups: dict[int, list[int]] = {}
    for v in range(1, n_verses + 1):
        groups.setdefault(find(v), []).append(v)
    return [sorted(g) for g in sorted(groups.values(), key=lambda g: g[0])]


def _verse_blocks(tafsir: dict, verse: int) -> list[tuple[str, int]]:
    m = tafsir['verses'].get(str(verse), {})
    return [(sid, idx) for sid, idx in m.items() if isinstance(idx, int)]


def _block_chars(tafsir: dict, keys: Iterable[tuple[str, int]]) -> int:
    return sum(len(tafsir['sets'][sid]['blocks'][idx]) for sid, idx in keys)


def _split_cluster(tafsir: dict, verses: list[int], max_verses: int, max_chars: int) -> list[list[int]]:
    """Greedy split of an oversized cluster. The cut is placed where the
    fewest source characters straddle it, inside the window that keeps the
    piece under the limits."""
    pieces = []
    start = 0
    while start < len(verses):
        # grow
        end = start
        seen: set[tuple[str, int]] = set()
        while end < len(verses):
            keys = set(_verse_blocks(tafsir, verses[end]))
            new = keys - seen
            chars = _block_chars(tafsir, seen | new)
            if end - start + 1 > max_verses or (chars > max_chars and end > start):
                break
            seen |= new
            end += 1
        if end >= len(verses):
            pieces.append(verses[start:])
            break
        # choose the cut inside [start+1, end] that minimises straddling chars
        best_cut, best_w = end, None
        lo = max(start + MIN_JOB_VERSES, end - 3)
        for cut in range(end, lo - 1, -1):
            if cut <= start:
                break
            left = set()
            for v in verses[start:cut]:
                left |= set(_verse_blocks(tafsir, v))
            right = set()
            for v in verses[cut:]:
                right |= set(_verse_blocks(tafsir, v))
            w = _block_chars(tafsir, left & right)
            if best_w is None or w < best_w:
                best_w, best_cut = w, cut
            if w == 0:
                break
        pieces.append(verses[start:best_cut])
        start = best_cut
    return pieces


def build_jobs(surah: int, *, max_verses: int = MAX_JOB_VERSES, max_chars: int = MAX_JOB_CHARS,
               strip_arabic: bool = False, with_intro: bool = True) -> list[Job]:
    tafsir = load_tafsir(surah)
    chapter = load_chapter(surah)
    meta = chapter_meta()[surah]
    n = meta['verses']
    if len(chapter['verses']) != n:
        raise RuntimeError(f'surah {surah}: chapter file has {len(chapter["verses"])} verses, meta says {n}')
    labels = {sid: f'Text {i + 1}' for i, sid in enumerate(SOURCE_ORDER)}

    def ayah(v):
        cv = chapter['verses'][v]
        return {'n': v, 'ar': cv['ar'], 'en': cv['en'], 'theme': cv['theme']}

    jobs: list[Job] = []
    clusters = _surah_clusters(tafsir, n)
    for cluster in clusters:
        for piece in _split_cluster(tafsir, cluster, max_verses, max_chars):
            keys: dict[tuple[str, int], None] = {}
            for v in piece:
                for k in _verse_blocks(tafsir, v):
                    keys.setdefault(k)
            blocks = []
            for sid in SOURCE_ORDER:
                for (s, idx) in keys:
                    if s != sid:
                        continue
                    st = tafsir['sets'][sid]
                    label = st['ranges'][idx]
                    covered = [x for x in range_verses(label) if 1 <= x <= n]
                    text = clean_block(st['blocks'][idx])
                    if strip_arabic:
                        text = strip_arabic_lines(text)
                    blocks.append(Block(source=sid, label=labels[sid], range=label, verses=covered,
                                        text=text, shared_outside=[x for x in covered if x not in piece]))
            before = [ayah(v) for v in range(max(1, piece[0] - 2), piece[0])]
            after = [ayah(v) for v in range(piece[-1] + 1, min(n, piece[-1] + 2) + 1)]
            job = Job(id=f'{surah:03d}-{piece[0]:03d}-{piece[-1]:03d}', kind='verses', surah=surah,
                      verses=list(piece), blocks=blocks, ayahs=[ayah(v) for v in piece],
                      context_before=before, context_after=after, meta=meta)
            job.chars = sum(len(b.text) for b in blocks)
            job.est_tokens = sum(approx_tokens(b.text) for b in blocks) + 600
            jobs.append(job)

    if with_intro:
        # The surah introduction is written from the blocks that open the
        # chapter (they carry the names, virtues, period and outline), plus
        # the theme outline the app already has.
        blocks = []
        for sid in ['ibn-kathir', 'maarif', 'tazkirul']:
            st = tafsir['sets'].get(sid)
            if not st or not st['blocks']:
                continue
            idx = tafsir['verses'].get('1', {}).get(sid)
            if not isinstance(idx, int):
                continue
            text = clean_block(st['blocks'][idx])
            if strip_arabic:
                text = strip_arabic_lines(text)
            label = st['ranges'][idx]
            blocks.append(Block(source=sid, label=labels[sid], range=label,
                                verses=[x for x in range_verses(label) if 1 <= x <= n], text=text))
        job = Job(id=f'{surah:03d}-intro', kind='intro', surah=surah, verses=[], blocks=blocks,
                  ayahs=[ayah(1)], context_before=[], context_after=[], meta=meta,
                  themes=chapter['themes'])
        job.chars = sum(len(b.text) for b in blocks)
        job.est_tokens = sum(approx_tokens(b.text) for b in blocks) + 800
        jobs.append(job)
    return jobs


def parse_surah_selection(spec: str) -> list[int]:
    """'1-114' | '1,112-114' | 'all' -> sorted list of surah numbers."""
    if not spec or spec.strip().lower() == 'all':
        return list(range(1, 115))
    out = set()
    for part in spec.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    bad = [s for s in out if not 1 <= s <= 114]
    if bad:
        raise ValueError(f'surah numbers out of range: {bad}')
    return sorted(out)


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def read_prompt(name: str) -> str:
    return read_text(os.path.join(PROMPTS, name))
