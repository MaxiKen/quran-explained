# Quran Explained — Tafsir Production Prompt

**Revision:** 2026-10-07

**Status:** Expanded original al-Fātiḥah commentary prepared for review. Do not start another surah before review.

## Mission

Write an accessible modern-English explanation of the Qur’an for the Quran Explained app, verse by verse and aligned to the app’s exact translation. For this project, treat `tafsir-al-tabari/NNN.txt` as an **evidence archive**—a collection of reports, Qur’anic cross-references, linguistic observations, grammar, readings, and poetry to evaluate and synthesize. Do not make al-Tabari’s own interpretive verdict the authority or narrative center of the commentary.

The desired editorial method is **informed by the explanatory structure associated with Ibn Kathir, not a reproduction of Ibn Kathir’s writing or content**. Use the method-level elements below while grounding every substantive claim in the supplied evidence file. Do not quote, paraphrase, cite, or import Ibn Kathir’s tafsir or any other outside tafsir. Do not imitate distinctive wording.

The English rendering in [`SafhaJournal/tafsir-ibn-kathir-english`](https://github.com/SafhaJournal/tafsir-ibn-kathir-english) was inspected only as an **organizational reference** (for example, its surah-level files and individually keyed verse blocks). It is not evidence or an authority for interpretation. Do not copy, paraphrase, cite, or rely on its substantive commentary.

## Method model: Ibn Kathir-inspired, modern, and source-bounded

Use these elements as a flexible method, not as a rigid template. Let the evidence available for each verse set the proportions.

1. **Explain meaning before evidence.** Every verse commentary must begin with the Markdown subheading `### Meaning`. First explain the verse in clear, passage-aware English—its role in the surah, what it says, and how it develops what came before or prepares for what follows. Do not open with a hadith, report, Qur’anic parallel, poem, or citation. Present supporting evidence only after the reader has a concise account of the verse’s meaning.
2. **Let the Qur’an illuminate the Qur’an.** Where the supplied source adduces relevant Qur’anic passages, explain the connection in plain English: what the parallel passage clarifies, confirms, contrasts, or adds. Cite it as `[Q surah:verse]`. Do not stack references without explaining their relevance or introduce unrelated cross-references.
3. **Give transmitted Prophetic reports real interpretive weight.** When present, translate the report’s relevant wording, give its setting or narrative detail if supplied, and explain how it bears on the verse. Identify the Companion or other attributed authority and the named collection/location only when the source text or its bibliographic apparatus supplies one.
4. **Bring in Companion and early-exegete explanations.** Name the attributed authorities and preserve meaningful differences among their explanations. Compare what each report illuminates; do not collapse distinct statements into one view or present every report as established fact.
5. **Compare evidence before synthesizing.** Consider agreements, disagreements, variant wording, and transmission routes that distinguish reports. Keep editorial bibliography separate from the Arabic source’s transmitted statements. Never invent a hadith grade or source.
6. **Use language in service of the explanation.** Explain a key Arabic term, reading, grammatical construction, or poem when it clarifies the evidence or resolves a real interpretive question. Keep word studies concise and subordinate to the reports, Qur’anic context, and passage-level meaning. Do not let etymology or grammar crowd out substantial narrative or transmitted material.
7. **Close with a grounded synthesis.** State what the evidence together supports and how it shapes the verse’s place in the surah. Distinguish a report’s wording from the writer’s conclusion. Do not add generic devotional application or claims unsupported by the file.

Use natural paragraphs and an engaging explanatory flow. Every verse must have **at least two meaningful `###` subheadings**: begin with `### Meaning`, then add one or more headings for the evidence or interpretive questions that actually deserve attention. Scale the number and depth of sections to the verse and the available evidence; do not force every verse into the same outline or use headings as padding. The result should feel like a coherent commentary, not a chain of lexical notes, report summaries, or checklist headings.

## Source and citation policy

Use only the matching `tafsir-al-tabari/NNN.txt` file for tafsir-related evidence. This constraint limits the evidence base; it does **not** require citations to al-Tabari as the interpretive authority.

- Cite Qur’anic passages in surah:verse form, for example `[Q 4:69]` or `[Q 10:22]`.
- Cite reports by their underlying attributed authority and any transmission route given in the source, for example `[Report: Ibn ʿAbbās via al-Ḍaḥḥāk]`. For a Prophetic report, identify its Companion narrator and use a form such as `[Hadith: Abū Hurayrah; Ṣaḥīḥ Muslim 1:166]` when supported.
- A named collection and hadith identifier/page location may be included only when the supplied text or its bibliographic apparatus explicitly provides it. Editorial notes may help locate a collection; they are not al-Tabari’s statements. Do not attribute their evaluations or hadith grades to him, and do not invent an identifier, grade, route, or collection.
- If no external collection is identified, cite the named authority and route actually supplied. Use “attributed to” where the report’s status needs to be clear.
- Cite poetry by the named poet when the source names one. If it does not, call it an unattributed Arabic line; never guess an attribution.
- Local report numbers in the Arabic file are research/navigation aids only. Do not expose them as citations. Never use `[al-Tabari, ...]`, a Tabari report number, or an unnumbered Tabari section as the source for an interpretation.
- Do not consult or cite other tafsirs, websites, modern scholarship, or remembered historical, legal, theological, or linguistic claims. The fetched English Ibn Kathir rendering is the sole structural-reference exception; its commentary is not evidence. Do not import Ibn Kathir’s substantive content while using his method as an editorial model.

## Style and evidence

- **Reader:** General audience; modern, clear, flowing English.
- **Arabic terms:** Explain important terms with transliteration and an English gloss when they matter. Do not turn every sentence into a word-by-word gloss.
- **Evidence:** Translate or quote short, relevant report wording and compare it with other evidence. Use narrative details and context when present. Make clear who is speaking and whether a statement is a Prophetic report, a Companion/Successor attribution, a Qur’anic parallel, or poetry.
- **Balance:** Give space to the source’s substantive reports, stories, Qur’anic parallels, and disagreements. Use linguistic discussion as support, not as the default focus. Summarize repetitive routes, but do not omit materially different views.
- **Length:** Each verse commentary must contain **400–1200 words**, excluding the structural heading, internal `###` subheadings, exact app-translation blockquote, and inline citation labels. Scale length to the amount and complexity of evidence. Four hundred words is a minimum, not a target; 1200 is a firm ceiling. Never pad or fabricate content to meet the range.
- **No unsupported grading:** Do not call a hadith authentic, weak, fabricated, or historical unless a supplied source explicitly supports that description and the task authorizes its use. In this project, do not reproduce grades from editorial notes.

## Verse alignment and exact app translations

Chapter data is in `data/chapter_NNN.js`. Each verse has an Arabic text (`ayah_ar`) and an existing English translation (`ayah_en`). For each verse:

1. Use the exact `ayah_en` wording as the alignment anchor.
2. Put that exact translation immediately under the Markdown verse heading as a one-line blockquote: `> <exact app translation>`.
3. Do not alter, replace, paraphrase, or repeat the full verse translation. Quotations from transmitted reports and glosses of individual Arabic terms are evidence, not competing translations.
4. Preserve the blockquote in JSON for editorial review. The app displays its own translation separately and strips the leading blockquote before rendering or speech.
5. Preserve existing chapter files, Quran text, translation, audio, and verse groupings.

## Paired Markdown and JSON deliverables

The rich Markdown is canonical; generate the app payload from it with the deterministic builder. Do not maintain separate hand-edited copies.

- Markdown: `data/tafsir_markdown/tafsir_NNN.md`
- JSON: `data/tafsir_NNN.json`
- Builder/validator: `scripts/build_tafsir_json.py`

Use one structural heading per verse, exactly `## SURAH:VERSE`. The verse body starts with the exact app-translation blockquote, then `### Meaning` as the first commentary subheading, followed by at least one more meaningful `###` subheading. JSON stores each complete body—including the blockquote, Markdown, and citations—but not the structural verse heading. Preserve all line breaks and rich formatting. Include exactly one entry for every verse in the corresponding chapter file, in order. An introduction is optional and should not be invented by default.

The renderer supports paragraphs, headings, bold, italics, blockquotes, ordered and unordered lists, horizontal rules, inline code, and links. Keep formatting purposeful; do not use raw HTML, complex tables, footnote extensions, or unsupported syntax.

## Scope and completion checks

**Current scope: Surah 1 (al-Fātiḥah) only.** Replace the previous Chapter 1 prose entirely with a fresh, source-led rewrite that follows the method model above. Do not begin another surah until the user explicitly reviews and approves this sample or changes the scope.

Before presenting a chapter:

1. Confirm verse count and exact translations from `data/chapter_NNN.js`.
2. Read all substantively relevant material in the matching Arabic evidence file, including adjacent sections when an argument spans verses. Consider reports, Qur’anic parallels, narrative context, variants, grammar, readings, and poetry; group only genuinely repetitive material.
3. Check that each verse begins with a meaning-first explanation before any supporting report, hadith, Qur’anic parallel, poem, or citation; ensure the evidence then clarifies that explanation rather than displacing it with word studies.
4. Validate exactly one structural heading and JSON key per expected verse, in order, with exact translation blockquotes, at least two `###` subheadings, and `### Meaning` first.
5. Validate 400–1200 substantive words per verse, a translated or quoted evidence excerpt, and underlying-source/Qur’anic citations without al-Tabari-as-authority citations or local report numbers.
6. Regenerate JSON using `scripts/build_tafsir_json.py`; validate JSON parsing, rich-text preservation, Markdown/JSON parity, and complete coverage.
7. Inspect the final files and diff. Stop at Chapter 1 for user review; do not fabricate content or continue to other chapters.

## Publishing note

`sw.js` currently lists `data/tafsir_002.json` under `RETIRED_PAYLOADS`; Chapter 1 is already active. When another chapter is approved for publication, remove its URL from the retired list and update the cache version if needed. Preserve unrelated service-worker behavior.
