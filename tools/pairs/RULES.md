# Phrase-by-phrase authoring rules

These rules apply to every new phrase explanation in `tools/pairs/authored/NNN.json`.

Two policies are in force, declared per chapter by `split_policy`. Chapters 2
to 43 are `sense-v1`; al-Fātiḥa is `tabari-v2`, the policy new chapters are
written under and old chapters migrate to one at a time. The writing rules
below apply to both. The length rules differ, and each chapter is held to the
policy it declares.

## Writing rules

- Use simple, direct English, written for a reader meeting the verse for the first time. Explain the phrase in context, including important terms when needed. Do not merely repeat the translation or add generic padding.
- The explanations should not all be short or fragmented. Each translation unit should express a meaningful phrase, clause, or complete sentence. Keep connected words and thoughts together unless a natural break is needed for clarity.
- Preserve uncertainty and disagreement when presenting a debated interpretation. Give historical identifications their historical context and do not generalize them to present-day people or communities.
- Do not name commentary authors in the explanations. Write in one voice of your own, with no Arabic script, em/en dashes, or semicolons. Transliteration is fine and often the clearest way to give a term.
- Phrase labels must be exact, consecutive pieces of the reader's English translation, covering every word once and in order.

## Length under `sense-v1` (chapters 2 to 43)

- Each phrase explanation must be **45–85 words** in **one paragraph**, counted separately. The translation label does not count.
- Split at meaningful internal boundaries when a verse contains distinct components, even if the full verse is also a coherent sentence. For example, keep a statement of praise separate from its appositional description of Allah, and keep an invocation separate from the divine attributes that follow it.
- Do not split merely to increase the number of entries. A short verse may have one unit when no meaningful internal boundary exists.

## Length under `tabari-v2` (al-Fātiḥa, and new chapters)

Length is **derived from the source, not chosen**. Each explanation is a
beginner's summary of what Tafsīr al-Ṭabarī says about that piece of the verse,
and it is as long as what he says deserves.

- Each phrase names the piece of the verse's Arabic it explains, in `ar`. The spans must be exact, consecutive pieces of `ayah_ar`, covering every word once and in order, mirroring the rule for the English labels. This is what the source is measured against.
- Phrase boundaries follow Ṭabarī's own units. Where he changes topic inside a verse, that is a phrase boundary, as long as the English label rule can still be met. `python3 tools/pairs/digest.py SURAH VERSE` prints his units and where each one falls on the verse.
- `assemble.py` measures the passage and prints a target and an accepted range for every phrase. Write to the target. There is a floor of 40 words and **no ceiling**: a phrase carrying nine opinions gets the room to report them.
- Short means the material was not used, and long means padding. Both fail the gate. Neither is a matter of taste.
- Several paragraphs are allowed and expected once an explanation runs long. Break at the joints of the argument, not to decorate.
- Summarise the substance: the meaning, the disagreement and its sides, the verdict preferred and why, and any context a beginner needs. Skip the chains of transmitters, the poetry quoted as linguistic evidence, and the translator's editorial footnotes. They are what the measurement discounts, and they are not what a reader is owed.

## Write and validate

Read the source first, with `python3 tools/pairs/digest.py SURAH VERSE --full`, then write explanations directly in `authored/NNN.json`, then validate and regenerate the reader's data:

```sh
python3 tools/pairs/digest.py SURAH VERSE --full   # what the source holds, per phrase
python3 tools/pairs/assemble.py --check
python3 tools/pairs/assemble.py
```

Run the tests against the regenerated data:

```sh
python3 -m unittest discover -s tools/pairs/tests
```

Automated validation checks structure, translation coverage, Arabic-span coverage, formatting, and that each explanation is as long as its material deserves under the policy its chapter declares.
