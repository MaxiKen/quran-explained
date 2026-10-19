# Phrase-by-phrase explanations

**Binding authoring rules:** before authoring, editing, reviewing, or publishing phrase explanations, read [`RULES.md`](RULES.md). It is authoritative for source-first reading, globally dense phrase splitting, simple English, word definitions where useful, evidence, and the 30–85-word explanation length.

## Workflow

1. Read the complete commentary for every verse being edited before drafting. `python3 tools/pairs/review.py SURAH VERSE` prints the full mapped English commentary to support this source-first review. It is a reading aid, not proof that the source was read.
2. Author in `authored/NNN.json`. New chapters should declare chapter-level `"split_policy": "dense-v1"`. When migrating a legacy chapter incrementally, place the marker on each revised verse so those entries are enforced immediately; move it to chapter level after the entire chapter complies.
3. Run the required verification gate after every authoring/editing run. Only supply the human-review confirmation after checking all source commentaries and the resulting explanations and boundaries:

   ```sh
   python3 tools/pairs/verify.py --confirm-human-review
   ```

4. If verification passes, publish the generated data:

   ```sh
   python3 tools/pairs/assemble.py
   ```

5. Inspect the result and run the verification gate again after any edits. Review examples with `python3 tools/pairs/show.py SURAH [VERSE]`.

The verification script runs the assembler's full validation and the unit test suite. It requires an explicit human-review confirmation because no script can prove that a person read the complete commentary, judged historical nuance, checked simple and accurate English, or ensured that splits remain meaningful rather than choppy. A failed check blocks publication; do not weaken the rules to make legacy material pass.

## Reading experience

The reader offers two separate commentary views in a switch: **Phrase by phrase** appears first, followed by **Full commentary**. Only the selected view is shown; the full Tafsīr al-Ṭabarī passage is not stacked underneath the phrase reading.

Phrase by phrase is a concise alternative to the full source commentary. It pairs each consecutive piece of a verse's English translation with one clear paragraph. Each explanation is 30–85 words, written in plain English, and explains the phrase rather than merely restating it. Add a related verse, quotation, context, history, or illustration only when it genuinely helps, and weave it into the explanation without a type label or formulaic lead-in.

This layer is authored for the reader and is not an excerpt from or replacement for Tafsīr al-Ṭabarī. Surahs 1–16 currently have authored phrase explanations; later surahs are not yet authored.

## Source format

`authored/NNN.json` is the hand-written source for one surah. Phrase labels must be exact, consecutive pieces of the reader's `ayah_en` translation, in reading order, covering every word exactly once. Each explanation is one substantive paragraph of 30–85 words.

```json
{
  "surah": 1,
  "split_policy": "dense-v1",
  "verses": {
    "7": {
      "phrases": [
        {
          "translation": "the Path of those",
          "explanation": "A phrase explanation in simple English, supported by the complete commentary and focused on the meaning of this translation unit."
        }
      ]
    }
  }
}
```

The example is illustrative only; complete authored chapters must include every verse and the required minimum number of meaningful phrases per verse. The `dense-v1` policy is enforced by `assemble.py` and `verify.py`. Legacy chapters can be migrated verse by verse using verse-level markers, then switched to a chapter-level marker when the full chapter complies.

## Tools

- `RULES.md`: binding authoring requirements.
- `review.py SURAH VERSE`: show complete source commentary for source-first review.
- `verify.py --confirm-human-review`: required post-edit verification gate. It runs structure, coverage, formatting, word-count, density, generated-data consistency, and unit checks, and requires an explicit human-review attestation.
- `assemble.py --check`: automated validation without writing generated files.
- `assemble.py`: publish validated authored entries to `data/pairs_NNN.json`.
- `show.py SURAH [VERSE]`: inspect the authored/published phrase sequence.
- `tests/`: automated regression tests.
