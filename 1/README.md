# Chapter 1 · al-Fātiḥah — source-by-source element extraction

This folder holds the **evidence layer** for chapter 1 of the TAFSIR book: the elements that each of
the eleven source works contains, extracted verse by verse as **(source → element) pairs**. The
per-source files are merged afterwards into a single master, where every element (the *head*) gathers
the evidence of all eleven sources on that verse.

## 1. Specification

| Item | Decision |
| :--- | :--- |
| Scope | Chapter 1 only (al-Fātiḥah, verses 1:1–1:7), plus the sūrah-level elements |
| Sources | The 11 folders: 6 Arabic + 5 English (listed in §3) |
| Unit | One file per source, named exactly after its folder; **all seven verses covered in each file** |
| Element list | The complete taxonomy of `../tafsir/elements.txt` — 6 sūrah-level, 17 verse-level |
| Language | Arabic sources are extracted into English |
| Fidelity | **Evidence verbatim with its citation** (Qurʾān clauses, ḥadīth wording, āthār, poetry, qirāʾāt); the source's own explanatory prose is condensed to its essential claim |
| Merge | `1/merged-chapter-1.md` — same element under one head, all sources gathered beneath it |

## 2. Conventions

* **Verse text.** Each verse section opens with the Arabic verse and an English rendering, marked
  `[context]`. This is the verse itself, not source material, and carries no source attribution.
* **Element heads.** `### V8 · Language, lexical & grammatical analysis (lughah · iʿrāb · balāghah)`.
  The `V`-numbers and `S`-numbers are the numbers of the list in `elements.txt`, so the merge is
  mechanical. Capitalised head names are stable across all eleven files.
* **Attribution.** Every block begins with the work in bold — `**As-Saʿdī.**` — so that when the merge
  gathers eleven sources under one head each item still names its own origin.
* **One passage, one head.** Where one passage could serve two elements, it is recorded once under the
  element that governs it; no passage is duplicated.
* **Cross-heads.** The second element a record serves is named inside it — `_Cross-heads: V11 — …_` — so
  that element is findable in the merge without the passage being filed twice.
* **Attribution lines.** In transmitted report-works (Tafsīr Ibn ʿAbbās, and the isnād material of
  Ṭabarī, Qurṭubī and Baghawī) the transmitter is named in the record, and V6 (āthār) is used as a head
  only where the whole report is the element, never to double-file an exposition that already has a home.
* **Coverage line.** Each verse section ends with `_Coverage: …_`, listing the elements that the source
  actually has for that verse. Elements not listed are the elements this source does not address — the
  record shows the silence rather than inventing filler.
* **Structural notes.** Where the corpus file mis-assigns or repeats material, the source file carries a
  `> Structural note` at the top stating exactly what was re-mapped, so every record can be traced back.

## 3. Source files and progress

| # | File | Source | Language | Verses 1:1–1:7 | Status |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `tafsir-al-alusi.md` | Rūḥ al-Maʿānī | Arabic | ✔ 1:1 (sūrah-level + basmalah; §4 defect — 1:2–1:7 absent from corpus) | done |
| 2 | `tafsir-al-baghawi.md` | Maʿālim al-Tanzīl | Arabic | ✔ 1:1–1:7 | done |
| 3 | `tafsir-al-jalalayn.md` | Tafsīr al-Jalālayn | English | ✔ 1:1–1:7 | done |
| 4 | `tafsir-al-qurtubi.md` | al-Jāmiʿ li-Aḥkām al-Qurʾān | Arabic | ✔ 1:1–1:7 | done |
| 5 | `tafsir-al-tabari.md` | Jāmiʿ al-Bayān | Arabic | ✔ 1:1–1:7 | done |
| 6 | `tafsir-as-saadi.md` | Taysīr al-Karīm al-Raḥmān | Arabic | **pilot** | done |
| 7 | `tafsir-ibn-abbas.md` | Tanwīr al-Miqbās (ascribed) | English | **pilot** | done |
| 8 | `tafsir-ibn-kathir.md` | Tafsīr al-Qurʾān al-ʿAẓīm | English | ✔ 1:1–1:7 | done |
| 9 | `tafsir-ibn-uthaymeen.md` | Tafsīr (lectures) | Arabic | ✔ 1:1–1:7 (re-mapped from the single lecture body) | done |
| 10 | `tafsir-maarif-ul-quran.md` | Maʿārif al-Qurʾān | English | ✔ 1:1–1:7 | done |
| 11 | `tafsir_initial.md` | The Study Quran (super-source) | English | ✔ 1:1–1:7 | done |
| — | `merged-chapter-1.md` | — | — | ✔ 1:1–1:7 (the eleven gathered under the element heads) | done |

## 4. Corpus facts that affect the extraction

One chapter, eleven files, four defects — all of them factual and all of them handled, never silently:

| File | Defect | Handling |
| :--- | :--- | :--- |
| `tafsir-as-saadi/001.txt` | The whole-sūrah commentary is repeated byte-identical under all seven verse headings | Repetition removed; material re-mapped to the verses the author's own `{n}` markers name |
| `tafsir-al-alusi/001.txt` | 1:2–1:7 are byte-identical (whole-sūrah text repeated); 1:1 is separate | Repetition removed; internal markers used to re-map |
| `tafsir-al-baghawi/001.txt` | All seven sections are byte-identical | As above |
| `tafsir-ibn-uthaymeen/001.txt` | All seven sections byte-identical; the body is one transcribed session — a ṣalāh / al-Fātiḥah lesson followed by the audience's questions — not a written per-verse tafsīr | Repetition collapsed once; the lesson's own order re-mapped into the sūrah-level heads and the seven verse heads (structural note in the file); the Takhrīj of the transcription's editor is marked *[ed.]* |
| `tafsir-al-jalalayn/001.txt` | The basmalah commentary is filed under `## 1:2` | Re-mapped to 1:1; the substitution note in 1:6–1:7 kept with its verses |

## 5. Element list used (from `../tafsir/elements.txt`)

**Sūrah-level:** S1 names & titles · S2 period & place of revelation · S3 verse, word & letter counts ·
S4 virtues & merits of the sūrah · S5 central theme & summary (maqāṣid) · S6 coherence & connection (munāsabah)

**Verse-level:** V1 text & translation · V2 running exposition (bayān) · V3 occasion of revelation ·
V4 Qurʾān cross-references · V5 prophetic traditions (ḥadīth) · V6 Companions & Successors (āthār) ·
V7 classical mufassirūn · V8 language, lexicon & grammar · V9 variant readings (qirāʾāt) · V10 juristic
rulings (aḥkām) · V11 creed & theology (ʿaqīdah) · V12 abrogation · V13 history, sīrah & parables ·
V14 spiritual purification & etiquette (tazkiyah · ādāb) · V15 wisdom & admonition (ḥikam · tadabbur) ·
V16 contemporary issues & application · V17 specific virtues & supplications (faḍāʾil · duʿāʾ)

## 6. The merged master (`merged-chapter-1.md`)

Built mechanically from the eleven files (458 KB / 5,158 lines): one head per element of `../tafsir/elements.txt`,
in the S/V order, with the sources' blocks gathered **verbatim** beneath it — each block keeping its own bold
attribution, so every item still names its origin. A head appears only where at least one source has material
for it; a source absent under a head is silent on that element (its own file's `_Coverage:_` line shows the
silence). The eleven `> Structural note`s are reproduced verbatim in the appendix, and the super-source's sigla
(*Q, Ṭ, Ṭb, …*) are kept inside its blocks. The merge was machine-made from the files in this folder, so it can
be regenerated at any time after a source file is revised.
