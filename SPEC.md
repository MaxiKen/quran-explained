# TAFSIR — build spec (v2, lean) · 2026-10-03

**Deliverable.** A verse-by-verse tafsir of the Qur'an. One book file per chapter: `<surah>/<slug>.md`
(e.g. `1/al-fatihah.md`, `2/al-baqarah.md`). Sources cited inline as **[Ṭabarī]**, **[Qurṭubī]**,
**[Ibn Kathīr]**, **[al-Jalālayn]**, **[as-Saʿdī]**, **[Study Quran]**.

## 1. Sources (six)

| # | Work | Corpus folder | Author / date |
|---|---|---|---|
| 1 | *Jāmiʿ al-Bayān* | `tafsir-al-tabari/` | al-Ṭabarī (d. 310/923) |
| 2 | *al-Jāmiʿ li-Aḥkām al-Qurʾān* | `tafsir-al-qurtubi/` | al-Qurṭubī (d. 671/1273) |
| 3 | *Tafsīr al-Qurʾān al-ʿAẓīm* | `tafsir-ibn-kathir/` | Ibn Kathīr (d. 774/1373) |
| 4 | *Tafsīr al-Jalālayn* | `tafsir-al-jalalayn/` | al-Maḥallī & al-Suyūṭī (d. 911/1505) |
| 5 | *Taysīr al-Karīm al-Raḥmān* | `tafsir-as-saadi/` | ʿAbd al-Raḥmān al-Saʿdī (d. 1376/1956) |
| 6 | *The Study Quran* | `tafsir_initial/` | Nasr et al. (2015) |

**Removed from the branch (2026-10-03):** al-Alūsī, al-Baghawī, Maʿārif al-Qurʾān, Ibn ʿAbbās and
Ibn ʿUthaymīn corpora — redundancy with al-Ṭabarī (al-Baghawī, Ibn ʿAbbās), padding for a modern
verse-by-verse book (al-Alūsī, Ibn ʿUthaymīn), or a role already covered by as-Saʿdī + The Study
Quran (Maʿārif). Only the six corpora above remain.

## 2. Entry format (one entry per verse, always)

```
## 1:1 — <Arabic verse text>
*<English translation>*

**Meaning.** Phrase-by-phrase exposition of the verse.
**Context.** Occasion / background where the verse has one.
**Ḥadīth & āthār.** Prophetic traditions and the sayings of the Companions & Successors.
**Rulings.** Legal deductions (only for verses that carry them).
**Belief.** Doctrinal points the verse establishes.
**Language.** A short lexical/grammatical note, only where the meaning turns on the Arabic.
**Cross-references.** Other Qur'anic verses that explain or echo this one.
**Readings.** A variant reading, only where it changes the sense.
**Stories & occasions.** Narratives the verse refers to.
**Reflection.** Wisdom, spiritual counsel, and practical application (brief).
```

Only the blocks that carry real content are written; a short verse may have three blocks, a
weighty verse ten. Verse-by-verse is the backbone — every verse of the chapter gets its own entry
with the verse number in the heading.

## 3. Length budget — "sized to the verse"

Target ≈ **120 words** for the shortest verses, up to ≈ **1,200 words** for the weightiest legal or
narrative verses; average ≈ 400–500 words. Chapter 2 (286 verses) ≈ 140,000 words.

## 4. Extraction rules

1. **Unique material only.** Skip isnād chains, repeated reports, poetic digressions, polemics and
   marginal asides. Collapse once whatever later sources copy from earlier ones — the corpora repeat
   whole commentary blocks under every verse heading they cover; never count the same block twice.
2. **English only.** Arabic is kept for the verse itself and for indispensable terms.
3. **One book per chapter.** No per-source files, no sūrah-level records, no coverage/audit lines.
4. **Verse-anchored.** Where the sources treat consecutive verses as one unit, the entry still opens
   at each verse number and covers it.

## 5. Working method

Read each source's section for the verse (`## n:m` in the corpora; `tafsir_initial/*.md` is
block-structured), extract the unique points into the entry, then move to the next verse. Chapter 1
is rebuilt first, then chapter 2 (2:1 → 2:286) without interruption.
