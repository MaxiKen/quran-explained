# Commentary audit — all 114 chapters

Generated from the corpus itself: every one of the 6,236 verse sections was measured against its own verse in `data/chapter_NNN.js`, not against a fixed word target.

## Overall

| measure | value |
|---|---|
| verse sections | 6,236 |
| commentary words | 2,473,262 |
| words per verse commentary | min 92, median 396, mean 396 |
| chapter intros | 114, min 238 words, median 541 |
| readability (Flesch) | min -16, 10th percentile 34, median 54 |
| quoted verse lines matching canon | 6,241 of 6,241 |

Element coverage across the corpus, in the share of sections that carry it:

| element | sections | share |
|---|---|---|
| meaning | 6,236 | 100% |
| lexical | 5,944 | 95% |
| context | 1,098 | 18% |
| hadith | 1,526 | 24% |
| ruling | 2,229 | 36% |
| crossref | 5,147 | 83% |
| story | 1,671 | 27% |
| theology | 3,860 | 62% |
| application | 2,845 | 46% |
| variant | 1,100 | 18% |
| flow | 5,939 | 95% |
| parable | 1,638 | 26% |

Objective readability measures, before and after this session's repairs:

| measure | before | after |
|---|---|---|
| sections with a 60-word sentence (3 or more) | 126 | 23 |
| sections dense by Flesch (<25) and over 150 words | 354 | 301 |
| sections with Flesch under 20 | 211 | 181 |
| Flesch 10th percentile | 31 | 34 |

The flag columns below are keyword-based prompts to inspect, not verdicts. Sampled sections flagged `under-depth` or `legal-not-explained` (3:7, 3:97, 3:144 among them) read as complete commentaries and were left alone, and rewriting a section can raise a depth flag simply by making the prose tighter. What the flags identified reliably, on inspection, were the telegraphic note-style sections, story verses that never tell the story, and legal verses with no ruling discussion. Those are queued in chapter order at the end of this report.

## Per chapter

`depth` = median commentary words as a multiple of the verse's own length; `elems` = share of the chapter's sections carrying at least one grounded element (lexicology, context, hadith, ruling, cross-reference, story, variant reading or parable); `open` = sections still carrying a content or readability flag.

