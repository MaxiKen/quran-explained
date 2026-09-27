# Tafsir quality acceptance

Chapter 1 is the frozen quality floor. Its hash, metrics and drift thresholds are in
`chapter-001-baseline.json`. The baseline is not regenerated during ordinary writing; a changed
Chapter 1 blocks the gate until a separately approved baseline update is made explicitly. Changing
an existing baseline requires `--freeze-baseline --approval FILE`; the approval JSON must name an
independent reviewer, contain `approved: true`, match `old_sha256` and `new_sha256`, and explain the
reason in at least eight words.

## States are different

- **Drafted:** prose exists in `tmp/work/` or the assembled chapter.
- **Mechanically clean:** `batch.py ... --draft` finds no format/evidence failure.
- **Accepted:** a different reviewer has completed the Chapter-1 rubric and citation ledger, and
  `batch.py` without `--draft` reports `QUALITY PARITY PASS`.

Only accepted prose may advance the frontier, be committed as commentary, or enter an app payload.

## One checkpoint

A checkpoint contains one to five consecutive verses:

```bash
python3 scripts/tafsir/quality.py --template 2 --from 101 --to 105 --writer WRITER_ID
```

This creates `reviews/002/101-105.json`. The writer does not fill the reviewer decision. A different
reviewer must:

1. identify himself or herself in `reviewer` and set `independent` to `true`;
2. score all eight dimensions from 1–5 for every verse;
3. give no score below 4, or return the verse for revision;
4. state the proposition beside every Qur'an cross-reference;
5. mark its support `direct` or `contextual`; contextual support needs a substantive rationale;
6. set each verse and the checkpoint to `accepted` only after the review is complete.

Then run:

```bash
python3 scripts/tafsir/batch.py 2 --from 101 --to 105
python3 scripts/tafsir/quality.py 2 --from 101 --to 105
```

## Metric exceptions

Metrics are drift alarms, not citation quotas. A genuinely source-sparse or technically difficult
checkpoint may use the top-level `exceptions` object:

```json
{
  "exceptions": {
    "QTY-EVIDENCE-DRIFT": "A specific explanation of why the mapped sources contain no additional independent evidence."
  }
}
```

The same code and a rationale of at least eight words must appear in every review covering the
alarmed verses. Exceptions cannot waive missing review, citation relevance, reviewer independence,
a rubric score below 4, or a hard editorial defect.

`QUALITY DRIFT` means generation stops immediately. The report names the last accepted frontier;
no later verse is written or published until the blocked checkpoint passes.

## GitHub notification

`.github/workflows/tafsir-quality.yml` runs the frozen-baseline check, regression tests and
`quality.py --all` on commentary/rule changes. Drift produces a failed GitHub check, a job-summary
report and a downloadable `tafsir-quality-drift-report` artifact. The workflow may also be started
manually with **Run workflow**.
