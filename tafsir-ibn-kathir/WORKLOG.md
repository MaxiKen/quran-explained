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
| **Insertion, ch 1 → 114** | **in progress — ch 1–23 done (28 insertions)** | ascending order |

### Insertions completed

| Verse | Evidence added | Commit |
|---|---|---|
| 1:4 | The silence of the Day (78:38, 20:108, 11:105) + Ad-Ḍaḥḥāk from Ibn ʿAbbās | `18613a3` |
| 1:6 | Aṭ-Ṭabarī on *ṣirāṭ*, the poet Jarīr ibn ʿAṭiyyah, 90:10, 7:43 | `18613a3` |
| 2:1 | "Do not turn your houses into graves" (Muslim, Aḥmad, at-Tirmidhī, an-Nasāʾī) + Ibn Masʿūd | `1f2ef71` |
| 2:7 | As-Suddī, Qatādah, Mujāhid via Ibn Jurayj, al-Aʿmash's hand demonstration | `1f2ef71` |
| 2:8 | *Asbāb an-nuzūl*: no hypocrites in Makkah; the pattern begins after Badr under Ibn Ubayy | `1f2ef71` |
| 3:2 | The Greatest Name report, Asmāʾ bint Yazīd, graded ḥasan ṣaḥīḥ | `c20deb3` |
| 3:4 | Najrān delegation, 9 AH — why the sūrah argues with Christians | `c20deb3` |
| 4:1 | Madinan provenance; Ibn Masʿūd's five verses he'd trade the world for | `65d128b` |
| 4:2 | As-Suddī on the "sheep for a sheep" fraud; eleven who called it a major sin | `65d128b` |
| 5:12 | The twelve leaders, and the twelve Anṣār at al-ʿAqabah | `0ffcfdf` |
| 6:2 | Al-Anʿām revealed whole at night with seventy thousand angels | `519ac70` |
| 7:2 | Mujāhid/Qatādah/as-Suddī on "do not let your breast be narrow" | `4ddba0e` |
| 8:1 | *Asbāb*: the Badr spoils dispute, ʿUbādah via Abū Umāmah (Imām Aḥmad) | `e01f088` |
| 9:2 | Post-Tabūk proclamation; Abū Bakr then ʿAlī sent; the missing *basmalah* | `746af56` |
| 10:2 | Aḍ-Ḍaḥḥāk from Ibn ʿAbbās on the objection to a human messenger; three readings of "rewards" | `f6dc8c7` |
| 11:1 | At-Tirmidhī: Hūd and its sisters turned the Prophet's ﷺ hair gray | `e306727` |
| 12:3 | Why a story was asked for; ʿUmar reading a borrowed book (Imām Aḥmad) | `301641a` |
| 13:13 | Abū al-Jald on *al-barq*; Qatādah on fear and hope; the Ghifār man's report | `2147868` |
| 14:47 | ʿĀʾishah and Thawbān on where people will be when the earth is changed | `777bac0` |
| 15:95 | Ibn Isḥāq names the five mockers; the supplication against Ibn al-Muṭṭalib | `89e38aa` |
| 16:69 | The honey report — al-Bukhārī and Muslim, from Abū Saʿīd al-Khudrī | `dd3a367` |
| 17:1 | The Miʿrāj: fifty prayers reduced to five, Mūsā's counsel | `47df9af` |
| 18:1 | Al-Barāʾ on the tranquillity that descended; the ten verses against Dajjāl | `a01aa52` |
| 19:96 | How affection reaches the ground — Ibn Abī Ḥātim's report citing this verse | `d9e436d` |
| 20:115 | Mūsā arguing with Ādam — decree against consequence | `8c78af0` |
| 21:96 | Yaʾjūj and Maʾjūj — the spear thrown at the sky as a trial | `ab6ec93` |
| 22:2 | ʿImrān ibn Ḥuṣayn on how these verses landed; the 999-in-1000 report | `821afc0` |
| 23:4 | Zakāt's chronology — Meccan principle, Madinan *nuṣub* | `8fd3be8`, fixed `8449a5a` |

### Chapters remaining

24 → 114.

### What the automation attempts produced

Four separate automated extractors were written and **all four were rejected**.
The last one rendered a witness account ("I saw the Messenger of Allah…") as a
prophetic saying, and a commentator's gloss the same way. Every attempt also
truncated quotations mid-word, because this edition places the English gloss
inside parentheses after the Arabic, so quote boundaries cannot be found
reliably.

The yield numbers were also misleading at first. A filter requiring
Arabic-free input matched only **64 of 6,236 verses (1.0%)**; stripping Arabic
before matching raised that to **1,252 (20.1%)**. The low figure was the
filter's bug, not the source's poverty.

Insertion is therefore done by hand, with `ik_review.py` as a reading aid.

### Real size of the remaining work

Measured on non-Qur'an evidence (hadith, named scholar, or revelation history) —
not on Qur'an cross-references, which nearly every section already carries:

