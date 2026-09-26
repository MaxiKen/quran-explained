# Tafsir handoff — how to pick this work up

Read this file first, then `TAFSIR_RULES.md` (the normative rule set, **v7.4**) and
`TAFSIR_PROMPT.md`. `TAFSIR_WORKLOG.md` is the progress ledger. This file is the
working state: where the writing stands, how a run of fifty verses is produced and
gated, and the gate findings that cost time to learn the first time.

## When the author says "continue" (start here)

**The call may come on any branch.** Nothing in the rules, the tools or the working state is tied to
one branch: the corpus, the eleven sources, the scripts, the scaffold and the chapter-1 payload are
all in the repository, so read them from wherever you are checked out. Work on the branch the session
gave you and push there. PR #70 brought chapter 1 and v7.5 into `main`; the chapter-2 writing through
2:150 was carried on `arena/01a0dd66-quran-explained`.

**First act: ask where to start.** The author names the start of every run, and it is the one thing
you do not choose. If the instruction is only "continue", reply by asking whether the run should
begin at a chapter or at a chapter and verse, and **wait** — do not plan, map or write anything
first. A chapter alone (`2`) means that chapter's first unwritten verse; a chapter and verse (`2:1`)
means exactly that verse. When the answer comes, take it as the run's first verse:

```bash
python3 scripts/tafsir/run.py --plan --start 2:151 # pins the fifty: 2:151–2:200 (a chapter alone works too)
python3 scripts/tafsir/run.py --build              # all eleven works for the run, opened once
python3 scripts/tafsir/run.py --slice 2:151 2:155  # read the map a stretch at a time
```

Then write the fifty from that start — stretches gated with `batch.py N --from A --to B` as they land,
fixed as they fail — and do not stop until `python3 scripts/tafsir/run.py --check` prints **RUN
COMPLETE** (50/50 written and clean). Naming a different start later re-cuts the run from there;
naming the same one returns the pinned run in hand. A chapter that is already complete is a stop, not
a guess: report it and wait for the next start.

Before any of that, two housekeeping steps:

1. **Read the rules first.** `TAFSIR_RULES.md` (**v7.4** — §0.11 the register, §0.12 the independence
   law) is normative; `TAFSIR_PROMPT.md` is the generation prompt built on it; this file is the
   working state; `TAFSIR_WORKLOG.md` is the ledger.
2. **Rebuild the scratch that is not in git.** `tmp/sources/` and `tmp/runs/` are ignored by design,
   so a fresh clone (and, in practice, a fresh session) has neither and the auditor reports
   `SRC-NODIGEST` on every verse until they are rebuilt. One pass does it:
   `python3 scripts/tafsir/run.py --build` (the run's chapters, all eleven works, per-chapter digests
   for the grounding check); a chapter outside the current run needs its own digest back —
   `python3 scripts/tafsir/sources.py 1`. **`SRC-NODIGEST` is a missing scratch file, never a defect
   in the prose.** The drafting bench `tmp/work/*.md` **is** tracked, so part files from earlier
   sessions are present and must not be overwritten.

State to expect on arrival (2026-09-26): `audit.py 1` → `RESULT: PASS` (0 FAIL, 10 WARN, 3 INFO —
known and accepted); `build_data.py 1 --check` → `1 up to date`; `batch.py 2 --from 1 --to 150` →
0 FAIL, 178 WARN, PASS; `run.py --check` for the pinned 2:101–2:150 run → **RUN COMPLETE**. `audit.py 2`
still fails on the 136 scaffolds from 2:151 onward, as expected until 2:286 is written.

## Where things stand (2026-09-26)

| | |
|---|---|
| Repo | `MaxiKen/quran-explained`, latest writing branch `arena/01a0dd66-quran-explained` |
| Written | **chapter 1 complete and published**; **chapter 2 introduction + 2:1–2:150 written** (122,847 verse words, 703/805/1,427 min/median/max, 100% phrase coverage, 150/150 analogies). The growing-range gate has 0 FAIL and `run.py --check` reports RUN COMPLETE for 2:101–2:150. |
| Next | Chapter 2 remains a scaffold at 2:151–2:286. **The author names the next run's start**; if the answer is chapter 2, it now resolves to 2:151 and pins 2:151–2:200. Ask and wait when the instruction is only "continue". |
| Standard | **v7.4**: the eleven works read for every verse; every cross-reference expanded with its translation; no verse presented like the last; every paragraph past 120 words; the register of §0.11 (third person, no contractions, no exclamation mark, no hype) and the independence law of §0.12 (the book quotes no book — it cites the reference itself) |
| Sources | the **eleven** of `corpus.SOURCE_ALLOWLIST`: al-Ṭabarī, al-Qurṭubī, al-Baghawī, Ibn Kathīr, al-Ālūsī, al-Jalālayn, Ibn ʿAbbās, al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān **+ `tafsir_initial`** — research only, never named, relayed, compared or quoted |

