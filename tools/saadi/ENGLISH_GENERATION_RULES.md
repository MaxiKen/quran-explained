# Tafsir as-Sa‘di English Generation and Review Rules

This document is the binding brief for translating the Arabic Tafsir as-Sa‘di material in `data/saadi_NNN.json` into the reader’s **Simple** English verse-by-verse content. Apply it to every verse, not just to a chapter sample. A generated verse is not ready to publish until it passes the mechanical checks below and has been reviewed by a competent human reader against the Arabic source.

## 1. Purpose and source of truth

- Translate the supplied Arabic Tafsir as-Sa‘di for that exact verse into clear, simple English.
- Use the verse’s English translation in `data/chapter_NNN.js` (`ayah_en`) as the project’s terminology and phrasing reference. When the verse translation uses a clear English term for a Qur’anic concept or name, use that term consistently in the explanation unless doing so would misrepresent what as-Sa‘di says.
- The English verse translation is a terminology guide, not a substitute for the tafsir source. The Arabic tafsir is the source of meaning and detail. Do not derive new interpretation from the English verse translation alone.
- Preserve the Arabic input verbatim in the source field. Write the English explanation into a separate field, such as `explanation_en`; never replace or edit the Arabic text during translation.
- The source text is Tafsir as-Sa‘di, not an invitation to write a general reflection, sermon, independent commentary, or ruling.

## 2. Binding per-verse length rule

Each English explanation must contain **at least twice as many words as the corresponding Arabic source explanation**. This is a minimum for each verse individually, not an average, chapter total, or target that may be offset by longer neighbouring verses.

### Counting convention

1. Read the source value at `data/saadi_NNN.json` → `verses` → verse number → `explanation`.
2. Count Arabic words by splitting that source string on whitespace. A token separated by whitespace counts as one word; punctuation attached to a token does not alter the count. Do not count JSON keys, verse numbers, headings, the English verse translation, or metadata.
3. Count English words by splitting `explanation_en` on whitespace. A whitespace-delimited token counts as one word. Do not count the verse translation, heading, attribution, or JSON metadata.
4. The rule is: `English word count >= 2 * Arabic source word count` for that verse.
5. Keep paragraphs inside the one `explanation_en` string, separated by a blank line. Paragraph breaks do not change the count.

Do not game the count with repeated phrases, redundant restatements, long quotations, lists of synonyms, or generic religious filler. Reach the required length by translating all of the source’s meaning and by making its relationships understandable to a reader who is new to the subject. Explain key terms, pronouns, implications, contrasts, and cause-and-effect only where they are supported by the Arabic source. If faithful, useful English cannot meet the minimum for a particular verse, flag it for human review rather than padding or inventing content.

## 3. Translation and explanation quality

- Use plain, contemporary English that a general reader can follow. Prefer common words, short sentences, active voice, and concrete explanations. Define a necessary technical term in ordinary English the first time it appears.
- Translate all meaningful material in the supplied source: definitions, qualifications, contrasts, stated reasons, implications, and any interpretation explicitly included by as-Sa‘di. Do not silently omit a difficult point.
- Preserve the source’s degree of certainty. Keep distinctions such as “means,” “indicates,” “may,” “it is said,” and “the more likely meaning” distinct. Do not turn a possibility into a fact or a preference into consensus.
- Keep the scope of claims faithful. Do not universalize a statement that is qualified, add a legal ruling, claim scholarly agreement, or infer a historical circumstance unless the source says so.
- Explain references sufficiently for comprehension, but do not introduce outside hadith, historical reports, causes of revelation, dates, names, theological claims, or cross-references absent from the supplied source. If context is needed but not provided, flag it for review.
- Add no new religious instruction, advice to the reader, personal opinion, devotional appeal, or claim about present-day groups. Do not address the reader as “you” unless the source itself does so.
- Do not present the translation as a scholarly verification or as a replacement for the Arabic source. Do not fabricate missing content. An empty or unavailable source verse must remain flagged as unavailable; it must not be completed from memory.

## 4. Terminology aligned with the project translation

Before translating a verse, read its exact `ayah_en` in `data/chapter_NNN.js`.

