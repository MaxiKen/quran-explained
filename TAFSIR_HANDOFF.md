# Tafsir handoff — how to pick this work up

Read this file first, then `TAFSIR_RULES.md` (the normative rule set, **v7.1**) and
`TAFSIR_PROMPT.md`. `TAFSIR_WORKLOG.md` is the progress ledger. This file is the
working state: where the writing stands, how a stretch is produced and gated, and the
gate findings that cost time to learn the first time.

## Where things stand (2026-09-25)

| | |
|---|---|
| Repo | `MaxiKen/quran-explained`, branch `arena/01a0d3cf-quran-explained` |
| Chapter 1 | **closed and frozen** — `tafsir/001.md`, 7 verses, 4,339 words, `audit.py 1` → 0 FAIL / 0 WARN / 1 INFO, payload `data/tafsir_001.json`. Do not edit it. |
| Chapter 2 | **in progress** — `tafsir/002.md`, 13 of 286 verses written and gated (2:1–2:13, 9,561 words), payload not built yet (`build_data.py` refuses a chapter that still has TODO scaffolds) |
| Next stretch | **2:14–2:19 are already drafted** (see below) — they are written, injected, and awaiting the punch list |
| Standard | v7.1: own unique modern commentary, every paragraph past 120 words, no verse presented in another verse's shape or diction |
| Sources | the ten of `corpus.SOURCE_ALLOWLIST` as research only: al-Ṭabarī, al-Qurṭubī, al-Baghawī, Ibn Kathīr, al-Ālūsī, al-Jalālayn, Ibn ʿAbbās, al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān |

Gate for the committed stretch, as left:

```
python3 scripts/tafsir/batch.py 2 --from 1 --to 13     # 0 FAIL, 0 WARN — RESULT: PASS
python3 scripts/tafsir/audit.py 1                      # 0 FAIL, 0 WARN, RESULT: PASS
```

### The drafts waiting next: 2:14–2:19

The prose for these six verses lives in `tmp/work/c2_v14.md` … `c2_v19.md` and is
**not** in `tafsir/002.md` (the chapter file stands at the last passing stretch).
To resume:

```
python3 tmp/work/splice2.py 14 15 16 17 18 19
python3 scripts/tafsir/batch.py 2 --from 14 --to 19
```

That run reports **12 FAIL / 7 WARN**; the full punch list, with the cure for each
item, is in **`tmp/work/gate_2_14-19.txt`**. Nothing in those drafts is a lost cause:
the headings, the paragraph floors, the analogies and the present-day lines are
already right, and most of the failures are two mechanical habits the gate catches
(a sentence claiming the verse "says" a word the translation does not carry, and a
phrase left unquoted where it is explained).

## The law this book is written to

The author's instructions, verbatim, in force:

* "There shouldn't be a standard diction use or phrased introduction/presentation used
  across verses. Each verse content should be uniquely presented not following a
  standard presentation or arrangement for other verses. And there's no rule that
  states there should be one paragraph content per heading, you can have more than
  one, just that each paragraph must must contain more than 120 words."
* The book is **the author's own unique and modern commentary, backed by evidence**.
  The ten works are research: learn from them, then write the book's own reading —
  never relay, compare, summarise or quote them, and never cite a work outside the ten.
* Their authenticated contents are taken as they stand: **no fact-checking** is
  required or wanted.
* **Each paragraph must be greater than 120 words** (`WRD-PARA-FLOOR`). A heading may
  carry one paragraph or several.
* Every verse section quotes each phrase of the verse in **bold italics** and explains
  it; the commentary's own voice carries no emphasis.

`scripts/tafsir/audit.py` mechanises all of it. `scripts/tafsir/ruletest.py` proves the
v7/v7.1 checks and `scripts/tafsir/selftest.py` mutates chapter 1 to prove the older
ones; run both after touching the auditor.

## The gait for one stretch (~15–20 verses)

1. **Read the sources for the verse.** They live in `tmp/sources/002.json` / `.txt`
   (not tracked — rebuild with `python3 scripts/tafsir/sources.py 2`, a few minutes,
   286/286 verses covered). Early-verse windows open with sūrah-level material; don't
   mine the openers as if they were the verse.
