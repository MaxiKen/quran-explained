# Tafsir worklog

Progress ledger for the verse-by-verse corpus in `tafsir/`. Update it in the same commit that
finishes a chapter: run `python3 scripts/tafsir/status.py --md` for the numbers rather than
typing them from memory.

## The standard a chapter is written to

Set on 2026-09-23, after chapter 1 was rewritten to it. `scripts/tafsir/audit.py` enforces every
line of it:

| Rule | Value |
|---|---|
| Sources | the **ten** of `corpus.SOURCE_ALLOWLIST` (al-Ṭabarī, al-Qurṭubī, al-Baghawī, Ibn Kathīr, al-Alūsī, al-Jalālayn, Ibn ʿAbbās, al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān); all ten pulled for every verse before it is written (`SRC-NOTCHECKED`, `SRC-NODIGEST`); at least five named in the prose, one classical + one modern (`SRC-SPREAD`, `SRC-FAMILY`); nothing outside the ten (`SRC-BANNED`) |
| Words per verse | floor `max(600, 8 × the verse's own words)`, capped 4,000; soft ceiling 5,000 |
| Introduction | 250–1,500 words |
| Headings | **UPPERCASE** descriptive titles of the writer's own (context, history, story, ruling, explanation) — never the verse's own wording (`FMT-HEADING-CASE`, `FMT-HEADING-QUOTED`, `FMT-HEADING-VERSE`) |
| Quoting style | this verse's own phrases in **bold italics** (`***“phrase”***`, enforced by `PHR-QUOTE-STYLE`); clauses of other verses in **bold only** inside their reference (`(C:V — **“clause”**)`, enforced by `REF-QUOTE-STYLE`) |
| Phrases | every phrase of the verse quoted **inside the prose**, in verse order, ≥90% coverage, no gap over 8 words, no single quote swallowing a verse (`PHR-*`); every quoted phrase backed beside it by a cross-reference, a hadith with its collection, or a named authority (`PHR-EVIDENCE`) |
| Evidence | every verse carries checkable anchors; every prophetic report names its collection |
| Analogy | at least half the chapter's verses carry a simple, relatable comparison |
| Diction | plain English; formal vocabulary fails (`STY-DICTION`) |
| Elements | history, reports with collections, cross-references, rulings, lesson, plain explanation, analogy and present-day application are carried by the prose and **never labelled** (`STY-LABELS`: no `Lesson:`, `Modern application:`, `History:`, …) |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% above 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |

## Progress

| Ch | File | Verses | Words | Min/Med/Max per verse | Analogy | Gate | Payload |
|---|---|---|---|---|---|---|---|
| 1 | `tafsir/001.md` | 7/7 | 8,559 | 1057/1249/1319 | 7/7 | PASS | `data/tafsir_001.json` |

Totals: **1 of 114 chapters written, 7 of 6,236 verses, 8,559 words.** Stdout for the row and the
numbers: `python3 scripts/tafsir/status.py --md`.

**Chapter 1 written to v4, 2026-09-24.** `tafsir/001.md` (7 verses, 8,559 words, 1,057–1,319 words a
verse against a floor of 600) plus `data/tafsir_001.json`, built by `build_data.py 1`. Written in two
stretches with the batch gate between them (`batch.py 1 --ranges 1-2`, then `batch.py 1`), each of the
ten works pulled into the per-verse digest first (`sources.py 1`) and at least six of the ten named in
each verse's prose. `audit.py 1` is clean: 0 FAIL, 0 WARN.

Two gate defects surfaced by this chapter and fixed in the same commit. `SRC-UNUSED` reported
al-Alūsī as never named although the chapter names him in five verses: the `AUTHORITY` pattern for
`tafsir-al-alusi` was written as `Al[ūs]i`, which cannot match the name's two letters (`ū` then `s`
before the `ī`), so the fix is `Alū? sī`. `GRD-TOKENS`, the advisory grounding check, treated the
names of the ten works, the hadith collections and ordinary capitalised English words (*the Book*,
*the Mother of the Book*, *Muslim*) as unverified named entities, which is a script artefact: nine of
the ten works for these verses are in Arabic, so a Latin transliteration can never be found in the
haystack. The check now skips the name-parts of the ten, the collections they cite and a short list of
ordinary capitalised vocabulary; a probe with invented authorities (*Zamakhshari of the Mu'tazila*,
*the University of Whitfield*, *the manuscript of Tabriz*) still reports every one of them.

**Corpus cleared, 2026-09-24.** `tafsir/001.md`, `tafsir/002.md` and `tafsir/003.md` were deleted
with the payloads `data/tafsir_001.json` and `data/tafsir_002.json`, and `tafsir/` was left empty
(`tafsir/.gitkeep`) ahead of a revision of the standard. Chapters 1, 2 and 3 are therefore unwritten
again and are re-generated to the revised rule when it is agreed. The scripts, the source corpus
(`tafsir-*/`), the chapter data (`data/chapter_*.js`), the helpers and the notes below are retained.

