# Phrase-by-phrase explanations

See [`RULES.md`](RULES.md) for the binding authoring rules. Each explanation must be 45–85 words. Phrase labels should represent meaningful phrases or clauses rather than chopped-up word fragments. Split distinct meaningful components, such as a statement of praise and its appositional description, even when both form one coherent sentence.

## Workflow

1. Write explanations directly in `authored/NNN.json`.
2. Validate and regenerate the published data:

   ```sh
   python3 tools/pairs/assemble.py --check
   python3 tools/pairs/assemble.py
   ```

3. Run the tests against the regenerated data:

   ```sh
   python3 -m unittest discover -s tools/pairs/tests
   ```

Automated checks verify structure, exact translation coverage and order, paragraph formatting, the 45–85-word limit, and that each authored verse has phrase content.

## Reading experience

The reader offers two separate commentary views in a switch: **Phrase by phrase** appears first, followed by **Full commentary**. Only the selected view is shown; the full Tafsīr al-Ṭabarī passage is not stacked underneath the phrase reading.

Phrase-by-phrase explanations are authored for the reader and are not excerpts from or replacements for the source commentary. Phrase data is optional per surah; the app displays the phrase view when published data exists.

## Source format

`authored/NNN.json` is the hand-written source for one surah. Phrase labels must be exact, consecutive pieces of the reader's `ayah_en` translation, covering every word exactly once and in reading order. Each explanation is one substantive paragraph of 45–85 words. Keep each label as a meaningful thought; one complete expression may be enough for a short verse, while longer verses may use a few coherent units.

```json
{
  "surah": 1,
  "verses": {
    "7": {
      "phrases": [
        {
          "translation": "the Path of those You have blessed",
          "explanation": "A clear, substantive explanation in simple English that gives the phrase's meaning in context. Keep each paragraph between forty-five and eighty-five words, without padding or unnecessary repetition."
        }
      ]
    }
  }
}
```

The example is illustrative. Complete authored chapters must include every verse. Each phrase should be a meaningful phrase, clause, or sentence. These natural boundaries are authored individually rather than forced to a fixed phrase count.

## Tools

- `RULES.md`: binding authoring requirements.
- `assemble.py --check`: validate without writing generated files.
- `assemble.py`: publish validated authored entries to `data/pairs_NNN.json`.
- `show.py SURAH [VERSE]`: inspect the authored/published phrase sequence.
- `tests/`: automated regression tests.
