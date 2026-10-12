# Progress

**543 verses are authored** — 1:1–1:7, chapter 2 complete (2:1–2:286), **chapter 3
complete (3:1–3:200)** and **chapter 4:1–4:50** (50 verses, five ten-verse batches).

The 2026-10-12 run on `arena/9a23575f-quran-explained` added **4:1–4:50** in five ten-verse
batches (4:1–10, 4:11–20, 4:21–30, 4:31–40, 4:41–50; 75,040 planned words, 62,000+ finished words) — each batch generated from the packets, compiled,
gated, committed and pushed before the next generation started. `data/guidance_004.json`
now holds 50 verses at 358,040 bytes; `tools/verify_verse.py` 4 --all is 50/50 and
`guidance-range` 42/42. A duplicate-phrase bug in `tools/verify_verse.py` (lead walk out-of-order on verses with identical phrases like 4:12) was fixed to use `find` from `at`.

The previous 493-verse state was:

The third 2026-10-12 run on `arena/fbd3f4f3-quran-explained` closed the sūrah, adding
**3:164–3:200** (37 verses, 49,264 words) in four batches — 3:164–173, 3:174–183,
3:184–193 and the closing 3:194–200 — each batch generated from the packets, compiled,
gated, committed and pushed before the next generation started (commit chain `1ea32f9`,
`c7b8b31`, `b6fde27`, `02ad6c3`). With it **Āl ʿImrān is finished**: `data/guidance_003.json`
now holds all 200 verses at 1,400,147 bytes.

The second 2026-10-12 run on the same branch added **3:114–3:163** in five ten-verse
batches (3:114–123, 3:124–133, 3:134–143, 3:144–153, 3:154–163), the first added
**3:64–3:113** in the same five-batch shape (3:64–73, 3:74–83, 3:84–93, 3:94–103,
3:104–113; 61,313 words). The 2026-10-11 run on `arena/fec53650-quran-explained` added
3:14–3:63 in the same five-batch shape, and a preceding run on the same day completed
chapter 2 and added 2:49–2:98; the notes below for 2:49–2:98 still describe that loop,
which is unchanged.

The earlier account of the layer is kept for the record: the 2026-10-11 run added 2:49–2:98
in five batches of ten (2:53, 2:90 and 2:96 authored because their available material is
under their floor, 2:80 authored for the same reason although the plan does not mark it
authored-only, the other forty-six compiled straight from the packets). The first 48 verses of the surah
were compiled on 2026-10-10 straight
from the eight sets with `tools/compile_guidance.py`, then **rewritten the same day**
against the lead rule that landed with them: every verse now opens by walking its own
translation phrase by phrase (193–344 words of explanation, 22–46% of the entry), with
the evidence pushed down under the headings. Everything before them was cleared on 2026-10-09: chapter 1,
2:1–2:46 and the 2:6–2:28 pilot, all of it quote-stacked rather than explained.
`docs/style.md` is the spec; [`../AGENTS.md`](../AGENTS.md) is the entry point.

| | |
|---|---|
| Written | **543 of 6,236 verses** — 750,610 planned words (12.72%), every one at or over its floor |
| Source sets | **8** (six complete, al-Qushayrī on 1,287 verses, al-Wāḥidī on 431) |
| Planned words | **5,902,150** (A 2,937,900 · B 2,409,170 · C 555,080) |
| Resume at | **4:51** — next authored-only is 4:136 |
| Files | `data/guidance_001.json` (7), `data/guidance_002.json` (286), `data/guidance_003.json` (200), `data/guidance_004.json` (**50**); `_112.json` still a placeholder |
| Chapter 4 shape (4:1–4:50, this run) | leads 222–777w (20–42% of the entry) · 5 headings · `draws_on` 5–7 sets · entries 711–1563w |

`tools/progress.py --next` is authoritative and says the same: `python3
tools/progress.py --next`. Regenerate the plan itself with
`python3 tools/tier_verses.py`; never hand-edit `data/plan.json`.