2. **Write the section into a part file**, `tmp/work/c2_vNN.md`, with placeholders:
   `{{P:v:i}}` for this verse's own phrase *i* (0-based, from
   `C.split_phrases(C.ayah_en(2, v))`) and `{{X:c:v:clause}}` for a clause of another
   verse. Phrases and clauses are injected byte-exact, so nothing can drift:
   ```
   python3 tmp/work/inject.py tmp/work/c2_v14.md tmp/work/c2_v15.md …
   ```
   A missing `--` clause or a non-verbatim clause is reported and left alone.
3. **Splice into the chapter** and **gate the stretch**:
   ```
   python3 tmp/work/splice2.py --intro          # introduction + every part file present
   python3 scripts/tafsir/batch.py 2 --from 14 --to 19
   ```
4. **Work the findings** in the part file, re-inject, re-splice, re-gate. Never edit
   `tafsir/002.md` directly: it is generated from the part files, and the next splice
   would overwrite the edit.
5. When the stretch is clean (0 FAIL; aim 0 WARN too), **commit the chapter file** with
   a subject in the house style:
   `Tafsir ch 2 (Al-Baqarah): 2:14–19 written — <phrase>`.
6. When the whole chapter is written: `python3 scripts/tafsir/build_data.py 2`,
   `python3 scripts/tafsir/status.py --all --check`, bump `CACHE_VERSION` in `sw.js`,
   add the worklog row, and commit the payload.

Useful while writing:

```
python3 scripts/tafsir/status.py --all          # per-chapter gate + word numbers
python3 scripts/tafsir/sources.py 2 --verse 14  # one verse's digest to the terminal
python3 tmp/work/extract_parts.py               # rebuild the bench from tafsir/002.md
```

## Gate findings learned while writing 2:1–2:19

Each of these is a real failure the gate raised; the cure is the one that worked.

* **`MTCH-TERM` / `AS_VERSE_TERM`** — a sentence saying "the verse says/names/…
  *word*" fails when the translation does not carry that word (the pattern's false
  friends are ordinary words: *the, that, they, already, done, been, from, the verse
  names*). Cure: make it passive, drop the subject, or rephrase plainly. Arabic terms
  that are *not* name-exempt and do fire it: Allāh, Shayṭān, taqwā, falāḥ, ṣalāh,
  zakāh. Safe (exempt): God, Gabriel, the devil, hadith collections, early
  authorities, "unseen", "prayer", "success", "certainty".
* **`MTCH-WORD`** — the prose must not explain wording the verse's translation does
  not carry; the flagged word is usually the head of a "the word/term/root …" study
  sentence (*covers, easier, behind, formed, the, since, runs, cannot*). Cure: rephrase
  so the flagged word is not in explaining position, or drop the study frame.
* **`PHR-EVIDENCE`** — every quoted phrase needs an anchor in its own paragraph or the
  next one: a cross-reference `(C:V — **“clause”**)`, a report with its collection, a
  named early authority, or a language point. `BARE_REF` matches only a bare `(C:V)`,
  not the one inside a cross-reference.
* **`PHR-PHRASE-MISSING` / `-EDGE` / `-GAP` / `-COVERAGE`** — quote *every* phrase,
  in verse order, ≥90% coverage, no gap over 8 words. A long verse's middle phrase is
  the one usually forgotten.
* **`REF-QUOTE`** — a cited clause must be byte-exact; copy it out of
  `C.ayah_en(c, v)` rather than typing it (em dashes and `˹…˺` brackets are where it
  breaks). `REF-QUOTE-REPEAT` warns on citing the same verse twice in one section.
* **`STY-ANALYSIS-FLOOR`** — at least 4 sentences per verse must reason about the
  verse (cure words: because, since, which means, which is why, that is why); 8 is the
  comfortable target. Adding a sentence can trip `MTCH-WORD`, so re-gate after every
  addition.
* **`STY-ANALOGY`** — one relatable comparison per verse, woven in (*picture, imagine,
  it is like, the way a*), never labelled. **`STY-APPLICATION`** — at least one line
  reaching the reader's own world (*today, these days, this week*), unwritten as a
  heading or label.
