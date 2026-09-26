# Tafsir worklog

Progress ledger for the verse-by-verse corpus in `tafsir/`. Update it in the same commit that
finishes a chapter: run `python3 scripts/tafsir/status.py --md` for the numbers rather than
typing them from memory.

## The standard a chapter is written to

Set on 2026-09-23, after chapter 1 was rewritten to it. `scripts/tafsir/audit.py` enforces every
line of it:

| Rule | Value |
|---|---|
| Sources | the **eleven** of `corpus.SOURCE_ALLOWLIST` (the ten tafsirs above plus the study draft `tafsir_initial/`, v7.2) as **research**: all eleven pulled for every verse before it is written (`SRC-NOTCHECKED`, `SRC-NODIGEST`), their contents taken as authenticated (no fact-checking of them); nothing outside the eleven cited (`SRC-BANNED`); the prose never relays, compares or quotes one of them — the book is the author's own (`STY-PARAPHRASE`, `SRC-QUOTED`; v7) |
| Words per verse | floor `max(500, 8 × the verse's own words)`, capped 4,000; soft ceiling 5,000; **every paragraph past 120 words** — introduction and verses alike (`WRD-PARA-FLOOR`; v7) — a heading may carry one paragraph or several |
| Runs | **fifty verses per run** (v7.2), mapped from all eleven in one pass at the start (`run.py --plan/--build`), read in slices, and finished — every one of the fifty written and clean — before the writer pauses or stops (`run.py --check`) |
| Presentation | **no house style across verses** (v7.1): no stock opening frame, no wording of the commentary's own recurring verse to verse, no heading reused or templated, no single arrangement of headings and paragraphs through a long chapter (`STY-UNIQUE-VERSE`); quoted matter may recur, the author's voice may not |
| Interweaving | one reading in the book's own voice, not a report per source: no run of three authority-led sentences, no more than 30% of a section's sentences or 45% of its paragraphs opening with a named authority, and at least four sentences per verse that reason about it (`STY-SOURCE-PARADE`, `STY-ANALYSIS-FLOOR`) |
| Introduction | 250–1,500 words |
| Headings | **UPPERCASE** descriptive titles of the writer's own (context, history, story, ruling, explanation) — never the verse's own wording (`FMT-HEADING-CASE`, `FMT-HEADING-QUOTED`, `FMT-HEADING-VERSE`) |
| Quoting style | this verse's own phrases in **bold italics** (`***“phrase”***`, enforced by `PHR-QUOTE-STYLE`); clauses of other verses in **bold only** inside their reference (`(C:V — **“clause”**)`, enforced by `REF-QUOTE-STYLE`) — **every** cross-reference expanded with the clause it points to, bare citations warn at 1–2 and fail from 3 in a section (`REF-BARE`, v7.2; `reference.py` prints them) |
| Bold | **reserved**: only the UPPERCASE headings, this verse's phrases (bold italics) and other verses' clauses (bold only) may be bold — anything else fails `MTCH-BOLD`; reports and athar are italic `*"…"*` (`EVD-QUOTE-STYLE`) |
| Matching the verse | the prose explains what the verse's translation carries: a word or phrase that *means the same thing* — English or Arabic — is adjusted to the verse's own wording (`MTCH-SYNONYM`, informational), anything else fails (`MTCH-WORD`); Arabic offered as the verse's own wording fails (`MTCH-TERM`); a bold-italic quote that is not this verse's wording fails (`PHR-QUOTE-FOREIGN`) |
| Phrases | every phrase of the verse quoted **inside the prose**, in verse order, ≥90% coverage, no gap over 8 words, no single quote swallowing a verse (`PHR-*`); every quoted phrase backed beside it by a cross-reference, a hadith with its collection, or a named authority (`PHR-EVIDENCE`) |
| Evidence | every verse carries checkable anchors (a Qur'an cross-reference **with the clause it points to**, a hadith with its collection, a named early authority, a language point); every prophetic report names its collection; each verse reaches the reader's own world (`STY-APPLICATION`) |
| Analogy | at least half the chapter's verses carry a simple, relatable comparison |
| Diction | plain English; formal vocabulary fails (`STY-DICTION`) |
| Elements | history, reports with collections, cross-references, rulings, lesson, plain explanation, analogy and present-day application are carried by the prose and **never labelled** (`STY-LABELS`: no `Lesson:`, `Modern application:`, `History:`, …) |
| Sentences | mean under 22 words (warn 26, fail 32); under 8% above 40 words |
| Reading ease | Flesch 60+ (warn 55, fail 45) |

**Standard v7.0 (2026-09-25) — the author's own book.** The chapters are not a survey of the
sources: they are one author's commentary, learned from them and written new. A sentence that
relays a work's opinion, compares the works, or quotes one of them fails (`STY-PARAPHRASE`,
`SRC-QUOTED`); the old naming quotas (`SRC-SPREAD`, `SRC-FAMILY`, `SRC-UNUSED`) are retired. The
sources' contents are taken as authenticated, so the writer neither fact-checks them nor grades
their chains. Every paragraph — in the introduction and in every verse — runs past 120 words
(`WRD-PARA-FLOOR`), and every verse reaches the reader's own world at least once
(`STY-APPLICATION`, warn). The evidence a reader checks is unchanged: Qur'an cross-references,
reports with their collections, named early authorities, language points. Full statement:
`TAFSIR_RULES.md` §0.

