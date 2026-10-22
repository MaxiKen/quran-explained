# Phrase-by-phrase authoring rules

These rules apply to every new phrase explanation in `tools/pairs/authored/NNN.json`.

## Writing rules

- Each phrase explanation must be **45–85 words**, counted separately. The translation label does not count.
- Use simple, direct English. Explain the phrase in context, including important terms when needed. Do not merely repeat the translation or add generic padding.
- The explanations should not all be short or fragmented. Each translation unit should express a meaningful phrase, clause, or complete sentence. Keep connected words and thoughts together unless a natural break is needed for clarity.
- Split only where the translation has a meaningful change of thought, clause, or phrase. Do not split merely to increase the number of entries. A short complete expression may remain one unit; a longer verse may be divided into a few coherent units.
- Preserve uncertainty and disagreement when presenting a debated interpretation. Give historical identifications their historical context and do not generalize them to present-day people or communities.
- Do not name commentary authors in the explanations. Write one substantive paragraph per phrase, with no Arabic script, em/en dashes, or semicolons.
- Phrase labels must be exact, consecutive pieces of the reader's English translation, covering every word once and in order.

## Write and validate

Write explanations directly in `authored/NNN.json`, then run:

```sh
python3 tools/pairs/assemble.py --check
python3 -m unittest discover -s tools/pairs/tests
```

If validation passes, regenerate the reader's data:

```sh
python3 tools/pairs/assemble.py
```

Automated validation checks structure, translation coverage, formatting, word count, and that each verse has phrase content.
