# Phrase-by-phrase explanations

See [`RULES.md`](RULES.md) for the binding authoring rules. Each explanation must be 45–85 words, and phrase labels must be meaningful, consecutive pieces of the reader's English translation.

## Workflow

1. Write explanations directly in `authored/NNN.json`.
2. Validate the authored material and run the tests:

   ```sh
   python3 tools/pairs/assemble.py --check
   python3 -m unittest discover -s tools/pairs/tests
   ```

3. When both pass, regenerate published data:

   ```sh
   python3 tools/pairs/assemble.py
   ```

Automated checks verify structure, exact translation coverage and order, paragraph formatting, the 45–85-word limit, and phrase density.

## Reading experience

The reader offers two separate commentary views in a switch: **Phrase by phrase** appears first, followed by **Full commentary**. Only the selected view is shown; the full Tafsīr al-Ṭabarī passage is not stacked underneath the phrase reading.

Phrase-by-phrase explanations are authored for the reader and are not excerpts from or replacements for the source commentary. Phrase data is optional per surah; the app displays the phrase view when published data exists.

## Source format

`authored/NNN.json` is the hand-written source for one surah. Phrase labels must be exact, consecutive pieces of the reader's `ayah_en` translation, covering every word exactly once and in reading order. Each explanation is one substantive paragraph of 45–85 words.

```json
{
  "surah": 1,
  "split_policy": "dense-v1",
  "verses": {
    "7": {
      "phrases": [
        {
          "translation": "the Path of those",
          "explanation": "A clear, substantive explanation in simple English that gives the phrase's meaning in context. Keep each paragraph between forty-five and eighty-five words, without padding or unnecessary repetition."
        }
      ]
    }
  }
}
```

The example is illustrative; complete authored chapters must include every verse and the required minimum number of meaningful phrases per verse. The `dense-v1` policy is enforced by `assemble.py`.

## Tools

- `RULES.md`: binding authoring requirements.
- `assemble.py --check`: validate without writing generated files.
- `assemble.py`: publish validated authored entries to `data/pairs_NNN.json`.
- `show.py SURAH [VERSE]`: inspect the authored/published phrase sequence.
- `tests/`: automated regression tests.
