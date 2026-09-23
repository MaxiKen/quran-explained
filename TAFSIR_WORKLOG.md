# Tafsir worklog

Progress ledger for the verse-by-verse corpus in `tafsir/`. Update it in the same commit that
finishes a chapter: run `python3 scripts/tafsir/status.py --md` for the numbers rather than
typing them from memory.

| Ch | File | Verses | Words | Min/Med/Max per verse | Gate | Payload |
|---|---|---|---|---|---|---|
| 1 | `tafsir/001.md` | 7/7 | 3,637 | 433/516/617 | PASS | 25 KB |

Totals: **1 of 114 chapters written, 7 of 6,236 verses, 3,637 words.**

## Chapter notes

### Chapter 1 — Al-Fatihah (commit pending)

* Written from all 28 sources; every verse carries at least two kinds of evidence (Qur'an
  cross-reference, hadith with collection, named authority, language point).
* Sources that carried the weight: Ibn Kathir (names of the sūrah, the basmalah debate, the
  hadith of the divided prayer, al-Nawwās ibn Samʿān's parable of the straight path, the Āmīn
  material), al-Ṭabarī (the repetition argument on the basmalah, ʿibādah as humility, the reports
  on "those You have blessed" including the weakness he himself grades), al-Qurṭubī (mercy
  paired with majesty, the iltifāt at verse 5), Maarif-ul-Quran (guidance and its degrees, why
  the Day of Requital is named), al-Mukhtaṣar, al-Jalālayn, al-Bayḍāwī, al-Zamakhsharī,
  al-Saʿdī, Tazkirul Qur'an and the study draft in `tafsir_initial/`.
* Disagreements reported rather than flattened: the basmalah as verse or divider; mālik/malik.
* Sources' duplicate records (four English files carrying one Sufi passage at 1:1) were treated
  as a single witness and are not leaned on.
* Audit: `0 FAIL, 0 WARN`. Payload built, `sw.js` bumped to `quran-reader-v2.5.28`.

## Conventions

* Chapter file: `tafsir/NNN.md`; payload: `data/tafsir_NNN.json`; digest: `tmp/sources/NNN.*`.
* Commit subject: `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`.
* Only chapters that pass `scripts/tafsir/audit.py` get a row here and a commit.

## Open items

* Chapter order is ascending, 001 → 114.
* The app shows "coming soon, in sha Allah" under verses whose chapter has no payload yet; this
  is expected until a chapter is written.
