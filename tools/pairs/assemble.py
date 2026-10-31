#!/usr/bin/env python3
"""Validate and publish the hand-written phrase explanations.

    python3 tools/pairs/assemble.py --check   # validate, write nothing
    python3 tools/pairs/assemble.py           # publish all authored chapters

`tools/pairs/authored/NNN.json` contains exact pieces of the reader's own
English verse translation and the explanation written for each piece. This
script verifies that the phrases cover the verse in reading order, then
publishes the data consumed by the app as `data/pairs_NNN.json`.

Two authoring policies are in force, declared per chapter by `split_policy`:

`sense-v1` (chapters 3 to 43 as first written) requires one paragraph of 45-85
words for every phrase, whatever the source holds.

`tabari-v2` derives the length from Tafsīr al-Ṭabarī instead. Each phrase also
names the exact piece of the verse's Arabic it explains, `digest.py` measures
what Ṭabarī says about that piece, and the explanation has to be as long as
the material deserves: a floor, a proportional target, and no ceiling. Several
paragraphs are allowed, because a phrase carrying nine opinions cannot be
answered in one block of 85 words. Chapters migrate one at a time; a chapter
that has not migrated keeps its old gates.

The house style every explanation follows, whatever its policy, lives in
`style.py`: no Arabic script, no em dash or en dash, no semicolon, a capital
letter at the start, and one voice that names no commentator, transmitter or
companion. Under `tabari-v2` the one-voice rule is enforced here.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import digest  # noqa: E402
import source  # noqa: E402
import style  # noqa: E402

AUTHORED = os.path.join(HERE, "authored")
LETTER_OR_NUMBER = re.compile(r"[A-Za-z0-9]")

POLICY_LEGACY = "sense-v1"
POLICY_TABARI = "tabari-v2"
POLICIES = (None, POLICY_LEGACY, POLICY_TABARI)

# sense-v1: every explanation sits in this band, one paragraph, no exceptions.
LEGACY_MIN_WORDS = 45
LEGACY_MAX_WORDS = 85


def check_explanation(
    value: object, where: str, problems: list[str], policy: str, target: dict | None
) -> str:
    """Validate one explanation under the policy the chapter declared."""
    if not isinstance(value, str) or not value.strip():
        problems.append("%s: empty explanation" % where)
        return ""

    text = value.strip()
    # The house style every explanation shares. Under tabari-v2 the one-voice
    # rule is enforced as well: the explanation names no commentator,
    # transmitter or companion. The older sense-v1 chapters keep the text
    # they were written under, and are held to it when they migrate.
    problems.extend(style.style_problems(text, where, one_voice=policy == POLICY_TABARI))

    if policy == POLICY_TABARI:
        # Paragraphs are allowed and expected once the material runs long.
        parts = [p.strip() for p in re.split(r"\n\s*\n", text)]
        words = len(" ".join(parts).split())
        if target is None:
            problems.append("%s: cannot measure the source for this phrase" % where)
        else:
            problem = digest.length_problem(words, target, where)
            if problem:
                problems.append(problem)
        return "\n\n".join(parts)

    words = text.split()
    if len(words) < LEGACY_MIN_WORDS:
        problems.append("%s: explanation is too short" % where)
    if len(words) > LEGACY_MAX_WORDS:
        problems.append("%s: explanation is too long to keep concise" % where)
    if "\n" in text or "\r" in text:
        problems.append("%s: explanation must be a single paragraph" % where)
    return text


def check_phrase(
    phrase: object,
    where: str,
    problems: list[str],
    policy: str,
    target: dict | None = None,
) -> dict[str, str]:
    if not isinstance(phrase, dict):
        problems.append("%s: phrase must be an object" % where)
        return {"translation": "", "explanation": ""}

    allowed = {"translation", "explanation"}
    if policy == POLICY_TABARI:
        # The Arabic piece the phrase explains: what the source is measured on.
        allowed.add("ar")
    extra = set(phrase) - allowed
    if extra:
        problems.append("%s: unexpected field(s): %s" % (where, ", ".join(sorted(extra))))

    translation = phrase.get("translation", "")
    if not isinstance(translation, str) or not translation.strip():
        problems.append("%s: empty translation phrase" % where)
        translation = ""
    else:
        translation = translation.strip()

    explanation = check_explanation(phrase.get("explanation"), where, problems, policy, target)
    return {
        "translation": translation,
        "explanation": explanation,
    }


def build_surah(surah: int) -> tuple[dict, list[str]]:
    """Return one published chapter payload and its validation problems."""
    problems: list[str] = []
    path = os.path.join(AUTHORED, "%03d.json" % surah)
    with open(path, encoding="utf-8") as handle:
        authored = json.load(handle)

    if authored.get("surah") != surah:
        problems.append("surah %d: authored file has a mismatched surah number" % surah)

    split_policy = authored.get("split_policy")
    if split_policy not in POLICIES:
        problems.append("surah %d: unknown split_policy %r" % (surah, split_policy))

    chapter = source.read_chapter(surah)
    verses: dict[str, dict] = {}
    authored_verses = authored.get("verses", {})
    if not isinstance(authored_verses, dict) or not authored_verses:
        problems.append("surah %d: no verses have been authored" % surah)
        return {"surah": surah, "verses": verses}, problems

    # A tabari-v2 chapter is measured against its own commentary, so the
    # passages are read once per chapter rather than once per phrase. A chapter
    # migrating one verse at a time declares the policy per verse, so a single
    # verse asking for measurement is enough to load it.
    tafsir = None
    measured: dict[str, list[dict]] = {}
    needs_tafsir = split_policy == POLICY_TABARI or any(
        isinstance(v, dict) and v.get("split_policy") == POLICY_TABARI
        for v in authored_verses.values())
    if needs_tafsir:
        try:
            tafsir, _, _ = digest.load_surah(surah)
        except (OSError, ValueError) as exc:
            problems.append("surah %d: cannot read the commentary to measure it: %s" % (surah, exc))

    for ayah, verse in authored_verses.items():
        where_verse = "surah %d verse %s" % (surah, ayah)
        if ayah not in chapter:
            problems.append("%s: verse does not exist in the reader's chapter data" % where_verse)
            continue
        if not isinstance(verse, dict):
            problems.append("%s: verse entry must be an object" % where_verse)
            continue

        verse_policy = verse.get("split_policy", split_policy)
        if verse_policy not in POLICIES:
            problems.append("%s: unknown split_policy %r" % (where_verse, verse_policy))

        phrases_data = verse.get("phrases", [])
        if not isinstance(phrases_data, list) or not phrases_data:
            problems.append("%s: no phrases have been authored" % where_verse)
            continue

        modern = chapter[ayah].get("en", "")

        # Where each phrase sits in the verse's Arabic, and what Ṭabarī says
        # about that slice. Both are needed before an explanation can be
        # judged, so they are resolved for the whole verse first.
        targets: list[dict | None] = [None] * len(phrases_data)
        if verse_policy == POLICY_TABARI and tafsir is not None:
            arabic = chapter[ayah].get("ar", "")
            spans_text = [p.get("ar", "") if isinstance(p, dict) else "" for p in phrases_data]
            if any(not isinstance(s, str) or not s.strip() for s in spans_text):
                problems.append("%s: every phrase needs the Arabic piece it explains (\"ar\")"
                                % where_verse)
            else:
                try:
                    passage = digest.verse_passage(tafsir, ayah)
                except KeyError as exc:
                    problems.append("%s: %s" % (where_verse, exc))
                    passage = None
                if passage is not None:
                    if ayah not in measured:
                        measured[ayah] = digest.measure(passage, arabic)
                    try:
                        spans = digest.phrase_spans(spans_text, arabic)
                    except ValueError as exc:
                        problems.append("%s: %s" % (where_verse, exc))
                        spans = None
                    if spans is not None:
                        targets = [digest.budget(measured[ayah], span) for span in spans]
                        # A split is only worth making where Ṭabarī has
                        # something of his own to say about the piece. A verse's
                        # only phrase is not a split and is left alone.
                        if len(targets) > 1:
                            for number, target in enumerate(targets, 1):
                                problem = digest.split_problem(
                                    target, "%s phrase %d" % (where_verse, number))
                                if problem:
                                    problems.append(problem)

        cursor = 0
        phrases = []
        for number, authored_phrase in enumerate(phrases_data, 1):
            where = "%s phrase %d" % (where_verse, number)
            phrase = check_phrase(authored_phrase, where, problems, verse_policy, targets[number - 1])
            translation = phrase["translation"]
            if translation:
                start = modern.find(translation, cursor)
                if start < 0:
                    problems.append("%s: translation phrase is missing or out of order" % where)
                else:
                    gap = modern[cursor:start]
                    if LETTER_OR_NUMBER.search(gap):
                        problems.append("%s: words are skipped between phrase parts" % where)
                    cursor = start + len(translation)
            phrases.append(phrase)

        if LETTER_OR_NUMBER.search(modern[cursor:]):
            problems.append("%s: the phrase parts do not cover the full verse translation" % where_verse)

        verses[ayah] = {"phrases": phrases}

    return {"surah": surah, "verses": verses}, problems


def main() -> int:
    check_only = "--check" in sys.argv
    names = sorted(name for name in os.listdir(AUTHORED) if name.endswith(".json"))
    if not names:
        print("nothing authored yet")
        return 0

    all_problems: list[str] = []
    written = 0
    for name in names:
        surah = int(name[:3])
        data, problems = build_surah(surah)
        all_problems.extend(problems)
        if problems:
            continue
        if not check_only:
            output = os.path.join(ROOT, "data", "pairs_%03d.json" % surah)
            with open(output, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
                handle.write("\n")
        written += 1

    print("%d surah(s) %s" % (written, "checked" if check_only else "written"))
    for problem in all_problems:
        print("  ! %s" % problem)
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