**Format change, 2026-09-24 (v3).** Chapter 1 was cleared and the written part of chapter 2 with it,
and their payload deleted. The bold headings are descriptive titles again (as in the old commentary
on this site), not the verse's phrases. Each phrase of the verse is quoted *inside* the paragraph
that explains it, in verse order, and each quoted phrase is backed beside it by evidence — a Qur'an
cross-reference, a hadith with its collection, or a named authority. Not every heading carries a
phrase: context, history, reports and rulings are headings of their own. `audit.py` enforces this
mechanically (`FMT-HEADING-QUOTED`, `FMT-HEADING-VERSE`, `PHR-*`, `PHR-EVIDENCE`), batches are
produced and gated in parallel (`batch.py N --ranges A-B,C-D,E-F`), and the writer keeps several
stretches in flight — a short chapter is finished in a single pass. Chapter 1 was rewritten to v3
first; chapter 2 was written to the same standard in one continuous run and passed the gate on 2026-09-24 (2:1–2:286).

Standard version: **v4** (2026-09-24: the corpus is the ten works of `corpus.SOURCE_ALLOWLIST` and
nothing else — the other seventeen `tafsir-*` folders, including the Arabic duplicates of al-Jalālayn
and Ibn Kathīr, were deleted; all ten must be pulled for a verse before it is written and at least
five named in its prose; floor 600 / 8×, cap 4,000, soft ceiling 5,000; the named elements —
history, reports, cross-references, rulings, lesson, plain explanation, analogy, present-day
application — must be shown in the flow and never labelled, with the corpus cleared to v3's
files and re-written from scratch).

Earlier: **v3** (descriptive headings; phrases quoted in the prose and evidenced there;
floor 550 / 7×; analogy rule; plain-diction and sentence-length checks).

## Chapter notes

### Chapter 1 — Al-Fatihah

* Written from all 28 sources; every verse carries at least two kinds of evidence (Qur'an
  cross-reference, hadith with collection, named authority, language point).
* Phrase cuts: 1:1 into "In the Name of Allah" / "the Most Compassionate, Most Merciful"; 1:5 into
  "You ˹alone˺ we worship" / "and You ˹alone˺ we ask for help"; 1:7 into three phrases, one per
  road it names. Coverage 97–100% on every verse.
* Analogies: the basmalah as naming the owner of the river before the first stroke; praise as
  streams leading back to one spring; al-Raḥmān as rain on field and rock, al-Raḥīm as rain turned
  into harvest; the Day of Judgement as a market closed for its final audit; the worker who
  accepts the foreman's orders before asking for tools; the two ways of going astray as two
  travellers and one timetable.
* Sources that carried the weight: Ibn Kathir (names of the sūrah, the basmalah debate, the
  twenty-five words, the hadith of the divided prayer, al-Nawwās ibn Samʿān's parable of the
  straight path, the Āmīn material), al-Ṭabarī (the repetition argument on the basmalah, ʿibādah
  as humility, the reports on "those You have blessed" including the chain he grades weak),
  al-Qurṭubī (mercy paired with majesty, the iltifāt at verse 5), Maʿārif al-Qurʾān (guidance and
  its degrees, why the Day of Requital is named, *Bismika Allāhumma* before the basmalah was
  revealed), al-Mukhtaṣar, al-Jalālayn, al-Bayḍāwī, al-Zamakhsharī, al-Saʿdī, Tazkir al-Qurʾān and
  the study draft in `tafsir_initial/`.
* Disagreements reported rather than flattened: the basmalah as verse or divider; mālik/malik.
* Duplicate records in the English sources (four files carrying one Sufi passage at 1:1) were
  treated as a single witness and are not leaned on.
* Source quirks met while writing: al-Baghawī and as-Saʿdī repeat whole-sūrah material under every
  verse, and Ibn ʿUthaymīn's 1:1 section opens with a transcribed lecture, so sections were read,
  not trusted by position.
