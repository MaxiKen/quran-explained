# Prompt to start a new session and continue automatically

Paste the block below as the first message of a new Arena session on
`MaxiKen/quran-explained`. It works whether or not the pipeline branch has been
merged to `main` yet.

---

Continue the plain-English commentary project in this repository. Work autonomously; all design decisions were made and recorded, so do not ask me about them.

1. If `tools/guidance/HANDOFF.md` is not in your checkout, bring the pipeline in without leaving your session branch:
   `git fetch origin arena/ea88d543-quran-explained && git merge --no-edit origin/arena/ea88d543-quran-explained`
2. Read `AGENTS.md` and `tools/guidance/HANDOFF.md` completely. Then read `tools/guidance/prompts/system.md`, `prompts/verse_job.md`, `prompts/exemplars/001_002.md`, and the published entries for 1:4 and 1:6 in `data/guidance_001.json`, so your writing matches the calibration.
3. Run `bash tools/guidance/resume.sh`. It realigns git if the sandbox rewound, runs the tests and prints the next job. Start the preview with the process tool: `python3 tools/serve.py 8000`.
4. Work in strict surah order, 1 → 2 → 3 … 114 (the next pending job is whatever `status.py --next` prints, intro first, then verses in order). Work job by job exactly as HANDOFF §4 says, three tool calls per job: read every part of `python3 tools/guidance/digest.py <job>` (parts in parallel; the checklist at the top is what the gates want), write the whole job to `work/raw/<job>.md` with the `<<<VERSE S:N>>>` markers, then `python3 tools/guidance/finish.py <job>` (it ingests, runs the gates, publishes, commits, pushes and prints the next job; if it reports a FAIL, fix the raw file and run it again). Continue to the next job in the same turn.
5. Rules that must never bend: write only from the job's material; never name the eight tafsīr works or their authors; no Arabic script, no em dashes or semicolons outside quotes; length proportional to the material; one entry per verse plus a surah introduction; never publish a `fail`, never use `--include-failed`, never loosen `verify.py` to pass an entry; stay on the session branch; never force-push.
6. Push after every job. Before you stop (end of context or when I say stop), make sure everything is committed and pushed, add a row to HANDOFF §8 for what you published, and give me a short report: surahs and verses published, words, ok/flag counts, anything needing my decision.

Begin with step 1 now.

---

If the maintainer has enabled the GitHub Actions path (secrets added, workflow on
`main`), say so in the first message instead, e.g. *"Secrets are set; run the
pilot through Actions (HANDOFF §7) and then verify and spot-read the output."*
