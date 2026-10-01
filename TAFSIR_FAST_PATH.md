# Fast path — the whole Quran's commentary at the v8 standard, in days instead of months

> **Proposal for the owner, 2026-10-01 — answered the same day: see §0 for what was decided.** The
> rest of this document is the original proposal, kept as the record of the options; this file is not
> itself part of the standard (the decisions live in `TAFSIR_RULES.md`). Figures marked *(measured)* were
> taken on the pre-clear tree (commit `95ad372`, recoverable with `git archive 95ad372`). Figures
> marked *(estimate)* are arithmetic on the assumptions in Appendix A. **Nothing here has been run
> against a real model yet** — §8 is the pilot that replaces the estimates with measurements.

## 0. What the owner decided (2026-10-01)

The owner answered the proposal. The answers, verbatim, are recorded in `TAFSIR_HANDOFF.md` and
`TAFSIR_WORKLOG.md`; what they came to:

| | Proposed (§6) | Decision | Now lives in |
|---|---|---|---|
| R1 | a second AI checks; the owner reads a sample | **Adopted, changed.** The AI writes, reviews its own range in a separate cold pass (`arena-review-agent`), posts the statistics, pushes to GitHub and carries on; the owner reads afterwards and asks for a change if needed; silence is never recorded as approval | RULES §0.9, §11.5; `stats.py` |
| R2 | parallel writers inside one chapter | **Dropped** — one AI is all that can be accessed | — |
| R3 | a stop per chapter instead of per fifty | **Removed**, read as "no stop-and-wait at all" | RULES §0.9 |
| R4 | chapters in parallel | **Agreed** | RULES §11.14 |
| R5 | Chapter 1: regenerate or restore | **(a) restored** to the approved text | `tafsir/001.md`, its payload and reviews |
| — | (not proposed) | Chapter 1 is a **writing-style yardstick only**; evidence density is posted, never an alarm | RULES §0.13; `quality.py` |

**What this means with one AI.** The scripted-writer factory of §5 needs a model API and several
models, and neither is available, so §5 stands only as the record of the options. What remains is one
AI working continuously under the rules above:

| Lever | Status |
|---|---|
| No stop-and-wait (R1, R3) | **Done** |
| Parallel sessions, one chapter each (A1, R4) | **Allowed**; how many sessions run is the owner's call |
| Faster draft check (E1) | **Done in part** — grounding limited to the reported verses; output byte-identical on the real corpus; one Chapter 2 verse 11.3 s instead of 15.3 s *(measured)*. The rest is the audit re-running its per-verse rules on every written verse of the chapter (≈ 0.2 s per written verse, per call), so it grows as a chapter fills; scoping that is a larger refactor, not done |
| Review compiler (C2) | **Not built** — the largest remaining saving for one AI: the hand-filled review is as much output as the prose (≈ −70 % *(estimate)*) |
| Closed-world evidence menu (C1) | **Not built** — the strongest guard against a wrong attribution |
| Canaries (C7) | **Not built** |
| Lower base floor (D1) | **Not changed** — the 700-word floor was not part of the yardstick change. It is what drives the volume: a 500-word base would cut the mandatory minimum by 28 % (4.38 → 3.17 M words), 400 by 41 % *(measured)* |

**Time with one AI** *(estimate)*: ≈ 2–2.5 minutes a verse including the review pass (writing ≈ 30 s,
gate waits ≈ 15 s, tool calls ≈ 20 s, review ≈ 50 s), so ≈ 25–30 verses an hour of continuous work
and ≈ 210–260 session-hours for the whole Quran.

| Sessions in parallel | Wall-clock, continuous work |
|---|---|
| 1 | ≈ 9–11 days |
| 5 | ≈ 2 days |
| 10 | ≈ 1 day |
| 20 or more | ≈ 10–12 h — the floor is Chapter 2's 286 verses written in order |

The first run (2:1–2:50) replaces these guesses with a measured rate.

## 1. Bottom line

1. **"No time" is not possible; hours of machine time and days of calendar time are.** At the
   standard's own floors the whole Quran is about **6.2 M words** of original prose (≈ 8–11 M output
   tokens). Producing that is ≈ 36–50 stream-hours of raw generation — about **3–4 hours of
   wall-clock** when chapters run in parallel, because the longest chain is Chapter 2's 286 verses.
