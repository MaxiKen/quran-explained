# Quran Explained — Modern Tafsir Production Prompt

**Revision:** 2026-10-07

**Status:** Draft reflecting the answers received; Al-Fatihah pilot is the proposed default before scaling.

## Mission

Create a clear, comprehensive, newly written modern-English explanation of the Qur’an for the Quran Explained web app. Write the commentary verse by verse, aligned to the English translation already used by the app. Use **Tafsir al-Tabari alone** as the source for tafsir content.

This is a modern explanatory synthesis based on al-Tabari, not a claim to reproduce his exact words or to replace qualified scholarship. Keep that attribution transparent.

## Agreed editorial direction

- **Language and audience:** Accessible modern English for general readers. Use an Arabic term or transliteration when it adds meaning, and explain it briefly on first use. Avoid unnecessary technical vocabulary and long Arabic quotations.
- **Depth:** Extended enough to explain the verse and relevant material in al-Tabari, but clear and focused. Let the source determine the length. There is **no fixed word minimum, citation-count minimum, or requirement to pad** a short explanation.
- **Approach:** Write a fresh synthesis of relevant material in al-Tabari, rather than a literal translation or a catalogue of every transmitted report. Simple connective wording is allowed for readability; it must not introduce a new interpretation or factual claim.
- **Form:** Use natural, connected prose. Do not force every verse into the same headings or checklist. Use a short paragraph break when it improves clarity; avoid generic reflections, repetitive summaries, tables, and unnecessary lists.
- **Reports:** Summarize significant transmitted reports and preserve meaningful differences of interpretation, including al-Tabari’s stated preference and reasons when he gives them. Condense long chains of transmission while retaining names or report details that matter to understanding. Describe a report as something al-Tabari transmits; do not present it as established fact without support in the source. Never invent a hadith authenticity grade or other source claim.

## Source material and verse alignment

### Sole tafsir source

Use only the matching file in `tafsir-al-tabari/`, named `NNN.txt` (for example, `001.txt` for al-Fātiḥah). Each file identifies a surah and contains verse sections headed `## SURAH:VERSE`.

- Read the section for the verse being explained. Read adjacent sections when al-Tabari discusses a passage across multiple verses, and make the verse-level connection clear without duplicating the same discussion in every entry.
- The Arabic corpus includes transmitted reports and bracketed edition/editor notes such as `[[...]]`. Do not misattribute an editor’s note to al-Tabari. Use such a note only when it genuinely clarifies the source; identify its editorial nature if it is important to include.
- Do not consult or cite other tafsirs, outside commentaries, web sources, or remembered historical claims. The removed multi-tafsir source folders are not part of this task.
- Use Qur’anic text and cross-references only as they appear in, or are needed to understand, al-Tabari’s discussion. Do not add unsupported modern historical, legal, theological, or linguistic claims.

### App translation to explain

The app’s chapter files are `data/chapter_NNN.js`. Each verse has an Arabic text (`ayah_ar`) and an existing English translation (`ayah_en`). For each verse:

1. Read and use that exact `ayah_en` translation as the alignment anchor.
2. Write commentary that explains the meaning of that verse as represented by the app’s translation, checked against the Arabic source discussion in al-Tabari.
3. Do not replace, edit, or create a competing English translation. In the authoring Markdown, place the exact `ayah_en` text immediately after the verse heading as a one-line Markdown blockquote, for example `> <exact app translation>`. This makes the source translation and its matching commentary easy to review together.
4. Keep that leading translation blockquote in the JSON value as well. The app displays the translation separately and its `stripLeadingVerseQuote()` function removes the initial blockquote before rendering/speaking the commentary, preventing a duplicate on screen. Do not repeat the Arabic verse or add another translation elsewhere in the entry.

The chapter data also groups verses into existing thematic units. Preserve those chapter files and groupings; commentary is keyed to individual verse numbers.

## Editorial rules

1. **Faithfulness:** Keep every substantive point traceable to al-Tabari. Distinguish al-Tabari’s own explanation or preference from opinions and reports he transmits.
2. **Meaningful disagreement:** Where al-Tabari presents different readings or explanations, summarize the relevant alternatives and his conclusion or reasoning when supplied. Do not flatten them into a single claim or imply that he endorses every report.
3. **Careful report language:** Use wording such as “Al-Tabari reports…” or “One report transmitted by al-Tabari says…” where needed. Do not independently label a report authentic, weak, fabricated, or historical unless the source itself clearly does so.
4. **Useful detail:** Retain names, events, lexical points, grammatical observations, and qualifications when they materially explain the verse. Condense repetitive isnāds and peripheral digressions; do not copy long passages verbatim.
5. **Modern readability:** Prefer direct, coherent prose and explain indispensable Arabic terms in plain language. “Modern” describes the language and presentation, not permission to import modern opinions.
6. **No padding:** Do not repeat the same point to reach a length target, add generic devotional applications, or fabricate context when the source is brief.
7. **Source attribution:** Identify the work as a modern explanation based on *Jāmiʿ al-Bayān* by al-Tabari. Attribute transmitted views in the prose when attribution helps the reader. Do not add arbitrary citation tags or unsupported page/report references.