## What changed under the last session

Two production modes now exist, both gated by the same check: **authored** prose,
and **compiled** splicing via `tools/verse_packet.py` + `tools/compile_guidance.py`
(see `docs/voice.md`). 18 verses were compiled and passed the gate; they were then
deleted, because they were written to the old, lower floors.

## Batched runs — what actually works

The maintainer defined a **run** as one go, with about **six batches** in it.
The pattern that works is: generate a batch → save to disk → extend the
harness range in the same change → run the suite → **push** → next batch.
Pushing per batch means a workspace reset costs at most one batch.

Measured across two runs: **ten batches, 30 verses, ~24,300 words**
(2:15–2:44, commits `a3e7dac` → `70cf9fe` → `0780489` → `7272617` → `dc7230f`
→ batch 6). That is roughly **810 words per verse** and **five to six batches
per run** at about **16,000–18,000 words**.

**The length rule is a FLOOR, not a band** (maintainer, 2026-10-09). A verse
may run long; it must not run short. The harness checks `n >= target * 0.75`,
against bands that were raised the same day — A 1,300–1,900, B 650–1,000,
C 300–450 — so the ~810 words/verse figure below is measured under the *old*
bands and is not a target any more.

Three verses had been trimmed under the old two-sided rule and have been
restored to their original length: **2:18 (393→524w), 2:31 (798→947w), 2:45
(734→818w)**. `tools/restore_trimmed.py` did it.

Auditing every authored surah against the new floor found a fourth problem —
**112:1 was 340w against a floor of 405**, written short in the original pilot
rather than trimmed. Expanded to 783w by `tools/expand_112_1.py`.

**No verse in any authored surah is now under its floor.** (True of the corpus as
it stood when written; the whole layer was cleared the same day, so it is now a
note about how the floor was audited, not a claim about the data.)

**Leave margin.** 2:54 first cleared its floor by exactly one word (939 against
938). That passes, but it is one edit away from failing, so it was expanded to
1,047w. When a verse lands within ~10% of its floor, expand it rather than
leaving it.

Applied in batch 12: 2:67 (58w margin), 2:68 (74w) and 2:70 (33w) all passed
but sat inside the 10% window, so all three were expanded — to margins of 204,
218 and 176 words respectively. **The floor report is not the only signal; read
the margin column.** The per-verse report in the authoring scripts now prints
a `pct` column and flags `TIGHT` under 10% as well as `SHORT`.

**Two distinct attribution failures to watch.** A named authority must appear
in *the block the verse is cited to*, not merely somewhere in that tafsīr.
Batch 13 cited al-ʿAwfī from Ibn ʿAbbās under 2:73; the report actually sits
in Ibn Kathīr's **2:74** block, where 2:74's commentary already used it — so
2:73 was both misranged and duplicating. `guidance-002.js` caught it. When a
report has to move, check whether the destination verse already covers it.

**The authority check also catches ordinary capitalised nouns.** Batch 16 wrote
"Two Muslims from Banū Salamah" in 2:89; the harness read the capitalised
*Muslims* as a cited authority and failed the verse, because `muslim` appears
nowhere in 2:89's source blocks. Rephrase to "two men from…" rather than
adding the word to `NAMES` — `NAMES` is for scholars and transmitters, not for
group labels.

Batch 18 tripped the **same check for the opposite reason**: 2:100 and 2:101
named ʿAbdullāh ibn Salām, who appears only in Ibn Kathīr's **2:97–98** block.
A genuine person, correctly named, cited to verses whose sources do not
contain him. Replaced with the sūrah's own cross-references ("a few of you" at
2:83, "a few of them" at 2:88). **The check is about range, not existence** —
a name can be entirely real and still fail if it sits outside the cited
block.

Verses that came out *under* target were expanded and stay expanded — 2:10,
2:14, 2:35, 2:43, 2:48.

