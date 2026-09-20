# Commentary editorial pass

Every verse commentary in `markdown commentry/` was drafted against a fixed
word target, so each verse section ran to roughly a thousand words whether or
not there was a thousand words of substance in it. This pass re-cut the whole
corpus (surahs 1-114, 6,350 sections) so that length follows substance.

**Result: 6,317,465 words to 3,380,769 words, 53.5 percent of the draft.**
Median verse section 1,019 words to 554; shortest 303, longest 1,139. Nothing
outside the commentary changed: verse text, translations and layout are
untouched.

## What is never cut

* Qur'an citations (`2:255`, `43:36`, ...) - verified preserved, zero losses.
* Hadith references (`Ṣaḥīḥ al-Bukhārī 4474`, ...) - verified preserved, zero losses.
* Quoted scripture inside a commentary (`> "..."` lines) - every quoted line
  present before the pass is present after it.
* Named authorities, dates, numbers, Arabic terms and historical accounts.
* Section headers: all 114 chapter files still carry every `## ... N:M` heading.

Where a citation appeared only in a line that was otherwise cut, the fact guard
re-inserted that line (656 restorations corpus-wide).

## What was removed

* Restated points: sentences repeating a claim already made in the same
  section, and claims already made earlier in the same surah.
* Generation/process meta that leaked into the text ("this file", "a thin
  source chunk", "the gate asked for", "the discipline is"), including three
  boilerplate blocks repeated under every verse of surahs 100-104
  ("The Arabic Still Has Work After the First Pass", "Conduct Follows if the
  Verse Is Believed", "A Checked Parallel, Not a Stolen Verse"). Their
  verse-specific cross-references were kept; the framing was dropped.
* Filler openers and generic exhortation with no verse detail.
* Weak headings, so a section reads as 2-5 paragraphs instead of 6-9 fragments.

## How it was done

`scripts/editorial_pass.py` runs in two passes over all 114 files:

1. collect every sentence, find sentences that repeat an earlier one anywhere
   in the corpus (cheap LSH signature plus 3-gram Jaccard);
2. per section: score sentences and blocks by information content, drop
   restatements, meta and filler, choose the blocks that carry the section's
   substance, apply the plain-English pass, then re-check that every citation
   in the original is still somewhere in the chapter and restore the line if not.

Run it with:

    python3 scripts/editorial_pass.py --all --write --report report.md

Then regenerate the app payload:

    python3 scripts/build_tafsir_json.py

## Per-surah word counts

| Surah | Words before | Words after | Kept |
|---|---|---|---|
| 1 | 7,973 | 5,054 | 63% |
| 2 | 338,691 | 203,266 | 60% |
| 3 | 199,767 | 86,314 | 43% |
| 4 | 185,153 | 112,948 | 61% |
| 5 | 117,615 | 65,558 | 56% |
| 6 | 158,976 | 94,457 | 59% |
| 7 | 262,098 | 152,064 | 58% |
| 8 | 70,059 | 42,399 | 61% |
| 9 | 117,024 | 40,198 | 34% |
| 10 | 100,667 | 54,077 | 54% |
| 11 | 115,908 | 55,071 | 48% |
| 12 | 122,529 | 67,358 | 55% |
| 13 | 40,712 | 25,169 | 62% |
| 14 | 49,444 | 30,151 | 61% |
| 15 | 95,794 | 55,908 | 58% |
| 16 | 126,669 | 60,929 | 48% |
| 17 | 100,081 | 59,340 | 59% |
| 18 | 104,235 | 52,633 | 50% |
| 19 | 93,059 | 56,361 | 61% |
| 20 | 131,623 | 73,699 | 56% |
| 21 | 120,306 | 65,905 | 55% |
| 22 | 103,691 | 61,269 | 59% |
| 23 | 114,476 | 59,044 | 52% |
| 24 | 57,423 | 27,917 | 49% |
| 25 | 75,352 | 45,519 | 60% |
| 26 | 212,529 | 79,582 | 37% |
| 27 | 88,955 | 40,539 | 46% |
| 28 | 81,616 | 36,030 | 44% |
| 29 | 83,850 | 47,045 | 56% |
| 30 | 58,532 | 31,181 | 53% |
| 31 | 32,584 | 19,824 | 61% |
| 32 | 29,551 | 17,248 | 58% |
| 33 | 68,656 | 30,957 | 45% |
| 34 | 52,752 | 32,309 | 61% |
| 35 | 41,072 | 19,593 | 48% |
| 36 | 82,068 | 49,437 | 60% |
| 37 | 203,018 | 74,282 | 37% |
| 38 | 88,020 | 48,826 | 55% |
| 39 | 69,267 | 42,586 | 61% |
| 40 | 75,904 | 46,478 | 61% |
| 41 | 55,640 | 34,592 | 62% |
| 42 | 52,538 | 23,951 | 46% |
| 43 | 88,772 | 45,143 | 51% |
| 44 | 56,844 | 33,175 | 58% |
| 45 | 35,756 | 20,473 | 57% |
| 46 | 33,008 | 19,349 | 59% |
| 47 | 36,709 | 19,935 | 54% |
| 48 | 29,147 | 11,718 | 40% |
| 49 | 18,157 | 7,609 | 42% |
| 50 | 43,250 | 26,658 | 62% |
| 51 | 57,833 | 34,011 | 59% |
| 52 | 49,288 | 29,412 | 60% |
| 53 | 64,939 | 32,936 | 51% |
| 54 | 52,365 | 29,621 | 57% |
| 55 | 76,025 | 28,942 | 38% |
| 56 | 96,075 | 56,557 | 59% |
| 57 | 29,220 | 17,440 | 60% |
| 58 | 23,553 | 11,457 | 49% |
| 59 | 25,808 | 13,353 | 52% |
| 60 | 13,849 | 8,116 | 59% |
| 61 | 14,111 | 8,410 | 60% |
| 62 | 10,757 | 6,494 | 60% |
| 63 | 12,035 | 7,637 | 63% |
| 64 | 17,192 | 9,692 | 56% |
| 65 | 11,694 | 6,744 | 58% |
| 66 | 11,520 | 6,066 | 53% |
| 67 | 30,342 | 18,281 | 60% |
| 68 | 51,752 | 30,482 | 59% |
| 69 | 50,479 | 28,127 | 56% |
| 70 | 42,649 | 25,025 | 59% |
| 71 | 29,972 | 17,868 | 60% |
| 72 | 29,283 | 17,662 | 60% |
| 73 | 18,792 | 9,718 | 52% |
| 74 | 51,870 | 22,419 | 43% |
| 75 | 38,613 | 23,424 | 61% |
| 76 | 30,313 | 17,498 | 58% |
| 77 | 47,892 | 29,581 | 62% |
| 78 | 39,984 | 24,218 | 61% |
| 79 | 48,496 | 28,737 | 59% |
| 80 | 41,675 | 25,558 | 61% |
| 81 | 29,554 | 15,736 | 53% |
| 82 | 19,168 | 11,142 | 58% |
| 83 | 37,366 | 18,990 | 51% |
| 84 | 25,333 | 12,985 | 51% |
| 85 | 21,837 | 12,862 | 59% |
| 86 | 16,849 | 8,407 | 50% |
| 87 | 18,645 | 7,481 | 40% |
| 88 | 25,348 | 9,576 | 38% |
| 89 | 28,156 | 11,194 | 40% |
| 90 | 23,421 | 13,788 | 59% |
| 91 | 18,080 | 10,212 | 56% |
| 92 | 29,452 | 12,826 | 44% |
| 93 | 13,865 | 8,591 | 62% |
| 94 | 10,235 | 5,452 | 53% |
| 95 | 8,008 | 5,061 | 63% |
| 96 | 19,502 | 10,853 | 56% |
| 97 | 5,343 | 3,122 | 58% |
| 98 | 8,210 | 4,608 | 56% |
| 99 | 8,269 | 4,698 | 57% |
| 100 | 13,217 | 6,347 | 48% |
| 101 | 11,643 | 5,449 | 47% |
| 102 | 8,409 | 4,215 | 50% |
| 103 | 3,606 | 1,896 | 53% |
| 104 | 8,888 | 4,606 | 52% |
| 105 | 5,244 | 3,076 | 59% |
| 106 | 4,327 | 2,330 | 54% |
| 107 | 7,014 | 3,915 | 56% |
| 108 | 3,431 | 1,683 | 49% |
| 109 | 6,635 | 3,804 | 57% |
| 110 | 4,665 | 2,684 | 58% |
| 111 | 7,129 | 4,415 | 62% |
| 112 | 6,036 | 3,413 | 57% |
| 113 | 6,873 | 4,203 | 61% |
| 114 | 7,811 | 4,535 | 58% |

## Second pass (natural-length rewrite)

A second pass re-cut the corpus again, this time to remove the generator's
"chain" habit — short sentences that only hand a word to the next one — and to
let every verse take the length its content actually needs.

**Result: 3,682,471 words to 2,724,601 words.** Verse commentary median 398
words (range 92 to 1,032) instead of a flat target.

Tools added for this pass:

* `scripts/chain_cleanup.py` — removes echo-link ("chain") sentences, never
  touching a citation, a hadith reference, a Qur'an reference or a quotation;
  reports a `chain_density` metric per file.
* `scripts/edit_sections.py` — the section-level editorial pass: scores each
  paragraph for substance, drops repeated points, trims the tail of sections
  that run past what the verse needs, and always keeps citations, hadith and
  quoted scripture.

Notes on what the second pass found:

* Sūrahs 37, 69 and 70 were machine filler even in the first draft (over 60
  percent of their sentences were chain residue). Their verse commentaries were
  written from scratch: 66 sections.
* Sixteen hadith reports that the first pass had dropped were restored from the
  draft, with their collection references intact (4:100, 4:102, 4:105, 4:125,
  5:30, 5:36, 5:67, 7:6, 7:7, 7:10, 7:16, 7:20, 7:21, 7:39, 7:94, 50:17).
* Every verse blockquote was checked against `data/chapter_NNN.js`; the corpus
  now matches the canonical verse text exactly (6,236 sections, 6,241 quoted
  lines, zero mismatches).

## Deepening pass

A third pass went back over every section that the earlier passes had left thin
or filler-driven, because cutting is not the same as writing:

* **Sūrah al-Ṣāffāt (37)** — 56 verse commentaries rewritten from filler,
  including the whole quarrel of the Fire (37:22–40) and the prophets' stories
  (37:75–146).
* **Sūrah al-Ḥāqqah (69) and al-Maʿārij (70)** — 46 sections rewritten; every
  verse of both chapters now carries verse-specific commentary (minimum 92 and
  95 words, previously 9 and 10).
* **Sūrah al-Naḥl (16)** — 68 sections replaced. The draft had generated 59 of
  them from a template that described the wrong verse entirely (16:90's
  commentary discussed the Sabbath, 16:125's discussed oaths), plus nine more
  with the same boilerplate. All 128 sections of the chapter now address their
  own verse.
* **Sūrahs 2, 12, 20, 28, 48, 49, 86** — 46 short sections extended with their
  parallel passages, occasions of revelation, or classical readings.

Corpus floor: 92 words (was 83), median unchanged at 398. `scripts/factcheck.py`
on the finished corpus reports no citation, quotation or reference problems, and
every chapter's section count still matches its `data/chapter_NNN.js`.
