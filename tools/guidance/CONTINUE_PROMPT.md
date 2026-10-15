# Start a chapter in a new session

Once the current pipeline/setup instructions are in the checkout, you only need
to send a chapter number, for example:

```text
18
```

That requests the introduction and every verse of chapter 18, or resumption of
its incomplete work. Numbers 1–114 are accepted. Later chapters may be generated
before earlier chapters. Each session stays on its assigned branch and selected
chapter. A completed chapter is reported, not automatically regenerated.

## Optional pasteable prompt

Generate or resume chapter **18** in this repository. Follow AGENTS.md,
HANDOFF.md and CHAPTER_RUN.md. Read the authoring prompts and exemplars, then
work autonomously without asking me to repeat established design decisions.

1. Inspect the working tree and record the session branch and starting commit
   in `tools/guidance/chapters/018.md`. Do not switch branches or overwrite other
   work. The checkout must already include these setup instructions; do not
   import a historical content branch wholesale.
2. Use `python3 tools/guidance/status.py --next --surah 18`. Write the intro,
   then verse jobs in verse order, reading every digest part. Resume existing
   entries and retain approved exemplars. Earlier chapters need not be complete.
3. Use `finish.py JOB` for per-job ingestion, work gates, assembly, commit and
   push. It does not run full published-chapter verification or advance to a
   different chapter. Correct failures and substantive omissions with scoped
   checks before finalization. Do not relax any verification gates.
4. Run FULL CHAPTER VERIFICATION **once**, only after the introduction and every
   verse have been fully generated and intended repairs finished. Do not run
   it on a partial chapter or after every job, batch, push or session. Record
   the result and payload hash in the chapter-local receipt; reuse a matching
   receipt on resume. Stop and report unexpected final failures rather than
   silently repeating full checks. See CHAPTER_RUN.md for later-change policy.
5. Change only this chapter's payload, raw drafts and chapter-local report.
   Do not edit shared instruction/progress files, other chapter content or UI
   files. Never stage unrelated changes. Keep the source-grounded anonymous
   voice, all substantive coverage, collectors/grades and disagreements.
6. At completion, run tests and render/raw consistency checks as prescribed,
   finalize `tools/guidance/chapters/018.md`, commit/push and stop. End with the
   exact list of every created/updated/deleted file, including ignored scratch
   outputs separately, branch, base/final commits, verification result and
   chapter-only merge allowlist. Inspect inherited branch changes before
   suggesting a chapter-only PR; never overwrite newer main or merge without
   authorization.

Replace 18/018 with the chapter requested. Do not start another chapter until
I give its number.

## Historical checkpoint

Surahs 1 and 2 are complete. Al-Baqarah's baseline flags were reviewed; its last
full published-data check found 272 ok, 15 reviewed residual flags and zero
failures over 287 entries. Those results are not scholarly certification and
are not a reason to reverify chapter 2 when generating a different chapter.
Use chapter payloads and chapter-local receipts for live status, not this
historical checkpoint.
