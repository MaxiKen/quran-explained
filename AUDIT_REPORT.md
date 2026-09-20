# Commentary audit — all 114 chapters

Generated from the corpus itself: every one of the 6,236 verse sections was measured against its own verse in `data/chapter_NNN.js`, not against a fixed word target.

## Overall

| measure | value |
|---|---|
| verse sections | 6,236 |
| commentary words | 2,506,972 |
| words per verse commentary | min 92, median 399, mean 402 |
| chapter intros | 114, min 238 words, median 541 |
| readability (Flesch) | min 11, 10th percentile 35, median 54 |
| quoted verse lines matching canon | 6,241 of 6,241 |

Element coverage across the corpus, in the share of sections that carry it:

| element | sections | share |
|---|---|---|
| meaning | 6,236 | 100% |
| lexical | 5,962 | 96% |
| context | 1,136 | 18% |
| hadith | 1,557 | 25% |
| ruling | 2,259 | 36% |
| crossref | 5,302 | 85% |
| story | 1,692 | 27% |
| theology | 3,898 | 63% |
| application | 2,909 | 47% |
| variant | 1,096 | 18% |
| flow | 5,978 | 96% |
| parable | 1,660 | 27% |

Objective readability measures, before and after this session's repairs:

| measure | before | after |
|---|---|---|
| sections with a 60-word sentence (3 or more) | 126 | 23 |
| sections dense by Flesch (<25) and over 150 words | 354 | 245 |
| sections with Flesch under 20 | 211 | 96 |
| Flesch 10th percentile | 31 | 35 |

The flag columns below are keyword-based prompts to inspect, not verdicts. Sampled sections flagged `under-depth` or `legal-not-explained` (3:7, 3:97, 3:144 among them) read as complete commentaries and were left alone, and rewriting a section can raise a depth flag simply by making the prose tighter. What the flags identified reliably, on inspection, were the telegraphic note-style sections, story verses that never tell the story, and legal verses with no ruling discussion. Those are queued in chapter order at the end of this report.

## Per chapter

`depth` = median commentary words as a multiple of the verse's own length; `elems` = share of the chapter's sections carrying at least one grounded element (lexicology, context, hadith, ruling, cross-reference, story, variant reading or parable); `open` = sections still carrying a content or readability flag.

