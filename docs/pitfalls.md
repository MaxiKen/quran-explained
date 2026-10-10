# Pitfalls

Every one of these was hit during the project. They are recorded so they are
not rediscovered.

## The workspace can be reset

The workspace was reset mid-project to `ada6890` — the original `main` commit.
Every large `data/tafsir_*.json` was stubbed to a 19-byte `{"verses":{}}`, and
`ATTRIBUTION.md`, `tools/`, `data/plan.json` and both guidance files vanished.
`/tmp` was wiped too, taking jsdom with it.

**Symptom:** the server returns `200` with 19 bytes for `data/tafsir_002.json`,
and `404` for the guidance files. It looks like the app is broken. It is not —
the working tree is.

**Recovery** (this branch; it happened again on 2026-10-10 with three pushed
commits missing and every file showing as modified — the worktree content was
still correct, so the reset was lossless):
```bash
git fetch origin arena/525a7113-quran-explained
git reset --hard origin/arena/525a7113-quran-explained
```
Check `git diff <remote-sha> --stat` before resetting if you are unsure: untracked
files show up as deletions in that diff, which is not the same as them being gone.

**Prevention:** push after every session, before writing the summary. The
remote branch is the only durable copy.

## Single-line JSON renders as an empty diff

`data/tafsir_*.json` files have **no newlines** — `tafsir_002.json` is one
3,388,389-character line. GitHub hides over-long lines in diffs, so the PR
showed the old multi-line payload deleted and the replacement invisible. A
maintainer reported the contents looked empty. They were intact:

```
remote blob sha  58135a2bf73fc6a2e40e5892c71b4c1967595a97
local  blob sha  58135a2bf73fc6a2e40e5892c71b4c1967595a97
downloaded from GitHub: 3,388,389 bytes — parses as surah 2, 6 sources, 286 verses
```

`.gitattributes` now marks them `-diff linguist-generated` so GitHub says the
diff is hidden rather than showing a blank.

**To verify a large file on the remote, use the blobs API, not contents.** The
contents API returns `content: ""` with `encoding: "none"` for anything over
1 MB, which reads as "the file is empty":

```bash
SHA=$(gh api "repos/OWNER/REPO/contents/PATH?ref=BRANCH" --jq '.sha')
gh api "repos/OWNER/REPO/git/blobs/$SHA" --jq '.content' | base64 -d
```

## GitHub's 1 MB inline-display limit

Pretty-printing `data/plan.json` took it from 871,814 to 1,292,195 bytes — over
the limit, so it stopped rendering at all. **Minified is more viewable than
pretty-printed past that threshold.** `data/guidance_*.json` is pretty-printed
because those files are small and are the ones a reviewer reads.

## Verify scripts must cast JSON object keys

`d['verses']` yields **string** ayah keys. Comparing against ints produced
25,478 false failures in an early audit. Always `int(a)`.

## A failed pre-step does not stop a chained command

An `assert` in a label-fix step threw, but `&&` sequencing let the builder
re-run on the unpatched script and print success. **Re-read the artefact, not
the exit code.**

## Do not test "range absent from block text"

Ibn Kathīr's prose contains incidental cross-references, so that assertion
fires spuriously. The real invariant is **0 blocks that `startsWith` their
range label**.

## Range labels must not over-claim

Compress scattered ayah sets into runs: `8:12,63-65`, not `8:12-65`. Thirty
such labels exist in the corpus.

## Do not conflate two word counts

5,041,691 **deduplicated unique** words is not the same as 12,043,324
**per-verse sum**. The 1.92× figure is the per-verse sum against the previous
single-source corpus.

## Two payload shapes in the upstream source data

`en-tafisr-ibn-kathir` (note the typo in the folder name) is a flat list of
`{text, ayah, surah}`. The others are `{"ayahs": [...]}` with a **sparse** ayah
list. Never assume coverage from the verse count.

## Unreachable from the sandbox

- `raw.githubusercontent.com` — use `api.github.com` contents/blobs, or `git`.
- `git/trees/<sha>?recursive=1` on `spa5k/tafsir_api` returns `truncated: true`
  at 71,483 paths — unusable.
