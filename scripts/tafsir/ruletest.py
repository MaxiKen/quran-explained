#!/usr/bin/env python3
"""ruletest.py — do the v7 rules bite, with no chapter on disk?

``selftest.py`` breaks each rule on a scratch copy of a *written* chapter, so it
cannot run while the corpus is being rewritten and has nothing to point at. This
script covers the rules that can be judged on synthetic prose, so the v7 standard
(``TAFSIR_RULES.md`` §0) is proven the moment it is added:

    python3 scripts/tafsir/ruletest.py

It checks that

* ``WRD-PARA-FLOOR`` fails a paragraph of 120 words or fewer and passes a longer one;
* ``STY-PARAPHRASE`` fails a point handed to a named work — reported, framed
  ("according to …", "the reading of …"), or led by the work's name — and passes
  an early authority cited as evidence (Ibn ʿAbbās), a report with its collection,
  and a plain mention of the eleven with no claim attached;
* ``SRC-QUOTED`` fails a quotation standing beside a work's name, and passes a
  hadith quoted with its collection;
* ``STY-APPLICATION`` sees the reader's own world only when the phrasing actually
  reaches it;
* v7.2: ``REF-BARE`` counts cross-references that carry no wording — one or two in a
  section warn, three in one section fail — and passes a citation expanded with the
  clause it points to.

Exit status is 0 when every expectation holds.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit as A  # noqa: E402

FAIL = A.FAIL


def findings(text: str, own_canon=None):
    """Run the authorship rule over synthetic prose; return the codes it raises."""
    out = []

    def fail(code, ref, line, msg):
        out.append(code)

    A._authorship_findings(text, own_canon, "3:1", 1, fail, curly=own_canon is not None)
    return sorted(set(out))


def long_para(tail: str = "") -> str:
    return ("The verse opens with a command, and the command carries a promise inside it. "
            "Every word here is doing work, and the work is the kind a reader can check "
            "against his own day. " * 8) + tail


AUTHORSHIP_CASES = [
    ("a reading written as the book's own", long_para(), []),
    ("a work reported", "Al-Ṭabarī records that the reading turns on the second clause.",
     ["STY-PARAPHRASE"]),
    ("a work framed", "According to al-Saʿdī, the verse is a warning to the heedless.",
     ["STY-PARAPHRASE"]),
    ("a work leading the sentence", "Ibn Kathīr, on this passage, is brief.",
     ["STY-PARAPHRASE"]),
    ("the vague stand-ins", "The commentators say the sentence is a warning.",
     ["STY-PARAPHRASE"]),
    ("a work quoted", 'The words of al-Jalālayn stand beside it: *"a brief enjoyment it is."*',
     ["STY-PARAPHRASE", "SRC-QUOTED"]),
    ("an early authority as evidence", "Ibn ʿAbbās said the word means the covenant itself.", []),
    ("a report with its collection",
     'Al-Bukhārī records that the Prophet ﷺ said, *"actions are by intentions."*', []),
    ("the eleven named as what was read",
     "This commentary was learned from al-Ṭabarī, al-Qurṭubī, al-Baghawī and the rest of the eleven.",
     []),
    ("the study draft relayed",
     "The study draft reads the verse as a warning to the heedless.", ["STY-PARAPHRASE"]),
]

PARA_CASES = [
    ("a short paragraph", "This paragraph is far too short to stand as one.", ["WRD-PARA-FLOOR"]),
    ("a full paragraph", long_para(), []),
]

class _Section:
    """The little a section needs to be judged for v7.1: a ref, a body, headings."""

    def __init__(self, ref, body, headings):
        self.ref, self._body, self._headings = ref, body, headings

    def body(self):
        return self._body

    def headings(self):
        return list(enumerate(self._headings, start=1))


def uniqueness(secs):
    """Run the v7.1 check over stub sections; return {level: [codes]}."""
    out = {"FAIL": [], "WARN": []}

    def fail(code, ref, line, msg):
        out["FAIL"].append(code)

    def warn(code, ref, line, msg):
        out["WARN"].append(code)

    A._uniqueness_findings(secs, fail, warn)
    return out


def _prose(n, tail=""):
    return ("Verse %d carries its own reading and its own way of saying it, with nothing "
            "borrowed from the verse beside it. " % n * 3) + tail


UNIQUENESS_CASES = [
    ("distinct verses stay clear",
     [_Section("1:1", "The opening names the owner of every act that follows, and the naming is "
                       "the first deed of the day. A worker who says it hands the hours over "
                       "before he spends them, which is why the line stands first.",
               ["THE OPENING WORD"]),
      _Section("1:2", "Praise arrives next, and it does not wait for a pleasant morning. The "
                       "verdict about who God is holds when the news is bad, and holding it is "
                       "the whole discipline the sentence asks of the tongue.",
               ["PRAISE AND ITS GROUND"])], []),
    ("one heading reused",
     [_Section("1:1", _prose(1), ["THE TWO NAMES"]),
      _Section("1:2", _prose(2), ["THE TWO NAMES"])], ["STY-UNIQUE-VERSE"]),
    ("one heading template",
     [_Section("1:%d" % i, _prose(i), ["THE RISE OF THINGS %d" % i]) for i in (1, 2, 3)],
     ["STY-UNIQUE-VERSE"]),
    ("one house opening",
     [_Section("1:%d" % i, "The point of the verse is that mercy answers fear. " * 3,
               ["TITLE %d" % i]) for i in (1, 2, 3)], ["STY-UNIQUE-VERSE"]),
    ("one arrangement, twelve verses",
     [_Section("1:%d" % i, _prose(i), ["A %d" % i, "B %d" % i, "C %d" % i]) for i in range(1, 13)],
     ["STY-UNIQUE-VERSE"]),
]

REF_CASES = [
    ("no citation at all", long_para(), []),
    ("one bare citation", long_para("The same promise stands elsewhere (2:255)."), ["WARN"]),
    ("two bare citations in one section",
     long_para("It answers (2:255) and it returns (2:256)."), ["WARN"]),
    ("three bare citations in one section",
     long_para("It answers (2:255), returns (2:256) and closes (2:257)."), ["FAIL"]),
    ("a list of citations",
     long_para("The Qur'an returns to the theme (2:156, 245, 281)."), ["WARN"]),
    ("an expanded citation",
     long_para("The Throne verse says (2:255 \u2014 **\u201cAllah! There is no god\u201d**) and "
               "the point stands."), []),
]


def bare_refs(text):
    """Run the v7.2 cross-reference rule over synthetic prose; return the levels raised."""
    out = []

    def fail(code, ref, line, msg):
        out.append("FAIL")

    def warn(code, ref, line, msg):
        out.append("WARN")

    A._bare_ref_findings(text, "3:1", 1, fail, warn)
    return out


APPLICATION_CASES = [
    ("reaching the reader today", long_para("And the same choice faces him today."), True),
    ("never reaching him", long_para(), False),
]


def main() -> int:
    bad = 0
    print("authorship — the book is the author's own (§0, v7)")
    for name, text, want in AUTHORSHIP_CASES:
        got = findings(text, own_canon="own wording not quoted here")
        ok = got == sorted(want)
        bad += not ok
        print("  %-4s %-34s want=%-28s got=%s"
              % ("ok" if ok else "FAIL", name, ",".join(want) or "-", ",".join(got) or "-"))

    print("paragraph floor — every paragraph past 120 words (§4, v7)")
    for name, para, want in PARA_CASES:
        out = []

        def fail(code, ref, line, msg):
            out.append(code)

        A._paragraph_floor([para], "3:1", 1, fail)
        ok = sorted(set(out)) == sorted(want)
        bad += not ok
        print("  %-4s %-34s want=%-28s got=%s"
              % ("ok" if ok else "FAIL", name, ",".join(want) or "-", ",".join(out) or "-"))

    print("v7.1 — no verse presented in another verse's shape or diction (§0.7)")
    for name, secs, want in UNIQUENESS_CASES:
        got = sorted(set(uniqueness(secs)["FAIL"] + uniqueness(secs)["WARN"]))
        ok = got == sorted(set(want))
        bad += not ok
        print("  %-4s %-34s want=%-28s got=%s"
              % ("ok" if ok else "FAIL", name, ",".join(want) or "-", ",".join(got) or "-"))

    print("v7.2 — every cross-reference carries the wording it points to (§2.5)")
    for name, text, want in REF_CASES:
        got = bare_refs(text)
        ok = bool(got) == bool(want)
        bad += not ok
        print("  %-4s %-34s want=%-28s got=%s"
              % ("ok" if ok else "FAIL", name, ",".join(want) or "-", ",".join(got) or "-"))

    print("application — the verse reaches the reader's own world (§8, v7)")
    for name, text, want in APPLICATION_CASES:
        got = bool(A.APPLICATION.search(text))
        ok = got == want
        bad += not ok
        print("  %-4s %-34s want=%-28s got=%s"
              % ("ok" if ok else "FAIL", name, want, got))

    print()
    print("v7 rule test: %s" % ("all expectations hold" if not bad else "%d FAILED" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
