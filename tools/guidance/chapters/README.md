# Chapter-local progress and completion receipts

Use one `SSS.md` file per requested chapter, for example `018.md`.
Do not edit this shared README during routine chapter generation.
The receipt isolates progress from other sessions and is also the merge manifest.
See ../CHAPTER_RUN.md for the authoritative workflow.

Copy this structure when starting a chapter, and fill it from actual results:

```markdown
# Chapter N: NAME

## Session scope
- Branch: assigned session branch
- Starting BASE commit: full SHA saved before chapter edits
- Latest content commit: SHA (not the final report commit's own hash)
- Status: partial / complete
- Intro: pending / complete
- Verse ranges generated/resumed: ...

## Checks and single final verification
- Work/scoped diagnostics: ...
- Pipeline tests: ...
- Raw/published consistency: ...
- Renderer check: ...
- Full check: deferred until complete / actual attempt result
- Exact command and date, if run: ...
- Published payload SHA-256, if run: ...
- Ok / flag / fail counts and residual review dispositions: ...
- Interrupted or failed full-check attempts, if any: ...

## Tracked changes since BASE
| Status (A/M/D/R) | Repository-relative path | Purpose |
|---|---|---|
| A | tools/guidance/chapters/SSS.md | Progress, verification receipt and manifest |

## Ignored scratch files created or updated (not merge candidates)
| Status | Repository-relative path | Purpose |
|---|---|---|

## Selective merge allowlist
- Exact paths, not unrelated whole-branch changes
- Shared-file exceptions: none / explicitly approved paths and reasons
- Inherited unrelated PR changes: none / list and exclude from proposed integration
- Main conflicts / same-chapter concurrent edits needing review: ...
```

The final user-facing handoff must include the final commit SHA and every file
path. Neither a passing deterministic check nor an isolated path list guarantees
scholarly approval or conflict-free integration.
