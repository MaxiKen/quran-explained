# Tafsir Rewrite Guide

Everything needed to continue the rewrite of `data/tafsir_NNN.js` on any chapter, in the
same style and to the same citation standard as chapters **1, 2, 3 and 4** (already done).

Hand this file plus `tools/` to any agent and say:
*"Apply the treatment in `tools/TAFSIR_REWRITE_GUIDE.md` to chapter N."*

---

## 1. The goal

Rewrite every verse commentary so that it is:

- **Simple English.** Anyone can understand it. Short sentences. Everyday vocabulary.
  No academic register, no long subordinate clauses.
- **Not padded.** No word-count filler, no abstract restatement of the obvious, no
  "this verse teaches us many profound lessons" throat-clearing.
- **Still long and comprehensive.** Target ~240–330 words per verse. Density, not length,
  is what was cut.
- **Fully referenced.** Every claim carries a reference. No exceptions.

Quoted material — Quran translations, hadith translations — is **never reworded**.

---

## 2. File format (the contract)

```js
var tafsirData_4 = {
  "1": "paragraph\n\nparagraph\n\nparagraph",
  "2": "...",
  ...
};
```

- Flat JS object literal. Keys are ayah numbers as **strings**, `"1"` … `"<verseCount>"`,
  contiguous, ascending numeric order.
- Values are single strings. Paragraphs separated by `\n\n`.
- **Plain text only — no HTML.** `js/app.js` renders via `textContent` into
  `<p id="modalBody">` with CSS `white-space: pre-line`. Any tag would be shown literally.
- Verse text comes from `data/chapter_NNN.js` (`chapterData_N`, array of themes, each with
  `verses: [{ayah_no_surah, ayah_ar, ayah_en, audio}]`). **Never edit chapter files.**

Serialization recipe (verified byte-identical round-trip across 100+ merges):

```
read file → eval → mutate object → write 'var tafsirData_N = ' + JSON.stringify(obj, null, 2) + ';\n'
```

`tools/build_tafsir.js` implements exactly this.

---

## 3. Style template

Match chapters 1–4 exactly.

1. **Open by quoting the verse**, then `(Quran C:V)`, then a one-line framing of what the
   verse is doing. Example:
   `'...' (Quran 4:135). The high point of the surah on justice.`
2. **4–6 short paragraphs**, ~240–330 words total.
3. **Transliterate then gloss key Arabic.** `'Stand firm for justice' — kunu qawwamina bi
   al-qist. The word 'qawwamin' is the same root used in 4:34...`
4. **Every scriptural quote is followed by `(Quran C:V)`.**
5. **Every hadith carries collection + number**, and a **grade** for anything outside
   Bukhari and Muslim (e.g. `graded sahih by al-Albani`, `hasan`, `graded sahih by Darussalam`).
6. **Tafsir works are cited by named author** — al-Tabari, Ibn Kathir, al-Qurtubi,
   al-Suyuti, al-Shafi'i — plus a phrase like *"commenting on this verse"*.
   **Never** write grouped anonymous attributions like *"Classical scholars of tafsir,
   including al-Tabari, al-Qurtubi, and Ibn Kathir, explain that…"* — that is the exact
   old-style marker being eliminated.
7. **Cross-reference within the surah.** Point back to earlier verses that used the same
   word or set up the same argument. This is what makes the commentary feel like one
   continuous reading rather than 176 disconnected notes.
8. **End with a practical takeaway** — something the reader does or notices, not a moral
   platitude.

### Things to avoid (they were all removed)

| Banned | Use instead |
|---|---|
| "the Quran says elsewhere" / "another verse says" | the actual `(Quran C:V)` |
| "scholars say" / "it is said that" / "commentators say" | a named authority |
| "including al-Tabari, al-Qurtubi, and Ibn Kathir" | one named author |
| any HTML tag | plain text |
| paraphrasing a hadith from memory | fetched sunnah.com wording |

---

## 4. Discipline (this is the part that matters)

- **Every Quran quotation is pasted from `node tools/verse.js` output**, including the
  `˹ ˺` bracket characters. Never type a translation from memory — the app uses a specific
  translation and the text must match it exactly.
- **Every hadith quotation is pasted from a fetched sunnah.com page.** Fetch
  `https://sunnah.com/<collection>:<number>` directly and copy the English wording and
  the grade from that page.
