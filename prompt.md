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

Rules added on 2026-10-10 and binding everywhere:

**Headings may be questions or further explanation.** A heading can be a question the reader would ask, or a part of the verse that needs more explanation. The evidence under a heading is taken from the sources in the context of that heading only: it answers the question asked, or explains the part named. Sources are not dumped under a heading that they do not address.

**The sources are read completely before writing.** Every source used for a verse is read in full and understood, not skimmed for a quotable line. The commentary is comprehensive: the material under the headings covers what the sources say on the question, including where they differ, and it is written in one plain voice.

Rules that were stated here and still hold, restated where they belong:

| old rule | now |
|---|---|
| one `## **SURAH:VERSE**` heading per verse | rejected — own-line `**Like this.**` subheadings; `docs/style.md` §1 |
| length must sit within 25% of target | rejected — a floor, never a band; `docs/style.md` §2 |
| "do not fabricate content" | kept and strengthened — compiled verses cannot express an unsourced claim at all; `docs/voice.md` |
| build with `scripts/build_tafsir_json.py` | no such script in this checkout — the app is static and served as it is; guidance JSON is written by `tools/compile_guidance.py` |