- The three tafsīr provenance hosts — egress allowlist.

## Small ones

- The sparse clone of the upstream corpus lands at
  `/tmp/spa5k/tafsir/en-tafisr-ibn-kathir`, not `.../tafsir/tafsir/...`.
- `fawazahmed0/hadith-api`'s default branch is `1`, not `main`.
- jsdom lacks `window.fetch` and `window.matchMedia` — stub both.
- The server must bind `0.0.0.0` or the user gets no preview.
- `getVerseCommentary(tafsir, ayah)` returns a **string**; the array version is
  `getVerseCommentaryAll(tafsir, ayah)`. Calling `.map` on the former throws.
- The ebook is rendered by `renderCompleteCommentary(div)` into the DOM. There
  is no `generateEbookContent()` — referencing it throws `ReferenceError`.
- A payload shape change needs an `sw.js` `CACHE_VERSION` bump; a new `data/`
  prefix needs the SW cache regex updated.

## Analytical errors worth not repeating

- **Ruling out paraphrase.** The single most consequential mistake of the
  project. It made the maintainer's core requirement sound impossible.
- **Describing the six-block layout as satisfying the brief.** It did not.
- **A throughput table built on an unmeasured 100–200 words/verse.** The first
  real pilot came in at ~340 words/verse. Estimates have since been re-derived
  from measured output — keep doing that.
- **Committing on a red suite.** `guidance-001.js` was pushed at 43/46 because
  the failure looked like a stale assertion. Fix the assertion, then commit.

### What it cost in practice

Auditing the harness after batch 28 found two independent gaps, both caused by
this exact bug:

| gap | how long | effect |
|---|---|---|
| `NAMES` missing 11 authorities | batches 25–28 | those narrators were never checked |
| `pairs` stuck at verse 48 | batches 8–28 | 109 verses had no translation-quote check |

`pairs` is the array asserting each verse quotes the app's own `ayah_en`. It
last grew in batch 7. Every batch after that reported the fragment additions in
its commit message while the file kept its old array — 109 verses, 210 checks,
silently absent for twenty-one commits.

Both were backfilled in one pass, with assertions on every replacement. The
backfill is mechanical and worth keeping: for each verse, take the longest runs
of consecutive `ayah_en` words that occur verbatim in the commentary, reject
anything containing an apostrophe or backslash, and assert uniqueness. It found
fragments for all 109 verses and all 210 new checks passed first time — which is
itself the useful result, because it means the prose had been quoting the
translation correctly all along. Only the check was missing.

The suite went from 328 to 544 checks on `guidance-002` with no verse changes.
A green suite is not evidence of coverage. Count the checks.

## An unasserted `.replace()` in a harness patch silently checks nothing

Every harness widening was done by a throwaway script in `/tmp` that read
`tools/tests/guidance-002.js`, called `str.replace` on the old `NAMES` line,
and wrote the file back. Two of those scripts — `h26.py` and `h27.py` — had
their `assert` on the wrong string, so the replace matched nothing, wrote the
file back unchanged, and printed success anyway.

The suite still passed. That is the whole problem: `NAMES` drives the
authority check, and a name that is absent from `NAMES` is not a failed check
— it is a check that never runs. Batches 25, 26 and 27 reported 318/318 and
323/323 while eleven newly cited authorities were being skipped entirely.

The gap showed up only when the names were finally added: `574 checked` became
`594 checked`, and one real error surfaced (2:131 named Namrūd, whose only
appearance in the six sources is Maʿārif's 2:130 block, reached through a
prose cross-reference the harness had not picked up).

Two rules follow.

**Assert the replacement, then assert the result.**

```python
old = "    'Mūsā'];"
assert old in s, 'target line not found'
s = s.replace(old, new)
assert new in s, 'replacement did not take'
```

**Read the checked-count, not just the pass line.** The authority check prints
`every named authority (N checked) appears in that verse's sources`. If `N`
did not go up when you added names, the patch did not apply. A green suite
whose coverage silently shrank is worse than a red one.

