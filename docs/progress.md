# Progress

**Data-derived status, updated 2026-10-11.** `python3 tools/progress.py --next`
is authoritative; this page is a convenience snapshot for the next session.

| | |
|---|---|
| Written | **300 of 6,236 verses** (4.81%) |
| Planned guidance represented | **428,310 of 5,902,150 words** (7.26%) |
| Complete guidance files | `guidance_001.json` (7 verses) and `guidance_002.json` (286 verses) |
| In progress | `guidance_003.json` (3:1–3:7) |
| Empty, intentional fallback | `guidance_112.json` |
| Next verse | **3:8**, compiled |
| Next authored-only verse | **3:78** |
| Working branch | `arena/dce9f1ba-quran-explained` |

## Latest batch: 2:284–2:286 and 3:1–3:7

This cross-chapter compiled batch completes al-Baqarah and begins Āl ʿImrān.
The emitted entries for 2:284–286 are 1,401, 1,411, and 1,717 words; entries
3:1–7 are 1,126, 931, 995, 1,230, 654, 927, and 2,159 words. Each records
5–8 source sets. The service-worker cache version is `quran-reader-v1.5.3-3-7`.

## Next work

Continue sequentially with **3:8**. The next ten-verse batch is 3:8–3:17;
all of these entries use the compiled workflow. Re-dump source packets, curate
heading-relevant references, dry-compile, and gate the completed batch.

## Verification for the latest batch

- `python3 tools/verify_verse.py 2 --all`: **286/286** verses pass.
- `python3 tools/verify_verse.py 3 --all`: **7/7** verses pass.
- `node tools/tests/style-check.js`: **9/9** checks pass.
- Render gate: **32/32** checks pass.
- Set integrity: **12/12** checks pass.
- Source rendering: **30/30** checks pass.
- Chapter-1 guidance rendering: **52/52** checks pass.

The format, source policy, batching guidance, and required test commands live in
[`../AGENTS.md`](../AGENTS.md), [`voice.md`](voice.md), and [`workflow.md`](workflow.md).
