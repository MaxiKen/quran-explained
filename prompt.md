# Quran Explained — Tafsir Production Prompt

**Status: superseded. This file is no longer the brief.**

It is kept only because `docs/progress.md` and old commit messages refer to it.
It described a two-sided length band, a `## **SURAH:VERSE**` heading format, and
a scope of "2:231–2:286" that was never merged — all of it is wrong now, and its
claims about completed chapters were wrong even when they were true of nothing
in this checkout.

**Read these instead, in this order:**

1. [`AGENTS.md`](AGENTS.md) — the entry point: what the project is, the two
   production modes, the checks to run, and what is already in the repo.
2. [`docs/style.md`](docs/style.md) — the normative format spec: the
   explanatory opening paragraph, 3–6 own-line `**Headings.**`, the tier bands
   and the one-sided floor.
3. [`docs/voice.md`](docs/voice.md) — the register, what each tier contains, and
   how the compiled mode differs from the authored one.
4. [`docs/workflow.md`](docs/workflow.md) and
   [`docs/progress.md`](docs/progress.md) — the batch loop and where to resume.

Rules that were stated here and still hold, restated where they belong:

| old rule | now |
|---|---|
| one `## **SURAH:VERSE**` heading per verse | rejected — own-line `**Like this.**` subheadings; `docs/style.md` §1 |
| length must sit within 25% of target | rejected — a floor, never a band; `docs/style.md` §2 |
| "do not fabricate content" | kept and strengthened — compiled verses cannot express an unsourced claim at all; `docs/voice.md` |
| build with `scripts/build_tafsir_json.py` | no such script in this checkout — the app is static and served as it is; guidance JSON is written by `tools/compile_guidance.py` |