## Trimming verses to fit a band

Until 2026-10-09 the length check was two-sided — a verse more than 25% away
from its plan target in *either* direction failed. That was wrong, and it
caused real damage: three verses were cut down to fit a band they did not need
to fit.

| verse | written | trimmed to | restored |
|---|---|---|---|
| 2:18 | 524w | 393w | 524w |
| 2:31 | 947w | 798w | 947w |
| 2:45 | 818w | 734w | 818w |

The rule is a **floor**. A verse may run long; it must not run short. The
harness now checks `n >= target * 0.75` and nothing else.

Trimming was also just slow and error-prone. Bringing 2:45 into band took six
attempts, because `str.replace` fails silently when the target is a file's
last paragraph — there is no trailing newline to match — so three of those
runs changed nothing and reported the same word count back.

`tools/restore_trimmed.py` recovers the original text by exec'ing the
authoring script with file writes suppressed and reading its `V` dict. It
takes each verse only from the script that actually authored it — an earlier
version took it from whichever script ran last, which silently restored the
already-trimmed copy and reported success.

## The extractive compiler: four failures that are only possible in compiled mode

`tools/compile_guidance.py` splices the sources' own sentences and lets only
checked connectives between them. That removes invented attribution, and
introduced four problems of its own, all seen in the first 18 verses.

**A spliced fragment reads fluently and means nothing.** Bracket-blind sentence
splitting cut `(Alif. Mim): 'Alif stands for Allah…'` in half and emitted a
sentence starting `Mim):`. It passed the traceability proof — it *is* the source's
text, substring and all — because the proof checks provenance, not wholeness.
Fixed at both ends: the splitter is bracket-depth aware, and a selection that
starts with punctuation, contains an isnād arrow, or is under three words is
refused with the message `is a fragment, not a sentence`.

**Ref drift is a selection bug, never a sourcing bug.** Refs are positional
(`M43.19.2` = maarif, paragraph 19, sentence 2). When segmentation improves, every
number below the change shifts, and a spec silently selects a *different but still
genuine* sentence. The gate cannot catch that — the new sentence is verbatim from
the same block. So the compiler now fails the verse with `re-read the packet`
rather than letting it through, which is only possible because the shift tends to
produce a fragment first. If you change `sentences()` in `verse_packet.py`, expect
to re-check every spec against a fresh packet.

**The short gloss sets are the translation, twice.** al-Jalālayn, al-Mukhtaṣar
and Tanwīr al-Miqbās often open by restating the verse in slightly different
English. Selecting two of them produced: *"In the Name of God the Compassionate
the Merciful In the name of Allah, the Beneficent, the Merciful."* Grammatically
fine, individually sourced, worthless as a paragraph. The compiler now drops a
selection whose content words are more than half covered by the app's own
translation — the lead has already quoted it, phrase by phrase.

**A 26-word connective cannot explain a verse — and a 150-word one cannot walk
one.** The opening paragraph has to quote every phrase of the translation in order
and explain each where it stands, which is 240+ words at tier A before anyone has
said anything useful; the budget is therefore positional (`LEAD_FLOOR` as a floor,
`LEAD_CAP` as a ceiling), and the `>` line is no longer emitted as an opening
recitation. The provenance rule is unchanged in both places, so the lead can
explain but still cannot name anyone the sources do not name — which is also why the
evidence (hadith, cross-references, rulings, occasion, theology) belongs under the
headings: a lead that has to stay inside the verse's own vocabulary cannot carry an
attribution honestly anyway.

## A floor is data now — and the fix for a thin verse is the mode, not the number

The enforced floor lives in `data/plan.json` (`floor`, `lead_floor`, `avail`,
`authored_only`), written by `tools/tier_verses.py`; `verify_verse.py`, `style-check.js`,
`compile_guidance.py` and `guidance-range.js` read it and fall back to `0.75 × words` only
for an old plan file. Change the rule in the classifier and every gate follows; change a
consumer and you have two truths again.