```
sections with no non-Qur'an evidence : 4,940 of 6,236  (79.2%)
largest gaps                         : ch 26 (226), ch 2 (179), ch 37 (161),
                                       ch 6 (153), ch 3 (152), ch 7 (149)
```

## 6. Verification log

| Run | Command | Result |
|---|---|---|
| ch 1 (`18613a3`) | `integrity.py` | 6,236 sections, 0 quote mismatches |
| ch 1 (`18613a3`) | `verify_quotes.py` | **RESULT: PASS** — 0 not-verbatim, 0 lost, 0 added, 0 Bible-given-Qur'an-quote |
| ch 1 (`18613a3`) | `factcheck.py` | `AUTH-REVIEW: 1831`, traced to the new `Ḍaḥḥāk's report` phrase |
| ch 2 (`1f2ef71`) | `integrity.py` / `build_tafsir_json.py` | 6,236 / 0 mismatches · 19.71 MB |
| ch 2 (`1f2ef71`) | `factcheck.py` | `AUTH-REVIEW: 1832`, traced to `al-Aʿmash reported` |
| ch 3 (`c20deb3`) | `integrity.py` / `build_tafsir_json.py` | 6,236 / 0 mismatches · 19.71 MB |
| ch 3 (`c20deb3`) | `factcheck.py` | `AUTH-REVIEW: 1833`, traced to `Asmāʾ … said` |
| ch 4 (`65d128b`) | `integrity.py` / build / `factcheck.py` | 6,236 / 0 · 19.71 MB · `AUTH-REVIEW: 1835` |
| ch 5 (`0ffcfdf`) | `integrity.py` / build | 6,236 / 0 · 19.71 MB |
| ch 6 (`519ac70`) | `integrity.py` / build | 6,236 / 0 · 19.72 MB |
| ch 7 (`4ddba0e`) | `integrity.py` / build / `add_verse_quotes.py` | 6,236 / 0 · new 46:35 wording attached |
| ch 8 (`e01f088`) | `integrity.py` / build / `factcheck.py` | 6,236 / 0 · 19.72 MB · `AUTH-REVIEW: 1835` |
| ch 9 (`746af56`) | `integrity.py` / build | 6,236 / 0 · 19.72 MB |
| ch 10 (`f6dc8c7`) | `integrity.py` / build / `factcheck.py` | 6,236 / 0 · 19.72 MB · `AUTH-REVIEW: 1837` |
| ch 11 (`e306727`) | `integrity.py` / build | 6,236 / 0 · 19.72 MB |
| ch 12 (`301641a`) | `integrity.py` / build | 6,236 / 0 · 19.73 MB |

### Shared Ibn Kathir blocks

Several verses share one Ibn Kathir record (e.g. 14:47 and 14:48 are byte-identical,
as are 15:94–99). **Place the evidence once**, at the verse the report actually
concerns — not at every verse in the range. `ik_targets.py` shows identical
`chars` columns for these; treat that as the signal.

### CRITICAL: never quote Ibn Kathir's English as the verse wording

Found at 23:4 and fixed in `8449a5a`. Three quotations I inserted were taken from
**Ibn Kathir's** English (the Darussalam translation) rather than from the
translation this app ships (`ayah_en` in `data/chapter_NNN.js`). All three read
correctly and all three failed:

| ref | what I wrote | what `ayah_en` says |
|---|---|---|
| 6:141 | "but pay the due thereof on the day of their harvest" | "Eat of the fruit they bear and pay the dues at harvest" |
| 91:9 | "he succeeds who purifies himself" | "Successful indeed is the one who purifies their soul" |
| 91:10 | "he fails who corrupts himself" | "and doomed is the one who corrupts it" |

These are two translations of the same Arabic, so quoting Ibn Kathir produces
plausible text that is **not** the wording this app ships. Ibn Kathir's own
paraphrase of a verse is *evidence about* the verse; it is never a substitute
for the verse.

**Rule: when Ibn Kathir cites a verse, quote that verse from `ayah_en` — never
copy his rendering.** Then run `verify_quotes.py`, which checks every wording
against its verse and will catch this. It reported PASS after the fix.

### One editing trap worth recording

`markdown commentry/` uses **straight** quotes (`"`), not curly ones. An
`edit_file` whose `old_text` used curly quotes silently failed to match. Always
`repr()` the target span before editing.

**Note on `verify_quotes.py`.** Its check 2 is "no citation added versus the last
commit", so a batch that deliberately adds references reports FAIL until the
batch is committed. Re-run after committing to get the true PASS. This is the
guard working, not a defect.

**Note on `AUTH-REVIEW`.** It fires on any `<Name> <verb>` pattern, so it
matches `the Qur'an describes` and `Lord said` as readily as a real scholar
citation — chapter 2 alone has 64 such hits. The counter moving by one per
insertion is expected. Always diff `/tmp/factcheck_issues.json` to confirm the
new entry is your own sentence rather than a genuine problem.
