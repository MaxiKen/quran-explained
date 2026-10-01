# Evidence first, commentary later — the two-phase approach

> **Status: a pilot, proposed by the author on 2026-10-01; the depth is chosen, the rest is not yet a
> rule.** The author read the two pilot maps and chose the **103 style (full depth)**, adding that he
> expects it to carry *more evidence than the first 103 map held*. `evidence/103.md` was rebuilt to that
> (§3) and awaits his word on the new density and its cost (§3, §7). Nothing here alters
> `TAFSIR_RULES.md`; commentary writing is **paused** until the author's Phase 2 prompt (see
> `TAFSIR_HANDOFF.md`).

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
  `**Sources with text:**` line, optionally `**Nothing further from:**` and `**Set aside:**` lines, then
  `### HEADS` (UPPERCASE descriptive titles, unique in the chapter) and under each head numbered items:
  `` - `103:1.7` · athar · summary [tabari¶5, qurtubi¶10, baghawi¶3] ``. The *kind* is one of quran,
  hadith, athar, language, occasion, ruling, history, lesson; the bracket names the works **and the
  paragraphs** that carry the point (`work¶3-5`, `work¶3+7`; `work@2¶4` = paragraph 4 of the passage
  under verse 2).
* **`scripts/tafsir/evidencemap.py`** — `read` (each work's passage with its paragraphs numbered from 1;
  `--full` prints every paragraph; without it a passage is cut at a cap and the rest listed in a table of
  contents; whole-sūrah passages shown once; `--para` and `--find` to drill and to locate) and `check`
  (validates a map; `--gaps` lists the paragraphs not yet accounted for).
* **`check` proves, mechanically:** the quoted line is the verse's own translation; the sources line
  matches what the digest holds; every one of the eleven works is cited or marked "Nothing further
  from" under each verse; every cited passage **and paragraph** exists; item numbers run 1..n; heads
  are UPPERCASE and unique and do not fall into a template; every cross-reference is a real verse; a
  hadith without a named collection and an athar without a named authority are flagged.
  **In a full map, every citation names paragraphs, and once the last verse is mapped every paragraph of
  every work's passage — a passage repeated under several verses counts once — is either cited by an
  item or listed on a `Set aside` line with its reason.** Headings and separators (under 20 letters) are
  exempt; a map that sets aside more than 20 % of the source text is warned. The check prints, per work,
  the paragraphs cited, set aside and missing. It does **not** prove an item is *true* — see §6.
* **Depth is declared** in the map's first comment. **Full** — the author's choice (2026-10-01): one item
  for each distinct claim (up to 100 words, split rather than squeeze), every paragraph accounted for.
  **Survey**, kept for quick looks: at most 12 items a verse (8 in the introduction), 35 words each; the
  checker warns that a survey map is not the chosen depth.

## 3. The pilot, measured

| | 103, first map | **103, rebuilt** | 108, survey |
|---|---|---|---|
| Depth | full, no pointers | **full, pointers, paragraph rule** | survey |
| Distinct source text (11 works) | 49,712 chars | 49,712 chars (148 real paragraphs) | 109,411 chars |
| Items (heads) | 70 (27) | **160 (33)** — introduction 17, then 48 / 31 / 64 | 41 (16) |
| Summary words | 2,937 | **6,080** | 1,219 |
| Items that point at paragraphs | 0 of 70 | **160 of 160** | optional |
| Paragraphs cited / set aside / missing | not measurable | **133 / 15 / 0** | not measured |
| Source text set aside | — | **2.9 %** (headings, greetings, quoted copies) | — |
| `check` | PASS, 4 warnings | **PASS, 0 errors, 5 warnings** | PASS, 1 warning (survey depth) |

*What the rebuild added.* The first map held most claims, squeezed: several scholars' views to one line,
no chain, no poem, no objection. The rebuild splits them (items citing Ṭabarī 7 → 15, Qurṭubī 23 → 35,
Baghawī 11 → 17, Alūsī 26 → 41, Ibn ʿUthaymīn 21 → 33, Maʿārif 11 → 18, the study draft 6 → 14; athar
items 9 → 31) and adds what was absent — Ādam's creation on a Friday as a reason for the oath, the oath by
al-ḍuḥā as a comparison, the oath being by one of two things unspecified, the
spearhead-and-blossom answer to "it came late", al-Māturīdī's note on the Muʿtazilah argument, Ṭabarī's
chain details, the Jarīr line. It also corrected one thing: the first map expanded the study draft's
initial "R" to al-Rāzī with nothing in the sources to say so; the rebuilt map keeps the initials as the
draft writes them (the repository holds no key to them).

