# Phrase-by-phrase authoring rules

These rules apply to every new phrase explanation in `tools/pairs/authored/NNN.json`.

## Writing rules

- Each phrase explanation must be **45–85 words**, counted separately. The translation label does not count.
- Use simple, direct English. Explain the phrase in context, including important terms when needed. Do not merely repeat the translation or add generic padding.
- The explanations should not all be short or fragmented. Each translation unit should express a meaningful phrase, clause, or complete sentence. Keep connected words and thoughts together unless a natural break is needed for clarity.
- Split at meaningful internal boundaries when a verse contains distinct components, even if the full verse is also a coherent sentence. For example, keep a statement of praise separate from its appositional description of Allah, and keep an invocation separate from the divine attributes that follow it. Each split should still read as a meaningful phrase or clause in context.
- Do not split merely to increase the number of entries. Keep inseparable words together, but do not combine distinct meaningful phrases just because they form one sentence. A short verse may have one unit when no meaningful internal boundary exists; longer or compound verses should be divided into their natural thought units.
- Preserve uncertainty and disagreement when presenting a debated interpretation. Give historical identifications their historical context and do not generalize them to present-day people or communities.
- Do not name commentary authors in the explanations. Write one substantive paragraph per phrase, with no Arabic script, em/en dashes, or semicolons.
- Phrase labels must be exact, consecutive pieces of the reader's English translation, covering every word once and in order.

## Write and validate

Write explanations directly in `authored/NNN.json`, then validate and regenerate the reader's data:

```sh
python3 tools/pairs/assemble.py --check
python3 tools/pairs/assemble.py
```

Run the tests against the regenerated data:

```sh
python3 -m unittest discover -s tools/pairs/tests
```

Automated validation checks structure, translation coverage, formatting, word count, and that each verse has phrase content.