**Every batch needs three things done together or the suite lies:**
1. the new verses written into `data/guidance_002.json`;
2. `HI` in `tools/tests/guidance-002.js` widened to match, plus the
   fallback-control verses moved past the new range;
3. any newly named authority added to the harness's `NAMES` list.

**Two traps hit this run:** an apostrophe inside a single-quoted JS string
(`'violate Allah's covenant'`) breaks the harness silently until `node
--check`; and translation fragments must be copied from `ayah_en` verbatim —
the app writes **Iblîs** with a circumflex, and a fragment reading `Iblis`
fails. Run `node --check` before the suite.

## The 50-verse target is still not being met

The standing instruction is **more than 50 verses per run**. The best run so
far delivered 23.

The reason is arithmetic, recorded so it is not re-litigated: 2:8–57 is 50
verses and **41,630 planned words** (34,150 even at the absolute floor of each
tier band). Measured output is ~4,700–5,400 finished words a session. The two
figures are about 6× apart, and no working method closes that gap.

The gap is also incompatible with the maintainer's own 200-word floor: 50
verses at 200 words is 10,000 words, still roughly double one session's output.

**Options, in order of preference:**
1. Lower the tier bands (one line — `BAND` in `tools/tier_verses.py`) so that
   50 verses fits. At ~100 words a verse the target is reachable but falls
   below the stated floor.
2. Accept ~7–14 verses a session at the current quality standard.
3. Split the work across parallel sessions on different sūrahs.

This needs a maintainer decision. Until then, keep authoring to the standard
in `docs/voice.md` and report the shortfall plainly each session rather than
padding verses to hit a count.

## Batching instruction

**More than 50 verses per session, stopping at a good place past 50.** See
[batching.md](batching.md) for the standing instruction verbatim and the honest
note about throughput — sessions so far have delivered 4–7 verses, so a session
that cannot reach 50 must say so plainly rather than shipping thin commentary.

## Commit chain

```
317b7e7  Integrate Tafsīr as-Saʿdī (Arabic)
a4507ce  Replace as-Saʿdī with Tafsīr Ibn Kathīr (English)
1056a5b  Carry six complete English tafsirs on every verse (1.92x content)
6547b4e  Add ATTRIBUTION.md and surface commentary provenance
5cd9de5  Author an integrated single-voice commentary; pilot on Sūrah 112
77d0e39  Classify every verse into three commentary tiers, fitted and verified
5bfc52f  Author chapter 1: al-Fātiḥah, all seven verses
4bb405c  Make the authored files reviewable; label the generated ones
c833757  Keep plan.json minified (1 MB display limit)
4c68ff1  Author chapter 2, verses 1-7
3d0923e  Pick the fallback control sūrah dynamically
```

Branch `arena/525a7113-quran-explained`, pushed; no open PR — the layer is empty,
so there is nothing to merge until a batch is generated.

