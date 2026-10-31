#!/usr/bin/env python3
"""Step two of authoring: write a batch, and let the rules check it.

    python3 tools/pairs/authoring/author.py DRAFT.json [--dry-run]

`DRAFT.json` holds the phrases for one or more verses:

```json
{
  "surah": 2,
  "verses": {
    "281": [
      {"translation": "...", "ar": "...", "explanation": "..."},
      {"translation": "...", "ar": "...", "explanation": "..."}
    ]
  }
}
```

The writer checks every phrase before it writes anything, and writes nothing
at all if any phrase fails. What it checks:

- the house style, including the one-voice rule that no commentator,
  transmitter or companion is named;
- the floor, and the length curve, with the working margin around it, so that
  a draft is not published far from the length its material deserves;
- the split rule, so that no piece of a verse is left standing on less of
  Ṭabarī's own discussion than it can carry;
- the Arabic spans, which must be exact, consecutive pieces of the verse's
  Arabic, covering the verse once in order;
- the English labels, which must be exact, consecutive pieces of the reader's
  own translation, covering the verse once in order.

This is the tool that keeps the rules in force while a chapter is being
written, so that a mistake is caught at the draft rather than at the gate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = os.path.dirname(HERE)
sys.path.insert(0, PAIRS)

import assemble  # noqa: E402
import curve  # noqa: E402
import digest  # noqa: E402
import source  # noqa: E402
import style  # noqa: E402

AUTHORED = os.path.join(PAIRS, "authored")


def check_batch(surah: int, batch: dict) -> list[str]:
    """Every problem in a batch of drafted phrases, as a list of messages."""
    problems: list[str] = []
    tafsir, verses, _ = digest.load_surah(surah)
    modern = source.read_chapter(surah)

    for number, phrases in batch.get("verses", {}).items():
        where_verse = "surah %d verse %s" % (surah, number)
        if number not in verses:
            problems.append("%s: the verse does not exist" % where_verse)
            continue
        if not isinstance(phrases, list) or not phrases:
            problems.append("%s: no phrases in the batch" % where_verse)
            continue

        arabic = verses[number]["ar"]
        spans_text = []
        for index, phrase in enumerate(phrases, 1):
            where = "%s phrase %d" % (where_verse, index)
            explanation = phrase.get("explanation", "")
            if not isinstance(explanation, str) or not explanation.strip():
                problems.append("%s: empty explanation" % where)
                continue
            problems.extend(style.style_problems(explanation, where))
            spans_text.append(phrase.get("ar", ""))

        try:
            spans = digest.phrase_spans(spans_text, arabic)
        except ValueError as exc:
            problems.append("%s: %s" % (where_verse, exc))
            continue

        measured = digest.measure(digest.verse_passage(tafsir, number), arabic)
        for index, (phrase, span) in enumerate(zip(phrases, spans), 1):
            where = "%s phrase %d" % (where_verse, index)
            info = digest.budget(measured, span)
            have = len(" ".join(phrase.get("explanation", "").split()).split())
            want = curve.desired(info["points"])

            floor = digest.length_problem(have, info, where)
            if floor:
                problems.append(floor)
            if curve.off_curve(have, want):
                problems.append("%s: %d words, the curve wants %d (margin %d)"
                                % (where, have, want, curve.tolerance(want)))
            if len(phrases) > 1:
                split = digest.split_problem(info, where)
                if split:
                    problems.append(split)

        cursor = 0
        translation = modern[number].get("en", "")
        for index, phrase in enumerate(phrases, 1):
            where = "%s phrase %d" % (where_verse, index)
            piece = phrase.get("translation", "")
            start = translation.find(piece, cursor) if piece else -1
            if start < 0:
                problems.append("%s: the translation phrase is missing or out of order" % where)
                continue
            cursor = start + len(piece)
        if assemble.LETTER_OR_NUMBER.search(translation[cursor:]):
            problems.append("%s: the phrase parts do not cover the full verse translation"
                            % where_verse)
    return problems


def write_batch(surah: int, batch: dict) -> None:
    """Write a checked batch into the authored chapter."""
    path = os.path.join(AUTHORED, "%03d.json" % surah)
    with open(path, encoding="utf-8") as handle:
        authored = json.load(handle)
    chapter_policy = authored.get("split_policy")
    for number, phrases in batch.get("verses", {}).items():
        existing = authored["verses"].get(number, {})
        entry = {"phrases": phrases}
        # A verse keeps the policy it was written under, so that a chapter
        # migrating one verse at a time carries both policies at once.
        policy = existing.get("split_policy") or chapter_policy
        if policy == assemble.POLICY_TABARI:
            entry["split_policy"] = policy
        authored["verses"][number] = entry
    authored["verses"] = {number: authored["verses"][number]
                          for number in sorted(authored["verses"], key=lambda n: int(n))}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(authored, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("draft", help="the drafted phrases, as JSON")
    parser.add_argument("--dry-run", action="store_true", help="check without writing")
    args = parser.parse_args()

    with open(args.draft, encoding="utf-8") as handle:
        batch = json.load(handle)
    surah = int(batch.get("surah") or os.path.basename(args.draft)[:3])

    problems = check_batch(surah, batch)
    if problems:
        for problem in problems:
            print("  ! %s" % problem)
        print("NOT WRITTEN: %d problem(s) in the batch" % len(problems))
        return 1

    if args.dry_run:
        print("the batch is clean (%d verse(s))" % len(batch.get("verses", {})))
        return 0

    write_batch(surah, batch)
    print("WROTE %d verse(s) into %03d.json" % (len(batch.get("verses", {})), surah))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
