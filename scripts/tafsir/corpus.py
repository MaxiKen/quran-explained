#!/usr/bin/env python3
"""Shared helpers for the verse-by-verse tafsir pipeline.

Everything that the generator's helpers and the auditor must agree on lives
here:

  * where the canonical translation is (``data/chapter_NNN.js``),
  * how a tafsir source file is read (``tafsir_*/NNN.txt`` and the
    Study-Quran-style ``tafsir_initial/NNN.md``),
  * how the generated chapter markdown (``tafsir/NNN.md``) is shaped.

No third-party packages. Python 3.8+.

Run any script in this folder with ``python3 scripts/tafsir/<name>.py`` from
the repository root (the paths are resolved from ``__file__``, so the cwd does
not matter).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "data"
TAFSIR_OUT = REPO / "tafsir"
TMP_DIR = REPO / "tmp"

NBSP = "\u00a0"          # some stored translations use a non-breaking space
INITIAL_SLUG = "tafsir_initial"

# --------------------------------------------------------------------- basics


def chapter_numbers():
    return range(1, 115)


def pad3(n: int) -> str:
    return "%03d" % int(n)


def digits(n: int) -> str:
    """Chapter number in the form the corpus uses: no leading zeros."""
    return str(int(n))


def chapter_path(n: int) -> Path:
    return DATA_DIR / ("chapter_%s.js" % pad3(n))


def output_path(n: int) -> Path:
    return TAFSIR_OUT / ("%s.md" % pad3(n))


def _norm_space(text: str) -> str:
    """Collapse whitespace the way the app and the auditor compare quotes."""
    return re.sub(r"\s+", " ", (text or "").replace(NBSP, " ")).strip()


# ------------------------------------------------------------- chapter metadata

_META = None


def meta():
    """``{num: {...}}`` parsed from ``js/chapters-meta.js`` (names, counts)."""
    global _META
    if _META is None:
        text = (REPO / "js" / "chapters-meta.js").read_text(encoding="utf-8")
        out = {}
        for blob in re.finditer(r"\{[^{}]*\}", text):
            b = blob.group(0)
            num = re.search(r"number:\s*(\d+)", b)
            if not num:
                continue

            def field(key, blob=b):
                m = re.search(key + r':\s*"((?:[^"\\]|\\.)*)"', blob)
                return m.group(1) if m else ""

            verses = re.search(r"verses:\s*(\d+)", b)
            out[int(num.group(1))] = {
                "number": int(num.group(1)),
                "name_ar": field("name_ar"),
                "name_en": field("name_en"),
                "meaning": field("meaning"),
                "verses": int(verses.group(1)) if verses else 0,
                "type": field("type"),
            }
        _META = out
    return _META


def chapter_name(n: int) -> str:
    return meta().get(int(n), {}).get("name_en", "Surah %d" % n)


def title_line(n: int) -> str:
    """The one legal H1 for a chapter file."""
    return "# S\u016brah %s (Chapter %d) \u2014 Verse-by-Verse Tafsir" % (chapter_name(n), n)


# ------------------------------------------------------- canonical translation

_VERSES = {}


def verses(n: int):
    """``[{ayah_no_surah, ayah_ar, ayah_en, audio}]`` in verse order.

    ``data/chapter_NNN.js`` is a JavaScript array of themes; each theme holds
    verses. The array itself is valid JSON once the ``var ... =`` wrapper is
    stripped, so it is parsed with ``json.loads`` rather than regex.
    """
    n = int(n)
    if n not in _VERSES:
        text = chapter_path(n).read_text(encoding="utf-8")
        blob = text[text.index("["): text.rindex("]") + 1]
        out = []
        for theme in json.loads(blob):
            for v in theme.get("verses", []):
                out.append({
                    "ayah_no_surah": int(v["ayah_no_surah"]),
                    "ayah_ar": v.get("ayah_ar", ""),
                    "ayah_en": v.get("ayah_en", ""),
                    "audio": v.get("audio", ""),
                })
        out.sort(key=lambda v: v["ayah_no_surah"])
        _VERSES[n] = out
    return _VERSES[n]


def verse_count(n: int) -> int:
    return len(verses(n))


def ayah_map(n: int):
    return {v["ayah_no_surah"]: v["ayah_en"] for v in verses(n)}


def ayah_en(n: int, v: int) -> str:
    return ayah_map(n).get(int(v), "")


# ------------------------------------------------------------- tafsir sources

_SOURCES = None


def source_catalog():
    """Every tafsir source folder, described from the source itself.

    Two shapes exist:

    * ``tafsir-*/NNN.txt`` — spa5k/tafsir_api exports, one ``## C:V`` section
      per ayah, Arabic or English (declared in the file header).
    * ``tafsir_initial/NNN.md`` — the Study-Quran-style draft, verses marked
      by ``**V**`` paragraphs separated by ``***``.

    English sources are listed first: they are the ones a person can read
    straight, and the prompt's source ladder leans on them.
    """
    global _SOURCES
    if _SOURCES is None:
        out = []
        for d in sorted(REPO.glob("tafsir-*")) + sorted(REPO.glob("tafsir_*")):
            if not d.is_dir():
                continue
            slug = d.name
            if slug == INITIAL_SLUG:
                out.append({
                    "slug": slug, "kind": "study", "lang": "en",
                    "title": "THE STUDY QURAN (initial draft; source initial/ -> tafsir_initial/)",
                    "upstream": "in-repo draft", "path": d,
                })
                continue
            head_file = d / "001.txt"
            if not head_file.exists():
                continue
            head = head_file.read_text(encoding="utf-8", errors="replace").split("\n")[:4]
            title = head[0].strip().split(" \u2014 ")[0]
            upstream = ""
            for line in head:
                if line.startswith("Source:"):
                    upstream = line.split("\u00b7", 1)[-1].strip()
            out.append({
                "slug": slug,
                "kind": "txt",
                "lang": "ar" if "(Arabic)" in head[0] else "en",
                "title": title,
                "upstream": upstream,
                "path": d,
            })
        out.sort(key=lambda s: (s["lang"] != "en", s["slug"]))
        _SOURCES = out
    return _SOURCES


def source_slugs():
    return [s["slug"] for s in source_catalog()]


def source_by_slug(slug: str):
    for s in source_catalog():
        if s["slug"] == slug:
            return s
    return None


_SOURCE_TEXT = {}


def _source_file_text(path: Path):
    key = str(path)
    if key not in _SOURCE_TEXT:
        _SOURCE_TEXT[key] = path.read_text(encoding="utf-8", errors="replace")
    return _SOURCE_TEXT[key]


def source_verse(slug: str, n: int, v: int):
    """The source's discussion of ayah ``n:v``, or ``''`` when it has none."""
    src = source_by_slug(slug)
    if src is None:
        return ""
    n, v = int(n), int(v)

    if src["kind"] == "study":
        p = src["path"] / ("%s.md" % pad3(n))
        if not p.exists():
            return ""
        text = _source_file_text(p)
        m = re.search(r"(?m)^\*\*%d\*\*[ \t]+" % v, text)
        if not m:
            return ""
        rest = text[m.start():]
        end = re.search(r"(?m)^\*\*\*[ \t]*$", rest[10:])
        return (rest[: end.start() + 10] if end else rest).strip()

    p = src["path"] / ("%s.txt" % pad3(n))
    if not p.exists():
        return ""
    text = _source_file_text(p)
    m = re.search(r"(?m)^## %d:%d[ \t]*$" % (n, v), text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"(?m)^## \d+:\d+[ \t]*$", rest)
    return (rest[: nxt.start()] if nxt else rest).strip()


