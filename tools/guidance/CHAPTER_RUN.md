# Chapter-number session workflow

This is the current operating policy. It supersedes older sequential-chapter,
per-job full-verification and shared-progress-log instructions.

## 1. A number is enough

A user message containing a chapter number, for example `18`, means:
**generate or resume chapter 18's introduction and all its verses** using the
existing source-grounded commentary workflow. Accept numbers 1–114, including
zero-padded forms. Ask for clarification only if the number is invalid or its
meaning is genuinely ambiguous. Do not require a longer prompt.

Chapters may be generated in any order. Chapter 18 may finish before chapter 3.
Different sessions may work on different chapters concurrently. Work only on
the requested chapter and the branch assigned to the current session. Never
switch branches, start another chapter automatically, or merge to main without
explicit authorization. An already complete chapter is not permission to
regenerate it: report its status and existing completion record instead.
Do not have two sessions write the same chapter concurrently.

## 2. Start and resume without importing unrelated changes

Read AGENTS.md, HANDOFF.md, this file, the authoring prompts and exemplars.
Use a checkout containing the current pipeline instructions; if they are missing,
ask for the setup changes to be brought in rather than merging a historical
content branch wholesale. Do not reset, overwrite, or stage another session's
work. Inspect `git status --short` first.

Record the current branch and starting commit **before any chapter edits**:

```bash
git branch --show-current
git rev-parse HEAD
python3 -m unittest discover -s tools/guidance/tests
python3 tools/guidance/status.py --next --surah 18
```

Replace `18` with the selected number in every command. Record the starting
commit as `BASE` in `tools/guidance/chapters/018.md` immediately, so a resumed
session retains the original comparison point. This chapter-local file is the
progress log and completion receipt. Do not update shared HANDOFF progress,
AGENTS.md, CONTINUE_PROMPT.md or pipeline code during routine content sessions.
Global `status.py --next` is discovery only, not authorization to change targets.
`resume.sh` is a legacy global helper; use the explicit startup commands above
for isolated chapter sessions.

The selected chapter's introduction comes first, then its verse jobs in verse
order. Read every digest part. Preserve existing published entries and approved
exemplars; write only missing entries unless repairs are requested. If scratch
outputs disappeared, reconstruct them from the chapter's existing raw drafts
or published payload before assembly. Never overwrite authoritative raw NOTES
with `--export-raw` merely for convenience.

## 3. Per-job work checks and incremental publication

```bash
python3 tools/guidance/digest.py 018-intro
# Read every remaining digest part, then write work/raw/018-intro.md.
python3 tools/guidance/finish.py 018-intro
python3 tools/guidance/status.py --next --surah 18
```

Continue the same loop for the selected chapter's verse jobs. `finish.py` now
runs work-output checks and assembly, commits the selected job's raw draft and
chapter payload, and pushes to the current session branch. It **does not run
full published-chapter verification** and it never advances to another chapter.
Inspect all job diagnostics and correct failures and substantive omissions.
Review flags honestly; never relax gates or use `--include-failed`.

The manual equivalent remains available:

```bash
python3 tools/guidance/ingest.py --job JOB --file work/raw/JOB.md
python3 tools/guidance/verify.py --source work --surahs S
python3 tools/guidance/assemble.py --surahs S
# Stage only the selected chapter payload and this job's raw file, then commit/push.
```

`JOB`, `S`, `SSS`, `BASE` and `SESSION_BRANCH` in examples are placeholders.
Per-job/work-output checks are allowed throughout generation. They are not the
full published-data chapter check. Never run that full check at session end,
after an introduction, after a batch, or after each push while verses remain.

## 4. One full check, only after the entire chapter is generated

Before the single full check:

1. Confirm a nonempty introduction and exactly every verse 1 through the
   chapter's verse count, with no gaps, blank entries or failures.
2. Finish all intended editorial repairs with scoped/work-output checks.
3. Confirm raw/published text consistency, run the pipeline tests and render
   checks, and review diagnostics. Do not change verification thresholds.
4. Check the chapter-local receipt: if full verification already ran for the
   current completed content, reuse its recorded result, do not run it again.

Then, **once for the completed chapter, not once per session**, run:

```bash
python3 tools/guidance/verify.py --source data --surahs 18
```

Immediately record the exact command, date, result, residual flags, and SHA-256
of `data/guidance_018.json` in `tools/guidance/chapters/018.md`. Record failed or
interrupted attempts too; do not silently claim success or repeatedly invoke the
full check. If a final failure occurs, stop and report it. Later content changes
invalidate that recorded verification; obtain explicit authorization for a new
full check rather than treating an old receipt as current or automatically
rerunning. Do not alter content after the final check as part of ordinary
chapter generation. This policy does not certify scholarly accuracy.

## 5. Chapter-local change manifest and handoff

At completion, and also when stopping with a partial chapter, update
`tools/guidance/chapters/SSS.md`. Include:

- Chapter number/name, session branch, starting `BASE`, latest content commit,
  generated introduction/verse ranges and complete/partial status.
- Tests, render/raw consistency results, verification state (deferred until
  complete, or the recorded single final result), exact warnings and payload hash.
- **Every created, modified, renamed or deleted file**, with repository-relative
  path, status and purpose. Include the chapter report itself. Separate committed
  merge candidates from ignored scratch outputs; list scratch job/report files
  created or updated too, but do not commit them or large datasets.
- A chapter-only merge allowlist and any shared-file exceptions. Shared changes
  need explicit authorization and separate review, not incidental staging.

Derive the tracked manifest from the saved starting commit, not merely the last
job commit. Before the final commit, inspect both committed and uncommitted work:

```bash
git diff --name-status BASE HEAD
git diff --name-status HEAD
git ls-files --others --exclude-standard
```

After staging the report, use `git diff --name-status BASE` to verify the final
tracked list includes it. After committing, record/report `git diff --name-status
BASE HEAD` and the final commit in the user-facing handoff. Do not put the final
commit's own hash inside the file it commits (use the latest content commit there).
End the response with the full created/updated/deleted file list, completion and
verification counts, branch and final commit. Never just say “several files”.

Normal merge candidates are only:

```text
data/guidance_SSS.json
work/raw/SSS-*.md
tools/guidance/chapters/SSS.md
```

Do not stage with `git add .` or `git add work/raw` across all chapters. Do not
modify other guidance payloads, chapter/tafsir datasets, global progress logs,
UI files, service-worker versions or shared manifests for a content-only run.
The reader discovers chapter payloads without a global content index update.

## 6. Merging without overwriting newer main content

Provide the allowlist, base commit and final commit so the maintainer can select
only this chapter's changes. A chapter-only PR is safest: inspect the **entire PR
file diff against current main**, not just the session's last commit. A branch
may contain earlier unmerged chapters even when the current session changed only
one chapter; disclose those inherited files and do not merge that PR wholesale.

Use a normal three-way merge for an authorized, chapter-only PR. Never copy a
whole stale branch tree over main, force-push, or resolve shared-file conflicts
by blindly choosing the session version. If the PR includes unrelated inherited
changes, transfer only the allowlisted chapter diff based on the recorded BASE
into a separately authorized integration workflow. Review that patch against
current main; concurrent changes to the **same** chapter need manual conflict
resolution. Do not do that integration in an Arena session fixed to another
branch, and do not merge/close a PR without authorization.

Different-chapter sessions normally touch disjoint paths. The isolated manifests
make selective integration possible, but do not guarantee a conflict-free merge
or replace reviewing main's latest state.
