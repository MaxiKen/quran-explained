# TAFSIR — build spec (v4) · 2026-10-05

> **Companion documents:** `HANDOVER.md` is the continuation prompt and operating manual; `tools/sect.py` is the per-verse corpus extractor. Read both documents before writing.

**Deliverable.** A verse-by-verse tafsir of the Qur'an, one Markdown file per chapter (`<surah>/<slug>.md`, e.g. `1/al-fatihah.md`, `2/al-baqarah.md`). Every verse gets its own entry, built from seven tafsir sources and cited inline.

## 1. Sources (seven)

| # | Work | Corpus folder |
|---|---|---|
| 1 | *Jāmiʿ al-Bayān* — al-Ṭabarī | `tafsir-al-tabari/` |
| 2 | *al-Jāmiʿ li-Aḥkām al-Qurʾān* — al-Qurṭubī | `tafsir-al-qurtubi/` |
| 3 | *Tafsīr al-Qurʾān al-ʿAẓīm* — Ibn Kathīr | `tafsir-ibn-kathir/` |
| 4 | *Tafsīr al-Jalālayn* — al-Maḥallī and al-Suyūṭī | `tafsir-al-jalalayn/` |
| 5 | *Taysīr al-Karīm al-Raḥmān* — as-Saʿdī | `tafsir-as-saadi/` |
| 6 | *Maʿārif al-Qurʾān* — Muftī Muḥammad Shafīʿ | `tafsir-maarif-ul-quran/` |
| 7 | *The Study Quran* — Nasr et al. (2015) | `tafsir_initial/` |

## 2. Entry format (one entry per verse)

```markdown
## 2:1

*<English translation>*

**Meaning.** Phrase-by-phrase exposition of the verse.
**Context.** Occasion/background where the sources provide one.
**Ḥadīth & āthār.** Prophetic traditions and sayings of Companions and Successors.
**Rulings.** Legal deductions, only where relevant.
**Belief.** Doctrinal points established by the verse.
**Language.** Lexical/grammatical notes where the meaning turns on Arabic.
**Cross-references.** Other Qur'anic verses that explain or echo this one.
**Readings.** Variant readings, where relevant.
**Stories & occasions.** Narratives attached to the verse by the sources.
**Reflection.** Wisdom and practical/spiritual application.
```

Use only blocks with relevant content; **Meaning** and **Reflection** are always present. The verse heading is machine-greppable as `^## N:M`. Keep Arabic to the verse and indispensable terms; write the commentary in English. Flag weak reports, Israelite tales, and worthwhile digressions as `*(weak)*`, `*(Isrāʾīliyyāt)*`, and `*(digression)*` respectively.

## 3. Minimum length and source-citation requirements

These are **per-verse-entry minimums**, not chapter averages:

- **At least 800 words per verse entry.**
- **At least 20 inline source citations per verse entry.**
- It is recommended and advised to go **above both minimums** whenever the source material supports further useful exposition.

Count the entry body between its verse heading and the next verse heading. The general body-word convention includes the English translation and labeled commentary, but excludes the chapter-level introduction/header and the Arabic verse text in the heading.

**Continuation clarification for 2:101–2:200:** the user requires at least **800 words of commentary prose** per verse. Audit this stricter floor independently by excluding the English verse translation, the standalone verse-number marker, commentary labels, and inline source tags; count the prose itself. Count the 20 source-attribution occurrences separately. This clarified prose-only floor governs every batch from 2:101 through 2:200.

**New authorization (2026-10-05), 2:201–2:286:** the user has authorized continuation through the end of Sūrah 2. No new word-count clarification was supplied for this range, so the general body-word convention above governs its formal 800-word minimum. For a robust audit, keep the commentary prose itself above 800 words where the reviewed sources support it, and count the 20 inline source tags separately.