# ------------------------------------------------------ generated chapter file

VERSE_HEADING_RE = re.compile(r"^## Verse (\d+):(\d+)[ \t]*$")
HEADING_RE = re.compile(r"^\*\*(.+?)\*\*[ \t]*$")
H1_RE = re.compile(r"^# .+$")
INTRO_HEADING = "## Introduction to the S\u016brah"


class Section:
    """One ``## Verse C:V`` block of a generated chapter file."""

    def __init__(self, chapter, verse, start, end, lines):
        self.chapter = chapter
        self.verse = verse
        self.start = start          # 1-based line number of the heading
        self.end = end              # 1-based line number of the last line
        self.lines = lines          # lines[start-1 : end]

    @property
    def ref(self):
        return "%d:%d" % (self.chapter, self.verse)

    def text(self):
        return "\n".join(self.lines)

    def quote(self):
        """The single ``> ...`` verse line, joined if wrapped ('' if absent)."""
        parts = []
        for line in self.lines[1:]:
            if line.startswith(">"):
                parts.append(line[1:].lstrip(" "))
            elif line.strip() == "":
                if parts:
                    break
                continue
            else:
                break
        return " ".join(parts).strip()

    def quote_lines(self):
        """How many ``>`` lines the verse quote occupies (should be 1)."""
        return len([l for l in self.lines[1:] if l.startswith(">")])

    def body(self):
        """Section text without the heading, the verse quote and the ``---``."""
        lines = self.lines[1:]
        i = 0
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        while i < len(lines) and lines[i].startswith(">"):
            i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        out = lines[i:]
        while out and out[-1].strip() in ("", "---"):
            out.pop()
        while out and out[-1].strip() == "":
            out.pop()
        return "\n".join(out)

    def headings(self):
        """``[(line_no, title)]`` for the bold headings inside the section."""
        found = []
        for i, line in enumerate(self.lines):
            m = HEADING_RE.match(line)
            if m:
                found.append((self.start + i, m.group(1).strip()))
        return found


