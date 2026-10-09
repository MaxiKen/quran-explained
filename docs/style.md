# Style and presentation — the house format

Set by the maintainer on 2026-10-09, after an audit found that chapter 1 and
chapter 2 had been written in three different formats. This document is
normative: every verse in `data/guidance_NNN.json` must conform.

## Why this exists

The audit measured the corpus as it stood at 168 authored verses:

| verse | rendered `<p>` | `<h4>` headings | inline `<strong>` |
|---|---|---|---|
| 1:1 | 1 | 0 | 4 |
| 2:1 | 1 | 0 | 3 |
| 2:10 | 9 | 1 | 6 |
| 2:156 | 48 | 8 | 0 |

Chapter 1 was one continuous paragraph per verse with headings buried inline.
Chapter 2 was 30–60 short paragraphs with headings on their own lines, which
`renderMarkdown` promotes to real `<h4 class="modal-section-title">` blocks.
The same screen showed two unrelated documents.

Two further drifts:

- The opening convention flipped at 2:10. Verses 2:1–9, 2:11–13 and 2:15 kept
  the translation inline; 2:10, 2:14 and 2:16 onward gave it its own paragraph.
- Paragraph count climbed from an average of 9.2 (2:1–20) to 62.9 (2:121–140).
  Word count growth is expected across tiers; a sevenfold rise in
  fragmentation is not.

## The format

**1. Layout — structured, with merged paragraphs.**

Bold headings go on their own line, so the renderer makes them `<h4>` section
titles. Body paragraphs are merged up to roughly 85 words. Do not leave
one- or two-sentence stub paragraphs between headings.

The measured effect on 2:157: 35 paragraphs → 12, with the same 7 headings.

**2. Opening — the translation inline.**

The verse opens by quoting the app's own `ayah_en` wording in italics, **in the
first paragraph**, flowing straight into the commentary. It does not get a
paragraph of its own.

```
*They are the ones who will receive Allah's blessings and mercy.* Verse 156
defined them by a sentence. Verse 157 states the return, in three parts.
```

Quoted *source* material later in the entry may stand alone as its own
paragraph when the quotation is long. That rule is about the opening, not
about quotations generally.

**3. Closing — forward pointers only where they are earned.**

Point at the next verse only when it genuinely continues the argument. A
forward link is not a required furniture of every entry. At the time of the
audit 115 of 157 chapter-2 verses ended this way, which reads as a tic rather
than an observation.

**4. Transliteration — one form per name.**

| use | not |
|---|---|
| Makkah | Mecca |
| Madīnah | Madinah |
| Bayt al-Maqdis | Jerusalem |

This applies to **prose only**. Text inside an italic quotation reproduces the
source verbatim and keeps whatever spelling the source used — the six tafsirs
write "Mecca" and "Jerusalem" freely, and altering a quotation would be
misquotation. At the audit, no verse mixed spellings inside its own prose; the
inconsistency was between verses.

## Verifying it

`tools/tests/style-check.js` asserts all four rules against every authored
verse, and fails on any verse that departs from them. Run it with the rest of
the suite:

```
NODE_PATH=/tmp/apptest/node_modules node tools/tests/style-check.js
```

Style drift is the same class of failure as the silent test gaps recorded in
`docs/pitfalls.md`: a convention nobody checks will break, and a green suite
will not tell you.

## Retrofit status

Scope chosen by the maintainer: **all authored verses**, chapter 1 and
2:1–157 included. See `docs/progress.md` for the current state.