## Progress

**Six author-named fifty-verse runs are delivered (2026-09-26).** The first chapter-only start resolved
to 2:1 and pinned **2:1–2:50**. All eleven works were mapped in one pass; the introduction and fifty
verse drafts were written, spliced and gated. Its gate reported 0 FAIL and 53 advisories.

The author then named **2:51** exactly, pinning **2:51–2:100**. The second fifty add 43,365 words,
with 730/859/1,062 as the minimum, median and maximum. Its own gate reports 0 FAIL and 51
advisories: 38 reasoning-floor preferences and 13 upstream `tafsir_initial` coverage gaps. The
growing 2:1–2:100 gate also passes at 0 FAIL and 105 advisories.

The author next chose chapter 2, which resolved to its first unwritten verse and pinned
**2:101–2:150**. This third run adds 40,937 words, with 718/808/1,427 as the minimum, median and
maximum. Its gate reports 0 FAIL and 45 advisories: 39 reasoning-floor preferences and six upstream
`tafsir_initial` coverage gaps. The growing 2:1–2:150 gate passes at 0 FAIL and 178 advisories.

After that delivery, the author said to continue and named **2:151**, pinning **2:151–2:200**. The
fourth run adds 46,129 words, with 724/882/1,307 as its minimum, median and maximum. Its exact gate
reports 0 FAIL and 81 advisories; the growing 2:1–2:200 gate reports 0 FAIL and 279 advisories.

The author then continued from **2:201**, pinning **2:201–2:250**. The fifth run adds 56,019 words,
with 901/1,123/1,438 as its minimum, median and maximum. Its exact gate reports 0 FAIL and 141
advisories; the growing 2:1–2:250 gate reports 0 FAIL and 425 advisories. `run.py --check` reports
**RUN COMPLETE — 50/50 written, 0 failing** for the pinned fifth run.

The author then named **2:251**, so the sixth run crossed a chapter boundary: **2:251–2:286 plus
3:1–3:14**. The chapter-2 portion adds 41,257 words, with 738/1,100/2,029 as its minimum, median and
maximum; the chapter-3 portion adds 11,508 words, with 707/775/1,087 by the part-file count. The
exact 2:251–2:286 gate, exact 3:1–3:14 gate, growing chapter-2 gate, and `run.py --check` all pass
with 0 FAIL. Every verse in the run has complete canonical phrase coverage, transmitted evidence,
an expanded cross-reference, present-day application and a relatable analogy.

Completing 2:286 also completed Al-Baqarah. Its whole-file audit passes with 0 FAIL, the chapter has
266,252 verse words, and `data/tafsir_002.json` was built from the markdown and checked current.
`sw.js` moved to `quran-reader-v2.5.48`. Chapter 3 remains deliberately unpublished because
3:15–3:200 are still scaffolds.

| Ch | File | Verses | Words | Range (min/med/max) | Gate |
|---|---|---|---|---|---|
| 1 | `tafsir/001.md` | 7/7 | 6,896 | 833/961/1,094 | PASS; published |
| 2 | `tafsir/002.md` | 286/286 | 266,252 | 703/867/2,029 | PASS; published |
| 3 | `tafsir/003.md` | 14/200 | 11,508 | 707/781/1,087 | 3:1–3:14 PASS; 186 verses still scaffold |

Totals: **2 of 114 chapters complete, 307 of 6,236 verses written.** Chapters 1 and 2 have current
payloads. Chapter 3 has a 617-word introduction and clean prose through 3:14 but no payload. A
completed run does not choose its successor: the author must name the next chapter or chapter:verse;
naming chapter 3 now would resolve to 3:15.

