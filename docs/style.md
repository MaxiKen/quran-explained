# Style — the house format

Set by the maintainer on 2026-10-09, and revised the same day after review of
the live preview. This document is normative. Every verse in
`data/guidance_NNN.json` must conform.

**Revision history.** Three successive versions were written on 2026-10-09.
The first specified a multi-paragraph layout. The second specified a single
paragraph per verse with inline `**bold**` signposts. Both were rejected. The
version below is the current one, and it is what 2:1–2:10 are written in.

---

## 1. Plain explanation first, then headed sections

Every verse has **two parts**:

**A plain-English introduction.** One short paragraph, roughly 60–120 words,
that says what the verse means. It names **no scholar**, uses **no technical
term**, and assumes **no prior knowledge**. A reader who stops here has
understood the verse.

**Then 3–6 headed sections.** Each heading is `**Like this.**` — bold, ending
with a full stop, **on its own line**, followed by a blank line and then its own
paragraph. `renderMarkdown` promotes an own-line `**bold**` block to `<h4>`, so
these render as real headings. Headings must not be inline inside a sentence.

Headings group the deeper material: what a word means, the readings on it, why
the scholars differed, what it implies, whom the sources say it refers to.

**Why.** The maintainer's instruction: *"the content is first of all simply
explained. Other things are grouped comprehensively under headings."* The
single-paragraph version put scholarly detail in the first sentence.

## 2. Length — tiered, and the check is a floor

| tier | target | floor (75%) |
|---|---|---|
| A | 900–1,300 | 675 |
| B | 450–700 | 338 |
| C | 200–320 | 150 |

Per-verse targets live in `data/plan.json` under `words`.

**The check is one-sided. The target is a floor, never a ceiling.** A verse that
runs long is fine and must not be trimmed to fit. Only under-length is a
failure. This reverses an earlier two-sided rule that caused three good verses
to be cut down; they were restored in `b83b69a`.

## 3. Transliteration — one form per name, in prose

`Makkah`, not Mecca. `Madīnah`, not Madinah. `Bayt al-Maqdis`, not Jerusalem.
Enforced in prose only — never rewritten inside a quotation, where the source's
own spelling stands.

---

## Rules removed on 2026-10-09

Three rules were deleted at the maintainer's instruction because the layout
change made them wrong rather than the data:

- **Signpost count (3–5 inline).** With headings on their own lines, the
  inline/heading distinction the rule assumed no longer exists.
- **Opens by quoting the translation.** The new layout deliberately opens with
  plain prose, so the translation is quoted *within* the introduction rather
  than as its first words. Quoting `ayah_en` remains good practice; it is no
  longer asserted.
- **Quotations average ≤10 words.** Removed. The ḥadīth exemption already
  hollowed it out, and the cap was flagging verses at 10.4 words — noise, not a
  real defect.

`tools/tests/style-check.js` now enforces only rules 1–3 above.

---

## Sources and attribution

Substance is synthesised from the six tafsīrs shipped in `data/tafsir_NNN.json`:
Ibn Kathīr, Maʿārif-ul-Qurʾān, Al-Mukhtaṣar, Tazkīrul Qurʾān, Tanwīr al-Miqbās,
al-Jalālayn. Nothing is invented. A named authority must appear in that verse's
own source block at that verse's range — grep the blob before citing.

`draws_on` lists **only** the sources actually used, not all six.

## Pace and the review gate

About 20–25 verses per run. An earlier 50-verse target was withdrawn: volume
was the cause of the prose decaying into stacked extracts.

Post one full verse in the chat before committing a batch.

## Chapters 2 and 112 start fresh

Both were cleared on 2026-10-09. The superseded text remains at `d021eee` but
must **not** be mined.

---

## Status

| chapter | verses | layout |
|---|---|---|
| 1 | 7 | **old single-paragraph — not yet converted** |
| 2 | 20 | plain intro + headed sections |
| 112 | 0 | cleared |

Chapter 1 currently **fails rule 1** because it predates this format. It was
written when the single-paragraph rule was in force and has not been converted.
