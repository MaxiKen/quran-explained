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
  and a plain mention of the ten with no claim attached;
* ``SRC-QUOTED`` fails a quotation standing beside a work's name, and passes a
  hadith quoted with its collection;
* ``STY-APPLICATION`` sees the reader's own world only when the phrasing actually
  reaches it.

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
    ("the ten named as what was read",
     "This commentary was learned from al-Ṭabarī, al-Qurṭubī, al-Baghawī and the rest of the ten.",
     []),
]

PARA_CASES = [
    ("a short paragraph", "This paragraph is far too short to stand as one.", ["WRD-PARA-FLOOR"]),
    ("a full paragraph", long_para(), []),
]

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
