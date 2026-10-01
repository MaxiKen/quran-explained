# Tafsir quality acceptance

Chapter 1 is the frozen **writing-style** yardstick. Its hash, metrics and style thresholds are in
`chapter-001-baseline.json`. Since the owner's instruction of 2026-10-01 it sets how the prose
*reads* — mean sentence length, the share of sentences over forty words, readability, and the limits
on a repeated production mould — and it does **not** set how much content or evidence a verse
carries: evidence density is measured and posted in the statistics but is never an alarm (the frozen
record still lists its old `evidence_density_min`; it is not enforced). The baseline is not
regenerated during ordinary writing; a changed Chapter 1 blocks the gate until a separately approved
baseline update is made explicitly. Changing an existing baseline requires `--freeze-baseline
--approval FILE`; the approval JSON must name different writer and reviewer identities, mark the
review independent, contain `approved: true`, match `old_sha256` and `new_sha256`, and explain the
reason in at least eight words.

> **State since 2026-10-01.** Chapter 2's commentary was cleared: the 2:1–2:56 prose, its review
> manifests under `reviews/002/` (they embedded excerpts of that prose and were fingerprinted to it)
> and the owner's draft receipt `draft-approvals/002/001-050.json` (bound to prose that no longer
> exists) — all of it remains in git history. Chapter 1 was restored to its approved text at the
> owner's choice, so the baseline, its approval and the Chapter-1 reviews under `reviews/001/` are
> intact and `quality.py --baseline` passes.

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
  --push-check` passes. When the review pass cannot be finished at a stop, this state is committed
  and pushed so nothing is left local, but it is
  not semantic acceptance.
- **Owner-approved for continued drafting (optional):** the owner explicitly approved a pushed
  candidate, recorded separately under `draft-approvals/`. This permits another draft run, not
  publication; it is no longer needed to continue.
- **Accepted:** the independent review pass (a separate reviewer identity) has completed the source
  synthesis, claim/evidence ledgers and rubric, and `batch.py` without either draft flag reports
  `QUALITY PARITY PASS`.

A clean candidate is committed and pushed at every stop, and the run goes on without waiting for
confirmation. Only accepted prose may advance the independent frontier or enter an app payload.

## Owner approval is not a fabricated semantic review

Under the standing order of 2026-10-01 the writer does not wait for owner approval. If the owner
does approve a pushed draft anyway, that may authorize the next run without having supplied all
detailed review records. Record that permission separately:

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
python3 scripts/tafsir/quality.py --template 2 --from 101 --to 150 --writer arena-writing-agent
# the independent review pass (below) fills quality/reviews/002/101-150.json
python3 scripts/tafsir/batch.py 2 --from 101 --to 150
python3 scripts/tafsir/stats.py 2 --from 101 --to 150 --write
# commit and push to the session branch, then carry on with the next run
```

This creates `reviews/002/101-150.json`. The writing pass does not fill the reviewer decision. There
is one AI, so the review is a separate pass under a separate identity — `reviewer:
arena-review-agent`, the writer being `arena-writing-agent` — made cold, from the finished prose and
the fingerprinted source passages only, never from the drafting notes. Its `notes` say so: that the
pass was made by the same AI model under the owner's standing order of 2026-10-01. If the pass cannot
be finished at a stop, run `batch.py ... --push-check`, commit and push the pending candidate, and
finish the pass before any further new draft is opened. The reviewer must:

1. identify itself in `reviewer` (an identity different from the writer's) and set `independent` to
   `true`;
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

Metrics are drift alarms, not quotas. A genuinely technically difficult checkpoint (for example a
legal passage that forces long defined terms) may use the top-level `exceptions` object:

```json
{
  "exceptions": {
    "QTY-PROSE-DRIFT": "A specific explanation of why this passage's subject forces long, technical sentences."
  }
}
```

The same code and a rationale of at least eight words must appear in every review covering the
alarmed verses. Exceptions cannot waive missing review, source-fingerprint or synthesis failure,
Qur'an/transmitted-evidence or substantive-claim relevance, reviewer independence, a rubric score
below 4, or a hard editorial defect.

`QUALITY DRIFT` means new drafting stops, the drift is repaired, the incident is noted in the
statistics and the clean state is pushed; then the run goes on. The report names the last
independently accepted frontier. A range may continue only
until fifty new drafts follow accepted or owner-approved prose. Draft approval never authorizes
unreviewed publication or a baseline change.

## Statistics posted with every push

`scripts/tafsir/stats.py N --from A --to B --write` saves `quality/stats/NNN/AAA-BBB.md` for the
checkpoint just reviewed; commit it with the range. It reports (1) **writing style against Chapter 1**
— mean sentence length, sentences over forty words, readability — with the gate's own alarms;
(2) **content and evidence, for information only** — words per verse, share of each verse's floor,
Qur'an cross-references and named authorities per 1,000 words — beside Chapter 1, the earlier verses
of the chapter and the other written chapters; and (3) **source coverage** from the review record, per
work. Nothing in (2) or (3) blocks a push; the author reads them afterwards.

## GitHub notification

`.github/workflows/tafsir-quality.yml` runs the frozen-baseline check, regression tests and
`quality.py --all --push-check` on commentary/rule changes. This accepts synchronized pending review
candidates without claiming semantic approval. Mechanical/metric drift, stale scaffolds, or more than
fifty drafts beyond the last accepted/owner-approved drafting frontier produce a failed GitHub check, a job-summary report and a downloadable
`tafsir-quality-drift-report` artifact. Accepted rows still receive the full semantic validation. The
workflow may also be started manually with **Run workflow**.
