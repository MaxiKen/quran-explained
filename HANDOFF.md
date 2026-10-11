# HANDOFF — current continuation point

Read [`AGENTS.md`](AGENTS.md) first. It is the normative workflow, source, style,
and testing contract. This file records only the current data state.

## Position after the 2026-10-11 batch

- **Written:** 270 of 6,236 verses; 383,820 planned words represented in the
  guidance layer.
- **Complete:** Sūrah 1, verses 1–7; Sūrah 2, verses 1–263.
- **Last batch:** 2:254–2:263. Verses 2:254 and 2:257 are authored-only entries;
  the remaining eight entries were compiled from curated, heading-relevant source
  selections. Their output lengths are 1,475, 1,831, 2,468, 1,402, 1,817, 1,773,
  1,928, 1,947, 1,830, and 1,337 words.
- **Cache:** `sw.js` uses `quran-reader-v1.5.3-2-263`.
- **Branch:** `arena/dce9f1ba-quran-explained`.
- **Verification:** 263/263 verse checks, 9/9 style checks, 23/23 render checks,
  12/12 set-integrity checks, 30/30 source-rendering checks, and 52/52 chapter-1
  guidance-rendering checks passed.

`python3 tools/progress.py --next` now resumes at **2:264**. It is compiled,
and all remaining verses of al-Baqarah (2:264–2:286) are eligible for the compiled
workflow. Keep the sequence and use dry compilation with curated source references.

## Resume checklist

1. Confirm the resume point with `python3 tools/progress.py --next`.
2. Read the relevant source packets fully before making a spec.
3. Compile only after the spec passes `--dry`; run the mandatory full suite at each
   completed batch boundary.
4. Bump `sw.js`, update this handoff and `docs/progress.md`, commit, and push
   `arena/dce9f1ba-quran-explained` at the end of each batch.