| ch | verses | med words | depth | elems | hadith | ruling | context | open |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 | 519 | 55.6x | 100% | 100% | 29% | 14% | 0 |
| 2 | 286 | 539 | 15.1x | 100% | 42% | 64% | 18% | 25 |
| 3 | 200 | 247 | 10.2x | 100% | 18% | 24% | 36% | 49 |
| 4 | 176 | 653 | 20.4x | 100% | 39% | 81% | 28% | 25 |
| 5 | 120 | 492 | 13.0x | 100% | 51% | 74% | 27% | 21 |
| 6 | 165 | 530 | 16.6x | 100% | 9% | 42% | 32% | 8 |
| 7 | 206 | 599 | 22.8x | 100% | 30% | 49% | 22% | 8 |
| 8 | 75 | 332 | 12.6x | 100% | 28% | 45% | 77% | 10 |
| 9 | 129 | 194 | 5.8x | 100% | 4% | 43% | 14% | 63 |
| 10 | 109 | 414 | 12.9x | 100% | 18% | 29% | 13% | 20 |
| 11 | 123 | 289 | 10.5x | 100% | 15% | 18% | 6% | 16 |
| 12 | 111 | 424 | 14.4x | 100% | 19% | 43% | 18% | 46 |
| 13 | 43 | 602 | 17.4x | 100% | 44% | 33% | 21% | 2 |
| 14 | 52 | 411 | 15.4x | 100% | 35% | 13% | 12% | 3 |
| 15 | 99 | 571 | 41.5x | 100% | 9% | 39% | 30% | 0 |
| 16 | 128 | 141 | 7.3x | 100% | 12% | 28% | 16% | 41 |
| 17 | 111 | 500 | 18.1x | 100% | 38% | 51% | 29% | 39 |
| 18 | 110 | 294 | 12.2x | 100% | 45% | 25% | 13% | 15 |
| 19 | 98 | 493 | 23.6x | 100% | 33% | 42% | 35% | 4 |
| 20 | 135 | 265 | 14.4x | 100% | 9% | 21% | 10% | 77 |
| 21 | 112 | 381 | 19.6x | 100% | 5% | 13% | 5% | 7 |
| 22 | 78 | 546 | 19.5x | 100% | 21% | 42% | 18% | 4 |
| 23 | 118 | 258 | 16.7x | 100% | 7% | 17% | 6% | 11 |
| 24 | 64 | 233 | 7.8x | 100% | 50% | 52% | 17% | 55 |
| 25 | 77 | 524 | 21.8x | 100% | 29% | 26% | 27% | 1 |
| 26 | 227 | 201 | 19.1x | 100% | 5% | 20% | 4% | 29 |
| 27 | 93 | 226 | 10.3x | 100% | 13% | 20% | 5% | 15 |
| 28 | 88 | 287 | 9.7x | 100% | 15% | 27% | 19% | 24 |
| 29 | 69 | 515 | 18.8x | 100% | 14% | 39% | 36% | 10 |
| 30 | 60 | 252 | 10.2x | 100% | 38% | 32% | 10% | 29 |
| 31 | 34 | 519 | 18.4x | 100% | 50% | 32% | 24% | 3 |
| 32 | 30 | 426 | 16.5x | 100% | 23% | 37% | 10% | 1 |
| 33 | 73 | 285 | 11.2x | 100% | 19% | 55% | 23% | 11 |
| 34 | 54 | 569 | 19.9x | 100% | 15% | 31% | 7% | 4 |
| 35 | 45 | 243 | 8.5x | 100% | 4% | 27% | 7% | 10 |
| 36 | 83 | 628 | 35.2x | 100% | 16% | 16% | 5% | 2 |
| 37 | 182 | 160 | 17.7x | 100% | 19% | 18% | 13% | 21 |
| 38 | 88 | 427 | 26.3x | 100% | 10% | 33% | 19% | 12 |
| 39 | 75 | 466 | 15.8x | 100% | 80% | 33% | 27% | 13 |
| 40 | 85 | 393 | 15.2x | 100% | 48% | 41% | 18% | 70 |
| 41 | 54 | 644 | 23.4x | 100% | 26% | 48% | 17% | 3 |
| 42 | 53 | 285 | 8.3x | 100% | 4% | 19% | 0% | 16 |
| 43 | 89 | 274 | 11.7x | 100% | 1% | 15% | 4% | 16 |
| 44 | 59 | 309 | 27.5x | 100% | 64% | 25% | 44% | 18 |
| 45 | 37 | 435 | 15.0x | 100% | 5% | 32% | 22% | 4 |
| 46 | 35 | 400 | 11.7x | 100% | 17% | 37% | 20% | 3 |
| 47 | 38 | 374 | 14.4x | 100% | 29% | 21% | 34% | 2 |
| 48 | 29 | 252 | 7.5x | 100% | 14% | 14% | 34% | 9 |
| 49 | 18 | 229 | 7.1x | 100% | 28% | 33% | 28% | 2 |
| 50 | 45 | 591 | 32.9x | 100% | 49% | 44% | 4% | 0 |
| 51 | 60 | 582 | 47.0x | 100% | 38% | 55% | 5% | 5 |
| 52 | 49 | 539 | 35.7x | 100% | 55% | 43% | 20% | 0 |
| 53 | 62 | 363 | 32.0x | 100% | 29% | 27% | 11% | 4 |
| 54 | 55 | 312 | 23.4x | 100% | 11% | 11% | 4% | 4 |
| 55 | 78 | 274 | 27.3x | 100% | 29% | 13% | 8% | 1 |
| 56 | 96 | 353 | 44.8x | 100% | 24% | 24% | 21% | 14 |
| 57 | 29 | 332 | 7.5x | 100% | 31% | 38% | 3% | 8 |
| 58 | 22 | 275 | 7.5x | 100% | 41% | 59% | 5% | 7 |
| 59 | 24 | 284 | 9.1x | 100% | 46% | 38% | 33% | 3 |
| 60 | 13 | 533 | 8.9x | 100% | 38% | 54% | 92% | 1 |
| 61 | 14 | 484 | 14.2x | 100% | 36% | 64% | 21% | 4 |
| 62 | 11 | 492 | 18.6x | 100% | 18% | 55% | 36% | 0 |
| 63 | 11 | 528 | 13.9x | 100% | 73% | 55% | 36% | 2 |
| 64 | 18 | 452 | 15.9x | 100% | 50% | 33% | 6% | 1 |
| 65 | 12 | 379 | 8.5x | 100% | 17% | 100% | 8% | 2 |
| 66 | 12 | 353 | 9.2x | 100% | 50% | 67% | 0% | 3 |
| 67 | 30 | 475 | 20.8x | 100% | 53% | 17% | 40% | 1 |
| 68 | 52 | 467 | 41.8x | 100% | 48% | 48% | 31% | 5 |
| 69 | 52 | 261 | 21.1x | 100% | 6% | 23% | 4% | 1 |
| 70 | 44 | 158 | 21.3x | 100% | 7% | 32% | 9% | 10 |
| 71 | 28 | 537 | 36.1x | 100% | 32% | 25% | 25% | 4 |
| 72 | 28 | 505 | 27.6x | 100% | 46% | 21% | 39% | 0 |
| 73 | 20 | 241 | 16.1x | 100% | 45% | 35% | 10% | 3 |
| 74 | 56 | 234 | 33.0x | 100% | 21% | 25% | 7% | 3 |
| 75 | 40 | 548 | 60.7x | 100% | 20% | 45% | 12% | 2 |
| 76 | 31 | 510 | 32.9x | 100% | 13% | 26% | 16% | 2 |
| 77 | 50 | 529 | 68.4x | 100% | 6% | 56% | 6% | 0 |
| 78 | 40 | 484 | 64.4x | 100% | 20% | 25% | 10% | 0 |
| 79 | 46 | 422 | 43.9x | 100% | 15% | 54% | 4% | 0 |
| 80 | 42 | 445 | 65.0x | 100% | 24% | 31% | 2% | 1 |
| 81 | 29 | 313 | 44.7x | 100% | 21% | 48% | 3% | 0 |
| 82 | 19 | 463 | 62.4x | 100% | 5% | 26% | 5% | 0 |
| 83 | 36 | 273 | 30.9x | 100% | 6% | 31% | 0% | 3 |
| 84 | 25 | 271 | 33.1x | 100% | 4% | 28% | 0% | 0 |
| 85 | 22 | 373 | 41.8x | 100% | 27% | 36% | 0% | 3 |
| 86 | 17 | 310 | 36.3x | 100% | 6% | 53% | 6% | 0 |
| 87 | 19 | 288 | 37.1x | 100% | 26% | 5% | 5% | 5 |
| 88 | 26 | 284 | 42.1x | 100% | 15% | 0% | 4% | 3 |
| 89 | 30 | 273 | 38.4x | 100% | 7% | 40% | 0% | 2 |
| 90 | 20 | 491 | 57.6x | 100% | 25% | 60% | 10% | 2 |
| 91 | 15 | 481 | 52.7x | 100% | 20% | 73% | 13% | 0 |
| 92 | 21 | 307 | 37.0x | 100% | 14% | 38% | 0% | 1 |
| 93 | 11 | 488 | 52.3x | 100% | 27% | 64% | 36% | 0 |
| 94 | 8 | 312 | 46.4x | 100% | 12% | 38% | 25% | 0 |
| 95 | 8 | 590 | 74.6x | 100% | 62% | 88% | 12% | 0 |
| 96 | 19 | 443 | 54.1x | 100% | 42% | 26% | 11% | 1 |
| 97 | 5 | 578 | 47.8x | 100% | 60% | 20% | 60% | 0 |
| 98 | 8 | 506 | 20.5x | 100% | 62% | 12% | 12% | 0 |
| 99 | 8 | 440 | 48.8x | 100% | 62% | 38% | 12% | 0 |
| 100 | 11 | 374 | 43.2x | 100% | 9% | 73% | 9% | 0 |
| 101 | 11 | 294 | 43.0x | 100% | 9% | 27% | 0% | 1 |
| 102 | 8 | 264 | 28.8x | 100% | 38% | 38% | 0% | 0 |
| 103 | 3 | 470 | 78.3x | 100% | 33% | 100% | 0% | 0 |
| 104 | 9 | 266 | 40.7x | 100% | 11% | 56% | 22% | 0 |
| 105 | 5 | 300 | 37.5x | 100% | 0% | 0% | 40% | 0 |
| 106 | 4 | 295 | 25.7x | 100% | 25% | 0% | 50% | 0 |
| 107 | 7 | 354 | 47.7x | 100% | 14% | 43% | 14% | 1 |
| 108 | 3 | 307 | 34.3x | 100% | 33% | 0% | 0% | 1 |
| 109 | 6 | 265 | 36.9x | 100% | 17% | 0% | 17% | 0 |
| 110 | 3 | 668 | 47.4x | 100% | 100% | 33% | 100% | 0 |
| 111 | 5 | 529 | 51.7x | 100% | 60% | 20% | 40% | 0 |
| 112 | 4 | 558 | 76.4x | 100% | 75% | 25% | 25% | 0 |
| 113 | 5 | 514 | 46.7x | 100% | 80% | 0% | 20% | 0 |
| 114 | 6 | 548 | 77.1x | 100% | 50% | 50% | 17% | 0 |

