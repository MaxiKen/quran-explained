#!/usr/bin/env python3
"""Chapter-1 parity gate for new tafsir writing (quality standard v8).

The ordinary auditor proves format and minimum evidence.  This gate answers the
separate question the old gate could not answer: does a newly written range still
read like chapter 1?

Chapter 1 is a WRITING-STYLE yardstick only (the owner's instruction, 2026-10-01):
sentence length, the share of very long sentences and readability are measured
against it.  How much content or evidence a verse carries is never compared with
chapter 1; that follows what the verse's own sources hold (the auditor's per-verse
floors and anchors, and the reviewer's material-point ledger).  Evidence density is
still measured and reported, as information, never as an alarm.

Fifty verses may be source-mapped and written in one review checkpoint. Automatic
prose alarms still run every fifty verses so degeneration is caught
early. Every non-baseline verse needs an independent semantic review in
``quality/reviews/`` before acceptance or publication. A review scores the prose
style against chapter 1, fingerprints and compares every available source passage, groups
duplicate witnesses into distinct material points, accounts for omissions, and
verifies Qur'an citations, named transmitted evidence, language claims, and
consequential legal/theological claims for source support and relevance—not merely
verbal presence.

A synchronized pending review template is enough for a review-candidate push. The
independent review pass normally advances the frontier; an explicit, fingerprinted
owner approval, if the owner gives one, may also advance the draft-continuation
frontier without fabricating semantic reviews. At most fifty new drafts may follow that
frontier. The push check and owner draft approval never grant independent acceptance;
the full source/claim/citation/rubric gate remains mandatory before publication.

Examples:

    python3 scripts/tafsir/quality.py --baseline
    python3 scripts/tafsir/quality.py 2 --from 101 --to 150
    python3 scripts/tafsir/quality.py --template 2 --from 101 --to 150 --writer writer-id
    python3 scripts/tafsir/quality.py --all --push-check
    python3 scripts/tafsir/quality.py --all

A non-zero full-gate exit means ``QUALITY DRIFT``. Acceptance and publication must
stop at that point; the output reports the last independently accepted verse. A
push-check failure blocks the checkpoint push until its draft/template is repaired.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import subprocess
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402

BASELINE_CHAPTER = 1
REVIEW_CHECKPOINT_SIZE = 50
METRIC_CHECKPOINT_SIZE = 50
MIN_SCORE = 4
BASELINE_PATH = C.REPO / "quality" / "chapter-001-baseline.json"
REVIEWS_DIR = C.REPO / "quality" / "reviews"
DRAFT_APPROVALS_DIR = C.REPO / "quality" / "draft-approvals"
DRAFT_APPROVAL_SCHEMA = 1
SCHEMA_VERSION = 2

RUBRIC = (
    "textual_attention",
    "source_synthesis",
    "citation_support",
    "reasoning",
    "theological_precision",
    "coherence",
    "prose",
    "editorial_finish",
)

# The baseline is an alarm floor, not a quota.  An independent reviewer may
# approve a technically difficult checkpoint by documenting a metric exception.
# Hard defects and missing semantic review cannot be waived.
#
# Chapter 1 is a WRITING-STYLE yardstick only (owner, 2026-10-01).  The alarms
# below measure how the prose reads: sentence length, the share of very long
# sentences, readability, and the production-mould checks (one authority
# supplying nearly every mention, one fixed section shape, one fixed application
# slot).  How much content or evidence a verse carries is NOT compared with
# chapter 1.  ``metrics()`` still reports the evidence density; it is
# information, not an alarm.
MEAN_SENTENCE_MARGIN = 2.0
FLESCH_MARGIN = 5.0
LONG_SENTENCE_MARGIN = 0.02
AUTHORITY_CONCENTRATION_LIMIT = 0.70
SHAPE_CONCENTRATION_LIMIT = 0.60
FINAL_APPLICATION_LIMIT = 0.80

REF_RE = re.compile(r"\((\d+:\d+)\s+—\s+\*\*“(.*?)”\*\*\)", re.S)
HEADING_LINE = re.compile(r"^\*\*[^*\n]+\*\*$")
QUOTED_MATTER = re.compile(
    r"\*\*\*“.*?”\*\*\*|\*\*“.*?”\*\*|\*\".*?\"\*|\*“.*?”\*",
    re.S,
)


@dataclass(frozen=True)
class Finding:
    code: str
    ref: str
    message: str
    verses: Tuple[int, ...] = ()
    hard: bool = True


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _written(section) -> bool:
    return "TODO" not in section.body()


def prose_text(section) -> str:
    """The commentary's prose, with headings and quoted evidence removed."""
    lines = [line for line in section.body().splitlines() if not HEADING_LINE.match(line.strip())]
    text = "\n".join(lines)
    text = QUOTED_MATTER.sub("", text)
    text = re.sub(r"[*_]+", "", text)
    text = re.sub(r"\([^()]*?\d+:\d+[^()]*?\)", "", text, flags=re.S)
    return re.sub(r"\s+", " ", text).strip()


def cross_references(section) -> List[Tuple[str, str]]:
    return [(m.group(1), re.sub(r"\s+", " ", m.group(2)).strip())
            for m in REF_RE.finditer(section.body())]


