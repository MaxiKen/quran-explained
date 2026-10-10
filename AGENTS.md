# AGENTS.md — read this first, then start

**You are continuing an in-progress project: a plain-English commentary on all
6,236 verses of the Qurʾān, synthesised from eight classical tafsīrs — six that
cover every verse and two selective ones that are read where they comment.**

Read this file completely. Then read [`docs/style.md`](docs/style.md) — the only
normative format spec — and [`docs/voice.md`](docs/voice.md). Nothing depends on
a previous chat: every rule, tool and number below is in the repo and pushed.

## Start here

```bash
git rev-parse HEAD origin/arena/525a7113-quran-explained   # the two must match
python3 tools/progress.py --next          # THE resume point — authoritative, from the data
node tools/tests/style-check.js           # 9/9
BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-range.js  # 22/22, the render gate
node tools/tests/sets-integrity.js        # 12/12
python3 tools/verify_verse.py 2 --all     # 35/35

python3 tools/serve.py 8090 &             # the DOM tests and the preview need a server
npm i jsdom --prefix /tmp/apptest         # /tmp is wiped between sessions
BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/sources-all.js
BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-001.js
```

**`tools/progress.py --next` wins over every number in this file.** The table below is
a snapshot taken at a commit, and it has been wrong before; the data files are what the
app renders. Never re-author a verse that `progress.py` reports as done, and never
clear a payload file because a doc says it is a placeholder — check `data/guidance_*.json`
first. Never serve the preview with `python -m http.server`: it sends `Last-Modified` and
no `Cache-Control`, which is how a new payload becomes invisible (`tools/serve.py` is
`no-store` on everything).

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

Snapshot at `5af740f`, 2026-10-10.

| | |
|---|---|
| Written | **84 of 6,236 verses** — every one at or over its floor |
| Chapter 1 (al-Fātiḥah) | **1:1–1:7 authored** — `data/guidance_001.json`, 38,399 B |
| Chapter 2 (al-Baqarah) | **2:1–2:97 authored** — `data/guidance_002.json` |
| Chapter 112 (al-Ikhlāṣ) | empty placeholder file — deliberate, it tests the fallback |
| Compiled shape, as shipped | leads 174–365w · 3–6 headings · `draws_on` 5–8 sets |
| **Resume at** | **2:98** — sequentially, in batches of 5 (2:119 is the next `authored_only`) |
| Branch | `arena/525a7113-quran-explained` |
| Source sets | 8 (6 complete + al-Qushayrī on 1,287 verses + al-Wāḥidī on 431) |
| Plan | 6,236 verses, **5,902,150** planned words (A 1,836 · B 2,920 · C 1,480) |

Everything authored before 2026-10-09 was pulled that day, the same day the length
bands were raised and the opening-paragraph rule was written, so the layer is
regenerated against the current contract instead of patched. What exists now
(1:1–1:7, 2:1–2:35) was compiled and rewritten under that contract and **is** the
reference implementation: read one or two compiled entries in
`data/guidance_002.json` for shape before writing a spec. Only `data/guidance_112.json`
is still an empty `{"verses": {}}` placeholder, which keeps the reader's fallback to the
tafsīr sets under test; `tools/tests/style-check.js` asserts the payload contract.
**A chapter with no authored verses is legitimate.**

Authoring order is **chapter 1 → 114**, sequentially. Do not jump ahead or work
by juzʾ.

### Thin verses are authored-only — decided, do not re-open it

**168 verses hold less material than their own floor.** `data/plan.json` measures it as
`avail` — every word the covering sets say about that verse, a block shared by several
verses counted in full because the compiler may splice it for any of them. Where `avail`
is under `0.75 × target` the row is marked `authored_only` (147 tier A, 21 tier B, 62,945
words of shortfall in total) and:

- **`tools/compile_guidance.py` refuses them**, with the verse's numbers and the commands
  to compose it instead. A compiled entry there could only reach its floor by repeating a
  sentence, padding a connective, or inventing — and the first two are the quote-stacking
  that got the 2026-10-09 corpus cleared.
- **They are composed**, where two readings can be weighed and a short source explained at
  length: `tools/dump_sources.py`, then `verify_verse.py --file --names`. Expect **5–10 per
  run**, against a compiled batch of five; the run is scheduled around them, not merged in.
- **The floor does not move.** Capping it was tried the same day and reverted: lowering the
  bar to the material looks neutral but it quietly abolishes the raised bands everywhere it
  binds, and it buys nothing that a composed entry does not buy honestly. If you feel the
  urge, read `docs/pitfalls.md` ("A floor is data now") — two plausible formulas there cap
  1,553 and 5,516 verses respectively before you notice.
- `python3 tools/progress.py --next` says which mode the resume verse belongs to, and names
  the next authored-only one in the surah, so a batch can be planned around it.
- No verse authored so far (1:1–1:7, 2:1–2:35) is flagged; the flag has been checked against
  the payload, so nothing already shipped needs rewriting. If a future change to the bands
  or to the sets flags something already compiled, **re-author that verse**, do not delete it
  and do not leave it.
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

