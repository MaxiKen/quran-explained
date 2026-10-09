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

**A plain-English introduction.** One paragraph that **explains the verse** —
what it says, to whom it is addressed, and what it is doing at this point in the
sūrah. Roughly 90–160 words at tier A, 60–120 at tiers B and C. It names **no
scholar**, uses **no technical term**, and assumes **no prior knowledge**. A
reader who stops here has understood the verse.

It is not a hook. A lead that sets a mood, poses a question, or promises that the
explanation is coming under the next heading does not satisfy this — the
explaining happens *in the lead*. The app's own translation is quoted inside this
paragraph (not necessarily as its first words). Enforced by
`tools/verify_verse.py` and `tools/tests/style-check.js`: minimum word count for
the opening paragraph, a 5-word run of `ayah_en` inside it, and no
question-only opening.

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
| A | 1,300–1,900 | 975 |
| B | 650–1,000 | 488 |
| C | 300–450 | 225 |

Per-verse targets live in `data/plan.json` under `words`, which is generated:
edit `BAND` in `tools/tier_verses.py` and re-run it — never hand-edit the plan.
The bands were raised on 2026-10-09 (from A 900–1,300 / B 450–700 / C 200–320)
after review of the compiled chapters: the old floor was being met by verses that
then left the named evidences out entirely.

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

## Two ways to produce a verse

**Authored** — composed prose, source-bounded. The only mode that can settle a
disagreement rather than present it.

**Compiled** — `tools/verse_packet.py` ranks the sentences of the six blocks that
cover the verse; a spec lists which to splice and where the seams go;
`tools/compile_guidance.py` pastes the sources' own wording, checks that every
spliced sentence is traceable to this verse's own blocks, allows only connectives
built from words those sources already use, and writes the JSON. Faster by an
order of magnitude and it cannot invent an attribution; it cannot adjudicate
either. Format rules above apply to both, and both are gated by the same
`tools/verify_verse.py` check — the compiler calls it rather than copying it.

## Pace and the review gate

About 20–25 authored verses per run, or 40–60 compiled ones. An earlier 50-verse
target was withdrawn for authored work: volume was the cause of the prose
decaying into stacked extracts.

Post one full verse in the chat before committing a batch.

## Every chapter is cleared as of 2026-10-09

Chapters 1 and 2 (7 and 35 verses) were removed the same day the bands and the
lead rule were raised, so the whole layer is regenerated against the current
contract rather than patched verse by verse. `data/guidance_112.json` remains as
an empty `{"verses": {}}` placeholder. Superseded text stays in history
(`d021eee`, `a2de9fe`, `d1e0609`) and must **not** be mined.

---

## Status

| chapter | verses | layout |
|---|---|---|
| 1 | 0 | cleared — regenerate at the new bands |
| 2 | 0 | cleared |
| 112 | 0 | empty placeholder |

`tools/tests/style-check.js` passes across all three files because there is
nothing left to fail.

This format is **the permanent rule** for all remaining verses. See
[`../AGENTS.md`](../AGENTS.md) for the entry point.
