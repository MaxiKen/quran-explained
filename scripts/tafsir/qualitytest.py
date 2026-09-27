#!/usr/bin/env python3
"""Regression tests for the v8 Chapter-1 parity gate.

The fixtures are synthetic so repairing Chapter 2 cannot make the tests fail. They
represent the defects that motivated v8: a triple-pasted clause, unreviewed citation
relevance, long and difficult prose, token authority use, fixed shape, and a fixed
final application slot.
"""

from __future__ import annotations

import sys
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

    baseline, baseline_findings = Q.load_baseline()
    if not baseline or baseline_findings:
        failures.append("frozen chapter-1 baseline must validate")
    try:
        Q.validate_baseline_approval(None)
        failures.append("an existing frozen baseline could be rewritten without approval")
    except SystemExit:
        pass

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
        row = {
            "status": "accepted",
            "scores": {dimension: 4 for dimension in Q.RUBRIC},
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
