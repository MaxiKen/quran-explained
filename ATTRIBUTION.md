# Attribution and licensing

## Commentary texts

The reader's tafsīr is Tafsīr al-Ṭabarī — see the section below. The eight
English tafsīrs it used to carry in `data/tafsir_NNN.json` were taken from
[spa5k/tafsir_api](https://github.com/spa5k/tafsir_api), which is distributed
under the MIT License, and were removed from the reader on 2026-10-17. The
plain-English commentary that was written from them went with them: **no part
of these eight works is in this repository any more.** They are recorded here
for the history, and per the terms of that license the copyright notice and
the permission notice are reproduced below in full.

```
MIT License

Copyright (c) 2023 Spark

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Per-source provenance

Recorded from the source table in the spa5k/tafsir_api README. The `id` is the
resource identifier used by that project. These ids were the ones a guidance
entry's `draws_on` field listed.

| Payload `id` | Work | Author | Upstream |
|---|---|---|---|
| `ibn-kathir` | Tafsīr Ibn Kathīr | Ḥāfiẓ Ibn Kathīr (d. 774 AH) | https://qul.tarteel.ai/resources/tafsir/35 |
| `maarif` | Maʿārif-ul-Qurʾān | Mufti Muḥammad Shafīʿ (d. 1396 AH) | https://qul.tarteel.ai/resources/tafsir/34 |
| `tazkirul` | Tazkīrul Qurʾān | Mawlānā Wāḥiduddīn Khān (d. 1442 AH) | https://quran.com/ |
| `tanwir` | Tanwīr al-Miqbās min Tafsīr Ibn ʿAbbās | attributed to Ibn ʿAbbās (d. 68 AH) | https://www.altafsir.com/ |
| `jalalayn` | Tafsīr al-Jalālayn | Jalāl al-Dīn al-Maḥallī (d. 864 AH) & Jalāl al-Dīn as-Suyūṭī (d. 911 AH) | https://www.altafsir.com/ |
| `mukhtasar` | Al-Mukhtaṣar fī tafsīr al-Qurʾān al-karīm | Tafsīr Center for Qurʾānic Studies | https://qul.tarteel.ai/resources/tafsir/266 |
| `qushayri` | Laṭāʾif al-Ishārāt | Abū al-Qāsim al-Qushayrī (d. 465 AH) | https://www.altafsir.com/ (upstream edition id 108, `en-al-qushairi-tafsir`) |
| `wahidi` | Asbāb al-Nuzūl | al-Wāḥidī (d. 468 AH) | https://www.altafsir.com/ (upstream edition id 86, `en-asbab-al-nuzul-by-al-wahidi`) |

The spa5k/tafsir_api README records explicit per-work licences only where they
are known (for example al-Jamīʿ al-Wajīz is noted as CC BY-ND 4.0, wording
redistributed unchanged). It does not state a separate licence for the eight
works above; their upstream terms are held by the projects listed. Those terms
have been checked and confirmed by the maintainer of this reader.

The commentary texts are reproduced unedited. No paraphrase, abridgement or
rewording has been applied to any of them, with two exceptions on the two
editions added on 2026-10-09: those were (i) filtered, because the upstream
Asbāb file is polluted with al-Qushayrī's text and only the 395 entries that can
be attributed to al-Wāḥidī with certainty are shipped, and (ii)
punctuation-normalised, because the upstream files carry `U+FFFD` where a decode
step lost Arabic punctuation marks. Neither filter nor normalisation changes a
word of any commentary. The reader no longer ships these eight, and nothing
derived from them survives either.

## Tafsīr al-Ṭabarī — the reader's tafsīr

`data/tafsir_NNN.json` carries *Jamiʿ al-bayān ʿan taʾwīl āy al-Qurʾān* — the
commentary of Imām Abū Jaʿfar Muḥammad ibn Jarīr al-Ṭabarī (d. 310 AH /
923 CE) — in two layers for every one of the 6,236 verses: the complete English
translation, and underneath it the Arabic original of the same commentary. Both
are taken from [tafseerquran.com](https://tafseerquran.com/en), with the
permission of the site's owner. The site publishes the text free to read,
search and keep offline, and its `robots.txt` allows the tafsir pages to be
crawled.

The text is imported by `tools/tabari/` and is reproduced unedited, as the
paragraphs the site publishes it in. The only thing taken out is what is not
part of the commentary: the previous/next ayah links and the site footer. The
Arabic original, which the site keeps behind a collapsed "Show original
Arabic" panel, is now carried as well — it is the text of record, and the
publisher's own caveat says so.

One presentational normalisation is applied, and it changes no word. The site
keeps its text in markdown and renders it without handling the escapes, so the
published page shows them: the section divider of the printed edition arrives
as `\* \* \*`, a quotation mark as `\"`, a footnote reference as `\[…\]`, and
in one passage a paragraph break as the two characters `\n`. Those escapes are
resolved here, and a divider becomes a horizontal rule, which is what it is in
the printed edition.

The English is a translation, made with AI assistance, of the Arabic of the
Dar al-Tarbiya wa-l-Turath edition (the taḥqīq of Maḥmūd Shākir) as published
by quran.com and verified against app.turath.io. The publisher's own caveat
travels with the text and is shown in the app under the Tabari entry:

> The Arabic source text is always authoritative. This translation is a study
> aid and has not been verified by scholars — do not use it as a basis for
> religious proof or for deriving rulings (ahkam). When in doubt, always
> consult the Arabic text and a qualified scholar.

Anyone reusing this translation should carry that notice with it, and should
treat the Arabic as the text of record.

## Fī Ẓilāl al-Qurʾān (Urdu) — the Simple view

The reader's **Simple** view is Fī Ẓilāl al-Qurʾān (In the Shade of the
Qurʾān) by Sayyid Quṭb (1906–1966), in an Urdu rendering. The text is imported
from the `tafsir-fe-zalul-quran-syed-qatab` edition in
[spa5k/tafsir_api](https://github.com/spa5k/tafsir_api) into
`data/qutb_NNN.json` by `tools/qutb/` — one passage per run of verses, not the
upstream file's copy per verse.

- **Licence.** The `tafsir_api` repository is MIT licensed, which covers its
  own code and packaging. The underlying work is not the repository's to
  license: Fī Ẓilāl al-Qurʾān was published by Sayyid Quṭb between 1952 and
  1966, and its Urdu rendering is a separate translation of the Arabic. The
  copyright in the tafsīr text and in the Urdu translation rests with their
  respective rights holders; this project claims no licence over either and
  carries the text on the basis on which the upstream distribution offers it.
  Anyone republishing this data beyond its present use should settle the
  position with the rights holders first.
- **Status of the content.** The text is Quṭb's own and is presented exactly as
  the source carries it: it is not a translation of the Qurʾān, not this
  project's creed, and not a substitute for a qualified teacher. The same
  upstream project records that this edition was withdrawn from its default
  distribution after users raised objections about the author's ʿaqīdah
  ([spa5k/tafsir_api#25](https://github.com/spa5k/tafsir_api/issues/25)); the
  reader shows the source's own text with a notice on the page rather than
  editing it, so a reader can weigh what a scholar of that school wrote in its
  own words.

`data/saadi_NNN.json` — Tafsīr as-Saʿdī in Arabic, which held the Simple view
until 2026-11-08 — has been removed from the repository, together with the
`tools/saadi/` English-generation brief that was written for it.


## Plain-English commentary (withdrawn)

This reader carried a second layer for a while: a commentary written for the
app — one entry per verse, one introduction per sūrah — shown under the label
"Plain-English commentary" above the tafsīr. It was a **derived work of the
eight tafsīrs above**: every entry was written from, and only from, the
material those sources give for the verse, by the pipeline in
`tools/guidance/` (a large language model writes each entry from the sources;
deterministic checks and an audit pass verify coverage, wording and
originality). It was never a translation of any of the eight, and it was not
a summary of Tafsīr al-Ṭabarī.

**It was withdrawn on 2026-10-17**, together with the eight sources it was
written from: the files are deleted, the reader no longer shows the layer, and
the tafsīr stands alone — Tafsīr al-Ṭabarī in English with the Arabic
original underneath. The pipeline in `tools/guidance/` is kept for the record,
with its verification gates and its account of how the layer was made, and it
stops with an explanation rather than running against a corpus the reader no
longer carries.

Anyone who has a copy of the withdrawn commentary should carry this notice and
the attribution of the underlying tafsīr texts above with it.

## Fonts

| File | Face | Licence | Licence text bundled |
|---|---|---|---|
| `fonts/hafs.18.woff2`, `fonts/hafs.18.ttf` | KFGQPC Uthmanic Script HAFS v18 | King Fahd Glorious Qurʾān Printing Complex | no |
| `fonts/AmiriQuran-Regular.ttf` | Amiri Qurʾan | SIL Open Font License | no |
| `fonts/NotoNaskhArabic-Regular.woff2`, `fonts/NotoNaskhArabic-Bold.woff2` | Noto Naskh Arabic | SIL Open Font License 1.1 | **yes** — `fonts/OFL-NotoNaskhArabic.txt` |
| `fonts/NotoNastaliqUrdu-Regular.woff2`, `fonts/NotoNastaliqUrdu-SemiBold.woff2` | Noto Nastaliq Urdu | SIL Open Font License 1.1 | **yes** — `fonts/OFL-NotoNastaliqUrdu.txt` |
| `fonts/Inter-Variable.ttf` | Inter | SIL Open Font License | no |

The Noto Naskh Arabic and Noto Nastaliq Urdu licence texts are present in the
repository; each was added with its font. Noto Nastaliq Urdu is used for the
Urdu of the Simple view, and its licence text is `fonts/OFL-NotoNastaliqUrdu.txt`.
The licence attributions for Amiri Qurʾan and Inter are the ones already
recorded in `css/styles.css` where those faces are declared, and the HAFS
attribution is the one recorded there for that face — none of the three has its
licence text bundled here. The SIL Open Font License asks that the licence
travel with the font, so if this reader is distributed rather than served,
those three licence texts should be added under `fonts/` before release.

## Verse text and recitation

Verse text (`ayah_ar`) is the KFGQPC Unicode Uthmanic script. Per-verse audio
URLs are carried in `data/chapter_NNN.js`; audio is served from `everyayah.com`.

## The English translation

`ayah_en` in `data/chapter_NNN.js` is the **Saheeh International** English
translation of the Qurʾān, published by the **Noor International Center** and
distributed through **QuranEnc.com** under the key `english_saheeh` (edition
1.1.2). It is carried complete for all 6,236 verses of all 114 sūrahs.

- **Source of the text.** `data/quranenc/english_saheeh.json` from the
  `risan/quran-json` project, which republishes the QuranEnc editions and states
  that QuranEnc material is republished "unmodified, credit the publisher and
  QuranEnc.com with the version number, keep up to date".
- **What was changed.** Footnote reference markers (`[98]`) and the leading
  verse number (`(255)`) are stripped, since the reader already numbers its
  verses and does not display footnotes. The footnote *text* is therefore not
  shipped. No word of the translation itself is altered, added or reordered.
  The bracketed words and phrases inside the translation — `[All]`,
  `[due]`, `[i.e., your forefathers]` — are part of the published text and are
  reproduced as published.
- **What remains open.** The translator and publisher hold the copyright in the
  translation text. This project claims no licence over it. As with the
  commentary sources above, the basis on which it is carried is that this reader
  is one person's private copy, served to that person's own devices, not
  published, sold or offered to the public. Anyone who takes this repository
  beyond that use should settle the position with the publisher first.

The "Clear teaching" payloads quote this translation word for word inside every
entry by design (`STYLE.md` §4), so they carry the same text and the same
position applies to them.

### Earlier translation

Until 2026-11-08 `ayah_en` carried **The Clear Quran®** by Dr. Mustafa Khattab
(© 2015, all rights reserved). It was replaced for licensing reasons: that
edition is not openly licensed, is not the similarly named *Clear Quran* of
Talal Itani (which is CC BY-ND 4.0), and Quran.com states that permission for it
must be sought from the author. It is no longer present in this repository in
any form, including inside the "Clear teaching" entries, whose spans were
re-synchronised to the current translation and whose prose was revised wherever
it had been written around Khattab's specific wording.
