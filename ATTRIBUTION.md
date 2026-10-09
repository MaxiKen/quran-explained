# Attribution and licensing

## Commentary texts

The six English tafsirs carried in `data/tafsir_NNN.json` are taken from
[spa5k/tafsir_api](https://github.com/spa5k/tafsir_api), which is distributed
under the MIT License. Per the terms of that license, the copyright notice and
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
resource identifier used by that project.

| Payload `id` | Work | Author | Upstream |
|---|---|---|---|
| `ibn-kathir` | Tafsīr Ibn Kathīr | Ḥāfiẓ Ibn Kathīr (d. 774 AH) | https://qul.tarteel.ai/resources/tafsir/35 |
| `maarif` | Maʿārif-ul-Qurʾān | Mufti Muḥammad Shafīʿ (d. 1396 AH) | https://qul.tarteel.ai/resources/tafsir/34 |
| `tazkirul` | Tazkīrul Qurʾān | Mawlānā Wāḥiduddīn Khān (d. 1442 AH) | https://quran.com/ |
| `tanwir` | Tanwīr al-Miqbās min Tafsīr Ibn ʿAbbās | attributed to Ibn ʿAbbās (d. 68 AH) | https://www.altafsir.com/ |
| `jalalayn` | Tafsīr al-Jalālayn | Jalāl al-Dīn al-Maḥallī (d. 864 AH) & Jalāl al-Dīn as-Suyūṭī (d. 911 AH) | https://www.altafsir.com/ |
| `mukhtasar` | Al-Mukhtaṣar fī tafsīr al-Qurʾān al-karīm | Tafsīr Center for Qurʾānic Studies | https://qul.tarteel.ai/resources/tafsir/266 |

The spa5k/tafsir_api README records explicit per-work licences only where they
are known (for example al-Jamīʿ al-Wajīz is noted as CC BY-ND 4.0, wording
redistributed unchanged). It does not state a separate licence for the six
works above; their upstream terms are held by the projects listed. Those terms
have been checked and confirmed by the maintainer of this reader.

The commentary texts are reproduced unedited. No paraphrase, abridgement or
rewording has been applied to any of the six.

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
