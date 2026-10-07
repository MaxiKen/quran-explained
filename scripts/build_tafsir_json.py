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
MIN_COMMENTARY_WORDS = 500
MAX_COMMENTARY_WORDS = 1200
WORD_TOKEN = re.compile(r"\b[^\W_]+(?:[’'‑-][^\W_]+)*\b", re.UNICODE)
SECTION_HEADING = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
SUBHEADING = re.compile(r"^###[ \t]+(.+?)[ \t]*$", re.MULTILINE)
VERSE_HEADING = re.compile(r"\*\*(\d+):(\d+)\*\*")
RICH_MARKDOWN = re.compile(
    r"\*\*.+?\*\*|\*[^*\n]+?\*|`[^`]+`|^#{2,6}[ \t]+.+|^[ \t]*[-*+][ \t]+",
    re.MULTILINE,
)
BRACKETED_CITATION = re.compile(
    r"\[(?:(?:Q\s+|Qur[’']an\s+|Surah\s+)\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?|"
    r"(?:Report|Hadith|Poem):[^\]\n]+|"
    r"(?:Ṣaḥīḥ|Musnad|al-Muwaṭṭaʾ)\b[^\]\n]*)\]",
    re.IGNORECASE,
)
INLINE_REFERENCE = re.compile(
    r"\b(?:Q\s+\d{1,3}:\d{1,3}|Qur[’']an\s+\d{1,3}:\d{1,3}|"
    r"(?:report|reports|narration|narrated|hadith|poem|line)\b|"
    r"(?:Ṣaḥīḥ|Musnad|al-Muwaṭṭaʾ)\b)",
    re.IGNORECASE,
)
COMPILER_CITATION = re.compile(
    r"\b(?:al[-\s]?(?:Ṭ|T)abar[iī]|(?:Ṭ|T)abar[iī])\b",
    re.IGNORECASE,
)
QUOTED_TEXT = re.compile(r"“[^”\n]+”|\"[^\"\n]+\"")
EVIDENCE_QUOTE = re.compile(r"\*{1,3}[“\"][^“”\"\n]{20,}[”\"]\*{1,3}")
BOLD_MARKUP = re.compile(r"\*\*\*(.+?)\*\*\*|\*\*(.+?)\*\*")
VERSE_HIGHLIGHT_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but",
    "by", "for", "from", "has", "have", "in", "is", "it", "of", "on",
    "or", "that", "the", "this", "to", "was", "were", "who", "with",
    "you", "your", "we", "us",
}


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


def validate_quoted_text(commentary: str, chapter_number: int, verse_number: int) -> None:
    """Require every double-quoted phrase to be set in Markdown italics."""
    for match in QUOTED_TEXT.finditer(commentary):
        before = commentary[: match.start()]
        after = commentary[match.end() :]
        star_open = len(before) - len(before.rstrip("*"))
        star_close = len(after) - len(after.lstrip("*"))
        underscore_open = len(before) - len(before.rstrip("_"))
        underscore_close = len(after) - len(after.lstrip("_"))
        if not (
            (star_open % 2 == 1 and star_close % 2 == 1)
            or (underscore_open % 2 == 1 and underscore_close % 2 == 1)
        ):
            raise BuildError(
                f"Quoted text at {chapter_number}:{verse_number} must be italicized"
            )


