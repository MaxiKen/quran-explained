# HANDOFF — current continuation point

Read [`AGENTS.md`](AGENTS.md) first. It is the normative workflow, source, style,
and testing contract. This file records only the current data state.

## Position after the 2026-10-11 batch

- **Written:** 260 of 6,236 verses; 366,970 planned words represented in the
  guidance layer.
- **Complete:** Sūrah 1, verses 1–7; Sūrah 2, verses 1–253.
- **Last batch:** compiled 2:250–2:253 from the source packets. The emitted
  commentary lengths are 1,035, 1,331, 601, and 1,594 words respectively; all
  are over their per-verse floors and use 6, 6, 6, and 7 source sets.
- **Cache:** `sw.js` now uses `quran-reader-v1.5.3-2-253`.
- **Branch:** `arena/dce9f1ba-quran-explained`.
- **Verification:** 253/253 verse checks, 9/9 style checks, 23/23 render checks,
  12/12 set-integrity checks, 30/30 source-rendering checks, and 52/52 chapter-1
  guidance-rendering checks passed.

`python3 tools/progress.py --next` now resumes at **2:254**. It is
`authored_only`: the available source material is 1,114 words against a 1,185-word
floor, so do not pass it to `compile_guidance.py`. Compose it from its complete
source blocks and gate it with `verify_verse.py --file --draws --names`. The next
such verse in al-Baqarah is 2:257. Keep the sequence, do not jump ahead, and do
not turn a thin verse into a compiled splice.

## Resume checklist

1. Confirm the resume point with `python3 tools/progress.py --next`.
2. For 2:254, read the full blocks with `python3 tools/dump_sources.py 2 254 254 --all`.
3. Follow the authored path in `docs/voice.md` and `docs/workflow.md`; names and
   claims must occur in 2:254's own source blocks.
4. Run the full verification suite, commit, and push **this branch** at the end of
   the next batch.

The prior handoff described earlier cleared and regenerated states. It is retained
in Git history, not as an instruction for the current payload.
