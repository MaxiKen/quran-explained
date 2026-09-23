# Tafsir worklog

Progress ledger for the verse-by-verse corpus in `tafsir/`. Update it in the same commit that
finishes a chapter: run `python3 scripts/tafsir/status.py --md` for the numbers rather than
typing them from memory.

## The standard a chapter is written to

Set on 2026-09-23, after chapter 1 was rewritten to it. `scripts/tafsir/audit.py` enforces every
line of it:

| Rule | Value |
|---|---|
| Words per verse | floor `max(500, 6 × the verse's own words)`, capped 3,000; soft ceiling 4,000 |
| Introduction | 250–1,500 words |
| Phrase splitting | every phrase of the verse quoted as `**“phrase”**`, in verse order, ≥90% coverage, no gap over 8 words |
| Evidence | every verse carries checkable anchors; every prophetic report names its collection |
| Analogy | at least half the chapter's verses carry a simple, relatable comparison |
| Diction | plain English; formal vocabulary fails (`STY-DICTION`) |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% above 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |

## Progress

| Ch | File | Verses | Words | Min/Med/Max per verse | Phrase headings | Gate | Payload |
|---|---|---|---|---|---|---|---|
| 1 | `tafsir/001.md` | 7/7 | 4,108 | 502/594/729 | 14 | PASS | 30 KB |

Totals: **1 of 114 chapters written, 7 of 6,236 verses, 4,108 words.**

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
* Style at the gate: mean sentence 18.9 words, 5% over 40 words, Flesch 72, long words 0.4%.
* Audit: `0 FAIL, 0 WARN`. Payload built, `sw.js` bumped to `quran-reader-v2.5.28`.

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
