#!/usr/bin/env python3
"""Chapter-1 parity gate for new tafsir writing (quality standard v8).

The ordinary auditor proves format and minimum evidence.  This gate answers the
separate question the old gate could not answer: does a newly written range still
match the accepted quality of chapter 1?

Fifty verses may be mapped at once, but quality is judged in checkpoints of no
more than five verses.  Every non-baseline verse needs an independent semantic
review in ``quality/reviews/``.  A review scores the prose against chapter 1 and
verifies every Qur'an cross-reference for relevance, not merely verbatim copying.

Examples:

    python3 scripts/tafsir/quality.py --baseline
    python3 scripts/tafsir/quality.py 2 --from 101 --to 105
    python3 scripts/tafsir/quality.py --template 2 --from 101 --to 105 --writer writer-id
    python3 scripts/tafsir/quality.py --all

A non-zero exit means ``QUALITY DRIFT``.  Generation, acceptance and publication
must stop at that point; the output reports the last independently accepted verse.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402
import corpus as C  # noqa: E402

BASELINE_CHAPTER = 1
CHECKPOINT_SIZE = 5
MIN_SCORE = 4
BASELINE_PATH = C.REPO / "quality" / "chapter-001-baseline.json"
REVIEWS_DIR = C.REPO / "quality" / "reviews"
SCHEMA_VERSION = 1

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
# approve a source-sparse or technically difficult checkpoint by documenting a
# metric exception.  Hard defects and missing semantic review cannot be waived.
MEAN_SENTENCE_MARGIN = 2.0
FLESCH_MARGIN = 5.0
LONG_SENTENCE_MARGIN = 0.02
EVIDENCE_DENSITY_RATIO = 0.65
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
        "checkpoint_size": CHECKPOINT_SIZE,
        "rubric": list(RUBRIC),
        "minimum_score": MIN_SCORE,
        "thresholds": {
            "mean_sentence_max": metrics(doc.sections)["mean_sentence"] + MEAN_SENTENCE_MARGIN,
            "long_sentence_share_max": max(
                0.10, metrics(doc.sections)["long_sentence_share"] + LONG_SENTENCE_MARGIN),
            "flesch_min": metrics(doc.sections)["flesch"] - FLESCH_MARGIN,
            "evidence_density_min": (
                metrics(doc.sections)["evidence_mentions_per_1000"] * EVIDENCE_DENSITY_RATIO),
            "authority_concentration_max": AUTHORITY_CONCENTRATION_LIMIT,
            "shape_concentration_max": SHAPE_CONCENTRATION_LIMIT,
            "final_application_share_max": FINAL_APPLICATION_LIMIT,
        },
    }
    return result


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
    if (approval.get("approved") is not True
            or not str(approval.get("reviewer", "")).strip()
            or approval.get("old_sha256") != current.get("sha256")
            or approval.get("new_sha256") != actual
            or len(reason.split()) < 8):
        raise SystemExit(
            "baseline approval must name an independent reviewer, approve the change, match the "
            "old and new hashes, and give a substantive reason")


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
        if end < start or end - start + 1 > CHECKPOINT_SIZE or keys != expected:
            findings.append(Finding(
                "QTY-CHECKPOINT-SIZE", str(path.relative_to(C.REPO)),
                "one review must contain exactly its consecutive from/to range and no more than "
                "%d verses" % CHECKPOINT_SIZE))
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
                                      "%s scored %d; 4 is the Chapter-1 quality floor" %
                                      (dimension, score)))

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
        review = item[0]
        rationale = (review.get("exceptions") or {}).get(code, "")
        if len(str(rationale).split()) < 8:
            return False
    return bool(verses)


def _metric_findings(chapter: int, sections: Sequence, baseline: dict) -> List[Finding]:
    findings = []
    by_verse = {s.verse: s for s in sections}
    thresholds = baseline["thresholds"]
    verses = sorted(by_verse)

    # Five-verse checkpoints catch prose and evidence drift near its beginning.
    for chunk in _chunks(verses, CHECKPOINT_SIZE):
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
        if m["evidence_mentions_per_1000"] < thresholds["evidence_density_min"]:
            findings.append(Finding(
                "QTY-EVIDENCE-DRIFT", ref,
                "checkable Qur'an/authority evidence density %.1f per 1,000 words is below the "
                "Chapter-1 alarm %.1f; do not add token citations—review the unused source material" %
                (m["evidence_mentions_per_1000"], thresholds["evidence_density_min"]),
                affected, False))

    # Ten verses are enough to reveal a production mould or token authority floor.
    for chunk in _chunks(verses, CHECKPOINT_SIZE * 2):
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


def evaluate(chapter: int, verses: Sequence[int], require_reviews: bool = True) -> Tuple[List[Finding], dict]:
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
                    "no independent Chapter-1 parity and citation-relevance review exists",
                    (section.verse,)))
            else:
                findings.extend(_review_errors(chapter, section, *item))

    for section in sections:
        repeated = _repeated_clause(section)
        if repeated:
            findings.append(Finding(
                "QTY-HARD-REPEATED-CLAUSE", section.ref,
                "a clause of five or more words repeats inside one sentence: %r" % repeated,
                (section.verse,)))

    if baseline and sections:
        metric_sections = list(sections)
        # A five-verse acceptance check also sees the five verses immediately
        # before it, so authority/shape/application degeneration is detected in
        # a rolling ten rather than only when somebody later audits the chapter.
        requested = {s.verse for s in sections}
        if len(sections) <= CHECKPOINT_SIZE:
            first = min(requested)
            previous = [smap[v] for v in range(max(1, first - CHECKPOINT_SIZE), first)
                        if v in smap and _written(smap[v])]
            if len(previous) == CHECKPOINT_SIZE:
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


def template(chapter: int, start: int, end: int, writer: str) -> Path:
    if end < start or end - start + 1 > CHECKPOINT_SIZE:
        raise SystemExit("one independent review checkpoint contains 1-%d verses" % CHECKPOINT_SIZE)
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
        rows[str(verse)] = {
            "status": "pending",
            "scores": {dimension: None for dimension in RUBRIC},
            "citations": citations,
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
    print("CHAPTER 1 — FROZEN QUALITY FLOOR")
    print("  sha256: %s" % data["sha256"])
    print("  words: %d | mean sentence %.1f | >40 words %.1f%% | Flesch %.0f" %
          (m["words"], m["mean_sentence"], 100 * m["long_sentence_share"], m["flesch"]))
    print("  evidence mentions: %.1f per 1,000 prose words" % m["evidence_mentions_per_1000"])
    print("  drift alarms: mean > %.1f | >40 words > %.1f%% | Flesch < %.0f | evidence < %.1f/1k" %
          (t["mean_sentence_max"], 100 * t["long_sentence_share_max"], t["flesch_min"],
           t["evidence_density_min"]))


def _emit(chapter: int, verses: Sequence[int], findings: Sequence[Finding], range_metrics: dict,
          json_output: bool = False) -> int:
    if json_output:
        print(json.dumps({
            "chapter": chapter,
            "verses": list(verses),
            "ok": not findings,
            "last_accepted_verse": accepted_frontier(chapter),
            "metrics": range_metrics,
            "findings": [asdict(f) for f in findings],
        }, ensure_ascii=False, indent=2))
        return 1 if findings else 0
    if findings:
        print("QUALITY DRIFT — GENERATION STOPPED")
        print("chapter %d | last independently accepted verse: %d:%d" %
              (chapter, chapter, accepted_frontier(chapter)))
        print("No later verse may be accepted, published or used as the quality baseline.\n")
        for finding in findings:
            print("BLOCK %-28s %-12s %s" % (finding.code, finding.ref, finding.message))
            if os.environ.get("GITHUB_ACTIONS"):
                print("::error title=%s,file=tafsir/%s.md::%s %s" %
                      (finding.code, C.pad3(chapter), finding.ref, finding.message))
        return 1
    if chapter == BASELINE_CHAPTER:
        print("QUALITY BASELINE PASS — chapter 1 matches its frozen hash and measurements")
    else:
        print("QUALITY PARITY PASS — %d:%d-%d independently reviewed against chapter 1" %
              (chapter, min(verses), max(verses)))
    print("last independently accepted verse: %d:%d" % (chapter, accepted_frontier(chapter)))
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
    ap.add_argument("--template", action="store_true", help="create an independent review template (maximum five verses)")
    ap.add_argument("--writer", help="writer identity recorded in a new review template")
    ap.add_argument("--metrics-only", action="store_true",
                    help="diagnostic only: skip review manifests; never counts as acceptance")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.freeze_baseline:
        validate_baseline_approval(args.approval)
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = baseline_payload()
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
        print("A different reviewer must complete every score and citation decision before acceptance.")
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
            findings, m = evaluate(chapter, verses, require_reviews=not args.metrics_only)
            overall |= _emit(chapter, verses, findings, m, args.json)
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
    findings, m = evaluate(args.chapter, verses, require_reviews=not args.metrics_only)
    return _emit(args.chapter, verses, findings, m, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
