# HANDOFF — current continuation point

Read [`AGENTS.md`](AGENTS.md) first. It is the normative workflow, source, style,
and testing contract. This file records only the current data state.

## Position after the 2026-10-11 batch

- **Written:** 300 of 6,236 verses; 428,310 planned words represented in the
  guidance layer.
- **Complete:** Sūrah 1, verses 1–7; Sūrah 2, verses 1–286.
- **In progress:** Sūrah 3, verses 1–7.
- **Last batch:** compiled 2:284–2:286 and 3:1–3:7 from curated,
  heading-relevant source selections. Their output lengths are 1,401, 1,411,
  1,717, 1,126, 931, 995, 1,230, 654, 927, and 2,159 words.
- **Cache:** `sw.js` uses `quran-reader-v1.5.3-3-7`.
- **Branch:** `arena/dce9f1ba-quran-explained`.
- **Verification:** 286/286 chapter-2 verse checks, 7/7 chapter-3 verse checks,
  9/9 style checks, 32/32 render checks, 12/12 set-integrity checks, 30/30
  source-rendering checks, and 52/52 chapter-1 guidance-rendering checks passed.

`python3 tools/progress.py --next` now resumes at **3:8**. The next batch is
3:8–3:17 and uses the compiled workflow. The next authored-only verse in this
surah is 3:78, so it is not part of the immediate continuation.

## Resume checklist

1. Confirm the resume point with `python3 tools/progress.py --next`.
2. Read the relevant source packets fully before making a spec.
3. Compile only after the spec passes `--dry`; run the mandatory full suite at each
   completed batch boundary.
4. Bump `sw.js`, update this handoff and `docs/progress.md`, commit, and push
   `arena/dce9f1ba-quran-explained` at the end of each batch.
