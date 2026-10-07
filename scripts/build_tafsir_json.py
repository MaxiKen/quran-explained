#!/usr/bin/env python3
"""Compile verse-aligned Tafsir Markdown into the app's JSON payload."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_DIR = ROOT / "data" / "tafsir_markdown"
DATA_DIR = ROOT / "data"
MIN_COMMENTARY_WORDS = 400
MAX_COMMENTARY_WORDS = 1200
WORD_TOKEN = re.compile(r"\b[^\W_]+(?:[’'‑-][^\W_]+)*\b", re.UNICODE)
SECTION_HEADING = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
VERSE_HEADING = re.compile(r"(\d+):(\d+)")
RICH_MARKDOWN = re.compile(
    r"\*\*.+?\*\*|\*[^*\n]+?\*|`[^`]+`|^#{2,6}[ \t]+.+|^[ \t]*[-*+][ \t]+",
    re.MULTILINE,
)
SOURCE_REFERENCE = re.compile(
    r"\[(?:Q\s+\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?|"
    r"(?:Report|Hadith|Poem):\s*[^\]\n]+)\]"
)
COMPILER_CITATION = re.compile(
    r"\[[^\]\n]*\b(?:al[-\s]?(?:Ṭ|T)abar[iī]|(?:Ṭ|T)abar[iī])\b"
    r"[^\]\n]*\]",
    re.IGNORECASE,
)
EVIDENCE_QUOTE = re.compile(r"[“\"][^“”\"\n]{20,}[”\"]")


class BuildError(Exception):
    """Raised for invalid source alignment or payload data."""


def chapter_verses(chapter_number: int) -> list[tuple[int, str]]:
    """Read the chapter's exact English translations from its JS data file."""
    chapter_path = DATA_DIR / f"chapter_{chapter_number:03}.js"
    if not chapter_path.is_file():
        raise BuildError(f"Missing chapter data: {chapter_path.relative_to(ROOT)}")

    source = chapter_path.read_text(encoding="utf-8")
    assignment = re.search(
        rf"\bvar\s+chapterData_{chapter_number}\s*=\s*", source
    )
    if not assignment:
        raise BuildError(
            f"Could not find chapterData_{chapter_number} in "
            f"{chapter_path.relative_to(ROOT)}"
        )

    try:
        data, end = json.JSONDecoder().raw_decode(source[assignment.end() :])
    except json.JSONDecodeError as exc:
        raise BuildError(f"Invalid chapter JSON in {chapter_path.name}: {exc}") from exc

    trailing = source[assignment.end() + end :].strip()
    if trailing != ";":
        raise BuildError(
            f"Expected a single JSON array assignment ending in ';' in {chapter_path.name}"
        )
    if not isinstance(data, list):
        raise BuildError(f"Expected an array in {chapter_path.name}")

    verses: list[tuple[int, str]] = []
    for theme in data:
        if not isinstance(theme, dict) or not isinstance(theme.get("verses"), list):
            raise BuildError(f"Malformed theme/verses structure in {chapter_path.name}")
        for verse in theme["verses"]:
            if not isinstance(verse, dict):
                raise BuildError(f"Malformed verse entry in {chapter_path.name}")
            number = verse.get("ayah_no_surah")
            translation = verse.get("ayah_en")
            if not isinstance(number, int) or not isinstance(translation, str):
                raise BuildError(f"Verse lacks ayah_no_surah or ayah_en in {chapter_path.name}")
            verses.append((number, translation))

    numbers = [number for number, _ in verses]
    if not verses or len(numbers) != len(set(numbers)):
        raise BuildError(f"No verses or duplicate verse numbers in {chapter_path.name}")
    return verses


def parse_markdown(markdown_path: Path, chapter_number: int) -> tuple[str | None, list[tuple[int, str]]]:
    text = markdown_path.read_text(encoding="utf-8")
    headings = list(SECTION_HEADING.finditer(text))
    if not headings:
        raise BuildError(f"No '## N:M' verse headings in {markdown_path.name}")

    intro: str | None = None
    sections: list[tuple[int, str]] = []
    seen_numbers: set[int] = set()

    for index, heading in enumerate(headings):
        label = heading.group(1).strip()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end() : end].strip()

        if label.casefold() == "introduction":
            if intro is not None or sections:
                raise BuildError("'## Introduction' may appear once, before all verses")
            if not body:
                raise BuildError("'## Introduction' cannot be empty")
            intro = body
            continue

        match = VERSE_HEADING.fullmatch(label)
        if not match:
            raise BuildError(f"Unsupported section heading: '## {label}'")
        surah_number, verse_number = map(int, match.groups())
        if surah_number != chapter_number:
            raise BuildError(
                f"Found heading {surah_number}:{verse_number} in chapter {chapter_number} source"
            )
        if verse_number in seen_numbers:
            raise BuildError(f"Duplicate verse heading {chapter_number}:{verse_number}")
        if not body:
            raise BuildError(f"Empty commentary for verse {chapter_number}:{verse_number}")
        sections.append((verse_number, body))
        seen_numbers.add(verse_number)

    return intro, sections


