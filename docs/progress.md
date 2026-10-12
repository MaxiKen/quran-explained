<!-- GENERATED FILE — do not edit by hand.
     python3 tools/progress.py --report   regenerates it from data/plan.json,
     data/guidance_*.json and data/runs/*.json. On a merge conflict here,
     re-run the command on the merged tree and commit the result.
     Narrative logs live in docs/runs/; per-run records in data/runs/. -->

# Progress

Generated 2026-10-12 by `tools/progress.py --report`.

## Corpus

| | |
|---|---|
| Verses authored | **543 of 6,236** (8.71%) |
| Planned words written | **749,840** of 5,902,150 (12.70%) |
| Words on disk | 693,959 (every verse at or over its floor: yes) |
| Remaining | 5,152,310 planned words |
| Source sets | 8 (six complete + al-Qushayrī 1,287 + al-Wāḥidī 431) |
| Runs on record | 2 |

`tools/progress.py --next` is authoritative for where to resume; `tools/progress.py --runs` lists every run. Chapters need **not** be authored in order — see [`parallel.md`](parallel.md).

## Chapters on record

| chapter | on disk | planned words on disk | claims |
|---|---|---|---|
| 1 | 7/7 | 7,747 | serial-era 1:1-7 (done) |
| 2 | 286/286 | 383,222 | serial-era 2:1-286 (done) |
| 3 | 200/200 | 243,336 | serial-era 3:1-200 (done) |
| 5 | 50/120 | 59,654 | ch5-73a7 5:1-50 (open) |

## Runs — every agent on record

### ch5-73a7 — in-progress

*branch* `arena/73a7ec92-quran-explained` · *claimed* 2026-10-12 · *updated* 2026-10-12 · *record* [`data/runs/ch5-73a7.json`](../data/runs/ch5-73a7.json)

| range | state | verses on disk | words on disk |
|---|---|---|---|
| 5:1-50 | open | 50/50 | 59,654 |

Batches:

- 2026-10-12 · 5:1-10 — `152498d`
- 2026-10-12 · 5:11-20 — `b3899bd`
- 2026-10-12 · 5:21-30 — `ec1133c`
- 2026-10-12 · 5:31-40 — `73215bb`
- 2026-10-12 · 5:41-50 — `37440b7`

> ch. 5 opening, 50 verses in 5 compiled batches

### serial-era — done

*branch* `arena/525a7113-quran-explained → arena/fec53650-quran-explained → arena/fbd3f4f3-quran-explained` · *claimed* 2026-10-09 · *updated* 2026-10-12 · *record* [`data/runs/serial-era.json`](../data/runs/serial-era.json)

| range | state | verses on disk | words on disk |
|---|---|---|---|
| 1:1-7 | done | 7/7 | 7,747 |
| 2:1-286 | done | 286/286 | 383,222 |
| 3:1-200 | done | 200/200 | 243,336 |

Batches:

- 2026-10-12 · 3:64-113 — five ten-verse batches, compiled
- 2026-10-12 · 3:114-163 — five ten-verse batches, compiled
- 2026-10-12 · 3:164-173 — `1ea32f9` — compiled
- 2026-10-12 · 3:174-183 — `c7b8b31` — compiled
- 2026-10-12 · 3:184-193 — `b6fde27` — compiled
- 2026-10-12 · 3:194-200 — `02ad6c3` — compiled; closes Āl ʿImrān

> Everything authored before parallel runs began (2026-10-12): 1:1–1:7, all of al-Baqarah, all of Āl ʿImrān. data/guidance_112.json is an empty placeholder on purpose — it keeps the reader's fallback to the six tafsīr sets under test. Full narrative, including the batch-by-batch lessons, is in docs/runs/serial-era.md.

## Open work — all surahs with verses left (order is free)

| surah | resume at | verses left | planned words left | authored-only | claim |
|---|---|---|---|---|---|
| 4 | 4:1 | 176 | 241,440 | 1 | unclaimed |
| 5 | 5:51 | 70 | 97,690 | — | ch5-73a7 5:1-50 |
| 6 | 6:1 | 165 | 215,020 | 2 | unclaimed |
| 7 | 7:1 | 206 | 241,580 | 21 | unclaimed |
| 8 | 8:1 | 75 | 95,820 | 1 | unclaimed |
| 9 | 9:1 | 129 | 173,560 | 17 | unclaimed |
| 10 | 10:1 | 109 | 129,200 | 10 | unclaimed |
| 11 | 11:1 | 123 | 145,320 | 13 | unclaimed |
| 12 | 12:1 | 111 | 145,790 | 15 | unclaimed |
| 13 | 13:1 | 43 | 59,220 | 4 | unclaimed |
| 14 | 14:1 | 52 | 62,140 | 2 | unclaimed |
| 15 | 15:1 | 99 | 60,820 | — | unclaimed |
| 16 | 16:1 | 128 | 136,290 | 2 | unclaimed |
| 17 | 17:1 | 111 | 121,360 | 9 | unclaimed |
| 18 | 18:1 | 110 | 114,200 | 6 | unclaimed |
| 19 | 19:1 | 98 | 81,400 | 3 | unclaimed |
| 20 | 20:1 | 135 | 120,610 | — | unclaimed |
| 21 | 21:1 | 112 | 98,460 | 4 | unclaimed |
| 22 | 22:1 | 78 | 87,150 | 3 | unclaimed |
| 23 | 23:1 | 118 | 87,290 | 7 | unclaimed |
| 24 | 24:1 | 64 | 81,810 | 3 | unclaimed |
| 25 | 25:1 | 77 | 71,900 | — | unclaimed |
| 26 | 26:1 | 227 | 120,760 | 1 | unclaimed |
| 27 | 27:1 | 93 | 93,480 | 1 | unclaimed |
| 28 | 28:1 | 88 | 106,480 | 11 | unclaimed |
| 29 | 29:1 | 69 | 72,630 | 2 | unclaimed |
| 30 | 30:1 | 60 | 59,100 | 4 | unclaimed |
| 31 | 31:1 | 34 | 37,450 | 1 | unclaimed |
| 32 | 32:1 | 30 | 26,720 | — | unclaimed |
| 33 | 33:1 | 73 | 87,560 | 2 | unclaimed |
| 34 | 34:1 | 54 | 64,010 | — | unclaimed |
| 35 | 35:1 | 45 | 52,950 | 4 | unclaimed |
| 36 | 36:1 | 83 | 62,490 | 1 | unclaimed |
| 37 | 37:1 | 182 | 96,630 | — | unclaimed |
| 38 | 38:1 | 88 | 65,220 | — | unclaimed |
| 39 | 39:1 | 75 | 80,810 | — | unclaimed |
| 40 | 40:1 | 85 | 86,960 | 4 | unclaimed |
| 41 | 41:1 | 54 | 59,540 | — | unclaimed |
| 42 | 42:1 | 53 | 57,830 | — | unclaimed |
| 43 | 43:1 | 89 | 71,260 | — | unclaimed |
| 44 | 44:1 | 59 | 35,360 | — | unclaimed |
| 45 | 45:1 | 37 | 36,090 | — | unclaimed |
| 46 | 46:1 | 35 | 42,860 | — | unclaimed |
| 47 | 47:1 | 38 | 38,720 | — | unclaimed |
| 48 | 48:1 | 29 | 36,960 | 1 | unclaimed |
| 49 | 49:1 | 18 | 24,350 | — | unclaimed |
| 50 | 50:1 | 45 | 34,040 | — | unclaimed |
| 51 | 51:1 | 60 | 37,400 | — | unclaimed |
| 52 | 52:1 | 49 | 29,300 | — | unclaimed |
| 53 | 53:1 | 62 | 38,650 | — | unclaimed |
| 54 | 54:1 | 55 | 36,990 | — | unclaimed |
| 55 | 55:1 | 78 | 33,640 | — | unclaimed |
| 56 | 56:1 | 96 | 39,650 | — | unclaimed |
| 57 | 57:1 | 29 | 38,720 | — | unclaimed |
| 58 | 58:1 | 22 | 28,470 | 2 | unclaimed |
| 59 | 59:1 | 24 | 30,960 | — | unclaimed |
| 60 | 60:1 | 13 | 19,290 | — | unclaimed |
| 61 | 61:1 | 14 | 14,640 | — | unclaimed |
| 62 | 62:1 | 11 | 13,850 | — | unclaimed |
| 63 | 63:1 | 11 | 13,140 | — | unclaimed |
| 64 | 64:1 | 18 | 19,810 | 2 | unclaimed |
| 65 | 65:1 | 12 | 18,050 | 1 | unclaimed |
| 66 | 66:1 | 12 | 17,390 | — | unclaimed |
| 67 | 67:1 | 30 | 25,620 | — | unclaimed |
| 68 | 68:1 | 52 | 29,420 | — | unclaimed |
| 69 | 69:1 | 52 | 25,340 | — | unclaimed |
| 70 | 70:1 | 44 | 21,950 | — | unclaimed |
| 71 | 71:1 | 28 | 17,230 | — | unclaimed |
| 72 | 72:1 | 28 | 21,190 | — | unclaimed |
| 73 | 73:1 | 20 | 16,250 | — | unclaimed |
| 74 | 74:1 | 56 | 24,970 | — | unclaimed |
| 75 | 75:1 | 40 | 18,930 | — | unclaimed |
| 76 | 76:1 | 31 | 20,130 | — | unclaimed |
| 77 | 77:1 | 50 | 19,180 | — | unclaimed |
| 78 | 78:1 | 40 | 18,660 | — | unclaimed |
| 79 | 79:1 | 46 | 22,290 | — | unclaimed |
| 80 | 80:1 | 42 | 14,940 | — | unclaimed |
| 81 | 81:1 | 29 | 11,390 | — | unclaimed |
| 82 | 82:1 | 19 | 7,630 | — | unclaimed |
| 83 | 83:1 | 36 | 15,400 | — | unclaimed |
| 84 | 84:1 | 25 | 10,730 | — | unclaimed |
| 85 | 85:1 | 22 | 10,500 | — | unclaimed |
| 86 | 86:1 | 17 | 6,820 | — | unclaimed |
| 87 | 87:1 | 19 | 8,150 | — | unclaimed |
| 88 | 88:1 | 26 | 10,190 | — | unclaimed |
| 89 | 89:1 | 30 | 17,440 | — | unclaimed |
| 90 | 90:1 | 20 | 8,280 | — | unclaimed |
| 91 | 91:1 | 15 | 7,490 | — | unclaimed |
| 92 | 92:1 | 21 | 8,760 | — | unclaimed |
| 93 | 93:1 | 11 | 6,470 | — | unclaimed |
| 94 | 94:1 | 8 | 3,510 | — | unclaimed |
| 95 | 95:1 | 8 | 5,050 | — | unclaimed |
| 96 | 96:1 | 19 | 9,450 | — | unclaimed |
| 97 | 97:1 | 5 | 3,120 | — | unclaimed |
| 98 | 98:1 | 8 | 6,900 | 1 | unclaimed |
| 99 | 99:1 | 8 | 4,290 | — | unclaimed |
| 100 | 100:1 | 11 | 5,260 | — | unclaimed |
| 101 | 101:1 | 11 | 3,820 | — | unclaimed |
| 102 | 102:1 | 8 | 4,440 | — | unclaimed |
| 103 | 103:1 | 3 | 1,500 | — | unclaimed |
| 104 | 104:1 | 9 | 3,660 | — | unclaimed |
| 105 | 105:1 | 5 | 2,700 | — | unclaimed |
| 106 | 106:1 | 4 | 2,900 | — | unclaimed |
| 107 | 107:1 | 7 | 2,530 | — | unclaimed |
| 108 | 108:1 | 3 | 2,870 | — | unclaimed |
| 109 | 109:1 | 6 | 2,690 | — | unclaimed |
| 110 | 110:1 | 3 | 2,390 | — | unclaimed |
| 111 | 111:1 | 5 | 2,920 | — | unclaimed |
| 112 | 112:1 | 4 | 2,330 | — | unclaimed |
| 113 | 113:1 | 5 | 2,940 | — | unclaimed |
| 114 | 114:1 | 6 | 3,410 | — | unclaimed |

## Why parallel merges do not overwrite each other

- **Data**: `data/guidance_NNN.json` is one file per chapter and a chapter has at most one open claim (`tools/progress.py --check` enforces it). A merge only ever brings the chapters its run owns.
- **Runs**: each agent edits only its own `data/runs/<agent>.json`. Claims and batch logs merge as whole, disjoint files.
- **This file**: generated. Never hand-edit it; on conflict, re-run `python3 tools/progress.py --report` and take the result.
- **Cache version**: `sw-stamps.js` is append-only (one stamp per landed batch) and marked `merge=union` in `.gitattributes`, so stamps concatenate instead of colliding.
- **Tests**: `tools/tests/guidance-NNN.js` is per chapter and added by its owner; `guidance-range.js` discovers payloads on its own and needs no edits.

The full protocol is [`parallel.md`](parallel.md).
