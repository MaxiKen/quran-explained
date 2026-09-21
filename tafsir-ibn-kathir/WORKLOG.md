# Ibn Kathir Evidence Integration — Worklog

This folder holds the offline source text and the running log of the work that
uses it. Read this file first: it says what the task is, what rules govern it,
and how far the work has got.

---

## 1. What this task is

Insert genuine supporting evidence drawn from **Tafsir Ibn Kathir** into the
verse commentaries in `markdown commentry/NNN.md` — hadith, historical context,
background, and lessons — so that each verse carries more backup than it does
now.

The goal is **evidence, not volume**. A section that gains a well-attributed
report or a piece of revelation history is better than one that gains three
paragraphs of paraphrase.

## 2. The source

| | |
|---|---|
| Upstream | `https://github.com/spa5k/tafsir_api` → `tafsir/en-tafisr-ibn-kathir/` |
| Files | 114 JSON, one per surah, one record per ayah, keys `text` / `ayah` / `surah` |
| Downloaded | 114/114 files, 43 MB, all valid JSON |
| Cleaned to | `tafsir-ibn-kathir/001.txt` … `114.txt` (36.0 MB) |
| Coverage check | **114/114 surahs carry exactly one record per ayah, ayah numbers running 1…N in order, 6,236 records = the 6,236 verses in `data/`** |
| Cleaning applied | CRLF→LF, control chars stripped, trailing spaces, space runs, blank-line runs collapsed. No content altered. |
| Rebuild | `python3 scripts/editorial/build_ik_txt.py` |

An earlier candidate source (`SafhaJournal/tafsir-ibn-kathir-english`) was
downloaded and then **rejected**: its own `PROVENANCE.md` states the English was
machine-generated, and it carries no hadith numbers. It is not used here.

## 3. Rules that govern every insertion

1. **Never drop a reference.** Every `(chapter:verse)` citation present before an
   edit must survive it.
2. **Never invent a hadith number.** This edition cites by collection and
   narrator. Carry that attribution honestly; do not add a number that the
   source does not give.
3. **Never attribute to the Prophet ﷺ anything the source does not.** A witness
   account ("I saw the Messenger of Allah…"), a Companion's ruling, or a
   commentator's gloss is not a prophetic saying. When the speaker is unclear,
   leave the report out.
4. **No padding.** Simple English. If a section already makes the point, it
   needs no addition.
5. **Quote the phrase, not the verse.** Long verses are trimmed to the clause
   being discussed.
6. **Verify after every batch.** `integrity.py`, `build_tafsir_json.py`,
   `verify_quotes.py`, `factcheck.py` must all come back clean, and
   `sw.js` `CACHE_VERSION` must be bumped whenever the tafsir payload changes.

## 4. Why the work is not automated end-to-end

Mechanical placement was tried and failed, and should not be retried:

- A topic-word matcher over 604 already-vetted hadith produced 225 candidates;
  hand-reading the 9 tightest gave **9 false positives out of 9**.
- A broad `tawakkul` probe returned 68 hits and all 68 were ordinary prose.
- An automated "lesson/analogy" pass over 6,236 sections would be padding.

What does work is **verse-aligned extraction plus hand review**. Because the
source is one record per ayah, the Ibn Kathir text for `2:222` is *about*
`2:222`. That removes the guesswork that made topic matching unreliable, but the
wording and the attribution still need a human-equivalent check before they go
in.

## 5. Progress

| Stage | Status | Detail |
|---|---|---|
| Map source links | done | 114 JSON identified, 1 shared file avoided (per-surah files used) |
| Download | done | 114/114, 43 MB, 0 invalid |
| Verify coverage | done | 6,236 records = 6,236 verses, 0 gaps |
| Clean to `.txt` | done | 114 files, 36.0 MB |
| Commit source + log | done | this folder |
| Extractor (`ik_extract.py`) | done | pulls collection-attributed reports per verse |
| Formatter (`ik_format.py`) | done, conservative | rejects anything not a clean prophetic saying |
| **Insertion, ch 1 → 114** | **not started** | next step, ascending order |

### Insertions completed

_None yet._

### Chapters remaining

1 → 114 (all).

## 6. Verification log

| Run | Command | Result |
|---|---|---|
| — | `scripts/editorial/integrity.py` | 6,236 sections, 0 quote mismatches |
| — | `scripts/build_tafsir_json.py` | 6,236 verses, 19.70 MB |
| — | `scripts/editorial/verify_quotes.py` | RESULT: PASS |
| — | `scripts/factcheck.py` | `{'AUTH-REVIEW': 1830}` (known informational baseline) |

These are the results from before insertion work began. Re-run and re-record
after every batch.
