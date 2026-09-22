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
   `verify_quotes.py`, `check_ik_quotes.py`, `factcheck.py` must all come back
   clean, and `sw.js` `CACHE_VERSION` must be bumped whenever the tafsir
   payload changes.

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
| **Insertion, ch 1 → 114** | **in progress — ch 1–50 done** | ascending order | ascending order |

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
| 24:37 | Ibn ʿUmar in the market when the *iqāmah* was called | `4e69d68` |
| 25:68 | Which sin is most serious — Ibn Masʿūd's three | `118d2b1` |
| 25:70 | The old man asking whether every evil deed can be repented | `118d2b1` |
| 26:224 | Kaʿb ibn Mālik asking how the poets verse applies to him | `aea9339` |
| 27:23 | Bilqīs; the palace built to frame the sun twice daily | `9c73908` |
| 28:52 | The seventy priests of an-Najāshī; Abū Umāmah at the Conquest | `cb482e6` |
| 29:8 | Why dutifulness follows tawḥīd; the gathering with the righteous | `be815db` |
| 30:4 | Abū Bakr's five-year wager, and why the verse says "three to nine" | `ad2109c` |
| 31:14 | Three glosses on "weakness upon weakness"; the 6:82 distress | `64b856f` |
| 32:16 | Muʿādh's question — the verse recited as one of the gates of goodness | `12605ca` |
| 33:39 | The task of conveying inherited by the community | `836da09` |
| 34:37 | Two reports on the upper rooms; what the answer leaves out | `6524bb0` |
| 35:37 | Sixty years; grey hair as the warner | `9bd355c` |
| 36:9 | Mujāhid and Qatādah on the enclosure; Ibn ʿAbbās's variant reading | `1e93c54` |
| 37:100 | Ibrāhīm's prayer as compensation for the people he left | `7c29d53` |
| 38:22 | What Ibn Kathir **declines** to tell — refusing unauthenticated Isrāʾīliyyāt | `e6a4048` |
| 39:56 | The man who killed ninety-nine; al-Ḥasan al-Baṣrī on the open call | `f235d48` |
| 40:43 | Qatādah vs as-Suddī on the idols; ʿĀʾishah and the grave | `4e000ae` |
| 41:23 | The three men under the Kaʿbah covering | `75f57e2` |
| 42:8 | The two books — names, fathers and tribes, closed to change | `69ca31f` |
| 43:58 | Ibn az-Zibaʿrā's devised argument, from Ibn Isḥāq's *Sīrah* | `d1a2d1e` |
| 44:11 | Ibn Masʿūd correcting the smoke reading; the famine years | `8a84f85` |
| 45:34 | What "We will neglect you" actually says | `719b62e` |
| 46:29 | The jinn were troubleshooting, not seeking a prophet | `0fb0b3a` |
| 47:23 | The sequence that produced the deafness — asking, receiving, refusing | `5c7dc9c` |
| 48:26 | The pride of ignorance was two phrases in a contract | `6184d66` |

### Chapters remaining

51 → 114.

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

### A pattern worth repeating: record what the source refuses

At 38:22 the most valuable thing Ibn Kathir offers is a **refusal** — he declines
to repeat the widely-told story of the two litigants because nothing
authenticated supports it, and says so plainly rather than retelling it with a
disclaimer. Where the source declines, record the decline. It teaches the reader
something about evidence that a paraphrase cannot.

### Shared Ibn Kathir blocks

Several verses share one Ibn Kathir record (e.g. 14:47 and 14:48 are byte-identical,
as are 15:94–99). **Place the evidence once**, at the verse the report actually
concerns — not at every verse in the range. `ik_targets.py` shows identical
`chars` columns for these; treat that as the signal.

### AUTOMATED: `scripts/editorial/check_ik_quotes.py`

The defect below happened **four times** (23:4, 25:70, 27:23, 3:2) before it was
automated. It is now a check, not a habit to remember:

    python3 scripts/editorial/check_ik_quotes.py      # RESULT: PASS

It scans every paragraph mentioning Ibn Kathir and verifies each quotation
against `ayah_en`. Quotations that were already non-verbatim at the pre-work
baseline `1a3067d` are reported separately and do not fail the check — churning
pre-existing content is against the standing rule.

**Run this after every batch.** `verify_quotes.py` does *not* catch this class:
it only checks wordings that `add_verse_quotes.py` attached, not ones written by
hand into a new paragraph.

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

