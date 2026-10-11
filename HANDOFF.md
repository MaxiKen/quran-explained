# HANDOFF — current continuation point

Read [`AGENTS.md`](AGENTS.md) first. It is the normative workflow, source, style,
and testing contract. This file records only the current data state.

## Position after the 2026-10-11 batch

- **Written:** 310 of 6,236 verses; 441,650 planned words represented in the
  guidance layer.
- **Complete:** Sūrah 1, verses 1–7; Sūrah 2, verses 1–286.
- **In progress:** Sūrah 3, verses 1–17.
- **Last batch:** compiled 3:8–3:17 from curated, heading-relevant source
  selections. Their output lengths are 943, 1,089, 961, 1,142, 1,272, 1,916,
  1,857, 1,535, 868, and 1,623 words.
- **Cache:** `sw.js` uses `quran-reader-v1.5.3-3-17`.
- **Branch:** `arena/dce9f1ba-quran-explained`.
- **Verification:** 286/286 chapter-2 verse checks, 17/17 chapter-3 verse checks,
  9/9 style checks, 32/32 render checks, 12/12 set-integrity checks, 30/30
  source-rendering checks, and 52/52 chapter-1 guidance-rendering checks passed.

`python3 tools/progress.py --next` now resumes at **3:18**. The next batch is
3:18–3:27 and uses the compiled workflow. The next authored-only verse in this
surah is 3:78, so it is not part of the immediate continuation.

## Resume checklist

1. Confirm the resume point with `python3 tools/progress.py --next`.
2. Read the relevant source packets fully before making a spec.
3. Compile only after the spec passes `--dry`; run the mandatory full suite at each
   completed batch boundary.
4. Bump `sw.js`, update this handoff and `docs/progress.md`, commit, and push
   `arena/dce9f1ba-quran-explained` at the end of each batch.