def validate_verse_wording(
    translation: str, commentary: str, chapter_number: int, verse_number: int
) -> None:
    """Require recognizable multiword wording from the current verse to be bold."""
    prose = "\n".join(
        line for line in commentary.splitlines() if not line.lstrip().startswith("### ")
    )
    translation_tokens = [match.group(0).casefold() for match in WORD_TOKEN.finditer(translation)]
    commentary_tokens = list(WORD_TOKEN.finditer(prose))
    bold_spans: list[tuple[int, int]] = []
    for match in BOLD_MARKUP.finditer(prose):
        group = 1 if match.group(1) is not None else 2
        bold_spans.append(match.span(group))

    for length in range(2, len(translation_tokens) + 1):
        for start in range(len(translation_tokens) - length + 1):
            phrase = translation_tokens[start : start + length]
            meaningful = sum(
                token not in VERSE_HIGHLIGHT_STOPWORDS for token in phrase
            )
            if meaningful < 2:
                continue
            for token_start in range(len(commentary_tokens) - length + 1):
                window = commentary_tokens[token_start : token_start + length]
                if [token.group(0).casefold() for token in window] != phrase:
                    continue
                for token in window:
                    if token.group(0).casefold() in VERSE_HIGHLIGHT_STOPWORDS:
                        continue
                    occurrence = token.span()
                    if not any(
                        bold_start <= occurrence[0] and occurrence[1] <= bold_end
                        for bold_start, bold_end in bold_spans
                    ):
                        excerpt = " ".join(item.group(0) for item in window)
                        raise BuildError(
                            f"Wording from verse {chapter_number}:{verse_number} appears "
                            f"without bold formatting: {excerpt!r}"
                        )


def parse_markdown(markdown_path: Path, chapter_number: int) -> tuple[str | None, list[tuple[int, str]]]:

    text = markdown_path.read_text(encoding="utf-8")
    markdown_headings = re.findall(r"(?m)^#{1,6}[ \t]+(.+?)[ \t]*$", text)
    if not markdown_headings:
        raise BuildError(f"No Markdown headings in {markdown_path.name}")
    for label in markdown_headings:
        styled = re.fullmatch(r"\*\*(.+)\*\*", label.strip())
        if not styled or styled.group(1) != styled.group(1).upper():
            raise BuildError(
                f"Heading must be bold and uppercase in {markdown_path.name}: {label!r}"
            )
    if not markdown_headings[0].strip().startswith("**SURAH "):
        raise BuildError(f"The first heading in {markdown_path.name} must name the surah")

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

        if label == "**INTRODUCTION**":
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

        subheadings = list(SUBHEADING.finditer(commentary))
        if len(subheadings) < 2:
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} needs at least two "
                "'###' subheadings"
            )
        for subheading in subheadings:
            label = subheading.group(1).strip()
            styled = re.fullmatch(r"\*\*(.+)\*\*", label)
            if not styled or styled.group(1) != styled.group(1).upper():
                raise BuildError(
                    f"Subheadings at {chapter_number}:{verse_number} must be bold and uppercase"
                )
        first_line = next((line.strip() for line in commentary.splitlines() if line.strip()), "")
        if first_line != "### **MEANING**" or subheadings[0].group(1).strip() != "**MEANING**":
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} must begin with "
                "'### **MEANING**' before supporting evidence"
            )
        meaning_end = subheadings[1].start()
        if INLINE_REFERENCE.search(commentary[subheadings[0].end() : meaning_end]):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} introduces supporting "
                "evidence before explaining the verse's meaning"
            )

        if BRACKETED_CITATION.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} uses bracketed citations; "
                "write source references in natural sentence flow"
            )
        if any(
            INLINE_REFERENCE.match(line.strip())
            and len(WORD_TOKEN.findall(line)) < 8
            for line in commentary.splitlines()
        ):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} places a bare source "
                "reference on its own line; weave it into a sentence"
            )
        if COMPILER_CITATION.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} cites al-Tabari "
                "as the interpretive authority; cite the underlying source instead"
            )

        countable = SUBHEADING.sub("", commentary)
        word_count = len(WORD_TOKEN.findall(countable))
        if word_count < MIN_COMMENTARY_WORDS or word_count > MAX_COMMENTARY_WORDS:
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} has {word_count} words; "
                f"required range is {MIN_COMMENTARY_WORDS}–{MAX_COMMENTARY_WORDS}"
            )
        if not INLINE_REFERENCE.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} needs a natural, inline "
                "Qur’anic/report/poem citation"
            )
        validate_quoted_text(commentary, chapter_number, verse_number)
        if not EVIDENCE_QUOTE.search(commentary):
            raise BuildError(
                f"Commentary at {chapter_number}:{verse_number} needs an italicized "
                "quoted or closely translated source-evidence excerpt"
            )
        validate_verse_wording(translation, commentary, chapter_number, verse_number)
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
