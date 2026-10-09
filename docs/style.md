# Style — the house format

Set by the maintainer on 2026-10-09, verse by verse, after the whole corpus was
cleared and restarted. This document is normative. Every verse in
`data/guidance_NNN.json` must conform.

**It supersedes an earlier version of this file** written the same day, which
specified a multi-paragraph layout with `**bold**` headings on their own lines.
The maintainer rejected that. See *Why the earlier version was wrong*, at the
end.

## 1. One paragraph per verse

Every verse is **a single continuous paragraph**. No blank lines inside a verse.
No standalone quotation blocks. No `##` headings.

## 2. Inline bold signposts, 3–5 per verse

Inside that paragraph, use 3–5 `**bold**` signposts to mark where the subject
turns, each followed immediately by prose. They are inline — never on their own
line.

```
**What mercy means here.** Al-Jalālayn gives the shortest definition in the
corpus: the One who possesses *mercy*, which means to will what is good for
those who deserve it.
```

## 3. Open with the translation

The first words of the paragraph quote the app's own `ayah_en` wording in
italics, then flow straight into the commentary.

```
*In the Name of Allah—the Most Compassionate, Most Merciful.* The translation
opens with a preposition. There is no verb here, and no subject either.
```

## 4. Quoted phrases only — about 10 words maximum

This is the rule the corpus failed on, and the reason it was cleared.

Quotations are **short phrases folded into sentences the author wrote**. The
chapter-1 average was 4–9 words.

**Ḥadīth are exempt — maintainer's ruling, 2026-10-09.** Asked whether chapter
1's long quotations should be shortened, the ruling was: *"the hadith quotations
should be left."* Chapter 1 carries ten quotations over twenty words, almost all
ḥadīth, including the 134-word parable in 1:6. Those stand, and nothing is
rewritten to shorten them. Quoting a ḥadīth or a classical definition whole is
legitimate; the cap applies to Qurʾānic fragments and paraphrase.

`tools/tests/style-check.js` enforces this by excluding any quotation over twenty
words from the per-verse average, rather than ignoring long quotes outright. One
ḥadīth quoted whole cannot fail an otherwise well-written verse, and the
remaining short quotations must still average down to phrase length — which is
what actually stops extract-stacking.

Measured, at the point the corpus was cleared:

| verse | quoted spans | avg quote | block quotes ≥25w |
|---|---|---|---|
| 2:1 | 21 | **5.4 words** | 2 |
| 2:3 | 17 | **5.6 words** | 1 |
| 2:20 | 19 | **23.5 words** | 8 |
| 2:60 | 22 | **29.6 words** | 14 |
| 2:140 | 37 | 20.8 words | 15 |

Up to 2:10 the commentary was genuinely synthesis. From 2:20 the entries became
stacked extracts with thin connective tissue. The maintainer's words: *"you're
just quoting unnecessarily, which doesn't make the whole thing make sense. The
flow is not there."*

**Flow is the requirement.** A verse must read as one sustained explanation.

## 5. Sources — use and name only what is actually used

Name in the prose only the tafsīrs genuinely drawn on, and record exactly those
in `draws_on`. Chapter 1 names 4–6 of the six per verse; that is correct. Do not
pad a verse with a source that adds nothing.

## 6. Length — tiered, and the check is a floor

Keep the A/B/C tiers from `docs/classifier.md` and `data/plan.json`:

| tier | target | floor |
|---|---|---|
| A | 900–1,300 | 75% of target |
| B | 450–700 | 75% of target |
| C | 200–320 | 75% of target |

**The floor is one-sided.** A verse may run as long as its content requires;
only under-length fails. Never trim a verse to fit a ceiling.

## 7. Transliteration — one form per name, in prose

| use | not |
|---|---|
| Makkah | Mecca |
| Madīnah | Madinah |
| Bayt al-Maqdis | Jerusalem |

**Prose only.** Text inside an italic quotation reproduces the source verbatim
and keeps whatever spelling the source used — the six tafsīrs write "Mecca" and
"Jerusalem" freely, and altering a quotation would be misquotation.

## 8. Pace, and the review gate

**About 20–25 verses per run.** This is deliberate: 50+ verses per run is the
pace that produced the quote-stacking.

**Before committing a batch, post one full verse in the chat for the maintainer
to read.** This is a standing instruction — *"always post one of your response
writeup in this place."* It is the primary defence against drift, because the
defect that cleared the corpus was a prose-quality defect that no automated
check caught.

## 9. Chapters 2 and 112 start fresh

The cleared text (167,000 words, preserved at
`d021eeee959645cc0bf7226418d718cf15dc6e39`) is **not to be mined**. Treat those
chapters as never written and re-read the six tafsīrs for every verse. The
prose was the thing that was wrong, so reusing it would carry the defect back.

## Status

| file | state |
|---|---|
| `guidance_001.json` | 7 verses, one paragraph each, 5,414 words — **the model** |
| `guidance_002.json` | cleared, 0 verses |
| `guidance_112.json` | cleared, 0 verses |

## Why the earlier version of this file was wrong

1. **I mistook a formatting inconsistency for the problem.** The audit found
   chapter 1 in one format and chapter 2 in another, so I standardised on
   chapter 2's. That fixed the inconsistency by making everything worse. The
   chapter-1 format was the good one.

2. **The real defect was in the writing, and my audit never measured it.** I
   counted paragraphs and headings. I did not measure quotation density, which
   is where the quality drop lived. A style rule that constrains only layout
   will not stop prose decaying into a stack of quotes.

3. **Speed was the cause and I kept the speed.** The degradation tracked batch
   volume. I raised the verse count per run instead of lowering it.

The lesson for any future audit: **measure the prose, not just the markup — and
have a human read a sample before a style is applied to 6,000 verses.**