**The session this handoff was written in also reset the workspace once.** It
was recovered with `git fetch` + `git reset --hard` from the pushed branch.
See [pitfalls.md](pitfalls.md#the-workspace-can-be-reset).

## Verification state (after 4:50, 2026-10-12)

`verify_verse 4 --all` **50/50** · `verify_verse 4 --range 1-10` **10/10** · `verify_verse 4 --range 11-20` **10/10** · `verify_verse 4 --range 21-30` **10/10** · `verify_verse 4 --range 31-40` **10/10** · `verify_verse 4 --range 41-50` **10/10** ·
`verify_verse 3 --all` **200/200** · `verify_verse 2 --all` **286/286** · `verify_verse 1 --all` **7/7** ·
`style-check` **9/9** · `sets-integrity` **12/12** (6,236 verses) · browser harness against `tools/serve.py`
on :8090 — `guidance-range` **42/42**, `sources-all` **30/30**, `guidance-001` **52/52**.
Every batch was gated the same way before its push; the numbers above are the
final payload (50 verses, 358,040 bytes, `sw.js` v1.7.0-4-50).

Previous state (after 3:200, 2026-10-12): `verify_verse 3 --range 164-200` **37/37** · `verify_verse 3 --range 114-163` **50/50** ·
`verify_verse 3 --range 64-113` **50/50** · `style-check` **9/9** ·
`sets-integrity` clean (6,236 verses) · browser harness against `tools/serve.py`
on :8090 — `guidance-range 3` **11/11**.
Every batch was gated the same way before its push; the numbers above are the
final payload (200 verses, 1,400,147 bytes, `sw.js` v1.6.9-3-200).

The earlier 2026-10-11 line is kept for the record: `verify_verse 3 --all`
**63/63** · `verify_verse 3 --range 14-63` **50/50** · `style-check` **9/9** ·
`sets-integrity` **12/12** (6,236 verses) · `guidance-range` **32/32**,
`sources-all` **30/30**, `guidance-001` **52/52**.

The earlier 2026-10-09 line is kept for the record: `style-check` 3/3 (contract
only — three empty placeholders) · `sets-integrity` 12/12 · `sources-all` 30/30 ·
`guidance-001` 13/13 · `verify_verse --all` reported nothing to check, because the
harnesses for sūrahs 2 and 112 were retired with the payloads they tested.

## The house format (set 2026-10-09)

An audit found the corpus had been written in three different formats: chapter 1
was one continuous paragraph per verse with inline bold headings, chapter 2 was
30–60 short paragraphs with headings on their own lines, and the opening
convention flipped mid-sūrah at 2:10. Paragraph count had also climbed from an
average of 9.2 (2:1–20) to 62.9 (2:121–140).

The maintainer chose: **Layout B** (structure kept, short paragraphs merged to
~85 words), **opening inline** in the first paragraph, **forward pointers only
where earned**, and **Makkah / Madīnah / Bayt al-Maqdis** in prose. Scope: all
authored verses.

`docs/style.md` is the normative statement; `tools/tests/style-check.js` enforces
it. All 168 verses were retrofitted. The retrofit was mechanical and is
reproducible — see the invariants below.

Word counts are preserved by construction: 168,579 → 168,591 (+12), where +6 is
five `Jerusalem`→`Bayt al-Maqdis` substitutions in sūrah 2 plus the word
`believers` restored to the 2:75 quotation, and +6 is the four chapter-112
opening reorders. No commentary was lost.

Two transform bugs were caught by invariants rather than by the tests passing,
and both would have shipped silently:

- `inline_opening` kept `parts[0]` *and* prepended it, duplicating the opening
  ayah (+19 words on 2:157).
- the sentence splitter tokenised `**bold**` as an empty italic span, dropping
  53 words from chapter 1.

The retrofit script asserts four invariants per verse before writing: word count
never decreases, growth never exceeds the substitution count, the set of italic
quotations is unchanged, and no heading is lost or invented. **Any future
mechanical pass over the corpus must carry the same invariants.**

| | verses | paras/verse | headings |
|---|---|---|---|
| sūrah 1 | 7 | 12.1 | 29 |
| sūrah 2 | 157 | 25.0 | 1,205 |
| sūrah 112 | 4 | 4.5 | 1 |

## Deferred, deliberately

Not bugs, not forgotten — the maintainer said *"Wait a bit on the tidy."* Do
not do these unprompted:

- stale reference at `prompt.md:61`
- three empty files in `data/tafsir_markdown/`
- dead `.quran-quote` CSS
- font licence texts for Amiri, Inter and the HAFS face, which should be added
  under `fonts/` before distribution (only Noto ships its licence text;
  `ATTRIBUTION.md` says so plainly)

## Open questions for the maintainer

- The authored guidance is **not read aloud** — `js/read-aloud.js` still speaks
  the primary source only. Whether to change that has not been raised.
- Whether Tier A/B/C word bands are right in practice. Chapter 1 and chapter
  2's opening both landed at the lower end of their bands.
