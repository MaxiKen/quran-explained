# Quran Explained — Tafsir Production Prompt

**Revision:** 2026-10-07

**Status:** Chapter 1 and Surah 2:1–2:130 were completed on prior review branches. The current batch extends the same fresh, source-bounded rewrite through verses 2:131–2:180, from Abraham’s submission and the change of the prayer direction to the law of retaliation and the bequest; the whole batch 2:131–2:180 is now drafted and validated on the working branch, and the work stops at 2:180, where it waits for review.

## Mission

Write clear, original, modern-English Qur’an commentary for the Quran Explained app, verse by verse, using the exact app translations for alignment. For every fresh rewrite, discard the existing chapter prose and draft the replacement from the matching evidence archive from a blank page; do not edit, paraphrase, or use the previous Markdown/JSON commentary as a starting point.

Use `tafsir-al-tabari/NNN.txt` as the substantive evidence archive: evaluate and synthesize its transmitted reports, Qur’anic parallels, narrative context, readings, language, grammar, and poetry. Do not make al-Tabari’s own verdict the authority or narrative center. Do not cite al-Tabari or expose local report numbers from the archive.

Use the familiar explanatory flow associated with Ibn Kathir only as a high-level method model: explain the verse, bring in relevant Qur’anic passages and transmitted reports, clarify significant differences, and synthesize. The fetched English Ibn Kathir rendering was inspected only as an organizational reference; neither it nor any other tafsir is evidence. Do not copy, paraphrase, cite, or import Ibn Kathir’s substantive interpretations or distinctive wording.

Write only material that genuinely clarifies the verse and fits ordinary tafsir: its meaning and place in the passage, relevant Qur’anic context, supported reports and their settings, meaningful interpretive differences, and brief language notes where useful. Avoid tangents, meta-commentary about the archive or editing process, speculative claims, generic padding, and technical disputes that do not help explain the verse. Do not introduce material from memory or outside sources.

## Method

1. **Meaning before evidence.** Every verse commentary begins with `### **MEANING**`. First explain the verse in its surah context, in plain English. Do not begin with a report, hadith, Qur’anic cross-reference, poem, or citation. Bring in evidence only after the reader understands the verse’s meaning.
2. **Use relevant Qur’anic parallels.** When the evidence archive points to another passage, explain how that passage clarifies or supports the verse. Cite it naturally in the sentence, such as “Qur’an 4:69 identifies the blessed company …”; never leave a bare reference without explaining its relevance.
3. **Use reports carefully.** Translate only relevant wording, explain the report’s setting when supplied, identify the attributed authority and route, and name the collection/location only when the archive or its bibliographic apparatus supplies it. Distinguish Prophetic reports from Companion and Successor explanations. Preserve meaningful differences; do not merge separate accounts or present every report as established fact.
4. **Keep language notes in proportion.** Explain an Arabic term, reading, grammatical point, or poem only when it helps the reader understand the verse or a real interpretive difference. Avoid long lexical digressions.
5. **Synthesize.** Close sections by showing what the evidence supports and how it fits the surah. Do not add devotional applications or theological claims unsupported by the archive.

Use at least two meaningful subheadings per verse. Scale the number and depth of sections to the evidence; do not force every verse into the same outline or use headings as padding.

## Citation style

References must read as part of professional prose, not as editorial tags.

- **Do not put citations in square brackets.** Do not use forms such as `[Q 4:69]`, `[Report: …]`, `[Hadith: …]`, or `[Poem: …]` anywhere in the commentary.
- Cite Qur’anic passages inline as `Qur’an 14:34`, `Qur’an 16:18`, or `Surah 4, verses 66–69`, embedded in a sentence that explains their relevance.
- Cite transmitted material in natural sentences. For example: “A report from Ibn ʿAbbās through al-Ḍaḥḥāk explains …”; “In Ṣaḥīḥ Muslim, Abū Hurayrah’s report through Abū al-Sāʾib recounts …”; or “Labīd’s farewell poem uses the line …”.
- Identify the underlying authority and route supplied by the archive. Include a collection and locator only when explicitly supported there. Do not invent identifiers, chains, collection references, or hadith grades.
- Do not put source notes on separate lines, in footnotes, at paragraph ends, or in a bibliography. Weave each reference beside the claim it supports.
- Cite poems by the named poet when known; otherwise describe the evidence as an unattributed Arabic line. Never guess an attribution.

