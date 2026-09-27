# Tafsir quality acceptance

Chapter 1 is the frozen quality floor. Its hash, metrics and drift thresholds are in
`chapter-001-baseline.json`. The baseline is not regenerated during ordinary writing; a changed
Chapter 1 blocks the gate until a separately approved baseline update is made explicitly. Changing
an existing baseline requires `--freeze-baseline --approval FILE`; the approval JSON must name
different writer and reviewer identities, mark the review independent, contain `approved: true`,
match `old_sha256` and `new_sha256`, and explain the reason in at least eight words.

A raised Chapter 1 must itself receive the complete all-source, claim/evidence, rubric and relevance
review in checkpoints of no more than five verses. Create `1:1–1:5` and `1:6–1:7` templates with the commands
below, have the same independent reviewer complete both, then freeze the approved baseline. A hash
approval without accepted semantic review is rejected. Freezing a richer chapter may tighten drift
thresholds, but `quality.py` preserves every stronger threshold from the previous floor; raising one
dimension can never quietly lower another.

```bash
python3 scripts/tafsir/quality.py --template 1 --from 1 --to 5 --writer WRITER_ID
python3 scripts/tafsir/quality.py --template 1 --from 6 --to 7 --writer WRITER_ID
python3 scripts/tafsir/quality.py --freeze-baseline \
  --approval quality/chapter-001-baseline-approval.json
```

## States are different

- **Drafted:** prose exists in `tmp/work/` or the assembled chapter.
- **Mechanically clean:** `batch.py ... --draft` finds no format/evidence failure.
- **Accepted:** a different reviewer has completed the source synthesis, claim/evidence ledgers and
  Chapter-1 rubric, and `batch.py` without `--draft` reports `QUALITY PARITY PASS`.

Only accepted prose may advance the frontier, be committed as commentary, or enter an app payload.

## One checkpoint

A checkpoint contains one to five consecutive verses:

```bash
python3 scripts/tafsir/quality.py --template 2 --from 101 --to 105 --writer WRITER_ID
```

This creates `reviews/002/101-105.json`. The writer does not fill the reviewer decision. A different
reviewer must:

1. identify himself or herself in `reviewer` and set `independent` to `true`;
2. compare the prose with every source named in `source_synthesis.available_sources`, verify the
   source fingerprint, set coverage to `complete`, and explain the comparison in `notes`;
3. build `distinct_material_evidence`: group works that carry the same point instead of counting
   duplicates, mark each material point `included` with an excerpt found in the commentary or
   `omitted` with a substantive reason, and leave no material source point unmapped;
4. mark `claim_verification.coverage` complete after inspecting the full prose; check every detected
   language and consequential legal/theological claim against a fingerprinted allowlisted source
   passage, recording `source_reference` when its support is mapped under another verse, and add any
   material claim the conservative detector missed to `additional_material_claims`;
5. score all eight dimensions from 1–5 for every verse;
6. give no score below 4, or return the verse for revision;
7. state the proposition beside every Qur'an cross-reference and mark its support `direct` or
   `contextual`; contextual support needs a substantive rationale;
8. inspect every scaffolded transmitted statement, identify its allowlisted source passage and
   verse reference, record that passage's fingerprint, paste a matching excerpt, state its
   proposition, and decide direct/contextual relevance;
9. set each verse and the checkpoint to `accepted` only after the review is complete.

A synthesis fingerprint changes when any of the eleven mapped passages for that verse changes.
Every claim/report locator also fingerprints its exact supporting passage, including cross-verse
support. The old review then fails instead of silently certifying prose against source text it never saw. Reviewers do not
reward name counts: duplicated or irrelevant material remains one witness, and omission is judged by
substance rather than by how many works are named in the commentary.

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
alarmed verses. Exceptions cannot waive missing review, source-fingerprint or synthesis failure,
Qur'an/transmitted-evidence or substantive-claim relevance, reviewer independence, a rubric score
below 4, or a hard editorial defect.

`QUALITY DRIFT` means generation stops immediately. The report names the last accepted frontier;
no later verse is written or published until the blocked checkpoint passes.

## GitHub notification

`.github/workflows/tafsir-quality.yml` runs the frozen-baseline check, regression tests and
`quality.py --all` on commentary/rule changes. Drift produces a failed GitHub check, a job-summary
report and a downloadable `tafsir-quality-drift-report` artifact. The workflow may also be started
manually with **Run workflow**.
