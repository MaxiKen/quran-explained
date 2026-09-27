# Tafsir handoff — how to pick this work up

Read this file first, then `TAFSIR_RULES.md` (the normative rule set, **v8**) and
`TAFSIR_PROMPT.md`. `TAFSIR_WORKLOG.md` is the progress ledger. Fifty verses are both the source-map
unit and the maximum independent-review checkpoint: write in order and mechanically check each verse,
while automatic drift alarms still run every fifty verses. Whenever generation stops, make the written
range a clean review candidate, commit it, and push it to GitHub before owner confirmation—even when
the chapter or review is incomplete. Independent acceptance still gates publication and the next
fifty-verse run. Review covers the complete source map, material omissions, Qur'an citations, every
named transmitted report, and language or consequential legal/theological claims—not only metrics.
`QUALITY DRIFT` is a mandatory stop, notification, and checkpoint push.

## When the author says "continue" (start here)

**The call may come on any branch.** Nothing in the rules or tools assumes a branch name. Read the
actual repository state, stay on the branch assigned to the session, and push there. Never restore
or copy the purged Chapter 2 draft from history.

**Resume a pinned run; otherwise ask where to start.** The author names the start of every new run,
and it is not chosen by the writing agent. If `run.py --plan` shows an existing pinned run, “continue”
resumes its next unwritten verse. Only when no run is pinned should a bare “continue” trigger a
question asking for a chapter or chapter:verse. The current run was explicitly pinned at 2:1.
**Owner approval has been received.** The author explicitly approved checkpoint `06ec1c6`
and requested further generation. That approval is recorded in `TAFSIR_WORKLOG.md`; do not ask
for the same general approval again. The detailed review records below are still pending, and no
scores or independent-review attestations have been fabricated. The next start and whether author
approval should authorize drafting before the detailed records are complete await clarification.

**All fifty verses of the pinned 2:1–2:50 run now have prose.** Verses 2:1–2:5 and 2:16–2:33
are accepted; 2:6–2:15 and 2:34–2:50 remain pending review. The contiguous accepted frontier is
still **2:5**. There is no unwritten verse left inside this pin. The next task is independent
review, not generation or regeneration. Do not open 2:51 or re-plan a run until the current run
is independently accepted and the author names the next start. If ignored scratch has disappeared,
restore the documented pin:

```bash
python3 scripts/tafsir/run.py --plan --start 2:1 # pins 2:1–2:50
python3 scripts/tafsir/run.py --build --cap-json 0 # full eleven-source digest; display caps are separate
python3 scripts/tafsir/run.py --slice 2:43 2:50   # read the map for the final pending checkpoint
```

During an authorized drafting run, write in verse order and gate each verse with `batch.py ... --draft`. At every
actual generation stop, create or refresh `quality.py --template` for the written candidate (never
more than fifty unaccepted verses), run `batch.py ... --push-check`, commit, and push. This happens
before owner confirmation and does not wait for chapter completion. A different reviewer then
compares every fingerprinted source passage with the prose, groups duplicate works into distinct
material points, accounts for omissions, completes the rubric and claim ledger, judges every Qur'an
citation, and locates every named report or early authority in an allowlisted source before
`batch.py` may grant acceptance. Do not open a fifty-first unaccepted verse. `QUALITY DRIFT` stops
generation, is reported immediately, and triggers a push of the clean checkpoint. `run.py --check`
reaches RUN COMPLETE only when all fifty are mechanically clean and independently accepted.

Before any of that, two housekeeping steps:

1. **Read the rules first.** `TAFSIR_RULES.md` (**v8** — §0.11 the register, §0.12 independence,
   §0.13 Chapter-1 parity) is normative; `TAFSIR_PROMPT.md` is the generation prompt built on it; this file is the
   working state; `TAFSIR_WORKLOG.md` is the ledger.
2. **Rebuild the scratch that is not in git.** `tmp/sources/` and `tmp/runs/` are ignored by design,
   so a fresh clone (and, in practice, a fresh session) has neither and the auditor reports
   `SRC-NODIGEST` on every verse until they are rebuilt. One pass does it:
   `python3 scripts/tafsir/run.py --build --cap-json 0` (the run's chapters, all eleven works, uncapped digests
   for the grounding check); a chapter outside the current run needs its own digest back —
   `python3 scripts/tafsir/sources.py 1`. **`SRC-NODIGEST` is a missing scratch file, never a defect
   in the prose.** The drafting bench `tmp/work/*.md` **is** tracked, so part files from earlier
   sessions are present and must not be overwritten.

