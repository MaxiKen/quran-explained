# Chapter 2 · al-Baqarah — source-by-source element extraction

This folder holds the **evidence layer** for chapter 2 of the TAFSIR book, on the same specification as
chapter 1 (`../1/README.md`): the elements that each of the ten source works contains, extracted as
**(source → element) pairs on a verse-by-verse basis**. The per-source files are merged afterwards into
`merged-chapter-2.md`, where every element (the *head*) gathers all ten sources on that verse.

## 1. Specification

| Item | Decision |
| :--- | :--- |
| Scope | Chapter 2 (al-Baqarah, 2:1–2:286), plus the sūrah-level elements |
| Sources | The same **10** folders as chapter 1 (5 Arabic + 5 English) |
| Unit | One file per source, named exactly after its folder; **all 286 verses covered in each file** |
| Element list | The complete taxonomy of `../tafsir/elements.txt` — 6 sūrah-level, 17 verse-level |
| Language | Arabic sources are extracted into English |
| Fidelity | **Evidence verbatim with its citation** (Qurʾān clauses, ḥadīth wording, āthār, poetry, qirāʾāt); the source's own explanatory prose is condensed to its essential claim |
| Merge | `merged-chapter-2.md` — same element under one head, all sources gathered beneath it |
| Working order | **Source-major**, as in chapter 1: one source is completed across the sūrah before the next begins; within a source the verses run in order |

## 2. Conventions

Identical to chapter 1 (`../1/README.md` §2): `### Vn · Head name` heads from the element list; bold
attribution opening every block; `*[context]*` verse line; `_Coverage:_` closing each verse section;
`_Cross-heads:_` where one passage serves a second element; `> Structural note` at the top of any file whose
corpus mis-assigns or repeats material.

## 3. The batching plan

286 verses are built in **15 batches of 20 verses** (the last of 6), so that progress is visible and the
files stay reviewable as they grow:

| Batch | Verses | Batch | Verses |
| :-: | :--- | :-: | :--- |
| B1 | 2:1–2:20 | B9 | 2:161–2:180 |
| B2 | 2:21–2:40 | B10 | 2:181–2:200 |
| B3 | 2:41–2:60 | B11 | 2:201–2:220 |
| B4 | 2:61–2:80 | B12 | 2:221–2:240 |
| B5 | 2:81–2:100 | B13 | 2:241–2:260 |
| B6 | 2:101–2:120 | B14 | 2:261–2:280 |
| B7 | 2:121–2:140 | B15 | 2:281–2:286 |
| B8 | 2:141–2:160 | | |

## 4. Source files and progress

| # | File | Source | Language | Progress | Status |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `tafsir-al-alusi.md` | Rūḥ al-Maʿānī | Arabic | S-level + B1 in progress (2:1–2:3 done) | **in progress** |
| 2 | `tafsir-al-baghawi.md` | Maʿālim al-Tanzīl | Arabic | — | pending |
| 3 | `tafsir-al-jalalayn.md` | Tafsīr al-Jalālayn | English | — | pending |
| 4 | `tafsir-al-qurtubi.md` | al-Jāmiʿ li-Aḥkām al-Qurʾān | Arabic | — | pending |
| 5 | `tafsir-al-tabari.md` | Jāmiʿ al-Bayān | Arabic | — | pending |
| 6 | `tafsir-as-saadi.md` | Taysīr al-Karīm al-Raḥmān | Arabic | — | pending |
| 7 | `tafsir-ibn-abbas.md` | Tanwīr al-Miqbās (ascribed) | English | — | pending |
| 8 | `tafsir-ibn-kathir.md` | Tafsīr al-Qurʾān al-ʿAẓīm | English | — | pending |
| 9 | `tafsir-maarif-ul-quran.md` | Maʿārif al-Qurʾān | English | — | pending |
| 10 | `tafsir_initial.md` | The Study Quran (super-source) | English | — | pending |
| — | `merged-chapter-2.md` | — | — | — | pending (after the ten) |

## 5. Corpus facts that affect the extraction (measured)

The chapter-2 corpus files carry **one defect, in seven of the ten verse-tagged works**: the API's verse
grouping means a single commentary block is filed under **each** of the verse headings it covers. The
repetition is never silently kept: it is collapsed once and the block is re-mapped to the verses its own
internal markers name (as in chapter 1). Measured on the raw files:

| Source file | Raw text | Unique text | Blocks | Blocks covering several verses |
| :--- | ---: | ---: | ---: | ---: |
| `tafsir-al-alusi/002.txt` | 2,384 KB | 2,374 KB | 283 | 3 |
| `tafsir-al-baghawi/002.txt` | 2,047 KB | 919 KB | 142 | 79 |
| `tafsir-al-jalalayn/002.txt` | 182 KB | 182 KB | 286 | 0 |
| `tafsir-al-qurtubi/002.txt` | 3,341 KB | 2,800 KB | 259 | 21 |
| `tafsir-al-tabari/002.txt` | 4,008 KB | 3,917 KB | 280 | 6 |
| `tafsir-as-saadi/002.txt` | 573 KB | 256 KB | 152 | 70 |
| `tafsir-ibn-abbas/002.txt` | 176 KB | 176 KB | 286 | 0 |
| `tafsir-ibn-kathir/002.txt` | 2,068 KB | 1,101 KB | 173 | 79 |
| `tafsir-maarif-ul-quran/002.txt` | 1,610 KB | 1,266 KB | 218 | 52 |
| **Total** | **17.1 MB** | **13.4 MB** | | |

Other facts:

* **al-Baqarah is complete in all ten works** — no missing-commentary defect like chapter 1's al-Alūsī
  gap. The sūrah-level material (names, Makkī/Madanī, counts, faḍāʾil, maqāṣid, munāsabah) sits inside each
  work's first section (`## 2:1` for the Arabic sources) and is extracted into the S-heads.
* **`tafsir_initial/002.md`** (The Study Quran) has no per-verse headings; its verses are block-quoted
  (`> **n** …`) with commentary numbered `**n**` and ranged (`**122–23**`), so its record is mapped from
  those markers.
  opens by recapitulating the Fātiḥah); 284 of 286 verses are headed, and the Q&A matter is handled as in
  chapter 1.

## 6. Element list used (from `../tafsir/elements.txt`)

**Sūrah-level:** S1 names & titles · S2 period & place of revelation · S3 verse, word & letter counts ·
S4 virtues & merits of the sūrah · S5 central theme & summary (maqāṣid) · S6 coherence & connection (munāsabah)

**Verse-level:** V1 text & translation · V2 running exposition (bayān) · V3 occasion of revelation ·
V4 Qurʾān cross-references · V5 prophetic traditions (ḥadīth) · V6 Companions & Successors (āthār) ·
V7 classical mufassirūn · V8 language, lexicon & grammar · V9 variant readings (qirāʾāt) · V10 juristic
rulings (aḥkām) · V11 creed & theology (ʿaqīdah) · V12 abrogation · V13 history, sīrah & parables ·
V14 spiritual purification & etiquette (tazkiyah · ādāb) · V15 wisdom & admonition (ḥikam · tadabbur) ·
V16 contemporary issues & application · V17 specific virtues & supplications (faḍāʾil · duʿāʾ)
