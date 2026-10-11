# Progress

**Data-derived status, updated 2026-10-11.** `python3 tools/progress.py --next`
is authoritative; this page is a convenience snapshot for the next session.

| | |
|---|---|
| Written | **310 of 6,236 verses** (4.97%) |
| Planned guidance represented | **441,650 of 5,902,150 words** (7.48%) |
| Complete guidance files | `guidance_001.json` (7 verses) and `guidance_002.json` (286 verses) |
| In progress | `guidance_003.json` (3:1–3:17) |
| Empty, intentional fallback | `guidance_112.json` |
| Next verse | **3:18**, compiled |
| Next authored-only verse | **3:78** |
| Working branch | `arena/dce9f1ba-quran-explained` |

## Latest batch: 3:8–3:17

This compiled batch continues Āl ʿImrān sequentially. The emitted entries are
943, 1,089, 961, 1,142, 1,272, 1,916, 1,857, 1,535, 868, and 1,623 words for
3:8–17 respectively. Each records 6–7 source sets. The service-worker cache
version is `quran-reader-v1.5.3-3-17`.

## Next work

Continue sequentially with **3:18**. The next ten-verse batch is 3:18–3:27;
all of these entries use the compiled workflow. Re-dump source packets, curate
heading-relevant references, dry-compile, and gate the completed batch.

## Verification for the latest batch

- `python3 tools/verify_verse.py 2 --all`: **286/286** verses pass.
- `python3 tools/verify_verse.py 3 --all`: **17/17** verses pass.
- `node tools/tests/style-check.js`: **9/9** checks pass.
- Render gate: **32/32** checks pass.
- Set integrity: **12/12** checks pass.
- Source rendering: **30/30** checks pass.
- Chapter-1 guidance rendering: **52/52** checks pass.

The format, source policy, batching guidance, and required test commands live in
[`../AGENTS.md`](../AGENTS.md), [`voice.md`](voice.md), and [`workflow.md`](workflow.md).