def source_fingerprint(chapter: int, verse: int) -> str:
    """Fingerprint every allowlisted source passage available for one verse.

    Review manifests become stale when the corpus changes, so accepted synthesis
    cannot silently survive the arrival or correction of source material.
    """
    digest = hashlib.sha256()
    for slug in C.SOURCE_ALLOWLIST:
        digest.update(slug.encode("utf-8"))
        digest.update(b"\0")
        digest.update(C.source_verse(slug, chapter, verse).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def available_sources(chapter: int, verse: int) -> List[str]:
    return [slug for slug in C.SOURCE_ALLOWLIST if C.source_verse(slug, chapter, verse).strip()]


def _standalone_search(pattern, text: str) -> bool:
    """Reject collection-name substrings such as ``Muslim`` in ``Muslims``."""
    for match in pattern.finditer(text):
        before = text[match.start() - 1] if match.start() else ""
        after = text[match.end()] if match.end() < len(text) else ""
        prefix = text[:match.start()]
        # ``Muslim`` is both a collection name and an ordinary noun. An article
        # marks the latter; continue searching in case the sentence later names
        # another collection (for example, Musnad Ahmad).
        if match.group(0).casefold() == "muslim" and re.search(r"\ba\s+$", prefix, re.I):
            continue
        if not before.isalnum() and not after.isalnum():
            return True
    return False


def transmitted_evidence(section) -> List[str]:
    """Statements that invoke a report, collection, Companion or Successor.

    These are scaffolded into the review ledger just like Qur'an references. The
    reviewer must locate each one in an allowlisted source and judge whether that
    transmitted evidence really supports the adjacent proposition.
    """
    text = A._prose_only(section.body())
    text = re.sub(r"[*_]+", "", text)
    statements = []
    for sentence in C.sentence_split(text):
        statement = re.sub(r"\s+", " ", sentence).strip()
        if statement and (A.FIRST_GEN.search(statement)
                          or _standalone_search(A.COLLECTIONS, statement)):
            statements.append(statement)
    return statements


SUBSTANTIVE_CLAIM_PATTERNS = {
    "language": re.compile(
        r"\b(?:Arabic|root|grammar|grammatical|singular|plural|construction|linguist|"
        r"teachers? of the language|scholars? of the language|"
        r"word (?:means|carries|names|describes)|term (?:means|carries|for)|"
        r"form can (?:mean|carry)|rendered .{0,30}(?:means|names))\b", re.I),
    "legal": re.compile(
        r"\b(?:law|legal|ruling|obligatory|required|requirement|permitted|forbidden|"
        r"schools? of law|counts? as|invalid|valid|cannot make .{0,20} lawful)\b", re.I),
    "theological": re.compile(
        r"\b(?:creed|theolog|divine (?:name|names|attribute|attributes|sovereignty|will|"
        r"decree|knowledge)|resurrection|foreknowledge|God alone|belongs? to God alone|"
        r"worship(?:ped|s)? (?:God )?alone|attribute of God|"
        r"God(?:’s|'s) (?:sovereignty|foreknowledge|decree))\b", re.I),
}


def substantive_claims(section) -> List[Tuple[List[str], str]]:
    """Conservative inventory of language and consequential legal/theological claims.

    Regex detection supplies a minimum ledger; the reviewer separately attests that
    the complete prose was checked and may add important claims the detector missed.
    """
    text = re.sub(r"[*_]+", "", A._prose_only(section.body()))
    claims = []
    for sentence in C.sentence_split(text):
        statement = re.sub(r"\s+", " ", sentence).strip()
        categories = [name for name, pattern in SUBSTANTIVE_CLAIM_PATTERNS.items()
                      if pattern.search(statement)]
        if statement and categories:
            claims.append((categories, statement))
    return claims


def _source_norm(text: str) -> str:
    """Search-normalise Latin or Arabic without discarding either script."""
    text = unicodedata.normalize("NFKD", text).casefold()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = "".join(ch if unicodedata.category(ch)[0] in ("L", "N") else " " for ch in text)
    return re.sub(r"\s+", " ", text).strip()


def source_passage_fingerprint(slug: str, chapter: int, verse: int) -> str:
    if slug not in C.SOURCE_ALLOWLIST:
        return ""
    payload = "%s\0%d:%d\0%s" % (slug, chapter, verse,
                                  C.source_verse(slug, chapter, verse))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_locator(item: dict, default_chapter: int, default_verse: int) -> Tuple[int, int]:
    value = str(item.get("source_reference", "%d:%d" %
                         (default_chapter, default_verse))).strip()
    match = re.fullmatch(r"(\d+):(\d+)", value)
    if not match:
        return 0, 0
    chapter, verse = map(int, match.groups())
    metadata = C.meta().get(chapter, {})
    if not metadata or not 1 <= verse <= metadata.get("verses", 0):
        return 0, 0
    return chapter, verse


def _source_excerpt_matches(slug: str, chapter: int, verse: int, excerpt: str) -> bool:
    if slug not in C.SOURCE_ALLOWLIST or not chapter or not verse or not excerpt.strip():
        return False
    needle = _source_norm(excerpt)
    haystack = _source_norm(C.source_verse(slug, chapter, verse))
    return len(needle) >= 12 and needle in haystack


def _claim_item_errors(chapter: int, verse: int, ref: str, item: object, number: int,
                       expected: Optional[Tuple[List[str], str]] = None,
                       additional: bool = False) -> List[Finding]:
    label = "additional claim" if additional else "substantive claim"
    if not isinstance(item, dict):
        return [Finding("QTY-CLAIM-REVIEW", ref,
                        "%s %d has no review object" % (label, number))]
    errors = []
    statement = re.sub(r"\s+", " ", str(item.get("statement", ""))).strip()
    categories = item.get("categories")
    if expected:
        expected_categories, expected_statement = expected
        if statement != expected_statement or categories != expected_categories:
            errors.append(Finding(
                "QTY-CLAIM-REVIEW", ref,
                "%s %d no longer matches the commentary" % (label, number)))
    elif (len(statement.split()) < 4 or not isinstance(categories, list)
          or not categories or any(category not in SUBSTANTIVE_CLAIM_PATTERNS
                                    for category in categories)):
        errors.append(Finding(
            "QTY-CLAIM-REVIEW", ref,
            "%s %d needs a statement and valid language/legal/theological category" %
            (label, number)))
    if len(str(item.get("proposition", "")).strip().split()) < 4:
        errors.append(Finding(
            "QTY-CLAIM-REVIEW", ref,
            "%s %d does not state the proposition being verified" % (label, number)))
    source_slug = str(item.get("source", "")).strip()
    source_excerpt = str(item.get("source_excerpt", "")).strip()
    source_chapter, source_verse = _source_locator(item, chapter, verse)
    expected_fingerprint = source_passage_fingerprint(
        source_slug, source_chapter, source_verse)
    if (not _source_excerpt_matches(
            source_slug, source_chapter, source_verse, source_excerpt)
            or not expected_fingerprint
            or item.get("source_fingerprint") != expected_fingerprint):
        errors.append(Finding(
            "QTY-CLAIM-SOURCE", ref,
            "%s %d lacks a matching fingerprinted excerpt from an allowlisted source" %
            (label, number)))
    support = item.get("support")
    rationale = str(item.get("rationale", "")).strip()
    if support not in ("direct", "contextual"):
        errors.append(Finding(
            "QTY-CLAIM-RELEVANCE", ref,
            "%s %d is not approved as direct or contextual support" % (label, number)))
    if support == "contextual" and len(rationale.split()) < 6:
        errors.append(Finding(
            "QTY-CLAIM-RELEVANCE", ref,
            "%s %d needs a substantive contextual rationale" % (label, number)))
    return errors


def _authority_mentions(text: str) -> List[str]:
    found = []
    for pattern in (A.FIRST_GEN, A.COLLECTIONS):
        for match in pattern.finditer(text):
            key = C.norm_key(match.group(0))
            if key:
                found.append(key)
    return found


def section_shape(section) -> Tuple[int, int]:
    paras = C.split_paragraphs(A._prose_only(section.body()))
    return len(section.headings()), len(paras)


def _final_application(section) -> bool:
    paras = C.split_paragraphs(A._prose_only(section.body()))
    return bool(paras and A.APPLICATION.search(paras[-1]))


def metrics(sections: Sequence) -> dict:
    prose = "\n".join(prose_text(s) for s in sections)
    style = C.style_metrics(prose)
    refs = sum(len(cross_references(s)) for s in sections)
    authorities = []
    for section in sections:
        authorities.extend(_authority_mentions(section.body()))
    per_1000 = max(1, style["words"]) / 1000.0
    return {
        "verses": len(sections),
        "words": style["words"],
        "sentences": style["sentences"],
        "mean_sentence": style["mean_sentence"],
        "long_sentence_share": style["long_sentence_share"],
        "flesch": style["flesch"],
        "quran_references": refs,
        "authority_mentions": len(authorities),
        "quran_references_per_1000": refs / per_1000,
        "authority_mentions_per_1000": len(authorities) / per_1000,
        "evidence_mentions_per_1000": (refs + len(authorities)) / per_1000,
    }


def baseline_payload() -> dict:
    doc = C.load_chapter_doc(BASELINE_CHAPTER)
    if doc is None or any(not _written(s) for s in doc.sections):
        raise SystemExit("chapter 1 must be complete before its quality baseline can be measured")
    result = {
        "schema_version": SCHEMA_VERSION,
        "chapter": BASELINE_CHAPTER,
        "file": "tafsir/001.md",
        "sha256": _sha256(C.output_path(BASELINE_CHAPTER)),
        "metrics": metrics(doc.sections),
        "checkpoint_size": METRIC_CHECKPOINT_SIZE,
        "rubric": list(RUBRIC),
        "minimum_score": MIN_SCORE,
        "thresholds": {
            "mean_sentence_max": metrics(doc.sections)["mean_sentence"] + MEAN_SENTENCE_MARGIN,
            "long_sentence_share_max": max(
                0.10, metrics(doc.sections)["long_sentence_share"] + LONG_SENTENCE_MARGIN),
            "flesch_min": metrics(doc.sections)["flesch"] - FLESCH_MARGIN,
            "authority_concentration_max": AUTHORITY_CONCENTRATION_LIMIT,
            "shape_concentration_max": SHAPE_CONCENTRATION_LIMIT,
            "final_application_share_max": FINAL_APPLICATION_LIMIT,
        },
    }
    return result


def preserve_stronger_thresholds(candidate: dict, previous: Optional[dict]) -> dict:
    """A raised floor may tighten an alarm but can never weaken an old one."""
    if not isinstance(previous, dict):
        return candidate
    old = previous.get("thresholds")
    new = candidate.get("thresholds")
    if not isinstance(old, dict) or not isinstance(new, dict):
        return candidate
    for key in ("mean_sentence_max", "long_sentence_share_max",
                "authority_concentration_max", "shape_concentration_max",
                "final_application_share_max"):
        if isinstance(old.get(key), (int, float)) and isinstance(new.get(key), (int, float)):
            new[key] = min(old[key], new[key])
    for key in ("flesch_min",):
        if isinstance(old.get(key), (int, float)) and isinstance(new.get(key), (int, float)):
            new[key] = max(old[key], new[key])
    return candidate


def validate_baseline_approval(path: Optional[str]) -> None:
    """Require a tracked independent decision before changing a frozen floor."""
    if not BASELINE_PATH.exists():
        return  # first installation only
    if not path:
        raise SystemExit("refusing to change the frozen Chapter-1 floor without --approval FILE")
    approval_path = Path(path)
    try:
        approval = json.loads(approval_path.read_text(encoding="utf-8"))
        current = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit("cannot read baseline approval: %s" % exc)
    actual = _sha256(C.output_path(BASELINE_CHAPTER))
    reason = str(approval.get("reason", "")).strip()
    writer = str(approval.get("writer", "")).strip()
    reviewer = str(approval.get("reviewer", "")).strip()
    if (approval.get("schema_version") != SCHEMA_VERSION
            or approval.get("approved") is not True
            or approval.get("independent") is not True
            or not writer or not reviewer or writer == reviewer
            or approval.get("old_sha256") != current.get("sha256")
            or approval.get("new_sha256") != actual
            or len(reason.split()) < 8):
        raise SystemExit(
            "baseline approval must name different writer and reviewer identities, mark the "
            "review independent, approve the change, match the old and new hashes, and give a "
            "substantive reason")

    # Raising the yardstick requires the same semantic and citation-relevance
    # review that the yardstick will demand from later chapters.  A signed hash
    # alone cannot certify that every new claim and cross-reference was read.
    reviews, load_findings = load_reviews()
    doc = C.load_chapter_doc(BASELINE_CHAPTER)
    review_findings = list(load_findings)
    if doc is None:
        review_findings.append(Finding(
            "QTY-NO-CHAPTER", "1", "chapter 1 does not exist for baseline review"))
    else:
        for section in doc.sections:
            item = reviews.get((BASELINE_CHAPTER, section.verse))
            if not item:
                review_findings.append(Finding(
                    "QTY-REVIEW-MISSING", section.ref,
                    "the revised baseline needs independent rubric and citation review"))
                continue
            review, row, path = item
            if (str(review.get("writer", "")).strip() != writer
                    or str(review.get("reviewer", "")).strip() != reviewer):
                review_findings.append(Finding(
                    "QTY-INDEPENDENCE", section.ref,
                    "baseline approval identities must match every Chapter-1 review manifest"))
            review_findings.extend(_review_errors(BASELINE_CHAPTER, section, review, row, path))
    if review_findings:
        first = review_findings[0]
        raise SystemExit(
            "baseline semantic review is incomplete: %s %s" % (first.code, first.message))


def load_baseline() -> Tuple[Optional[dict], List[Finding]]:
    if not BASELINE_PATH.exists():
        return None, [Finding("QTY-BASELINE-MISSING", "1",
                              "the frozen chapter-1 quality baseline is missing")]
    try:
        data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [Finding("QTY-BASELINE-INVALID", "1", "cannot read baseline: %s" % exc)]
    path = C.output_path(BASELINE_CHAPTER)
    expected = data.get("sha256")
    actual = _sha256(path) if path.exists() else None
    findings = []
    if not expected or actual != expected:
        findings.append(Finding(
            "QTY-BASELINE-CHANGED", "1",
            "tafsir/001.md no longer matches the frozen quality baseline; an explicit reviewed "
            "baseline update is required, never an automatic lowering of the floor"))
    return data, findings


def _review_files() -> List[Path]:
    return sorted(REVIEWS_DIR.glob("**/*.json")) if REVIEWS_DIR.exists() else []


def load_reviews() -> Tuple[Dict[Tuple[int, int], Tuple[dict, dict, Path]], List[Finding]]:
    index: Dict[Tuple[int, int], Tuple[dict, dict, Path]] = {}
    findings: List[Finding] = []
    for path in _review_files():
        try:
            review = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            findings.append(Finding("QTY-REVIEW-INVALID", str(path.relative_to(C.REPO)),
                                    "cannot parse review: %s" % exc))
            continue
        try:
            chapter = int(review["chapter"])
            verse_rows = review["verses"]
        except Exception:
            findings.append(Finding("QTY-REVIEW-INVALID", str(path.relative_to(C.REPO)),
                                    "review needs integer chapter and a verses object"))
            continue
        if not isinstance(verse_rows, dict):
            findings.append(Finding("QTY-REVIEW-INVALID", str(path.relative_to(C.REPO)),
                                    "review verses must be an object"))
            continue
        try:
            start, end = int(review["from"]), int(review["to"])
            keys = {int(v) for v in verse_rows}
        except Exception:
            findings.append(Finding("QTY-REVIEW-INVALID", str(path.relative_to(C.REPO)),
                                    "review needs numeric from/to bounds and verse keys"))
            continue
        expected = set(range(start, end + 1))
        if end < start or end - start + 1 > REVIEW_CHECKPOINT_SIZE or keys != expected:
            findings.append(Finding(
                "QTY-CHECKPOINT-SIZE", str(path.relative_to(C.REPO)),
                "one review must contain exactly its consecutive from/to range and no more than "
                "%d verses" % REVIEW_CHECKPOINT_SIZE))
            continue
        for raw_verse, row in verse_rows.items():
            try:
                verse = int(raw_verse)
            except Exception:
                findings.append(Finding("QTY-REVIEW-INVALID", str(path.relative_to(C.REPO)),
                                        "review contains a non-numeric verse key"))
                continue
            key = chapter, verse
            if key in index:
                findings.append(Finding("QTY-REVIEW-DUPLICATE", "%d:%d" % key,
                                        "more than one semantic review claims this verse"))
            else:
                index[key] = review, row, path
    return index, findings


def _review_errors(chapter: int, section, review: dict, row: dict, path: Path) -> List[Finding]:
    verse = section.verse
    ref = "%d:%d" % (chapter, verse)
    errors = []
    location = str(path.relative_to(C.REPO))
    writer = str(review.get("writer", "")).strip()
    reviewer = str(review.get("reviewer", "")).strip()
    if review.get("schema_version") != SCHEMA_VERSION:
        errors.append(Finding("QTY-REVIEW-SCHEMA", ref,
                              "%s does not use review schema %d" % (location, SCHEMA_VERSION)))
    if review.get("status") != "accepted" or row.get("status") != "accepted":
        errors.append(Finding("QTY-NOT-ACCEPTED", ref,
                              "the independent semantic review has not accepted this verse"))
    if not writer or not reviewer or writer == reviewer or review.get("independent") is not True:
        errors.append(Finding(
            "QTY-INDEPENDENCE", ref,
            "writer and reviewer must be named, different, and marked independent in %s" % location))

    scores = row.get("scores") if isinstance(row, dict) else None
    if not isinstance(scores, dict):
        errors.append(Finding("QTY-RUBRIC-MISSING", ref, "the Chapter-1 parity rubric is missing"))
    else:
        for dimension in RUBRIC:
            score = scores.get(dimension)
            if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
                errors.append(Finding("QTY-RUBRIC-MISSING", ref,
                                      "%s needs an integer score from 1 to 5" % dimension))
            elif score < MIN_SCORE:
                errors.append(Finding("QTY-BELOW-CHAPTER-1", ref,
                                      "%s scored %d; 4 is the minimum (prose and finish match Chapter 1's style; "
                                      "the rest must be sound for what the sources carry)" %
                                      (dimension, score)))

    synthesis = row.get("source_synthesis") if isinstance(row, dict) else None
    expected_sources = available_sources(chapter, verse)
    expected_fingerprint = source_fingerprint(chapter, verse)
    if not isinstance(synthesis, dict):
        errors.append(Finding(
            "QTY-SOURCE-SYNTHESIS", ref,
            "the reviewer must compare the prose with every available allowlisted source"))
    else:
        reviewed_sources = synthesis.get("available_sources")
        if reviewed_sources != expected_sources:
            errors.append(Finding(
                "QTY-SOURCE-FINGERPRINT", ref,
                "the reviewed source list does not match the available corpus passages"))
        if synthesis.get("source_fingerprint") != expected_fingerprint:
            errors.append(Finding(
                "QTY-SOURCE-FINGERPRINT", ref,
                "the source corpus changed after this synthesis review was prepared"))
        if synthesis.get("coverage") != "complete":
            errors.append(Finding(
                "QTY-SOURCE-SYNTHESIS", ref,
                "source coverage is not marked complete after comparison with the draft"))
        notes = str(synthesis.get("notes", "")).strip()
        if len(notes.split()) < 8:
            errors.append(Finding(
                "QTY-SOURCE-SYNTHESIS", ref,
                "the reviewer must explain how the source map was compared with the prose"))
        evidence_map = synthesis.get("distinct_material_evidence")
        if (not isinstance(evidence_map, list)
                or (expected_sources and not evidence_map)):
            errors.append(Finding(
                "QTY-SOURCE-SYNTHESIS", ref,
                "distinct_material_evidence must map material points rather than count works"))
        else:
            prose_norm = _source_norm(section.body())
            for number, item in enumerate(evidence_map, 1):
                if not isinstance(item, dict):
                    errors.append(Finding(
                        "QTY-SOURCE-SYNTHESIS", ref,
                        "material evidence point %d has no review object" % number))
                    continue
                point = str(item.get("point", "")).strip()
                sources = item.get("sources")
                decision = item.get("decision")
                anchor = _source_norm(str(item.get("commentary_anchor", "")))
                reason = str(item.get("reason", "")).strip()
                if (len(point.split()) < 4 or not isinstance(sources, list) or not sources
                        or len(set(sources)) != len(sources)
                        or any(source not in expected_sources for source in sources)):
                    errors.append(Finding(
                        "QTY-SOURCE-SYNTHESIS", ref,
                        "material evidence point %d needs a substantive point and its unique "
                        "available sources" % number))
                if decision == "included":
                    if len(anchor) < 12 or anchor not in prose_norm:
                        errors.append(Finding(
                            "QTY-SOURCE-SYNTHESIS", ref,
                            "included evidence point %d needs an excerpt found in the commentary" %
                            number))
                elif decision == "omitted":
                    if len(reason.split()) < 8:
                        errors.append(Finding(
                            "QTY-SOURCE-OMISSION", ref,
                            "omitted evidence point %d needs a substantive editorial reason" %
                            number))
                else:
                    errors.append(Finding(
                        "QTY-SOURCE-SYNTHESIS", ref,
                        "material evidence point %d must be marked included or omitted" % number))

    actual_claims = substantive_claims(section)
    claim_review = row.get("claim_verification") if isinstance(row, dict) else None
    if not isinstance(claim_review, dict):
        errors.append(Finding(
            "QTY-CLAIM-REVIEW", ref,
            "language and consequential legal/theological claims need source review"))
    else:
        if claim_review.get("coverage") != "complete":
            errors.append(Finding(
                "QTY-CLAIM-REVIEW", ref,
                "claim coverage is not marked complete after review of the full prose"))
        if len(str(claim_review.get("notes", "")).strip().split()) < 8:
            errors.append(Finding(
                "QTY-CLAIM-REVIEW", ref,
                "the reviewer must explain the language/legal/theological claim check"))
        detected = claim_review.get("detected_claims")
        if not isinstance(detected, list) or len(detected) != len(actual_claims):
            errors.append(Finding(
                "QTY-CLAIM-REVIEW", ref,
                "review records %d detected claims but the commentary contains %d" %
                (len(detected) if isinstance(detected, list) else 0, len(actual_claims))))
        else:
            for number, (expected, item) in enumerate(zip(actual_claims, detected), 1):
                errors.extend(_claim_item_errors(
                    chapter, verse, ref, item, number, expected=expected))
        additional = claim_review.get("additional_material_claims")
        if not isinstance(additional, list):
            errors.append(Finding(
                "QTY-CLAIM-REVIEW", ref,
                "additional_material_claims must be a list after full-prose review"))
        else:
            for number, item in enumerate(additional, 1):
                errors.extend(_claim_item_errors(
                    chapter, verse, ref, item, number, additional=True))

    actual_transmitted = transmitted_evidence(section)
    transmitted_ledger = row.get("transmitted_evidence") if isinstance(row, dict) else None
    if not isinstance(transmitted_ledger, list):
        errors.append(Finding(
            "QTY-TRANSMITTED-REVIEW", ref,
            "every named report and early-authority statement needs source and relevance review"))
    elif len(transmitted_ledger) != len(actual_transmitted):
        errors.append(Finding(
            "QTY-TRANSMITTED-REVIEW", ref,
            "review records %d transmitted statements but the commentary contains %d" %
            (len(transmitted_ledger), len(actual_transmitted))))
    else:
        for number, (actual_statement, item) in enumerate(
                zip(actual_transmitted, transmitted_ledger), 1):
            if not isinstance(item, dict):
                errors.append(Finding(
                    "QTY-TRANSMITTED-REVIEW", ref,
                    "transmitted statement %d has no review object" % number))
                continue
            if re.sub(r"\s+", " ", str(item.get("statement", ""))).strip() != actual_statement:
                errors.append(Finding(
                    "QTY-TRANSMITTED-REVIEW", ref,
                    "transmitted statement %d no longer matches the commentary" % number))
            proposition = str(item.get("proposition", "")).strip()
            source_slug = str(item.get("source", "")).strip()
            source_excerpt = str(item.get("source_excerpt", "")).strip()
            support = item.get("support")
            rationale = str(item.get("rationale", "")).strip()
            if len(proposition.split()) < 4:
                errors.append(Finding(
                    "QTY-TRANSMITTED-REVIEW", ref,
                    "transmitted statement %d does not state its supported proposition" % number))
            source_chapter, source_verse = _source_locator(item, chapter, verse)
            expected_source_fingerprint = source_passage_fingerprint(
                source_slug, source_chapter, source_verse)
            if (not _source_excerpt_matches(
                    source_slug, source_chapter, source_verse, source_excerpt)
                    or not expected_source_fingerprint
                    or item.get("source_fingerprint") != expected_source_fingerprint):
                errors.append(Finding(
                    "QTY-TRANSMITTED-SOURCE", ref,
                    "transmitted statement %d lacks a matching fingerprinted excerpt from an "
                    "allowlisted source" % number))
            if support not in ("direct", "contextual"):
                errors.append(Finding(
                    "QTY-TRANSMITTED-RELEVANCE", ref,
                    "transmitted statement %d is not approved as direct or contextual support" %
                    number))
            if support == "contextual" and len(rationale.split()) < 6:
                errors.append(Finding(
                    "QTY-TRANSMITTED-RELEVANCE", ref,
                    "transmitted statement %d needs a substantive contextual rationale" % number))

    actual_refs = cross_references(section)
    ledger = row.get("citations") if isinstance(row, dict) else None
    if not isinstance(ledger, list):
        errors.append(Finding("QTY-CITATION-REVIEW", ref,
                              "every Qur'an cross-reference needs a semantic relevance record"))
    elif len(ledger) != len(actual_refs):
        errors.append(Finding(
            "QTY-CITATION-REVIEW", ref,
            "review records %d citations but the commentary contains %d" %
            (len(ledger), len(actual_refs))))
    else:
        for number, ((actual_ref, actual_quote), item) in enumerate(zip(actual_refs, ledger), 1):
            if not isinstance(item, dict):
                errors.append(Finding("QTY-CITATION-REVIEW", ref,
                                      "citation %d has no review object" % number))
                continue
            if item.get("reference") != actual_ref or re.sub(
                    r"\s+", " ", str(item.get("quoted_clause", ""))).strip() != actual_quote:
                errors.append(Finding("QTY-CITATION-REVIEW", ref,
                                      "citation %d review does not match %s and its quoted clause" %
                                      (number, actual_ref)))
            proposition = str(item.get("proposition", "")).strip()
            support = item.get("support")
            rationale = str(item.get("rationale", "")).strip()
            if len(proposition.split()) < 4:
                errors.append(Finding("QTY-CITATION-REVIEW", ref,
                                      "citation %d does not state the proposition it is meant to support" % number))
            if support not in ("direct", "contextual"):
                errors.append(Finding("QTY-CITATION-RELEVANCE", ref,
                                      "citation %d is not approved as direct or contextual support" % number))
            if support == "contextual" and len(rationale.split()) < 6:
                errors.append(Finding("QTY-CITATION-RELEVANCE", ref,
                                      "citation %d needs a substantive rationale for contextual support" % number))
    return errors


def _review_scaffold_errors(chapter: int, section, review: dict, row: dict,
                            path: Path) -> List[Finding]:
    """Validate a review candidate without pretending that it is accepted.

    This is the GitHub-push gate.  A pending template must remain synchronized
    with source availability and every machine-detectable claim/evidence ledger.
    If the owner has already accepted the row, the complete semantic gate applies.
    """
    if (review.get("status") == "accepted" and isinstance(row, dict)
            and row.get("status") == "accepted"):
        return _review_errors(chapter, section, review, row, path)

    verse = section.verse
    ref = "%d:%d" % (chapter, verse)
    location = str(path.relative_to(C.REPO))
    errors = []
    if review.get("schema_version") != SCHEMA_VERSION:
        errors.append(Finding(
            "QTY-PUSH-REVIEW-SCHEMA", ref,
            "%s does not use review schema %d" % (location, SCHEMA_VERSION)))
    if not str(review.get("writer", "")).strip():
        errors.append(Finding(
            "QTY-PUSH-REVIEW-WRITER", ref,
            "%s must identify the writer before it is pushed for review" % location))
    if review.get("status") not in ("pending", "accepted"):
        errors.append(Finding(
            "QTY-PUSH-REVIEW-STATUS", ref,
            "%s must remain pending or record complete acceptance" % location))
    if not isinstance(row, dict):
        return errors + [Finding(
            "QTY-PUSH-REVIEW-STALE", ref,
            "%s has no verse review object" % location)]
    if row.get("status") not in ("pending", "accepted"):
        errors.append(Finding(
            "QTY-PUSH-REVIEW-STATUS", ref,
            "%s has an invalid verse status" % location))

    synthesis = row.get("source_synthesis")
    if not isinstance(synthesis, dict):
        errors.append(Finding(
            "QTY-PUSH-REVIEW-STALE", ref,
            "the pending review has no source-synthesis scaffold"))
    else:
        if synthesis.get("available_sources") != available_sources(chapter, verse):
            errors.append(Finding(
                "QTY-PUSH-REVIEW-STALE", ref,
                "the pending review source list no longer matches the corpus"))
        if synthesis.get("source_fingerprint") != source_fingerprint(chapter, verse):
            errors.append(Finding(
                "QTY-PUSH-REVIEW-STALE", ref,
                "the pending review source fingerprint no longer matches the corpus"))

    claim_review = row.get("claim_verification")
    actual_claims = substantive_claims(section)
    if not isinstance(claim_review, dict):
        errors.append(Finding(
            "QTY-PUSH-REVIEW-STALE", ref,
            "the pending review has no substantive-claim scaffold"))
    else:
        detected = claim_review.get("detected_claims")
        scaffolded = []
        if isinstance(detected, list):
            for item in detected:
                if isinstance(item, dict):
                    scaffolded.append((item.get("categories"), re.sub(
                        r"\s+", " ", str(item.get("statement", ""))).strip()))
                else:
                    scaffolded.append((None, ""))
        expected = [(categories, statement) for categories, statement in actual_claims]
        if scaffolded != expected:
            errors.append(Finding(
                "QTY-PUSH-REVIEW-STALE", ref,
                "the pending substantive-claim ledger no longer matches the commentary"))
        if not isinstance(claim_review.get("additional_material_claims"), list):
            errors.append(Finding(
                "QTY-PUSH-REVIEW-STALE", ref,
                "additional_material_claims must remain a list in the review candidate"))

    actual_refs = cross_references(section)
    ledger = row.get("citations")
    scaffolded_refs = []
    if isinstance(ledger, list):
        for item in ledger:
            if isinstance(item, dict):
                scaffolded_refs.append((item.get("reference"), re.sub(
                    r"\s+", " ", str(item.get("quoted_clause", ""))).strip()))
            else:
                scaffolded_refs.append((None, ""))
    if scaffolded_refs != actual_refs:
        errors.append(Finding(
            "QTY-PUSH-REVIEW-STALE", ref,
            "the pending Qur'an-citation ledger no longer matches the commentary"))

    actual_transmitted = transmitted_evidence(section)
    transmitted = row.get("transmitted_evidence")
    scaffolded_transmitted = []
    if isinstance(transmitted, list):
        for item in transmitted:
            scaffolded_transmitted.append(
                re.sub(r"\s+", " ", str(item.get("statement", ""))).strip()
                if isinstance(item, dict) else "")
    if scaffolded_transmitted != actual_transmitted:
        errors.append(Finding(
            "QTY-PUSH-REVIEW-STALE", ref,
            "the pending transmitted-evidence ledger no longer matches the commentary"))
    return errors


def _repeated_clause(section) -> Optional[str]:
    """Return a 5+-word clause pasted three times inside one sentence, if present.

    Two parallel uses can be deliberate rhetoric (and occur in chapter 1).  Three
    non-overlapping copies are the unfinished-edit signature this hard rule is for.
    """
    for sentence in C.sentence_split(prose_text(section)):
        tokens = C.norm_key(sentence).split()
        for size in range(min(12, len(tokens) // 3), 4, -1):
            positions = collections.defaultdict(list)
            for i in range(len(tokens) - size + 1):
                positions[tuple(tokens[i:i + size])].append(i)
            for gram, starts in positions.items():
                non_overlapping = []
                for start in starts:
                    if not non_overlapping or start - non_overlapping[-1] >= size:
                        non_overlapping.append(start)
                if len(non_overlapping) >= 3:
                    return " ".join(gram)
    return None


def _chunks(values: Sequence[int], size: int) -> Iterable[List[int]]:
    values = sorted(values)
    for start in range(0, len(values), size):
        chunk = values[start:start + size]
        if len(chunk) == size and chunk == list(range(chunk[0], chunk[0] + size)):
            yield chunk


def _exception_allowed(code: str, verses: Sequence[int], chapter: int,
                       reviews: Dict[Tuple[int, int], Tuple[dict, dict, Path]]) -> bool:
    if code.startswith("QTY-HARD") or code.startswith("QTY-CITATION"):
        return False
    for verse in verses:
        item = reviews.get((chapter, verse))
        if not item:
            return False
        review, row, _path = item
        if (review.get("status") != "accepted" or not isinstance(row, dict)
                or row.get("status") != "accepted"
                or review.get("independent") is not True):
            return False
        rationale = (review.get("exceptions") or {}).get(code, "")
        if len(str(rationale).split()) < 8:
            return False
    return bool(verses)


def _metric_findings(chapter: int, sections: Sequence, baseline: dict) -> List[Finding]:
    findings = []
    by_verse = {s.verse: s for s in sections}
    thresholds = baseline["thresholds"]
    verses = sorted(by_verse)

    # Fifty-verse metric windows catch prose drift near its beginning.  Style only:
    # the amount of evidence is reported by ``metrics()`` but is never an alarm.
    for chunk in _chunks(verses, METRIC_CHECKPOINT_SIZE):
        group = [by_verse[v] for v in chunk]
        m = metrics(group)
        ref = "%d:%d-%d" % (chapter, chunk[0], chunk[-1])
        affected = tuple(chunk)
        if m["mean_sentence"] > thresholds["mean_sentence_max"]:
            findings.append(Finding(
                "QTY-PROSE-DRIFT", ref,
                "mean sentence %.1f exceeds the Chapter-1 alarm %.1f" %
                (m["mean_sentence"], thresholds["mean_sentence_max"]), affected, False))
        if m["long_sentence_share"] > thresholds["long_sentence_share_max"]:
            findings.append(Finding(
                "QTY-PROSE-DRIFT", ref,
                "%.1f%% of sentences exceed 40 words; Chapter-1 alarm is %.1f%%" %
                (100 * m["long_sentence_share"], 100 * thresholds["long_sentence_share_max"]),
                affected, False))
        if m["flesch"] < thresholds["flesch_min"]:
            findings.append(Finding(
                "QTY-READABILITY-DRIFT", ref,
                "Flesch %.0f is below the Chapter-1 alarm %.0f" %
                (m["flesch"], thresholds["flesch_min"]), affected, False))

    # One hundred verses reveal a production mould or token authority floor.
    for chunk in _chunks(verses, METRIC_CHECKPOINT_SIZE * 2):
        group = [by_verse[v] for v in chunk]
        ref = "%d:%d-%d" % (chapter, chunk[0], chunk[-1])
        affected = tuple(chunk)
        mentions = []
        for section in group:
            mentions.extend(_authority_mentions(section.body()))
        if len(mentions) >= len(chunk):
            top, count = collections.Counter(mentions).most_common(1)[0]
            share = count / len(mentions)
            if share > thresholds["authority_concentration_max"]:
                findings.append(Finding(
                    "QTY-SOURCE-CONCENTRATION", ref,
                    "%s supplies %.0f%% of named authority/collection mentions; this resembles an "
                    "evidence-floor token rather than source synthesis" % (top, share * 100),
                    affected, False))
        shapes = collections.Counter(section_shape(s) for s in group)
        shape, count = shapes.most_common(1)[0]
        share = count / len(group)
        if share >= thresholds["shape_concentration_max"]:
            findings.append(Finding(
                "QTY-SHAPE-DRIFT", ref,
                "%d of %d verses share the same %d-heading/%d-paragraph arrangement" %
                (count, len(group), shape[0], shape[1]), affected, False))
        final_share = sum(_final_application(s) for s in group) / len(group)
        if final_share >= thresholds["final_application_share_max"]:
            findings.append(Finding(
                "QTY-APPLICATION-TEMPLATE", ref,
                "present-day application appears in the final paragraph of %.0f%% of this range; "
                "application has become a fixed slot" % (final_share * 100), affected, False))
    return findings


def evaluate(chapter: int, verses: Sequence[int], require_reviews: bool = True,
             push_check: bool = False) -> Tuple[List[Finding], dict]:
    """Evaluate acceptance, a review-candidate push, or metrics-only prose.

    ``push_check`` deliberately accepts synchronized pending templates but never
    advances the independently accepted frontier.  It cannot be combined with a
    full acceptance check.
    """
    if require_reviews and push_check:
        raise ValueError("push_check and require_reviews are mutually exclusive")
    baseline, findings = load_baseline()
    doc = C.load_chapter_doc(chapter)
    if doc is None:
        return findings + [Finding("QTY-NO-CHAPTER", str(chapter), "chapter file does not exist")], {}
    smap = doc.section_map()
    sections = []
    for verse in sorted(set(verses)):
        section = smap.get(verse)
        if section is None or not _written(section):
            findings.append(Finding("QTY-NOT-WRITTEN", "%d:%d" % (chapter, verse),
                                    "verse is not complete enough for quality review", (verse,)))
        else:
            sections.append(section)

    # Chapter 1 is the frozen yardstick.  It is not required to review itself.
    if chapter == BASELINE_CHAPTER:
        return findings, metrics(sections) if sections else {}

    reviews, review_load_findings = load_reviews()
    findings.extend(review_load_findings)
    if require_reviews and sections and min(s.verse for s in sections) > 1:
        required_frontier = min(s.verse for s in sections) - 1
        frontier = accepted_frontier(chapter)
        if frontier < required_frontier:
            findings.append(Finding(
                "QTY-PRIOR-FRONTIER", "%d:%d" % (chapter, required_frontier),
                "cannot accept or advance this range while the independently accepted frontier "
                "is %d:%d" % (chapter, frontier), tuple(s.verse for s in sections)))
    if require_reviews:
        for section in sections:
            item = reviews.get((chapter, section.verse))
            if not item:
                findings.append(Finding(
                    "QTY-REVIEW-MISSING", section.ref,
                    "no independent all-source, Chapter-1 parity and evidence-relevance review exists",
                    (section.verse,)))
            else:
                findings.extend(_review_errors(chapter, section, *item))
    elif push_check:
        frontier, approval_findings = draft_approval_frontier(chapter)
        findings.extend(approval_findings)
        all_written = sorted(s.verse for s in smap.values() if _written(s))
        unaccepted = [verse for verse in all_written if verse > frontier]
        if unaccepted:
            expected = list(range(frontier + 1, max(unaccepted) + 1))
            if unaccepted != expected:
                findings.append(Finding(
                    "QTY-UNACCEPTED-FRONTIER", "%d:%d" % (chapter, frontier),
                    "review candidates must extend the accepted or owner-approved draft frontier "
                    "without skipping verses", tuple(unaccepted)))
            if len(unaccepted) > REVIEW_CHECKPOINT_SIZE:
                findings.append(Finding(
                    "QTY-UNACCEPTED-LIMIT", "%d:%d-%d" %
                    (chapter, unaccepted[0], unaccepted[-1]),
                    "no more than %d new drafts may follow the last independent acceptance "
                    "or recorded owner draft approval" % REVIEW_CHECKPOINT_SIZE, tuple(unaccepted)))
        for section in sections:
            item = reviews.get((chapter, section.verse))
            if not item:
                findings.append(Finding(
                    "QTY-PUSH-REVIEW-MISSING", section.ref,
                    "a synchronized pending review template is required before this draft is pushed",
                    (section.verse,)))
            else:
                findings.extend(_review_scaffold_errors(chapter, section, *item))

    for section in sections:
        repeated = _repeated_clause(section)
        if repeated:
            findings.append(Finding(
                "QTY-HARD-REPEATED-CLAUSE", section.ref,
                "a clause of five or more words repeats inside one sentence: %r" % repeated,
                (section.verse,)))

    if baseline and sections:
        metric_sections = list(sections)
        # A review checkpoint also sees the fifty verses immediately before it,
        # so authority/shape/application degeneration is detected in a rolling
        # hundred rather than only when somebody later audits the chapter.
        requested = {s.verse for s in sections}
        if len(sections) <= REVIEW_CHECKPOINT_SIZE:
            first = min(requested)
            previous = [smap[v] for v in range(max(1, first - METRIC_CHECKPOINT_SIZE), first)
                        if v in smap and _written(smap[v])]
            if len(previous) == METRIC_CHECKPOINT_SIZE:
                metric_sections = previous + metric_sections
        for finding in _metric_findings(chapter, metric_sections, baseline):
            if not requested.intersection(finding.verses):
                continue
            if not _exception_allowed(finding.code, finding.verses, chapter, reviews):
                findings.append(finding)
    return findings, metrics(sections) if sections else {}


def review_valid(chapter: int, section,
                 reviews: Dict[Tuple[int, int], Tuple[dict, dict, Path]]) -> bool:
    item = reviews.get((chapter, section.verse))
    return bool(item and not _review_errors(chapter, section, *item))


def accepted_frontier(chapter: int) -> int:
    """Last contiguous verse that passes review *and* unwaived drift checks."""
    if chapter == BASELINE_CHAPTER:
        return C.verse_count(chapter)
    doc = C.load_chapter_doc(chapter)
    if doc is None:
        return 0
    reviews, load_errors = load_reviews()
    if load_errors:
        return 0
    smap = doc.section_map()
    frontier = 0
    accepted_sections = []
    for verse in range(1, C.verse_count(chapter) + 1):
        section = smap.get(verse)
        if not section or not _written(section) or not review_valid(chapter, section, reviews):
            break
        repeated = _repeated_clause(section)
        if repeated:
            break
        accepted_sections.append(section)
        frontier = verse

    baseline, baseline_errors = load_baseline()
    if not baseline or baseline_errors or not accepted_sections:
        return 0 if baseline_errors else frontier
    for finding in _metric_findings(chapter, accepted_sections, baseline):
        if not _exception_allowed(finding.code, finding.verses, chapter, reviews):
            frontier = min(frontier, min(finding.verses) - 1)
    return max(0, frontier)


def _draft_approval_hashes(chapter: int, start: int, end: int, doc) -> dict:
    """Bind an owner's drafting permission to exactly the prose and source map seen.

    Later verses are deliberately excluded, so continuing the draft cannot make
    the previous approval stale. Changes within the approved scope do invalidate it.
    """
    smap = doc.section_map()
    verses = list(range(start, end + 1))
    if any(v not in smap or not _written(smap[v]) for v in verses):
        raise ValueError("draft approval requires complete prose throughout its range")
    content = {
        "chapter": chapter,
        "introduction": doc.intro if start == 1 else None,
        "verses": [(v, smap[v].quote(), smap[v].body()) for v in verses],
    }
    sources = [(v, source_fingerprint(chapter, v)) for v in verses]
    return {
        key: hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        for key, value in (("content_sha256", content), ("sources_sha256", sources))
    }


def draft_approval_frontier(chapter: int) -> Tuple[int, List[Finding]]:
    """Draft-continuation permission only; NEVER independent acceptance.

    This function is used only by push/status checks. Acceptance, baseline changes
    and publication continue to use accepted_frontier and the complete reviews.
    """
    frontier = accepted_frontier(chapter)
    independent_frontier = frontier
    doc = C.load_chapter_doc(chapter)
    findings = []
    approved = []
    for path in sorted((DRAFT_APPROVALS_DIR / C.pad3(chapter)).glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("approval must be a JSON object")
            start, end = record.get("from"), record.get("to")
            writer, owner = record.get("writer"), record.get("owner")
            if (record.get("schema_version") != DRAFT_APPROVAL_SCHEMA
                    or record.get("chapter") != chapter
                    or record.get("scope") != "draft_continuation"
                    or record.get("approved") is not True
                    or type(start) is not int or type(end) is not int
                    or not 1 <= start <= end <= C.verse_count(chapter)
                    or end - start + 1 > REVIEW_CHECKPOINT_SIZE
                    or not isinstance(writer, str) or not writer.strip()
                    or not isinstance(owner, str) or not owner.strip()
                    or writer.strip() == owner.strip()
                    or not isinstance(record.get("approval_statement"), str)
                    or len(record["approval_statement"].split()) < 5
                    or not isinstance(record.get("candidate_commit"), str)
                    or not re.fullmatch(r"[0-9a-f]{40}", record["candidate_commit"])):
                raise ValueError("approval needs a bounded range, distinct owner/writer, explicit statement and candidate commit")
            # Complete independent acceptance supersedes an older drafting receipt.
            if end <= independent_frontier:
                continue
            if doc is None:
                raise ValueError("approved chapter no longer exists")
            hashes = _draft_approval_hashes(chapter, start, end, doc)
            if any(record.get(key) != value for key, value in hashes.items()):
                findings.append(Finding(
                    "QTY-DRAFT-APPROVAL-STALE", "%d:%d-%d" % (chapter, start, end),
                    "approved prose or sources changed; renewed owner approval is required in %s" % path.name,
                    tuple(range(start, end + 1))))
                continue
            approved.append((start, end))
        except (OSError, ValueError, TypeError, KeyError) as exc:
            findings.append(Finding("QTY-DRAFT-APPROVAL-INVALID", str(chapter),
                                    "%s: %s" % (path.name, exc)))
    for start, end in sorted(approved):
        if start > frontier + 1:
            findings.append(Finding(
                "QTY-DRAFT-APPROVAL-GAP", "%d:%d-%d" % (chapter, start, end),
                "owner draft approvals must extend the existing frontier without gaps",
                tuple(range(start, end + 1))))
        else:
            frontier = max(frontier, end)
    return frontier, findings


def _verify_draft_snapshot(chapter: int, start: int, end: int, doc, commit: str) -> None:
    """At recording time, verify the cited Git candidate, not just its hash syntax.

    Validation of stored receipts uses fingerprints and needs no historical Git
    objects, so ordinary push checks work in a shallow CI checkout as well.
    """
    try:
        text = subprocess.check_output(
            ["git", "show", "%s:tafsir/%s.md" % (commit, C.pad3(chapter))],
            cwd=C.REPO, text=True, stderr=subprocess.PIPE)
        snapshot = C.ChapterDoc(chapter, C.output_path(chapter), text)
        if (_draft_approval_hashes(chapter, start, end, snapshot)["content_sha256"] !=
                _draft_approval_hashes(chapter, start, end, doc)["content_sha256"]):
            raise ValueError("current prose differs from the candidate the owner approved")
        paths = ["%s/%s.%s" % (slug, C.pad3(chapter), "md" if slug == C.INITIAL_SLUG else "txt")
                 for slug in C.SOURCE_ALLOWLIST]
        subprocess.check_output(["git", "diff", "--exit-code", commit, "--", *paths],
                                cwd=C.REPO, stderr=subprocess.PIPE)
        if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all", "--", *paths],
                                   cwd=C.REPO, stderr=subprocess.PIPE).strip():
            raise ValueError("source files must be committed and match the approved candidate")
    except subprocess.CalledProcessError as exc:
        raise ValueError("approved Git candidate is unavailable or its source files differ") from exc


def approve_draft(chapter: int, start: int, end: int, writer: str, owner: str,
                  statement: str, candidate_commit: str) -> Path:
    """Record an approval actually supplied by the owner, not a writer's review."""
    if (chapter == BASELINE_CHAPTER or not 1 <= chapter <= 114
            or not 1 <= start <= end <= C.verse_count(chapter)
            or end - start + 1 > REVIEW_CHECKPOINT_SIZE
            or not writer.strip() or not owner.strip() or writer.strip() == owner.strip()
            or len(statement.split()) < 5 or not re.fullmatch(r"[0-9a-f]{40}", candidate_commit)):
        raise SystemExit("draft approval needs 1–50 verses, distinct owner/writer, the owner's statement and a full commit hash")
    doc = C.load_chapter_doc(chapter)
    if doc is None:
        raise SystemExit("chapter does not exist")
    try:
        hashes = _draft_approval_hashes(chapter, start, end, doc)
        _verify_draft_snapshot(chapter, start, end, doc, candidate_commit)
    except ValueError as exc:
        raise SystemExit(str(exc))
    findings, _metrics = evaluate(chapter, list(range(start, end + 1)),
                                 require_reviews=False, push_check=True)
    if findings:
        raise SystemExit("repair the candidate before recording approval: " +
                         "; ".join(f.code for f in findings))
    frontier, _errors = draft_approval_frontier(chapter)
    if start > frontier + 1:
        raise SystemExit("draft approval must extend the existing frontier without gaps")
    path = DRAFT_APPROVALS_DIR / C.pad3(chapter) / ("%03d-%03d.json" % (start, end))
    if path.exists():
        raise SystemExit("draft approval already exists: %s" % path)
    payload = {
        "schema_version": DRAFT_APPROVAL_SCHEMA, "scope": "draft_continuation",
        "chapter": chapter, "from": start, "to": end, "approved": True,
        "writer": writer, "owner": owner, "approval_statement": statement,
        "candidate_commit": candidate_commit, **hashes,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def template(chapter: int, start: int, end: int, writer: str) -> Path:
    if end < start or end - start + 1 > REVIEW_CHECKPOINT_SIZE:
        raise SystemExit("one independent review checkpoint contains 1-%d verses" % REVIEW_CHECKPOINT_SIZE)
    doc = C.load_chapter_doc(chapter)
    if doc is None:
        raise SystemExit("tafsir/%s.md does not exist" % C.pad3(chapter))
    smap = doc.section_map()
    rows = {}
    for verse in range(start, end + 1):
        section = smap.get(verse)
        if section is None or not _written(section):
            raise SystemExit("%d:%d is not written" % (chapter, verse))
        citations = [
            {
                "reference": reference,
                "quoted_clause": quote,
                "proposition": "",
                "support": "pending",
                "rationale": "",
            }
            for reference, quote in cross_references(section)
        ]
        transmitted = [
            {
                "statement": statement,
                "proposition": "",
                "source": "",
                "source_reference": "%d:%d" % (chapter, verse),
                "source_fingerprint": "",
                "source_excerpt": "",
                "support": "pending",
                "rationale": "",
            }
            for statement in transmitted_evidence(section)
        ]
        claims = [
            {
                "categories": categories,
                "statement": statement,
                "proposition": "",
                "source": "",
                "source_reference": "%d:%d" % (chapter, verse),
                "source_fingerprint": "",
                "source_excerpt": "",
                "support": "pending",
                "rationale": "",
            }
            for categories, statement in substantive_claims(section)
        ]
        rows[str(verse)] = {
            "status": "pending",
            "scores": {dimension: None for dimension in RUBRIC},
            "source_synthesis": {
                "source_fingerprint": source_fingerprint(chapter, verse),
                "available_sources": available_sources(chapter, verse),
                "coverage": "pending",
                "notes": "",
                "distinct_material_evidence": [],
            },
            "claim_verification": {
                "coverage": "pending",
                "notes": "",
                "detected_claims": claims,
                "additional_material_claims": [],
            },
            "citations": citations,
            "transmitted_evidence": transmitted,
            "notes": "",
        }
    payload = {
        "schema_version": SCHEMA_VERSION,
        "chapter": chapter,
        "from": start,
        "to": end,
        "writer": writer,
        "reviewer": "",
        "independent": False,
        "status": "pending",
        "exceptions": {},
        "verses": rows,
    }
    directory = REVIEWS_DIR / C.pad3(chapter)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / ("%03d-%03d.json" % (start, end))
    if path.exists():
        raise SystemExit("review template already exists: %s" % path.relative_to(C.REPO))
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _print_baseline(data: dict) -> None:
    m = data["metrics"]
    t = data["thresholds"]
    print("CHAPTER 1 — FROZEN WRITING-STYLE YARDSTICK")
    print("  sha256: %s" % data["sha256"])
    print("  words: %d | mean sentence %.1f | >40 words %.1f%% | Flesch %.0f" %
          (m["words"], m["mean_sentence"], 100 * m["long_sentence_share"], m["flesch"]))
    print("  evidence mentions: %.1f per 1,000 prose words (information only, never an alarm)" %
          m["evidence_mentions_per_1000"])
    print("  style alarms: mean > %.1f | >40 words > %.1f%% | Flesch < %.0f" %
          (t["mean_sentence_max"], 100 * t["long_sentence_share_max"], t["flesch_min"]))


def _emit(chapter: int, verses: Sequence[int], findings: Sequence[Finding], range_metrics: dict,
          json_output: bool = False, mode: str = "acceptance") -> int:
    if json_output:
        print(json.dumps({
            "chapter": chapter,
            "verses": list(verses),
            "mode": mode,
            "ok": not findings,
            "last_accepted_verse": accepted_frontier(chapter),
            "metrics": range_metrics,
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
        return 1 if findings else 0
    if findings:
        if mode == "push":
            print("PUSH CHECK FAILED — CHECKPOINT NOT READY")
        elif mode == "metrics":
            print("QUALITY DIAGNOSTIC FAILED")
        else:
            print("QUALITY DRIFT — ACCEPTANCE AND PUBLICATION STOPPED")
        print("chapter %d | last independently accepted verse: %d:%d" %
              (chapter, chapter, accepted_frontier(chapter)))
        if mode == "acceptance":
            print("No later verse may be accepted, published or used as the quality baseline.\n")
        elif mode == "push":
            print("Repair the draft/template before committing and pushing this generation stop.\n")
        else:
            print("This diagnostic never grants semantic acceptance.\n")
        for finding in findings:
            print("BLOCK %-28s %-12s %s" % (finding.code, finding.ref, finding.message))
            if os.environ.get("GITHUB_ACTIONS"):
                print("::error title=%s,file=tafsir/%s.md::%s %s" %
                      (finding.code, C.pad3(chapter), finding.ref, finding.message))
        return 1
    if chapter == BASELINE_CHAPTER:
        print("QUALITY BASELINE PASS — chapter 1 matches its frozen hash and measurements")
    elif mode == "push":
        print("PUSH CHECK PASS — %d:%d-%d is ready for a review-candidate push" %
              (chapter, min(verses), max(verses)))
        print("independent acceptance may remain pending; publication is still blocked")
    elif mode == "metrics":
        print("QUALITY DIAGNOSTIC PASS — no mechanical quantitative drift was detected")
        print("this result is not semantic acceptance")
    else:
        print("QUALITY PARITY PASS — %d:%d-%d independently reviewed against chapter 1" %
              (chapter, min(verses), max(verses)))
    print("last independently accepted verse: %d:%d" % (chapter, accepted_frontier(chapter)))
    if mode == "push" and chapter != BASELINE_CHAPTER:
        draft_frontier, _approval_findings = draft_approval_frontier(chapter)
        print("draft-continuation frontier: %d:%d (not publication approval)" % (chapter, draft_frontier))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", nargs="?", type=int)
    ap.add_argument("--from", dest="start", type=int)
    ap.add_argument("--to", dest="end", type=int)
    ap.add_argument("--all", action="store_true", help="check all written non-baseline commentary")
    ap.add_argument("--baseline", action="store_true", help="show and validate the frozen chapter-1 floor")
    ap.add_argument("--freeze-baseline", action="store_true",
                    help="rewrite the frozen baseline only with an independent approval record")
    ap.add_argument("--approval", help="JSON approval required when changing an existing baseline")
    ap.add_argument("--template", action="store_true",
                    help="create an independent review template (maximum 50 verses)")
    ap.add_argument("--writer", help="writer identity recorded in a review template or draft approval")
    ap.add_argument("--approve-draft", action="store_true",
                    help="record explicit owner permission to continue drafting; NOT semantic acceptance")
    ap.add_argument("--owner", help="owner identity, distinct from the writer, for --approve-draft")
    ap.add_argument("--approval-statement", help="the actual owner statement authorizing continued drafting")
    ap.add_argument("--candidate-commit", help="full commit hash of the draft the owner approved")
    ap.add_argument("--push-check", action="store_true",
                    help="validate a review-candidate push; pending review is allowed but must be synchronized")
    ap.add_argument("--metrics-only", action="store_true",
                    help="diagnostic only: skip review manifests; never counts as acceptance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.push_check and args.metrics_only:
        ap.error("--push-check and --metrics-only are mutually exclusive")

    if args.approve_draft:
        if (not args.chapter or args.start is None or args.end is None or not args.writer
                or not args.owner or not args.approval_statement or not args.candidate_commit):
            ap.error("--approve-draft needs chapter, --from, --to, --writer, --owner, --approval-statement and --candidate-commit")
        if args.freeze_baseline or args.baseline or args.template or args.all or args.push_check or args.metrics_only:
            ap.error("--approve-draft cannot be combined with another action")
        path = approve_draft(args.chapter, args.start, args.end, args.writer, args.owner,
                             args.approval_statement, args.candidate_commit)
        print("wrote %s" % path.relative_to(C.REPO))
        print("Owner permission advances drafting only. Independent review and publication gates are unchanged.")
        return 0

    if args.freeze_baseline:
        previous = None
        if BASELINE_PATH.exists():
            previous = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        validate_baseline_approval(args.approval)
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = preserve_stronger_thresholds(baseline_payload(), previous)
        BASELINE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote %s" % BASELINE_PATH.relative_to(C.REPO))
        _print_baseline(data)
        return 0

    if args.baseline:
        data, findings = load_baseline()
        if data:
            _print_baseline(data)
        for finding in findings:
            print("BLOCK %s %s" % (finding.code, finding.message))
        return 1 if findings else 0

    if args.template:
        if not args.chapter or args.start is None or args.end is None or not args.writer:
            ap.error("--template needs chapter, --from, --to and --writer")
        path = template(args.chapter, args.start, args.end, args.writer)
        print("wrote %s" % path.relative_to(C.REPO))
        print("A different reviewer must complete all-source synthesis, claim/evidence ledgers, and scores before acceptance.")
        return 0

    if args.all:
        overall = 0
        any_written = False
        for chapter in C.chapter_numbers():
            if chapter == BASELINE_CHAPTER or not C.output_path(chapter).exists():
                continue
            doc = C.load_chapter_doc(chapter)
            verses = [s.verse for s in doc.sections if _written(s)]
            if not verses:
                continue
            any_written = True
            findings, m = evaluate(
                chapter, verses,
                require_reviews=not args.metrics_only and not args.push_check,
                push_check=args.push_check)
            mode = "push" if args.push_check else ("metrics" if args.metrics_only else "acceptance")
            overall |= _emit(chapter, verses, findings, m, args.json, mode)
        if not any_written:
            print("no non-baseline commentary is written")
        return overall

    if not args.chapter:
        ap.error("give a chapter, --all, --baseline or --freeze-baseline")
    doc = C.load_chapter_doc(args.chapter)
    if doc is None:
        raise SystemExit("tafsir/%s.md does not exist" % C.pad3(args.chapter))
    written = [s.verse for s in doc.sections if _written(s)]
    start = args.start if args.start is not None else (min(written) if written else 1)
    end = args.end if args.end is not None else (max(written) if written else start)
    verses = list(range(start, end + 1))
    findings, m = evaluate(
        args.chapter, verses,
        require_reviews=not args.metrics_only and not args.push_check,
        push_check=args.push_check)
    mode = "push" if args.push_check else ("metrics" if args.metrics_only else "acceptance")
    return _emit(args.chapter, verses, findings, m, args.json, mode)


if __name__ == "__main__":
    raise SystemExit(main())