- **Do not trust search-result snippets for hadith numbers or grades.** They were wrong
  repeatedly during this work (e.g. Tirmidhi 2330 vs the correct 2329).
- **Check the grade before using.** Widely-quoted narrations are sometimes weak.
  Confirmed rejections from this project:
  - `abudawud:4903` (envy devours good deeds) — **da'if** (al-Albani). Replaced with Sahih Muslim 2564a.
  - `tirmidhi:3022` — da'if, mursal.
  - `tirmidhi:3095` — da'if; use Tirmidhi 2954 instead.
  - "I am the supplication of my father Ibrahim" — contested attribution; use Ibn Kathir's
    citation of the sound wording.
  - Invalid-URN sunnah.com pages seen: `muslim:2749a`, `muslim:1337a`, `muslim:251`,
    `muslim:1469a`. Use `muslim:251a`; use Bukhari 5185/5186 in place of Muslim 1469.

---

## 5. Workflow, per batch

Work in batches of **14 verses**. Larger batches degrade quality and hit output limits.

```bash
cd /home/user/quran-explained

# 1. read the verses and the current tafsir
node tools/show.js 5 1 14          # verse + existing tafsir
node tools/show.js 5 1 14 --v      # verse text only (use for ranges > ~7)

# 2. look up every verse you plan to cross-reference, exactly
node tools/verse.js 2:178 5:45 17:33 6:151

# 3. verify every hadith by fetching its page
#    https://sunnah.com/bukhari:6878   etc.

# 4. author the batch to a scratch file, format below

# 5. merge
node tools/build_tafsir.js 5 /tmp/batch_5a.txt
#    → tafsir_005.js: updated 14 entries, total 120

# 6. QA
node tools/qa_tafsir.js 5
#    → QA CLEAN

# 7. commit
git add -A && git commit -m "Rewrite tafsir 5:1-14"
```

Push at the end of every two or three batches:
`git push origin arena/01a0250e-quran-explained`

### Batch file format

```
===1===
First paragraph of the commentary for verse 1.

Second paragraph.

Third paragraph.
===2===
First paragraph for verse 2.

...
```

`===<verse>===` on its own line, paragraphs separated by blank lines. Existing keys are
replaced, untouched keys preserved, keys re-sorted numerically.

---

## 6. Tools

All in `tools/`, all plain Node with no dependencies, all resolve the repo from their own
location so they work from any cwd.

| Script | Usage | Purpose |
|---|---|---|
| `verse.js` | `node tools/verse.js 4:135 5:8` | Print the app's exact `ayah_en` for each reference. |
| `show.js` | `node tools/show.js 4 111 124 [--v]` | Verse text plus current tafsir for a range. `--v` = verse only. |
| `build_tafsir.js` | `node tools/build_tafsir.js 4 /tmp/batch.txt` | Merge an authored batch into `data/tafsir_004.js`. |
| `qa_tafsir.js` | `node tools/qa_tafsir.js 4` | Regex sweep + key count + contiguity + word stats. Prints `QA CLEAN` or lists issues. |

Verify a file by hand at any time:

```bash
node -e "eval(require('fs').readFileSync('data/tafsir_004.js','utf8')); console.log(Object.keys(tafsirData_4).length)"
```

---

## 7. Status

| Chapter | Verses | State | Word count (min / max / avg) |
|---|---|---|---|
| 1 al-Fatihah | 7 | done | 332 / 382 / 359 |
| 2 al-Baqarah | 286 | done | 246 / 378 / 299 |
| 3 Ali 'Imran | 200 | done | 237 / 329 / 272 |
| 4 an-Nisa | 176 | done | 224 / 343 / 262 |
| 5 al-Ma'idah | 120 | done | 211 / 312 / 254 |
| 6 al-An'am | 165 | done | 228 / 293 / 252 |
| 7–114 | 5,282 remaining | not started | — |

Largest remaining chapters: 26 (227), 7 (206), 37 (182), 20 (135), 9 (129), 11 (123).

All six completed chapters pass `qa_tafsir.js` clean.

---

## 8. Local preview

```bash
python3 -m http.server 8000
```

Serve from the repo root and open the app; the loader is `loadTafsirData(num)` in
`js/app.js` (~line 262), and `getVerseCommentary()` (~line 824) pulls the string that
`showExplanation()` renders.
