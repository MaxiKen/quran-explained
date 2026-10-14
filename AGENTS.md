# Agent instructions for this repository

This is a static Qur'an reader (no build step) with eight classical tafsīrs per
verse, plus an ongoing project that writes an original **plain-English
commentary for every verse and every surah** from those eight texts and
publishes it as `data/guidance_NNN.json`.

If you are here to continue that project, **everything you need is in
`tools/guidance/HANDOFF.md`**. Read it completely before acting. The design
decisions in its §2 are final; do not ask the maintainer about them again.

Start of session:

```bash
bash tools/guidance/resume.sh          # git realignment, tests, progress, next job
python3 tools/serve.py 8000            # run with the process tool so the preview stays up
```

Then follow HANDOFF §4 job by job, three tool calls per job: read all of
`digest.py <job>` (checklist + material), write `work/raw/<job>.md`, run
`finish.py <job>` (gates, publish, commit, push, next job).

Non-negotiables (details and reasons in the handoff):

- Write only from the material in the job. No outside knowledge, names, grades or verse numbers.
- Never name the eight works or their authors; one anonymous voice.
- No Arabic script (ﷺ only), no em dashes or semicolons outside quotes, plain English.
- Length is proportional to the material (≈ 0.6 ×), never a band, never padded.
- Every verse gets its own self-contained entry; every surah gets an introduction. Surahs are done strictly in order, 1 → 2 → 3 … 114.
- Never publish a `fail`; never use `--include-failed`; never relax `verify.py` to pass an entry.
- Work only on the session's branch, commit after every job, push every time, never force-push.
- Keep `tools/guidance/HANDOFF.md` §8 (progress log) current before you stop.

The paste-able prompt for starting a new session is `tools/guidance/CONTINUE_PROMPT.md`.
