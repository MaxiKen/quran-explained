# Progress

**Data-derived status, updated 2026-10-11.** `python3 tools/progress.py --next`
is authoritative; this page is a convenience snapshot for the next session.

| | |
|---|---|
| Written | **280 of 6,236 verses** (4.49%) |
| Planned guidance represented | **399,690 of 5,902,150 words** (6.77%) |
| Complete guidance files | `guidance_001.json` (7 verses) and `guidance_002.json` (273 verses) |
| Empty, intentional fallback | `guidance_112.json` |
| Next verse | **2:274**, compiled |
| Remaining in Sūrah 2 | **13 verses** (2:274–2:286) |
| Working branch | `arena/dce9f1ba-quran-explained` |

## Latest batch: 2:264–2:273

This compiled ten-verse batch uses curated, heading-relevant source selections.
The emitted entries are 1,688, 1,789, 1,996, 2,723, 1,250, 1,211, 1,102,
1,472, 1,793, and 1,507 words respectively. Each records 6–7 source sets. The
service-worker cache version is `quran-reader-v1.5.3-2-273`.

## Next work

Continue sequentially with **2:274**. Verses 2:274–2:286 are eligible for the
compiled workflow; re-dump their source packets, curate heading-relevant
references, dry-compile, and gate each completed batch before it is merged.

## Verification for the latest batch

- `python3 tools/verify_verse.py 2 --all`: **273/273** verses pass.
- `node tools/tests/style-check.js`: **9/9** checks pass.
- Render gate: **23/23** checks pass.
- Set integrity: **12/12** checks pass.
- Source rendering: **30/30** checks pass.
- Chapter-1 guidance rendering: **52/52** checks pass.

The format, source policy, batching guidance, and required test commands live in
[`../AGENTS.md`](../AGENTS.md), [`voice.md`](voice.md), and [`workflow.md`](workflow.md).
