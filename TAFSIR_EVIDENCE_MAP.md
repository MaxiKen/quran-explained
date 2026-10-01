# Evidence first, commentary later — the two-phase approach

> **Status: a pilot, proposed by the author on 2026-10-01 and not yet adopted as a rule.** The
> author said he does not yet know whether it will work and asked to be heard out. This file records
> the idea, what was built to try it, what the pilot measured, and what would have to change if it is
> adopted. Nothing here alters `TAFSIR_RULES.md`; commentary writing is **paused** until the author's
> Phase 2 prompt (see `TAFSIR_HANDOFF.md`).

## 1. The idea, in the author's words

> "…you have opened all the sources for each of the verses and the content, the evidences that you
> can pick for each of the verses … and use them to generate head. So each verse is going to have
> head and under this head a summary of the evidences that you got. Presently we are not building the
> whole thing, but you are highlighting what is going to be built upon. This should be quick. Then
> later there is going to be a prompt to tell you that we go into each of the chapters and then start
> building up on the verses, and with this approach we are going to move out of generating content
> based on a fixed range of word lengths and focus on evidence based: all the evidences that you can
> pick up from the sources, which you itemize under the heads in each verse, is what it will be built
> upon, and evidences will now determine the length of each verse's commentary."

In one line: **Phase 1** writes, for every verse, the *heads* (the future headings) with a short
summary of the evidence under each, taken from all eleven works. **Phase 2**, later and chapter by
chapter on the author's prompt, builds the commentary from the map, and its length is whatever the
evidence needs — no fixed word range. The author also asked that Chapter 1's commentary be deleted;
it was (with the rest of the generated commentary), so no commentary exists in the tree.

## 2. What was built to try it

* **`evidence/NNN.md`** — one map per chapter. A `## Introduction` block (the sūrah-level evidence:
  where and why it came, its merit) and a `## Verse C:V` block per verse. Under each verse: the
  `**Sources with text:**` line, then `### HEADS` (UPPERCASE descriptive titles, unique in the
  chapter) and under each head numbered items:
  `` - `103:1.2` · athar · summary [tabari, qurtubi@2] ``. The *kind* is one of quran, hadith, athar,
  language, occasion, ruling, history, lesson; the bracket names the works that carry the point
  (`@V` = the passage sits under verse V).
* **`scripts/tafsir/evidencemap.py`** — `read` (a survey reader: each work's passage up to a cap, a
  table of contents for the rest, whole-sūrah passages shown once, `--para` to drill into a
  paragraph, `--find` to locate a verse inside a long passage) and `check` (validates a map).
* **`check` proves, mechanically:** the quoted line is the verse's own translation; the sources line
  matches what the digest holds; **every one of the eleven works is cited or explicitly marked
  "Nothing further from"** (so none can be silently skipped); every cited passage exists; item
  numbers run 1..n; heads are UPPERCASE and unique; every cross-reference is a real verse; a hadith
  without a named collection and an athar without a named authority are flagged. Summaries are held
  to a limit by *depth* (below). It does **not** prove an item is *true* — see §6.
* **Depth is declared** in the map's first comment. **Survey** (the quick pass): at most 12 items a
  verse (8 in the introduction), 35 words each, read from the capped passages and their tables of
  contents. **Full**: the passages read through, everything found listed (up to 60 words an item).

## 3. The pilot, measured

| | Chapter 103 (al-ʿAṣr) | Chapter 108 (al-Kawthar) |
|---|---|---|
| Depth | **full** — passages read almost through | **survey** — caps, tables of contents, about a dozen drill-downs |
| Distinct source text (11 works) | 49,712 chars | 109,411 chars |
| Items (heads) | 70 (27) — introduction 7, then 17 / 16 / 30 | 41 (16) — introduction 5, then 12 / 12 / 12 |
| Summary words | 2,937 | 1,219 |
| Per verse | ≈ 980 words | ≈ 406 words |
| Map size against the source it summarises | **40 %** | **8 %** |
| `check` | PASS — 0 errors, 4 warnings | PASS — 0 errors, 0 warnings |

The four warnings in 103 are real flags, not noise: four reports whose **collection the sources
themselves do not name** (103:1.6, 103:1.7, 103:2.12, 103:3.4). The map says so on each item; the
commentary may not use such a report with a collection it cannot show.

Reading it honestly: the verses of 103 came out with 17, 16 and 30 items and those of 108 hit the
survey cap of 12 on all three — length followed evidence, not a word target. And **full depth is not
quick**: a full-depth map is about 40 % of the size of its source, which scaled to the whole Qurʾān is
roughly 8 M words — longer than the commentary itself. At survey depth (8 %) the same scaling gives
about **1.6 M words**, about a quarter of the commentary volume under the old floors.

