# Parallel runs — several agents, one `main`

As of 2026-10-12 the maintainer runs **several authoring agents at the same
time**, on different parts of the commentary, to finish the corpus on time.
Chapters are **not** authored in order any more. This file is the contract that
keeps concurrent runs from overwriting each other when they merge to `main`.
The short version: **everyone branches from `main`, claims their work before
writing, and touches only their own files.**

## The loop

1. **Branch from `main`.** Every run starts at the same `main` commit. Your
   branch name is yours alone (`arena/<id>-quran-explained` in this project).

2. **Claim before writing.** Register the ranges you are taking:

   ```bash
   python3 tools/progress.py --claim 4:1-50 --agent agent-a \
       --branch arena/73fc335e-quran-explained --note "ch. 4 opening"
   ```

   This writes `data/runs/agent-a.json` — **your file, yours alone**. Commit
   and push it immediately so the other runs can see the claim. Pick any agent
   name (`[A-Za-z0-9._-]+`); it is the identity progress records under.

3. **Author in batches** exactly as [`workflow.md`](workflow.md) describes
   (packet → spec → compile → verify → commit → push). After each batch, record
   it and append a cache stamp:

   ```bash
   python3 tools/progress.py --batch 4:1-10 --agent agent-a --commit $(git rev-parse --short HEAD)
   # in sw-stamps.js, APPEND one line inside RUN_STAMPS — never edit anyone else's:
   #   'ch4-1-10-2026-10-12-agent-a',
   ```

4. **Close what you finished** (and what you will not finish — a released
   claim is as useful as a closed one):

   ```bash
   python3 tools/progress.py --done 4:1-50 --agent agent-a --note "chapter 4 opening lands"
   python3 tools/progress.py --done --agent agent-a      # close the whole run
   ```

5. **Regenerate the aggregate** before you push, so `docs/progress.md` reflects
   your run alongside the others:

   ```bash
   python3 tools/progress.py --report
   ```

6. **Merge to `main` whenever you are done** — early is fine. Others may still
   be working; that is the point. See "Merge rules" below.

## File ownership — why merges do not overwrite

| file | who touches it | merge behaviour |
|---|---|---|
| `data/guidance_NNN.json` | the one run that claimed chapter N | one owner per chapter, so no two branches write it |
| `data/runs/<agent>.json` | only that agent | disjoint by construction |
| `sw-stamps.js` | everyone, **append-only** | `merge=union` in `.gitattributes` — additions concatenate |
| `docs/progress.md` | **nobody** — generated | on conflict: re-run `tools/progress.py --report`, take the result |
| `tools/tests/guidance-NNN.js` | the run that authored chapter N | new file per chapter |
| `data/plan.json` | nobody, ad hoc | regenerated only by `tools/tier_verses.py` in a coordinated change |
| `AGENTS.md`, `docs/*.md` | only for **rule** changes | do not record per-batch state in them any more |

The hard rule behind the table: **one open claim per chapter across all
agents.** `data/guidance_NNN.json` is a single file, so two runs writing one
chapter concurrently would merge-overwrite each other there. `--claim` refuses
a second claimant and `--check` fails if one ever appears. To share a big
chapter, hand off in time (one run closes its range, the next claims the rest)
— not in parallel.

Verse ranges *within* your claim are up to you (`--claim 4:1-50`, `--claim 4`,
`--claim 4:7` are all valid). Batches need not arrive in order either:
`--batch 4:21-30` inside a `4:1-50` claim is fine.

## Merge rules

- **Only your files change.** If a merge would touch a file you did not author,
  stop and split the change. A run's diff is: its `data/guidance_NNN.json`, its
  `data/runs/<agent>.json`, its `tools/tests/guidance-NNN.js`, an appended
  `sw-stamps.js` line, and — if needed — a regenerated `docs/progress.md`.
- **Never edit another agent's run file.** If their claim is stale (agent gone,
  range untouched for days), the maintainer releases it; runs do not steal.
- **Generated files are resolved by regeneration, never by hand:**
  `docs/progress.md` → `python3 tools/progress.py --report`;
  `data/plan.json` → `python3 tools/tier_verses.py` (coordinated changes only).
- **`sw-stamps.js` conflicts mean both sides appended** — keep both lines. The
  `merge=union` attribute normally does this for you.
- **Rebase or merge `main` before your final push** if others have landed
  already; the whole point of the ownership table is that this is boring.
- After any merge to `main`, run `python3 tools/progress.py --check` once. It
  fails loudly if two claims ever collided.

## Claims are the map; the data is the truth

`python3 tools/progress.py --next` lists **every** surah with verses left —
unclaimed ones are yours to take, claimed ones name their owner — and
`--next --agent NAME` prints the resume points inside your own claims. The
corpus totals come from `data/guidance_*.json`, so they are right no matter how
many runs are in flight or in what order the chapters landed. Never re-author a
verse the data already carries; never trust a narrative doc over `--next`.

`docs/progress.md` documents **every run on record**: its branch, its claims,
its batches, its word counts. That is the file the maintainer reads to see who
did what; per-run narratives (optional) go in `docs/runs/<agent>.md` and are
linked from the run record.

## Why the pace rule still applies

Parallel runs change *who* works at once, not *how* each verse is made. Every
run keeps the standard in [`style.md`](style.md), [`voice.md`](voice.md) and
[`workflow.md`](workflow.md): read the sources, write to the contract, gate the
batch, push every batch. A run that cannot meet a count says so in its run
record rather than shipping thin commentary.
