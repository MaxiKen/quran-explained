# Tafsir handoff — how to pick this work up

Read this file first, then `TAFSIR_RULES.md` (the normative rule set, **v8**) and
`TAFSIR_PROMPT.md`. `TAFSIR_WORKLOG.md` is the progress ledger.

**Commentary writing is paused (2026-10-01).** The author is trying a two-phase approach: an
*evidence map* for every verse first (heads, with a short summary of the evidence the eleven works carry
under each), commentary built from the maps later, chapter by chapter, **on his prompt**, its length
decided by the evidence rather than a fixed word range (`TAFSIR_EVIDENCE_MAP.md`). All generated
commentary, Chapter 1's included, was cleared. **No commentary exists, and none is to be written until the
author gives the Phase 2 prompt** — so a bare “continue” does *not* start commentary at 1:1.

The rest of this file is the procedure for commentary, kept for when it resumes. Its standing order
(2026-10-01): at every stop, review your own range in a separate cold pass, post the statistics, commit,
push to the session branch, and carry straight on — never stop to ask whether to continue; the author reads
GitHub afterwards and asks for a change if something is not right; silence is not an approval and is never
recorded as one. Independent acceptance still gates publication.

## When the author says "continue" (start here)

**The call may come on any branch.** Nothing in the rules or tools assumes a branch name. Read the actual
repository state, stay on the branch assigned to the session, and push there. Never restore or copy cleared
commentary from history: it was cleared on 2026-10-01 and the book is written again from the sources.

**Now, “continue” means Phase 1 — the evidence maps — once the author has accepted the pilot.** The pilot
maps are `evidence/103.md` (full depth) and `evidence/108.md` (survey depth). If the author's words show he
has not yet judged them, say the pilot awaits his verdict; do not start commentary and do not map further
chapters at scale. Once he has accepted the format, “continue” means: map the next chapters in order from the
first chapter that has no map, at the depth he named (**survey** unless told otherwise), one
`evidence/NNN.md` per chapter:

```bash
python3 scripts/tafsir/sources.py N --cap-json 0                       # the chapter's digest (git-ignored scratch)
python3 scripts/tafsir/evidencemap.py read N V --cap-en 2000 --cap-ar 1000   # survey a verse, all eleven works
python3 scripts/tafsir/evidencemap.py read N V --find TEXT --only tabari     # locate a verse in a long passage
python3 scripts/tafsir/evidencemap.py read N V --para tabari:62,64           # drill into paragraphs
python3 scripts/tafsir/evidencemap.py check N                                # must say PASS (0 errors)
```

Write a head per theme and under it the evidence found, each item naming the works that carry it; account for
all eleven works under every verse (cite each, or list it under "Nothing further from" — and only if it was
really read); take attributions only from what the passages themselves say, and say so where a hadith's
collection is not named. Commit and push each finished chapter. Several chapters may be mapped at once by
separate sessions (one file per chapter). Phase 2 — building commentary from a map, beginning with a
deepening pass — starts only on the author's prompt.