* Second pass (6,290 words, verses 748–1,140, floors 550): added the basmalah-as-verse reports
  (Ibn Sīrīn on Ubayy, Ibn Masʿūd and ʿUthmān; al-Dāraquṭnī's sound chain from Abū Hurayrah; Umm
  Salamah), its private names (al-Wāfiyah, al-Kāfiyah, asās al-Qurʾān, miftāḥ kull kitāb), Saʿīd
  ibn Jubayr's account of why it was recited aloud in Makkah and then quietly, Ibn Sīrīn's caution
  over the name Umm al-Kitāb against (13:39); the ḥamd/shukr distinction; the faʿlān/faʿīl grammar
  of al-Raḥmān and al-Raḥīm with the polytheists' confusion at (25:60); the full list of readings
  of mālik/malik from al-Baḥr al-Muḥīt; al-Saʿdī's picture of ranks dissolving on the Day; the
  iyyāka placement rule with al-Saʿdī's hasr note; al-Ṭabarī's reading of "guide us" as a request
  for firmness, with his ʿAbd Allāh ibn ʿAbbās report and its chain; the ʿUmar, Ibn al-Zubayr,
  ʿIkrimah and al-Aswad reading *ghayr al-maghḍūb ʿalayhim wa ghayr al-ḍāllīn*; the Wādī al-Qurā
  report of ʿAbdullāh ibn Shaqīq al-ʿUqaylī and Abū Dharr's question; ʿAdī ibn Ḥātim's report with
  its collections (Aḥmad, al-Ṭabarī, Ibn Ḥibbān, At-Tirmidhī ḥasan); and the Āmīn material from
  Wāʾil ibn Ḥujr, Abū Mūsā al-Ashʿarī, Abū Zuhayr an-Numayrī and ʿĀʾishah.
* **Mis-attribution removed in the second pass.** The first pass credited a saying on the three
  kinds of worship to al-Ṭabarī's report from Jaʿfar al-Ṣādiq. `scripts/tafsir/verify.py` shows
  the passage exists only in `tafsir_initial` (the Study Quran draft), with no chain, and not in
  al-Ṭabarī at all. It was deleted rather than re-worded. This is the failure mode the
  attribution law and `verify.py` exist to prevent: a claim that borrows authority it does not
  have.
* Style at the gate: mean sentence 20.7 words, 8% over 40 words, Flesch 70, long words 0.3%.
* Gate: `0 FAIL`, one advisory `GRD-TOKENS` warning (English source names such as "Al-Mukhtaṣar"
  do not appear literally in the Arabic digests — expected; the check is advisory by design).
* Phrase coverage 97–100% on every verse; no phrase of the chapter is left unexplained.

## In progress

### Chapter 1 — Al-Fatihah (7 verses)

* Rewritten to v3 on 2026-09-24, in a single pass: 7/7 verses, 6,557 words, floors 550 each, verse
  lengths 736–1,210. Gate: `audit.py 1` → **0 FAIL, 1 WARN**; batch style before the final trim:
  mean sentence 20.1 words, 7% over 40 words, Flesch 71, long words 0.36%; analogies 7/7.
* Headings are descriptive throughout (the line that opens the Book; is the basmalah a verse of the
  chapter; praise is a wider word than thanks; the readings behind the word; the turn from speaking
  about God to speaking to Him; the road that has no branches; the road named by the people who walk
  it; Āmīn, the seal the chapter ends on). The verse's own wording is quoted inside those
  paragraphs, and every quoted phrase is answered by evidence in the same paragraph or the next.
* The one warning is advisory: `GRD-TOKENS` on 1:4 flags Companion and reciter names (Ubayy ibn
  Kaʿb, Ibn Masʿūd, Muʿādh, Khalaf) that the verse's own slice of the digest does not spell out —
  they come from al-Baḥr al-Muḥīṭ's list of the readings, which the section names.
* Phrase coverage 100% on every verse (2/2, 2/2, 1/1, 1/1, 2/2, 1/1, 3/3), every quoted phrase
  evidenced, no verse quoted whole.
* Material carried over from the earlier version and restructured: the basmalah reports
  (al-Dāraquṭnī, Ibn Sīrīn, Uthmān and Ibn Masʿūd, Umm Salamah), the names of the line (al-Wāfiyah,
  al-Kāfiyah, asās al-Qurʾān, miftāḥ kull kitāb), Saʿīd ibn Jubayr on reciting it aloud, Ibn Mughaffal
  in the two Ṣaḥīḥs, al-Ṭabarī's explanation of ḥamd, the ḥamd/shukr distinction from al-Rāghib, the
  iyyāka rule with al-Zamakhsharī and al-Saʿdī, al-Ṭabarī's definition of worship as humility, the
  ḥadīth qudsī that divides the prayer, al-Ṭabarī on guidance as firmness with the Jibrīl report,
  al-Rāghib's degrees of guidance, an-Nawwās ibn Samʿān's parable of the path (Aḥmad), the ghayr
  al-maghḍūb recitation of ʿUmar and the Successors, ʿAdī ibn Ḥātim's report (Aḥmad, al-Ṭabarī, Ibn
  Ḥibbān, At-Tirmidhī ḥasan), and the Āmīn material (Wāʾil ibn Ḥujr, Abū Mūsā, Abū Zuhayr, ʿĀʾishah).
* Mis-attribution to keep out: the saying on three kinds of worship exists only in `tafsir_initial`,
  with no chain — it is not in al-Ṭabarī, and it is not in this chapter.
