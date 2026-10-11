# Progress

**Data-derived status, updated 2026-10-11.** `python3 tools/progress.py --next`
is authoritative; this page is a convenience snapshot for the next session.

| | |
|---|---|
| Written | **290 of 6,236 verses** (4.65%) |
| Planned guidance represented | **415,190 of 5,902,150 words** (7.03%) |
| Complete guidance files | `guidance_001.json` (7 verses) and `guidance_002.json` (283 verses) |
| Empty, intentional fallback | `guidance_112.json` |
| Next verse | **2:284**, compiled |
| Remaining in Sūrah 2 | **3 verses** (2:284–2:286) |
| Working branch | `arena/dce9f1ba-quran-explained` |

## Latest batch: 2:274–2:283

This compiled ten-verse batch uses curated, heading-relevant source selections.
The emitted entries are 1,311, 1,881, 1,212, 1,622, 1,678, 1,451, 1,663,
1,576, 2,295, and 1,469 words respectively. Each records 6–8 source sets. The
service-worker cache version is `quran-reader-v1.5.3-2-283`.

## Next work

Continue sequentially with **2:284**. The next batch crosses the chapter boundary:
2:284–2:286 followed by 3:1–3:7. Use the compiled workflow for each verse,
curate heading-relevant references, dry-compile, and gate the completed batch.

## Verification for the latest batch

- `python3 tools/verify_verse.py 2 --all`: **283/283** verses pass.
- `node tools/tests/style-check.js`: **9/9** checks pass.
- Render gate: **23/23** checks pass.
- Set integrity: **12/12** checks pass.
- Source rendering: **30/30** checks pass.
- Chapter-1 guidance rendering: **52/52** checks pass.

The format, source policy, batching guidance, and required test commands live in
[`../AGENTS.md`](../AGENTS.md), [`voice.md`](voice.md), and [`workflow.md`](workflow.md).
