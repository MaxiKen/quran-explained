# Testing

Four harnesses in `tools/tests/`. Each boots the **real app** in jsdom against
a running static server and asserts against what it actually renders. No logic
is re-implemented in the harness — a test that copies the code it tests proves
nothing.

```bash
python3 -m http.server 8000 --bind 0.0.0.0     # from the repo root, in background
npm i jsdom --prefix /tmp/apptest               # /tmp does not persist between sessions
export NODE_PATH=/tmp/apptest/node_modules
for h in sources-all guidance-001; do           # jsdom harnesses (need the server)
  printf "%-16s " "$h:"; node tools/tests/$h.js 2>&1 | tail -1
done
node tools/tests/sets-integrity.js              # pure node, no server
node tools/tests/style-check.js                 # pure node, no server
```

Current: **sources-all 30/30 · sets-integrity 12/12 · style-check 3/3**, and
guidance-001 in contract-only mode (the chapter is empty, so it asserts the
payload shape and nothing about prose).

The guidance harnesses for sūrahs 2 and 112 went with the payloads they tested;
they come back when those chapters are re-authored — copy the closest one below.

| tool | scope |
|---|---|
| `tools/verify_verse.py` | per-verse gate: house layout, tier floor, transliteration, Cyrillic, `ayah_en` quote run, `draws_on`, and **every cited authority against that verse's own source blocks**. Run with `--file` before writing a draft, and on the payload after. |

| harness | scope |
|---|---|
| `sources-all.js` | eight-source payload, all 114 files, read-aloud path |
| `sets-integrity.js` | the two added sets: index integrity, the Asbāb pollution guard, coverage bounds |
| `guidance-001.js` | authored layer, sūrah 1 (currently empty → payload contract) |
| `style-check.js` | house format — `docs/style.md` rules 1, 2 and 4, all three files |

Plus `python3 tools/tier_verses.py --verify`, which exits non-zero if
classifier accuracy drops below 70% or severe misses exceed 3%.

## Adding a harness for a new sūrah

Copy the closest existing one:

- **fully authored sūrah** → copy `guidance-001.js`
- **partially authored** → copy `guidance-002.js`

Change: `S`, `LO`, `HI`, `LAST`; the translation-fragment `pairs`; and the
`NAMES` list of authorities you cited.

## What the guidance harnesses check

- the file loads and covers exactly the verses claimed
- every entry has a correct `range` and its `draws_on` meets the tier rule (5+ at
  A and B, 4+ at C, capped by the sets covering the verse)
- **every verse's length meets its `data/plan.json` floor** — 75% of the target. One-sided: running long passes, running short fails
- **the guidance quotes the app's own stored `ayah_en` wording** — explicit
  fragment assertions, not a vague similarity check
- guidance renders first, labelled "In plain words", range as its first line
- every source with text on the verse folds behind `<details class="tafsir-sources">`
- modal and ebook both carry it
- **attribution integrity** (below)
- a sūrah with no guidance still renders every source that has text, directly

## Attribution integrity — the check that matters most

Every narrator and collector named in the guidance is confirmed to appear in
that verse's own source text. This is what stops synthesis sliding into
fabrication.

Three subtleties, each learned the hard way:

1. **Diacritics.** The sources write plain ASCII — `Imam Ahmad`, `Ibn \`Abbas` —
   while the commentary uses `Imām Aḥmad`, `Ibn ʿAbbās`. The matcher folds NFD
   combining marks and hamza variants, and **strips all spaces** so that
   `Mas'ud` and `Masʿūd` both become `masud`.
2. **Romanisation variants.** Some names genuinely differ: `Ibn Marduwayh` is
   `Ibn Marduwyah` in Ibn Kathīr; `Murrah al-Hamadhānī` is `al-Hamadani`. These
   go in the `VARIANTS` map, matched against both spellings. Do not silently
   widen the matcher instead — a variant map is auditable, a fuzzy matcher is not.
3. **Cross-verse citations.** Prose sometimes says "recorded by Ibn Kathīr at
   2:4". The matcher therefore parses `N:M` references out of the guidance and
   folds those verses' sources into the blob.

The tafsīr **titles** are *not* checked against body text — a work does not
cite itself. They are matched against the payload's `sources[].label`.

## The control sūrah is chosen dynamically

The fallback checks need a sūrah with no guidance. **Do not hard-code one.**
Hard-coding sūrah 1 broke `guidance-112.js`; hard-coding sūrah 2 broke
`guidance-001.js`. Both now pick the first sūrah that genuinely has no guidance
file:

```js
const CTL = await w.eval(`(async()=>{
  for (const n of [3,4,5,6,7,8,9,10,11,12]) {
    if ((await loadGuidanceData(n)) === null) return n;
  }
  return 0;})()`);
```

If that ever returns 0, every sūrah in the list has been authored — extend the
list rather than pinning a number.

## jsdom setup notes

- `window.fetch` does not exist in jsdom — stub it in `beforeParse` to proxy to
  the static server.
- `window.matchMedia` does not exist either — stub it.
- Suppress CSS parse noise when counting errors:
  `errs.filter(e => !/Could not parse CSS|Not implemented/i.test(e))`.