Chapter 2 keeps byte-exact verse quotes throughout. The tracked drafting bench now holds
`tmp/work/c2_intro.md` and `c2_v001.md`–`c2_v150.md`; those files are the source of the assembled
prose and must not be overwritten. Measured state:

```
python3 scripts/tafsir/audit.py 1                   # chapter 1: PASS
python3 scripts/tafsir/build_data.py 1 --check      # the chapter-1 payload still matches
python3 scripts/tafsir/batch.py 2 --from 1 --to 150 # 0 FAIL, PASS
python3 scripts/tafsir/run.py --check               # RUN COMPLETE, 50/50 (2:101–2:150)
python3 scripts/tafsir/audit.py 2                   # fails on TODO 2:151–2:286 (expected)
```

Chapter 2 fails the chapter gate until all 286 verses are written. That is expected rather than a
regression: gate every new stretch against the growing range from verse 1 so cross-verse repeats are
caught, and run the whole chapter audit when the last verse lands.

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
  processing and writing but that 50 result must be completed before you pause or stop."
* The book is **the author's own unique and modern commentary, backed by evidence**.
  The eleven works are research: learn from them, then write the book's own reading —
  never relay, compare, summarise or quote them, and never cite a work outside the
  eleven.
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
4. **Write the section into a part file**, `tmp/work/cN_vVVV.md` (three digits keep them
   sorted), holding the body only — UPPERCASE headings and prose. Splice with
   `python3 scripts/tafsir/assemble.py N`; gate with `python3 scripts/tafsir/batch.py N
   --from A --to B`. Never edit `tafsir/NNN.md` by hand: it is generated from the
   scaffold plus the part files, and the next splice overwrites hand edits.
5. **Expand every cross-reference with the tool, never by hand**:
   `python3 scripts/tafsir/reference.py 2:255` prints ready-made citations;
   `--scan N` lists every bare citation in a chapter with its replacement (`--write`
   applies them). A typed clause is where `REF-QUOTE` failures come from.
6. **Work the findings** in the part file, re-splice, re-gate. When the stretch is clean,
   go straight on to the next stretch. Commit per stretch with
   `Tafsir ch N (<Name>): verses A-B`.
7. **The run is finished before pausing.** `python3 scripts/tafsir/run.py --check` must
   print RUN COMPLETE (all fifty written, no FAIL anywhere in them) before the writer
   stops for anything but a real blockage.
8. **When a chapter is finished**: `python3 scripts/tafsir/audit.py N` (whole file PASS),
   `python3 scripts/tafsir/status.py N`, `python3 scripts/tafsir/build_data.py N`,
   bump `sw.js` `CACHE_VERSION`, add the worklog row (`status.py --md`), commit and push.

Useful while writing:

```
python3 scripts/tafsir/run.py --status          # the fifty: words vs floors, failing verses
python3 scripts/tafsir/batch.py 2 --progress    # how far one chapter has come
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
* **`STY-ANALYSIS-FLOOR`** — at least 4 sentences per verse must reason about the verse
  (cure words: because, since, which means, which is why, that is why); 8 is the
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

The session opens with HEAD at an old commit and `tmp/` gone while the *files* still hold the
latest work. The branch is the source of truth.

```
git fetch origin refs/heads/arena/01a0da50-quran-explained:refs/remotes/origin/arena/01a0da50-quran-explained
git log --oneline -3 origin/arena/01a0da50-quran-explained
for f in tafsir/002.md TAFSIR_RULES.md scripts/tafsir/audit.py sw.js; do \
  a=$(git show origin/arena/01a0da50-quran-explained:$f | sha1sum); b=$(sha1sum $f); \
  [ "$a" = "$b" ] && echo "same $f" || echo "DIFF $f"; done
git reset --hard origin/arena/01a0da50-quran-explained
python3 scripts/tafsir/run.py --build            # rebuilds the digests and the run map
```

Hash-compare before resetting: if a file differs from the remote tip, it is newer work
and must be committed before the reset, not after. The verse drafts under `tmp/work/`
are tracked through a `.gitignore` exception, so they survive a wipe; the source
digests (`tmp/sources/…`) and the run maps (`tmp/runs/…`) do not, and `run.py --build`
rebuilds both in one pass.

Push policy: push to the session branch you were given and to no other — this work was carried on
`arena/01a0da50-quran-explained`, and a later session will have its own `arena/<id>-quran-explained`.
A single writer holds a branch, so `--force` is acceptable if a lease goes stale, but never push to
`main` from a session branch: `main` is brought up to date by merging the branch's pull request.

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
* The run map is capped: `--cap-en 2400`, `--cap-ar 700` per work per verse, and the
  per-chapter digest JSON is capped hard (1600/533) because grounding reads names, not
  length. Raise the caps for a verse that needs the full discussion.

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
