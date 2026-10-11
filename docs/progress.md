# Progress

**Data-derived status, updated 2026-10-11.** `python3 tools/progress.py --next`
is authoritative; this page is a convenience snapshot for the next session.

| | |
|---|---|
| Written | **270 of 6,236 verses** (4.33%) |
| Planned guidance represented | **383,820 of 5,902,150 words** (6.50%) |
| Complete guidance files | `guidance_001.json` (7 verses) and `guidance_002.json` (263 verses) |
| Empty, intentional fallback | `guidance_112.json` |
| Next verse | **2:264**, compiled |
| Remaining in Sūrah 2 | **23 verses** (2:264–2:286) |
| Working branch | `arena/dce9f1ba-quran-explained` |

## Latest batch: 2:254–2:263

This ten-verse mixed batch includes authored-only verses **2:254** and **2:257**,
which were composed from their complete source blocks, and compiled verses
**2:255–256** and **2:258–263**, which were built from curated source selections.
The emitted entries are 1,475, 1,831, 2,468, 1,402, 1,817, 1,773, 1,928, 1,947,
1,830, and 1,337 words respectively. Each records 6–8 source sets. The
service-worker cache version is `quran-reader-v1.5.3-2-263`.

## Next work

Continue sequentially with **2:264**. Verses 2:264–2:286 are all eligible for
the compiled workflow; re-dump their source packets, curate heading-relevant
references, dry-compile, and gate each completed batch before it is merged.

## Verification for the latest batch

- `python3 tools/verify_verse.py 2 --all`: **263/263** verses pass.
- `node tools/tests/style-check.js`: **9/9** checks pass.
- Render gate: **23/23** checks pass.
- Set integrity: **12/12** checks pass.
- Source rendering: **30/30** checks pass.
- Chapter-1 guidance rendering: **52/52** checks pass.

The format, source policy, batching guidance, and required test commands live in
[`../AGENTS.md`](../AGENTS.md), [`voice.md`](voice.md), and [`workflow.md`](workflow.md).