*The five warnings are real flags*: reports attributed to the Prophet whose **collection the sources
themselves do not name** (103:1.19, 1.20, 1.24, 2.22, 3.8). The map says so on each item; the commentary
may not use such a report with a collection it cannot show.

*What it costs.* At the rebuilt density the map is about 124 words per 1,000 characters of source — 41
words and 1.08 items per real paragraph. Scaled to the Qurʾān (125 M characters, 342,338 real paragraphs of
410,270): about **14–15 M words and ≈ 370,000 items** — twice the 7.4 M words of the first density, and
about twice the commentary under the old floors. The rebuild took about 17 minutes of sandbox clock, tool
changes included; at that rate the Qurʾān is of the order of **500–700 one-AI hours** (3–4 weeks
non-stop). Sessions can run in parallel, one per chapter, but Chapter 2 alone (13 % of the corpus, 54,361
paragraphs) is about 100 hours and, with one writer to a chapter (§0.9 R2), cannot be split — so four to
five days is the best case however many sessions run. These are rough figures from one short chapter. So **full depth is not quick** — it is complete — and a leaner density (shorter items,
the same paragraph rule) is a dial the author can turn.

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
* **Phase 2 need not re-read everything**: each item says which works and which paragraphs carry it, so the writer opens exactly those.
* **Nothing is skipped silently**: the all-eleven accounting is enforced per verse, and in a full map every paragraph is cited or set aside with a reason.

## 6. What it does not yet solve

* **Completeness is per paragraph, not per point.** A long paragraph can hold several points; the check
  proves no paragraph was passed over, not that every point inside one was itemised. In 103 the long
  paragraphs were audited by hand against the items; that audit is the writer's, not the machine's.
* **A map can be wrong.** The checker proves traceability and completeness of coverage, not truth. The
  closed-world check (every named collection or authority really occurs in the cited paragraph) is not
  built; the Latin-script names in a summary do not match Arabic passages without a transliteration table.
  The pointer is what lets a reviewer open the paragraph and check.
* **One AI reads about 125 M characters** (≈ 40 M tokens) and writes the map either way; the map does not
  reduce Phase 1 reading, only what Phase 2 must re-read (§3 gives the cost).
* **Two rules will collide with evidence-led length** when Phase 2 starts: the 700-word verse floor
  (`WRD-FLOOR`, `TAFSIR_RULES.md` §4) and the 120-word paragraph floor (`WRD-PARA-FLOOR`). A verse with
  little evidence cannot honestly reach either. They are not changed now (the maps do not touch them).
* **`evidence/108.md` is still a survey map** and does not meet the chosen depth; it is rebuilt at full
  depth in its turn (the checker warns until then).

## 7. What would change for Phase 2 (for the author to decide)

1. **Length from evidence.** Replace the word floors with a coverage rule: every item of the map is built
   into the commentary, or struck from the map with a recorded reason; no padding; length is whatever that
   takes. The review ledger's included/omitted decisions already express this.
2. **The 120-word paragraph floor** — keep it (a paragraph combines several items) or drop it.
3. **The Chapter-1 style record.** `quality/chapter-001-baseline.json` still holds the style thresholds
   (mean sentence ≤ 23.0, readability ≥ 62) but Chapter 1 is deleted, so `quality.py --baseline` blocks
   until a chapter is built and frozen or the record is retired. Settle it when Phase 2 starts.
4. **Density.** *Decided:* full depth (2026-10-01). *Open:* how dense — the rebuilt 103 (§3), or leaner.

## 8. How to try it

```bash
python3 scripts/tafsir/sources.py N --cap-json 0                  # the digest for chapter N (git-ignored scratch)
python3 scripts/tafsir/evidencemap.py read N V --full             # every paragraph of every work, numbered
python3 scripts/tafsir/evidencemap.py read N V --find TEXT --only tabari     # locate a verse in a long passage
python3 scripts/tafsir/evidencemap.py read N V --para tabari:62,64           # read chosen paragraphs (from 1)
python3 scripts/tafsir/evidencemap.py check N                     # validate evidence/NNN.md (--gaps lists what is unaccounted)
```

`evidence/103.md` is the full-depth map to judge by; `evidence/108.md` is the survey sample it replaces as
the standard.
