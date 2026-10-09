# Sources and provenance

Full licence text and upstream URLs are in [`ATTRIBUTION.md`](../ATTRIBUTION.md)
at the repo root. This file records the working knowledge a session needs.

## The six tafsīrs

100% coverage of all 6,236 verses across all six.

| id | source | author | words | verse-specific |
|---|---|---|---|---|
| `ibn-kathir` *(primary)* | Tafsīr Ibn Kathīr | Ḥāfiẓ Ibn Kathīr (d. 774 AH) | 6,281,305 | 30.5% |
| `maarif` | Maʿārif-ul-Qurʾān | Mufti Muḥammad Shafīʿ (d. 1396 AH) | 3,583,999 | 49.1% |
| `tazkirul` | Tazkīrul Qurʾān | Mawlānā Wāḥiduddīn Khān (d. 1442 AH) | 1,068,701 | 31.5% |
| `tanwir` | Tanwīr al-Miqbās | attributed to Ibn ʿAbbās (d. 68 AH) | 396,789 | 99.6% |
| `jalalayn` | Tafsīr al-Jalālayn | al-Maḥallī (d. 864 AH) & as-Suyūṭī (d. 911 AH) | 394,149 | 99.2% |
| `mukhtasar` | Al-Mukhtaṣar | Tafsīr Center for Qurʾānic Studies | 318,381 | 98.7% |

Totals: 12,043,324 words per-verse sum (**1.92×** the previous single-source
corpus), 5,041,691 deduplicated unique, 31 MB across 114 payloads.

**Read the "verse-specific" column before designing anything.** Ibn Kathīr is
the largest source but writes in long runs, so he tells you little about an
individual verse. The four ~99% sources are where per-verse signal lives — that
is why the classifier reads all six.

## Excluded, and why

Available in the upstream corpus but not shipped:

| source | reason |
|---|---|
| Kashānī | 26.7% verse coverage — too sparse |
| al-Tustarī | 14.2% verse coverage |
| Asbāb al-Nuzūl (al-Wāḥidī) | only 77 files, not per-verse structured |

There is **no English as-Saʿdī** in the upstream corpus. An Arabic one was
integrated early (`317b7e7`) and then replaced by Ibn Kathīr at the
maintainer's direction (`a4507ce`).

## Upstream

`spa5k/tafsir_api`, MIT, *Copyright (c) 2023 Spark*. The repo was redistributing
31 MB of it with no licence notice anywhere — an unmet MIT condition, closed by
`ATTRIBUTION.md` (`6547b4e`).

Per-edition provenance, from the upstream README:

| editions | host |
|---|---|
| Ibn Kathīr (35), Maʿārif (34), Al-Mukhtaṣar (266) | qul.tarteel.ai |
| Tazkīrul Qurʾān | quran.com |
| Tanwīr al-Miqbās, al-Jalālayn | altafsir.com |

**Those three hosts are not reachable from the sandbox** (egress allowlist:
github.com, codeload.github.com, api.github.com, registry.npmjs.org,
pypi.org, files.pythonhosted.org). Their redistribution terms are recorded in
`ATTRIBUTION.md` as the **maintainer's confirmation**, not as independently
verified. The maintainer confirmed: *"I have and it's all good."*

The upstream README records licences only where known — al-Jamīʿ al-Wajīz is
CC BY-ND 4.0 with "the wording is redistributed unchanged". It states no
separate licence for the six shipped here.

## Other reachable sources, if ever needed

- **`fawazahmed0/hadith-api`** — default branch is **`1`**, not `main`.
  `editions.json` is keyed by book (`bukhari, muslim, abudawud, tirmidhi,
  nasai, ibnmajah, malik, nawawi, qudsi, dehlawi`). Files
  `editions/eng-<book>/<n>.json` → `{metadata, hadiths}` with `hadithnumber`.
  This gives real, checkable numbers if a future requirement calls for citing
  ḥadīth by number rather than as the tafsīrs report them.
- **`mustafa0x/quran-morphology`** (branch `master`) — `quran-morphology.txt`,
  `morphology-terms-ar.json`. Word-level morphology, useful for a
  phrase-by-phrase translation-tracking layer.
- **`risan/quran-json`** — reachable.
- **`raw.githubusercontent.com` is NOT reachable.** Use `api.github.com`
  contents/blobs, or `git clone` / `git fetch`.

## Fonts

| font | licence text shipped |
|---|---|
| Noto Naskh Arabic | ✅ `fonts/OFL-NotoNaskhArabic.txt` |
| Amiri | ❌ annotation in `css/styles.css` only |
| Inter | ❌ annotation only |
| HAFS | ❌ annotation only |

The three missing licence texts should be added under `fonts/` **before
distribution**. `ATTRIBUTION.md` states this plainly — do not soften it.
