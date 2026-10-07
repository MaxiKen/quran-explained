# Quran Explained — Modern Tafsir Production Prompt

**Revision:** 2026-10-07

**Status:** Fresh al-Fātiḥah pilot in progress; no other surah may be started before the user reviews and approves this sample.

## Mission

Create clear, comprehensive, newly written modern-English Qur’an commentary for the Quran Explained web app. Write verse by verse, aligned to the exact English translation already used by the app. For this pilot, use `tafsir-al-tabari/001.txt` as an **evidence archive**: independently synthesize the underlying reports, Qur’anic cross-references, linguistic and grammatical arguments, and poetry represented there. Do not make al-Tabari’s interpretive conclusions the center of the commentary or present them as the authority for its claims. Do not import another tafsir or unsupported outside material.

## Editorial direction

- **Audience and voice:** Accessible modern English for general readers. Use natural, connected prose. Explain important Arabic terms with transliteration and a plain English gloss on first use (for example, *rabb*—“lord” or “master”). Avoid unexplained technical language, unnecessary Arabic quotations, generic devotional filler, and repetitive summaries.
- **Length:** Each verse commentary must contain **400–1200 words**, excluding its structural heading and the exact leading app-translation blockquote. Count inline citation labels as references, not substantive words. Scale the length to the amount and complexity of the evidence; the minimum is not a target, and the maximum is firm. Do not pad or invent material to meet either limit.
- **Independent analysis:** Treat transmitted explanations as evidence to assess and compare, not as conclusions to repeat. Represent all substantively distinct positions and relevant evidence in the supplied section, including meaningful reports, differences in wording, Qur’anic cross-references, Arabic usage, grammar, and poetry. Repeated routes carrying the same point may be summarized together, but do not omit a meaningful variant. Explain what each item supports and where it does not settle the question. Draw only conclusions supported by the supplied evidence.
- **Quoted evidence:** Quote or closely translate concise, relevant evidence, then analyze it. Make clear whether a statement is a Prophetic hadith, a report attributed to a Companion or later authority, a Qur’anic cross-reference, or poetry. Preserve uncertainty and disagreement; do not present every transmitted report as established fact.
- **Arabic:** Do not reproduce the full Arabic verse. When a key term matters, give its transliteration and English sense. Keep any Arabic quotations short and only where needed.

## Evidence and citation policy

Use only the corresponding Arabic file in `tafsir-al-tabari/` for tafsir-related evidence. The corpus is the evidence archive, not a citation target for the interpretation.

- Cite Qur’anic passages in **surah:verse** form, such as `[Q 4:69]` or `[Q 10:22]`.
- For a report, cite its underlying attributed authority and the transmission route available in the Arabic text, for example `[Report: Ibn ʿAbbās via al-Ḍaḥḥāk]`. For a Prophetic report, use a label such as `[Hadith: Abū Hurayrah; Ṣaḥīḥ Muslim 1:166]`. Cite a named collection and identifier/location only when the supplied text or its bibliographic apparatus actually provides it.
- Local report numbers in the Arabic file are navigation aids only. Do **not** present them as visible citations, and do not use references such as `[al-Tabari, 1:5, report 171]` or `[al-Tabari, 1:5]` as the source for an interpretation.
- Bracketed editorial notes such as `[[...]]` are not statements by al-Tabari. Their bibliographic details may be used cautiously to identify a report’s collection or location, but do not attribute editorial judgments or hadith grades to al-Tabari, and do not invent a source, identifier, chain detail, or authenticity grade.
- Where no collection or identifier is provided, cite only the named authority and transmission route actually preserved; do not guess. In prose, say a report is “attributed to” its named source when appropriate.
- Attribute poetry to the named poet if supplied. If the Arabic source does not name the poet, describe it as an unattributed Arabic verse rather than inventing an attribution.
- Do not cite or rely on outside tafsirs, websites, modern scholarship, or remembered claims. Use Qur’anic cross-references relevant to the evidence in the supplied source; do not use a cross-reference to introduce unrelated claims.

## Verse alignment and translations

The app’s chapter files are `data/chapter_NNN.js`. Each verse contains an Arabic text (`ayah_ar`) and the exact English translation already used by the app (`ayah_en`). For every verse:

1. Read the exact `ayah_en` translation and use it as the alignment anchor.
2. In Markdown, put that exact text immediately after the verse heading as a one-line blockquote, for example `> <exact app translation>`.
3. Do not edit, replace, paraphrase, or duplicate the verse translation. Quotations from reports and glosses of individual Arabic terms are evidence, not alternate translations of the whole verse.
4. Keep the translation blockquote in the JSON value. The app displays its own translation separately and strips the leading blockquote from the commentary before display or speech.

Preserve the app’s existing chapter files and thematic groupings. Commentary is keyed to individual verses.

## Markdown and JSON deliverables

For each surah, the rich Markdown manuscript is the source of truth; generate the app JSON deterministically from it. Do not maintain two independently edited versions.

- Markdown: `data/tafsir_markdown/tafsir_NNN.md`
- JSON: `data/tafsir_NNN.json`
- Builder/validator: `scripts/build_tafsir_json.py`

Use one structural verse heading per entry, exactly `## SURAH:VERSE`. The heading is excluded from the JSON value. The body must start with the exact app-translation blockquote, followed by rich-text commentary. Preserve Markdown formatting, line breaks, citations, and the blockquote in JSON.

The JSON expects an optional `intro` string and a `verses` object whose keys are verse numbers as strings. Each value is the complete Markdown body between structural verse headings, excluding the heading. Include exactly one Markdown section and JSON key for every verse in the corresponding chapter file, in order. Do not create an introduction unless requested.

The renderer supports paragraphs, headings, bold, italics, blockquotes, ordered and unordered lists, horizontal rules, inline code, and links. Use supported formatting purposefully; do not use raw HTML, complex tables, footnote extensions, or unsupported syntax.

## Scope and quality checks

Begin with **Surah 1 (al-Fātiḥah) only**. Replace the rejected Chapter 1 commentary completely with a fresh, independent synthesis. Do not begin another surah until the user explicitly reviews and approves this pilot or changes the scope.

Before completing a pilot:

1. Confirm the chapter number, verse count, and exact translations from `data/chapter_NNN.js`.
2. Read all relevant material for each verse in the matching Arabic evidence file, using adjacent sections where a passage spans verses. Consider all substantive evidence, while grouping only genuinely repetitive routes.
3. Confirm every expected verse heading and JSON key appears exactly once, in order, with none missing or extra.
4. Confirm each Markdown entry begins with the exact matching translation blockquote and has **400–1200 substantive commentary words** after it.
5. Confirm each verse includes a short translated or quoted piece of evidence, important Arabic terms are glossed in transliteration and English, and meaningful reports, disagreements, grammar, poetry, and Qur’anic cross-references are compared where relevant.
6. Check citations identify the underlying Qur’anic verse, attributed report/hadith source and supplied route, or named poet—not al-Tabari as the interpretive authority. Do not expose local report numbers or invent sources, identifiers, or hadith grades.
7. Regenerate JSON with `scripts/build_tafsir_json.py`; validate JSON parsing, exact translation alignment, complete coverage, and Markdown synchronization.
8. Inspect both files and the diff. Record genuine gaps for review rather than importing outside claims or padding.

## Publishing note

`sw.js` currently lists `data/tafsir_001.json` and `data/tafsir_002.json` under `RETIRED_PAYLOADS`. When a chapter is approved for publication, remove its URL from that retired list and update the service-worker cache version as needed so stale cached commentary is not served or immediately purged. Preserve the existing Quran text, translations, audio, and unrelated app features.
