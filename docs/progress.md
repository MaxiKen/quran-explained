# Progress

**Data-derived status, updated 2026-10-11.** `python3 tools/progress.py --next`
is authoritative; the table is a convenience snapshot for the next session.

| | |
|---|---|
| Written | **260 of 6,236 verses** (4.17%) |
| Planned guidance represented | **366,970 of 5,902,150 words** (6.22%) |
| Complete guidance files | `guidance_001.json` (7 verses) and `guidance_002.json` (253 verses) |
| Empty, intentional fallback | `guidance_112.json` |
| Next verse | **2:254**, authored-only |
| Next authored-only after it | **2:257** |
| Working branch | `arena/dce9f1ba-quran-explained` |

## Latest batch: 2:250–2:253

The batch is compiled from the source packets and retains only distinct,
heading-relevant source selections. It added 5,730 planned words. The finished
entries are 1,035 words for 2:250, 1,331 for 2:251, 601 for 2:252, and 1,594 for
2:253. Their `draws_on` counts are 6, 6, 6, and 7 respectively. The service-worker
cache version is `quran-reader-v1.5.3-2-253`.

## Next work

Verse 2:254 is under its source-material floor and is therefore authored-only.
Read every available source block, compose a source-bounded entry, pass
`--draws` and `--names` to the verse gate, and do not compile or lower its floor.
Keep the chapter sequence; the next authored-only verse is 2:257.

## Verification for the latest batch

- `python3 tools/verify_verse.py 2 --all`: **253/253** verses pass.
- `node tools/tests/style-check.js`: **9/9** checks pass.
- Render gate: **23/23** checks pass.
- Set integrity: **12/12** checks pass.
- Source rendering: **30/30** checks pass.
- Chapter-1 guidance rendering: **52/52** checks pass.

The format, source policy, batching guidance, and required test commands live in
[`../AGENTS.md`](../AGENTS.md), [`voice.md`](voice.md), and [`workflow.md`](workflow.md).
