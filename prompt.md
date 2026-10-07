# Quran Explained — Modern Tafsir Production Prompt

**Revision:** 2026-10-07

**Status:** Al-Fatihah pilot revised with source evidence, inline references, and a 400-word-per-verse minimum; awaiting review before any further chapters.

## Mission

Create a clear, comprehensive, newly written modern-English explanation of the Qur’an for the Quran Explained web app. Write the commentary verse by verse, aligned to the English translation already used by the app. Use **Tafsir al-Tabari alone** as the source for tafsir content.

This is original analytical writing based on al-Tabari, not a compressed restatement of his conclusions. Treat the Arabic text as a primary-source dossier: present relevant reports and linguistic evidence, compare what they support, and distinguish al-Tabari’s stated preference from the synthesis made here. Keep the attribution transparent and do not claim more independence than the source permits.

## Agreed editorial direction

- **Language and audience:** Accessible modern English for general readers. Use an Arabic term or transliteration when it adds meaning, and explain it briefly on first use. Avoid unnecessary technical vocabulary and long Arabic quotations.
- **Depth:** Each verse commentary must contain **at least 400 words**, excluding the structural heading and leading app-translation blockquote. Four hundred words is a floor, not a target ceiling: let the amount and complexity of source evidence determine how much longer the entry should be. Meet the floor with substantive evidence and analysis, never generic padding. If the source genuinely cannot support it, flag the shortfall for review rather than inventing content.
- **Approach:** Write an original comparative synthesis of the material al-Tabari transmits and analyzes, not merely a restatement of his final verdict. Put relevant reports, lexical or grammatical arguments, poetry, and Qur’anic cross-references into view; compare what each piece of evidence supports, where accounts differ, and how al-Tabari reasons from them. Do not turn that comparison into claims unsupported by the source.
- **Form:** Use natural, connected prose. Do not force every verse into the same headings or checklist. Use paragraph breaks to separate evidence, comparison, and analysis; avoid generic reflections, repetitive summaries, tables, and unnecessary lists.
- **Reports:** Quote or closely translate selected evidence where its wording matters, then analyze it. Preserve meaningful disagreements and al-Tabari’s stated preference and reasons, while clearly distinguishing reports he transmits from his own analysis and from the present synthesis. Condense long transmission chains but retain the attributed authority and any chain detail needed to distinguish reports. Describe a report as something al-Tabari transmits; never invent an authenticity grade or other source claim.

## Source material and verse alignment

### Sole tafsir source

Use only the matching file in `tafsir-al-tabari/`, named `NNN.txt` (for example, `001.txt` for al-Fātiḥah). Each file identifies a surah and contains verse sections headed `## SURAH:VERSE`.

- Read the section for the verse being explained. Read adjacent sections when al-Tabari discusses a passage across multiple verses, and make the verse-level connection clear without duplicating the same discussion in every entry.
- The Arabic corpus includes transmitted reports and bracketed edition/editor notes such as `[[...]]`. Do not misattribute an editor’s note to al-Tabari. Use such a note only when it genuinely clarifies the source; identify its editorial nature if it is important to include. Report numbers printed in the source may be cited as locating references, but do not treat editorial commentary around them as al-Tabari’s words.
- Do not consult or cite other tafsirs, outside commentaries, web sources, or remembered historical claims. The removed multi-tafsir source folders are not part of this task.
- Use Qur’anic text and cross-references only as they appear in, or are needed to understand, al-Tabari’s discussion. Do not add unsupported modern historical, legal, theological, or linguistic claims.

### App translation to explain

The app’s chapter files are `data/chapter_NNN.js`. Each verse has an Arabic text (`ayah_ar`) and an existing English translation (`ayah_en`). For each verse:

1. Read and use that exact `ayah_en` translation as the alignment anchor.
2. Analyze the verse using al-Tabari’s source material, quoting or closely translating evidence from the Arabic text and comparing relevant reports and arguments.
3. Do not replace, edit, or create a competing English translation. In the authoring Markdown, place the exact `ayah_en` text immediately after the verse heading as a one-line Markdown blockquote, for example `> <exact app translation>`. This is the only full verse translation in the entry; quoted reports and lexical glosses are evidence, not alternate renderings of the verse.
4. Keep that leading translation blockquote in the JSON value as well. The app displays the translation separately and its `stripLeadingVerseQuote()` function removes the initial blockquote before rendering/speaking the commentary, preventing a duplicate on screen. Do not repeat the Arabic verse.

The chapter data also groups verses into existing thematic units. Preserve those chapter files and groupings; commentary is keyed to individual verse numbers.

## Editorial rules

