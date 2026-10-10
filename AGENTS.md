# AGENTS.md — read this first, then start

**You are continuing an in-progress project: a plain-English commentary on all
6,236 verses of the Qurʾān, synthesised from eight classical tafsīrs — six that
cover every verse and two selective ones that are read where they comment.**

Read this file completely. Then read [`docs/style.md`](docs/style.md) — the only
normative format spec — and [`docs/voice.md`](docs/voice.md). Nothing depends on
a previous chat: every rule, tool and number below is in the repo and pushed.

## Start here

```bash
git log --oneline -3                      # HEAD should be at or past 8a0ae2e
python3 tools/progress.py --next          # the resume point, from the data
python3 -m http.server 8000 --bind 0.0.0.0 &   # the app is static; tests need this
node tools/tests/style-check.js           # 3/3 while the layer is empty
node tools/tests/sets-integrity.js        # 12/12
```

If the working tree looks wrong or `git log` is behind the remote, do **not**
re-do the work — recover it:

```bash
git fetch origin arena/525a7113-quran-explained
git reset --hard origin/arena/525a7113-quran-explained
```

This has happened four times across the project, most recently on 2026-10-10, when
`HEAD` was found at `a2de9fe` with three pushed commits missing and every file
showing as modified. A hard reset to the remote restored the tree exactly. The
rule it teaches is the one that saved the project: **push at the end of every run.**

---

## Current state

| | |
|---|---|
| Written | **0 of 6,236 verses** |
| Chapter 1 (al-Fātiḥah) | cleared 2026-10-09, empty placeholder file |
| Chapter 2 (al-Baqarah) | cleared 2026-10-09, empty placeholder file |
| Chapter 112 (al-Ikhlāṣ) | empty placeholder file |
| **Resume at** | **1:1** — nothing is authored |
| Branch | `arena/525a7113-quran-explained` |
| Source sets | 8 (6 complete + al-Qushayrī on 1,287 verses + al-Wāḥidī on 431) |
| Plan | 6,236 verses, **5,902,150** planned words (A 1,836 · B 2,920 · C 1,480) |

Everything previously authored was pulled on 2026-10-09, the same day the length
bands were raised and the opening-paragraph rule was written, so the layer is
regenerated against the current contract instead of patched. The three payload
files exist as empty `{"verses": {}}` placeholders: the reader's fallback to the
tafsīr sets is the path being exercised, and the payload contract is asserted by
`tools/tests/style-check.js`. **A chapter with no authored verses is legitimate.**

Authoring order is **chapter 1 → 114**, sequentially. Do not jump ahead or work
by juzʾ.

### One decision is still the maintainer's

**164 verses hold less raw material than their own floor** (measured across all
eight sets, `docs/sources.md`). Compiled mode cannot fill them without padding, and
padding is what got the last corpus cleared. Either cap those verses' floors at
their material, or treat them as authored-only. Do not resolve it by inventing
depth — and if you touch it, re-run `tools/tier_verses.py` so the plan and the
gate agree.

---

## The eight source sets

Six cover every verse: Ibn Kathīr, Maʿārif-ul-Qurʾān, Tazkīrul Qurʾān, Tanwīr
al-Miqbās, al-Jalālayn, al-Mukhtaṣar. Two were added on 2026-10-09 to give the
raised bands something to draw on: **al-Qushayrī** (*Laṭāʾif al-ishārāt*, the
allusive/spiritual reading, 1,287 verses) and **al-Wāḥidī** (*Asbāb al-nuzūl*,
occasion of revelation, 431 verses).

- Read **all eight** blocks for a verse. A set with no block there is *absent*,
  not thin — never imply an occasion or an allusion the payload does not carry.
- `draws_on` needs **5+ sets at tiers A and B, 4+ at C**, capped by the number of
  sets that actually cover the verse (`tools/verify_verse.py`). Nobody is failed
  for a source that has nothing to say.
- al-Wāḥidī exists only through the pollution guard in `docs/sources.md`: 395 of
  the upstream edition's 1,089 entries are his, the rest are al-Qushayrī's text
  misfiled. Its isnād chains are cut by the packet and are never quoted or graded.
- Re-ingest with `python3 tools/build_sets.py qushayri wahidi` (it **rebuilds** a
  set, never merges into it), then re-run `tools/tier_verses.py` — a new *source*
  moves tier assignments, a new *band* does not.
- The Arabic-only editions on the same upstream (Qurṭubī, Ṭabarī, *al-Kashshāf*,
  ʿĀshūr, Shawkānī, *al-Nashr*) stay out deliberately: the compiler splices a
  source's own English sentence, so anything needing translation would cost back
  the verbatim traceability the whole pipeline exists to have.

---

## The format — a rule, not a preference

Every verse has **two parts**:

