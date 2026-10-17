# Attribution and licensing

## Commentary texts

The reader's tafsīr is Tafsīr al-Ṭabarī — see the section below. The eight
English tafsīrs it used to carry in `data/tafsir_NNN.json` were taken from
[spa5k/tafsir_api](https://github.com/spa5k/tafsir_api), which is distributed
under the MIT License, and were removed from the reader on 2026-10-17. Their
text is still reproduced, in derived form, in `data/guidance_NNN.json`: the
plain-English commentary was written from them. Their attribution therefore
still travels with this repository, and per the terms of that license the
copyright notice and the permission notice are reproduced below in full.

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
resource identifier used by that project. These ids are the ones a guidance
entry's `draws_on` field still lists.

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
word of any commentary. The reader itself no longer ships these eight; what
survives of them is the derived plain-English commentary described further
down.

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

## Plain-English commentary (derived layer)

`data/guidance_NNN.json` carries a commentary written for this app, one entry
per verse and one introduction per sūrah, shown under the label
"Plain-English commentary" with the note "written with AI assistance from
eight classical tafsīrs · the reader now carries al-Ṭabarī in full, below".

- It is a **derived work of the eight tafsīrs above**: every entry is written
  from, and only from, the material those sources give for the verse, by the
  pipeline in `tools/guidance/` (a large language model writes each entry
  from the sources; deterministic checks and an audit pass verify coverage,
  wording and originality). No entry names the works or their authors; the
  text speaks in one integrated voice and keeps the Companions, early
  scholars, hadith collectors and gradings exactly as the sources give them.
- The wording is original: no run of twelve or more words is copied from a
  source outside an explicit quotation. The sources it draws on for each
  verse are listed in the entry's `draws_on` field. Those eight sources are no
  longer carried by the reader, so the field is a record of provenance, not a
  pointer to text in this repository; the tafsīr shown under the entry is
  Tafsīr al-Ṭabarī, which the commentary was not written from.
- The commentary is **not** a translation of any of the eight works and
  should not be cited as one. Where the sources differ, the entry says so;
  where a report is graded weak by a source, the grading is kept.
- Each file records the generation date, model and pipeline version in its
  `generated` field. Generated entries that did not pass the checks are left
  out of the file, so the app falls back to the tafsīr for those verses.

Anyone reusing the derived commentary should carry this notice and the
attribution of the underlying tafsīr texts above with it.

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