A source citation is one inline attribution to a named tafsir source, in the standard form `**[Saʿdī]**`, `**[Ṭabarī]**`, etc. **Count every occurrence:** repeats count again; if a claim is attributed to three sources, write three individual tags and count all three. Do not combine multiple source names inside one bracket. The chapter-level source list, Qur'anic verse references, and bare mentions of a scholar are not inline source citations and do not count toward the 20.

Meet the thresholds through accurate, relevant source attribution and useful synthesis—not padding, duplicate prose, or invented citations. Read all seven sources for every verse; cite a source only for material actually supported by that source. If a source section is empty or a genuine source shortage makes a threshold impossible, never fabricate material: record the exception for review and continue.

## 4. Source-reading and synthesis rules

1. Read all seven source sections for each verse, using `tools/sect.py` (copy to `/home/user/sect.py` for convenience). Read in manageable chunks when Ṭabarī or Qurṭubī is long.
2. Keep unique material. Collapse repeated reports and material copied across later sources; do not recount the same source wording as distinct content. Cite each source where it genuinely contributes to a point.
3. Every summary must stand alone: use clear complete sentences and retain the names, numbers, substance, and qualifications needed to understand the report. Do not leave cryptic stubs.
4. Keep disagreements visible rather than flattening them. Mark weak/spurious reports, Israelite narratives, and relevant digressions as specified above.
5. Do not quote long Arabic passages. Translate or paraphrase responsibly; preserve essential Arabic terms where needed.
6. Where sources treat consecutive verses as a unit, still create a separately headed entry for every verse and explain the verse-level relation accurately.

## 5. Ten-verse iteration protocol for the 2:101–2:200 continuation

- Continue at **2:101**. The target is **100 verses**, written in **10 iterations of 10 consecutive verses**: 2:101–2:110, 2:111–2:120, …, 2:191–2:200.
- At every iteration, size and read the ten verses as a batch across all seven sources, then write and verify those ten entries together. Be fast and focused, but do not skip a source or a verse.
- Save after every ten-verse iteration, then immediately continue with the next iteration in the same run. Do not pause for a check-in between iterations.
- For each entry, verify both minima independently (≥800 words and ≥20 source-citation occurrences). A batch average does not compensate for an individual entry below either minimum.
- Keep source attributions precise and keep the prose useful; exceeding the minimums is encouraged when supported by the sources.

### 5.1 Newly authorized extension: 2:201–2:286

- Continue from 2:201 through 2:286 in eight complete ten-verse batches (2:201–2:280) and a final six-verse batch (2:281–2:286).
- For each batch, size and read all seven source sections, draft the entries, audit each entry independently for at least 800 words under the applicable convention and at least 20 inline source tags, then save and continue without a check-in.
- For this extension, the user has not replaced the general body-word convention with a prose-only rule; nevertheless, keep the commentary itself above 800 words where source material supports it to avoid a borderline count.
- Commit each finished batch on the fixed session branch, excluding the Sūrah 3 and 4 deletions and unreviewed scratch files.

### Progress snapshot (2026-10-05)

The continuation is appended and audited through **2:260**; the next batch is **2:261–2:270**. The
2:251–2:260 commentary-prose/source-tag counts are 2:251 900/58; 2:252 891/59; 2:253 878/64;
2:254 879/59; 2:255 874/64; 2:256 876/63; 2:257 875/66; 2:258 873/61; 2:259 876/60;
2:260 855/64. Study Quran has no separate section for 2:251, and the extracted Maʿārif section for
2:259 is misaligned with 2:258; neither was cited for those verses. The separate source-accuracy review
of 2:121–2:130 remains pending.

## 6. Verification before saving a batch

For the current Sūrah 2 continuation, confirm that each verse in the batch appears exactly once and meets both per-entry floors. Count only the seven standard inline source tags, once per occurrence. A quick audit can be done with Python by splitting the Markdown on verse headings and counting whitespace-delimited words plus every occurrence of the seven exact source tags. Then inspect the diff and ensure no source was attributed without support.

For 2:201–2:286, use the general body-count convention unless the user clarifies otherwise; count source tags separately. The prose in this extension is being kept above 800 words per verse as an additional safety margin.