**1. A plain-English introduction that walks the verse.** The translation is
taken **phrase by phrase, in order**: each phrase quoted, each phrase explained
where it stands, with a link to the verse before and after where the sources make
one. 240+ words at tier A, 170+ at B, 110+ at C, and never under 20% of the entry
— this paragraph does the **most work** in the verse. It is not a hook, not a
mood, not a question-only opener, and it may **not** start by quoting the whole
verse in one line. Names **no scholar**, uses **no technical term**, assumes **no
prior knowledge**. Evidence is not its business: hadith, cross-references, rulings
and their disagreement, the occasion, and theology all go under the headings, with
more detail than the lead can carry. A reader who stops at the end of the lead has
understood the verse; a reader who wants authority goes on.

The **view must not undo rule 1.** Both the verse modal and the commentary ebook
print the complete English verse directly above the commentary, which reads as the
commentary *starting with the verse*; where a verse has guidance that block is
dropped (`verseHasGuidance()` in `js/app.js`), and it stays exactly as it was for
unauthored verses. The same rule is why the compiler no longer emits the `>` line as
an opening recitation, and why `data/*.json` is fetched network-first by `sw.js` and
with `cache: 'no-store'` by the app: a stale guidance file is indistinguishable from
an unpublished chapter. `tools/tests/guidance-001.js` asserts all three.

**2. Then 3–6 headed sections.** Each heading is `**Like this.**` — bold, ending
with a full stop, **on its own line**, blank line, then its own paragraph.
Headings group the deeper material: what a word means, the readings on it, why
the scholars differed, whom the sources say it refers to.

Why own-line matters: `renderMarkdown` promotes an own-line `**bold**` block to
`<h4>`; inline `**bold**` stays `<strong>` and produces no heading.

There is **no reference implementation in the data** — the layer is empty.
`docs/style.md` is the spec; history has conforming examples for shape only
(`a2de9fe` authored, `d1e0609` compiled). Do not mine them for content.

**Three formats were tried and rejected** on 2026-10-09: a multi-paragraph layout,
then a single paragraph with inline `**bold**` signposts. Do not reinvent either.
If any other document here describes verse layout differently, `docs/style.md` wins.

---

## Length — the check is one-sided

Targets are in `data/plan.json` under `words`, generated from `BAND` in
`tools/tier_verses.py`: **A 1,300–1,900 · B 650–1,000 · C 300–450** (raised
2026-10-09). The enforced floor is `round(words × 0.75)` per verse — about
975 / 488 / 225 at the band edges. **There is no ceiling.** A long verse is fine
and must never be trimmed; only under-length fails. Never hand-edit `plan.json` —
edit `BAND` and re-run the classifier.

```
python3 tools/progress.py --next      # next verse to write
python3 tools/tier_verses.py --verify # tier assignments
```

---

## Two ways to make a verse

**Compiled** — the default for volume, and the reason the project can run at all.
The sources' own sentences are spliced, with only gated connectives between them.

```bash
python3 tools/verse_packet.py 1 1-7                 # ranked, numbered sentences from all 8 sets
# write a spec:  ### 1:1 / > translation line / ~ connective / ## Heading. / - J1.1.1
python3 tools/compile_guidance.py 1 /tmp/b001.md --dry
python3 tools/compile_guidance.py 1 /tmp/b001.md
```

The compiler refuses a spliced sentence that is not verbatim in that verse's own
blocks, refuses an unsourced word in a connective or heading, refuses attributive
and ruling verbs it cannot trace, drops a selection that only restates the
translation, caps connectives at 26 words (the pre-heading lead gets
`verify_verse.LEAD_CAP`, 620/460/320 by tier, because it has to quote and explain
every phrase), requires the tier floor and the lead's phrase coverage and order, and calls
`tools/verify_verse.check()` for layout — one implementation, not two.

What the gate actually rejects, learned compiling 1:1–1:7 and 2:1–2:20 on
2026-10-10 — all four are lead-authoring problems, not gate problems:

- **Connectives cannot contain a speech or ruling verb**, even an ordinary one:
  `said`, `says`, `holds`, `adds`, `notes` and `majority` are all refused in a `~`
  line and in a heading. Write `carries`, `is taken to be`, `puts it that`,
  `reads X as Y`. A refused lead is *dropped silently*, and the verse then fails the
  opening-paragraph gate with a misleading word count — read the whole message.
- **`+auto` does not count toward `draws_on`.** Only curated `- REF` lines do, so a
  verse needs 5 distinct sets *selected*, not 5 present. Sūrahs 1–77 have wāḥidī
  blocks and al-Qushayrī is thinnest before verse 20 — if a verse has no wāḥidī
  block, curate from J/M/K/T/D/X/Q instead of padding.
