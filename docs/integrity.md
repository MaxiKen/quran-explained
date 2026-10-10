# Integrity rules

The line between what is required and what is forbidden. Both halves were
misunderstood once and cost the project a round trip.

## Synthesis is required

The maintainer's correction, verbatim:

> "I don't know how you plan to accomplish what I wanted without paraphrasing"

Paraphrase, synthesis and restatement from the real sources — eight of them,
six on every verse — are **the task**. An earlier claim that paraphrase was off-limits was wrong — it conflated
paraphrase with fabrication. Do not repeat that framing.

## Fabrication is forbidden

Never invent:

- a ḥadīth number
- a grading (*ṣaḥīḥ*, *ḥasan*, *ḥasan gharīb*) the source did not give
- an attribution — a narrator, collector, or scholar who is not named in that
  verse's source text
- a Qurʾān cross-reference
- a detail of a narrative the sources do not supply

The rule that keeps this honest: **every named authority in the commentary must
appear in that verse's own source text.** `tools/tests/guidance-*.js` enforces
it mechanically — see [testing.md](testing.md#attribution-integrity--the-check-that-matters-most).

When the sources disagree, present the disagreement. Do not resolve it into a
single comfortable answer, and do not drop the minority position to make the
prose cleaner.

When a source's own chain is weak or its attribution contested (Tanwīr
al-Miqbās is *attributed* to Ibn ʿAbbās, not certainly his), say so rather than
asserting it as settled.

## What is not verifiable from a sandbox

Recorded so no session re-litigates it or over-claims:

- **The redistribution terms at the three upstream hosts** (qul.tarteel.ai,
  quran.com, altafsir.com) cannot be reached — egress is allowlisted to
  github.com, npmjs.org and pypi.org only. `ATTRIBUTION.md` records them as
  the maintainer's confirmation, **not** as independently checked. The
  maintainer confirmed the licence situation: *"I have and it's all good."*
- **Attributions run through the English translations.** If Maʿārif cites
  al-Qurṭubī, we carry that as Maʿārif's citation. Nobody has checked al-Qurṭubī
  in the Arabic. Do not upgrade a translated attribution into a verified one.

## The texts are reproduced unedited

`data/tafsir_*.json` carries the source wording as published, with two
mechanical transformations only: deduplication of repeated blocks, and
compression of scattered ayah sets into runs. No wording is altered, smoothed
or modernised. `ATTRIBUTION.md` claims this and the claim must stay true.

The **authored** layer is the place where paraphrase lives, and it is labelled
"In plain words / integrated from N classical tafsirs" so the reader is never
confused about which is which.

## Do not type transliterated Arabic as literal Unicode in a script

Cyrillic homoglyphs have slipped in before — `Maʿārиā` with a Cyrillic `и`.
Both `tools/author_template.py` and the builder scripts assert-scan for
U+0400–U+04FF before writing. Keep that scan.

If a label must be constructed programmatically, use `\uXXXX` escapes rather
than pasting the character.