## 4. What the whole Qurʾān's material says about "evidence decides the length"

Distinct source text under each of the 6,236 verses (a whole-sūrah passage repeated under every verse
counted once; 127 M characters in all):

| | chars | | | share of verses below |
|---|---|---|---|---|
| poorest 10 % | 1,681 | | 3,000 chars | 16.5 % |
| 25th percentile | 4,759 | | 6,000 chars | 31.4 % |
| **median** | **11,359** | | 12,000 chars | 51.7 % |
| 75th percentile | 25,036 | | 25,000 chars | 75.0 % |
| richest 10 % | 48,025 | | 50,000 chars | 90.7 % |
| largest verse | 399,757 | | | |

The richest tenth of verses carries about **110 times** the material of the poorest tenth. Under the
present rule every verse must run at least 700 words (about 4,500 characters). For the third of verses
with under 6,000 characters of material the floor is longer than all the source text those verses
have: padding by necessity. Evidence-led length removes that, and gives the richest verses the room
their material needs.

## 5. Why it should work

* **The map is the review ledger, built first.** v8 already makes the reviewer list every distinct
  material point and mark it included or omitted. The map is that list, made before writing; the
  review in Phase 2 can be pre-filled from it. That is the biggest single cost measured for one AI
  (the hand-filled review is as much output as the prose).
* **Heads are planned for the whole chapter before any prose**, so the "no heading reused, no shared
  opening" rules (`STY-UNIQUE-VERSE`) are checked up front; the checker already caught two verses
  opening a head with the same two words.
* **The author can steer cheaply.** A chapter's map is minutes to read; its commentary is not.
* **Phase 2 need not re-read everything**: each item says which works and which passage carry it.
* **Nothing is skipped silently**: the all-eleven accounting is enforced per verse.

## 6. What it does not yet solve

* **Depth decides what Phase 2 can build.** A survey map holds highlights; items beyond the cap are
  not recorded. So Phase 2 must begin each chapter with a *deepening* pass — drill into the cited
  passages and the paragraphs the survey skipped, extend the map — and only then write.
* **Summaries lose nuance.** Items point to a work and a verse's passage, not yet to a paragraph;
  adding a paragraph pointer (the `--para` index) to each item would let Phase 2 jump straight to it.
* **A map can be wrong.** The checker proves traceability and completeness, not truth. The closed-world
  check (every named collection or authority really occurs in the cited passage) is not built; the
  Latin-script names in a summary do not match Arabic passages without a transliteration table.
* **One AI reads about 127 M characters** (≈ 40 M tokens) either way; the map does not reduce
  Phase 1 reading, only what Phase 2 must re-read.
* **Two rules will collide with evidence-led length** when Phase 2 starts: the 700-word verse floor
  (`WRD-FLOOR`, `TAFSIR_RULES.md` §4) and the 120-word paragraph floor (`WRD-PARA-FLOOR`). A verse with
  little evidence cannot honestly reach either. They are not changed now (the maps do not touch them).

## 7. What would change for Phase 2 (for the author to decide)

1. **Length from evidence.** Replace the word floors with a coverage rule: every item of the (deepened)
   map is built into the commentary, or struck from the map with a recorded reason; no padding; length
   is whatever that takes. The review ledger's included/omitted decisions already express this.
2. **The 120-word paragraph floor** — keep it (a paragraph combines several items) or drop it.
3. **The Chapter-1 style record.** `quality/chapter-001-baseline.json` still holds the style thresholds
   (mean sentence ≤ 23.0, readability ≥ 62) but Chapter 1 is deleted, so `quality.py --baseline` blocks
   until a chapter is built and frozen or the record is retired. Settle it when Phase 2 starts.
4. **Where reading depth goes.** Survey for every chapter now, deepen per chapter in Phase 2
   (recommended), or full depth throughout.

## 8. How to try it

```bash
python3 scripts/tafsir/sources.py N --cap-json 0            # the digest for chapter N (git-ignored scratch)
python3 scripts/tafsir/evidencemap.py read N V --cap-en 2000 --cap-ar 1000   # survey one verse
python3 scripts/tafsir/evidencemap.py read N V --find TEXT --only tabari      # locate a verse in a long passage
python3 scripts/tafsir/evidencemap.py read N V --para tabari:62,64            # read chosen paragraphs
python3 scripts/tafsir/evidencemap.py check N                                  # validate evidence/NNN.md
```

The pilot maps are `evidence/103.md` (full) and `evidence/108.md` (survey); reading them side by side
is the quickest way to judge the format and the depth.
