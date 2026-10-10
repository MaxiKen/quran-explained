# The voice

The deliverable is **one integrated commentary per verse in a single voice** —
not eight attributed blocks stacked together. It must read as though written from
one source, synthesised from the classical tafsīrs, and it must work
through the app's own English translation, quoting its actual words.

This was the maintainer's explicit correction:

> "important contents from the sources are well integrated like they are one
> (written from a source) and also integrate with the English translation
> already in the app, quoting its actual words for explanation."

**Punctuation, because it is what makes a spliced entry read as one voice:** connectives
use commas and full stops only — **no em dashes, no semicolons, no parentheses asides, no
markup**. The sources' sentences are spliced on that same rhythm, so a dash or a
semicolon inside my own line is the one tell that the paragraph was pasted in. This is
not enforced by a gate; it is enforced by reading the finished entry aloud once.

## Structure of a verse

**Headings may be questions or further explanation.** A heading can be a question the reader would ask, or a part of the verse that needs more explanation. The evidence under a heading is taken from the sources in the context of that heading only: it answers the question asked, or explains the part named. Sources are not dumped under a heading that they do not address.

**The sources are read completely before writing.** Every source used for a verse is read in full and understood, not skimmed for a quotable line. The commentary is comprehensive: the material under the headings covers what the sources say on the question, including where they differ, and it is written in one plain voice.

Not a rigid template, but the shape that has worked:

1. **Open on the translation's own wording, and explain the verse in the same
   paragraph.** This is not a hook slot. The opening paragraph must say what the
   verse says, to whom it is addressed, and what it is doing here in the
   argument — before any rhetorical framing. It must quote the translation itself,
   and it may not consist only of questions. Maintainer rule, 2026-10-09, after a
   batch of verses whose first paragraph set a mood and left the explaining to the
   first heading. Checked by `tools/verify_verse.py`: 90 words minimum at tier A,
   60 at B and C, a 5-word run of the app's translation inside that paragraph, and
   no question-only lead.
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

Bold subheadings are used in the longer tiers to break a 1,300-word entry into
readable movements. Tier C entries are plain prose — a 300-word entry does not
need headings. (3–6 own-line `**Heading.**` paragraphs are required wherever
headings are used at all; see `tools/verify_verse.py`.)

Transliterate consistently with the sources: *ṣaḥīḥ*, *ḥasan gharīb*,
*Ibn ʿAbbās*, *al-Bukhārī*. Use ﷺ after the Prophet's name as the source data
does.

## What each tier contains

| Tier | Words | Contains |
|---|---|---|
| **A** | 1300–1900 | Walk the translation phrase by phrase · wording and why this word · occasion of revelation where the sources give one · the ruling or the narrative developed properly · Qurʾān cross-references · named evidences with narrators · what it establishes · application |
| **B** | 650–1000 | Walk the translation · wording · connection to what surrounds it · the main evidence · application |
| **C** | 300–450 | The meaning, its connection to what surrounds it, and why it is short. **No padding.** A refrain needs one honest paragraph, not five |

The bands above are set in `tools/tier_verses.py` (`BAND`) and are what
`data/plan.json` is generated from — change them there and regenerate, never by
hand-editing the plan. They were raised on 2026-10-09 (from 900–1300 / 450–700 /
200–320) because the old bands were fitted to a ~50-verse pilot and left the named
evidences out of the longest verses.

The plan target per verse is in `data/plan.json`. It is a **floor**, not a
band: meet at least 75% of it (so 975 / 488 / 225 words as the bands now stand),
and let the verse run as long as the material carries it. The harness fails a verse for falling short and never for running
long. Set by the maintainer on 2026-10-09, reversing an earlier two-sided 25%
band.

## Two ways a verse gets made


**Which of the two a verse uses is decided by `data/plan.json`.** 168 verses hold less
material than their own floor and are marked `authored_only`: `tools/compile_guidance.py`
refuses them, because a compiled entry there could only reach its floor by repeating,
padding or inventing. They are composed here, in runs of 5–10, and the sources they lean
on are the same blocks — authored mode buys the weighing, not a licence to invent.
Both write the same field in `data/guidance_NNN.json` and are gated by the same
`tools/verify_verse.py` check, so neither can hold a looser standard than the other.

