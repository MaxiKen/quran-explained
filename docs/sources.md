# Sources and provenance

Full licence text and upstream URLs are in [`ATTRIBUTION.md`](../ATTRIBUTION.md)
at the repo root. This file records the working knowledge a session needs.

## The eight tafsīrs

The first six cover 100% of all 6,236 verses. The last two, added 2026-10-09
with `tools/build_sets.py`, are selective works: they are read where they
comment, and absent where their author did not, which is what a selective
commentary looks like in the data.

| id | source | author | words | verse-specific |
|---|---|---|---|---|
| `ibn-kathir` *(primary)* | Tafsīr Ibn Kathīr | Ḥāfiẓ Ibn Kathīr (d. 774 AH) | 6,281,305 | 30.5% |
| `maarif` | Maʿārif-ul-Qurʾān | Mufti Muḥammad Shafīʿ (d. 1396 AH) | 3,583,999 | 49.1% |
| `tazkirul` | Tazkīrul Qurʾān | Mawlānā Wāḥiduddīn Khān (d. 1442 AH) | 1,068,701 | 31.5% |
| `tanwir` | Tanwīr al-Miqbās | attributed to Ibn ʿAbbās (d. 68 AH) | 396,789 | 99.6% |
| `jalalayn` | Tafsīr al-Jalālayn | al-Maḥallī (d. 864 AH) & as-Suyūṭī (d. 911 AH) | 394,149 | 99.2% |
| `mukhtasar` | Al-Mukhtaṣar | Tafsīr Center for Qurʾānic Studies | 318,381 | 98.7% |
| `qushayri` | Laṭāʾif al-Ishārāt | Abū al-Qāsim al-Qushayrī (d. 465 AH) | 311,598 | 3.4% (1,287 verses) |
| `wahidi` | Asbāb al-Nuzūl | al-Wāḥidī (d. 468 AH) | 82,505 | 0.9% (431 verses) |

Totals: 12,514,682 words per-verse sum (**1.99×** Ibn Kathīr alone), 32.9 MB
across 114 payloads. Effect on the deep verses, measured against the floors in
`data/plan.json`: tier A's median material/floor moved from 1.70× to 1.80×, the
share of tier A under 2× went from 62% to 58%, and the number of verses holding
less raw material than their own floor went from 195 to 164, and the floors of the 115 that truly cannot be met are now
capped at that material (`plan["floor"]`; see `AGENTS.md`, "Thin verses") That is a real gain
in the long Medinan sūrahs and none elsewhere: al-Qushayrī's three heaviest
sūrahs (2, 3, 4) hold 659 of his 1,287 entries.

**Read the "verse-specific" column before designing anything.** Ibn Kathīr is
the largest source but writes in long runs, so he tells you little about an
individual verse. The four ~99% sources are where per-verse signal lives — that
is why the classifier reads all eight (`SRC` in `tools/tier_verses.py`), and why
it tolerates a set having nothing on a verse instead of scoring the silence as
thinness.

## Excluded, and why

Available in the upstream corpus but not shipped:

| source | reason |
|---|---|
| Kashānī | 26.7% verse coverage — too sparse, and 27 of its chapter-2 entries are under 40 words |
| al-Tustarī | 14.2% verse coverage |

**Asbāb al-Nuzūl (al-Wāḥidī) was excluded on 2026-10-08 and is now included in a
guarded form** — see the next section. The Arabic-only editions (Qurṭubī,
Ṭabarī, *al-Kashshāf*, ʿĀshūr, Shawkānī, *al-Nashr* for the qirāʾāt) stay out on
purpose: the compiler splices a source's own English sentences, and an Arabic
block cannot be spliced into English prose. Using them would mean translating
them, which gives back the verbatim traceability the pipeline exists to keep.

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
| Al-Qushayrī (108), al-Wāḥidī (86) | added 2026-10-09 via `tools/build_sets.py` |
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

## Upstream damage, and the guard that came out of it

`en-asbab-al-nuzul-by-al-wahidi` is not a clean file. Of its 1,089 entries,
**693 open with text that belongs to `en-al-qushairi-tafsir`** and 120 repeat
themselves inside the same file. Ingesting it as it stands would print
al-Qushayrī's mystical prose under the heading "al-Wāḥidī — occasions of
revelation", i.e. a fabricated attribution shipped at scale.

`tools/build_sets.py` therefore keeps an Asbāb entry only if it

1. cites a `[surah:ayah]` of its **own** surah — the book's own structure, not a
   range guessed from its position; and
2. matches no al-Qushayrī entry for that surah, tested at two offsets because
   the pollution is not always at the start.

**395 of 1,089 entries survive**, spread over 431 verses. Every dropped entry is
dropped as *unattributable*, not as inconvenient. `tools/tests/sets-integrity.js`
asserts the guard holds on the shipped data, so a future re-ingest that loosens
it fails loudly.

Both editions also arrive with `U+FFFD` where the upstream decode lost Arabic
punctuation (26% of al-Qushayrī's entries, 36% of al-Wāḥidī's). The builder
strips the replacement characters and folds quotation marks to the corpus's own
convention. It does **not** repair wording: no paraphrase, no translation, no
reordering. What is stored is what the edition says, which is what makes a
spliced sentence provable.