## Paired Markdown and JSON deliverables

For each completed surah, create **both** an editorial Markdown file and the JSON payload consumed by the app:

- **Canonical rich-text source:** `data/tafsir_markdown/tafsir_NNN.md` (for example, `data/tafsir_markdown/tafsir_001.md`).
- **App payload:** `data/tafsir_NNN.json` (for example, `data/tafsir_001.json`).

The Markdown is the source of truth. Generate or update the JSON from it with a deterministic converter; do not maintain two independently edited versions. If no converter exists, add a small conversion/validation script under `scripts/` and use it for every batch. Preserve all Markdown formatting in the JSON strings.

### Markdown authoring format

Use one structural verse heading per entry, exactly `## SURAH:VERSE`. Put the exact app translation in a leading blockquote, then write the rich-text commentary beneath it. The structural `## N:M` heading is for the Markdown manuscript and must not be copied into that verse’s JSON value.

```markdown
# Surah 1: Al-Fatihah

## 1:1
> In the Name of Allah—the Most Compassionate, Most Merciful

Al-Tabari explains **the meaning of the opening phrase**. When helpful, explain an Arabic term such as *raḥmah* in plain English and show how al-Tabari connects it to the verse.

## 1:2
> All praise is for Allah—Lord of all worlds

Write the matching explanation here, using paragraphs and Markdown emphasis where useful.
```

Rich Markdown is required; do not reduce the commentary to unformatted plain text. The current renderer in `js/app.js` supports paragraphs, headings, bold, italics, blockquotes, ordered and unordered lists, horizontal rules, inline code, and links. Use those features sparingly and purposefully while keeping the prose natural. Do not use raw HTML, complex tables, footnote extensions, or other syntax unless the app renderer is first updated to support it. A bold or italic phrase, an optional short heading, or a short list may organize genuinely distinct points, but there is no mandatory heading template.

### JSON mapping

The app loads each `data/tafsir_NNN.json` file. It expects an optional `intro` string and a `verses` object whose keys are verse numbers as strings. Each `verses` value must be the complete Markdown body between that verse’s structural heading and the next verse heading, **including** the leading English-translation blockquote and all rich-text markup, but **excluding** the structural `## N:M` heading.

Example:

```json
{
  "verses": {
    "1": "> In the Name of Allah—the Most Compassionate, Most Merciful\n\nAl-Tabari explains **the meaning of the opening phrase**.\n",
    "2": "> All praise is for Allah—Lord of all worlds\n\nWrite the matching explanation here."
  }
}
```

- Create one pair of files per surah: Markdown source `tafsir_001.md` through `tafsir_114.md`, and JSON payload `tafsir_001.json` through `tafsir_114.json`.
- Include exactly one `## N:M` Markdown section and one JSON verse key for every verse in the corresponding `data/chapter_NNN.js`; do not omit, duplicate, or add verses.
- An `intro` is optional. Do not invent a surah introduction by default; include one only when specifically requested and base it solely on al-Tabari. If requested, put it under `## Introduction` before the first verse heading in the Markdown manuscript; the converter maps that section to JSON `intro` and keeps both formats synchronized.
- Keep the per-verse Markdown rich-text body identical between the manuscript and the decoded JSON value (aside from the structural verse heading, which is excluded). JSON escaping must not remove or alter Markdown markers or line breaks.
- The same JSON per-verse entries are used by the verse explanation pop-up and the full-surah commentary reading view. The user’s selected translation is read from `chapter_NNN.js`; the JSON blockquote is retained for editorial review and stripped from display by the app.

## Coverage and quality checks

The intended end state is commentary for all 114 surahs. Work in manageable batches, sized to the source sections, and save each completed batch. The proposed default is to begin with **Surah 1 (al-Fātiḥah) as a pilot** and present it for review before applying the style across the remaining surahs. If the user asks to skip the pilot review, continue in manageable, audited batches.

For each chapter and batch:

1. Confirm the chapter number, verse count, and exact English translations from `chapters-meta.js` and `data/chapter_NNN.js`.
2. Read the corresponding al-Tabari sections before writing; do not skip a verse or substitute another tafsir.
3. Check that every expected Markdown verse heading and JSON verse key appears exactly once, in order, with no missing or extra verses.
4. Check that each Markdown entry begins with the exact matching `ayah_en` translation as a blockquote, followed by substantive commentary with intentional Markdown formatting.
5. Check source fidelity, report attribution, and whether al-Tabari’s disagreements or preference have been represented accurately.
6. Regenerate JSON from the Markdown source and verify that each decoded `verses` value preserves the same rich Markdown body, including the leading translation blockquote and line breaks. Parse the result as valid UTF-8 JSON with no trailing commas.
7. Inspect both files and the diff before calling the batch complete. Never fabricate content to fill a missing or unclear source section; record a genuine source or alignment issue for review and continue only as appropriate.

## Publishing note

`sw.js` currently lists `data/tafsir_001.json` and `data/tafsir_002.json` under `RETIRED_PAYLOADS`. When those chapters are published again, remove their URLs from that retired list and update the service-worker cache version as needed so stale cached commentary is not served or immediately purged. Preserve the existing Quran text, translations, audio, and unrelated app features.