**Corpus cleared for v7.2 (2026-09-25).** The commentary generated for chapter 1 (7 verses, 4,339
words, previously gated 0F/0W) and the written part of chapter 2 (the introduction and 2:1–2:19, 13
of them gated clean and 6 drafted) was deleted at the author's direction, because the standard
changed under it: `tafsir/001.md`, `tafsir/002.md`, the payload `data/tafsir_001.json` and the whole
chapter-2 drafting bench (`tmp/work/`) are gone, the stale digests are dropped, and the cached app
entry is dropped (`sw.js` → `quran-reader-v2.5.45`). The deleted files stay in git history for the
record but are not the standard any longer: chapters are written again from verse 1 under v7.2.

**Standard v7.2 (2026-09-25).** Added on the author's instruction, three changes:

1. **The eleventh work.** `tafsir_initial/` (the study-Quran-style draft) joins
   `corpus.SOURCE_ALLOWLIST`: all eleven are digested and read for every verse before a word is
   written, the draft like the rest — and, like the rest, never relayed, compared or quoted. Its
   coverage is partial, so a verse it does not carry is a coverage gap for that verse only.
2. **Every cross-reference is expanded with its translation** — `(C:V — **“the clause”**)`, copied
   verbatim from `data/chapter_NNN.js`. A bare citation, or a list of them, no longer counts:
   `REF-BARE` warns at one or two in a section and fails from three. `scripts/tafsir/reference.py`
   prints ready-made citations (`C:V`), finds a verse by its wording (`--find`), and lists (or
   applies) the expansion of every bare citation in a chapter (`--scan [--write]`).
3. **Fifty-verse runs.** `scripts/tafsir/run.py` plans the next fifty verses (chapter order, across
   chapters as needed), maps them out of all eleven works in one pass — the sources are opened once
   for fifty verses, not once per verse — and reports the run's state; `--check` prints RUN COMPLETE
   only when every one of the fifty is written and clean. `scripts/tafsir/assemble.py` splices the
   `tmp/work/` drafts into the chapter file. The law is in `TAFSIR_RULES.md` §0.8–§0.9 and §11.4,
   and proved by `ruletest.py` (the cross-reference levels; the eleven named and the study draft
   relayed) with the auditor (77 codes now).

**History, for the record.** Chapter 1 was written under v7.0 and frozen by the author under v7.1
(`audit.py 1` → 0F/0W/1I, 4,339 words, payload 25,857 B), and chapter 2 had reached 2:1–2:13 clean
plus 2:14–2:19 drafted. An earlier corpus (chapters 1–3, 329,000 words) had been cleared the same
way on 2026-09-25. All of it is readable in git history and none of it is the standard any longer.

**Standard v7.4 (2026-09-26).** Two laws added on the author's instruction, after studying the
professional English diction of a published tafsir (*Illuminating Discourses on the Noble Qur'an*,
vol. 1) **for its style of writing and choice of words only** — nothing of its content, arrangement
or wording is carried into this book, and it is never named or quoted in it. Every earlier rule
remains in force.

1. **The register of the book** (§0.11). The book has one voice: plain declarative sentences, one
   idea to a sentence; third person throughout (never "you", never an authorial "we"); no
   contractions, no exclamation marks, no hype words, no praise of the text in place of its
   explanation; a question raised only where it is settled in the same movement; terms of art
   glossed once in place and then used; evidence in plain reporting language. This is a register,
   not a shape: §0.7 still forbids a stock opening, a heading template or one arrangement used by
   most verses.
2. **The independence law** (§0.12). The commentary is an independent book: it names, summarises,
   paraphrases and quotes no work — neither the eleven behind it nor any other. What it may quote
   is what those books themselves quote as evidence: the Qur'an in the book's own citation form
   (every clause verbatim), a report (hadith or athar) in the straight-quote style with its
   collection named in the same sentence, or a transmitted reading attributed to an early authority
   by name. The point written is the book's own.

Enforcement: `audit.py` gains `IND-WORK` and `IND-QUOTE` (a work named in the prose; a quotation of
six words or more that hangs on no reference) and `STY-CONTRACTION`, `STY-EXCLAIM`, `STY-HYPE`,
`STY-QUESTION` — the register codes measured on the book's own words only, with quotations stripped
first so a quoted report may carry whatever it carries. `selftest.py` carries a firing mutation for
each (uncaught rules 0 / rules not exercised 0 / false alarms 0), `ruletest.py` green, and the
ruling text lives in `TAFSIR_RULES.md` §0.11–§0.12 with the codes in Appendix A.

