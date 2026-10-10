# HANDOFF — the state of the project, and why it is in this shape

Read [`AGENTS.md`](AGENTS.md) first: it has the entry commands, the rules and the
current numbers. This file is the *narrative* — what changed recently and what
each decision cost, so that a new session does not relitigate them or undo them by
accident.

## What the commentary layer looks like right now

**27 verses, all compiled, all at or over their floors.** 1:1–1:7 and 2:1–2:20 were
rebuilt on 2026-10-10 from the eight sets with `tools/compile_guidance.py`, and then
rewritten against the lead rule the maintainer set the same day — 25,576 words,
`draws_on` of 5–7 sets a verse, nothing hand-written except the opening paragraph,
which now has to quote and explain every phrase of the translation in order.
What stood before them (42 verses across chapters 1 and 2) had been deleted on
2026-10-09 (`626fe14`) the day the bands were raised, because patching 42 verses to a
new contract is slower than regenerating them. `data/guidance_112.json` is still an
empty `{"verses": {}}` placeholder, which keeps the reader's fallback path under test.

**Resume at 2:21** (266 verses left in surah 2). `python3 tools/progress.py --next` is
the authority, not this file.

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

The first real batch should be **1:1 → 1:7**, compiled. Expect the first dry run to
fail: the packet now ranks eight sets and has extra CUT rules, so an older spec
selects different sentences than it did when it was written, and the floors are
much higher than the ones the last batch met. Re-dump the packet, re-pick the refs,
compile with `--dry` first, read every line of the failure list, and post one full
verse for review before committing the batch.

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
