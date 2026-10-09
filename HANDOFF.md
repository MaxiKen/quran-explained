# HANDOFF — read this first

You are continuing a project that is **partially complete and in good order**.
Everything you need is in this repository and on this branch. Nothing depends
on a previous chat session.

**Start by reading [`docs/progress.md`](docs/progress.md)** — it says exactly
which verse to resume at. Then follow [`docs/workflow.md`](docs/workflow.md).

---

## What this project is

A Qurʾān reader app. The work in progress is its **commentary layer**: every
verse gets an authored, single-voice commentary that reads the six classical
tafsīrs together and explains the app's own English translation, quoting its
actual words.

Three layers, all working:

1. **`data/tafsir_NNN.json`** — six complete English tafsīrs on all 6,236
   verses, 1.92× the previous corpus. Generated, committed, done.
2. **`data/plan.json`** — a fitted classifier that gives every verse a tier and
   a word target, so a ruling or a narrative gets room and a refrain gets one
   honest paragraph. Built by `tools/tier_verses.py`, verified, done.
3. **`data/guidance_NNN.json`** — the authored commentary. **This is the
   remaining work: 18 of 6,236 verses are written.**

## The single most important instruction

> **Author more than 50 verses per session, and stop at a good place past 50.**
>
> **Commit and push at the end of every session.**

Both are standing maintainer instructions. Full text, with the reasoning and an
honest note about throughput, is in [`docs/batching.md`](docs/batching.md).

The push rule is not bureaucratic. The workspace was reset mid-project once,
destroying the local tree entirely; everything survived only because it had
been pushed. See [`docs/pitfalls.md`](docs/pitfalls.md#the-workspace-can-be-reset).

## Do this first

```bash
git log --oneline -3                                  # confirm you are where progress.md says
python3 tools/progress.py --next                      # the exact verse to resume at
python3 -m http.server 8000 --bind 0.0.0.0 &          # must bind 0.0.0.0 for the preview
curl -s -o /dev/null -w "%{http_code} %{size_download}\n" \
  http://127.0.0.1:8000/data/tafsir_002.json          # must be 200 and ~3.4M
```

If that last line returns **19 bytes**, the workspace has been reset. Recover
before doing anything else:

```bash
git fetch origin arena/2c46b8a2-quran-explained
git reset --hard origin/arena/2c46b8a2-quran-explained
```

## The loop, in short

```bash
python3 tools/dump_sources.py 2 8 60      # read the sources BEFORE writing
cp tools/author_template.py /tmp/g.py     # fill in SURAH and the VERSES dict
python3 /tmp/g.py                         # writes data/guidance_002.json

npm i jsdom --prefix /tmp/apptest         # once per session
export NODE_PATH=/tmp/apptest/node_modules
for h in sources-all guidance-112 guidance-001 guidance-002; do
  printf "%-16s " "$h:"; node tools/tests/$h.js 2>&1 | tail -1
done

git add -A && git commit -m "..." && git push origin arena/2c46b8a2-quran-explained
```

Every step is explained in [`docs/workflow.md`](docs/workflow.md).

## The documents

| file | what it is for |
|---|---|
| [`docs/progress.md`](docs/progress.md) | **where you are** — resume point, commit chain, what is deferred |
| [`docs/workflow.md`](docs/workflow.md) | the session loop, step by step |
| [`docs/batching.md`](docs/batching.md) | the 50-verse rule and the push rule, verbatim from the maintainer |
| [`docs/voice.md`](docs/voice.md) | **how to write it** — structure, register, what each tier contains |
| [`docs/classifier.md`](docs/classifier.md) | how tiers are assigned, and the known weakness on narrative verses |
| [`docs/contracts.md`](docs/contracts.md) | the four payload shapes and what breaks if you change one |
| [`docs/testing.md`](docs/testing.md) | the harnesses, how to add one, the attribution check |
| [`docs/integrity.md`](docs/integrity.md) | **synthesis is required, fabrication is forbidden** |
| [`docs/pitfalls.md`](docs/pitfalls.md) | everything that has already gone wrong, so it does not again |
| [`docs/sources.md`](docs/sources.md) | the six tafsīrs, provenance, what is and is not reachable |
| [`ATTRIBUTION.md`](ATTRIBUTION.md) | licence notices and upstream provenance, shipped with the data |

## The tools

| file | purpose |
|---|---|
| `tools/tier_verses.py` | classify all 6,236 verses → `data/plan.json`; `--verify` re-runs the validation |
| `tools/dump_sources.py` | print translations + plan + six sources for a verse range. **The read-before-you-write step** |
| `tools/author_template.py` | template for building a guidance file; enforces the payload shape and scans for homoglyphs |
| `tools/progress.py` | what is authored, what is next |
| `tools/tests/sources-all.js` | six-source payload, all 114 files, read-aloud |
| `tools/tests/guidance-112.js` | authored layer, sūrah 112 |
| `tools/tests/guidance-001.js` | authored layer, sūrah 1 |
| `tools/tests/guidance-002.js` | authored layer, sūrah 2 (partial) |

## Things that will otherwise cost you an hour

- **The six tafsīr payloads are one long line each.** GitHub renders the diff
  as blank and it looks like 31 MB vanished. It did not — verify with the
  *blobs* API, not the contents API (which returns empty past 1 MB).
- **Do not pretty-print `data/plan.json`.** At 1.29 MB it passes GitHub's 1 MB
  display limit and stops rendering. Tried and reverted.
- **Do not hard-code a control sūrah in a harness.** Doing so broke two
  harnesses. They now pick one dynamically.
- **`getVerseCommentary` returns a string.** The array version is
  `getVerseCommentaryAll`.
- **Never rule out paraphrase.** Synthesis from the real sources *is* the task.
  What is forbidden is fabrication — invented ḥadīth numbers, misattributed
  quotes. `docs/integrity.md` draws the line.

## Verification state at the time of writing

`sources-all` 27/27 · `guidance-112` 28/28 · `guidance-001` 47/47 ·
`guidance-002` 55/55 · `tier_verses.py --verify` exit 0.

Branch `arena/2c46b8a2-quran-explained`, PR #89 open against `main`.
**Always work on that branch; never create or push another.**