2. **Writing speed is not what makes today's format slow.** Four things are:
   (a) one interactive agent writing verse by verse;
   (b) a draft check that costs ≈ 14 s per call whatever the range;
   (c) every ≤ 50-verse checkpoint waiting on a human sign-off — `reviewer` is `project-owner` in
   all five accepted manifests, and 33 of the 63 written verses were still waiting;
   (d) rule churn — seven revisions of the standard (v7.0 → v8) and three corpus clears in five days.
3. **Human review is the hard ceiling.** Reading 6.2 M words once takes **258–413 hours** (32–52
   working days). Anything both fast and standard-keeping must verify with machines first and let
   people read *samples and exceptions*, not everything.
4. **Recommended:** a "factory" (§5) — a scripted writer per verse with the gate's findings fed
   back, chapters in parallel, a closed-world evidence menu, a review compiler plus two machine
   reviewers, and a human sample. Every floor, code and threshold stays exactly as it is.
5. **Two decisions are yours and they set the speed:** may a machine be the *independent reviewer*
   (R1), and may stops be per chapter instead of per fifty verses (R3).

## 2. Where the time goes

| What | Measured | Why it matters |
|---|---|---|
| Size of the job | 114 chapters, 6,236 verses. The floor `max(700, 9 × English words)` sums to **4.38 M words**; 98 % of verses sit on the flat 700-word base | Depth, not verse length, drives the volume |
| Expected real volume | Chapters 1–2 came to ×1.41 of floor (62,304 words / 63 verses) → **≈ 6.2 M words ≈ 8.4 M tokens** (10.9 M on a +30 % tokenizer) *(estimate)* | |
| Raw generation | 8.4 M tokens ÷ 65 tok/s = **36 stream-hours**; 50 with 40 % regeneration *(estimate)* | Spread over 25 streams ≈ 2 h |
| Writer's reading | capped digest **≈ 15 KB ≈ 4,800 tokens per verse**; uncapped 110–395 KB per verse | Reading is prefill — cheap, not the bottleneck |
| Review manifest | **9.7 KB per verse** (612 KB for 63 verses): 36 % claim ledger, 27 % transmitted-evidence ledger, 20 % source synthesis, 13 % Qur'an cross-reference ledger, 3 % notes and scores | Hand-filling it is as much output as the prose itself |
| Gate cost | **≈ 12–15 s per call** on Chapter 2 for 1 verse or 56 — it re-audits the whole chapter on every call. Measured afterwards: the grounding check was about a quarter of it (now limited to the reported verses); the rest is the per-verse rules re-run on every *written* verse, ≈ 0.2 s each | A check after every verse costs ≈ 0.2 s × the verses already written in the chapter, per call — ≈ 18 CPU-hours across the Quran, growing as a chapter fills; one audit per chapter ≈ 5–10 CPU-minutes *(estimate)* |
| Digest build | 0.1 s (Ch. 1), 1.4 s (Ch. 36), 21 s (Ch. 2) | Source mapping is not a bottleneck |
| Human checkpoint | ≈ 50,000 words per 50-verse checkpoint; 125 checkpoints | Reading everything: 258–413 h. A 2 % sample ≈ 8 h; 5 % ≈ 21 h |
| History | 63 verses stood on 2026-09-27, five days after the standard was first set; 30 accepted, 33 pending | ≈ 13 verses/day → ≈ 500 days at that rate |
| Churn | v7.0 → v8 between 2026-09-25 and 09-27; corpus cleared 09-24, 09-25, 09-27 | Each change rewrote earlier prose |

## 3. What "the same standard" means

| Layer | What certifies it | In the fast path |
|---|---|---|
| Form and evidence | `audit.py`: 77 codes — 700-word floor, every paragraph past 120 words, every phrase of the verse quoted, every cross-reference expanded, no source parade, no repeated shape across verses | Unchanged; the writer sees the failing codes and repairs |
| Parity | `quality.py` drift alarms frozen from Chapter 1, in 50-verse windows: mean sentence ≤ 23.0, sentences over 40 words ≤ 10 %, Flesch ≥ 62, evidence ≥ 8.2 per 1,000 words | Unchanged; given to the writer as numeric targets |
| Review record | Manifest: all eleven sources fingerprinted, every claim, cross-reference and transmitted statement ledgered, eight scores all ≥ 4 | Same schema and gate; a compiler fills the bookkeeping, a reviewer supplies the judgements |
| Truth | **No gate proves doctrine.** The gates prove form, traceability and consistency | Closed-world citations, two reviewers, canaries, scholar sampling (C1, C3, C4, C5, C7) |