State to expect on arrival (2026-09-27): the source-enriched Chapter 1 is independently approved,
frozen as the raised quality floor, and published. Its accepted source/claim/evidence reviews are in
`quality/reviews/001/001-005.json` and `006-007.json`, with owner approval in
`quality/chapter-001-baseline-approval.json`. The old Chapter 2 commentary was purged from current
state without rewriting history. A fresh introduction and 2:1–2:5 were generated from all eleven
works and independently accepted by the project owner in `quality/reviews/002/001-005.json`.
The accepted `016-024.json` and `025-033.json` bring the Chapter-2 accepted count to 23.
The pending manifests are `006-006.json`, `007-015.json`, `034-042.json` and the new
`043-050.json` (27 verses). The earlier checkpoint refreshed only the pending 2:11–2:12 entries
for small prose/heading fixes. Completing 2:43–2:50 changed no inherited prose or review decision.
All written verses, 2:1–2:50, pass the mechanical, fifty-verse quantitative and review-candidate
push gates. Verses 2:51–2:286 remain scaffolds. The pin remains 2:1–2:50, **REVIEW PENDING**;
`run.py --status` exits nonzero in that state even though the push check passes.

## Where things stand (2026-09-27)

| | |
|---|---|
| Repo | `MaxiKen/quran-explained`, latest writing branch `arena/01a0e398-quran-explained` |
| Written | **Chapter 1 is independently accepted, published and frozen as the raised quality floor**. Chapter 2 has 50/286 verses written: 23 accepted (1–5, 16–33), 27 pending (6–15, 34–50), 236 scaffolds. |
| Next | Independent review of **2:6–2:15 and 2:34–2:50**. No new run until acceptance and an author-named start; 2:51 is still scaffold. |
| Standard | **v8 raised**: all v7.4 laws plus Chapter-1 parity, all-source fingerprint/synthesis review, substantive-claim, Qur'an and transmitted-evidence ledgers, independent rubric, maximum fifty-verse review candidates, fifty-verse automatic drift windows, and immediate stop/push notification. |
| Sources | the **eleven** of `corpus.SOURCE_ALLOWLIST`: al-Ṭabarī, al-Qurṭubī, al-Baghawī, Ibn Kathīr, al-Ālūsī, al-Jalālayn, Ibn ʿAbbās, al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān **+ `tafsir_initial`** — research only, never named, relayed, compared or quoted |

Chapter 2 keeps byte-exact verse quotes throughout. The tracked drafting bench holds
`tmp/work/c2_intro.md` and fresh `c2_v001.md`–`c2_v050.md`. The purged old prose formerly in
`c2_v006.md`–`c2_v100.md` must not be restored or copied; the current parts through 050 are
replacement drafts from the eleven-source map. New 2:43–2:50 has 100% phrase coverage and clears
all word floors; each verse was spliced and immediately draft-gated. All eleven mapped source
entries were checked before drafting each of those verses, with full Arabic readings and reuse of
already-read, byte-identical shared passages. Independent source-synthesis, claim, evidence and
rubric decisions remain for the reviewer. No Chapter-1 text, payload, baseline, rule or script changed.
`tafsir_initial` has no mapped passage at 2:38–2:39; this is an upstream coverage gap, not a reason
to use an outside source. Measured state:

```
python3 scripts/tafsir/audit.py 1                    # raised Chapter 1: mechanical PASS
python3 scripts/tafsir/build_data.py 1 --check       # accepted payload matches
python3 scripts/tafsir/quality.py --baseline         # validates raised frozen hash and floor
python3 scripts/tafsir/batch.py 2 --from 1 --to 5    # accepted Chapter-1 parity checkpoint
python3 scripts/tafsir/batch.py 2 --from 1 --to 50 --push-check # PASS; pending reviews remain
python3 scripts/tafsir/quality.py --all --push-check # all current review candidates are push-clean
python3 scripts/tafsir/qualitytest.py                # parity gate regression suite
python3 scripts/tafsir/audit.py 2                    # TODO failure on 2:51–2:286 (expected)
```

The full Chapter 2 gate fails only because the chapter is intentionally incomplete. No
`data/tafsir_002.json` is published from this partial state.