1. **Evidence before verdict:** Do not give only al-Tabari’s conclusion. Present the relevant evidence he records or adduces, explain what each item says, and compare the items before stating al-Tabari’s preference and the synthesis drawn from them.
2. **Meaningful disagreement:** Preserve competing reports, readings, and explanations where they materially differ. Do not flatten them into a single claim or imply that al-Tabari endorses every report.
3. **Traceable quotations and references:** Quote concise English renderings of reports when useful, identifying the attributed authority in the prose. Attach an inline reference in the form `[al-Tabari, 1:5, report 171]`; use the surah:verse and printed report number exactly as located in the source file (Western digits are acceptable). Cite al-Tabari’s unnumbered argument as `[al-Tabari, 1:5]`. For cross-references al-Tabari himself adduces, use a form such as `[Q 4:69, cited by al-Tabari at 1:7]`. Do not invent page numbers or report IDs.
4. **Translation of evidence:** English quotations from the Arabic source are the writer’s translations. Keep them short and faithful, mark them as translated report wording, and never present them as an existing English edition or as al-Tabari’s own English prose.
5. **Careful report language:** Say “al-Tabari transmits a report attributed to…” or equivalent. Do not independently label a report authentic, weak, fabricated, or historical unless the source itself clearly does so; do not misattribute editor’s notes or grades.
6. **Useful detail:** Retain names, evidence, lexical points, grammatical observations, and qualifications when they materially explain the verse. Condense repetitive isnāds but preserve enough provenance to distinguish one report from another.
7. **Modern readability:** Prefer direct, coherent prose and explain indispensable Arabic terms in plain language. “Modern” describes the language and presentation, not permission to import modern opinions.
8. **No padding or outside material:** Reach the 400-word minimum with relevant evidence, comparison, and analysis—not repetition or generic devotional application. Use only material in al-Tabari’s source file; flag genuine gaps rather than importing another tafsir or remembered claims.
9. **Source attribution:** Identify the work as an original modern analysis based on *Jāmiʿ al-Bayān* by al-Tabari. Clearly separate transmitted voices, al-Tabari’s own reasoning, and the present synthesis.

## Paired Markdown and JSON deliverables

For each completed surah, create **both** an editorial Markdown file and the JSON payload consumed by the app:

- **Canonical rich-text source:** `data/tafsir_markdown/tafsir_NNN.md` (for example, `data/tafsir_markdown/tafsir_001.md`).
- **App payload:** `data/tafsir_NNN.json` (for example, `data/tafsir_001.json`).

The Markdown is the source of truth. Generate or update the JSON from it with a deterministic converter; do not maintain two independently edited versions. If no converter exists, add a small conversion/validation script under `scripts/` and use it for every batch. Preserve all Markdown formatting in the JSON strings.

### Markdown authoring format

Use one structural verse heading per entry, exactly `## SURAH:VERSE`. Put the exact app translation in a leading blockquote, then write the rich-text commentary beneath it. The structural `## N:M` heading is for the Markdown manuscript and must not be copied into that verse’s JSON value. The brief sample below illustrates syntax only; every production commentary must meet the 400-word minimum and include evidence with inline references.

```markdown
# Surah 1: Al-Fatihah

## 1:1
> In the Name of Allah—the Most Compassionate, Most Merciful

Compare evidence in a transmitted report with al-Tabari’s linguistic reasoning, then give a source-grounded synthesis. For a report quotation use a reference such as `[al-Tabari, 1:1, report 138]`; for an unnumbered argument use `[al-Tabari, 1:1]`.

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

The intended end state is commentary for all 114 surahs. Work in manageable batches, sized to the source sections, and save each completed batch. Begin with **Surah 1 (al-Fātiḥah) as the pilot** and present it for review. Do not begin any other surah until the user explicitly approves the sample or changes the scope.

For each chapter and batch:

1. Confirm the chapter number, verse count, and exact English translations from `chapters-meta.js` and `data/chapter_NNN.js`.
2. Read the corresponding al-Tabari sections before writing; do not skip a verse or substitute another tafsir.
3. Check that every expected Markdown verse heading and JSON verse key appears exactly once, in order, with no missing or extra verses.
4. Check that each Markdown entry begins with the exact matching `ayah_en` translation as a blockquote and contains at least 400 words of substantive commentary after it.
5. Check that claims and translated quotations are traceable to named reports or specific al-Tabari sections, with inline citations; compare the evidence and distinguish transmitted views from al-Tabari’s reasoning and the present synthesis.
6. Verify accurate report attribution, disagreements, and any stated preference without inventing hadith grades or editor claims.
7. Regenerate JSON from Markdown and verify that every decoded `verses` value preserves the complete rich-text body, citations, blockquote, and line breaks. Parse valid UTF-8 JSON with no trailing commas.
8. Inspect both files and the diff before calling the batch complete. Never fabricate content to satisfy the word minimum; record a genuine source or alignment issue for review.

## Publishing note

`sw.js` currently lists `data/tafsir_001.json` and `data/tafsir_002.json` under `RETIRED_PAYLOADS`. When those chapters are published again, remove their URLs from that retired list and update the service-worker cache version as needed so stale cached commentary is not served or immediately purged. Preserve the existing Quran text, translations, audio, and unrelated app features.
