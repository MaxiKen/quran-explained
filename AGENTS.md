# AGENTS.md — read this first

**You are continuing an in-progress project: a plain-English commentary on all
6,236 verses of the Qurʾān, synthesised from eight classical tafsīrs — six that
cover every verse and two selective ones that are read where they comment.**

Read this file completely before writing anything. Then read
[`docs/style.md`](docs/style.md) — it is the only normative format spec.

---

## Current state

| | |
|---|---|
| Written | **0 of 6,236 verses** |
| Chapter 1 (al-Fātiḥah) | cleared 2026-10-09 |
| Chapter 2 (al-Baqarah) | cleared 2026-10-09 |
| Chapter 112 (al-Ikhlāṣ) | empty placeholder file |
| **Resume at** | **1:1** — nothing is authored |
| Branch | `arena/525a7113-quran-explained` |

Everything previously authored was pulled the same day the length bands and the
opening-paragraph rule were raised, so that the layer is regenerated against the
current contract instead of being patched. All three payload files —
`data/guidance_001.json`, `_002.json`, `_112.json` — exist as empty
`{"verses": {}}` placeholders, so the reader's fallback to the tafsīr sets is the
path being exercised, and the payload contract is still asserted by
`tools/tests/style-check.js`. A chapter with no authored verses is legitimate.

## The eight source sets

Six sets cover every verse: Ibn Kathīr, Maʿārif-ul-Qurʾān, Tazkīrul Qurʾān,
Tanwīr al-Miqbās, al-Jalālayn, al-Mukhtaṣar. Two are selective and were added on
2026-10-09 to give the raised bands something to draw on: **al-Qushayrī**
(*Laṭāʾif al-ishārāt*, allusive/spiritual reading, 1,287 verses) and
**al-Wāḥidī** (*Asbāb al-nuzūl*, occasion of revelation, 431 verses).

Rules that go with them:

- Read **all eight** blocks for a verse; a set with no block there is absent, not
  thin. Never imply an occasion or an allusion the payload does not carry.
- `draws_on` needs **5+ sets at tiers A and B, 4+ at C**, capped by the number of
  sets that cover the verse (`tools/verify_verse.py`).
- al-Wāḥidī arrives only through the pollution guard in `docs/sources.md`: 395 of
  the upstream edition's 1,089 entries are his. Its isnād chains are cut by the
  packet and are never quoted or graded.
- Re-ingest with `python3 tools/build_sets.py qushayri wahidi` (it rebuilds the
  set, never merges into it), then re-run `tools/tier_verses.py` — a new source
  moves tier assignments, a new band does not.


Authoring order is **chapter 1 → 114**, sequentially. Do not jump ahead or work
by juzʾ.

---

## The format — this is a rule, not a preference

Every verse has **two parts**:

**1. A plain-English introduction that explains the verse.** ~90–160 words at
tier A, 60–120 at B/C. It says what the verse says, to whom it is addressed, and
what it is doing here — it is not a hook, and it may not be only a question.
Names **no scholar**. Uses **no technical term**. Assumes **no prior knowledge**.
A reader who stops here has understood the verse.

**2. Then 3–6 headed sections.** Each heading is `**Like this.**` — bold, ending
with a full stop, **on its own line**, followed by a blank line and its own
paragraph. Headings group the deeper material: what a word means, the readings
on it, why the scholars differed, whom the sources say it refers to.

Why own-line matters: `renderMarkdown` promotes an own-line `**bold**` block to
`<h4>`. Inline `**bold**` stays `<strong>` and does not produce a heading.

There is **no reference implementation in the data any more** — the layer is
empty. `docs/style.md` is the spec, and the git history has conforming examples
(`a2de9fe` for authored prose, `d1e0609` for compiled); read them for shape, do
not mine them for content.

### Three formats were tried and rejected

A multi-paragraph layout, then a single paragraph with inline `**bold**`
signposts. Both rejected by the maintainer on 2026-10-09. **Do not reinvent
them.** If any other document in this repo describes verse layout differently,
`docs/style.md` wins.

