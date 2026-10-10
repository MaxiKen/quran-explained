# HANDOFF — the state of the project, and why it is in this shape

Read [`AGENTS.md`](AGENTS.md) first: it has the entry commands, the rules and the
current numbers. This file is the *narrative* — what changed recently and what
each decision cost, so that a new session does not relitigate them or undo them by
accident.

## What the commentary layer looks like right now

**15 verses, all compiled and at or over their floors** (15,336 words). Batch 1
completed 1:6–1:7 and 2:1–2:8, bringing chapter 1 to its end and opening chapter 2.
The five entries already present at the start of this branch are 1:1–1:5; the current
payloads are `data/guidance_001.json` and `data/guidance_002.json`. Only
`data/guidance_112.json` remains an empty placeholder, which keeps the reader's fallback
path under test.

**Resume at 2:9.** `python3 tools/progress.py --next` is the authority, not this file.
The requested run is five sequential batches of ten compiled verses, validating and
pushing each batch before starting the next. The next range begins at 2:9.

## The two rules that were added, and why

**Length bands raised** (A 1,300–1,900, B 650–1,000, C 300–450; floor = 75% of the
per-verse target). The old bands were being met by verses that then left the named
evidences out entirely — a verse can satisfy 675 words with four sentences of
gloss and nothing else. Total plan went 4,013,330 → 5,798,620 words from this.

**The opening paragraph has to explain the verse.** A lead of 11–43 words was
passing while doing nothing but setting a mood, which is the opposite of the
project's purpose: a reader who stops at the lead must have the verse. Enforced
three ways — a minimum lead length by tier (90w at A, 60w at B/C), a 5-word run of
the app's own translation inside it, and no question-only lead — in
`tools/verify_verse.py` (the single implementation) and mirrored in
`tools/tests/style-check.js` as rule 4.

Both were pointless as prose in a doc, so both are gates. The pattern to keep: **a
rule that no tool enforces will be violated by the next session, including by
whoever wrote it.**

## The extractive compiler — why it exists and what it cannot do

Generated volume was the bottleneck, not reading: all eight source blocks for a
verse are ~3.7k tokens, and prose at 1,300–1,900 words out was the expensive part.
So a verse can now be *assembled* instead of written — `tools/verse_packet.py`
numbers and ranks the sentences of every block covering a verse, a spec lists which
to splice and where the seams go, and `tools/compile_guidance.py` emits the JSON.
Roughly 200–350 out-tokens per verse instead of 1,300–1,900, one agent, nothing
unattended.

What makes it safe is that it cannot say anything of its own: every spliced
sentence must be verbatim in *that verse's own blocks*, every connective word must
appear in those sources, attributive and ruling verbs are refused outright, and a
selection that merely restates the translation is dropped. It also cannot *adjudicate*
— it can put two scholars side by side, never weigh them. Verses with a live legal
disagreement, and the 164 verses whose material is thinner than their floor, stay
authored. `docs/voice.md` and `docs/pitfalls.md` carry the details; `docs/style.md`
is the format for both modes.

## The two sets that were added last

Approved on 2026-10-09 to feed the raised bands: **al-Qushayrī** (*Laṭāʾif
al-ishārāt*, 1,287 verses) and **al-Wāḥidī** (*Asbāb al-nuzūl*, 431 verses), ingested
through a new `tools/build_sets.py` so the corpus is rebuildable rather than
hand-assembled. Measured effect is modest and lopsided — tier A's median
material/floor moved 1.70× → 1.80× and the starved count 195 → 164 — because both
editions concentrate in the long Medinan sūrahs. That is the honest result, and it
is recorded in `docs/sources.md` rather than smoothed over.

Two things a future session must not undo:

- **The Asbāb pollution guard.** Upstream's Asbāb file has 693 of 1,089 entries
  filled with al-Qushayrī's text. `build_sets.py` keeps only entries that cite a
  verse of their own surah and match no Qushayrī entry — 395 survive. Broadening
  the rule to gain coverage would attribute one author's words to another at scale,
  which is the single failure this project cannot absorb.
- **Rebuild, never merge.** A set is written from scratch each run, indices and
  all. The first version merged into the old mapping and produced in-range indices
  pointing at the wrong paragraph — silently plausible, silently wrong.

## What to expect when you generate

Batch 1 has completed through 2:8. Resume at **2:9**, re-dump the packet for each
ten-verse batch, validate with `--dry` before writing, and run the house gate and
render harnesses at each boundary.

## Rules about working here, not about the text

- One agent, no fan-out, no API keys, nothing unattended. Speed comes from the
  compiler, never from reading fewer sources.
- Push at the end of every run. The workspace is reset without warning; on
  2026-10-10 `HEAD` was found three commits behind the remote with a dirty tree,
  and `git reset --hard origin/<branch>` restored everything that had been pushed.
- The maintainer reads the finished verse, never the corpus dump. Keep chat to
  gate output, counts and decisions.
- There is no build step. If a doc mentions `npm run build`, `www/`, `scripts/` or
  a `data/tanzir_ul_quran.json`, it is stale — fix the doc rather than following it.

## Heading proof and the retired auto fill (2026-10-10)

- **Every heading is written from its own sources.** A heading is a question or a part of the verse that needs explaining. The sentences cited under it must answer that question or explain that part, in full.
- **Real content, not a term.** The gate requires each heading to cite at least two source sentences carrying its key terms, totalling at least 60 words. A key term alone is not enough. The gate measures coverage; the writer must still read the sources in full.
- **The automatic fill is retired.** The compiler no longer appends unlabelled sentences under a generic heading such as "What else the same passage holds". A `+auto` line fails the gate.
- **The sources are read completely before writing.** Comprehensive, detailed and helpful is the standard.
