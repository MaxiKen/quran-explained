#!/usr/bin/env python3
"""Corpus access for the tafsir pipeline.

One place that knows where everything is:

* ``data/chapter_NNN.js`` — the app's verse text (Arabic, English, audio). It is
  the **only** source of Qur'an wording: verse quotes and cross-references are
  copied from here, never retyped from a tafsir.
* ``js/chapters-meta.js`` — chapter names, meanings, verse counts, Makkan/Medinan.
* ``tafsir-<work>/NNN.txt`` — the ten classical works. Each file is a flat text
  dump with one section per verse under a ``## N:V`` marker. Some works repeat
  the whole-surah passage under every verse; :func:`source_sections` returns the
  raw sections and :func:`distinct_paragraphs` drops the repeats.
* ``tafsir_initial/NNN.md`` — the study-style draft (partial coverage).
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# The ten classical works. key -> (folder, language, display name)
SOURCES: dict[str, tuple[str, str, str]] = {
    "tabari": ("tafsir-al-tabari", "ar", "al-Ṭabarī, Jāmiʿ al-Bayān"),
    "qurtubi": ("tafsir-al-qurtubi", "ar", "al-Qurṭubī, al-Jāmiʿ li-Aḥkām al-Qurʾān"),
    "kathir": ("tafsir-ibn-kathir", "ar", "Ibn Kathīr, Tafsīr al-Qurʾān al-ʿAẓīm"),
    "saadi": ("tafsir-as-saadi", "ar", "al-Saʿdī, Taysīr al-Karīm al-Raḥmān"),
    "uthaymeen": ("tafsir-ibn-uthaymeen", "ar", "Ibn ʿUthaymīn, Tafsīr al-Qurʾān al-Karīm"),
    "baghawi": ("tafsir-al-baghawi", "ar", "al-Baghawī, Maʿālim al-Tanzīl"),
    "alusi": ("tafsir-al-alusi", "ar", "al-Ālūsī, Rūḥ al-Maʿānī"),
    "jalalayn": ("tafsir-al-jalalayn", "en", "al-Jalālayn (English)"),
    "abbas": ("tafsir-ibn-abbas", "en", "Ibn ʿAbbās, Tanwīr al-Miqbās (English)"),
    "maarif": ("tafsir-maarif-ul-quran", "en", "Maʿārif al-Qurʾān (English)"),
}

#: The study-style draft: read for coverage, never quoted or relayed.
INITIAL = ("tafsir_initial", "en", "study draft")

#: Sources quoted in a chapter's evidence pack, in the order they are shown.
ORDER = ["tabari", "qurtubi", "kathir", "baghawi", "alusi", "saadi", "uthaymeen", "maarif", "jalalayn", "abbas", "initial"]


def pad3(n: int) -> str:
    return f"{int(n):03d}"


# ---------------------------------------------------------------- app data ---

_CHAPTERS: list[dict] | None = None
_VERSES: dict[int, list[dict]] = {}


def chapters() -> list[dict]:
    """The app's chapter metadata, parsed out of js/chapters-meta.js."""
    global _CHAPTERS
    if _CHAPTERS is None:
        text = (ROOT / "js/chapters-meta.js").read_text(encoding="utf-8")
        rows = []
        for m in re.finditer(
            r'\{\s*number:\s*(\d+),\s*name_ar:\s*"([^"]*)",\s*name_en:\s*"([^"]*)",'
            r'\s*meaning:\s*"([^"]*)",\s*verses:\s*(\d+),\s*type:\s*"([^"]*)"\s*\}',
            text,
        ):
            rows.append(
                {
                    "number": int(m.group(1)),
                    "name_ar": m.group(2),
                    "name_en": m.group(3),
                    "meaning": m.group(4),
                    "verses": int(m.group(5)),
                    "type": m.group(6),
                }
            )
        _CHAPTERS = rows
    return _CHAPTERS


def meta(n: int) -> dict:
    for ch in chapters():
        if ch["number"] == int(n):
            return ch
    raise KeyError(f"chapter {n} is not in js/chapters-meta.js")


def verses(n: int) -> list[dict]:
    """Every verse of a chapter: ``[{ayah_no_surah, ayah_ar, ayah_en}, ...]``."""
    n = int(n)
    if n not in _VERSES:
        path = ROOT / "data" / f"chapter_{pad3(n)}.js"
        text = path.read_text(encoding="utf-8")
        body = text[text.index("[") : text.rindex("]") + 1]
        themes = json.loads(body)
        rows = [v for theme in themes for v in theme.get("verses", [])]
        rows.sort(key=lambda v: v["ayah_no_surah"])
        _VERSES[n] = rows
    return _VERSES[n]


