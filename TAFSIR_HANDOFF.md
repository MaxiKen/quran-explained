# Tafsir handoff — how to pick this work up

Read this file first, then `TAFSIR_RULES.md` (the normative rule set, **v8**) and
`TAFSIR_PROMPT.md`. `TAFSIR_WORKLOG.md` is the progress ledger. Fifty verses are both the source-map
unit and the maximum independent-review checkpoint: write in order and mechanically check each verse,
while automatic drift alarms still run every fifty verses. **The author's standing order
(2026-10-01): at every stop, review your own range in a separate cold pass, post the statistics,
commit, push to the session branch, and carry straight on — never stop to ask whether to continue.**
The author reads GitHub afterwards and asks for a change if something is not right; silence is not an
approval and is never recorded as one. Independent acceptance still gates publication. Review covers
the complete source map, material omissions, Qur'an citations, every named transmitted report, and
language or consequential legal/theological claims—not only metrics. `QUALITY DRIFT` stops new
drafting: repair it, note it in the statistics, push the clean state, carry on.

## When the author says "continue" (start here)

**The call may come on any branch.** Nothing in the rules or tools assumes a branch name. Read the
actual repository state, stay on the branch assigned to the session, and push there. Never restore or
copy cleared commentary (Chapter 2's prose, its drafting bench, its reviews) from history: it was
cleared on 2026-10-01 and the book is written again from the sources.

**"Continue" means: pin the first unwritten verse and go.** If `run.py --plan` shows an existing pinned
run, resume its next unwritten verse. Otherwise run `python3 scripts/tafsir/run.py --plan` with no
`--start`: it pins the fifty verses from the first verse of the Book not yet written — **2:1** at the
moment. The author may re-aim the work at any time by naming a chapter or a chapter:verse
(`--start C:V`); otherwise the author's standing order is the start, and the writer does not ask. The
pin lives in git-ignored `tmp/runs/`, which a fresh checkout does not have, so a fresh session simply
re-plans from the frontier.

**What the 2026-10-01 clear removed — and what it kept.** Removed: `tafsir/002.md`; the tracked
drafting bench `tmp/work/c1_*.md` and `c2_*.md` (only the `dig.py` helper remains); every Chapter 2
review manifest under `quality/reviews/002/` (they embed excerpts of the prose and are fingerprinted to
it); and the owner's draft-continuation receipt `quality/draft-approvals/002/001-050.json` (the
approval of checkpoint `06ec1c6`, bound by fingerprint to prose that no longer exists). All of it stays
in git history; none of it is the standard and none of it may be restored or copied. **Kept — Chapter 1
was restored at the author's choice:** `tafsir/001.md`, its payload `data/tafsir_001.json` and its two
review records `quality/reviews/001/`, with the frozen Chapter-1 record
(`quality/chapter-001-baseline.json` and its approval). Also kept: the eleven source corpora,
`data/chapter_NNN.js`, the rules, prompt and scripts.

**Chapter 1 is the writing-style yardstick, and only that.** Through the frozen record it sets how the
prose *reads*: sentence length, the share of very long sentences, readability, and the
production-mould limits. It does **not** set how much content or evidence a verse carries — that
follows what the verse's own sources hold, under the floors and anchors of `audit.py` and the
reviewer's material-point ledger. Evidence density is measured and posted in the statistics, never an
alarm.

If ignored scratch has disappeared, there is no pin to restore: re-plan and rebuild from the frontier.

```bash
python3 scripts/tafsir/run.py --plan [--start C:V] # pin the next fifty (default: the first unwritten verse)
python3 scripts/tafsir/run.py --build --cap-json 0 # full eleven-source digest
python3 scripts/tafsir/run.py --slice C:V C:V     # a source-reading stretch of the pinned run
```

During a run, write in verse order and gate each verse with `batch.py ... --draft`. At every actual
generation stop (never more than fifty new drafts beyond the accepted/owner-approved frontier):

1. `quality.py --template N --from A --to B --writer arena-writing-agent` — the review scaffold;
2. **the independent review pass** — a separate, cold pass as reviewer `arena-review-agent`: compare
   every fingerprinted source passage with the prose, group duplicate works into distinct material
   points, account for omissions, complete the rubric and claim ledger, judge every Qur'an citation,
   and locate every named report or early authority in an allowlisted source. Work from the prose and
   the source passages only, never from the drafting notes; a score below 4 sends the verse back for
   revision; say in the manifest's `notes` that the pass was made by the same AI model under the
   standing order of 2026-10-01;