## The law this book is written to

The author's instructions, verbatim, in force:

* "There shouldn't be a standard diction use or phrased introduction/presentation used
  across verses. Each verse content should be uniquely presented not following a
  standard presentation or arrangement for other verses. And there's no rule that
  states there should be one paragraph content per heading, you can have more than
  one, just that each paragraph must must contain more than 120 words."
* "tafsir_initial should be added as one of the sources now making 11. All the 11
  sources are to be looked into before anything is generated. All Quran cross
  reference should be expanded with their translation content etc."
* "I want you to only study is for your choice of diction and professionalism. You're not
  copying it's contents. Its style of writing and choice of words is what I want you to study.
  Write that style etc to replicate something like that into the rule. The additional rule to also
  be documented is You're not to qoute any book since this is to be an independent book, you can
  only quote the references in those books like those books do and make original point. Every other
  rule remains. Add and enforce the rules." — in force since 2026-09-26 as **§0.11** (the register:
  the diction studied from a published tafsir's style and choice of words only, never its content)
  and **§0.12** (the independence law: no work is named, relayed or quoted anywhere; the book cites
  the reference itself and makes its own point), mechanised as `IND-WORK`, `IND-QUOTE`,
  `STY-CONTRACTION`, `STY-EXCLAIM`, `STY-HYPE`, `STY-QUESTION`.
* "I want you to be generating content for 50 verses in every badge. And I want the
  total generation process to be fast. An approach you can take is to at the start
  map out 50 verses (it might be across 2 chapters o more) from all sources (this is
  to avoid opening 11 sources Everytime to get content). After, you can start
  processing and writing but that 50 result must be completed before you pause or stop." Later
  instructions qualify this: fifty is also the maximum unaccepted review candidate, automatic
  degeneration alarms still run every fifty verses, and any actual generation stop triggers an
  immediate clean checkpoint commit and push before confirmation.
* The book is **the author's own unique and modern commentary, backed by evidence**.
  The eleven works are research: learn from them, then write the book's own reading —
  never relay, compare, summarise or quote them, and never cite a work outside the
  eleven.
* "Add every other rule you feel is necessary for generation of the best of contents backed by
  evidences from sources and that is later generations doesn't lose content quality. Make them go
  round." This is enforced by source fingerprints, full-map synthesis review, material-omission
  decisions, Qur'an and transmitted-evidence relevance ledgers, explicit language/legal/theological
  claim verification, and the same
  complete review before Chapter 1 itself may be raised.
* Their authenticated contents are taken as they stand: **no fact-checking** is
  required or wanted.
* **Each paragraph must be greater than 120 words** (`WRD-PARA-FLOOR`). A heading may
  carry one paragraph or several.
* Every verse section quotes each phrase of the verse in **bold italics** and explains
  it; every cross-reference is **expanded with the clause it points to**, copied from
  `data/chapter_NNN.js`; the commentary's own voice carries no emphasis.

`scripts/tafsir/audit.py` mechanises all of it (88 codes). `scripts/tafsir/ruletest.py`
proves the v7/v7.2 checks with no chapter on disk (they are the only proof that runs
while the corpus is empty); `scripts/tafsir/selftest.py` mutates a *written* chapter, so it
is live again now that chapter 1 is written — it carries a firing mutation for every code,
including the v7.4 ones (`IND-WORK`, `IND-QUOTE`, `STY-CONTRACTION`, `STY-EXCLAIM`,
`STY-HYPE`, `STY-QUESTION`), and must print `uncaught rules: 0 | rules not exercised: 0 |
false alarms: 0` after any change to the gate.

## The gait for one run (50 verses)

1. **Plan and map once, from the author's start.** `python3 scripts/tafsir/run.py --plan --start 2:1`
   cuts and pins the fifty from the verse the author named (ask for it when the instruction is only
   "continue");
   `python3 scripts/tafsir/run.py --build` pulls all eleven works for the run's chapters
   in one pass (~22 s for chapters 1–2) and writes `tmp/runs/run-001.txt` plus the
   per-chapter digests the auditor's grounding check reads (`tmp/sources/NNN.json`).
   The map is written with caps (`--cap-en`, `--cap-ar`, `--cap-json`); the whole run
   is read in slices, never by re-opening the raw sources.
