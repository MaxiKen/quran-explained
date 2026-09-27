# Tafsir quality acceptance

Chapter 1 is the frozen quality floor. Its hash, metrics and drift thresholds are in
`chapter-001-baseline.json`. The baseline is not regenerated during ordinary writing; a changed
Chapter 1 blocks the gate until a separately approved baseline update is made explicitly. Changing
an existing baseline requires `--freeze-baseline --approval FILE`; the approval JSON must name
different writer and reviewer identities, mark the review independent, contain `approved: true`,
match `old_sha256` and `new_sha256`, and explain the reason in at least eight words.

A raised Chapter 1 must itself receive the complete all-source, claim/evidence, rubric and relevance
review in checkpoints of no more than fifty verses. The present Chapter 1 was historically reviewed
as `1:1–1:5` and `1:6–1:7`; both accepted files remain valid under the larger limit. A hash approval
without accepted semantic review is rejected. Freezing a richer chapter may tighten drift thresholds,
but `quality.py` preserves every stronger threshold from the previous floor; raising one dimension
can never quietly lower another.

```bash
python3 scripts/tafsir/quality.py --template 1 --from 1 --to 5 --writer WRITER_ID
python3 scripts/tafsir/quality.py --template 1 --from 6 --to 7 --writer WRITER_ID
python3 scripts/tafsir/quality.py --freeze-baseline \
  --approval quality/chapter-001-baseline-approval.json
```

## States are different

- **Drafted:** prose exists in `tmp/work/` or the assembled chapter.
- **Mechanically clean:** `batch.py ... --draft` finds no format/evidence failure.
- **Pushable review candidate:** a synchronized pending review scaffold exists and `batch.py ...
  --push-check` passes. This state must be committed and pushed whenever generation stops, but it is
  not semantic acceptance.
- **Owner-approved for continued drafting:** the owner explicitly approved a pushed candidate,
  recorded separately under `draft-approvals/`. This permits another draft run, not publication.
- **Accepted:** a different reviewer has completed the source synthesis, claim/evidence ledgers and
  Chapter-1 rubric, and `batch.py` without either draft flag reports `QUALITY PARITY PASS`.

A clean review candidate may and must be committed/pushed before confirmation. Only accepted prose
may advance the independent frontier or enter an app payload.

## Owner approval is not a fabricated semantic review

An owner who approves a pushed draft and asks for continued generation may authorize the next run
without having supplied all detailed review records. Record that permission separately:

```bash
python3 scripts/tafsir/quality.py --approve-draft 2 --from 1 --to 50 \
  --writer WRITER_ID --owner OWNER_ID \
  --approval-statement "THE OWNER'S ACTUAL APPROVAL AND CONTINUATION REQUEST" \
  --candidate-commit FULL_APPROVED_COMMIT_HASH
```

The owner and writer must differ. The record is bound to the approved verse text, introduction
when applicable, and complete source-map fingerprints. It covers at most fifty consecutive
verses; approvals cannot skip gaps. Recording verifies the cited Git candidate and unchanged
source files. Changed approved content requires renewed owner approval unless complete independent
acceptance has superseded the older drafting receipt.
At most fifty new drafts may follow this separate drafting frontier. Pending review scaffolds
and all mechanical/metric checks still apply, including to previously written prose.

This permission is never read by `accepted_frontier`, the full review gate, baseline approval or
the publisher. It does not manufacture scores, attest to an independent source comparison, or mark
any citation or claim reviewed. A writer may document the owner's actual words but must never
supply approval on the owner's behalf. Publication still requires every independent review below.

## One checkpoint

A checkpoint contains one to fifty consecutive verses:

```bash
python3 scripts/tafsir/quality.py --template 2 --from 101 --to 150 --writer WRITER_ID
python3 scripts/tafsir/batch.py 2 --from 101 --to 150 --push-check
# commit and push the pending candidate here for owner inspection
```

This creates `reviews/002/101-150.json`. The writer does not fill the reviewer decision. A different
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
python3 scripts/tafsir/batch.py 2 --from 101 --to 150
python3 scripts/tafsir/quality.py 2 --from 101 --to 150
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

`QUALITY DRIFT` means generation stops immediately and the current clean state is pushed for owner
inspection. The report names the last independently accepted frontier. A range may continue only
until fifty new drafts follow accepted or owner-approved prose. Draft approval never authorizes
unreviewed publication or a baseline change.

## GitHub notification

`.github/workflows/tafsir-quality.yml` runs the frozen-baseline check, regression tests and
`quality.py --all --push-check` on commentary/rule changes. This accepts synchronized pending review
candidates without claiming semantic approval. Mechanical/metric drift, stale scaffolds, or more than
fifty drafts beyond the last accepted/owner-approved drafting frontier produce a failed GitHub check, a job-summary report and a downloadable
`tafsir-quality-drift-report` artifact. Accepted rows still receive the full semantic validation. The
workflow may also be started manually with **Run workflow**.