- Reuse the project’s English wording for names, titles, and concepts when it accurately expresses the same concept in the tafsir.
- Preserve the project’s established spelling and capitalization. In particular, use “Allah” where the project’s verse translation uses “Allah”; do not alternate casually with “God.”
- Do not force a phrase from `ayah_en` into the explanation when the Arabic tafsir is discussing a different nuance. Accuracy to the tafsir takes precedence; note a genuine terminology mismatch for review.
- Use one English rendering for the same Arabic term throughout a surah unless the context clearly requires a different sense. Maintain a chapter glossary of any term whose translation is not already fixed by `ayah_en`.
- Do not put Arabic script in the English explanation. Transliteration may be used sparingly when a term is essential and has no clear English equivalent; explain it in plain English at first use and spell it consistently.

## 5. Output format

For every verse, retain the existing verse key and Arabic explanation and add the English translation separately. The intended per-verse object is:

```json
{
  "explanation": "Original Arabic Tafsir as-Sa‘di text, unchanged.",
  "explanation_en": "Simple English translation and explanation.\n\nA further paragraph where the source has another connected point."
}
```

- `explanation_en` must be a plain string, not HTML or Markdown.
- Use blank lines (`\n\n`) between meaningful paragraphs. Do not put literal line breaks inside a paragraph.
- Do not add a phrase-by-phrase structure, English paraphrase of the Qur’an in place of tafsir, unsupported footnotes, or source content from another commentary.
- Keep JSON valid UTF-8 and escape strings with a JSON serializer. Preserve the surrounding dataset’s schema and numeric verse keys.
- Do not publish a partial chapter as if complete. Record missing, ambiguous, or low-confidence verses explicitly in a separate review report.

## 6. Mandatory automated gates

The generator/publisher must reject the batch unless all these checks pass:

1. **Coverage:** the generated verse keys exactly match the source chapter’s verse keys. No missing, extra, or duplicate verse keys.
2. **Source preservation:** every original Arabic `explanation` is byte-for-byte unchanged from its input. English generation may add fields but may not alter source material.
3. **English present:** every non-empty Arabic source explanation has a non-empty `explanation_en`; no English field is whitespace-only.
4. **Per-verse length:** compute both counts using the whitespace convention in section 2 and reject any verse below the 2:1 minimum. Report the verse number, Arabic count, English count, and required minimum for every failure.
5. **No padding pattern:** flag identical repeated sentences, excessive repeated phrases, and unexplained boilerplate across verses for human inspection. These flags cannot by themselves prove quality.
6. **Language/script:** flag Arabic-script characters in `explanation_en`, malformed JSON, raw HTML, and unexpected markup. Transliteration exceptions must be reviewed and documented.
7. **Translation alignment:** load the exact `ayah_en` for each verse and flag inconsistent renderings of terms in the chapter glossary. This is a review flag, not permission to alter the tafsir’s meaning to match the translation.
8. **No unreviewed output:** generated text is a draft until human review is recorded for every verse. A successful word-count check is not evidence of translation accuracy.

At minimum, the validation report must include chapter number, verse number, Arabic count, English count, required minimum, ratio, and review status. It must be possible to rerun the checks deterministically against the committed source and generated files.

## 7. Required generation prompt

Use this instruction for each verse or batch of verses:

> Translate the supplied Arabic Tafsir as-Sa‘di explanation into simple, natural English for a general reader. Use the exact project `ayah_en` text as a terminology and spelling reference, while treating the Arabic tafsir as the authority for the explanation. Preserve every supported meaning, qualification, contrast, and stated implication. Add only clarifying detail needed to make those source points understandable; do not add outside facts, opinions, rulings, or generic filler. Keep the source’s level of certainty and do not omit difficult material. Write at least twice as many whitespace-delimited words as the supplied Arabic explanation for this verse. Reach that minimum with faithful explanation, never repetition or padding. Return only the requested JSON field `explanation_en`, as plain text with blank lines between logical paragraphs. Do not alter the Arabic source. If the source is empty, unclear, or cannot be expanded to the minimum without invention, return a review flag instead of guessing.

## 8. Human review checklist

A reviewer must compare every generated verse directly with its Arabic source and confirm:

- the full meaning is represented without omission or invented content;
- the wording is simple and understandable, not merely longer;
- certainty, qualifications, scope, and distinctions are preserved;
- terminology follows `ayah_en` where accurate and remains consistent across the surah;
- the minimum length is met without padding;
- any ambiguity or missing context is flagged, not silently resolved.

Record reviewer identity, date, chapter, verses reviewed, and any corrections. Re-run all automated gates after revisions. No verse is publishable until both the automated checks and human review pass.