- **A selected sentence that only restates the app translation is dropped**, so a
  curated list compiles shorter than it reads. Check `sentences=` in `--dry`, and
  keep a `+auto 30–50` as a floor backstop rather than as the body.
- **A heading may only use words visible in that verse's packets**, and refs are
  verse-scoped (`M6.1.43` is valid under 1:6, not under 1:7).

Specs are **drafts in `/tmp` or `/home/user/proto`, not committed artifacts**, and
they are positional (`Q3.1.2` = qushayri, paragraph 1, sentence 2). Any change to
`sentences()` or the CUT list in `tools/verse_packet.py` shifts them, so always
re-dump the packet before compiling a spec you did not just write.

**Authored** — composed prose, still source-bounded, for what the compiler cannot
do: *weigh* two scholars instead of placing them side by side, settle a ruling
disagreement, and carry the verses whose material is thinner than their floor.

```bash
python3 tools/dump_sources.py 2 29 34   # everything the six-and-two sets say, ~12KB
python3 tools/verify_verse.py 2 --range 29-34 --file /tmp/draft.txt --names "Ibn ʿAbbās"
```

Both modes are gated identically. Read `docs/voice.md` before either.

---

## Before you commit — mandatory

```bash
python3 tools/verify_verse.py 1 --all                        # per-verse gate
node tools/tests/style-check.js                              # layout, floor, lead, transliteration
node tools/tests/sets-integrity.js                           # eight sets + the Asbāb guard
NODE_PATH=/tmp/apptest/node_modules node tools/tests/sources-all.js     # needs the server + jsdom
NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-001.js    # app render
```

All must pass. Read the `N/N checks passed` line — **never trust the exit code
alone.** `/tmp` does not persist between sessions:
`npm i jsdom --prefix /tmp/apptest` first.

`tools/verify_verse.py` is the per-verse gate: house layout, tier floor,
transliteration, Cyrillic homoglyphs, a 5-word run of the app's own `ayah_en`
inside the **opening paragraph**, the tier-aware `draws_on` count, and — with
`--names` — that **every authority cited occurs in that verse's own source
blocks**. Run it on a draft before it goes into the payload (`--file`), and on the
payload after (`--range`). It is the only check that catches an invented citation.

Then **post one full verse in the chat for review** before committing a batch.

---

## Pace

**20–25 authored verses per run, or 40–60 compiled ones.** The old 50-verse
authored target was withdrawn — it is the pace that produced the quote-stacking
which got the entire corpus cleared. Volume was the cause, not a side effect.

**Commit and push at the end of every session**, `git push origin
arena/525a7113-quran-explained`. The remote branch is the only durable copy.

---

## Files

| file | |
|---|---|
| [`docs/style.md`](docs/style.md) | **the format — normative** |
| [`docs/voice.md`](docs/voice.md) | the register, both production modes, what each tier contains |
| [`docs/workflow.md`](docs/workflow.md) | the loop, in order |
| [`docs/contracts.md`](docs/contracts.md) | JSON payload shapes, and what to touch when one changes |
| [`docs/sources.md`](docs/sources.md) | the eight tafsīrs, provenance, the Asbāb pollution guard |
| [`docs/pitfalls.md`](docs/pitfalls.md) | every trap found so far — read before scripting |
| [`docs/testing.md`](docs/testing.md) | the harnesses and how to run them |
| [`docs/integrity.md`](docs/integrity.md) | what is required (synthesis) vs forbidden (invention) |
| [`docs/classifier.md`](docs/classifier.md) | how tiers and targets are fitted |
| [`docs/batching.md`](docs/batching.md), [`docs/progress.md`](docs/progress.md) | batch sizing; the cleared-layer history |
| [`HANDOFF.md`](HANDOFF.md) | this session's handoff: what changed and why |
| `ATTRIBUTION.md` | licence and upstream per edition |

**There is no build system.** No `package.json`, no bundler, no `www/` — the PWA is
served as it is from the repo root, and `sw.js` is the only cache layer. Any
document describing an `npm run build` step is describing a different tree.

## Hard prohibitions

- Do **not** mine the cleared text (`d021eee`, `a2de9fe`, `d1e0609`) for content.
- Do **not** invent a ḥadīth number, a grading, an attribution, a cross-reference,
  or a narrative detail the sources do not supply. No exceptions, ever.
- Do **not** trim a verse to fit a length band; the target is a floor.
- Do **not** stack attributed blocks — eight quoted extracts is not commentary.
- Do **not** change a payload shape without bumping `CACHE_VERSION` in `sw.js`.
- Do **not** type transliterated Arabic as literal Unicode in a script (the gate
  asserts no U+0400–U+04FF; Cyrillic homoglyphs have slipped in before).
- Do **not** show the corpus to the maintainer. They read the finished product.