2. **Read the map a stretch at a time.** `python3 scripts/tafsir/run.py --slice 2:1 2:5`
   prints those verses with all eleven works beneath them. Raise the caps for one verse
   when it needs the full discussion (`--slice 2:255 2:255 --cap-ar 4000`).
3. **Collect evidence, not prose**: occasions of revelation, reports with collections
   and narrators, the early authorities' glosses (Ibn ʿAbbās, Mujāhid, Qatādah,
   al-Suddī, ʿIkrimah), the language point that changes the meaning, the ruling, and
   the cross-references that let the Qur'an explain itself. Arabic works are first-class:
   read them and put the substance into the book's own English.
4. **Write one section into a part file**, `tmp/work/cN_vVVV.md`, splice with `assemble.py`,
   and run `batch.py N --from V --to V --draft`. Never edit the assembled chapter by hand. Do not
   open a fifty-first unaccepted verse; automatic fifty-verse metrics remain early alarms.
5. **Expand every cross-reference with the tool, never by hand**:
   `python3 scripts/tafsir/reference.py 2:255` prints ready-made citations;
   `--scan N` lists every bare citation in a chapter with its replacement (`--write`
   applies them). A typed clause is where `REF-QUOTE` failures come from.
6. **At every generation stop, push before confirmation.** Create or refresh the quality review
   template for the written range (maximum fifty), run `batch.py ... --push-check`, then commit and
   push the incomplete/pending candidate. The project owner reviews that GitHub state. A different
   reviewer compares all fingerprinted source passages with the draft, records omissions, scores
   every rubric dimension, verifies every Qur'an citation, and gives every named transmitted
   statement a matching fingerprinted allowlisted passage reference, excerpt and relevance decision.
   After approval is recorded, run `batch.py` without either draft flag for `QUALITY PARITY PASS`.
7. **Quality drift is the stop and push point.** Report the trigger, blocked range and last accepted
   verse immediately, preserve the clean state, and push it. `run.py --check` completes only when all
   fifty have passed both gates; pending review never authorizes the next run or publication.
8. **When a chapter is finished**: `audit.py N` and `quality.py N` must both pass, then run
   `status.py N`, `build_data.py N`, bump `sw.js` `CACHE_VERSION`, add the worklog row
   (`status.py --md`), and push the publication commit. Chapter completion is not a prerequisite for
   earlier review-candidate pushes.

Useful while writing:

```
python3 scripts/tafsir/run.py --status          # the fifty: words vs floors, failing verses
python3 scripts/tafsir/batch.py 2 --progress    # how far one chapter has come
python3 scripts/tafsir/quality.py --baseline    # verify frozen Chapter-1 floor
python3 scripts/tafsir/quality.py 2 --from A --to B
python3 scripts/tafsir/qualitytest.py
python3 scripts/tafsir/reference.py --find "the Most Compassionate" --chapter 2
python3 scripts/tafsir/match.py 1:4 "the day of reckoning"   # is this the verse's wording?
python3 scripts/tafsir/verify.py "<claim>" --chapter 2       # do the sources carry this?
python3 scripts/tafsir/assemble.py 1 --check    # drafted / not drafted, verse by verse
python3 tmp/work/dig.py 2 2500 900            # bench helper: one verse, all eleven, capped
```

## Gate findings learned while writing the cleared chapters

Each of these is a real failure the gate raised; the cure is the one that worked.

* **`REF-BARE` (new in v7.2)** — a citation with no wording, `(2:255)`, or a list,
  `(2:156, 245, 281)`, warns at one or two in a section and fails from three. Cure:
  `reference.py --scan N --write`, then read the prose to check the clause fits.
* **`REF-QUOTE`** — a cited clause must be byte-exact; copy it from `reference.py` or
  `C.ayah_en(c, v)` rather than typing it (the `˹…˺` brackets and em dashes are where it
  breaks). `REF-QUOTE-REPEAT` warns on citing the same verse twice in one section.
* **`MTCH-TERM` / `AS_VERSE_TERM`** — a sentence saying "the verse says/names/… *word*"
  fails when the translation does not carry that word. Cure: make it passive, drop the
  subject, or rephrase plainly. Arabic terms that are *not* name-exempt and do fire it:
  Allāh, Shayṭān, taqwā, falāḥ, ṣalāh, zakāh. Safe (exempt): God, Gabriel, the devil,
  hadith collections, early authorities, "unseen", "prayer", "success", "certainty".