**The verse belongs to the app, the walk belongs to the commentary.** The verse card
(`.modal-verse-translation`, `.ebook-translation`) shows the Arabic and the English
translation above the commentary, and it is **not** to be suppressed for guided verses —
the maintainer asked for it back on 2026-10-10 after a first attempt removed it, because
it is the reader's verse, not part of the generated commentary. What must not happen is
the *guidance* restating it: the lead quotes each phrase as it explains it, so the
compiler no longer emits the `>` line as an opening recitation and `verify_verse` refuses
a lead that opens with the whole verse. `tools/tests/guidance-001.js` asserts the guidance
card contains neither a recital of the whole translation nor any verse-card markup.
Freshness is a separate rule and stands: `data/*.json` is fetched network-first by
`sw.js`, `no-store` by the app, `updateViaCache: 'none'` at registration, and the preview
is served by `tools/serve.py` — a stale guidance file is indistinguishable from an
unpublished chapter.

**2. Then 3–6 headed sections.** Each heading is `**Like this.**` — bold, ending
with a full stop, **on its own line**, blank line, then its own paragraph.
Headings group the deeper material: what a word means, the readings on it, why
the scholars differed, whom the sources say it refers to.

Why own-line matters: `renderMarkdown` promotes an own-line `**bold**` block to
`<h4>`; inline `**bold**` stays `<strong>` and produces no heading.

`docs/style.md` is the spec and `data/guidance_002.json` is what conformance looks
like on the page. The cleared corpus (`d021eee`, `a2de9fe`, `d1e0609`) is history, not a
mine: do not copy content out of it.

**Three formats were tried and rejected** on 2026-10-09: a multi-paragraph layout,
then a single paragraph with inline `**bold**` signposts. Do not reinvent either.
If any other document here describes verse layout differently, `docs/style.md` wins.

---

## Length — the check is one-sided

