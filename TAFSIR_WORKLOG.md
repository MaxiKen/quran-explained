# Tafsir worklog

Progress ledger for the verse-by-verse corpus in `tafsir/`. Update it in the same commit that
finishes a chapter: run `python3 scripts/tafsir/status.py --md` for the numbers rather than
typing them from memory.

## The standard a chapter is written to

Set on 2026-09-23, after chapter 1 was rewritten to it. `scripts/tafsir/audit.py` enforces every
line of it:

| Rule | Value |
|---|---|
| Words per verse | floor `max(550, 7 × the verse's own words)`, capped 3,500; soft ceiling 4,500 |
| Introduction | 250–1,500 words |
| Phrase splitting | every phrase of the verse quoted as `**“phrase”**`, in verse order, ≥90% coverage, no gap over 8 words |
| Evidence | every verse carries checkable anchors; every prophetic report names its collection |
| Analogy | at least half the chapter's verses carry a simple, relatable comparison |
| Diction | plain English; formal vocabulary fails (`STY-DICTION`) |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% above 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |

## Progress

| Ch | File | Verses | Words | Min/Med/Max per verse | Analogy | Gate | Payload |
|---|---|---|---|---|---|---|---|
| 1 | `tafsir/001.md` | 7/7 | 6,290 | 748/845/1,140 | 7/7 | PASS | 47 KB |

Totals: **1 of 114 chapters written, 7 of 6,236 verses, 6,290 words.**

Standard version: **v2** (floor 550 / 7×, phrase coverage gate, analogy rule, plain-diction checks).
Chapter 1 was taken through v2 twice: 4,108 words at first pass, 6,290 after the second, which
added the source-level material listed below.

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

### Chapter 2 — Al-Baqarah (286 verses)

* Digest built for the whole chapter: `tmp/sources/002.txt` (13.8 MB) and `002.json` (85 MB, uncapped
  for writing; `sources.py` now takes `--cap-json` when a smaller digest is enough). All 286 verses
  have source material. The scaffold is in place with 1,362 phrase headings.
* **Written so far: the introduction and verses 2:1–2:94** (94/286) — the letters, the portrait of
  the believers and the hypocrites, the parable of the fire, the creation of Adam, the covenant with
  Israel, the manna, the rock, the cow, the murdered man and the raised dead, the broken covenants,
  the distortion of scripture and the claim to an exclusive hereafter, up to "wish for death" and the
  answer given in the next verse. Every verse carries its own analogy (89/89 in the 2:6–2:94 range);
  phrase coverage 97–99% a verse; per-verse words run from 560 to 2,164 against floors of 550–735.
* Batch gate for 2:6–2:94: `batch.py 2 --from 6 --to 94` → **PASS** (0 FAIL, 33 advisory `GRD-TOKENS`
  warnings about source-name tokens). Batch style for the range: mean sentence 21.5 words, 5% over 40
  words, Flesch 68, long words 0.47% — inside every threshold. `audit.py --all` reports the chapter as
  `in progress: 94/286 written, next 2:95`, and `build_data.py 2` refuses to publish it while scaffolds
  remain — so the app can never receive a half-written sūrah.
* The chapter is written batch by batch and the writer does not stop between batches
  (`TAFSIR_PROMPT.md` §10). Batch tooling: `batch.py N --from A --to B`, `batch.py N --progress`.
* No payload, no worklog row and no `sw.js` bump until the chapter passes the gate in full, so the
  app keeps showing "coming soon" for al-Baqarah.
* Next batches: 2:95–2:103 (the claim of an exclusive hereafter answered, then Gabriel and the
  accusation against Solomon), continuing in batches of four to six verses until `audit.py 2` passes.

## Conventions

* Chapter file: `tafsir/NNN.md`; payload: `data/tafsir_NNN.json`; digest: `tmp/sources/NNN.*`.
* Commit subject: `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`.
* Only chapters that pass `scripts/tafsir/audit.py` get a row here and a commit.

## Open items

* Chapter order is ascending, 001 → 114.
* The app shows "coming soon, in sha Allah" under verses whose chapter has no payload yet; this
  is expected until a chapter is written.
* Chapter 1 is the reference for the new standard. When a rule and chapter 1 disagree, the rule
  wins and chapter 1 is fixed.