* **`MTCH-WORD`** — the prose must not explain wording the verse's translation does not
  carry. The false friends are ordinary words (*covers, easier, behind, formed, since,
  runs, cannot*). Cure: rephrase so the flagged word is not in explaining position, or
  drop the study frame. (v7.2 fix: the `WORD_STUDY` path now only reads a headword when
  the sentence is actually studying it — "with the name before he wrote" is no longer
  read as word-study of *before*.)
* **`PHR-EVIDENCE`** — every quoted phrase needs an anchor in its own paragraph or the
  next one: an expanded cross-reference, a report with its collection, a named early
  authority, or a language point.
* **`PHR-PHRASE-MISSING` / `-EDGE` / `-GAP` / `-COVERAGE`** — quote *every* phrase, in
  verse order, ≥90% coverage, no gap over 8 words. A long verse's middle phrase is the
  one usually forgotten.
* **`EVD-ATTRIBUTION`** — the collection must stand **inside the sentence that carries
  the report** ("The Prophet ﷺ said, *\"…\"* as al-Bukhārī carries it"), not in the next
  sentence.
* **`STY-ANALYSIS-FLOOR`** — at least 5 sentences per verse must reason about the verse
  (cure words: because, since, which means, which is why, that is why); 9 is the
  comfortable target. Adding a sentence can trip `MTCH-WORD`, so re-gate after every
  addition.
* **`STY-ANALOGY`** — one relatable comparison per verse, woven in, and the gate has to
  *see* it: "think of", "imagine", "it is like", "the way a", "picture". A comparison
  without one of those markers counts as absent.
* **`STY-APPLICATION`** — at least one line reaching the reader's own world (*today,
  these days, this week*), unwritten as a heading or label.
* **`STY-PARAPHRASE`** — never let "the sources", "the commentators", "the tafsīrs", a
  work's name or the study draft speak in the prose; the sentence fails even when the
  quotation marks are absent.
* **`EVD-THIN`** — a verse needs two kinds of anchor among quran/hadith/scholar/
  language. A name alone is not a collection; the scholar kind is satisfied by Ibn
  ʿAbbās, Mujāhid, Qatādah, Ibn Masʿūd, al-Ṭabarī, al-Qurṭubī and the rest of `SCHOLARS`.
* **`STY-UNIQUE-VERSE` (v7.1)** — the free prose of two verses may not share a 4-word
  opening (2 WARN / 3 FAIL), six unquoted words in a row (WARN / FAIL), a heading, or a
  two-word heading prefix. The habitual offenders read like one author's tics: *"Ibn
  ʿAbbās is reported to have"*, *"is reported to have said that"*, *"in it, which is why
  the"*. Cure: write the sentence a different way rather than synonym-swapping.
* **`GRD-TOKENS`** — distinctive names should appear in that verse's source digest;
  quoted matter and the first word of a paragraph are ignored. Cure: drop the name or
  cite a clause that passes.
* **`MTCH-BOLD` / `PHR-QUOTE-FOREIGN` / `EVD-QUOTE-STYLE`** — bold is reserved for the
  UPPERCASE headings, this verse's phrases (`***“…”***`) and other verses' clauses
  inside their reference (`**“…”**`); reports and authority quotes are `*"…"*` in
  straight quotes, and Qur'anic wording is never straight-quoted. **Watch the quote
  characters**: a straight quote typed into some editors comes back as a curly one,
  which the gate reads as a Qur'an clause (`EVD-QUOTE-STYLE`, `REF-UNANCHORED`).
* **`WRD-PARA-FLOOR`** — every paragraph, in the introduction too, must run past 120
  words. The introduction itself is 250–1,500 words with no headings.
* **Sentence metrics** — mean sentence under 26 words (fail 32), under 12% above 40
  words, Flesch 62+. A section written at 30+ words a sentence fails the chapter even
  when every other rule passes: keep the sentences short and the paragraphs long.
* **`SRC-BANNED`** — never cite al-Wāḥidī, al-Kalbī, al-Shawkānī or any other work
  outside the eleven, and never name `tafsir_initial` or "the Study Quran" as a voice.
* **`STY-PARAPHRASE` catches the carry-alls too** — "the sources", "the commentaries",
  "the tafsīrs" count as a work's voice even with no name attached, and a report verb
  beside them ("as the sources carry it") fails outright. Write the point; leave its
  provenance in the digest.