* Payload `data/tafsir_001.json` rebuilt (43 KB); `sw.js` `CACHE_VERSION` = `quran-reader-v2.5.33`.
* Quoting style applied to the chapter on 2026-09-24: headings uppercased, 31 cross-reference quotes
  moved to bold only, and 12 stretch of this verse's own phrases set in bold italics. `audit.py 1`
  still **PASS** (0 FAIL, 1 advisory warning).

### Chapter 2 — Al-Baqarah (286 verses)

* Digest built for the whole chapter: `tmp/sources/002.txt` (13.8 MB) and `002.json` (85 MB, uncapped
  for writing; `sources.py` takes `--cap-json` when a smaller digest is enough). All 286 verses have
  source material.
* Cleared on 2026-09-24 (2:1–2:141 had been written in the old phrase-heading format); the old text
  is in this branch's history. The v3 rewrite restarted with the introduction and **2:1–2:4** in a
  single pass, then continued straight on: **2:1–2:8** (831/932/786/704/636/789/677/860 words against
  floors of 550; phrase coverage 100% on each; analogies 8/8). Batch gate: `batch.py 2 --from 1
  --to 8` → **PASS** (0 FAIL, 4 advisory `GRD-TOKENS`); batch style mean sentence 21.6 words, 8% over
  40, Flesch 70. So far: the cut letters, the Book that leaves no room for doubt, the faith that
  trusts what the eye cannot see, the community that owns every scripture, the harvest behind the
  word for success, the two groups that follow the measuring line, and the hypocrites' half-truth.
  The chapter continues from 2:9.
* The chapter is written batch by batch, with several batches in flight at once, and the writer does
  not stop between batches (`TAFSIR_PROMPT.md` §1, §10). Batch tooling: `batch.py N --from A --to B`,
  `batch.py N --ranges A-B,C-D,E-F` (in parallel), `batch.py N --progress`.
* No payload, no worklog row and no `sw.js` bump until the chapter passes the gate in full, so the
  app keeps showing "coming soon" for al-Baqarah.

### Chapter 2 — Al-Baqarah

* All 286 verses written from the 28-source digest, gated by the whole-file auditor:
  `audit.py 2` → **0 FAIL, 139 WARN**, `RESULT: PASS`; word range 551/742/2,306, total 234,301
  words. Analogies 285/286 (2:217 has none that fits); the remaining warnings are the advisory
  `EVD-THIN` (a single kind of evidence in some verses), `GRD-TOKENS` (source-token checks) and
  `FMT-HEADING-VERSE` headings.
* Written in stretches of three to six verses in one continuous run: 2:1–2:8 first, then batches up
  to 2:286 with `batch.py 2 --from A --to B` after each stretch, and inline patches to
  `tafsir/002.md` (never re-running a wave script over an already-patched section) to clear the
  word floors and the `REP-SENTENCE`, `PHR-*` and `FMT-HEADING-VERSE` findings.
* Verse splits follow `audit.py`'s own phrase cutter, and every phrase of every verse is quoted
  inside the prose in bold italics and backed beside the quote by a cross-reference, a hadith with
  its collection, a named authority or a language point.
* Landmark verses: 2:255 (Ayat al-Kursi — the greatest verse of the Qur'an, recited at night,
  "sufficient for him" in Ṣaḥīḥ al-Bukhārī and Ṣaḥīḥ Muslim), 2:282 (the longest verse: debts on
  paper, the scribe, the witnesses, small and great sums), 2:256 (no compulsion in religion),
  2:275–281 (interest, the debtor's respite, the warning of war), 2:285–286 (the two verses sent
  out of the treasures of Paradise and the prayer that closes the sūrah).
* Payload `data/tafsir_002.json` (1.3 MB, 286 verses) built with `build_data.py 2`;
  `build_data.py --all --check` → **2 up to date, 0 stale**; `sw.js` `CACHE_VERSION` bumped to
  `quran-reader-v2.5.34`.

## Conventions

* Chapter file: `tafsir/NNN.md`; payload: `data/tafsir_NNN.json`; digest: `tmp/sources/NNN.*`.
* Commit subject: `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`.
* Only chapters that pass `scripts/tafsir/audit.py` get a row here and a commit.

## Open items

* Chapter order is ascending, 001 → 114.
* The app shows "coming soon, in sha Allah" under verses whose chapter has no payload yet; with the
  corpus cleared this is currently every chapter, and payloads return as each chapter passes the gate.
* No chapter is currently the reference for the standard; the revised rule will be the reference once
  it is agreed, and the first chapter written under it becomes the worked example.
* Next step: agree the revised standard, encode it in `scripts/tafsir/audit.py`, then write chapter 1
  as the first file under it.
