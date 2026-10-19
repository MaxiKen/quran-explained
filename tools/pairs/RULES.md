# Phrase-by-phrase authoring laws

**Binding across every surah.** Read this file before authoring, editing, reviewing, or publishing any phrase explanations. These rules apply to all `tools/pairs/authored/NNN.json` files, not just Surah 1.

## 1. Read the complete source first

For every verse, before drafting or changing any phrase explanation, read the reader's English translation and the **entire commentary mapped to that verse** in `data/tafsir_NNN.json`, including continuation text. Digest its explanation, evidence, uncertainty, and disagreement before choosing boundaries or writing. Do not rely on searches, summaries, adjacent verses, or an earlier draft. This applies to every edit, even one word. Work in smaller batches rather than skimming long commentaries. If no commentary is mapped, record that and do not invent evidence.

## 2. Dense splitting is mandatory

The aim is close reading. Do not copy the former coarse practice of only two or three broad chunks. Split every verse into short, useful, consecutive sense units.

- **Hard minimum:** one phrase for every three translation words, rounded up. Calculate `ceil(number of translation words / 3)`. For example, a 9-word verse needs at least 3 phrases; a 17-word verse needs at least 6. Any verse of 3 or more words must have at least 2 phrases. Authored files adopting this rule must set `"split_policy": "dense-v1"`; the assembler enforces this minimum mechanically.
- Aim for still more than the minimum when the wording contains additional meaningful units. Most phrases should be 1–3 words. A single word is welcome where it carries a distinct meaning and can be explained clearly.
- Do not inflate counts by isolating articles, prepositions, pronouns, or fragments with no useful meaning. Keep words together when they form an indivisible name or expression, or when a split would be misleading or awkward. If a meaningful split is not possible, use the smallest natural phrase and explain the exception during review. Never create nonsense to satisfy a number.
- Split clauses, contrasts, repeated words, and meaningful parts of a phrase whenever the grammar allows. Preserve the verse's sequence and meaning; do not impose identical boundaries on similar verses.
- Phrase pieces must cover the reader's translation exactly, once, and in order. Do not omit, repeat, rearrange, or paraphrase translation words. Punctuation may be placed at a boundary.
- Read the full sequence aloud. If it sounds like a chopped word list, repair the boundaries while retaining the highest natural density. If any unit remains an oversized block, split it further.

The density law applies when a surah is first authored or revised, whether or not it is Surah 1. Existing chapters without `dense-v1` are legacy and are not silently treated as examples; when revising one, bring its verses into compliance and set the marker. Do not lower the rule just to pass old content.

## 3. Explain the words simply

- **Each phrase explanation must be 30–85 words**, counted separately for that phrase. The phrase label and neighboring explanations do not count.
- Use simple, direct English and clear sentence structure. Explain what the phrase means in context. **Define or explain individual words when that is needed to understand them** (especially titles, key religious terms, images, or words with a relevant range of meanings); do not add dictionary definitions where they do not help.
- Summarize relevant evidence from the complete commentary. Do not merely restate the translation, pad with generic devotion, repeat nearby material, or add outside claims. Preserve uncertainty and disagreement rather than presenting a debated reading as certain.
- Write in the reader's voice, not as a report about a commentary author. Do not name al-Ṭabarī or another author; avoid repeated frames such as “the commentator says.” Present supported explanations directly. State distinct readings naturally when they matter.
- Vary openings and sentence patterns. Avoid predictable templates, while keeping clarity and accuracy first.
- For sensitive historical identifications, state the historical context and scope. Do not turn an interpretation about earlier communities into a judgment about present-day people.
- One paragraph per phrase. No Arabic script, em/en dashes, or semicolons in authored prose. Structural and formatting constraints are checked mechanically.

## 4. Validate and review

```sh
python3 tools/pairs/assemble.py --check
python3 tools/pairs/assemble.py
python3 tools/pairs/show.py SURAH [VERSE]
cd tools/pairs && python3 -m unittest discover -s tests
```

The assembler checks exact translation coverage and order, full coverage, paragraph structure, formatting, the 30–85 word limit, and (for `dense-v1`) minimum split count. Passing checks does not prove the source was read, evidence is accurate, English is simple, or boundaries are natural. Human review must verify all of those. Stop and flag ambiguity rather than guess.