def verse_count(n: int) -> int:
    return len(verses(n))


def ayah_en(n: int, v: int) -> str:
    for row in verses(n):
        if row["ayah_no_surah"] == int(v):
            return row["ayah_en"]
    raise KeyError(f"{n}:{v}")


def ayah_ar(n: int, v: int) -> str:
    for row in verses(n):
        if row["ayah_no_surah"] == int(v):
            return row["ayah_ar"]
    raise KeyError(f"{n}:{v}")


# --------------------------------------------------------------- the works ---

_HEADER = re.compile(r"^=+\s*$")
_FOOTNOTE = re.compile(r"\[\[.*?\]\]", re.S)
_SECTION = re.compile(r"^##\s+(\d+):(\d+)\s*$", re.M)


def _strip_noise(text: str) -> str:
    """Drop dump headers, footnotes and page furniture from a corpus file."""
    text = _FOOTNOTE.sub("", text)
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"\[\[.*?\]\]", "", text, flags=re.S)
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if _HEADER.match(s):
            continue
        if s.startswith(("TAFSIR ", "Source:", "Verses:")):
            continue
        if re.fullmatch(r"[\*_\-—=·•]{3,}", s):
            continue
        if re.fullmatch(r"\d+", s):  # stray page numbers
            continue
        lines.append(line.rstrip())
    text = "\n".join(lines)
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def source_sections(n: int, key: str) -> dict[int, str]:
    """``{verse: text}`` for one work, cleaned. Missing verses are absent."""
    folder = dict((k, v[0]) for k, v in SOURCES.items()).get(key)
    if folder is None:
        if key == "initial":
            return _initial_sections(n)
        raise KeyError(key)
    path = ROOT / folder / f"{pad3(n)}.txt"
    if not path.exists():
        return {}
    text = _strip_noise(path.read_text(encoding="utf-8"))
    parts = _SECTION.split(text)
    out: dict[int, str] = {}
    for i in range(1, len(parts), 3):
        chapter, verse = int(parts[i]), int(parts[i + 1])
        if chapter != int(n):
            continue
        body = parts[i + 2].strip()
        if body:
            out[verse] = body
    return out


def _initial_sections(n: int) -> dict[int, str]:
    """The study draft's ``**V**`` blocks, one per verse."""
    path = ROOT / "tafsir_initial" / f"{pad3(n)}.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    marker = "\n## Text and Commentary"
    if marker in text:
        text = text.split(marker, 1)[1]
    blocks = re.split(r"^>\s*\*\*(\d+)\*\*.*$", text, flags=re.M)
    out: dict[int, str] = {}
    for i in range(1, len(blocks), 2):
        verse = int(blocks[i])
        body = re.sub(r"^\*\*\d+\*\*\s*", "", blocks[i + 1].strip())
        body = body.split("***")[0].strip()
        if body:
            out[verse] = body
    return out


def initial_intro(n: int) -> str:
    """The introductory essay of ``tafsir_initial/NNN.md`` (research reading only)."""
    path = ROOT / "tafsir_initial" / f"{pad3(n)}.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## Introduction\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end() :]
    end = re.search(r"^##\s", rest, re.M)
    return (rest[: end.start()] if end else rest).strip()


def paragraphs(text: str) -> list[str]:
    """Paragraphs, one per blank-line-separated block (markers kept in place)."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text.strip()) if w]


def normalise(text: str) -> str:
    """Whitespace/quote-insensitive form used for comparing quoted wording."""
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u02bf", "").replace("\u02be", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def source_intro(n: int, key: str) -> str:
    """Whatever a work says about the sūrah as a whole (before its first verse)."""
    folder = dict((k, v[0]) for k, v in SOURCES.items()).get(key)
    if folder is None:
        return ""
    path = ROOT / folder / f"{pad3(n)}.txt"
    if not path.exists():
        return ""
    text = _strip_noise(path.read_text(encoding="utf-8"))
    m = _SECTION.search(text)
    return text[: m.start()].strip() if m else text.strip()


def all_source_ints(n: int) -> str:
    return initial_intro(n)


# ------------------------------------------------------------ cross-refs ------

def clause(n: int, v: int, words_wanted: int = 12) -> str:
    """A readable clause of a verse, for a cross-reference."""
    text = normalise(ayah_en(n, v))
    parts = re.split(r"(?<=[,;:.!?])\s+", text)
    out = ""
    for part in parts:
        if out and len(words(out + " " + part)) > words_wanted:
            break
        out = (out + " " + part).strip()
    return out or text