**Chapter 1 generated under v7.4.** `tafsir/001.md`: the introduction (862 words) and al-Fatihah
1:1–1:7 written from all eleven works, 7,646 words in all, mean sentence 25 words.

* every verse carries an expanded cross-reference with its clause and a transmitted reading — a
  named early authority or a report with its collection — and a relatable analogy;
* no work is named anywhere in the chapter, and nothing is quoted that does not hang on a reference
  (`IND-WORK`, `IND-QUOTE` clean);
* `audit.py 1` → **0 FAIL, 10 WARN, 3 INFO — RESULT: PASS**;
* chapter 2 remains a scaffold at the author's instruction; the chapter-2 drafting bench is
  removed.

**Chapter 1 published (2026-09-26).** `build_data.py 1` built `data/tafsir_001.json` from
`tafsir/001.md` (7 verses, 862-word introduction, 7,774 words in all, 42,803 bytes) and `--check`
confirms it still matches the markdown. `sw.js` moves to `quran-reader-v2.5.47` with
`RETIRED_PAYLOADS` emptied again: chapter 1 is current text now, so the URL must be kept rather
than purged from a device's cache. The app fetches `data/tafsir_NNN.json` by chapter number, so
publication is the payload plus that cache-version bump and nothing else. Chapter 2 stays
unpublished — `build_data.py` refuses to build while any verse is still a `TODO` scaffold.

**Continuity pass (2026-09-26).** `TAFSIR_HANDOFF.md` now opens with an *If you are told to
continue* section: the branch the work lives on, the reading order, the scratch that is not in git
(`tmp/sources/`, `tmp/runs/` — `run.py --build`, or `sources.py N` for a chapter outside the current
run; `SRC-NODIGEST` means a missing scratch file, never a defect in the prose), the lines to expect
from the gate on the inherited state, the run in force (**2:1–2:50** — the planner re-anchors at the
first unwritten verse now that chapter 1 is complete), and the publish sequence for chapter 2. The
author's v7.4 instruction is quoted verbatim in the law list beside the earlier ones, the code count
is corrected to 88, and `README.md` / `TAFSIR_PIPELINE.md` name v7.4 as the standard in force. No
rule, chapter or payload changed in this pass.

**The run law, v7.5 (2026-09-26).** On the author's instruction, the run of fifty verses is now cut
from a start **the author names** and verified as fifty before a call is finished:

* `run.py --plan --start N[:M]` — a chapter (`2`, meaning that chapter's first unwritten verse) or a
  chapter:verse (`2:1`) — cuts the fifty from there and pins them; `--build`, `--slice`, `--status`
  and `--check` all read that same pinned run, so a run in flight is never re-cut to the frontier.
  Naming a different start re-cuts the run from there; naming the same one returns the fifty in hand.
* a completed chapter is a stop rather than a guess: the planner reports it and waits for the next
  start.
* `run.py --check` prints RUN COMPLETE only at **50/50** written and clean, and says so in the plan
  output: a call that stops at 49/50 has not finished the run.
* **when the instruction is only "continue", the first act is to ask where the run starts and to
  wait for the answer** — no verse is planned, mapped or written before it comes. The law is written
  into `TAFSIR_RULES.md` §0.9, `TAFSIR_PROMPT.md` (instructions 1 and 4), `TAFSIR_PIPELINE.md` §5,
  `README.md` and `TAFSIR_HANDOFF.md` ("When the author says continue"), and proved mechanically by
  `scripts/tafsir/ruletest.py`, which exercises the planner's own code
  (`v7.5 — a run is fifty verses, cut from the start the author named`).

**Pinned-run completion fix (2026-09-26).** Writing the fiftieth draft used to make the planner
release the current manifest before `--check` could judge it, because “written” was mistaken for
“written and clean.” The pin now remains authoritative until the author names another start.
`--status`, `--slice` and `--check` therefore keep reading the same fifty even after all fifty hold
prose; `--check` reports RUN COMPLETE and waits for the author's next start. The added eighth v7.5
planner expectation sets all fifty to written and proves that the pin still does not move. The default
mutation self-test now selects only complete chapters, so a partly written chapter's expected
scaffold failures cannot hide the finding introduced by a test mutation.
