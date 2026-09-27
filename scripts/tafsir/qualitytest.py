#!/usr/bin/env python3
"""Regression tests for the v8 Chapter-1 parity gate.

The fixtures are synthetic so repairing Chapter 2 cannot make the tests fail. They
represent the defects that motivated v8 and the raised baseline: a triple-pasted
clause, unreviewed Qur'an or transmitted evidence, unverified source synthesis,
long and difficult prose, token authority use, fixed shape, and a fixed final
application slot.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402
import quality as Q  # noqa: E402


class FakeSection:
    def __init__(self, verse: int, body: str, heading: str = "A DISTINCT HEADING"):
        self.chapter = 2
        self.verse = verse
        self.ref = "2:%d" % verse
        self._body = "**%s %d**\n\n%s" % (heading, verse, body)

    def body(self):
        return self._body

    def headings(self):
        return [(1, self._body.split("**", 2)[1])]


def main() -> int:
    failures = []

    if Q.REVIEW_CHECKPOINT_SIZE != 50 or Q.METRIC_CHECKPOINT_SIZE != 5:
        failures.append("review checkpoints must allow fifty verses while drift metrics stay five-verse")

    original_reviews_dir = Q.REVIEWS_DIR
    try:
        with tempfile.TemporaryDirectory(dir=C.REPO / "tmp") as temp_dir:
            Q.REVIEWS_DIR = Path(temp_dir)
            fifty = {
                "chapter": 2, "from": 1, "to": 50,
                "verses": {str(verse): {} for verse in range(1, 51)},
            }
            (Q.REVIEWS_DIR / "fifty.json").write_text(json.dumps(fifty))
            _reviews, errors = Q.load_reviews()
            if errors:
                failures.append("a fifty-verse review checkpoint was rejected")
            (Q.REVIEWS_DIR / "fifty.json").unlink()
            fifty_one = {
                "chapter": 2, "from": 1, "to": 51,
                "verses": {str(verse): {} for verse in range(1, 52)},
            }
            (Q.REVIEWS_DIR / "fifty-one.json").write_text(json.dumps(fifty_one))
            _reviews, errors = Q.load_reviews()
            if "QTY-CHECKPOINT-SIZE" not in {error.code for error in errors}:
                failures.append("a fifty-one-verse review checkpoint was not rejected")
    finally:
        Q.REVIEWS_DIR = original_reviews_dir

    pending_section = FakeSection(1, "A clean review candidate remains pending for its owner.")
    pending_review = {
        "schema_version": Q.SCHEMA_VERSION,
        "chapter": 2,
        "writer": "writer-test",
        "reviewer": "",
        "independent": False,
        "status": "pending",
    }
    pending_row = {
        "status": "pending",
        "source_synthesis": {
            "source_fingerprint": Q.source_fingerprint(2, 1),
            "available_sources": Q.available_sources(2, 1),
        },
        "claim_verification": {
            "detected_claims": [],
            "additional_material_claims": [],
        },
        "citations": [],
        "transmitted_evidence": [],
    }
    candidate_path = C.REPO / "quality/reviews/002/pending-test.json"
    if Q._review_scaffold_errors(2, pending_section, pending_review, pending_row, candidate_path):
        failures.append("a synchronized pending review candidate did not pass its push check")
    pending_section._body += " The Arabic word means a binding legal rule."
    stale = Q._review_scaffold_errors(2, pending_section, pending_review, pending_row, candidate_path)
    if "QTY-PUSH-REVIEW-STALE" not in {error.code for error in stale}:
        failures.append("a stale pending claim ledger was accepted for push")

    baseline, baseline_findings = Q.load_baseline()
    if not baseline or baseline_findings:
        failures.append("frozen chapter-1 baseline must validate")
    try:
        Q.validate_baseline_approval(None)
        failures.append("an existing frozen baseline could be rewritten without approval")
    except SystemExit:
        pass

    weaker = {"thresholds": {
        "mean_sentence_max": 30.0, "flesch_min": 50.0,
        "evidence_density_min": 4.0,
    }}
    previous = {"thresholds": {
        "mean_sentence_max": 24.0, "flesch_min": 62.0,
        "evidence_density_min": 7.0,
    }}
    preserved = Q.preserve_stronger_thresholds(weaker, previous)["thresholds"]
    if preserved != {"mean_sentence_max": 24.0, "flesch_min": 62.0,
                      "evidence_density_min": 7.0}:
        failures.append("raising the baseline weakened an existing drift threshold")

    if baseline:
        original_baseline_path, original_reviews_dir = Q.BASELINE_PATH, Q.REVIEWS_DIR
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp = Path(temp_dir)
                Q.BASELINE_PATH = temp / "baseline.json"
                Q.REVIEWS_DIR = temp / "reviews"
                Q.REVIEWS_DIR.mkdir()
                Q.BASELINE_PATH.write_text(json.dumps(baseline) + "\n")
                approval_path = temp / "approval.json"
                approval_path.write_text(json.dumps({
                    "schema_version": Q.SCHEMA_VERSION,
                    "writer": "writer-test",
                    "reviewer": "reviewer-test",
                    "independent": True,
                    "approved": True,
                    "old_sha256": baseline["sha256"],
                    "new_sha256": Q._sha256(C.output_path(1)),
                    "reason": "This candidate adds stronger evidence without lowering any established quality floor.",
                }) + "\n")
                try:
                    Q.validate_baseline_approval(str(approval_path))
                    failures.append("baseline approval without complete verse reviews was accepted")
                except SystemExit as exc:
                    if "baseline semantic review is incomplete" not in str(exc):
                        failures.append("baseline review guard failed for the wrong reason: %s" % exc)
        finally:
            Q.BASELINE_PATH, Q.REVIEWS_DIR = original_baseline_path, original_reviews_dir

    triple = FakeSection(
        1,
        "What the challenge produces is a refusal: What the challenge produces is a refusal: "
        "What the challenge produces is a refusal: the answer then follows.")
    if Q._repeated_clause(triple) != "what the challenge produces is a refusal":
        failures.append("a triple-pasted clause was not detected")
    parallel = FakeSection(
        2,
        "The wording does not say that the door was absent, and the wording does not say that "
        "the traveller failed to see it. The two denials make separate points.")
    if Q._repeated_clause(parallel) is not None:
        failures.append("deliberate two-part parallel wording was mistaken for a triple paste")

    chapter1 = C.load_chapter_doc(1)
    section = chapter1.section_map()[1] if chapter1 else None
    if section is None:
        failures.append("chapter 1 review fixture is missing")
    else:
        refs = Q.cross_references(section)
        test_chapter, test_verse = 2, 1
        sources = Q.available_sources(test_chapter, test_verse)
        source_slug = sources[0]
        source_text = C.source_verse(source_slug, test_chapter, test_verse)
        source_excerpt = " ".join(source_text.split()[:12])
        row = {
            "status": "accepted",
            "scores": {dimension: 4 for dimension in Q.RUBRIC},
            "source_synthesis": {
                "source_fingerprint": Q.source_fingerprint(test_chapter, test_verse),
                "available_sources": sources,
                "coverage": "complete",
                "notes": "Every available source passage was compared with the finished commentary.",
                "distinct_material_evidence": [{
                    "point": "The opening names carry mercy into each lawful beginning.",
                    "sources": [source_slug],
                    "decision": "included",
                    "commentary_anchor": " ".join(section.body().split()[:12]),
                    "reason": "",
                }],
            },
            "claim_verification": {
                "coverage": "complete",
                "notes": "Every language, legal, and theological claim was checked against sources.",
                "detected_claims": [
                    {
                        "categories": categories,
                        "statement": statement,
                        "proposition": "This source evidence supports the substantive claim being reviewed.",
                        "source": source_slug,
                        "source_reference": "%d:%d" % (test_chapter, test_verse),
                        "source_fingerprint": Q.source_passage_fingerprint(
                            source_slug, test_chapter, test_verse),
                        "source_excerpt": source_excerpt,
                        "support": "direct",
                        "rationale": "",
                    }
                    for categories, statement in Q.substantive_claims(section)
                ],
                "additional_material_claims": [],
            },
            "citations": [
                {
                    "reference": ref,
                    "quoted_clause": quote,
                    "proposition": "This citation directly supports the stated interpretive proposition.",
                    "support": "direct",
                    "rationale": "",
                }
                for ref, quote in refs
            ],
            "transmitted_evidence": [
                {
                    "statement": statement,
                    "proposition": "This transmitted evidence supports the adjacent interpretive claim.",
                    "source": source_slug,
                    "source_reference": "%d:%d" % (test_chapter, test_verse),
                    "source_fingerprint": Q.source_passage_fingerprint(
                        source_slug, test_chapter, test_verse),
                    "source_excerpt": source_excerpt,
                    "support": "direct",
                    "rationale": "",
                }
                for statement in Q.transmitted_evidence(section)
            ],
        }
        review = {
            "schema_version": Q.SCHEMA_VERSION,
            "chapter": 2,
            "writer": "writer-test",
            "reviewer": "reviewer-test",
            "independent": True,
            "status": "accepted",
        }
        test_path = C.REPO / "quality/reviews/002/test.json"
        errors = Q._review_errors(2, section, review, row, test_path)
        if errors:
            failures.append("a complete independent review fixture did not validate: %s" %
                            ", ".join(e.code for e in errors))
        if row["citations"]:
            row["citations"][0]["support"] = "pending"
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-CITATION-RELEVANCE" not in {e.code for e in errors}:
                failures.append("an unapproved citation relevance decision was accepted")
            row["citations"][0]["support"] = "direct"
        row["source_synthesis"]["coverage"] = "pending"
        errors = Q._review_errors(2, section, review, row, test_path)
        if "QTY-SOURCE-SYNTHESIS" not in {e.code for e in errors}:
            failures.append("an incomplete all-source comparison was accepted")
        row["source_synthesis"]["coverage"] = "complete"
        mapped_point = row["source_synthesis"]["distinct_material_evidence"][0]
        mapped_point["decision"] = "omitted"
        mapped_point["reason"] = "too brief"
        errors = Q._review_errors(2, section, review, row, test_path)
        if "QTY-SOURCE-OMISSION" not in {e.code for e in errors}:
            failures.append("a material omission without a substantive reason was accepted")
        mapped_point["decision"], mapped_point["reason"] = "included", ""
        mapped_point["sources"] = [source_slug, source_slug]
        errors = Q._review_errors(2, section, review, row, test_path)
        if "QTY-SOURCE-SYNTHESIS" not in {e.code for e in errors}:
            failures.append("duplicate works were counted as distinct material evidence")
        mapped_point["sources"] = [source_slug]
        fingerprint = row["source_synthesis"]["source_fingerprint"]
        row["source_synthesis"]["source_fingerprint"] = "stale-source-map"
        errors = Q._review_errors(2, section, review, row, test_path)
        if "QTY-SOURCE-FINGERPRINT" not in {e.code for e in errors}:
            failures.append("a stale source-map review was accepted")
        row["source_synthesis"]["source_fingerprint"] = fingerprint
        row["claim_verification"]["coverage"] = "pending"
        errors = Q._review_errors(2, section, review, row, test_path)
        if "QTY-CLAIM-REVIEW" not in {e.code for e in errors}:
            failures.append("incomplete language/legal/theological claim review was accepted")
        row["claim_verification"]["coverage"] = "complete"
        if row["claim_verification"]["detected_claims"]:
            claim = row["claim_verification"]["detected_claims"][0]
            statement = claim["statement"]
            claim["statement"] = "A stale substantive claim no longer present in the prose."
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-CLAIM-REVIEW" not in {e.code for e in errors}:
                failures.append("a changed substantive claim retained stale approval")
            claim["statement"] = statement
            claim_fingerprint = claim["source_fingerprint"]
            claim["source_fingerprint"] = "stale-supporting-passage"
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-CLAIM-SOURCE" not in {e.code for e in errors}:
                failures.append("a stale substantive-claim source fingerprint was accepted")
            claim["source_fingerprint"] = claim_fingerprint
        if row["transmitted_evidence"]:
            item = row["transmitted_evidence"][0]
            item["support"] = "pending"
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-TRANSMITTED-RELEVANCE" not in {e.code for e in errors}:
                failures.append("unreviewed transmitted evidence was accepted")
            item["support"] = "direct"
            transmitted_statement = item["statement"]
            item["statement"] = "A changed report no longer present in the commentary."
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-TRANSMITTED-REVIEW" not in {e.code for e in errors}:
                failures.append("a changed transmitted statement retained stale approval")
            item["statement"] = transmitted_statement
            transmitted_fingerprint = item["source_fingerprint"]
            item["source_fingerprint"] = "stale-supporting-passage"
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-TRANSMITTED-SOURCE" not in {e.code for e in errors}:
                failures.append("a stale transmitted-evidence source fingerprint was accepted")
            item["source_fingerprint"] = transmitted_fingerprint
            excerpt = item["source_excerpt"]
            item["source_excerpt"] = "words absent from every mapped source passage"
            errors = Q._review_errors(2, section, review, row, test_path)
            if "QTY-TRANSMITTED-SOURCE" not in {e.code for e in errors}:
                failures.append("transmitted evidence without a source match was accepted")
            item["source_excerpt"] = excerpt

    difficult = (
        "Ibn ʿAbbās transmitted this reading. Today, the contemporary institutional arrangement "
        "repeatedly demonstrates an extraordinarily complicated accumulation of responsibilities, "
        "interpretations, qualifications, and administrative consequences that remain difficult "
        "for an ordinary person to disentangle without substantial preparation, sustained attention, "
        "specialised assistance, and considerable patience throughout the entire demanding process."
    )
    synthetic = [FakeSection(v, difficult, "THE SAME PRODUCTION SHAPE") for v in range(1, 11)]
    metric_codes = {f.code for f in Q._metric_findings(2, synthetic, baseline)} if baseline else set()
    for required in ("QTY-PROSE-DRIFT", "QTY-READABILITY-DRIFT",
                     "QTY-SOURCE-CONCENTRATION", "QTY-SHAPE-DRIFT",
                     "QTY-APPLICATION-TEMPLATE"):
        if required not in metric_codes:
            failures.append("synthetic degeneration did not exercise %s" % required)

    if failures:
        for failure in failures:
            print("FAILED: %s" % failure)
        print("quality gate tests: %d FAILED" % len(failures))
        return 1
    print("quality gate tests: all expectations hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