Targets are in `data/plan.json` under `words`, generated from `BAND` in
`tools/tier_verses.py`: **A 1,300–1,900 · B 650–1,000 · C 300–450** (raised
The enforced floor is `plan["floor"]` = `round(words × 0.75)` — about 975 / 488 / 225 at
the band edges — and `plan["lead_floor"]` is the tier's lead minimum; `verify_verse.py`,
`style-check.js`, `compile_guidance.py` and `guidance-range.js` read those two numbers
rather than re-deriving them, so the rule has one implementation. A verse whose material
cannot meet its floor is **not** exempted: it is marked `authored_only` and composed
instead of spliced (see "Thin verses are authored-only"). **There is no ceiling.** A long
verse is fine and must never be trimmed; only under-length fails. Never hand-edit
`plan.json` — edit `BAND` or `LEAD_FLOOR` in `tools/tier_verses.py`, re-run the
classifier, and run `--verify` after.

```
python3 tools/progress.py --next      # next verse to write
python3 tools/tier_verses.py --verify # tier assignments
```

---

## Two ways to make a verse

**Compiled** — the default for volume, and the reason the project can run at all.
The sources' own sentences are spliced, with only gated connectives between them.

```bash
# 1. what the eight sets actually say, ranked and numbered
PACKET_CAP=4 PACKET_TRUNC=66 python3 tools/verse_packet.py 2 36-40
# 2. write the spec: ### 2:36 / ~ lead / ## heading / - REF lines / +auto N   (no `>` line needed)
python3 tools/fill_quotes.py /home/user/proto/b006.md   # inserts each verse's `> ` line verbatim
# 3. gate the draft, fix EVERY fail, gate again, only then write the payload
python3 tools/compile_guidance.py 2 /home/user/proto/b006.md --dry
python3 tools/compile_guidance.py 2 /home/user/proto/b006.md
# 4. the finished product, then the batch boundary
python3 tools/verify_verse.py 2 --range 36-40
node tools/tests/style-check.js
sed -i "s/const CACHE_VERSION = .*/const CACHE_VERSION = 'quran-reader-vX.Y.Z-2-40';/" sw.js
git add data/guidance_002.json sw.js && git commit && git push origin arena/525a7113-quran-explained
```

`PACKET_CAP` (sentences per set shown) and `PACKET_TRUNC` (words per sentence) only
shrink what the packet prints, never what the compiler will accept — 3/62 is a fast read
of a five-verse batch, 6/120 when a verse will not compile. Refs are **positional**
(`Q36.1.2` = qushayri, block 1, sentence 2), so re-dump a packet before compiling a spec
you did not just write. `fill_quotes.py` exists because typing the `> ` line is the one
ungated step in the loop. Patch a spec with `if a in s: s = s.replace(...)` and report
the misses: a script that `assert`s mid-way never reaches its `open(...,'w')`, so the
file is silently unchanged and the next gate looks like a regression.

The compiler refuses a spliced sentence that is not verbatim in that verse's own
blocks, refuses an unsourced word in a connective or heading, refuses attributive
and ruling verbs it cannot trace, drops a selection that only restates the
translation, caps connectives at 26 words (the pre-heading lead gets
`verify_verse.LEAD_CAP`, 620/460/320 by tier, because it has to quote and explain
every phrase), requires the tier floor and the lead's phrase coverage and order, and calls
`tools/verify_verse.check()` for layout — one implementation, not two.

What the gate actually rejects, learned compiling 1:1–1:7 and 2:1–2:35 on
2026-10-10 — all four are lead-authoring problems, not gate problems:

- **Connectives cannot contain a speech or ruling verb**, even an ordinary one:
  `said`, `says`, `holds`, `adds`, `notes`, `mentions`, `forbids` and `majority` are all
  refused in a `~` line and in a heading. Write `carries`, `is taken to be`, `puts it
  that`, `reads X as Y`. A refused lead is *dropped silently*, and the verse then fails
  the opening-paragraph gate with a misleading word count — read the whole message.
  **One exemption, and only one** (`tr_all` in `compile_guidance.py`): a refused word is
  allowed when that word is in the verse's *own translation*, because walking a verse
  phrase by phrase sometimes means writing `Remember when your Lord said to the angels`
  or `if what you say is true`, and the verse's word is not my attribution. Spliced
  source sentences are never an exemption. If a BANNED hit survives that, the verb is
  mine — reword it, do not quote around it.
- **A quoted phrase must survive the translation's own punctuation.** Coverage is
  checked canonically (case, diacritics and `˹…˺` stripped), so `Allah said, O Adam` in
  a lead covers `˹Remember˺ when your Lord said…`; but a 5-word run of raw `ayah_en` is
  also required, so quoting only `“O Adam”` fails. Quote the run as the translation
  prints it, `We cautioned, O Adam! Live with your wife in Paradise`, and a compound
  chunk cannot be split by an intervening clause — `…the disbelievers", whose difficulty
  is a question, "they argue…` does not cover `"the disbelievers, they argue"`.
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
disagreement, and **carry the 168 `authored_only` verses** whose material is thinner than
their floor — those are refused in compiled mode, so this is their only path. Runs of
**5–10** of them, on their own, not added to a compiled batch.

```bash
python3 tools/dump_sources.py 2 53 53   # everything the six-and-two sets say, ~12KB
# draft = the lead that walks the translation, then 3-6 headed sections, same layout
python3 tools/verify_verse.py 2 --range 53 --file /tmp/a053.txt --draws maarif,ibn-kathir,jalalayn,tanwir,tazkirul --names "Ibn ʿAbbās"
```

`--draws` is the set ids that go into the entry's `draws_on`; `--names` lists every
authority the draft cites, and the gate checks each one really appears in that verse's own
blocks — it is the only check that catches an invented citation, so never skip it in this
mode, where the prose is not spliced and nothing else constrains it. A thin verse is
explained longer, not padded: if the draft cannot reach the floor honestly, the sources
are the limit, and `docs/voice.md` says what to do about that.

Both modes are gated identically on layout, floor, lead and transliteration. Read
`docs/voice.md` before either.

---

## Before you commit — mandatory

```bash
python3 tools/verify_verse.py 1 --all                        # per-verse gate
node tools/tests/style-check.js                              # layout, floor, lead, transliteration
BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-range.js  # what the reader gets
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

Then report the batch to the maintainer as **counts and paths, not passages**: verses
compiled, words, `draws_on`, which gates went green, which commit. They read the finished
product in the preview, not the corpus and not a pasted entry — the one exception is when
they ask to see a verse. Do not paste a generated verse or a source block into the chat
unprompted, and do not open a second agent to go faster.

---

## Pace

**Standing instructions from the maintainer, in force every session:** one agent, no
fan-out, no parallel sessions, no API batch runner; every source set that covers a verse
is actually read for that verse; verbatim traceability over speed, with depth and length
expendable when they conflict; answers short; the corpus stays out of the chat.

**20–25 authored verses per run, or 40–60 compiled ones** (in practice **batches of 5**,
gated at the boundary and pushed there). The old 50-verse The 168 `authored_only` verses are worked in **runs of 5–10** on their
own — they cannot be compiled, so they are never slotted into a compiled batch to keep
the pace up.
authored target was withdrawn — it is the pace that produced the quote-stacking
which got the entire corpus cleared. Volume was the cause, not a side effect.

**Commit and push at the end of every batch**, not only of every session: `git push origin
arena/525a7113-quran-explained`. The remote branch is the only durable copy.

---

## Files

| file | |
|---|---|
| [`docs/style.md`](docs/style.md) | **the format — normative** |
| [`tools/examples/spec_2-31_2-35.md`](tools/examples/spec_2-31_2-35.md) | a worked spec that compiles clean — the shape to copy |
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
| `tools/serve.py`, `tools/fill_quotes.py` | the `no-store` preview server; pastes each verse's translation into a spec |
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
