#!/usr/bin/env python3
"""evidencemaptest.py — self-test of the evidence-map checker (``evidencemap.py``).

Runs on a small synthetic digest of chapter 103 (two works, a whole-sūrah passage repeated under
every verse), so it needs neither the source corpora nor ``tmp/sources``.  It builds one valid full
map, shows it passes, then breaks it one way at a time and requires the checker to notice:

    python3 scripts/tafsir/evidencemaptest.py        # prints PASS/FAIL per case; exit 1 on any failure

Cases: a pointer past the end of a passage; an item with no pointer in a full map; a paragraph neither
cited nor set aside; a paragraph both cited and set aside; a set-aside entry with no reason; too much
set aside; a survey map (warned, not held to the paragraph rule); a partly mapped chapter (counted, not
enforced); and the small helpers that read and print paragraph ranges.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402
import evidencemap as E  # noqa: E402

LONG = ("A real paragraph of evidence with plenty of letters in it, enough to count as more than a heading, "
        "so the paragraph rule applies to it.")
WHOLE = "\n\n".join(["Heading with enough letters to count as a paragraph of its own here.", LONG + " One.",
                     LONG + " Two.", LONG + " Three."])           # four paragraphs, the same under every verse
DIGEST = {
    "1": {"tafsir-al-tabari": WHOLE, "tafsir-al-qurtubi": LONG + " Qurtubi, first verse."},
    "2": {"tafsir-al-tabari": WHOLE, "tafsir-al-qurtubi": LONG + " Qurtubi, second verse."},
    "3": {"tafsir-al-tabari": WHOLE, "tafsir-al-qurtubi": LONG + " Qurtubi, third verse."},
}


def base_map(depth: str = "full", pointers: bool = True) -> str:
    """A valid map: the heading (¶1) is set aside; verses 1-3 and the introduction cite ¶3, ¶4, ¶2, ¶2."""
    q = {v: C.ayah_en(103, v) for v in (1, 2, 3)}
    P = (lambda n: "¶%d" % n) if pointers else (lambda n: "")
    text = "# Evidence map — test\n\n<!-- depth: %s. test -->\n\n" % depth
    text += "## Introduction\n\n### WHERE IT STANDS\n\n"
    text += "- `103:0.1` · lesson · Tabari says the sūrah gathers the whole way of life in three short verses. [tabari%s]\n\n" % P(2)
    text += "## Verse 103:1\n\n> %s\n\n**Sources with text:** tabari, qurtubi\n" % q[1]
    if pointers:
        text += "**Set aside:** tabari¶1 (heading)\n"
    text += "\n### THE FIRST THEME\n\n"
    text += "- `103:1.1` · language · Qurtubi gives the first meaning of the word and the ground it offers for it. [qurtubi%s, tabari%s]\n\n" % (P(1), P(3))
    text += "## Verse 103:2\n\n> %s\n\n**Sources with text:** tabari, qurtubi\n\n### THE SECOND THEME\n\n" % q[2]
    text += "- `103:2.1` · language · Qurtubi gives the second meaning of the word, with the reason that he states. [qurtubi%s, tabari%s]\n\n" % (P(1), P(4))
    text += "## Verse 103:3\n\n> %s\n\n**Sources with text:** tabari, qurtubi\n\n### THE THIRD THEME\n\n" % q[3]
    text += "- `103:3.1` · language · Qurtubi gives the third meaning of the word, with the reason that he states. [qurtubi%s, tabari%s]\n" % (P(1), P(2))
    return text


def run(text: str, digest=DIGEST):
    """``(problems, stats)`` of ``text`` checked as chapter 103 against ``digest``."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "103.md").write_text(text, encoding="utf-8")
        old_dir, old_digest = E.MAP_DIR, E._digest
        E.MAP_DIR, E._digest = Path(tmp), (lambda chapter: digest)
        try:
            return E.check_chapter(103)
        finally:
            E.MAP_DIR, E._digest = old_dir, old_digest


def has(problems, level, needle):
    return any(p[0] == level and needle in p[3] for p in problems)


