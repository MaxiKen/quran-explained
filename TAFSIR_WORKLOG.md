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

**The next run is planned and mapped.** Run 1 of the v7.2 standard is **1:1–1:7 (all of al-Fātiḥah)
followed by 2:1–2:43** — fifty verses across two chapters, floors totalling about 25,000 words of
commentary. All eleven works are already digested for chapters 1 and 2 (`python3 scripts/tafsir/run.py
--build`, ~22 seconds for 293 verses) and the map is `tmp/runs/run-001.txt`; the chapter files are
scaffolded with byte-exact verse quotes. The run is not started.

| Ch | File | Verses | Words | Min/Med/Max per verse | Analogy | Gate | Payload |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

Totals: **0 of 114 chapters written, 0 of 6,236 verses.** The next run covers 50 of them.

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
