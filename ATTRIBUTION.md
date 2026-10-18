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

## Phrase-by-phrase explanations

`data/pairs_NNN.json` pairs pieces of the reader's English verse translation
with short, original explanations. The translation pieces reuse `ayah_en`;
the explanations are editorial material created for this reader and may add
illustrative or contextual detail where useful. They are not excerpts from,
or a replacement for, Tafsīr al-Ṭabarī, and are not a scholarly ruling.
Al-Fātiḥah (Surah 1), Al-Baqarah (Surah 2), Āl ʿImrān (Surah 3), and
An-Nisāʾ (Surah 4) have been published in this format; other surahs are not yet
authored.

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
| `fonts/Inter-Variable.ttf` | Inter | SIL Open Font License | no |

Only the Noto Naskh Arabic licence text is currently present in the repository;
it was added with the font. The licence attributions for Amiri Qurʾan and Inter
are the ones already recorded in `css/styles.css` where those faces are
declared, and the HAFS attribution is the one recorded there for that face —
none of the three has its licence text bundled here. The SIL Open Font License
asks that the licence travel with the font, so if this reader is distributed
rather than served, those three licence texts should be added under `fonts/`
before release.

## Verse text and recitation

Verse text (`ayah_ar`) is the KFGQPC Unicode Uthmanic script. English
translations (`ayah_en`) and per-verse audio URLs are carried in
`data/chapter_NNN.js`; audio is served from `everyayah.com`.