---

## Length — the check is one-sided

Per-verse targets are in `data/plan.json` under `words`, generated from `BAND`
in `tools/tier_verses.py` (A 1,300–1,900 · B 650–1,000 · C 300–450 as of
2026-10-09). **The floor is 75% of target. There is no ceiling.** A long verse
is fine and must never be trimmed to fit. Only under-length is a failure.

```
python3 tools/progress.py --next      # next verse to write
python3 tools/tier_verses.py --verify # tier assignments
```

---

## Workflow per verse

```bash
python3 tools/dump_sources.py 2 29 34      # every source, max 6 verses, truncates ~12KB
```

Synthesise from them. **Nothing invented.** A named authority must appear in
that verse's own source block at that verse's range — grep the blob before
citing. `draws_on` lists **only** the sources actually used.

Write into `data/guidance_NNN.json` as:

```json
"21": { "range": "2:21", "draws_on": ["maarif", "ibn-kathir"], "text": "..." }
```

---

## Before you commit — mandatory

```bash
python3 tools/verify_verse.py 2 --range 21-28          # per-verse gate (see below)
node tools/tests/style-check.js                        # format + length + transliteration
node tools/tests/sets-integrity.js                     # eight-set payload + the Asbāb guard
node tools/tests/sources-all.js                        # source payload integrity
python3 tools/build_sets.py qushayri wahidi --dry       # re-ingest an added edition
NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-001.js   # app render (needs jsdom)
```

All must pass. Read the `N/N checks passed` line — **never trust the exit
code alone.**

`tools/verify_verse.py` is the per-verse gate: it checks the house layout, the
tier floor, transliteration, Cyrillic homoglyphs, that the verse quotes 5+
consecutive words of the app's own `ayah_en`, that `draws_on` names 4+ real
sources, and — with `--names` — that **every authority cited occurs in that
verse's own source blocks**. Run it on a draft *before* writing it into the
payload (`--file`) and on the payload after (`--range`); it is the only check
that catches an invented citation before it is committed.

Then **post one full verse in the chat for review** before committing the batch.

---

## Pace

**About 20–25 verses per run.** An earlier 50-verse target was **withdrawn** —
it is the pace that produced the quote-stacking which got the entire corpus
cleared. Volume was the cause, not a side effect.

**Commit and push at the end of every session.** The sandbox workspace has been
reset four times, destroying the local tree. Everything survived only because it
had been pushed:

```bash
git fetch origin arena/2c46b8a2-quran-explained && git reset --hard <sha>
```

`/tmp` does not survive a reset. Reinstall jsdom before the render tests:

```bash
mkdir -p /tmp/apptest && cd /tmp/apptest && npm install jsdom --silent
python3 -m http.server 8000 --bind 0.0.0.0   # from the repo root
```

---

## Files

| file | |
|---|---|
| [`docs/style.md`](docs/style.md) | **the format — normative** |
| [`docs/contracts.md`](docs/contracts.md) | JSON payload shapes |
| [`docs/pitfalls.md`](docs/pitfalls.md) | every trap found so far — read before scripting |
| [`docs/testing.md`](docs/testing.md) | how to run the suite |
| [`docs/sources.md`](docs/sources.md) | the eight tafsīrs, their provenance, and the Asbāb pollution guard |
| [`HANDOFF.md`](HANDOFF.md) | longer project history |
| `docs/batching.md`, `docs/progress.md` | **withdrawn / stale — do not follow** |

---

## Hard prohibitions

- Do **not** mine the cleared text at commit `d021eee`. Chapters 2 and 112 start
  fresh from the eight tafsīrs.
- Do **not** trim a verse to fit a length band. The target is a floor.
- Do **not** stack attributed blocks. Eight quoted extracts is not commentary.
- Do **not** change a payload shape without bumping `CACHE_VERSION` in `sw.js`.
- Do **not** type transliterated Arabic as literal Unicode in a script (assert no
  U+0400–U+04FF — Cyrillic homoglyphs have slipped in before).