**What the 2026-10-01 clear removed.** `tafsir/001.md` and `tafsir/002.md`; the payload
`data/tafsir_001.json` (no `data/tafsir_NNN.json` exists now); the tracked drafting bench `tmp/work/c1_*.md`
and `c2_*.md` (only the `dig.py` helper remains); every review manifest under `quality/reviews/` (they embed
excerpts of the prose and are fingerprinted to it); and the owner's draft-continuation receipt
`quality/draft-approvals/002/001-050.json` (bound by fingerprint to prose that no longer exists). `sw.js`
(v2.5.51) retires `./data/tafsir_001.json` and `./data/tafsir_002.json` so devices drop a cached copy. All of
it stays in git history; none of it is the standard and none of it may be restored or copied. (Chapter 1 was
restored once, at the author's choice, and deleted again when he began the two-phase pilot.) **Kept:** the
eleven source corpora, `data/chapter_NNN.js`, the rules, prompt and scripts, and the Chapter-1 style record
(`quality/chapter-001-baseline.json` with its approval).

**The style record now points at nothing.** With `tafsir/001.md` gone, `quality.py --baseline` blocks with
`QTY-BASELINE-CHANGED`, `qualitytest.py` stops with `FileNotFoundError`, and the “Tafsir quality parity”
workflow fails at its baseline step. Pushes that touch only `evidence/` do not trigger that workflow. The way
out is the author's call, for when Phase 2 starts: build a chapter, have it independently reviewed and
re-freeze the record with `quality.py --freeze-baseline --approval FILE` (thresholds can only tighten); or
retire the record (the next freeze is then a first installation with no approval and no inherited
thresholds). Do neither without the author's word. Chapter 1, when it exists, is the **writing-style**
yardstick only — never a measure of how much content or evidence a verse carries.

**When commentary resumes** (not before the author's prompt). If `run.py --plan` shows a pinned run, resume
its next unwritten verse; otherwise `python3 scripts/tafsir/run.py --plan` with no `--start` pins the fifty
verses from the first verse not yet written — **1:1** at the moment. The pin lives in git-ignored
`tmp/runs/`, so a fresh session simply re-plans from the frontier.

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
this file change only when a chapter is finished. A chapter's gate needs the Chapter-1 style record to
validate (see above).

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
   `python3 scripts/tafsir/sources.py 1 --cap-json 0`. **`SRC-NODIGEST` is a missing scratch file, never a
   defect in the prose.** The drafting bench `tmp/work/*.md` **is** tracked, so any part files from earlier
   sessions are present and must not be overwritten (after the 2026-10-01 clear only `dig.py`
   remains, so there are none).

State to expect on arrival (2026-10-01): no commentary is written and no payload is published. `tafsir/`
holds only `.gitkeep`; `evidence/` holds the two pilot maps; no run is pinned; `tmp/sources/` and `tmp/runs/`
are absent, as in every fresh checkout. Before the clear, Chapter 1 was published and frozen as the style
yardstick and Chapter 2 had reached 2:56 (23 verses accepted, 33 pending, 230 scaffolds); that state is
recorded in `TAFSIR_WORKLOG.md` and is readable in git history, nothing more.

## Where things stand (2026-10-01)

| | |
|---|---|
| Repo | `MaxiKen/quran-explained`, latest writing branch `arena/01a0f50f-quran-explained` (the previous one was `arena/01a0e398-quran-explained`) |
| Commentary | **None written; writing paused** until the author's Phase 2 prompt. All generated commentary was cleared on 2026-10-01. |
| Evidence maps | **Pilot:** `evidence/103.md` (full depth, 70 items) and `evidence/108.md` (survey depth, 41 items); both pass `evidencemap.py check`. Awaiting the author's verdict on the format and depth. |
| Next | The author judges the pilot; then Phase 1 across the chapters (survey depth), then Phase 2 on his prompt. |
| Standard | **v8 raised** for commentary, unchanged and not applied while it is paused; narrowed on 2026-10-01 so Chapter 1 is a writing-style yardstick only. |
| Sources | the **eleven** of `corpus.SOURCE_ALLOWLIST`: al-Ṭabarī, al-Qurṭubī, al-Baghawī, Ibn Kathīr, al-Ālūsī, al-Jalālayn, Ibn ʿAbbās, al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān **+ `tafsir_initial`** — research only, never named in the book, relayed, compared or quoted |

Chapter 2's cleared prose, drafting bench and reviews are history, not material: do not restore or copy
any of it. The source corpora, `data/chapter_NNN.js` and the rules are unchanged. `tafsir_initial` has no
mapped passage at 2:38–2:39; this is an upstream coverage gap, not a reason to use an outside source.
Measured on the final tree:

```
python3 scripts/tafsir/evidencemap.py check --all    # 103 PASS (4 warnings: reports with no collection named); 108 PASS
python3 scripts/tafsir/audit.py --all                # 0/114 chapters written
python3 scripts/tafsir/build_data.py --all --check   # 0 up to date, 0 stale, 114 not written yet
python3 scripts/tafsir/quality.py --all --push-check # no non-baseline commentary is written
python3 scripts/tafsir/quality.py --baseline         # BLOCK QTY-BASELINE-CHANGED (expected: Chapter 1 is deleted)
python3 scripts/tafsir/qualitytest.py                # FileNotFoundError: needs the real tafsir/001.md (expected)
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
* The author's new approach and his instruction to clear Chapter 1, 2026-10-01: "I'm thinking of a new
  approach which I presently do not know if it is going to work just hear me out." · "You'll have to delete
  chapter 1 commentary also." · "…you have opened all the sources for each of the verses and the content the
  evidences that you can pick for each of the verses you have them and use them to generate head. So each
  verses are going to have head and under this head are going to be a summary of the evidences that you got
  so presently we are not building the whole thing, but you are highlighting what is going to be built upon.
  This should be quick. Then after later on there is going to be a prompt to tell you that we go into each of
  the chapters and then start building up on the verses and with this approach, I believe that we are going
  to move out of generating content based on a fixed range of words lengths and focus on evidence based one
  which is going to be that all the evidences that you can pick up from the sources which you itemize under
  the heads in each verses is going to be what it will be built upon. and evidences will now determine the
  length of each was commentary." — recorded in `TAFSIR_EVIDENCE_MAP.md`; a pilot, not yet a rule.
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
