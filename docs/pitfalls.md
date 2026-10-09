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

**Recovery:**
```bash
git fetch origin arena/2c46b8a2-quran-explained
git reset --hard origin/arena/2c46b8a2-quran-explained
```

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
