# Phrase-by-phrase authoring rules

These rules apply to every new phrase explanation in `tools/pairs/authored/NNN.json`.

## Writing rules

- Each phrase explanation must be **45–85 words**, counted separately. The translation label does not count.
- Use simple, direct English. Explain the phrase in context, including important terms when needed. Do not merely repeat the translation or add generic padding.
- Preserve uncertainty and disagreement when presenting a debated interpretation. Give historical identifications their historical context and do not generalize them to present-day people or communities.
- Do not name commentary authors in the explanations. Write one substantive paragraph per phrase, with no Arabic script, em/en dashes, or semicolons.
- Split translations into meaningful, consecutive units. Avoid arbitrary boundaries and ensure phrase labels cover the complete translation exactly once and in order.
- New chapters should use `"split_policy": "dense-v1"`. This requires at least one phrase per three translation words, rounded up, with at least two phrases for verses of three or more words. Use natural boundaries; do not make fragments solely to meet a count.

## Write and validate

Write phrase explanations directly in `authored/NNN.json`, then run:

```sh
python3 tools/pairs/assemble.py --check
python3 -m unittest discover -s tools/pairs/tests
```

If validation passes, regenerate the reader's data:

```sh
python3 tools/pairs/assemble.py
```

Automated validation checks structure, translation coverage, formatting, word count, and phrase density.