| ch | verses | med words | depth | elems | hadith | ruling | context | open |
|---|---|---|---|---|---|---|---|---|
| 1 | 7 | 519 | 55.6x | 100% | 100% | 29% | 14% | 0 |
| 2 | 286 | 539 | 15.1x | 100% | 43% | 64% | 18% | 20 |
| 3 | 200 | 328 | 10.6x | 100% | 20% | 28% | 38% | 10 |
| 4 | 176 | 653 | 20.4x | 100% | 39% | 81% | 28% | 25 |
| 5 | 120 | 492 | 12.9x | 100% | 51% | 75% | 27% | 20 |
| 6 | 165 | 530 | 16.6x | 100% | 9% | 42% | 32% | 8 |
| 7 | 206 | 599 | 22.8x | 100% | 30% | 49% | 22% | 8 |
| 8 | 75 | 332 | 12.6x | 100% | 28% | 45% | 77% | 10 |
| 9 | 129 | 246 | 6.8x | 100% | 18% | 50% | 26% | 25 |
| 10 | 109 | 414 | 13.1x | 100% | 18% | 29% | 13% | 13 |
| 11 | 123 | 293 | 10.9x | 100% | 15% | 20% | 6% | 9 |
| 12 | 111 | 426 | 14.4x | 100% | 19% | 45% | 18% | 45 |
| 13 | 43 | 602 | 17.4x | 100% | 44% | 33% | 21% | 2 |
| 14 | 52 | 411 | 15.4x | 100% | 35% | 13% | 12% | 3 |
| 15 | 99 | 571 | 41.5x | 100% | 9% | 39% | 30% | 0 |
| 16 | 128 | 249 | 9.0x | 100% | 13% | 31% | 17% | 21 |
| 17 | 111 | 496 | 18.1x | 100% | 38% | 50% | 29% | 35 |
| 18 | 110 | 316 | 12.2x | 100% | 45% | 25% | 13% | 13 |
| 19 | 98 | 493 | 23.6x | 100% | 33% | 42% | 35% | 4 |
| 20 | 135 | 268 | 14.8x | 100% | 10% | 20% | 9% | 58 |
| 21 | 112 | 381 | 19.6x | 100% | 5% | 13% | 6% | 7 |
| 22 | 78 | 546 | 19.5x | 100% | 21% | 42% | 18% | 4 |
| 23 | 118 | 261 | 16.8x | 100% | 7% | 18% | 6% | 7 |
| 24 | 64 | 258 | 8.8x | 100% | 50% | 56% | 22% | 45 |
| 25 | 77 | 524 | 21.8x | 100% | 29% | 26% | 27% | 1 |
| 26 | 227 | 203 | 19.2x | 100% | 5% | 20% | 4% | 18 |
| 27 | 93 | 228 | 10.5x | 100% | 14% | 20% | 5% | 10 |
| 28 | 88 | 291 | 9.8x | 100% | 15% | 28% | 22% | 18 |
| 29 | 69 | 515 | 18.8x | 100% | 14% | 39% | 36% | 10 |
| 30 | 60 | 283 | 10.5x | 100% | 38% | 30% | 13% | 23 |
| 31 | 34 | 519 | 18.4x | 100% | 50% | 32% | 24% | 3 |
| 32 | 30 | 426 | 16.5x | 100% | 23% | 37% | 10% | 1 |
| 33 | 73 | 292 | 11.2x | 100% | 19% | 55% | 25% | 10 |
| 34 | 54 | 569 | 19.9x | 100% | 15% | 31% | 7% | 4 |
| 35 | 45 | 271 | 9.1x | 100% | 7% | 27% | 7% | 7 |
| 36 | 83 | 628 | 35.2x | 100% | 16% | 16% | 5% | 2 |
| 37 | 182 | 161 | 18.7x | 100% | 20% | 18% | 13% | 19 |
| 38 | 88 | 427 | 26.3x | 100% | 10% | 33% | 19% | 12 |
| 39 | 75 | 466 | 15.8x | 100% | 80% | 33% | 27% | 13 |
| 40 | 85 | 386 | 15.0x | 100% | 44% | 40% | 20% | 57 |
| 41 | 54 | 644 | 23.4x | 100% | 26% | 48% | 17% | 3 |
| 42 | 53 | 287 | 9.0x | 100% | 8% | 19% | 0% | 10 |
| 43 | 89 | 276 | 12.4x | 100% | 1% | 15% | 4% | 10 |
| 44 | 59 | 309 | 27.5x | 100% | 64% | 25% | 44% | 18 |
| 45 | 37 | 437 | 15.2x | 100% | 5% | 32% | 22% | 4 |
| 46 | 35 | 400 | 11.7x | 100% | 17% | 37% | 20% | 3 |
| 47 | 38 | 374 | 14.4x | 100% | 29% | 21% | 34% | 2 |
| 48 | 29 | 293 | 9.8x | 100% | 17% | 14% | 45% | 7 |
| 49 | 18 | 230 | 7.6x | 100% | 33% | 39% | 28% | 1 |
| 50 | 45 | 591 | 32.9x | 100% | 49% | 44% | 4% | 0 |
| 51 | 60 | 582 | 47.0x | 100% | 38% | 55% | 5% | 5 |
| 52 | 49 | 539 | 35.7x | 100% | 55% | 43% | 20% | 0 |
| 53 | 62 | 363 | 32.0x | 100% | 29% | 27% | 11% | 4 |
| 54 | 55 | 312 | 23.4x | 100% | 11% | 11% | 4% | 4 |
| 55 | 78 | 274 | 27.3x | 100% | 29% | 13% | 8% | 1 |
| 56 | 96 | 353 | 44.8x | 100% | 24% | 24% | 21% | 14 |
| 57 | 29 | 325 | 7.5x | 100% | 31% | 38% | 3% | 8 |
| 58 | 22 | 282 | 7.6x | 100% | 41% | 59% | 9% | 6 |
| 59 | 24 | 284 | 9.1x | 100% | 46% | 38% | 33% | 3 |
| 60 | 13 | 533 | 8.9x | 100% | 38% | 54% | 92% | 1 |
| 61 | 14 | 484 | 14.2x | 100% | 36% | 64% | 21% | 3 |
| 62 | 11 | 492 | 18.6x | 100% | 18% | 55% | 36% | 0 |
| 63 | 11 | 528 | 13.9x | 100% | 73% | 55% | 36% | 2 |
| 64 | 18 | 452 | 15.9x | 100% | 50% | 33% | 6% | 1 |
| 65 | 12 | 379 | 8.5x | 100% | 17% | 100% | 8% | 2 |
| 66 | 12 | 353 | 9.2x | 100% | 50% | 67% | 0% | 3 |
| 67 | 30 | 475 | 20.8x | 100% | 50% | 17% | 40% | 1 |
| 68 | 52 | 467 | 41.8x | 100% | 48% | 48% | 31% | 5 |
| 69 | 52 | 258 | 20.3x | 100% | 6% | 25% | 4% | 1 |
| 70 | 44 | 188 | 21.3x | 100% | 7% | 32% | 9% | 7 |
| 71 | 28 | 537 | 36.1x | 100% | 32% | 25% | 25% | 4 |
| 72 | 28 | 505 | 27.6x | 100% | 46% | 21% | 39% | 0 |
| 73 | 20 | 241 | 16.1x | 100% | 45% | 35% | 10% | 3 |
| 74 | 56 | 234 | 33.0x | 100% | 21% | 25% | 7% | 3 |
| 75 | 40 | 548 | 60.7x | 100% | 20% | 45% | 12% | 2 |
| 76 | 31 | 510 | 32.9x | 100% | 13% | 26% | 16% | 2 |
| 77 | 50 | 529 | 67.2x | 100% | 6% | 56% | 6% | 0 |
| 78 | 40 | 484 | 64.4x | 100% | 20% | 25% | 10% | 0 |
| 79 | 46 | 422 | 43.9x | 100% | 15% | 54% | 4% | 0 |
| 80 | 42 | 445 | 65.0x | 100% | 21% | 31% | 2% | 1 |
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
| 95 | 8 | 592 | 74.8x | 100% | 62% | 88% | 12% | 0 |
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
* 32 sections rewritten from note-style into connected prose: Sūrah al-Anfāl 8:39–75 (19 sections), 2:28, 11:16, 14:27, 14:31, 20:54, 21:29, 21:61–65, and 37:54, 69:16, 70:28.
* Every cross-reference, hadith citation and quoted verse in those 29 sections was carried across; the applier refuses a rewrite that would drop a real reference.
* Verified afterwards: 6,236 sections, all 6,241 quoted lines matching the canonical translations, no empty sections, `scripts/factcheck.py` clean apart from the standing authority-whitelist review.

