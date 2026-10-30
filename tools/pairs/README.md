# Phrase-by-phrase explanations

See [`RULES.md`](RULES.md) for the binding authoring rules. Phrase labels should represent meaningful phrases or clauses rather than chopped-up word fragments.

Two policies are in force, declared per chapter by `split_policy`:

| policy | chapters | length rule | paragraphs |
| --- | --- | --- | --- |
| `sense-v1` | 2 to 43 | fixed 45–85 words per phrase | one |
| `tabari-v2` | 1 (al-Fātiḥa), and new chapters | derived from Tafsīr al-Ṭabarī: floor 40 words, no ceiling | as many as the argument needs |

Under `tabari-v2` an explanation is a beginner's summary of what Ṭabarī says about that piece of the verse, and it is as long as what he says deserves. Each phrase names the piece of the verse's Arabic it explains (`ar`), `digest.py` measures the passage against those spans, and `assemble.py` holds the result to the measured target. A phrase where Ṭabarī makes one point stays short; a phrase where he weighs two readings, three opinions and a verdict grows to fit, and is not truncated by a ceiling.

Chapters migrate one at a time. A chapter that has not migrated keeps the gates it was written under, so `assemble.py --check` passes on the whole corpus at every commit.

## Workflow

1. Read the source for the verse, measured against the phrases:

   ```sh
   python3 tools/pairs/digest.py SURAH VERSE --full
   ```

2. Write explanations directly in `authored/NNN.json`.
3. Validate and regenerate the published data:

   ```sh
   python3 tools/pairs/assemble.py --check
   python3 tools/pairs/assemble.py
   ```

4. Run the tests against the regenerated data:

   ```sh
   python3 -m unittest discover -s tools/pairs/tests
   ```

Automated checks verify structure, exact translation coverage and order, exact Arabic-span coverage, paragraph formatting, and that every explanation is as long as its material deserves under the policy its chapter declares.

## Reading experience

The reader offers two separate commentary views in a switch: **Phrase by phrase** appears first, followed by **Full commentary**. Only the selected view is shown; the full Tafsīr al-Ṭabarī passage is not stacked underneath the phrase reading.

Phrase-by-phrase explanations are written for the reader. They are not excerpts from the source commentary and do not replace it: under `tabari-v2` they summarise what Ṭabarī discusses, in plain modern English, at the length his discussion deserves. Phrase data is optional per surah; the app displays the phrase view when published data exists. An explanation that runs to several paragraphs is rendered as several paragraphs.

## Source format

`authored/NNN.json` is the hand-written source for one surah. Phrase labels must be exact, consecutive pieces of the reader's `ayah_en` translation, covering every word exactly once and in reading order. Under `tabari-v2` each phrase also carries `ar`, an exact consecutive piece of the reader's `ayah_ar`, covering the verse once in order. That span is what the source is measured against, and it is not published to the reader.

```json
{
  "surah": 1,
  "split_policy": "tabari-v2",
  "verses": {
    "7": {
      "phrases": [
        {
          "translation": "the Path of those You have blessed",
          "ar": "صِرَٰطَ ٱلَّذِينَ أَنۡعَمۡتَ عَلَيۡهِمۡ",
          "explanation": "A summary in plain English of what the commentary says about this piece of the verse, as long as that material deserves.\n\nA second paragraph when the material has a second joint to break at."
        }
      ]
    }
  }
}
```

The example is illustrative. Complete authored chapters must include every verse. Each phrase should be a meaningful phrase, clause, or sentence, and under `tabari-v2` the boundaries follow the units the commentary itself works through.

## Tools

- `RULES.md`: binding authoring requirements.
- `digest.py SURAH [VERSE]`: what Ṭabarī discusses for each phrase of a verse, classified and measured, with the word target that follows. `--full` prints the source of each substantive paragraph, for authoring from it. `--stats SPEC` measures a range of chapters.
- `assemble.py --check`: validate without writing generated files.
- `assemble.py`: publish validated authored entries to `data/pairs_NNN.json`.
- `show.py SURAH [VERSE]`: inspect the authored/published phrase sequence.
- `review.py SURAH VERSE`: the complete commentary for one verse before the draft.
- `verify.py --confirm-human-review`: the full gate, automated checks plus the recorded human review.
- `tests/`: automated regression tests.
