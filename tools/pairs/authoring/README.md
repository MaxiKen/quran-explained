# Authoring tools

The rules in [`../RULES.md`](../RULES.md) made executable. Each tool here is
one step of writing a chapter, and each one checks the rules it can check
before anything is written.

| tool | step | what it does |
| --- | --- | --- |
| `measure.py SURAH VERSE [--full]` | read | what Ṭabarī holds for the verse, classified and measured, with every candidate piece scored |
| `author.py DRAFT.json` | write | checks a batch of drafted phrases against every rule, then writes them into the chapter |
| `audit.py SURAH [FIRST LAST]` | check | the published chapter against the curve, the house style, the floor and the split rule |
| `curve.py POINTS` | measure | the length curve itself, for a given amount of material |

`../digest.py` remains the measurement engine underneath them, and
`../assemble.py` remains the publishing gate.

## measure.py

```sh
python3 tools/pairs/authoring/measure.py 2 281 --full
```

Prints three things:

1. **What the source holds.** Every paragraph of Ṭabarī's passage for the
   verse, with its class, its weight in points, and where it sits in the
   verse. `--full` prints the whole text, which is what a draft is written
   from.
2. **The candidate pieces.** Every run of one, two or three words of the
   verse, with the points Ṭabarī makes about it and the curve it would need.
   A piece marked *merge with a neighbour* carries less than
   `digest.MIN_SPLIT_POINTS` substantive points, so it cannot stand as a
   phrase of its own.
3. **The split as it stands**, for a verse that has been authored already,
   with the words written against the curve.

## author.py

```sh
python3 tools/pairs/authoring/author.py draft.json
```

The draft is a JSON file holding the phrases for one or more verses:

```json
{
  "surah": 2,
  "verses": {
    "281": [
      {"translation": "In the Name", "ar": "بِسۡمِ", "explanation": "..."}
    ]
  }
}
```

The writer checks every phrase before it writes anything, and writes nothing
at all if any phrase fails:

- the house style, including the one-voice rule;
- the floor, and the curve with its working margin;
- the split rule;
- the Arabic spans: exact, consecutive, covering the verse once in order;
- the English labels: exact, consecutive, covering the verse once in order.

`--dry-run` checks without writing. A verse keeps the policy it was written
under, so a chapter migrating one verse at a time carries both policies at
once.

## audit.py

```sh
python3 tools/pairs/authoring/audit.py 2
```

Reports the published chapter against the curve and the house style, phrase
by phrase. The curve is a working target rather than a published rule, so a
phrase outside the margin is reported as a warning; the house style, the
floor and the split rule always fail the run. `--strict` also fails on the
curve, and `--quiet` prints only the problems.

al-Fātiḥa is reported above the curve. That is expected: the curve was
measured from al-Fātiḥa's own practice, and the curve is a target plus a
tenth, not a cap.

## curve.py

```sh
python3 tools/pairs/authoring/curve.py 12.5
```

The length rule as arithmetic:

- `desired(points) = round(1.1 × max(110, round(15 × points)))`
- `tolerance(want) = max(12, int(want × 0.12))`

15 words for every point Ṭabarī makes, the target plus a tenth to write to,
never less than 110 words. There is no ceiling: the curve is where a draft
is written, not a limit on what it may say.