---

## 7. Pass two — full-verse integration (rules: `SECOND_PASS_RULES.md`)

Pass one inserted ~1 evidence per chapter (ch 1–50 done). Pass two re-reads
**every verse from 001 → 114** and adds whatever verse-aligned Ibn Kathir
evidence the section still lacks, restructures each section to **≥2 headings**,
and leaves the whole file coherent. Progress tracked here, separately from §5.

### Pass-two insertions completed

| Chapter | Verses touched | Evidence added | Commit |
|---|---|---|---|
| 1 | 1:1–1:7 + intro | Names (Tirmidhi Sahih Umm al-Qur'an, Bukhari, Ibn Jarir umm), two lights (Muslim/Nasa'i Ibn Abbas), prayer incomplete + behind-imam (Muslim Abu Hurayrah); basmalah opinions map + aloud reports (Umm Salamah, Mu'awiyah, A'ishah) + Bismillah virtues (Ahmad rider, Nasa'i Usamah, wudu Hasan, Muslim eating) + 99 Names (Two Sahihs); Jarir on hamd + Umar/Ali + Ibn Abbas + 4 hamd virtues; Rabb/Alamin map (Farra, Zayd, Qatadah, Qurtubi, 26:23-24, alamah); womb hadith (Tirmidhi Sahih) + 33:43 + Qurtubi warning/encouragement (15:49-50, 6:165, Muslim); Owner/King (59:23, king-of-kings, 2:247, 18:79, 5:20) + Yawm ad-Din (Ibn Abbas) + reckoning (37:53, wise, Umar, 69:18, Two Sahihs proclamation); kaf speech-change + Ubadah + Salaf secret + ibadah + 11:123/67:29/73:9 + Dahhak/Qatadah + objective/tool + Abd missions (18:1); firmness (4:136, 3:8) + Tabari sirat usage + 16:121/37:23 + parable chain (Ahmad/Nawwas); 4:70 + Adi bin Hatim chain (Ahmad/Tirmidhi Hasan Gharib) + 5:60 + Zayd bin Amr + surah summary. Fixed 2 pre-existing non-verbatim quotes (40:16, 6:153). 3 headings × 7 verses. | `50d7e2a` |
| 2 (batch A) | 2:1–2:12 | Verse-aligned IK evidence, 15 new refs (see commit body for per-verse detail). | `d4a1aed` |
| 2 (batch B) | 2:13–2:24 | Verse-aligned IK evidence, 13 new refs + 4 structural repairs. | `492c16e` |
| 2 (batch C) | 2:25–2:36 | Verse-aligned IK evidence, 15 new refs + 6 structural repairs. | `92a288f` |
| 2 (batch D) | 2:37–2:86 | Verse-aligned IK evidence, 34 new refs + 10 structural repairs. | `01a8a0a` |
| 2 (batch E) | 2:87–2:136 (95/123/131 checked, nothing missing) | 46 new H2s, all Quran wordings verbatim from ayah_en: succession/Spirit roster (87), qalil debate (88), Mu'adh+Bishr→Sallam (89), wrath pairs+Bawlas (90), 2:146 (91), 7:133 (92), Qatadah love-chain + worst deed (93), wish-cost + Abu Ubaydah (94), Iblis parallel (96), Ibn Salam 3Q+flip (97), couriers on command (98), unlettered informant (99), Malik denial (100), Asaf book (101), Harut/Marut angels + Bazzar soothsayer (102), 28:80 (103), Rifa'ah + imitation (104), sever-friendship (105), Naskh denial + precedents (106), kingdom gloss (107), Rafi'/Wahb + Mughirah + Hajj-3x (108), Ka'b + abrogation roster + Usamah (109), 40:52 (110), wishes gloss (111), two conditions + 25:23/18:110 + fear/grief (112), Rafi' + 4 views + 22:17 (113), 8:34/9:18/9:28 + Mina + Busr (114), exile/qiblah/traveler (115), 6:101 + 19:90-91 + qudsi + patience (116), 54:50 + bid'ah (117), Rafi' + file parallels (118), 13:40/50:45 + Torah portrait (119), Jarir/Qatadah + victors (120), remnant portraits + hear-of-me (121), envy (122), model profile + fitrah (124), 3:97/24:36 (125), 17:20/11:102/14:39 + Abu Shurayh (126), 23:60 + Wuhayb + Black Stone (127), I shall do that + 3 deeds (128), supplication named (129), hanif breaks + 3:68 (130), enduring word + die-as-lived (132), witnesses + 3:83 (133), lineage (134), Ibn Suriya (135), Hebrew Torah + Fajr (136). Defects repaired: 2:87 (17:85), 2:97 (Daniel refs), 2:102 (label), 2:127 (Baca gloss), 2:108 (Muslim 2358), 2:121 (subject-split), 2:125 H4, spacing/grammar (92/93/101/102/103/104/110/112/113/115/117/122/123/124/128/130/131/135/136/168). All 50 verses ≥2 H2. | `44130ae` |
| 2 (batch F) | 2:137–2:186 (137/139/141/147/162/172/175/176 checked, nothing missing) | ṣibghah chain + 11-roster + 30:30 (138); Ḥasan testimony-content, H3 rewritten (140); 3 envies (ʿĀʾishah/Aḥmad) + H3 rewritten (first-naskh, 2:106, knowledge-rule, Anṣār-ʿAṣr) + first-ʿAṣr/rukūʿ-turns H5 (142); wasaṭ=ʿadl + Nūḥ/prophet-two (Abū Saʿīd) + ʿUmar 4→3→2 + heels/9:124-125/two-qiblahs + faith-not-lost/double-reward/captive-woman H5 (143); majority-reading H2 + shaṭr/exceptions H3 + foreknowledge H4 (144); proof-against-knowers (145); ʿUmar↔Ibn Salām (146); every-nation-qiblah H2 + flesh-scatter (148); pleasure-upgrade (149); Jews-knew/Arabs-liked + Quraysh-exception H2 + comparative guidance (150); Jāhiliyyah→awliyāʾ + 14:28 + favor-means-Muḥammad + Mujāhid bridge (151); Ḥasan exchange-gloss + thanks/14:7 H2 (152); three-patiences/33:44 H2 (153); not-returned ending + Kaʿb believers-share H2 (154); 47:31 + wealth/lives/fruits H2 + Bukhārī-1283 fix (155); Umm Salamah sequel (156); safety + heights (157); orphan pulled inside → hesitation H3 + practice H4 (158); occasion + bridle-fire H2 + drought/trio (159); callers-extension (160); cursing-line + Qunūt (161); Greatest-Name (Tirmidhī 3478/Abū Dāwūd 1496/Ibn Mājah 3855) (163); 36:40 + 11:6 + winds (164); nidd back-ref (165); 28:63/34:41 + asbāb + 34:32-33 (166); 6:28 + regrets H2 (167); no-harm + footsteps/vows + 35:6 (168); innovator-scope (169); Jews-occasion (170); 9-roster + 16:60 (171); 5:96/two-and-two/Salmān + feast-ruling + necessity H5 (173); concealment economy (174); east/west H2 + charity H2 (3:92/76:9/59:9, miskīn, wayfarer) + prayer/alms/pledges H2 + battlefield roster (177); Nadir/Qurayẓah H2 (5:45, Bukhārī/ʿAlī, Ḥanafī, Ṣanʿāʾ, Aḥmad) + pardon-file (178); Abū al-ʿĀliyah + roster (179); two-nights + heir-bar chain/fourth + abrogation verdict (180); reward-preserved (181); error-examples (182); those-before H2 + shield (183); numbering + stages/scope/tharīd (184); scriptures-dates + ease-chains + travel-rulings + takbīr (185); three-answers/hastiness + battle-setting + divine-saying + fast-supplication H2 (186). Defects repaired: 140 H3 (dangling senses), 142 H3 (broken quote), 144 H2 (missing majority) + H3 (filler trim), 155 (1283 dangle), 156 H3 (unfinished ending), 158 (post---- orphan). 36 new refs, all verbatim. All 50 verses ≥2 H2. | `f172b05` |
| 2 (batch G) | 2:187–2:236 (no SKIPs, all 50 touched) | 187: Qays/Barāʾ hardship + Garment-H2 + seek-ordained/16-roster + Sahl threads (Bukhārī) + iʿtikāf-total + last-ten + suḥūr (Anas) + junub-dawn; 188: indebted-man + Umm Salamah arguer (Two Ṣaḥīḥs); 189: moons 3-uses + Back-door-H (Barāʾ/Bukhārī) + taqwā; 190: first-fighting-verse + Ḥasan list; 191–192: Abū Mālik ranking + sanctuary + energy-parity + pardon; 193: fitnah=shirk/9-roster + unjust-gloss; 194: 7 occasions + likeness-justice + Jābir/Aḥmad + Ṭāʾif + iḥsān; 195: Ḥudhayfah spending (Bukhārī) + Abū Ayyūb-H (Aslam/Constantinople) + Barāʾ raiding; 196: finish-started + Ḥudaybiyyah + prevention-wider + hady-sheep + tamattuʿ + hady-less-fast + Farewell-tamattuʿ + Kaʿb + ten-emphasis; 197: months-bind-iḥrām + months-named + faraḍa + Rafath-H + fusūq/15 + jidāl/20 + Provisions-H; 198: ʿUkāẓ-scruple + ʿArafāt-H + standing-pillar + Ibrāhīm-naming + Ḥums + remembrance-ruling; 199–200: Jāhiliyyah-chants + bedouin-rain + praised-prayer + Anas-duʿāʾ + worker-report; 201–203: Tashrīq-counting + takbīr-form + gathering-frame; 204–205: oath-glosses + aladd/ludda + Akhnas + Nawf + saʿā; 206: counsel-refusal; 207: seller-occasion/6 + ʿUmar/Hishām; 208: silm=Islam + footsteps; 209: slide-back; 210: coming=Resurrection + Moses-signs; 211: Quraysh-alteration (14:28–29); 212: beautification + above-them + without-reckoning; 213: ten-generations + last-first + by-leave; 214: baʾsāʾ/12 + Khabbāb-shaking; 215: charity-dating + good-known; 216: jihād-reach + hateful + perhaps-dislike; 217: Jundub-expedition + Ibn Isḥāq + Rajab-placing + ranking; 218: triad-biography + sequel; 219: khamr-definition + staircase + ʿafw-surplus; 220: orphan-occasion + mixing-brotherhood; 221: general-scope + 8-roster + Ṭabarī-ijmāʿ + Ḥudhayfah-letter + Zayd-asymmetry + Ibn ʿUmar/Bukhārī + 4-reasons + righteous-wife + 60:10 + invite/by-leave; 222: Anas-occasion + Usayd/ʿAbbād + fondling-file + Masrūq-ʿĀʾishah + Maymūnah-izār + Ibn Saʿd + bath/tayammum + blood/water + farj + Names; 223: pregnancy-place + one-valve + anal-file (Khuzaimah/Tirmidhī/Dārimī/Mālik/10-roster) + Jābir cross-eyed + Umm Salamah-full + Nāfiʿ-vindication + Bismillah + Bukhārī-duʿāʾ + meeting/tidings; 224: 24:22 + persisting-ḥadīth + Ibn ʿAbbās + 17-roster + Abū Mūsā + Abū Hurayrah; 225: laghw-habit + Lāt/ʿUzzā + angry/prohibit-allowed + Anṣārī-brothers/ʿUmar + knowing-lie + 5:89; 226: īlāʾ-durations + ʿĀʾishah-29 + fayʾa-roster + no-auto-divorce file; 227: resolve-rule; 228: qurūʾ-rosters (12+19) + ʿUmar-bath-case + Fāṭimah/Mundhir + concealment-file + Jābir-Farewell + Bahz + Wakīʿ + darajah + 4:34 + Names; 229: abrogation + retain-gloss + triple-at-once + 4:19/4:4 + Thawbān + Thābit/Ḥabībah (Mālik/Bukhārī) + khulʿ-ʿiddah + limits-ḥadīth; 230: ʿusaylah + Rifāʿah-full + taḥlīl-file + reunion-honor; 231: 8-roster + witnesses + Hikmah=Sunnah + jest-file; 232: walī-rule + Maʿqil-full + vow-expiation; 233: taḥrīm-2-years + ʿĀʾishah-dissent + 65:7 + ḍarar-file + heir + fiṭām-consult; 234: Ibn Masʿūd/Barwāʿ + Subayʿah + embryology-wisdom + kohl-case + Jāhiliyyah-year; 235: hint-wordings + Fāṭimah b. Qays + 28:69/60:1 + secret-pact + contract-void; 236: touched=congress + Umaymah/Bukhārī. Defects repaired: 196 (fidyah), 218 H1 (2:16→2:216), 222 H1 (Qur'an 15:19 wording misattributed to Leviticus), 235-H6 blank (+3 pre-existing missing blanks fixed by insertion). 124 insertions + 6 new H2s, 60 new citations, all verbatim. All 50 verses ≥2 H2. | `8d08458` |
| 2 (batch H) | 2:237–2:286 (no SKIPs, all 50 touched; per-H SKIPs where covered) | 237: not-Mutʿah/agreed-half + wife-remit/16-roster + knot=husband (ʿAmr b Shuʿayb) + remit-nearer + liberality/Seer; 238: dearest-deed (Two Ṣaḥīḥs/Ibn Masʿūd) + qunūt-file + ʿAṣr-majorities/Dumyāṭī-roster + ʿAlī-Aḥzāb + Samurah + miss/cloudy; 239: intense-fear (Mālik/Nāfiʿ) + 4/2/1 + Awzāʿī/Makḥūl + Anas-Tustar + 4:103 + 4:102-defer; 240: ʿUthmān-collect + 4:12-abrogation + pregnancy + 7-roster + 7m20d + ʿAṭāʾ + Farīʿah; 241: Ibn-Zayd-occasion + every-divorced (Saʿīd/Jarīr); 242: kadhālika/taʿqilūn; 243: resurrection-proof + destiny + Dawardān/4000/Ezekiel + Sargh; 244: fixed-terms + Khālid + 3:168 + 4:77–78; 245: night-descent + 2:261 + widen/narrow; 246: Samuel + Wahb-file + driven/turned glosses; 247: soldier/Judah + water/dyer + not-on-my-own + king-qualities + Authority/Wāsiʿ-ʿAlīm; 248: Ṭābūt-return + sky-carrying/Shamʿūn + sakīnah-glosses + relic-rosters; 249: scholars-strengthened + 80000/Sharīʿah/quenched + Barāʾ-310; 250: pour/firm/victory; 251: sling + Ṭālūt-promise + transfer/ḥikmah; 252: conform + emphatic; 253: 17:55 + slap-file/resolution + spoken-to/degrees + proofs/Spirit + decree; 254: rush + gold + 23:101 + ʿAṭāʾ-Dīnār; 255: Ubayy-tongue + Ghoul + Greatest-Name/20:111 + ten-sentences/30:25 + Abū-Mūsā-4 + servants/19:93–95 + 53:26/21:28 + Throne-ḥadīth + 19:64/20:110 + Kursī/ring + 13:9 + Salaf-rule; 256: plain-clear + Anas-invitation + Anṣār-occasion + shun/ʿUmar-Jibt + Ibn-Salām-dream; 257: peace-paths + Shayṭān-beautifies + 6:153/6:1/16:48; 258: Nimrod-lines + 4-kings + heart + Creator-proof + IK-correction + sunrise + 28:38 + unjust-stripped + after-fire; 259: eyes-first + sun-thought + table + ʿUzayr-ID + Jerusalem + 70-years + nunshiz/nunshir + Suddī-donkey + eyewitness; 260: Nimrod-sequel + seek-certainty + ṣurhunna-roster + Ibn-ʿAbbās-birds + ʿAzīz-Ḥakīm + hope-chains; 261: obedience/jihād + grows + camel-700 + fast-range + sincerity/Wāsiʿ-ʿAlīm; 262: refrainers + Himself-rewards + horrors/offspring; 263: compassion-duʿāʾ + injustice-forms; 264: Abū-Dharr-trio + insufficient + pretends + ṣafwān/wābil/dust; 265: iḥtisāb + rabwah/ṭall/never-barren; 266: ʿUmar-session + ʿAwfī-parable + Ḥākim-duʿāʾ + 29:43; 267: pure-best + Barāʾ-smugglers + debt-scene + gap/22:37; 268: lammah + contest-glosses; 269: Qurʾan-literacy + two-envies + ulūʾl-albāb; 270: perfect/tremendous + dated-helplessness; 271: imitation-exception + reader-parable + seven-shade + rank/expiation + custody; 272: Nasāʾī-occasion + Ḥasan/ʿAṭāʾ + three-nights; 273: good-minds/47:30 + miskīn + ūqiyah + emigrants/4:101/73:20; 274: household + Saʿd/wife's-mouth + Abū-Masʿūd + 2:38; 275: insane-seized + blood-river + defiance + mother-mercy + fences (mukhābarah/Jews-fat/curse-4) + ʿUmar-3 + Nuʿmān/shepherd + last-verse + 70-types + conquest-amnesty + proof-established; 276: stripped/tormented + 5:100/8:37 + ends-less + kaffār-athīm + date-terms; 277: praise-file; 278: Thaqīf/Makhzum/ʿAttāb + watching/still-owed; 279: take-up-arms + ruler-duty + exact-capital + Farewell-wording; 280: Jāhilī-ultimatum + day-pricing + Abū-Qatādah-shade + Ḥudhayfah-lenient; 281: ending-advice + last-verse (Nasāʾī); 282: last-from-Throne + salam + abrogation-view + scribe-charity/bridle + dictation-tiers + money-scope + Muslim-women + Khuzaymah + trust-file + summons-tiers + both-ways-harm + 8:29/57:28; 283: no-paper + Anas-shield + twin-sins + 5:106/4:135; 284: no-secret + 3:29/20:7 + hard-fall + self-talk/intentions + abrogation-narration; 285: Oneness/no-differentiation + heard-implemented; 286: kindness/abrogating-answer + ledger + petition-glosses/I-shall/I-did + Ḥanīfiyyah + three-needs + Mawlā/victory + Muʿādh-āmīn + virtue-trio. Defects repaired: 249 H1 (Qurʾan 7:4–7 wording misattributed to Judges 7:4–7). 117 insertions + 1 repair, 0 new H2s, 47 new citations, all verbatim. All 50 verses ≥2 H2. | `0906cb1` |
| 3 (batch I) | 3:1–3:50 (SKIP 1, 2, 5, 22, fully covered; per-H SKIPs where covered) | 105 insertions + 2 new H2s (v34 Chosen Households, One From Another; v35 So Accept It From Me); 24 new refs (2:116, 3:59, 3:123, 4:82, 5:51, 6:124, 7:53, 8:42, 8:73, 12:36, 12:98, 12:100, 12:108, 17:21, 21:23, 25:1, 28:7, 40:52, 43:31, 43:32, 43:59, 54:50, 60:1, 89:22), all verbatim. All 50 verses ≥2 H2. | `43e710d` |
| 3 (batch J) | 3:51–3:100 (v51 shared block placed at v50; per-H SKIPs where covered) | 68 insertions + 5 new H2s (v68 My Friend Among Them Is My Father Abraham; v74 Chosen for Mercy; v77 Four Reports on the False Oath; v89 Kindness to the Repentant; v91 Asked Less and Easier); 5 blank-line repairs (vv79, 86); 22 new refs (2:97, 2:125, 2:177, 3:92, 4:18, 4:159, 9:29, 13:34, 14:31, 16:36, 16:48–50, 16:123, 17:79, 19:21, 19:34–35, 21:25, 21:29, 24:55, 26:88, 29:67, 39:38, 43:45, 66:5, 76:8, 106:4), all verbatim. All 50 verses ≥2 H2. | `ed0e0ab` |
| 3 (batch K) | 3:101–3:150 (SKIP v132, no IK gloss; per-H SKIPs where covered) | 92 insertions + 2 new H2s (v129 Never Asked About What He Does; v133 Where Is the Fire Then?); 9 blank-line repairs (vv118, 120, 145–147); 19 new refs (2:214, 2:274, 3:112, 3:199, 5:79, 6:2, 8:9, 8:62–63, 9:25, 9:104, 13:40, 17:18–19, 29:2, 35:11, 42:20, 47:4–6, 55:54, 57:8), all verbatim. All 50 verses ≥2 H2. | `ad272dc` |
| 3 (batch L) | 3:151–3:200 (SKIP v182, gloss carried at 181; per-H SKIPs where covered) | 151: good-news-terror + Jābir-five (Two Sahihs); 152: fulfilled/Fashiltum + Barāʾ-full (Bukhārī) + Zubayr/Hind + Anas-b-Naḍr; 153: Tuṣʿidūna/Suddī-rock + grief-file + defense-file (Ṭalḥah/Saʿd/Ubayy/67:11/Sahl); 154: Abū-Ṭalḥah-sword + Zubayr-dream + hypocrites/48:12/Muʿattib + destiny; 155: Salaf-maxim + ʿUthmān-file (Aḥmad/Shaqīq) + pardon; 156: hypocrites-gloss + false-creed; 157: qualifier-yield + short-delights; 158: return-sorts; 159: soft-gift + entrusted (Ibn-Mājah) + campaign-consultations + trust; 160: 3:126-parallel + trust-condition; 161: red-robe-exoneration + ghulūl-file (Luṭbiyyah/Muʿādh/necks/Khaybar); 162: 28:61 + 13:19-bare; 163: grades/degrees/compensate; 164: 30:21/25:20/12:109/6:130 + reciting/purifying/Book-Sunnah; 165: seventy-arithmetic + ʿUmar-ransom + archers-roster; 166: will/decree + patient-firm; 167: stages + Ibn-Ubayy-withdrawal; 168: sitters/Mujāhid-Jābir + ward-off-death; 169: green-birds (Muslim/Masrūq) + Anas + Ibn-ʿAbbās-Uḥud + Jābir-father + river-tents + believer-bird (3-Imāms); 170: rejoice + Biʾr-Maʿūnah-70; 171: Ibn-Isḥāq + Ibn-Zayd; 172: Ḥamrāʾ + ʿIkrimah + ʿĀʾishah-70; 173: threat/trust + Mardawayh-Anas + Ibrāhīm-fire; 174: relied + Bayhaqī-caravan; 175: 39:36/4:76/22:40/47:7/40:51 + 58:19/58:21; 176: eager-grief + no-portion; 177: exchanging + NEW-H2 self-harm/painful; 178: 23:55-56/68:44/9:85-remainder; 179: 72:26-27 + Uḥud-sorting (Mujāhid/Qatādah) + obey/reward; 180: miser-ledger + 57:7-trust + snake-file; 181: record/taste + 2:245-occasion; 183: fire-rite-refuted + why-kill; 184: precedent-comfort + Zubur/Munīr; 185: 55:26-27 + Ever-Living + whip-place + 87:16-17/28:60 + finger-sea + Qatādah; 186: Usāmah-file + 2:155/degree + determining-affairs; 187: covenant-chastisement + scholar-warning/bridle; 188: show-off-file + two occasions; 189: Owner/Most-Able; 190: sky-earth-catalog + 12:105-106 + Maymūnah-night + ʿĀʾishah-weeping; 191: ʿImrān-postures + contemplate/purpose/salvation; 192: disgraced/no-helpers; 193: caller=Messenger + forgive/cover/Abrār; 194: promise-gloss + before-creation; 195: Umm-Salamah-occasion + emigration-file + 60:1/85:8 + debt-ḥadīth + Garden-drinks; 196: 10:69-70/31:24/86:17 + 28:61-bare; 197: brief/worst-rest; 198: entertainment/Abrār + Abū-Dardāʾ; 199: Najāshī-file + 5:82/5:85 + 2:121/7:159/17:107-109 + swift-reckoning; 200: Ḥasan-command + Muʿādh-charge + ʿUmar-letter + Ribāṭ-file (Sahl/Salmān/Faḍālah/two-eyes/dīnār/Ibn-Mubārak). Defects repaired: 156 (after-header blank), 157 (before-header blank), H-blanks 152×2/159×3/164×2/165×2/167×2/179×2/181×2/185×2/186×2/193×2/195×2/198×2 (27 total). 84 insertions + 1 new H2, 35 new citations, all verbatim. All 50 verses ≥2 H2. Closes sūrah 3. | `778b9a1` |
| 4 (batch M) | 4:1–4:50 | 143 insertions + 1 repair (stray "040" artifact in v21 para); 52 refs touched (2:88, 2:104, 2:111, 2:134, 2:188, 2:228, 2:229, 2:233, 3:24, 4:4, 4:20, 4:23, 4:31, 4:40, 4:48, 4:64, 4:110, 4:127, 4:176, 5:18, 5:91, 6:23, 6:151, 6:158, 9:38, 9:60, 16:89, 17:23, 17:32, 21:47, 24:61, 25:68, 25:70, 31:13, 31:14, 31:16, 33:4, 33:21, 33:37, 33:40, 35:1, 36:8, 39:69, 40:84, 58:6, 59:18, 62:5, 78:40, 99:6, 100:6), all verbatim. All 50 verses ≥2 H2. | `51473ba` |
| 4 (batch N) | 4:51–4:100 | 124 insertions + 71 repairs; 32 refs touched (2:14, 2:195, 3:7, 3:152, 4:9, 4:48, 4:58, 4:73, 4:82, 4:83, 5:52, 6:151, 7:131, 8:26, 9:5, 17:100, 21:34, 22:11, 24:47, 24:51, 25:70, 31:21, 33:25, 39:53, 42:10, 42:30, 47:4, 47:13, 47:20, 47:24, 55:26), all verbatim (24:47 corrects IK's "22:47" typo). All 50 verses ≥2 H2. | `2d6bbd0` |
| 4 (batch O) | 4:101–4:150 | 115 insertions + 24 repairs (22 double-blanks, v102 header-after, v103 dashes-blank); 58 refs touched (1:6, 2:9, 2:20, 2:200, 2:201, 2:202, 2:283, 3:28, 3:68, 3:78, 3:135, 4:3, 4:11, 4:23, 4:48, 5:8, 5:52, 5:103, 6:68, 6:69, 6:164, 7:186, 9:36, 14:8, 14:22, 16:120, 16:123, 17:18, 17:21, 18:17, 18:53, 24:33, 28:86, 34:41, 35:10, 36:60, 37:22, 37:158, 40:51, 42:20, 42:41, 42:52, 43:19, 47:38, 53:19, 57:13, 57:15, 57:28, 58:18, 59:7, 61:5, 63:8, 64:6, 65:2, 68:44, 73:20, 99:7, 99:8), all verbatim. All 50 verses ≥2 H2. | `87a9f23` |
| 4 (batch P) | 4:151–4:176 | 71 insertions + 6 double-blank repairs; 39 refs touched (2:54, 2:56, 2:61, 2:88, 2:255, 2:285, 3:7, 3:55, 3:59, 3:93, 4:11, 5:17, 5:73, 5:75, 5:116, 5:118, 6:101, 6:146, 7:138, 7:143, 7:163, 7:171, 9:31, 14:8, 15:6, 17:90, 19:88, 19:93, 20:110, 20:134, 21:91, 22:26, 28:47, 40:60, 41:5, 41:42, 43:59, 45:13, 66:12), all verbatim. All 26 verses ≥2 H2. Closes sūrah 4. | `4732f05` |
| 5 (batch I) | 5:1–50 | 43 insertions + 38 repairs (32 HDR blanks, 6 heading blanks); 20 refs touched (13:25, 9:36, 2:217, 57:8, 9:29, 18:25, 45:16, 7:140, 2:143, 2:50, 2:84, 2:85, 5:95, 39:53, 5:48, 7:157, 5:68, 15:9, 12:103, 6:116), all verbatim. All 50 verses ≥2 H2. | `8d75b27` |
| 5 (batch J) | 5:51–100 | 29 insertions + 41 repairs (36 HDR blanks, 3 heading blanks, 2 missing `---`); 14 refs touched (14:19, 14:20, 3:28, 85:8, 17:82, 7:159, 35:32, 33:37, 13:40, 19:30, 5:116, 43:59, 57:27, 67:12), all verbatim. All 50 verses ≥2 H2. | `4e96532` |
| 5 (batch K) | 5:101–120 | 18 insertions + 38 repairs (17 HDR blanks, 14 heading blanks, 7 missing `---`); 7 refs touched (3:97, 15:92, 15:93, 28:7, 21:104, 37:61, 83:26), all verbatim. All 20 verses ≥2 H2. Closes sūrah 5. | `dbf0065` |
| 6 (batch Q) | 6:1–50 | 19 insertions + 47 HDR-blank repairs; 19 refs touched (15:14, 15:15, 52:44, 15:8, 25:22, 51:56, 11:17, 2:171, 8:23, 17:102, 27:14, 52:15, 36:70, 17:59, 78:40, 67:23, 10:31, 8:24, 13:19), all verbatim. All 50 verses ≥2 H2. | `2a6b3e0` |
| 6 (batch R) | 6:51–100 | 13 insertions + 47 HDR-blank repairs; 16 refs touched (23:57, 13:21, 18:28, 40:60, 46:11, 19:73, 19:74, 74:38, 3:91, 39:37, 8:50, 14:27, 21:30, 18:50, 19:44, 34:41), all verbatim. All 50 verses ≥2 H2. | `21b0934` |
| 6 (batch S) | 6:101–150 | 12 insertions + 50 HDR-blank repairs + 1 new H2 (v146 What Was Left of the Fat); 5 refs touched (19:95, 25:31, 9:31, 49:7, 10:99), all verbatim. All 50 verses ≥2 H2. | `b5741d5` |
| 6 (batch T) | 6:151–165 | 9 insertions + 15 HDR-blank repairs; 8 refs touched (4:116, 4:10, 2:220, 42:13, 2:130, 16:120, 21:25, 6:153), all verbatim. All 15 verses ≥2 H2. Closes sūrah 6. | `7b4ddd1` |
