# Commentary tiering

`tools/tier_verses.py` assigns every verse a tier and a word target, written to
`data/plan.json`. Nothing in it reads a human's opinion — every signal comes
from the tafsīr payloads in `data/tafsir_NNN.json` plus the verse text — eight
sets since 2026-10-09, and a set with nothing on a verse is skipped rather than
scored as thinness.

```bash
python3 tools/tier_verses.py            # regenerate data/plan.json
python3 tools/tier_verses.py --verify   # re-run the validation, exit 0 or 1
```

## The tiers

| | verses | share | words |
|---|---|---|---|
| A | 1,836 | 29.4% | 1,300–1,900 |
| B | 2,920 | 46.8% | 650–1,000 |
| C | 1,480 | 23.7% | **300**–450 |
| | **6,236** | | **5,902,150** |

Those are the counts after the two new sets were folded in: **147 verses changed
tier** (mostly B→A in al-Baqarah and Āl ʿImrān, where al-Qushayrī and al-Wāḥidī
have material) and 2,080 word targets moved. Note the difference from raising
`BAND` alone, which changed 0 tiers: adding a *source* changes what the
classifier can see, so it changes assignments; changing a *band* does not.

The bands were raised on 2026-10-09 (from A 900–1,300 / B 450–700 / C 200–320)
in `tools/tier_verses.py`, and the plan above was regenerated from it; tier
*assignment* did not move at all — 0 of 6,236 verses changed tier, only their
`words`. The 300-word floor is the current form of the maintainer instruction
*"The base should be 200 (minimum)."*

Length is **continuous inside each band** — the tier sets the range, the
verse's own score sets its position within it. This is deliberate: a verse
mis-tiered by one step still receives roughly the right length, so the fuzzy
B↔C boundary does not produce visible damage.

## Signals

The key one is that the classifier reads **all eight** sources, not Ibn Kathīr
alone. Ibn Kathīr writes in long runs covering many verses, so his per-verse
numbers say almost nothing about an individual verse. Maʿārif, Tanwīr,
al-Jalālayn and al-Mukhtaṣar write verse-by-verse (~99% verse-specific), and
that is where the per-verse signal lives.

| signal | meaning |
|---|---|
| `max_specific` | longest *verse-specific* entry across the sets — what a scholar wrote about this verse **alone** |
| `n_specific` | how many sets treat it individually with 60+ words — independent agreement |
| `tr_words` / `ar_words` | length of the verse in the app's translation / in Arabic |
| `sum_density` | sum of the per-verse densities |
| `ruling` | legal vocabulary in the **verse text first**, then verse-specific prose |
| `narrative` | prophet / tribe / place names in the verse text or its tafsīr |
| `occasion` | reason-for-revelation language in the verse-specific prose |
| `imp` | imperative and address markers in the verse text |
| `refrain` | same translation text repeated 3+ times in the sūrah (85 verses) |

## Safeguards

A fitted score alone misbehaves at the extremes, so three rules override it:

- a **refrain is always Tier C**
- the score can **never** put a verse in C if it has 25+ translation words or
  400+ words of verse-specific tafsīr
- the score can **never** keep a verse in B if it has 40+ translation words or
  1,200+ words of verse-specific tafsīr

## Validation

Weights were fitted by grid search over 497,664 combinations under 5-fold
cross-validation against a 337-verse labelled set held in the script itself.

**Current: 71.8% exact agreement, 91% on Tier A, 1.5% severe misses** (a Tier A
verse judged C or the reverse). `--verify` fails the build below 70% accuracy
or above 3% severe misses.

Per-class: A 91%, B 52%, C 67%. **B↔C is the weak boundary** and that is where
error is cheapest.

## Known weakness — read this before authoring a narrative sūrah

The classifier is **strong on rulings and weak on plot.** A narrative verse
buried inside a long run is under-scored, because no source writes about it
individually. Verified examples:

- `12:30` (the women of the city) — `max_specific` 100, lands Tier B
- `18:9` (opening of the People of the Cave) — `max_specific` 288, lands Tier B

Both are pivotal and both should be authored as Tier A. **Promote these by
hand while authoring**, and record the promotion in the commit message. This is
the author's judgement, not something to route back to the maintainer.

## How the tier system was arrived at

Three earlier attempts failed and the failures are instructive:

1. **Blended score with keyword flags** — `story` fired on 4,024 of 6,236
   verses because the regex matched *"they said"* and *"king"*. It put 103:1
   (*"By time"*, five words) in Tier A.
2. **Tightened keywords** — better, but Tier A grew to 54.6% of the Qurʾān,
   which is not a tier system.
3. **The labelled set itself was contaminated** — the Tier-B list was built by
   dumping sūrah openings and assuming they were "standard", but 5:2 has 92
   translation words and 4:1 has 52. Twenty-four verses were mislabelled,
   suppressing measured accuracy. Correcting them moved accuracy up.

Also worth knowing: the *muqattaʿāt* (`Ṭā-Hā`, `Ḥā-Mīm`, `Yā-Sīn`) are excluded
from scoring accuracy because B vs C on a two-letter sequence is arbitrary by
nature.

## What the plan carries per verse (updated 2026-10-10)

`tier`, `words` (the target: an ambition, never a ceiling), `score`, `tr_words`,
`ar_words`, `max_specific`, `n_specific`, `flags`, `refrain`, and the figures the gates
enforce: `avail`, `floor` (= `0.75 × words`; kept in the plan so no consumer re-derives
it), `lead_floor` (the tier's lead minimum, same reason), and **`authored_only`** — true
when `avail` is below that floor, which is the 168 verses that must be composed rather
than spliced. `floor`/`lead_floor` are read by `verify_verse.py`, `style-check.js`,
`compile_guidance.py` and `guidance-range.js`; `authored_only` is enforced by
`compile_guidance.py` and announced by `progress.py --next`.

`avail` counts a shared block **in full** for every verse it covers, because the compiler
may splice it for any of them. The cheaper-looking alternative — scoring a verse's
exclusive share — flags 5,516 verses and would route most of the corpus into authored
mode; `docs/pitfalls.md` has the arithmetic.