3. `batch.py N --from A --to B` — must report `QUALITY PARITY PASS`;
4. `stats.py N --from A --to B --write` — the statistics posted with the push;
5. commit (the headline statistics line in the message) and push to the session branch;
6. pin the next run (`run.py --plan`) and carry on.

If the review pass cannot be finished in the same sitting, run `batch.py ... --push-check`, commit and
push the pending candidate so nothing is left local, and finish the pass before any further new draft is
opened. `run.py --check` reaches RUN COMPLETE only when all fifty are mechanically clean and
independently accepted. Never record an approval in the owner's name that the owner did not supply.

Several chapters may be written at once by separate sessions: one chapter per session, each on its own
branch, each editing only its own chapter's files, review records and statistics. The worklog row and
this file change only when a chapter is finished. Chapter 1 must be intact for any chapter's gate.

Before any of that, two housekeeping steps:

1. **Read the rules first.** `TAFSIR_RULES.md` (**v8** — §0.9 the standing run order, §0.11 the
   register, §0.12 independence, §0.13 Chapter 1 as the writing-style yardstick) is normative;
   `TAFSIR_PROMPT.md` is the generation prompt built on it; this file is the working state;
   `TAFSIR_WORKLOG.md` is the ledger.
2. **Rebuild the scratch that is not in git.** `tmp/sources/` and `tmp/runs/` are ignored by design,
   so a fresh clone (and, in practice, a fresh session) has neither and the auditor reports
   `SRC-NODIGEST` on every verse until they are rebuilt. One pass does it:
   `python3 scripts/tafsir/run.py --build --cap-json 0` (the run's chapters, all eleven works, uncapped digests
   for the grounding check); a chapter outside the current run needs its own digest back —
   `python3 scripts/tafsir/sources.py 1`. **`SRC-NODIGEST` is a missing scratch file, never a defect
   in the prose.** The drafting bench `tmp/work/*.md` **is** tracked, so any part files from earlier
   sessions are present and must not be overwritten (after the 2026-10-01 clear only `dig.py`
   remains, so there are none).

State to expect on arrival (2026-10-01): Chapter 1 is written, published and frozen as the style
yardstick, and nothing else is written. `tafsir/` holds `001.md` and `.gitkeep`; `data/tafsir_001.json`
is the only payload; no run is pinned; `tmp/sources/` and `tmp/runs/` are absent, as in every fresh
checkout. Chapter 2 had reached 2:56 (23 verses accepted, 33 pending, 230 scaffolds) before it was
cleared; that state is recorded in `TAFSIR_WORKLOG.md` and is readable in git history, nothing more.

## Where things stand (2026-10-01)

| | |
|---|---|
| Repo | `MaxiKen/quran-explained`, latest writing branch `arena/01a0f50f-quran-explained` (the previous one was `arena/01a0e398-quran-explained`) |
| Written | **Chapter 1 only** — 7 verses, 8,747 words, published, the frozen writing-style yardstick. Chapter 2 (56/286 written before) was cleared on 2026-10-01. |
| Next | Under the standing order: pin the first unwritten verse, **2:1**, and go — no waiting between runs. |
| Standard | **v8 raised**: all v7.4 laws plus Chapter-1 *style* parity, all-source fingerprint/synthesis review, substantive-claim, Qur'an and transmitted-evidence ledgers, independent rubric (a separate review pass), maximum fifty-verse review candidates, fifty-verse automatic drift windows; every stop reviewed, posted and pushed — and the run goes on. |
| Sources | the **eleven** of `corpus.SOURCE_ALLOWLIST`: al-Ṭabarī, al-Qurṭubī, al-Baghawī, Ibn Kathīr, al-Ālūsī, al-Jalālayn, Ibn ʿAbbās, al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān **+ `tafsir_initial`** — research only, never named, relayed, compared or quoted |

Chapter 2's cleared prose, drafting bench and reviews are history, not material: do not restore or copy
any of it. The source corpora, `data/chapter_NNN.js` and the rules are unchanged, so a new run is
mapped and written exactly as before. `tafsir_initial` has no mapped passage at 2:38–2:39; this is an
upstream coverage gap, not a reason to use an outside source. Measured on the final tree:

```
python3 scripts/tafsir/quality.py --baseline         # pass: Chapter 1 matches the frozen record (style alarms only)
python3 scripts/tafsir/qualitytest.py                # all expectations hold
python3 scripts/tafsir/quality.py --all --push-check # no non-baseline commentary is written
python3 scripts/tafsir/audit.py 1                    # RESULT: PASS
python3 scripts/tafsir/build_data.py --all --check   # 1 up to date, 0 stale, 113 not written yet
python3 scripts/tafsir/run.py --status               # next verse to write: 2:1
```

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
  instructions qualify this: every semantic review covers at most fifty verses, at most fifty new
  drafts may follow accepted/owner-approved prose, and metric alarms still run every fifty verses.
  Any actual generation stop triggers an immediate review, statistics post, commit and push, and the run goes on without waiting for confirmation (the 2026-10-01 standing order, below).
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
* The author's standing order and the yardstick, 2026-10-01 (answers to the proposals in
  `TAFSIR_FAST_PATH.md`): "R1. should be AI write and post the statistics relating to others, also
  pushing the content to github. It doesn't even need to tell me if I want to continue. I'll go over
  it, if it's not okay, I'll ask for a change, if it is I may say nothing" · "R2 it's just one AI that
  can be accessed ooo. I hope you know that" · "Remove R3" · "I agree with R4" · "R5 I pick a." ·
  "It should be known that chapter 1 is go only be followed for its wiritter writing style and not
  the amount of content or evidences to be presented." — in force as §0.9 (the standing run order:
  review, post, push, carry on; no waiting; silence is not an approval), §0.13 (Chapter 1 is the
  writing-style yardstick only) and §11.14 (chapters may be written in parallel). There is one AI, so
  the review is a separate cold pass under `arena-review-agent`.
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
   cuts and pins the fifty from the verse the author named (when the instruction is only "continue",
   leave `--start` off: the standing order is the start — the first unwritten verse);
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
   open a fifty-first new draft beyond accepted/owner-approved prose; fifty-verse metrics remain early alarms.
5. **Expand every cross-reference with the tool, never by hand**:
   `python3 scripts/tafsir/reference.py 2:255` prints ready-made citations;
   `--scan N` lists every bare citation in a chapter with its replacement (`--write`
   applies them). A typed clause is where `REF-QUOTE` failures come from.
6. **At every generation stop: review, post, push, go on.** Create or refresh the quality review
   template for the written range (maximum fifty). Then make the independent review pass (a separate,
   cold pass as `arena-review-agent`): compare all fingerprinted source passages with the draft, record
   omissions, score every rubric dimension, verify every Qur'an citation, and give every named
   transmitted statement a matching fingerprinted allowlisted passage reference, excerpt and relevance
   decision. Run `batch.py` without either draft flag for `QUALITY PARITY PASS`, post the statistics
   with `stats.py ... --write`, commit and push to the session branch, and carry on with the next run —
   no waiting. Only if the pass cannot be finished in the sitting: `--push-check`, commit and push the
   pending candidate, and finish the pass first.
7. **Quality drift stops new drafting.** Repair it; note the trigger, blocked range and last accepted
   verse in the statistics; push the clean state; carry on. `run.py --check` completes only when all
   fifty have passed both gates. An owner draft approval, if the owner gives one, may authorize a run,
   but neither that approval nor a pending review authorizes publication.
8. **When a chapter is finished**: `audit.py N` and `quality.py N` must both pass, then run
   `status.py N`, `build_data.py N`, bump `sw.js` `CACHE_VERSION`, add the worklog row
   (`status.py --md`), and push the publication commit. Chapter completion is not a prerequisite for
   earlier review-candidate pushes.

Useful while writing:

```
python3 scripts/tafsir/run.py --status          # the fifty: words vs floors, failing verses
python3 scripts/tafsir/batch.py 2 --progress    # how far one chapter has come
python3 scripts/tafsir/quality.py --baseline    # verify the frozen Chapter-1 style yardstick
python3 scripts/tafsir/stats.py 2 --from A --to B --write   # the statistics posted with a push
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
python3 scripts/tafsir/run.py --plan [--start C:V] # re-pin the run (default: the first unwritten verse)
python3 scripts/tafsir/run.py --build --cap-json 0 # full passages, not a truncated research digest
```

The latest continuation branch is `arena/01a0f50f-quran-explained`. Push only to the branch
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
