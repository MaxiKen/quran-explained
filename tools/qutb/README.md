# Fī Ẓilāl al-Qurʾān — importer

The reader's **Simple** view is Fī Ẓilāl al-Qurʾān (In the Shade of the
Qurʾān) by Sayyid Quṭb, in the **Urdu** rendering, for every verse of the
Qurʾān. The payload is `data/qutb_NNN.json`, imported from
[spa5k/tafsir_api](https://github.com/spa5k/tafsir_api), edition slug
`tafsir-fe-zalul-quran-syed-qatab`.

## Why this file and not the upstream one

Upstream ships the same passage once **per verse of a run**: al-Baqarah 2:1–5
is one discussion, stored five times. Copying that shape would put 43.5 MB in
the repository and show the same paragraphs five times in a row on screen. The
importer deduplicates each surah's passages and publishes the reader's own
shape — one block per distinct discussion, addressed by verse:

```
data/qutb_NNN.json
{
  "surah": 1, "lang": "ur", "dir": "rtl",
  "source": "Fī Ẓilāl al-Qurʾān — Sayyid Quṭb",
  "edition": "tafsir-fe-zalul-quran-syed-qatab",
  "sourceUrl": "https://github.com/spa5k/tafsir_api",
  "notice": "...",
  "blocks": ["<passage>", "<passage>", ...],
  "ranges": ["1:1", "1:2-7", ...],
  "verses": { "1": 0, "2": 1, ... }
}
```

`verses[n]` is an index into `blocks`; `ranges[i]` names the verses block `i`
covers. Runs are contiguous: a surah's passages appear in verse order and each
distinct passage is stored once, so the reader can render a run once, at its
first verse, instead of stacking duplicates.

## What the importer guarantees

- **Coverage.** Every verse the reader carries (6,236 across 114 chapters) maps
  to a block. A surah whose upstream file is incomplete fails the run rather
  than shipping a silent hole.
- **Verbatim text.** Passages are copied unchanged apart from trailing
  whitespace. Nothing is translated, summarised or reflowed; `blocks[i]` is
  exactly what the source says, paragraph breaks included.
- **Deterministic output.** Byte-identical input gives byte-identical output,
  so a re-run only touches files whose source changed.

## Running it

Plain Python 3.9+, standard library only. The source is fetched from a local
clone of `tafsir_api` so the run is reproducible and does not hammer GitHub:

```
git clone --depth 1 --filter=blob:none --sparse \
    https://github.com/spa5k/tafsir_api.git work/qutb/src
cd work/qutb/src && git sparse-checkout set tafsir/tafsir-fe-zalul-quran-syed-qatab && cd - 
python3 tools/qutb/importer.py --src work/qutb/src/tafsir/tafsir-fe-zalul-quran-syed-qatab --out data
python3 tools/qutb/verify.py --data data
python3 -m unittest discover -s tools/qutb/tests
```

The surah list is the reader's own: `js/chapters-meta.js`.

## Licence

`tafsir_api` is MIT (© its authors, see the upstream `LICENSE`), but that
licence covers the repository's own code and data packaging, not the
underlying work: Fī Ẓilāl al-Qurʾān is Sayyid Quṭb's, first published
1952–1966, and the Urdu rendering is a separate translation of it. The same
upstream repository notes that this edition was withdrawn from its default
distribution after objections were raised about the author's ʿaqīdah
(issue #25). `ATTRIBUTION.md` records this and the terms the reader applies.
