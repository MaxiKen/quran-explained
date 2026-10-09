# Progress

Updated at the end of every session, before pushing. **Read this first** — it is
faster than reconstructing state from `git log`.

## Authored so far

| surah | verses | words | plan words | notes |
|---|---|---|---|---|
| 1 — al-Fātiḥah | 7 / 7 | 5,414 | 5,790 | complete |
| 2 — al-Baqarah | 91 / 286 | 78,116 | 78,580 | 1–91, in sixteen batches |
| 112 — al-Ikhlāṣ | 4 / 4 | 1,375 | — | the original pilot, pre-dates the tier plan |

**98 of 6,236 verses (1.57%) · 85,497 of 4,013,330 planned words (2.13%)**

Check with `python3 tools/progress.py --next` — it is authoritative, this table
is for humans.

## Resume here

**Sūrah 2, verse 49.** The address to the Children of Israel runs to about
2:141 — roughly a hundred verses, the largest single unit in the sūrah.
2:40–2:91 are done — the whole address to the Children of Israel from the
exodus to the prophets they killed. Next: 2:92–2:96, the calf after Mūsā
left, the mountain again, the Sabbath-breakers' town, and the claim that
death will not reach them.

Mujāhid's count, recorded by Ibn Kathīr at 2:4, is the map for the opening:
four verses on the believers, two on the disbelievers, thirteen on the
hypocrites. That whole block, 2:1–2:20, is now authored.

252 verses remain in sūrah 2, 241,800 planned words.

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
may run long; it must not run short. The harness checks `n >= target * 0.75`.

Three verses had been trimmed under the old two-sided rule and have been
restored to their original length: **2:18 (393→524w), 2:31 (798→947w), 2:45
(734→818w)**. `tools/restore_trimmed.py` did it.

Auditing every authored surah against the new floor found a fourth problem —
**112:1 was 340w against a floor of 405**, written short in the original pilot
rather than trimmed. Expanded to 783w by `tools/expand_112_1.py`.

**No verse in any authored surah is now under its floor.**

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

Branch `arena/2c46b8a2-quran-explained`, PR #89 open against `main`.

**The session this handoff was written in also reset the workspace once.** It
was recovered with `git fetch` + `git reset --hard` from the pushed branch.
See [pitfalls.md](pitfalls.md#the-workspace-can-be-reset).

## Verification state

`sources-all` 27/27 · `guidance-112` 28/28 · `guidance-001` 47/47 ·
`guidance-002` 268/268 · `tier_verses.py --verify` exit 0 (71.8% exact, 91% on
Tier A, 1.5% severe). 370 checks total.

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
