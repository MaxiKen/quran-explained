# Tafsīr al-Ṭabarī — importer

Tafsīr al-Ṭabarī in English, with the Arabic original underneath it, imported
from [tafseerquran.com](https://tafseerquran.com/en) into the reader's tafsir
payload: `data/tafsir_NNN.json`.

## Why the reader's own tafsir files

The reader used to carry eight classical tafsīrs in `data/tafsir_NNN.json`,
taken from [spa5k/tafsir_api](https://github.com/spa5k/tafsir_api). They are
gone: Tafsīr al-Ṭabarī is the reader's tafsīr now, in English, complete for
every verse of the Qur'an, with the Arabic text of the same commentary below
it. One payload file per surah, one source, the Arabic underneath.

So the importer writes the file the reader already loads — no merge step, no
second file to keep in step, and nothing for the app to special-case.

## Permission

The owner of tafseerquran.com has given this project permission to use the
translation. The site's `robots.txt` allows the tafsir pages
(`User-Agent: * / Allow: /`, with only `/auth/` and `/api/` excluded), and the
text itself is published for free reading, searching and offline use.

## What the importer does

`importer.py` fetches `https://tafseerquran.com/en/tafsir/<surah>/<ayah>` for
every ayah of the surahs listed in `plan.json` and writes one file per surah:

```
data/tafsir_NNN.json
{
  "surah": 1, "lang": "en", "dir": "ltr",
  "source": "Tafsīr al-Ṭabarī", "primary": "tabari",
  "sources": [ { "id": "tabari", "label": "Tafsīr al-Ṭabarī", "author": "..." } ],
  "notice": "The Arabic source text is always authoritative. ...",
  "arabicSource": { "id": "tabariAr", "label": "The Arabic original", ... },
  "sets": { "tabari":   { "ranges": ["1:1", ...], "blocks": ["...", ...] },
            "tabariAr": { "ranges": ["1:1", ...], "blocks": ["...", ...] } },
  "verses": { "1": { "tabari": 0, "tabariAr": 0 }, ... }
}
```

`primary` and `sources` say which source the reader shows; `sets.tabari` holds
the English and `sets.tabariAr` the Arabic, both addressed per verse the way
the reader addresses a source. A verse with no Arabic panel on the site still
gets an entry, so the mapping has no hole.

### The extraction

Every passage on the page is rendered as

```html
<div class="...">Full English translation of Tabari's text</div>
<div class="text-base"> <p>…</p> <p>…</p> … </div>
```

and the Arabic original sits behind a collapsed panel:

```html
<details><summary>Show original Arabic</summary>
<div dir="rtl" lang="ar" class="font-arabic …"> … </div></details>
```

The importer takes the `text-base` container for the English and the
right-to-left container for the Arabic, and nothing else — the ayah links and
the footer stay out. The English keeps the paragraphs the site publishes it
in, with the Arabic Qurʾānic quotations left inline inside their sentence.

The two containers are told apart by more than their class: the English one is
matched on its exact class attribute and the Arabic one on `dir="rtl"` and
`lang="ar"`, so the `text-base` token the Arabic container also carries can
never make one be read as the other.

### The escapes

The site keeps its text in markdown and renders it without handling the
escapes, so the published page shows them: the section divider of the printed
edition arrives as `\* \* \*`, a quotation mark as `\"`, a footnote reference
as `\[…\]`, and in one passage a paragraph break as the two characters `\n`.
The importer resolves those escapes and turns a divider into a horizontal
rule, which is what it is in the printed edition. No word is changed.

## Running it

The importer needs plain internet access. On a machine that can reach the
site:

```bash
python3 tools/tabari/importer.py --plan tools/tabari/plan.json --out data
python3 tools/tabari/verify.py --data data
```

`plan.json` lists the surahs to import. The GitHub Actions workflow
(`.github/workflows/tabari-import.yml`) does the same thing on a runner, which
has open internet, and commits the result to the branch it ran on: edit
`plan.json` and push.

Every fetched page is cached under `work/tabari/raw/`, so a re-run of a
surah that has already been fetched does not touch the site again. The site
is crawled politely: a few workers, a short delay between requests, and
retries with backoff.

## Checks

`verify.py` refuses a surah file when a verse is missing, a passage is empty
or too short, markup or site furniture is left in the text, the Arabic
original is missing or has no Arabic script in it, or the file disagrees with
the reader's own verse counts for that surah.

Over the whole corpus it also holds the import to the publisher's own
figures: 6,236 verses and 6,226 distinct passages — the number
tafseerquran.com publishes for the canonical layer. A partial import cannot
land on both.

## Notes on the text

The English is a translation, made with AI assistance, of the Arabic of the
Dar al-Tarbiya wa-l-Turath edition (the tahqiq of Maḥmūd Shākir) as published
by quran.com and verified against app.turath.io. The publisher's own caveat
travels with the text in the `notice` field and is shown in the app under the
Tabari entry:

> The Arabic source text is always authoritative. This translation is a study
> aid and has not been verified by scholars — do not use it as a basis for
> religious proof or for deriving rulings (ahkam). When in doubt, always
> consult the Arabic text and a qualified scholar.

The plain-English commentary in `data/guidance_NNN.json` was written from the
eight sources the reader used to carry, before Tafsīr al-Ṭabarī was imported.
It is a layer above the tafsīr, not a substitute for it, and the app says so.