The gate requires only that writer and reviewer are non-empty, different, and `independent` is
`true` (`quality.py`). It cannot tell a genuine review from a perfunctory one — which is why §4 pairs
every machine reviewer with checks that do not rely on it.

## 4. All the ways

*Needs your OK* names the rule change in §6, or "no" when the standard already permits it.

### A. Run more at once

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| A1 | **Chapter-parallel workers**, verses in order within each chapter. The gate's frontier is per chapter (`accepted_frontier(chapter)`) and RULES §11.12 / PIPELINE §5 item 5 already split work by chapter | Wall-clock = longest chain ≈ 3–4 h for the whole Quran | none | Only that Chapter 1 (the floor) exists first: every chapter is gated against its record |
| A2 | **Window lanes inside a chapter** — ≈ 50-verse lanes, each with its own style card (a fixed set of heading words and sentence openings it may use); cross-lane duplicates repaired afterwards | Chapter 2 ≈ 40 min | none (same gates) | R2; mid-run push-checks will not apply |
| A3 | **Stateless per-verse workers**, then one pass regenerating only uniqueness collisions | Limited by rate limits only | none; more repairs | R2 |
| A4 | **Overlap the stages** — review chapter *k* while chapter *k+1* drafts; the writer runs ≤ 50 drafts ahead of the accepted frontier, as the gate already allows | Removes review latency from the chain | none | no |
| A5 | **Many parallel Arena sessions**, one chapter each | ≈ sessions × 13 verses/day (100 sessions ≈ 5 days) | none | no — but stays interactive and every checkpoint still needs sign-off |

### B. Replace hand-writing with a script

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| B1 | **Scripted writer loop** — packet → model → gate → up to 3 repairs fed by the gate's own findings → quarantine | The main change: removes the interactive agent. The repo has no model client today | none; the same gates decide | An API key, kept as a repository secret, never in chat |
| B2 | **Verse packets** — floor, required phrase list (`PHR-*`), cross-reference expansions (`REF-*`, from `reference.py`), digest, numeric targets from the baseline, ledger of headings, openings and 6-word runs already used in the chapter | Far fewer first-pass failures | none | no |
| B3 | **Prompt caching** of the static prefix (rules plus one exemplar, ≈ 13 k tokens) | Cache reads bill at 0.1× the input price on most models | none | no |
| B4 | **Batch API** for non-sequential stages (reviews, lanes) | −50 % price, separate rate-limit pool, completes within 24 h and often sooner | none | no |
| B5 | **Model tiering / best-of-N** — a fast model drafts, a stronger one repairs failures and writes the floor chapter | A speed-versus-cost dial | none | no |
| B6 | **Fast-inference hosts or fast modes** (hundreds to thousands of tokens/s) | Lower per-verse latency | Unproven on this gate until the pilot | no |
| B7 | **Resumable, idempotent runs** — all state in files; a rule tweak regenerates only the failing verses | Rework becomes cheap | none | no |

### C. Verify with machines first

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| C1 | **Closed-world evidence menu** — the writer may cite only reports and authorities that appear in that verse's digest, extracted with their collection; a script checks every attribution by lookup | The cheapest verification there is | **Stronger** — a fabricated attribution becomes a hard fail | no |
| C2 | **Review compiler** — a script pre-fills the manifest's bookkeeping (fingerprints, locators, excerpts, candidate source passages); the reviewer returns judgements only (direct / contextual, included / omitted, eight scores, a short rationale) | Reviewer output ≈ −70 % *(estimate)* | Same schema, same gate | no |
| C3 | **Two machine reviewers** from different model families; accept only when both score every dimension ≥ 4; disagreement goes to repair or to a human | Removes the 125-checkpoint human queue | Same gate; see the caveat in §3 | **R1** |
| C4 | **Risk-weighted human review** — legal rulings, divine attributes, prophet stories and Isrā'īliyyāt, eschatology go 100 % to a scholar | Human time goes where errors cost most | **Stronger** | no |
| C5 | **Statistical sampling** — a stratified 2–5 % plus every flagged verse (≈ 8–21 h of reading) | 258–413 h → 8–21 h | Replaces "read all" with a measured error rate | R1, R3 |
| C6 | **Drift monitor as stop-loss** — the existing 50-verse metric windows halt a chapter automatically; you receive an exception report instead of 125 checkpoints | Removes waiting | Same thresholds | R3 |
| C7 | **Canaries** — seed known-bad verses into the sample to measure what the reviewers actually catch | Tells you whether C3 can be trusted | **Stronger** | no |

