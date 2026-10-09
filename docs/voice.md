# The voice

The deliverable is **one integrated commentary per verse in a single voice** —
not six attributed blocks stacked together. It must read as though written from
one source, synthesised from the six classical tafsīrs, and it must work
through the app's own English translation, quoting its actual words.

This was the maintainer's explicit correction:

> "important contents from the sources are well integrated like they are one
> (written from a source) and also integrate with the English translation
> already in the app, quoting its actual words for explanation."

## Structure of a verse

Not a rigid template, but the shape that has worked:

1. **Open on the translation's own wording.** Quote it, then take it apart
   phrase by phrase. If the translation has a bracketed gloss, explain why the
   gloss is there — that is often the whole point of the verse.
2. **Say what the wording is doing.** Grammar matters and is not pedantry: a
   fronted object, a definite noun where you expected a verb, a missing
   object. The sources attend to these and so should the commentary.
3. **Bring in the substance**, naming narrators and collectors inline as the
   sources give them.
4. **Carry disagreement honestly.** When the scholars differ, present the
   positions and the evidence for each. Do not flatten a real disagreement
   into a single comfortable answer, and do not pretend the majority view is
   the only one.
5. **Close by tying back** to the sūrah's argument or to the verse that
   follows.

## Register

Modern, simple grammar. Comprehensive and detailed. No archaising, no
devotional inflation, no filler. Short declarative sentences carry the
argument; longer ones are for the material itself.

Bold subheadings are used in the longer tiers to break a 900-word entry into
readable movements. Tier C entries are plain prose — a 200-word entry does not
need headings.

Transliterate consistently with the sources: *ṣaḥīḥ*, *ḥasan gharīb*,
*Ibn ʿAbbās*, *al-Bukhārī*. Use ﷺ after the Prophet's name as the source data
does.

## What each tier contains

| Tier | Words | Contains |
|---|---|---|
| **A** | 900–1300 | Walk the translation phrase by phrase · wording and why this word · occasion of revelation where the sources give one · the ruling or the narrative developed properly · Qurʾān cross-references · named evidences with narrators · what it establishes · application |
| **B** | 450–700 | Walk the translation · wording · connection to what surrounds it · the main evidence · application |
| **C** | 200–320 | The meaning, its connection to what surrounds it, and why it is short. **No padding.** A refrain needs one honest paragraph, not five |

The plan target per verse is in `data/plan.json`; stay within 25% of it. The
harness enforces this.

## Length is a floor on quality, not a licence to pad

If a verse has less to say than its target, say less and flag it — do not
inflate. Padding is worse than missing a word count, and the maintainer asked
for detail, not volume.

## Read aloud

`js/read-aloud.js` speaks the **primary source only** (`getVerseCommentary`,
around line 391 in `unitFor`). The authored guidance is **not yet spoken**. If
that changes, the range label must never be spoken and a shared run must be
spoken once at its first verse — that behaviour is already tested by
`tools/tests/sources-all.js` and must not regress.