* **`MTCH-WORD` can land on an ordinary connective.** A sentence that reads as
  explaining *before*, *since* or *behind* — words the verse line does not carry — is
  reported by the headword. Explain only what the verse line says, and keep the
  explanatory frame for those words alone.

## If the sandbox wipes the scratch directory

Ignored source digests and run maps can be rebuilt without resetting the checkout. The tracked
chapter and `tmp/work/` parts are the prose record; preserve any local changes and remain on the
branch assigned to the session. Do not reset to a branch named in an older handoff.

```bash
git status --short
git log --oneline -3
python3 scripts/tafsir/run.py --plan --start 2:1  # restore the documented 2:1–2:50 pin
python3 scripts/tafsir/run.py --build --cap-json 0 # full passages, not a truncated research digest
```

The current continuation branch is `arena/01a0e398-quran-explained`. Push only to the branch
assigned to the current session, never to `main`. An incomplete or pending review candidate still
needs its ordinary checkpoint commit and push; it does not authorize a force-push or the loss of
another session’s work.

## House facts worth not rediscovering

* `audit.py --json` is broken; use the text runs. `audit_chapter(chapter, opts, path=None)`
  wants an argparse Namespace; there is no `--file` flag. `audit.py N` on a chapter with
  scaffolding fails by design (`TODO`) — gate a stretch with `batch.py N --from A --to B`.
* `audit.py N` counts 88 codes now; `selftest.py` needs a **written** chapter, so it is
  skipped until verse 1 of the run lands (chapter 1 is written, so it runs). `ruletest.py` is the proof that runs with an
  empty corpus.
* Intros are `## Introduction to the Sūrah`, plain paragraphs, no `**` inside.
* A verse section is: `## Verse 2:N`, a blank line, the `> verse line` exactly as the
  scaffold holds it, a blank line, the body, a blank line, `---`.
* Rebuild the payload after *any* prose edit: `build_data.py` compares the chapter file
  with `data/tafsir_NNN.json` and reports stale payloads.
* `tafsir_initial/002.md` does not carry 2:285–2:286 (it stops at 284); missing verses
  there are `SRC-ABSENT` warnings, not failures.
* The run-map display is capped (`--cap-en 2400`, `--cap-ar 700`), separately from the
  per-chapter JSON. For drafting, use `run.py --build --cap-json 0` once to retain the full
  source passages in `tmp/sources/NNN.json`. Raising a display cap cannot recover text already
  truncated in the JSON. Read long passages in slices small enough to avoid tool-output truncation.

## Gate lessons that cost time (v7.2–v7.4, chapters 1–2)

* `WRD-PARA-FLOOR` is strict: 120 words fails, 121 passes. Measure every paragraph with
  `len(C.words(p))` over `C.split_paragraphs` **after** each edit — fixing one paragraph
  can push its neighbour under the line.
* `PHR-EVIDENCE`: every paragraph that explains a quoted phrase needs its own anchor —
  a cross-reference, a report with its collection, or a named early authority. One anchor
  at the end of a quote-heavy section leaves EVD-NONE + several PHR-EVIDENCE open.
* House phrases are caught as repeated six-word runs across verses (`STY-UNIQUE-VERSE`):
  "the book does not describe the", "at the end of the line", "the practical content of the
  verse is", "for a reader today the verse" all had to be varied. `tmp/phrase_lint.py`
  (bench helper) lists them before the gate does.
* Headings repeat as well: three verses opening a heading with the same two words fail
  ("WHY THE" ×5 at one point). Check every new heading against the chapter's existing
  openings.
* Never write "the verse says plainly X" or "the verse names X" unless X is literally in
  the verse translation — `MTCH-TERM` fires, and so does `MTCH-WORD` on ordinary verbs
  read as glosses.
* Only `reference.py candidates()` text may be quoted (`REF-QUOTE`), and a cross-reference
  must be the full `(C:V — **“…”**)` expansion (`REF-BARE` fails on a bare number).
* Gate the wide range, not just the new verses: `batch.py 2 --from 1 --to N` before every
  commit, because cross-verse repeats only show up against the earlier work.
* Run the gate as its own command and read "0 FAIL" before committing; `grep -E "FAIL|RESULT"`
  exits 0 on matches, so `&& git commit` chains have committed with failures still open.