### D. Change the product — these lower or reshape the standard; not recommended unless forced

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| D1 | **Depth tiers** — the 700-word floor only for Tier A chapters, shorter for the rest | ×2–3 on Tier B *(estimate; e.g. a 300-word floor)* | **Lowers it** | yes |
| D2 | Cross-reference the **144 repeated refrain verses** instead of rewriting them (2.3 % of the work) | Small | Changes the per-verse format | yes |
| D3 | **Passage-level source maps** — read per pericope, write per verse | Small, input side only | none | no |
| D4 | **Intro-first release** — the 114 chapter introductions (250–1,500 words) ship first | Something real in every chapter early | none, but `build_data.py` refuses any chapter with a `TODO` verse, so the publisher and app need a small change | yes (new payload type) |

### E. Fix the tooling drag — behaviour-preserving

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| E1 | **Scope the draft check.** Done in part (§0): grounding limited to the reported verses, byte-identical output, ≈ −26 % per check *(measured)*; the per-verse rules still run on every written verse | Smaller than first estimated (not 14 s → a few seconds) | none | no |
| E2 | **Prebuild all 114 digests** (minutes), audit chapters in parallel, CI matrix per chapter | Minutes | none | no |

### F. Process

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| F1 | **Freeze v8 before bulk generation**; any rule change goes through the pilot first | Removes the biggest source of rework | none | yes — a commitment |
| F2 | **Per-chapter automated stops** with an exception report instead of per-fifty push-and-confirm | Removes waiting | none | R3 |
| F3 | **Publish chapter by chapter** — the app already shows "coming soon" for the rest | Something presentable early | none | no |
| F4 | **Pick a showcase set** (§7) | Decides what must be finished first | none | yes |

### G. Capacity and venue

