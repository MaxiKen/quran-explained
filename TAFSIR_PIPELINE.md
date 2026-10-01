# Tafsir pipeline — how this repository now works

The old commentary corpus (`markdown commentry/`, 114 files written against a word target and
then edited down over many passes) was deleted in commit `b600667`, together with its payloads
(`data/tafsir_*.json`), its process documents and its generator scripts. What replaces it is a
small, strict pipeline: one chapter file at a time, written from the **eleven** works in this
repository (v7.4: the ten tafsirs plus the study draft `tafsir_initial/`), gated by an auditor that
will not pass anything malformed, unevidenced, repetitive or padded. Fifty verses are mapped from
all eleven works in one pass for research speed. Prose is checked one verse at a time, automatic
quality alarms still run in fifty-verse windows, and independent review checkpoints contain at most
fifty verses. Every generation stop is reviewed, committed and pushed with its statistics, and the
run goes on without waiting for confirmation (the author's standing order, 2026-10-01), even when the
range or chapter is incomplete; publication still requires acceptance. **Since 2026-10-01 commentary
writing is paused** while the author pilots an evidence-first, two-phase approach — an evidence map
per chapter first, commentary built from it later, its length decided by the evidence
([`TAFSIR_EVIDENCE_MAP.md`](TAFSIR_EVIDENCE_MAP.md)).

* **What to write, and under which rules:** [`TAFSIR_PROMPT.md`](TAFSIR_PROMPT.md)
* **Every rule in one list:** [`TAFSIR_RULES.md`](TAFSIR_RULES.md) — the whole rule set, each rule
  with the `audit.py` code that enforces it and its threshold
* **How far the work has got:** [`TAFSIR_WORKLOG.md`](TAFSIR_WORKLOG.md)
* **The output:** `tafsir/NNN.md`, one file per chapter, 114 in all
* **The app payload:** `data/tafsir_NNN.json`, built from the markdown, read by `js/app.js`

## 1. Repository layout

| Path | What it is |
|---|---|
| `tafsir/` | the generated corpus — `001.md` … `114.md` (empty at present: all generated commentary was cleared on 2026-10-01 and `tafsir/.gitkeep` remains) |
| `evidence/NNN.md` | the evidence map of the two-phase pilot: per verse, heads with a short summary of the evidence the eleven works carry under each, every item naming its works; written and validated with `scripts/tafsir/evidencemap.py` (pilots: 103 at full depth, 108 at survey depth) |
| `data/chapter_NNN.js` | canonical Arabic, translation and audio per verse — the **only** source of Qur'an wording |
| `data/tafsir_NNN.json` | app payload built from `tafsir/NNN.md` by `scripts/tafsir/build_data.py` |
| `scripts/tafsir/` | the pipeline: source digest, phrase splitting, scaffold, batch gate, audit, payload build, status, source verification |
| `tafsir-*/NNN.txt` | the ten tafsir works of `corpus.SOURCE_ALLOWLIST` (4 English, 6 Arabic), one `## C:V` section per ayah |
| `tafsir_initial/NNN.md` | the study-Quran-style verse draft, verses marked `**V**` — since v7.2 the **eleventh source** of `corpus.SOURCE_ALLOWLIST` (partial coverage; read, never cited) |
| `js/`, `css/`, `index.html`, `sw.js` | the reader app; unchanged except that a missing payload no longer breaks a chapter |
| `tmp/sources/NNN.{txt,json}` | the per-chapter source digests (all eleven), rebuildable, git-ignored |
| `tmp/runs/run-NNN.{txt,json}` | a run's map — the fifty verses with all eleven works beneath them — and its manifest, git-ignored |
| `tmp/work/cN_v*.md` | verse drafts; assembly makes them readable but does not make them accepted |
| `quality/chapter-001-baseline.json` | frozen Chapter-1 hash, measurements and style-drift thresholds — a **writing-style** yardstick only since 2026-10-01 (it does not set how much content or evidence a verse carries). Kept, but Chapter 1 is deleted, so `quality.py --baseline` blocks with `QTY-BASELINE-CHANGED` until a chapter is built and frozen or the record is retired |
| `quality/reviews/NNN/AAA-BBB.json` | tracked pending or accepted review for at most fifty verses: rubric, all-source fingerprint/synthesis, substantive-claim verification, Qur'an relevance, and transmitted-evidence source/relevance ledgers (none at present: they embed excerpts of the prose and were removed with it on 2026-10-01) |
| `quality/stats/NNN/AAA-BBB.md` | the statistics posted with every push (`scripts/tafsir/stats.py`): style against Chapter 1, content and evidence for information, source coverage |

History is not gone. The deleted corpus and its rule documents are readable at the previous
commit, e.g.

```bash
git show f50425f:"markdown commentry/001.md" | head -40
git show f50425f:SECOND_PASS_RULES.md | head -40
git show f50425f:tafsir-ibn-kathir/WORKLOG.md | head -60
git show f50425f:data/tafsir_001.json | head -c 300
```

## 2. The sources

The corpus is **eleven** works: the ten fixed on 2026-09-24 and the study draft of
`tafsir_initial/`, added as the eleventh on 2026-09-25 (v7.2) — `corpus.SOURCE_ALLOWLIST`. The
other seventeen `tafsir-*` folders, including the Arabic duplicates of al-Jalālayn and Ibn Kathīr and
the gloss collections (al-Qushayrī, al-Tustarī, Kashānī, Kashf al-Asrār, Asbāb al-Nuzūl), were
deleted: the chapter is written from these eleven and from nothing else, and the gate refuses a work
outside the list (`SRC-BANNED`). The exports came from `spa5k/tafsir_api`; each file header carries its
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
| 11 | `tafsir_initial` | English | the study-Quran-style draft | the **eleventh work (v7.2)**: digested and read like the rest, partial coverage, never relayed, compared or quoted |

`tafsir_initial/` was reference material until v7.2; it is now a source — digested by `sources.py`
with the ten, read for every verse it covers before the verse is written, and held to the same law
as the others (research, never quoted).

## 3. Tools

```bash
# 0. the run: fifty verses, planned and mapped from all eleven in one pass (v7.2)
python3 scripts/tafsir/run.py --plan --start 2:1         # fifty from the author's start (2 or 2:1)
python3 scripts/tafsir/run.py --build                  # map them (tmp/runs/) + per-chapter digests
python3 scripts/tafsir/run.py --slice 2:1 2:5          # read the map a stretch at a time
python3 scripts/tafsir/run.py --status                 # the run's words, floors and gate state
python3 scripts/tafsir/run.py --check                  # all fifty clean and independently accepted

# cross-references are expanded, never typed (v7.2)
python3 scripts/tafsir/reference.py 2:255              # ready-made citations for a verse
python3 scripts/tafsir/reference.py --find "<wording>" # which verse carries this phrase?
python3 scripts/tafsir/reference.py --scan 2           # every bare citation in tafsir/002.md + the fix

# 1. see where the material is for a chapter, then build the digest
python3 scripts/tafsir/sources.py 2 --stats
python3 scripts/tafsir/sources.py 2                     # tmp/sources/002.txt + 002.json
python3 scripts/tafsir/sources.py 2 --verse 255 --cap-ar 4000 --stdout

# 2. scaffold the chapter file: byte-exact verse quotes, headings left to the writer
python3 scripts/tafsir/scaffold.py 2
python3 scripts/tafsir/scaffold.py 2 --phrases | head -40   # the phrase cut every verse is measured against
python3 scripts/tafsir/verify.py "Musaylimah" --chapter 2   # before crediting any source
python3 scripts/tafsir/match.py 1:4 "the day of reckoning"  # is this the verse's wording, a synonym, or neither?

# 3. write in order: mechanical check per verse, review checkpoint at most fifty
python3 scripts/tafsir/assemble.py 2
python3 scripts/tafsir/batch.py 2 --from 7 --to 10 --draft
# at every generation stop, create/refresh a pending scaffold and push the candidate first
python3 scripts/tafsir/quality.py --template 2 --from 7 --to 10 --writer WRITER_ID
python3 scripts/tafsir/batch.py 2 --from 7 --to 10 --push-check
# commit and push here, although the chapter and independent review are still incomplete
# a different reviewer then completes quality/reviews/002/007-010.json on the GitHub candidate:
# all-source comparison + omissions, rubric, substantive-claim ledger, Qur'an ledger,
# and transmitted-evidence ledger
python3 scripts/tafsir/batch.py 2 --from 7 --to 10
python3 scripts/tafsir/quality.py 2 --from 7 --to 10
python3 scripts/tafsir/batch.py 2 --progress
python3 scripts/tafsir/audit.py 2                       # whole chapter mechanical gate
python3 scripts/tafsir/quality.py 2                     # whole chapter parity gate
python3 scripts/tafsir/audit.py 2 --json > findings.json
python3 scripts/tafsir/audit.py --all                   # corpus overview

# 4. publish to the app and record progress
python3 scripts/tafsir/build_data.py 2                  # data/tafsir_002.json
python3 scripts/tafsir/build_data.py --all --check      # is the payload in sync?
python3 scripts/tafsir/status.py 2
python3 scripts/tafsir/status.py --md                   # table for the worklog
python3 scripts/tafsir/selftest.py                     # mechanical mutation tests
python3 scripts/tafsir/qualitytest.py                  # Chapter-1 parity regression tests
```

`selftest.py` proves the contract is real: it mutates a written chapter once per rule (lower-case
heading, mis-quoted verse, unanchored citation, a section written source by source) and fails if
`audit.py` does not report the rule's code. `audit.py` is the contract, not a suggestion; `batch.py` applies the same contract to the verses
written so far, so a stretch can be judged while the rest of the chapter is still scaffold. Codes and
what they mean:

| Code | Meaning |
|---|---|
| `FMT-*` | wrong shape: title, introduction, verse set/order, quote line, separators, spacing, placeholders — and a heading that is not UPPERCASE (`FMT-HEADING-CASE`), is the verse's own wording (`FMT-HEADING-QUOTED`), repeats it (`FMT-HEADING-VERSE`), or is generic |
| `PHR-*` | phrases: quoting style (`PHR-QUOTE-STYLE` — this verse's phrases are bold italics `***“…***`, other references bold only), the verse is not quoted in the prose (`PHR-PHRASE-NONE`), a phrase is never quoted (`PHR-PHRASE-MISSING`), the quoted share is under 90%, an unquoted gap runs past 8 words, the edges are dropped, one quote swallows the verse (`PHR-CHUNK`), or a quoted phrase has no evidence beside it (`PHR-EVIDENCE`) |
| `WRD-*` | length: a verse under its floor (700 words, or 9× the verse's own length, capped at 4,000) or an introduction outside 250–1,500 |
| `EVD-*` | evidence: a verse with no checkable anchor, or a prophetic report that never names its collection |
| `REF-*` | references: a citation to a non-existent verse, a quote that is not verbatim from `data/`, quoting style broken |
| `REP-*` | repetition: a duplicated sentence, two verse sections sharing phrasing, filler or machine prose |
| `STY-*` | mechanical style diagnostics: diction, sentence length, reading ease, and analogy/application marker presence; v8 semantic acceptance is separate |
| `MTCH-*` | match: bold used outside the three markers — the UPPERCASE headings, this verse's phrases (bold italics `***“…***`), clauses of other verses quoted in bold only inside their reference (`MTCH-BOLD`); a headword that neither is the verse's wording nor *means the same thing* — one word or a whole phrase (`MTCH-WORD`, fail), or Arabic offered as the verse's own wording (`MTCH-TERM`, fail); a synonym, or an Arabic term whose meaning the verse carries, is adjusted to the verse's own wording and recorded as information (`MTCH-SYNONYM`) |
| `GRD-*` | grounding (advisory): names or terms in a section that do not appear in that verse's sources |
| `QTY-SOURCE-*` | acceptance blocker: source fingerprint changed, all available works were not compared with the prose, or a material omission lacks a decision |
| `QTY-CITATION-*` | acceptance blocker: a Qur'an quote is mismatched, unsupported or not relevance-reviewed |
| `QTY-TRANSMITTED-*` | acceptance blocker: a named report/early authority lacks an allowlisted matching excerpt or relevance decision |

v7.2 adds `REF-BARE`: a cross-reference with no wording — `(2:255)`, or a list such as
`(2:156, 245, 281)` — warns once or twice in a section and fails from three; `reference.py --scan`
prints the expansion for every one of them.

The thresholds that keep chapters honest as they grow:

| Rule | Value |
|---|---|
| Words per verse | floor `max(700, 9 × verse words)`, capped 4,000; soft ceiling 5,000 |
| Introduction | 250–1,500 words |
| Phrase coverage | ≥90% of the verse's words, no gap over 8 words, edges within 3 words |
| Analogy/application | optional; must add verse-specific clarity and may not occupy a repeated production slot |
| V8 review checkpoint | at most 50 new drafts beyond accepted/owner-approved prose and at most 50 verses per semantic review; fifty-verse metric windows; every generation stop push-checked/committed/pushed; acceptance requires complete all-source comparison, rubric scores all ≥4, and source/relevance review of every scaffolded/additional substantive claim, Qur'an citation and transmitted statement |
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
2. The author's standing order (2026-10-01) names the start: the first verse not yet written, run
   after run, until the author says otherwise. Fifty verses are mapped from all eleven works in one
   pass. Each semantic review covers at most fifty verses. Prose is written in order and mechanically
   checked per verse; fifty-verse metric windows catch early drift. The writer does not wait for
   confirmation between runs; the author reads afterwards, and an explicit, fingerprinted owner
   approval is optional. No fifty-first new draft beyond the accepted/owner-approved drafting
   frontier is opened. `QUALITY DRIFT` stops new drafting: repair it, note it in the statistics, push
   the clean checkpoint and carry on; `run.py --check` completes only after all fifty are
   independently accepted.
3. Never leave a half-written verse. At every generation stop, create or refresh the review scaffold,
   complete the independent review pass (a separate, cold pass under the reviewer identity), run the
   full gate, post the statistics (`stats.py --write`), commit, and push — even if the chapter is
   incomplete — and go on. Assembled prose remains unaccepted until that review compares every source passage, accounts for
   omissions, validates every Qur'an citation, locates named transmitted statements, and passes the
   rubric. Source fingerprints invalidate stale reviews automatically. Payload and completion-worklog
   changes wait for the accepted, finished chapter.
4. A chapter is done when `audit.py N` ends `RESULT: PASS`, `quality.py N` ends `QUALITY PARITY PASS`, every verse clears its own word floor
   (`status.py N` shows them side by side), `build_data.py N --check` reports no stale payload, the
   worklog row exists, and `sw.js` has been bumped. Commit per chapter on the session branch
   (`Tafsir ch N (<Name>): verse-by-verse from all <k> sources`); push only to that branch.
5. Parallel work splits by chapter, never by verse within one file: two writers on one file
   will overwrite each other. Several sessions may write different chapters at once; chapters are
   taken in ascending order by default.

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