## Formatting and voice

- **Headings:** Every Markdown heading must be bold and uppercase. Use `# **SURAH 2: AL-BAQARAH**`, `## **2:1**`, and `### **MEANING**`; uppercase and bold every other heading as well.
- **Verse wording:** Whenever all or a meaningful part of the current verse’s English wording is repeated in the commentary, bold that wording. Do not bold the exact app-translation blockquote. If a quoted phrase repeats the verse, format it both bold and italic, for example `***“All praise”***`.
- **Quotations:** Italicize quoted words and passages, including direct quotations from reports, poems, and Qur’anic translations. Use `*“quoted words”*`; use bold italics when the quotation is also wording from the current verse.
- **Prose:** Accessible, accurate, and coherent for a general reader. Use transliteration sparingly and explain important Arabic terms briefly. Keep quotations short and relevant.
- **Length:** Each verse commentary must contain **500–1200 words**, excluding the structural heading, internal subheadings, and exact app-translation blockquote. Count the actual explanation; do not pad to reach the minimum or exceed the maximum.
- Never reproduce hadith grades or claim a report is authentic, weak, fabricated, or historical. Do not attribute editorial notes or assessments to the transmitted authority.

## Verse alignment and translations

Chapter data is in `data/chapter_NNN.js`. For each verse:

1. Use the exact `ayah_en` wording as the alignment anchor.
2. Put that exact translation immediately under the bold structural heading as a one-line Markdown blockquote: `> <exact app translation>`.
3. Do not alter or replace the translation. Do not repeat the complete translation in the commentary. Commentary may discuss or quote a meaningful portion of the verse, following the bolding and italics rules above.
4. Preserve the blockquote in JSON for editorial review. The app displays its own translation separately.
5. Do not modify Qur’anic text, translations, audio, verse groupings, or unrelated app data.

## Markdown and JSON deliverables

The rich Markdown is canonical; generate JSON with the deterministic builder. Do not hand-maintain separate copies.

- Markdown: `data/tafsir_markdown/tafsir_NNN.md`
- JSON: `data/tafsir_NNN.json`
- Builder and validator: `scripts/build_tafsir_json.py`

Use one bold, uppercase structural heading per verse, exactly `## **SURAH:VERSE**`. The body begins with the exact translation blockquote, followed by `### **MEANING**` and at least one other meaningful bold-uppercase subheading. JSON stores each complete body—including the translation blockquote and rich formatting—but not the structural verse heading. Include exactly one entry for every verse in the declared range, in order. The builder supports partial coverage with `--chapter N --through M`; for this assignment the JSON must contain verses 1–180, with new material at 2:131–2:180. An introduction is optional and should not be invented by default.

Use supported Markdown only: paragraphs, headings, bold, italics, blockquotes, lists, inline code, and links. Do not use raw HTML, tables, footnote syntax, or unsupported formatting.

## Scope and completion checks

**Current scope: Surah 2 (al-Baqarah), verses 2:131–2:180 only.** Draft these fifty commentaries from a blank page using `tafsir-al-tabari/002.txt` and the exact translations in `data/chapter_002.js`. Do not draft verse 2:181 or any later verse. Do not start another surah before the user reviews this range. Preserve Chapter 1 and the already-reviewed 2:1–2:130 commentary unchanged.

Before presenting this range:

1. Read the substantively relevant material in the Arabic evidence file, including adjacent sections when arguments span verses.
2. Confirm the exact translations for 2:131–2:180 from `data/chapter_002.js` and use no later verse.
3. Ensure each verse explains meaning before presenting supporting evidence, uses only relevant material, and has at least two bold-uppercase subheadings.
4. Confirm that repeated wording from the current verse is bold, all quoted words are italicized, and every reference is naturally woven into sentence flow with no square-bracket citations or detached reference lines.
5. Validate 500–1200 words per verse, the translated/quoted source evidence, underlying attributions and routes, exact alignment, and absence of local report numbers or al-Tabari-as-authority citations.
6. Generate the partial JSON with `python3 scripts/build_tafsir_json.py --chapter 2 --through 180`; validate JSON parsing, Markdown/JSON synchronization, formatting, and coverage through verse 2:180.
7. Inspect the final diff. Stop at verse 2:180 for review; do not fabricate content or continue to verse 2:181 or another chapter.
