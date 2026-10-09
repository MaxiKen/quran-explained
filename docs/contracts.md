# Data contracts

Four payload types live in `data/`. Changing any of them has consequences
listed at the end — read those before editing a shape.

## `data/chapter_NNN.js` — the Qurʾān text (pre-existing, untouched)

A `.js` file assigning an array. Each sūrah object has `verses`, each verse has
`ayah_no_surah`, `ayah_ar`, `ayah_en`. **`ayah_en` is the translation the
commentary must quote** — the harness checks that the guidance contains its
actual wording.

## `data/tafsir_NNN.json` — the six-source evidence base (generated, committed)

```json
{
  "surah": 2, "lang": "en", "dir": "ltr", "primary": "ibn-kathir",
  "sources": [{"id": "...", "label": "...", "author": "..."}],
  "sets": {"<sourceId>": {"ranges": ["2:8-10"], "blocks": ["..."]}},
  "verses": {"8": {"ibn-kathir": 3, "maarif": 5, "tazkirul": 1,
                   "tanwir": 8, "jalalayn": 8, "mukhtasar": 7}}
}
```

`verses[<ayah>][<sourceId>]` is an **index** into that source's `blocks`, not
the text. Blocks are deduplicated, so many verses share one block; `ranges[i]`
says which verses `blocks[i]` covers.

Single-line JSON, ~31 MB across 114 files. Marked `-diff linguist-generated`
in `.gitattributes` because GitHub hides over-long lines and the diff renders
blank. **This has already caused a false alarm that the data was missing.**

The legacy single-source shape (no `sets`) is still handled by the accessors;
don't rely on it for new work.

## `data/guidance_NNN.json` — the authored layer

```json
{
  "surah": 2, "lang": "en", "dir": "ltr", "title": "Al-Baqarah",
  "verses": {
    "1": {"range": "2:1",
          "draws_on": ["maarif", "tazkirul", "mukhtasar", "jalalayn", "tanwir", "ibn-kathir"],
          "text": "..."}
  }
}
```

- `range` is rendered as the **first line** of the entry, in the form `2:1` or
  `2:8-10`. It is never spoken aloud.
- `draws_on` records which sources informed the verse. The harness requires 4+
  and that every id exists in the payload's `sources`.
- `text` is whitespace-normalised on write.
- **Pretty-printed on purpose** — these are the files a reviewer reads, and the
  app loads them with `res.json()` so whitespace is free.

**A missing file, or a missing verse inside a present file, is normal.** Both
resolve to no guidance and the app falls back to showing the six sources
directly. This is what makes incremental authoring safe — `data/guidance_002.json`
currently covers 7 of 286 verses.

## `data/plan.json` — the tier manifest (generated, committed)

```json
{"1:1": {"tier": "A", "words": 900, "score": 137.5, "tr_words": 9,
         "ar_words": 4, "max_specific": 8389, "n_specific": 4,
         "flags": [], "refrain": false}}
```

Minified, 871,814 bytes. **Do not pretty-print it** — that takes it to
1,292,195 bytes, over GitHub's 1 MB inline-display limit, which makes it
*less* viewable. This was tried and reverted.

Regenerate any time with `python3 tools/tier_verses.py`.

## Rendering contract

`renderCommentaryHtml(tafsir, text, ayahNum)` in `js/app.js`:

1. If guidance exists for that verse → `renderGuidanceHtml(...)` **followed by**
   `renderSourcesPanel(entries)`. Guidance is a
   `<section class="tafsir-entry tafsir-entry-primary tafsir-guidance" data-source="guidance">`
   labelled *"In plain words"*, with the range as its first child. The six
   sources go inside `<details class="tafsir-sources">`, indexed from 1 so none
   is marked primary.
2. Otherwise → the six entries render directly, index 0 marked
   `tafsir-entry-primary`.

`renderGuidanceHtml` returns `''` when the file is absent **or** the verse is
absent from a present file. Both paths are tested.

## Consequences of changing a shape

| change | also required |
|---|---|
| new `data/` filename prefix | update the cache regex in `sw.js` (`/\/data\/(?:tafsir_\|chapter_\|guidance_)/`) |
| any payload content change | bump `CACHE_VERSION` in `sw.js`, or browsers serve stale cached copies |
| `tafsir_NNN.json` shape | update `getVerseCommentary`, `getVerseCommentaryAll`, `getCommentaryRange` and `tools/dump_sources.py` |
| `guidance_NNN.json` shape | update `renderGuidanceHtml`, `loadGuidanceData`, `tools/author_template.py`, every harness |