On 2026-10-10 the 168 verses whose material is below their own floor were first handled by
**capping the floor**, then reverted the same day: the cap moves the goalposts on the one
number the whole project is measured against, and it is invisible in the reader's product.
**The mode is the lever.** Those verses are authored-only — composed prose, 5–10 a run —
and `compile_guidance.py` refuses to splice them, so the failure is loud and at the right
moment instead of quiet and permanent.

If you reach for a cap anyway, here is the arithmetic, so you do not spend an hour proving
it: `avail × 0.55` caps 1,553 floors (it forgets that the lead is explanation, not
quotation, so a rich verse looks thin); scoring a verse's *exclusive* share of each block
caps 5,516 (fairness-shaped, and it would route 88% of the corpus out of the depth bands).
Both look like safety valves and are actually policy changes. **Print how many verses a
floor rule moves before trusting it** — if the number is not small and named, the rule is
wrong. And when a band or set change newly flags a verse that is already in the payload,
re-author it; deleting it, or leaving a spliced entry that cannot meet its floor, are both
worse.

## Raising a floor is a three-file change or it is a lie

The bands live in `BAND` in `tools/tier_verses.py`; `data/plan.json` is generated
from it; `tools/verify_verse.py`, `tools/tests/style-check.js` and
`tools/compile_guidance.py` all read the plan and apply `× 0.75`. Editing the
docs only gives you a rule nothing enforces; editing the plan by hand gives you a
number the next `tier_verses.py` run overwrites. Raise `BAND`, re-run
`tools/tier_verses.py`, and check the diff says `tier changes: 0` — the bands move
word counts, not tiers, and if a tier moved you changed the classifier by
accident.


## The upstream corpus is not clean: the Asbāb file is 64% someone else's book

`spa5k/tafsir_api`'s `en-asbab-al-nuzul-by-al-wahidi` was integrated on
2026-10-08, dropped, and re-integrated on 2026-10-09 through a guard. The reason
it is not simply ingested: **693 of its 1,089 entries begin with text that is in
`en-al-qushairi-tafsir`**, and 120 repeat themselves inside the same file. Load it
as it comes and you publish al-Qushayrī's mystical prose under
"al-Wāḥidī, occasions of revelation" — a fabricated attribution, at scale, in the
one direction the maintainer forbids.

