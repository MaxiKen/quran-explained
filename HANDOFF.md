# HANDOFF — current continuation point

Read [`AGENTS.md`](AGENTS.md) first. It is the normative workflow, source, style,
and testing contract. This file records only the current data state.

## Position after the 2026-10-11 batch

- **Written:** 290 of 6,236 verses; 415,190 planned words represented in the
  guidance layer.
- **Complete:** Sūrah 1, verses 1–7; Sūrah 2, verses 1–283.
- **Last batch:** compiled 2:274–2:283 from curated, heading-relevant source
  selections. Their output lengths are 1,311, 1,881, 1,212, 1,622, 1,678,
  1,451, 1,663, 1,576, 2,295, and 1,469 words.
- **Cache:** `sw.js` uses `quran-reader-v1.5.3-2-283`.
- **Branch:** `arena/dce9f1ba-quran-explained`.
- **Verification:** 283/283 verse checks, 9/9 style checks, 23/23 render checks,
  12/12 set-integrity checks, 30/30 source-rendering checks, and 52/52 chapter-1
  guidance-rendering checks passed.

`python3 tools/progress.py --next` now resumes at **2:284**. The next ten-verse
batch crosses into Sūrah 3: 2:284–2:286, then 3:1–3:7. Use dry compilation with
curated source references and retain the chapter sequence.

## Resume checklist

1. Confirm the resume point with `python3 tools/progress.py --next`.
2. Read the relevant source packets fully before making a spec.
3. Compile only after the spec passes `--dry`; run the mandatory full suite at each
   completed batch boundary.
4. Bump `sw.js`, update this handoff and `docs/progress.md`, commit, and push
   `arena/dce9f1ba-quran-explained` at the end of each batch.