## Progress of the element-repair pass

Chapters 1-28 have been read section by section against their verses. 288 sections were extended or rewritten to carry the element their verse calls for and that the commentary had not supplied — principally rulings (2:158, 2:230, 2:234, 2:282, 3:97, 5:89, 5:95, 5:106), occasions of revelation (5:106), narrative detail (2:20, 5:112, 5:114, 5:115), and cross-references where the section had summarised without grounding. Nine of them (5:89, 5:95, 5:96, 5:106, 5:108, 5:112, 5:114, 5:115, 5:116) were in the old word-by-word gloss style — 'itha, when; qāla, he said' — and are now plain prose.

The largest single patch was Surah al-Tawbah, whose 51 short sections were read against their verses and extended with the Tabūk setting, the hadith of ʿAdī ibn Ḥātim on taking rabbis as lords, the Prophet's farewell-sermon statement of the sacred months, the eight categories of alms, the mosque of Ḍirār, the pledge of ʿAqabah behind 9:111, and Kaʿb ibn Mālik's account of the three who stayed behind. Surah al-Nahl's thirty short sections gained the milk and bee passages with the hadith on honey, the two parables read against the associate-gods, the report of ʿAmmār ibn Yāsir behind 16:106, and the method of invitation in 16:125. Surahs 10-14, 18-28 and 16 gained their missing cross-references, rulings and occasions of revelation in the same way.

## Still open (queued, in chapter order)

1. **Telegraphic sections**: none known to be left. The last batch — 37:54, 69:16 and 70:28 — was rewritten in the same way as 8:74 and 21:63. Six sections that the same heuristic picked out (25:62, 25:67, 25:72, 65:5, 65:11, 101:6) were read and left alone: they are connected prose, and only the sentence-length measure flagged them.
2. **Hard-to-read sections**: 96 with Flesch under 20 and more than 140 words — 4:140, 5:110, 5:113, 5:119, 17:2, 17:6, 17:17, 17:27, 17:32, 17:38, 17:64, 17:76, 17:101, 17:104, 17:111, 20:8, 20:9, 20:32, 20:53, 20:56, 20:57, 20:60, 20:62, 20:64, … (worst first, chapter order).
3. **Content gaps to verify one by one**: 372 sections flagged as a story verse without story content, a legal verse without a ruling, or nothing but paraphrase. Each needs to be read against its verse before adding anything, because the flag can be a false positive (it fires on keyword absence, not on absence of substance).