`tools/build_sets.py` keeps an entry only if it cites a `[surah:ayah]` of its own
surah (the book's structure, not a range inferred from where it sits) and matches
no al-Qushayrī entry, tested at two offsets because the contamination is not
always at the start. **395 of 1,089 survive.** `tools/tests/sets-integrity.js`
re-checks the shipped data, so loosening the guard fails the suite rather than
passing quietly.

The lesson generalises: a new source is not a number of words, it is a chain of
custody. Before adding an edition, test it *against the other editions in the
same repo* — cross-file duplication is invisible to a coverage check and obvious
to a substring one.

## Two failure modes when you add a set to the payload

**Rebuild, never merge.** `build_sets.py` writes `sets[id]` and then points
`verses[ayah][id]` at block indices. On the first run I forgot to clear the
previous mapping, so verses kept indices from the earlier blocks array — indices
*in range* but pointing at the wrong commentary. Nothing raised; the reader would
have shown a plausible, wrong paragraph. The builder now deletes the set's old
blocks and every per-verse index for it before writing, and
`sets-integrity.js` asserts index/range consistency over all 114 files.

**A selective set breaks an "every verse has N sources" assumption.** The reader's
`getVerseCommentaryAll` skips a set with no text (so the UI is fine), but the
corpus harness asserted `length === 6` per verse and the classifier indexed
`m[sid]` directly. Both now express the real invariant — the six *primary* sets
always, plus never a stale or empty card — and every count the harnesses check is
derived from the payload instead of hard-coded. A test that pins a count is a
test that will be weakened the first time the data legitimately changes.

## Adding a source moves tiers; raising a band does not

`BAND` changes rewrote 6,236 word targets and moved **0** tiers. Adding
al-Qushayrī and al-Wāḥidī moved **147** tiers (B→A in the long Medinan sūrahs) on
top of 2,080 word targets, because the classifier scores what the sources say
about each verse, and it can now see more of it. So the order matters: change the
corpus, re-run `tools/tier_verses.py`, and *then* argue about bands. Reading the
`tier changes` line is the difference between a plan update and an unexplained
rewrite of the queue.


## Compiled-mode gates that fire for reasons other than the obvious one

Found authoring 2:21–2:35 on 2026-10-10. Each cost a needless round because the
message points at the wrong file.

- **A BANNED verb inside a *quote of the translation*.** The refusal list for
  `said`/`says`/`adds`/`forbids` ran over the whole `~` line, including words inside
  quotation marks, so 2:30 could not quote `Remember when your Lord said to the angels`
  and 2:31 could not quote `if what you say is true` — and a lead that cannot quote a
  phrase fails the coverage gate instead. `compile_guidance.prov_ok` now excuses a
  refused word when it occurs in that verse's own `ayah_en` (`tr_all`). If a BANNED hit
  survives that exemption the verb is yours, not the verse's: reword it. Do not
  paraphrase the translation to get past a gate, and do not widen the exemption to
  spliced source sentences, which is the only thing standing between this pipeline and
  invented attribution.
- **A quote broken by the translation's own punctuation.** Coverage is canonical
  (case, diacritics, `˹…˺` stripped) but the 5-consecutive-word rule is raw, so
  `"We cautioned, O Adam"` fails on length while `"We cautioned, O Adam! Live with your
  wife in Paradise"` covers both. Quote the run as it is printed.
- **A compound phrase split by an intervening clause does not cover.** `…the
  disbelievers", whose whole difficulty is a question, "they argue…` leaves
  `"the disbelievers, they argue"` uncovered. Keep a chunk contiguous, or quote the
  whole span and explain after the closing quote.
- **7 headings, and nobody says which one to drop.** The cap is 3–6; the fix is to
  merge a thin pair into one heading with both ref lists, not to delete a source.
- **Tier A leads are measured against 20% of the entry, so adding sections raises the
  lead's own target.** A 1,392-word entry needs a 279-word lead; the same words at
  1,150 need 240. Lengthen the lead last, after the sections stop moving.

## A patch script that `assert`s mid-way writes nothing

Spec fixes are applied by a Python script that reads the file, replaces, and writes at the
end. When one `assert a in s` raised, the write never ran: the file stayed exactly as it
was, and the next `--dry` reported the failures I had just "fixed", which read like the
gate ignoring its own message. Patch with `if a in s: … else: print('MISS', …)` and read
the report. The same rule made `tools/fill_quotes.py` idempotent rather than fatal.

## A harness port is configuration, not a constant

`tools/tests/sources-all.js` and `tools/tests/guidance-001.js` had `127.0.0.1:8000`
hard-wired. When the preview moved to 8090 both died with `ECONNREFUSED`, which looks
like a broken payload. They now read `BASE` (default unchanged). Anything that reaches a
server from a test takes its address from the environment.

## A stale entry point is worse than no entry point

`AGENTS.md`'s state table said **0 of 6,236 verses, resume at 1:1** while `data/` held 42
authored verses. A new session that trusted it would have re-authored chapters 1 and 2 or
"restored" them from history. The rule now written into `AGENTS.md`: the table is a
snapshot, `python3 tools/progress.py --next` and the payload files win, and **the table is
updated in the same commit as the payload it describes**.

## Heading proof and the retired auto fill (2026-10-10)

- **Every heading is written from its own sources.** A heading is a question or a part of the verse that needs explaining. The sentences cited under it must answer that question or explain that part, in full.
- **Real content, not a term.** The gate requires each heading to cite at least two source sentences carrying its key terms, totalling at least 60 words. A key term alone is not enough. The gate measures coverage; the writer must still read the sources in full.
- **The automatic fill is retired.** The compiler no longer appends unlabelled sentences under a generic heading such as "What else the same passage holds". A `+auto` line fails the gate.
- **The sources are read completely before writing.** Comprehensive, detailed and helpful is the standard.