* **`EVD-THIN`** — a verse needs two kinds of anchor among quran/hadith/scholar/
  language. A name alone is not a collection; the scholar kind is satisfied by
  Ibn ʿAbbās, Mujāhid, Qatādah, Ibn Masʿūd, al-Ṭabarī, al-Qurṭubī and the rest of
  `SCHOLARS`.
* **`STY-UNIQUE-VERSE` (v7.1)** — the free prose of two verses may not share a 4-word
  opening (2 WARN / 3 FAIL), six unquoted words in a row (WARN / FAIL), a heading, or
  a two-word heading prefix. The habitual offenders read like one author's tics:
  *"Ibn ʿAbbās is reported to have"*, *"is reported to have said that"*,
  *"in it, which is why the"*, *"the test costs him nothing"*, *"are both named among
  those who"*. Cure: write the sentence a different way rather than synonym-swapping.
* **`GRD-TOKENS`** — distinctive names should appear in that verse's source digest;
  quoted matter and the first word of a paragraph are ignored. Cure: drop the name or
  cite a clause that passes.
* **`MTCH-BOLD` / `PHR-QUOTE-FOREIGN` / `EVD-QUOTE-STYLE`** — bold is reserved for the
  UPPERCASE headings, this verse's phrases (`***“…”***`) and other verses' clauses
  inside their reference (`**“…”**`); reports and authority quotes are
  `*"…"*` in straight quotes, and Qur'anic wording is never straight-quoted.
* **`WRD-PARA-FLOOR`** — every paragraph, in the introduction too, must run past 120
  words. The introduction itself is 250–1,500 words with no headings.
* **`SRC-BANNED`** — never cite al-Wāḥidī or al-Kalbī (or any work outside the ten).

## If the sandbox wipes the scratch directory

This has happened repeatedly: the session opens with HEAD at an old commit and `tmp/`
gone, while the *files* still hold the latest work. The branch is the source of truth.

```
git fetch origin refs/heads/arena/01a0d3cf-quran-explained:refs/remotes/origin/arena/01a0d3cf-quran-explained
git log --oneline -3 origin/arena/01a0d3cf-quran-explained
for f in tafsir/002.md TAFSIR_RULES.md scripts/tafsir/audit.py sw.js; do \
  a=$(git show origin/arena/01a0d3cf-quran-explained:$f | sha1sum); b=$(sha1sum $f); \
  [ "$a" = "$b" ] && echo "same $f" || echo "DIFF $f"; done
git reset --hard origin/arena/01a0d3cf-quran-explained
python3 scripts/tafsir/sources.py 2          # and 1, for chapter 1's digest
```

Hash-compare before resetting: if a file differs from the remote tip, it is newer work
and must be committed before the reset, not after. Since 2026-09-25 the drafting bench
(`tmp/work/*.md`, `*.py`, `*.txt`) is tracked through a `.gitignore` exception, so part
files and helpers survive a wipe; the source digests (`tmp/sources/…`) do not, and are
rebuilt by `sources.py`.

Push policy for this branch: `git push origin arena/01a0d3cf-quran-explained`
(a single writer, so `--force` is acceptable if a lease goes stale).

## House facts worth not rediscovering

* `audit.py --json` is broken; use the text runs. `audit_chapter(chapter, opts, path=None)`
  wants an argparse Namespace; there is no `--file` flag. `audit.py N` on a chapter with
  scaffolding fails by design (`TODO`) — gate a stretch with `batch.py N --from A --to B`.
* Intros are `## Introduction to the Sūrah`, plain paragraphs, no `**` inside.
* A verse section is: `## Verse 2:N`, a blank line, the `> verse line` exactly as the
  scaffold holds it, a blank line, the body, a blank line, `---`.
* Rebuild the payload after *any* prose edit: `build_data.py` compares the chapter file
  with `data/tafsir_NNN.json` and reports stale payloads.
* Prefer short sentences: the gate wants a mean under 26 words (fail 32), under 12%
  above 40 words, Flesch 62+.