**Authored** — prose written from the sources by hand. The only mode that can
*resolve* a disagreement between the sets rather than set the positions side by
side. Slow: roughly 1,300 tokens of typing per tier-A verse, every claim and name
needing to be checked against the verse's own blocks.

**Compiled** — an extractive splice. `tools/verse_packet.py` numbers and ranks the
sentences of the blocks that cover the verse; the spec lists which of them to
use (`- M43.19.2`) and where the seams go; `tools/compile_guidance.py` pastes the
source's own sentences and writes the file. Three rules make it safe rather than
merely fast:

  * a spliced sentence must be a folded substring of *this verse's* source blocks,
    which is checked, so a claim has nowhere to come from except the sources;
  * a connective's every content word must already occur in this verse's sources or
    in the app's translation, attribution and ruling verbs are refused, and the
    budget is 26 words inside a section — the opening paragraph excepted, at
    `verify_verse.LEAD_CAP` (620/460/320 by tier), because the lead has to quote and
    explain every phrase of the verse and a join cannot;
  * fragment splices, isnād arrows and passages that only repeat the translation
    are dropped by the compiler, not left for review.

What compilation gives up: it can place two scholars against each other, it cannot
weigh them. Where a verse turns on a dispute that needs settling, that verse is
authored.

## Length is a floor on quality, not a licence to pad

If a verse has less to say than its target, say less and flag it — do not
inflate. Padding is worse than missing a word count, and the maintainer asked
for detail, not volume.

## Read aloud

`js/read-aloud.js` speaks the **primary source only** (`getVerseCommentary`,
around line 391 in `unitFor`). The guidance layer is **not yet spoken**. If
that changes, the range label must never be spoken and a shared run must be
spoken once at its first verse — that behaviour is already tested by
`tools/tests/sources-all.js` and must not regress.

## The two voices added on 2026-10-09, and their limits

**Laṭāʾif al-ishārāt (al-Qushayrī, d. 465)** is a commentary of *allusion* — what
the verse indicates beyond its apparent sense. It is the only English source in
the shelf that reads a verse spiritually rather than legally, which is why the
deep Medinan verses needed it. Its register is the trap: it writes in homilies
("the lovers' secrets", "the people of the station"), and it is not evidence for
a ruling, a cause, or what a scholar held. Use it for what a verse does to the
reader, in its own words or not at all. Never let an allusion become a claim
about law, and never cite it as a consensus — it records none.

**Asbāb al-nuzūl (al-Wāḥidī, d. 468)** answers *why a verse was said when it was*.
It is the source the new opening-paragraph rule needed most, and the one with the
harshest handling rules:

- It is present on 431 verses. Its absence says nothing about the other 5,805 —
  do not let an authored verse imply an occasion the file does not carry.
- Its entries are chains. The chain (`X informed us > Y said`) is exactly what
  `verse_packet` cuts, and it must stay cut: we are not a ḥadīth collection and
  we do not grade anything.
- Only the entries that survive the pollution guard in `docs/sources.md` exist in
  our payload. Never cite "al-Wāḥidī reports" from memory of the book — cite it
  from the block, or not at all.

Both sets are optional *inputs*: `draws_on` asks for 5 of them at tiers A and B,
capped by what covers the verse. Nobody is ever failed for a source that has
nothing to say.

## Heading proof and the retired auto fill (2026-10-10)

- **Every heading is written from its own sources.** A heading is a question or a part of the verse that needs explaining. The sentences cited under it must answer that question or explain that part, in full.
- **Real content, not a term.** The gate requires each heading to cite at least two source sentences carrying its key terms, totalling at least 60 words. A key term alone is not enough. The gate measures coverage; the writer must still read the sources in full.
- **The automatic fill is retired.** The compiler no longer appends unlabelled sentences under a generic heading such as "What else the same passage holds". A `+auto` line fails the gate.
- **The sources are read completely before writing.** Comprehensive, detailed and helpful is the standard.
