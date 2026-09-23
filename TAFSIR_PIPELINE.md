# Tafsir pipeline — how this repository now works

The old commentary corpus (`markdown commentry/`, 114 files written against a word target and
then edited down over many passes) was deleted in commit `b600667`, together with its payloads
(`data/tafsir_*.json`), its process documents and its generator scripts. What replaces it is a
small, strict pipeline: one chapter file at a time, written from the 28 tafsir sources in this
repository, gated by an auditor that will not pass anything malformed, unevidenced, repetitive
or padded.

* **What to write, and under which rules:** [`TAFSIR_PROMPT.md`](TAFSIR_PROMPT.md)
* **How far the work has got:** [`TAFSIR_WORKLOG.md`](TAFSIR_WORKLOG.md)
* **The output:** `tafsir/NNN.md`, one file per chapter, 114 in all
* **The app payload:** `data/tafsir_NNN.json`, built from the markdown, read by `js/app.js`

## 1. Repository layout

| Path | What it is |
|---|---|
| `tafsir/` | the generated corpus — `001.md` … `114.md` (currently `001.md`) |
| `data/chapter_NNN.js` | canonical Arabic, translation and audio per verse — the **only** source of Qur'an wording |
| `data/tafsir_NNN.json` | app payload built from `tafsir/NNN.md` by `scripts/tafsir/build_data.py` |
| `scripts/tafsir/` | the pipeline: source digest, phrase splitting, scaffold, audit, payload build, status |
| `tafsir-*/NNN.txt` | 27 imported tafsir works (11 English, 16 Arabic), one `## C:V` section per ayah |
| `tafsir_initial/NNN.md` | the study-Quran-style verse draft (`initial/` renamed), verses marked `**V**` |
| `js/`, `css/`, `index.html`, `sw.js` | the reader app; unchanged except that a missing payload no longer breaks a chapter |
| `tmp/` | scratch: source digests (`tmp/sources/NNN.{txt,json}`), git-ignored |

History is not gone. The deleted corpus and its rule documents are readable at the previous
commit, e.g.

```bash
git show f50425f:"markdown commentry/001.md" | head -40
git show f50425f:SECOND_PASS_RULES.md | head -40
git show f50425f:tafsir-ibn-kathir/WORKLOG.md | head -60
git show f50425f:data/tafsir_001.json | head -c 300
```

## 2. The sources

All 27 `tafsir-*` folders were exported from `spa5k/tafsir_api`; each file header carries its
upstream path (`Source: spa5k/tafsir_api · tafsir/en-tafisr-ibn-kathir/1.json`). They are
cleaned copies: one `## C:V` section per ayah, no other edits.

**English (11):** `tafsir-ibn-kathir`, `tafsir-al-jalalayn`, `tafsir-al-mukhtasar`,
`tafsir-maarif-ul-quran`, `tafsir-tazkirul-quran`, `tafsir-asbab-al-nuzul`, `tafsir-ibn-abbas`,
`tafsir-al-qushairi`, `tafsir-al-tustari`, `tafsir-kashani`, `tafsir-kashf-al-asrar`

**Arabic (16):** al-Ṭabarī, al-Qurṭubī, al-Baghawī, al-Bayḍāwī, al-Alūsī, al-Kashshāf,
Fath al-Qadīr, al-Baḥr al-Muḥīt, As-Saʿdī, Ibn ʿUthaymīn, Abu Bakr al-Jazāʾirī, al-Wasīṭ,
Ad-Durr al-Manthūr, Tadabbur wa ʿAmal, Ibn Kathīr (Arabic), al-Jalālayn (Arabic)

**Plus** `tafsir_initial/` — the earlier verse draft kept as a 28th voice.

Known quirks, worth knowing before reading:

* Some upstream records are duplicated across names. In Sūrah 1, for example,
  `tafsir-al-qushairi`, `tafsir-kashani`, `tafsir-kashf-al-asrar` and `tafsir-asbab-al-nuzul`
  all carry the same Sufi passage for 1:1. Treat duplicated text as one witness.
* Verse alignment is by the file's own `## C:V` markers, so it is reliable. What is not reliable
  is assuming the whole of a section belongs to that verse: several sources open a verse's
  section with sūrah-level material, or transcribe a lecture that drifts. Read the opening lines
  of a section before quoting it as that verse's opinion.
* Several sources attach whole-sūrah material to every verse (al-Baghawī's Sūrah 1 record is
  28,669 characters repeated under each of the seven verses; as-Saʿdī and Tazkirul Qur'an do the
  same). That material belongs in the chapter introduction or at the verse it actually concerns —
  once.
* `tafsir-al-tustari` has no record for some verses (4 of 7 in Sūrah 1). Coverage gaps are
  normal; the digest reports them and the writer uses the other 27.

## 3. Tools