## What this session repaired

* A plain-English pass over the whole corpus: 1,738 sections had over-long sentences split at safe clause boundaries and abstract register replaced with everyday wording (sentence-level rewrites are guarded so no citation, hadith number, quote line or heading can change; 0 sections were rolled back by the guard because none broke).
* 29 sections rewritten from note-style into connected prose: Sūrah al-Anfāl 8:39–75 (19 sections) and 2:28, 11:16, 14:27, 14:31, 20:54, 21:29, 21:61–65.
* Every cross-reference, hadith citation and quoted verse in those 29 sections was carried across; the applier refuses a rewrite that would drop a real reference.
* Verified afterwards: 6,236 sections, all 6,241 quoted lines matching the canonical translations, no empty sections, `scripts/factcheck.py` clean apart from the standing authority-whitelist review.

## Still open (queued, in chapter order)

1. **Telegraphic sections**: 9 left — 25:62, 25:67, 25:72, 37:54, 65:5, 65:11, 69:16, 70:28, 101:6. Same treatment as 8:74 and 21:63 above.
2. **Hard-to-read sections**: 181 with Flesch under 20 and more than 140 words — 2:282, 4:140, 5:95, 5:106, 5:110, 5:113, 5:119, 17:2, 17:4, 17:6, 17:16, 17:17, 17:27, 17:32, 17:38, 17:45, 17:58, 17:64, 17:76, 17:88, 17:99, 17:100, 17:101, 17:104, … (worst first, chapter order).
3. **Content gaps to verify one by one**: 418 sections flagged as a story verse without story content, a legal verse without a ruling, or nothing but paraphrase. Each needs to be read against its verse before adding anything, because the flag can be a false positive (it fires on keyword absence, not on absence of substance).