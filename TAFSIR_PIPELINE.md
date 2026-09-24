# Tafsir pipeline — how this repository now works

The old commentary corpus (`markdown commentry/`, 114 files written against a word target and
then edited down over many passes) was deleted in commit `b600667`, together with its payloads
(`data/tafsir_*.json`), its process documents and its generator scripts. What replaces it is a
small, strict pipeline: one chapter file at a time, written from the ten tafsir works in this
repository, gated by an auditor that will not pass anything malformed, unevidenced, repetitive
or padded.

* **What to write, and under which rules:** [`TAFSIR_PROMPT.md`](TAFSIR_PROMPT.md)
* **Every rule in one list:** [`TAFSIR_RULES.md`](TAFSIR_RULES.md) — the whole rule set, each rule
  with the `audit.py` code that enforces it and its threshold
* **How far the work has got:** [`TAFSIR_WORKLOG.md`](TAFSIR_WORKLOG.md)
* **The output:** `tafsir/NNN.md`, one file per chapter, 114 in all
* **The app payload:** `data/tafsir_NNN.json`, built from the markdown, read by `js/app.js`

## 1. Repository layout

| Path | What it is |
|---|---|
| `tafsir/` | the generated corpus — `001.md` … `114.md` (empty at present: `001.md` and `002.md` were cleared on 2026-09-24, `tafsir/.gitkeep` remains) |
| `data/chapter_NNN.js` | canonical Arabic, translation and audio per verse — the **only** source of Qur'an wording |
| `data/tafsir_NNN.json` | app payload built from `tafsir/NNN.md` by `scripts/tafsir/build_data.py` |
| `scripts/tafsir/` | the pipeline: source digest, phrase splitting, scaffold, batch gate, audit, payload build, status, source verification |
| `tafsir-*/NNN.txt` | the ten tafsir works (`corpus.SOURCE_ALLOWLIST`; 4 English, 6 Arabic), one `## C:V` section per ayah |
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

The corpus is **ten** works, fixed on 2026-09-24 (`corpus.SOURCE_ALLOWLIST`). The other seventeen
`tafsir-*` folders, including the Arabic duplicates of al-Jalālayn and Ibn Kathīr and the gloss
collections (al-Qushayrī, al-Tustarī, Kashānī, Kashf al-Asrār, Asbāb al-Nuzūl), were deleted: the
chapter is written from these ten and from nothing else, and the gate refuses a work outside the
list (`SRC-BANNED`). The exports came from `spa5k/tafsir_api`; each file header carries its
upstream path (`Source: spa5k/tafsir_api · tafsir/en-tafisr-ibn-kathir/1.json`). They are cleaned
copies: one `## C:V` section per ayah, no other edits.

| # | Folder | Language | Author (d. AH) | Use |
|---|---|---|---|---|
| 1 | `tafsir-al-tabari` | Arabic | al-Ṭabarī (310) | reports and chains, the first generations |
| 2 | `tafsir-al-qurtubi` | Arabic | al-Qurṭubī (671) | rulings, occasions, disagreements |
| 3 | `tafsir-al-baghawi` | Arabic | al-Baghawī (516) | the maʾthūr tradition, concisely |
| 4 | `tafsir-ibn-kathir` | English | Ibn Kathīr (774) | reports with grading |
| 5 | `tafsir-al-alusi` | Arabic | al-Alūsī (1270) | language, grammar, later debate |
| 6 | `tafsir-al-jalalayn` | English | al-Maḥallī & al-Suyūṭī (911) | the plain running sense |
| 7 | `tafsir-ibn-abbas` | English | attributed to Ibn ʿAbbās | the earliest gloss |
| 8 | `tafsir-as-saadi` | Arabic | al-Saʿdī (1956) | the modern meaning-first reading |
| 9 | `tafsir-ibn-uthaymeen` | Arabic | Ibn ʿUthaymīn (2001) | modern teaching tafsir (partial coverage) |
| 10 | `tafsir-maarif-ul-quran` | English | Muftī Shafīʿ (1976) | modern reading, fiqh, contemporary questions |

`tafsir_initial/` (the earlier verse draft) is kept on disk as reference but is **not** a source:
it is not digested and nothing may be cited from it.

## 3. Tools