```bash
# 1. see where the material is for a chapter, then build the digest
python3 scripts/tafsir/sources.py 2 --stats
python3 scripts/tafsir/sources.py 2                     # tmp/sources/002.txt + 002.json
python3 scripts/tafsir/sources.py 2 --verse 255 --cap-ar 4000 --stdout

# 2. scaffold the chapter file: byte-exact verse quotes + phrase headings
python3 scripts/tafsir/scaffold.py 2
python3 scripts/tafsir/scaffold.py 2 --stdout | head -40   # preview the phrase cut
python3 scripts/tafsir/verify.py "Musaylimah" --chapter 2   # before crediting any source

# 3. write the prose, then run the gate
python3 scripts/tafsir/audit.py 2                       # exit 0 only on PASS
python3 scripts/tafsir/audit.py 2 --json > findings.json
python3 scripts/tafsir/audit.py --all                   # corpus overview

# 4. publish to the app and record progress
python3 scripts/tafsir/build_data.py 2                  # data/tafsir_002.json
python3 scripts/tafsir/build_data.py --all --check      # is the payload in sync?
python3 scripts/tafsir/status.py 2
python3 scripts/tafsir/status.py --md                   # table for the worklog
```

`audit.py` is the contract, not a suggestion. Codes and what they mean:

| Code | Meaning |
|---|---|
| `FMT-*` | wrong shape: title, introduction, verse set/order, quote line, headings, separators, spacing, placeholders, and the phrase headings that must cover the verse |
| `REF-PHRASE*` | a phrase heading that is not the verse's own wording, or is out of verse order |
| `WRD-*` | length: a verse under its floor (550 words, or 7× the verse's own length, capped at 3,500) or an introduction outside 250–1,500 |
| `EVD-*` | evidence: a verse with no checkable anchor, or a prophetic report that never names its collection |
| `REF-*` | references: a citation to a non-existent verse, a quote that is not verbatim from `data/`, quoting style broken |
| `REP-*` | repetition: a duplicated sentence, two verse sections sharing phrasing, filler or machine prose |
| `STY-*` | style: formal diction instead of plain English, sentences too long, reading ease too low, or no relatable analogy in the verse |
| `GRD-*` | grounding (advisory): names or terms in a section that do not appear in that verse's sources |

The thresholds that keep chapters honest as they grow:

| Rule | Value |
|---|---|
| Words per verse | floor `max(550, 7 × verse words)`, capped 3,500; soft ceiling 4,500 |
| Introduction | 250–1,500 words |
| Phrase coverage | ≥90% of the verse's words, no gap over 8 words, edges within 3 words |
| Analogy | at least half the chapter's verses carry one |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% over 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |

The grounding check reads `tmp/sources/NNN.json`, so run `sources.py N` before `audit.py N` for
the full picture (`--no-grounding` skips it).

## 4. The app contract

`data/tafsir_NNN.json` is `{"surah": N, "intro": "<markdown>", "verses": {"V": "<markdown>"}}`,
pretty-printed with `indent=2` and no trailing newline — exactly the shape the app has always
read. `js/app.js` strips the leading `> …` verse quote at render time, so the markdown keeps it.

Chapters whose payload does not exist yet still open: they show the translation and a short
"coming soon" note where the commentary will stand. Bump `CACHE_VERSION` in `sw.js` whenever a
payload is (re)generated, so returning readers get the new file instead of the cached one.

## 5. Working agreement

1. One chapter, one file, `tafsir/NNN.md`; never edit another chapter's file in the same change.
2. A chapter is done when `audit.py N` ends `RESULT: PASS`, every verse clears its own word floor
   (`status.py N` shows them side by side), `build_data.py N --check` reports no stale payload, the
   worklog row exists, and `sw.js` has been bumped.
3. Commit per chapter on the session branch
   (`Tafsir ch N (<Name>): verse-by-verse from all <k> sources`); push only to that branch.
4. Long chapters may be written in batches, but each commit leaves a chapter that passes the
   gate, or (if a batch is mid-flight) leaves the file untouched and keeps the batch as a patch.
5. Parallel work splits by chapter, never by verse within one file: two writers on one file
   will overwrite each other.

## 6. What was deliberately dropped

* `markdown commentry/` and every script that maintained it.
* `data/tafsir_*.json` for all 114 chapters (regenerated chapter by chapter as the new corpus
  lands).
* `data/audit.json` and `data/bible_web.json` (the old corpus's Bible-parallel quoting was part
  of the deleted editorial layer; nothing in the app reads either file).
* The old process documents (`EDITORIAL_PASS.md`, `SECOND_PASS_RULES.md`, `REMAINING_WORK.md`,
  `AUDIT_REPORT.md`, `COMMENTARY_REVIEW.md`, `TAFSIR_EDIT_REPORT.md`, `PASS_TWO_AGENT.md`,
  `tafsir-ibn-kathir/WORKLOG.md`). They describe a corpus that no longer exists; use
  `git show f50425f:<path>` when something in them is still wanted.

`UX_UPDATES.md` is kept: it documents the app, which is still the app.
