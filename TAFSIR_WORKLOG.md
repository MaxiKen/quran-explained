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
| Headings | descriptive titles of the writer's own (context, history, story, ruling, explanation) — never the verse's own wording (`FMT-HEADING-QUOTED`, `FMT-HEADING-VERSE`) |
| Phrases | every phrase of the verse quoted **inside the prose**, in verse order, ≥90% coverage, no gap over 8 words, no single quote swallowing a verse (`PHR-*`); every quoted phrase backed beside it by a cross-reference, a hadith with its collection, or a named authority (`PHR-EVIDENCE`) |
| Evidence | every verse carries checkable anchors; every prophetic report names its collection |
| Analogy | at least half the chapter's verses carry a simple, relatable comparison |
| Diction | plain English; formal vocabulary fails (`STY-DICTION`) |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% above 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |

## Progress

| Ch | File | Verses | Words | Min/Med/Max per verse | Analogy | Gate | Payload |
|---|---|---|---|---|---|---|---|
| 1 | `tafsir/001.md` | 0/7 | — | — | — | scaffold | — |
| 2 | `tafsir/002.md` | 0/286 | — | — | — | scaffold | — |

Totals: **0 of 114 chapters written, 0 of 6,236 verses.**

**Reset, 2026-09-24.** Chapter 1 and the written part of chapter 2 were cleared and their payload
deleted. The format changed: the bold headings are descriptive titles again (as in the old
commentary on this site), not the verse's phrases. Each phrase of the verse is quoted *inside* the
paragraph that explains it, in verse order, and each quoted phrase is backed beside it by evidence —
a Qur'an cross-reference, a hadith with its collection, or a named authority. Not every heading
carries a phrase: context, history, reports and rulings are headings of their own. `audit.py`
enforces this mechanically (`FMT-HEADING-QUOTED`, `FMT-HEADING-VERSE`, `PHR-*`, `PHR-EVIDENCE`), and
batches are now produced and gated in parallel (`batch.py N --ranges A-B,C-D,E-F`). Chapter 1 is
rewritten first, then chapter 2.

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

* Cleared and scaffolded under the new format on 2026-09-24. To be rewritten first — the earlier
  6,290-word version in the old phrase-heading format is in the git history, not in the file.

### Chapter 2 — Al-Baqarah (286 verses)

* Digest built for the whole chapter: `tmp/sources/002.txt` (13.8 MB) and `002.json` (85 MB, uncapped
  for writing; `sources.py` takes `--cap-json` when a smaller digest is enough). All 286 verses have
  source material.
* Cleared on 2026-09-24 (2:1–2:141 had been written in the old phrase-heading format); the file is
  back to a full scaffold, 0/286 written, and the payload was never built. The old text is in the
  git history of this branch.
* The chapter is written batch by batch, with several batches in flight at once, and the writer does
  not stop between batches (`TAFSIR_PROMPT.md` §1, §10). Batch tooling: `batch.py N --from A --to B`,
  `batch.py N --ranges A-B,C-D,E-F` (in parallel), `batch.py N --progress`.
* No payload, no worklog row and no `sw.js` bump until the chapter passes the gate in full, so the
  app keeps showing "coming soon" for al-Baqarah.

## Conventions

* Chapter file: `tafsir/NNN.md`; payload: `data/tafsir_NNN.json`; digest: `tmp/sources/NNN.*`.
* Commit subject: `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`.
* Only chapters that pass `scripts/tafsir/audit.py` get a row here and a commit.

## Open items

* Chapter order is ascending, 001 → 114. Chapter 1 first, then chapter 2 from verse 1.
* The app shows "coming soon, in sha Allah" under verses whose chapter has no payload yet; this
  is expected until a chapter is written. `data/tafsir_001.json` was deleted with the reset and is
  rebuilt when chapter 1 passes the gate again.
* Chapter 1 is the reference for the standard. When a rule and chapter 1 disagree, the rule wins
  and chapter 1 is fixed.
