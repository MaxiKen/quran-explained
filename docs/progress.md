# Progress

Updated at the end of every session, before pushing. **Read this first** — it is
faster than reconstructing state from `git log`.

## Authored so far

| surah | verses | words | plan words | notes |
|---|---|---|---|---|
| 1 — al-Fātiḥah | 7 / 7 | 5,414 | 5,790 | complete |
| 2 — al-Baqarah | 34 / 286 | 26,106 | 27,180 | 1–14, then 15–20, 21–26, 27–30, 31–34 |
| 112 — al-Ikhlāṣ | 4 / 4 | 1,375 | — | the original pilot, pre-dates the tier plan |

**41 of 6,236 verses (0.66%) · 34,160 of 4,013,330 planned words (0.85%)**

Check with `python3 tools/progress.py --next` — it is authoritative, this table
is for humans.

## Resume here

**Sūrah 2, verse 35.** The Ādam story runs 2:30–2:39 (Maʿārif's ten verses);
30–34 are done, so 35–39 completes it — the garden, the tree, the slip, the
descent. Then 2:40 turns to the Children of Israel.

Mujāhid's count, recorded by Ibn Kathīr at 2:4, is the map for the opening:
four verses on the believers, two on the disbelievers, thirteen on the
hypocrites. That whole block, 2:1–2:20, is now authored.

252 verses remain in sūrah 2, 241,800 planned words.

## Batched runs — what actually works

The maintainer defined a **run** as one go, with about **six batches** in it.
The pattern that works is: generate a batch → save to disk → extend the
harness range in the same change → run the suite → **push** → next batch.
Pushing per batch means a workspace reset costs at most one batch.

Measured in one run: four batches, 23 verses, ~13,900 words
(2:15–2:34, commits `a3e7dac` → `70cf9fe` → `0780489` → batch 4).

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
`guidance-002` 162/162 · `tier_verses.py --verify` exit 0 (71.8% exact, 91% on
Tier A, 1.5% severe). 264 checks total.

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
