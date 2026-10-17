# Tafsīr al-Ṭabarī in English — importer

The English translation of *Jamiʿ al-bayān ʿan taʾwīl āy al-Qurʾān* (Tafsīr
al-Ṭabarī) that the reader carries as a ninth source, imported from
[tafseerquran.com](https://tafseerquran.com/en).

## Why a separate importer

The eight sources already in `data/tafsir_NNN.json` come from
[spa5k/tafsir_api](https://github.com/spa5k/tafsir_api) and are reproduced
unedited. Tafsīr al-Ṭabarī comes from a different publisher, with a different
licence position, so it is kept in its own files (`data/tabari_NNN.json`) and
merged into the surah's payload at load time. Nothing in the eight existing
sources is touched, and a surah without a Tabari file simply has no Tabari
source.

## Permission

The owner of tafseerquran.com has given this project permission to use the
translation. The site's `robots.txt` allows the tafsir pages
(`User-Agent: * / Allow: /`, with only `/auth/` and `/api/` excluded), and the
text itself is published for free reading, searching and offline use.

## What the importer does

`importer.py` fetches `https://tafseerquran.com/en/tafsir/<surah>/<ayah>` for
every ayah of the surahs listed in `plan.json` and writes one file per surah:

```
data/tabari_NNN.json
{
  "surah": 1, "lang": "en", "dir": "ltr",
  "source": { "id": "tabari", "label": "Tafsīr al-Ṭabarī", "author": "..." },
  "notice": "The Arabic source text is always authoritative. ...",
  "sets": { "tabari": { "ranges": ["1:1", ...], "blocks": ["...", ...] } },
  "verses": { "1": 0, "2": 1, ... }
}
```

The shape is the one the reader already uses for its tafsir payloads, so
`js/app.js` merges the file with a handful of lines and every existing view
(verse sheet, surah eBook, read-aloud) picks Tabari up without further change.

### The extraction

Every passage on the page is rendered as

```html
<div class="...">Full English translation of Tabari's text</div>
<div class="text-base"> <p>…</p> <p>…</p> … </div>
```

followed by a collapsed "Show original Arabic" panel, the previous/next ayah
links and the site footer. The importer takes the `text-base` container and
nothing else, so the Arabic original, the links and the footer stay out. The
text is kept as the paragraphs the site publishes it in, with the Arabic
Qurʾānic quotations left inline inside their sentence.

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
or too short, markup or site furniture is left in the text, or the file
disagrees with the reader's own verse counts for that surah.

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
other eight sources, before Tabari was added. The app says so where both are
shown.