| # | Way | Speed effect | Standard effect | Needs your OK |
|---|---|---|---|---|
| G1 | **Scholar reviewers in parallel**, one packet per juz, for C4 and C5 | Human capacity | **Stronger** | no |
| G2 | **Run bulk generation in CI or on a server, not in a chat session.** GitHub-hosted jobs stop at 6 h, a matrix holds 256 jobs, and 20 / 40 / 60 jobs run at once on Free / Pro / Team ([limits](https://docs.github.com/en/actions/reference/limits)). The whole output is ≈ 140 MB — more than one Arena turn carries (≈ 128 MB / 10,000 files, best effort) | Unattended and parallel | none | no |

## 5. Recommended: the factory

*Superseded in part by §0: the factory assumes a model API and several models, neither of which is
available. It is kept as the record of the options.*

```text
Chapter 1 (the floor) ─► freeze baseline (you approve once)
                              │
        ┌─────────────────────┴──── 113 chapters in parallel ────────────────────┐
        ▼                                                                          ▼
 packet(v) ─► writer(v) ─► gate ─fail─► repair (≤3) ─► quarantine                 …
                     │pass
                     ▼
        review compiler ─► reviewer A ┐
                           reviewer B ┴─► both agree, all ≥ 4? ─no─► repair / quarantine
                     │yes
                     ▼
     accepted (frontier advances) ─► next verse … ─► chapter done ─► audit + quality + build_data ─► PR
                                         you read: exceptions + a 2–5 % sample
```

| Station | What it does | Built from |
|---|---|---|
| 0. Floor first | The only strictly serial step. Either restore the approved Chapter 1 from git (instant), or regenerate it, read it in full (≈ 40 min), and re-freeze with `--freeze-baseline --approval` | `quality.py` |
| 1. Packets | Per verse: text, floor, phrase list, cross-reference expansions, digest, evidence menu, numeric targets, chapter ledger | `corpus.py`, `reference.py`, `sources.py` + new |
| 2. Writer | One call per verse in a fresh context, cached static prefix, ≤ 3 repairs from the gate's findings, then quarantine. Chapters in parallel | new |
| 3. Gate | `audit` (scoped), then `quality` draft check; every result logged | `audit.py`, `quality.py` + E1 |
| 4. Review | Compile the manifest, two reviewers return judgements, the gate validates; disagreement or any score < 4 → regenerate with the reviewers' notes (≤ 2 loops), then quarantine | `quality.py --template` + new |
| 5. Human | Quarantine, the risk categories (C4), a stratified 2–5 % sample, canaries; one exception report per chapter | — |
| 6. Publish | `build_data.py`, `sw.js` bump, worklog from `status.py --md`; one PR per chapter or juz | existing |

**Time and cost *(estimate, assumptions in Appendix A)*.**

| | Result |
|---|---|
| Whole Quran, chapter-parallel (A1) | Longest chain = Chapter 2, ≈ **2.9 h** with a scoped gate, ≈ 3.8 h with today's 14 s gate; median chapter ≈ 25–32 min |
| With 6 lanes in Chapter 2 (A2) | ≈ 38 min |
| Concurrency needed | ≈ 50 stream-hours ÷ available streams; 25 streams ≈ 2 h, 10 streams ≈ 5 h |
| Writer cost (synchronous API, mid-tier) | ≈ $250 |
| Two batch reviewers, judgement-only | ≈ $150 |
| Total | **≈ $400**; ≈ $800 with pilots and rework; a top-tier model at 5–10× ≈ $2–4 k |
| Calendar | Pilot and tuning 1–2 days → full run ≈ 1 day of machine time → your sample, fixes and publish ≈ 2–3 days. **About a week**, almost none of it waiting on the machine |

Batch discounts, cache pricing and rate limits are the provider's: see
[Anthropic's pricing page](https://platform.claude.com/docs/en/about-claude/pricing) and
[OpenAI's Batch API guide](https://developers.openai.com/api/docs/guides/batch). Both document 50 %
batch pricing; Anthropic documents cache reads at 0.1× and stacking with the batch discount.

## 6. Rule changes only the owner can make

*All decided — see §0.*

No floor, audit code, drift threshold or manifest requirement changes in any of these.

| | Change | Where | Needed for |
|---|---|---|---|
| **R1** | A distinct automated identity may be the *independent reviewer*, with human sampling as the check on it. The gate already accepts any non-empty identity different from the writer with `independent: true`, so this is policy text, not code | `quality/README.md` ("A different reviewer…"), RULES §11.5 | C3, C5 |
| **R2** | Prose may be written in parallel stretches by stateless workers, with the gate's uniqueness checks enforcing diversity afterwards | RULES §11.3; PROMPT §1 item 4 and §10 "Rules that hold at every checkpoint" item 3 | A2, A3 |
| **R3** | A generation stop is per chapter, not per fifty verses; you confirm by exception report rather than by pushed candidate | RULES §0.9, §11.1, §11.5, §11.8; PIPELINE §5 items 2–3 | C5, C6, F2 |
| **R4** | "Chapter order is ascending" is the default order of work, not a ban on parallel chapters (RULES §11.12 and PIPELINE §5 item 5 already split work by chapter) | RULES §11.14 | A1 |
| **R5** | Chapter 1: regenerate and re-freeze, or restore the approved one from git | `quality/README.md` | Station 0 |

Chapter-parallel work (A1) needs only R4 and R5. Machine review (C3) adds R1, per-chapter stops (C5, C6,
F2) add R3, and lanes (A2, A3) add R2. The rest of the factory is tooling.

## 7. Presenting soon

A chapter is a unit of release: the app already says "coming soon" for any chapter without a
payload. Machine-time estimates assume the factory above, after the pilot.

| Showcase set | Chapters | Verses | Share | Longest chain | Machine time |
|---|---|---|---|---|---|
| Juz 30 | 37 (78–114) | 564 | 9.0 % | 46 verses | ≈ 30–40 min |
| Chapters of ≤ 30 verses | 51 | 756 | 12.1 % | 30 verses | ≈ 20–25 min |
| Juz 29 + 30 | 48 (67–114) | 995 | 16.0 % | 56 verses | ≈ 35–45 min |
| The app's popular list (1, 36, 67, 55, 56, 18, 112, 2) | 8 | 694 | 11.1 % | 286 verses (Ch. 2) | ≈ 3–4 h; ≈ 1–1.5 h without Chapter 2 |
| Whole Quran | 114 | 6,236 | 100 % | 286 verses | ≈ 3–4 h |

Machine time is not review time. State plainly what the review was — e.g. "source-grounded,
machine-reviewed by two independent models, scholar-sampled" — rather than implying that every
verse was read.

## 8. Pilot — the cheap test that de-risks everything

*With one AI the pilot is the first run, 2:1–2:50 (§0).*

* **Set:** Chapter 112 (4 verses), Chapter 1 (7 verses, the floor) and Chapter 36 (83 verses, to
  stress uniqueness across a long chapter and the rate limits). ≈ 94 verses, ≈ 1–2 h, under $25
  *(estimate)*.
* **Exit criteria — all must hold:**
  1. ≥ 90 % of verses pass `audit.py` within three attempts;
  2. every 50-verse window passes the `quality.py` drift thresholds;
  3. zero unverifiable attributions under the closed-world check (C1);
  4. both reviewers score every dimension ≥ 4 on ≥ 85 % of verses, and catch ≥ 90 % of canaries;
  5. you read ≈ 10 verses and judge them at the Chapter 1 standard;
  6. measured tokens and seconds per verse replace every *(estimate)* above.
* **If anything fails:** tune the prompts and packets, never the rules, and rerun the pilot.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Independent calls give homogeneous prose and trip `STY-UNIQUE-VERSE` | Style cards, the chapter ledger in every packet, repair of the later verse of each collision; measured in the pilot |
| A fabricated or misattributed report | Closed-world evidence menu (C1); a hard fail, not a warning |
| Same-model blind spots | Reviewers from different model families; canaries; scholar sampling |
| A perfunctory review passes the gate | Judgement-only forms over retrieved passages, two reviewers, disagreement escalation, canaries (C7) |
| Rate limits or outages | Resumable state, backoff, a per-run budget cap |
| A rule changes mid-run | F1: freeze, and pilot any change first |
| Output larger than a session carries | G2: CI or a server; one PR per chapter or juz |
| The gates certify form, not doctrine | C4 and G1: a scholar reads the high-risk categories in full |

## Appendix A — assumptions behind every *(estimate)*

* 6.2 M words = 6,236 verses × 994; Chapters 1–2 achieved ×1.41 of the floor. 1.35 tokens per word
  (+30 % on newer tokenizers, per Anthropic's pricing notes).
* 65 output tokens/s per stream; 5 s prefill per request; scoped gate 3 s (14 s unscoped).
* 40 % of verses regenerated once after a gate failure — replace with the pilot's figure.
* Writer input per verse: 4,800 digest and 1,500 packet tokens uncached, 13,000 cached prefix.
* Reviewer per verse: 7,600 uncached and 4,000 cached input tokens; 800 output tokens judgement-only
  (today's hand-filled manifest ≈ 2,800); two reviewers.
* Prices: $2 in / $10 out / $0.20 cached per million tokens for a mid-tier model (Anthropic's listed
  Sonnet 5.5 rate on 2026-10-01); batch = 50 %.
* Whole output on disk ≈ 40 MB prose + 40 MB payloads + 61 MB review manifests ≈ 140 MB.

## Appendix B — reproduce the measurements

Timings vary about ±15 % from run to run; the figures above use the upper end.

```bash
mkdir -p /tmp/qe-measure && git archive 95ad372 | tar -x -C /tmp/qe-measure && cd /tmp/qe-measure
export PYTHONDONTWRITEBYTECODE=1
time python3 scripts/tafsir/sources.py 2                          # digest: ≈ 18–21 s, 51 MB uncapped
time python3 scripts/tafsir/batch.py 2 --from 5 --to 5 --draft    # ≈ 12–14 s for ONE verse
time python3 scripts/tafsir/quality.py --all --push-check         # ≈ 5.5–6.5 s for 63 verses
python3 - <<'EOF'                                                  # the floor, summed over the Quran
import sys; sys.path.insert(0, "scripts/tafsir")
import corpus as C, audit as A
print(sum(A.verse_floor(len(C.words(C.ayah_en(n, v))))
          for n in C.chapter_numbers() for v in range(1, C.verse_count(n) + 1)))   # 4,383,566
EOF
```