def build_payload(chapter_number: int, markdown_path: Path) -> str:
    expected_verses = chapter_verses(chapter_number)
    intro, sections = parse_markdown(markdown_path, chapter_number)

    expected_numbers = [number for number, _ in expected_verses]
    actual_numbers = [number for number, _ in sections]
    if actual_numbers != expected_numbers:
        raise BuildError(
            f"Verse coverage/order mismatch for chapter {chapter_number}: "
            f"expected {expected_numbers}, found {actual_numbers}"
        )

    payload: dict[str, object] = {}
    if intro is not None:
        payload["intro"] = intro
    verses_payload: dict[str, str] = {}

    for (verse_number, body), (_, translation) in zip(sections, expected_verses):
        lines = body.splitlines()
        expected_quote = f"> {translation}"
        if not lines or lines[0].strip() != expected_quote:
            found = lines[0].strip() if lines else "<empty>"
            raise BuildError(
                f"Translation mismatch at {chapter_number}:{verse_number}: "
                f"expected {expected_quote!r}, found {found!r}"
            )

        commentary = "\n".join(lines[1:]).strip()
        if not commentary:
            raise BuildError(f"Missing commentary at {chapter_number}:{verse_number}")
        if not RICH_MARKDOWN.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} has no supported "
                "Markdown formatting"
            )

        if COMPILER_CITATION.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} cites al-Tabari "
                "as the interpretive authority; cite the underlying source instead"
            )

        # Count substantive commentary only: exclude source tags and the exact app
        # translation (which is outside this string by construction).
        countable = SOURCE_REFERENCE.sub("", commentary)
        word_count = len(WORD_TOKEN.findall(countable))
        if word_count < MIN_COMMENTARY_WORDS or word_count > MAX_COMMENTARY_WORDS:
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} has {word_count} words; "
                f"required range is {MIN_COMMENTARY_WORDS}–{MAX_COMMENTARY_WORDS}"
            )
        if not SOURCE_REFERENCE.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} needs an inline "
                "Qur’an, report/hadith, or poem source reference"
            )
        if not EVIDENCE_QUOTE.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} needs a quoted "
                "or closely translated source-evidence excerpt"
            )
        verses_payload[str(verse_number)] = body

    payload["verses"] = verses_payload
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chapter",
        type=int,
        help="Build/check only this surah (1-114); otherwise process all Markdown sources.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate sources and fail if a JSON payload is missing or out of sync.",
    )
    args = parser.parse_args()

    if args.chapter is not None and not 1 <= args.chapter <= 114:
        parser.error("--chapter must be between 1 and 114")

    if args.chapter is not None:
        chapters = [args.chapter]
    else:
        chapters = sorted(
            int(match.group(1))
            for path in MARKDOWN_DIR.glob("tafsir_*.md")
            if (match := re.fullmatch(r"tafsir_(\d{3})\.md", path.name))
        )

    if not chapters:
        parser.error(f"No Markdown sources found in {MARKDOWN_DIR}")

    try:
        for chapter_number in chapters:
            markdown_path = MARKDOWN_DIR / f"tafsir_{chapter_number:03}.md"
            output_path = DATA_DIR / f"tafsir_{chapter_number:03}.json"
            if not markdown_path.is_file():
                raise BuildError(f"Missing Markdown source: {markdown_path.relative_to(ROOT)}")

            generated = build_payload(chapter_number, markdown_path)
            decoded = json.loads(generated)
            if not isinstance(decoded.get("verses"), dict):
                raise BuildError(f"Generated payload for chapter {chapter_number} is malformed")

            if args.check:
                if not output_path.is_file():
                    raise BuildError(f"Missing JSON payload: {output_path.relative_to(ROOT)}")
                current = output_path.read_text(encoding="utf-8")
                if current != generated:
                    raise BuildError(
                        f"{output_path.relative_to(ROOT)} is out of sync; "
                        "rerun scripts/build_tafsir_json.py"
                    )
                print(
                    f"Checked Surah {chapter_number}: {len(decoded['verses'])} verses "
                    f"({MIN_COMMENTARY_WORDS}–{MAX_COMMENTARY_WORDS} words each)"
                )
            else:
                output_path.write_text(generated, encoding="utf-8")
                print(f"Wrote {output_path.relative_to(ROOT)}: {len(decoded['verses'])} verses")
    except (BuildError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