```bash
# 1. see where the material is for a chapter, then build the digest
python3 scripts/tafsir/sources.py 2 --stats
python3 scripts/tafsir/sources.py 2                     # tmp/sources/002.txt + 002.json
python3 scripts/tafsir/sources.py 2 --verse 255 --cap-ar 4000 --stdout

# 2. scaffold the chapter file: byte-exact verse quotes, headings left to the writer
python3 scripts/tafsir/scaffold.py 2
python3 scripts/tafsir/scaffold.py 2 --phrases | head -40   # the phrase cut every verse is measured against
python3 scripts/tafsir/verify.py "Musaylimah" --chapter 2   # before crediting any source

# 3. write the prose in long stretches (the whole chapter where it allows), gating as they land
python3 scripts/tafsir/batch.py 2 --from 6 --to 20      # gate an unfinished chapter's batch
python3 scripts/tafsir/batch.py 2 --ranges 6-20,21-35,36-50   # several batches at once, in parallel
python3 scripts/tafsir/batch.py 2 --progress            # how far the chapter has come
python3 scripts/tafsir/audit.py 2                       # whole chapter: exit 0 only on PASS
python3 scripts/tafsir/audit.py 2 --json > findings.json
python3 scripts/tafsir/audit.py --all                   # corpus overview

# 4. publish to the app and record progress
python3 scripts/tafsir/build_data.py 2                  # data/tafsir_002.json
python3 scripts/tafsir/build_data.py --all --check      # is the payload in sync?
python3 scripts/tafsir/status.py 2
python3 scripts/tafsir/status.py --md                   # table for the worklog
python3 scripts/tafsir/selftest.py                     # break each rule on a scratch copy: does the gate catch it?
```

`selftest.py` proves the contract is real: it mutates a written chapter once per rule (lower-case
heading, mis-quoted verse, unanchored citation, a section written source by source) and fails if
`audit.py` does not report the rule's code. `audit.py` is the contract, not a suggestion; `batch.py` applies the same contract to the verses
written so far, so a batch can be judged while the rest of the chapter is still scaffold. Codes and
what they mean:

| Code | Meaning |
|---|---|
| `FMT-*` | wrong shape: title, introduction, verse set/order, quote line, separators, spacing, placeholders — and a heading that is not UPPERCASE (`FMT-HEADING-CASE`), is the verse's own wording (`FMT-HEADING-QUOTED`), repeats it (`FMT-HEADING-VERSE`), or is generic |
| `PHR-*` | phrases: quoting style (`PHR-QUOTE-STYLE` — this verse's phrases are bold italics `***“…***`, other references bold only), the verse is not quoted in the prose (`PHR-PHRASE-NONE`), a phrase is never quoted (`PHR-PHRASE-MISSING`), the quoted share is under 90%, an unquoted gap runs past 8 words, the edges are dropped, one quote swallows the verse (`PHR-CHUNK`), or a quoted phrase has no evidence beside it (`PHR-EVIDENCE`) |
| `WRD-*` | length: a verse under its floor (500 words, or 8× the verse's own length, capped at 4,000) or an introduction outside 250–1,500 |
| `EVD-*` | evidence: a verse with no checkable anchor, or a prophetic report that never names its collection |
| `REF-*` | references: a citation to a non-existent verse, a quote that is not verbatim from `data/`, quoting style broken |
| `REP-*` | repetition: a duplicated sentence, two verse sections sharing phrasing, filler or machine prose |
| `STY-*` | style: formal diction instead of plain English, sentences too long, reading ease too low, or no relatable analogy in the verse |
| `MTCH-*` | match: bold used outside the three markers — the UPPERCASE headings, this verse's phrases (bold italics `***“…***`), clauses of other verses quoted in bold only inside their reference (`MTCH-BOLD`); a word-study of a word the verse's translation does not carry, Arabic included (`MTCH-WORD`); Arabic offered as the verse's own wording (`MTCH-TERM`, fail) or carried as a free-standing language point (warn) |
| `GRD-*` | grounding (advisory): names or terms in a section that do not appear in that verse's sources |

The thresholds that keep chapters honest as they grow:

| Rule | Value |
|---|---|
| Words per verse | floor `max(500, 8 × verse words)`, capped 4,000; soft ceiling 5,000 |
| Introduction | 250–1,500 words |
| Phrase coverage | ≥90% of the verse's words, no gap over 8 words, edges within 3 words |
| Analogy | at least half the chapter's verses carry one |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% over 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |
| Bold | the UPPERCASE headings, this verse's phrases (bold italics) and other verses' clauses (bold only) — nothing else |
| Explained words | word-studies may only be about wording the verse's translation carries (Arabic terms included) |

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
2. A long chapter is written in batches and the writer does not stop between them: write a batch,
   gate it with `batch.py N`, fix every FAIL, start the next batch, and continue on until the last
   verse is written. Stopping mid-chapter is for a real blockage (a source that cannot be located,
   a contradiction that needs a decision), never for a check-in.
3. Never leave a half-written verse: a section is either the scaffold's `TODO` text or finished
   prose. Batches are committed as they land, with the payload, `sw.js` bump and worklog row left
   for the end of the chapter.
4. A chapter is done when `audit.py N` ends `RESULT: PASS`, every verse clears its own word floor
   (`status.py N` shows them side by side), `build_data.py N --check` reports no stale payload, the
   worklog row exists, and `sw.js` has been bumped. Commit per chapter on the session branch
   (`Tafsir ch N (<Name>): verse-by-verse from all <k> sources`); push only to that branch.
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