class ChapterDoc:
    """A parsed ``tafsir/NNN.md``."""

    def __init__(self, chapter, path, text):
        self.chapter = chapter
        self.path = path
        self.text = text
        self.lines = text.split("\n")
        self.title = self.lines[0] if self.lines else ""
        self.intro_heading_line = None
        self.intro_start = None
        self.intro_end = None
        self.intro = ""
        self.sections = []
        self.problems = []          # structural notes the auditor reports
        self._parse()

    def _parse(self):
        lines = self.lines
        verse_starts = [i for i, l in enumerate(lines) if VERSE_HEADING_RE.match(l)]

        for i, l in enumerate(lines):
            if l.startswith(INTRO_HEADING):
                self.intro_heading_line = i + 1
                break
        if self.intro_heading_line is not None:
            start = self.intro_heading_line          # 0-based index of heading + 1
            end = verse_starts[0] if verse_starts else len(lines)
            self.intro_start = start + 1
            self.intro_end = end
            body = lines[start:end]
            # drop trailing separator / blank lines
            while body and body[-1].strip() in ("", "---"):
                body.pop()
            self.intro = "\n".join(body).strip()

        for idx, start in enumerate(verse_starts):
            end = verse_starts[idx + 1] if idx + 1 < len(verse_starts) else len(lines)
            m = VERSE_HEADING_RE.match(lines[start])
            section = Section(int(m.group(1)), int(m.group(2)), start + 1, end, lines[start:end])
            self.sections.append(section)

    def section_map(self):
        return {s.verse: s for s in self.sections}

    def words(self, text=None):
        text = self.text if text is None else text
        return len(re.findall(r"[A-Za-z0-9\u2019'\-]+", text))


def load_chapter_doc(n: int, path: Path = None):
    path = Path(path) if path else output_path(n)
    if not path.exists():
        return None
    return ChapterDoc(int(n), path, path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------- markdown

def split_paragraphs(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def sentence_split(text: str):
    """Sentences, good enough for duplicate and filler detection."""
    clean = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?\u061f])\s+(?=[A-Z\u201c\u2018\"'])", clean)
    return [p.strip() for p in parts if p.strip()]


def norm_key(text: str) -> str:
    """Normalised comparison key: lowercase, punctuation and quotes dropped."""
    text = text.lower().replace(NBSP, " ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def shingles(text: str, size: int = 8):
    words = norm_key(text).split()
    return {" ".join(words[i:i + size]) for i in range(max(0, len(words) - size + 1))}