def main() -> int:
    results = []

    def case(name, ok, detail=""):
        results.append(ok)
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("   — " + detail) if (detail and not ok) else ""))

    # the valid map
    problems, stats = run(base_map())
    errors = [p for p in problems if p[0] == "ERROR"]
    case("a valid full map passes", not errors, "; ".join(p[3] for p in errors))
    cov = stats["coverage"]
    case("coverage counts cited and set-aside paragraphs", cov["tabari"]["cited"] == 3 and cov["tabari"]["aside"] == 1
         and cov["tabari"]["missing"] == 0, repr(cov["tabari"]))

    # a pointer past the end of its passage
    problems, _ = run(base_map().replace("tabari¶4", "tabari¶9"))
    case("a pointer past the end of a passage is an error", has(problems, "ERROR", "only 4 paragraphs"))

    # an item with no pointer, in a full map
    problems, _ = run(base_map().replace("qurtubi¶1, tabari¶3", "qurtubi, tabari¶3"))
    case("a full map must cite paragraphs", has(problems, "ERROR", "cites paragraphs"))

    # a paragraph neither cited nor set aside (¶4 is cited only under verse 2)
    unaccounted = base_map().replace("[qurtubi¶1, tabari¶4]", "[qurtubi¶1]").replace(
        "**Sources with text:** tabari, qurtubi\n\n### THE SECOND", "**Sources with text:** tabari, qurtubi\n**Nothing further from:** tabari\n\n### THE SECOND")
    problems, _ = run(unaccounted)
    case("a paragraph left unaccounted is an error", has(problems, "ERROR", "not accounted for") and has(problems, "ERROR", "¶4"),
         repr([p[3] for p in problems if p[0] == "ERROR"]))

    # both cited and set aside (¶3 is cited under verse 1)
    problems, _ = run(base_map().replace("tabari¶1 (heading)", "tabari¶1 (heading), tabari¶3 (claimed twice)"))
    case("a paragraph both cited and set aside is warned", has(problems, "WARN", "both cited and set aside"))

    # no reason given
    problems, _ = run(base_map().replace("tabari¶1 (heading)", "tabari¶1"))
    case("a set-aside entry without a reason is warned", has(problems, "WARN", "without a reason"))

    # too much set aside: every paragraph of the whole-sūrah passage, and nothing of it cited
    heavy = base_map()
    for old, new in (("[qurtubi¶1, tabari¶2]", "[qurtubi¶1]"), ("[qurtubi¶1, tabari¶3]", "[qurtubi¶1]"),
                     ("[qurtubi¶1, tabari¶4]", "[qurtubi¶1]"), ("[tabari¶2]", "[qurtubi¶1]"),
                     ("tabari¶1 (heading)", "tabari¶1 (a), tabari¶2 (b), tabari¶3 (c), tabari¶4 (d)")):
        heavy = heavy.replace(old, new)
    heavy = heavy.replace("**Sources with text:** tabari, qurtubi\n", "**Sources with text:** tabari, qurtubi\n**Nothing further from:** tabari\n")
    problems, _ = run(heavy)
    case("setting most of the text aside is warned", has(problems, "WARN", "of the source text is set aside"),
         repr([(p[0], p[3][:70]) for p in problems]))

    # a survey map: warned, and not held to the paragraph rule
    problems, _ = run(base_map("survey", pointers=False))
    case("a survey map is warned as not the chosen depth", has(problems, "WARN", "not the chosen depth"))
    case("a survey map is not held to the paragraph rule", not has(problems, "ERROR", "not accounted for")
         and not has(problems, "ERROR", "cites paragraphs"), repr([p[3] for p in problems if p[0] == "ERROR"]))

    # a partly mapped chapter: counted, not enforced
    partial = base_map().split("## Verse 103:3")[0]
    problems, _ = run(partial)
    case("a partly mapped chapter reports gaps without failing", has(problems, "INFO", "not yet accounted for")
         and not has(problems, "ERROR", "not accounted for"), repr([(p[0], p[3][:60]) for p in problems]))

    # helpers
    case("expand_spec reads ranges and lists", E.expand_spec("3-5+9") == {3, 4, 5, 9} and E.expand_spec("7") == {7})
    case("expand_spec refuses what it cannot read", all(E.expand_spec(x) is None for x in ("0", "5-3", "a", "1-", "")))
    case("compress prints ranges", E.compress({1, 2, 3, 7, 9, 10}) == "¶1-3, ¶7, ¶9-10")
    case("short headings are exempt, real paragraphs are not", E.is_trivial("* *") and E.is_trivial("Ends here")
         and not E.is_trivial(LONG))

    failed = results.count(False)
    print("\n%d of %d cases pass%s" % (len(results) - failed, len(results), "" if not failed else " — %d FAILED" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
