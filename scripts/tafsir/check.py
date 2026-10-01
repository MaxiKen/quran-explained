#!/usr/bin/env python3
"""Check a chapter file before it is published.

    python3 scripts/tafsir/check.py 112
    python3 scripts/tafsir/check.py --all

What is proved here is form, traceability and honesty of the quoting — not
doctrine. The checks, in order:

* the file exists and has the chapter title;
* the introduction is present, non-empty and of a sane length;
* every verse of the chapter appears once, in order, each with the canonical
  ``> ayah_en`` line, byte-identical to ``data/chapter_NNN.js`` after
  whitespace normalisation;
* every quoted Qur'an clause in a cross-reference really is the wording of the
  verse it cites (``(C:V — **"clause"**)``);
* cross-references point at real verses, and are expanded rather than bare;
* headings are ``**UPPERCASE**`` on their own line; hygiene (tabs, trailing
  spaces, double blank lines, file ending) is clean;
* every work of the corpus is accounted for, either cited in the pack or
  recorded as carrying nothing (``--sources``).

Exit code 1 if anything FAILs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

REF = re.compile(r"\((\d+):(\d+)\s+—\s+\*\*[“\"](.+?)[”\"]\*\*\)")
BARE = re.compile(r"\((\d+):(\d+)\)")
HEADING = re.compile(r"^\*\*([A-Z][A-Z0-9 ,'’\-:&/]+)\*\*$", re.M)
PHRASE = re.compile(r"\*\*\*[“\"](.+?)[”\"]\*\*\*")
HADITH = re.compile(
    r"(al-Bukhārī|Bukhārī|Muslim|al-Tirmidhī|Tirmidhī|Abū Dāwūd|Abu Dawud|al-Nasāʾī|Nasāʾī|Ibn Mājah|Aḥmad|Ahmad|al-Ṭabarānī|Ṭabarānī|al-Ḥākim|Ḥākim|Mālik|al-Dārimī|ʿAbd al-Razzāq)"
)
# a named Companion, Successor or first imam satisfies the evidence floor
# together with a collection; either one is enough (EVD-TAFSIR in the rules)
AUTHORITY = re.compile(
    r"(Ibn ʿAbbās|Ibn Masʿūd|Ibn ʿUmar|Ibn Isḥāq|Ibn Jarīr|Ibn Abī Ḥātim|Ibn Zayd|Ibn Jubayr|Ibn al-Ḥanafiyya|Ibn ʿĀmir|"
    r"Mujāhid|Qatādah|al-Ḥasan|ʿIkrima|al-Ḍaḥḥāk|al-Suddī|Abū al-ʿĀliyah|Abū Mālik|al-Rabīʿ|Saʿīd ibn Jubayr|"
    r"Muqātil|ʿAṭāʾ|ʿAlī ibn Abī|ʿUmar|Abū Bakr|ʿUthmān|Abū Hurayrah|ʿĀʾishah|Anas|Ubayy|al-Kalbī|al-Shaʿbī|"
    r"al-Nawwās|Zayd ibn Aslam|ʿAbd Allāh ibn|Abū Umāmah|Abū Saʿīd|Usayd|al-Nuʿmān|Shurayḥ|Masrūq|ʿAlqama|al-Aswad)"
)


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.fails = 0
        self.warns = 0

    def ok(self, msg: str) -> None:
        self.lines.append(f"  ok    {msg}")

    def warn(self, msg: str) -> None:
        self.warns += 1
        self.lines.append(f"  WARN  {msg}")

    def fail(self, msg: str) -> None:
        self.fails += 1
        self.lines.append(f"  FAIL  {msg}")

    def text(self) -> str:
        return "\n".join(self.lines)


def check(n: int, report: Report, sources: bool = False) -> None:
    path = C.ROOT / "tafsir" / f"{C.pad3(n)}.md"
    meta = C.meta(n)
    report.lines.append(f"\n=== Sūrah {n} {meta['name_en']} ({meta['verses']} verses) — {path.name} ===")
    if not path.exists():
        report.fail(f"tafsir/{C.pad3(n)}.md does not exist")
        return
    raw = path.read_text(encoding="utf-8")
    total = C.verse_count(n)

    # ---- hygiene
    if "\t" in raw:
        report.fail("tab character(s) in the file")
    if re.search(r"[ \t]+$", raw, re.M):
        report.fail("trailing whitespace")
    if "\n\n\n" in raw:
        report.fail("more than one blank line in a row")
    if not raw.endswith("\n") or raw.endswith("\n\n"):
        report.fail("file must end with exactly one newline")

    # ---- title + introduction
    title = re.search(r"^#\s+(.+)$", raw, re.M)
    if not title:
        report.fail("no '# …' title line")
    elif f"(Chapter {n})" not in title.group(1):
        report.warn(f"title does not carry '(Chapter {n})': {title.group(1)!r}")
    else:
        report.ok(f"title: {title.group(1)}")

    m = re.search(r"^##\s+Introduction to the Sūrah\s*$", raw, re.M)
    if not m:
        report.fail("no '## Introduction to the Sūrah' heading")
        intro = ""
    else:
        nxt = re.search(r"^##\s", raw[m.end() :], re.M)
        intro = raw[m.end() : m.end() + (nxt.start() if nxt else len(raw))].strip(" -\n")
    iw = len(C.words(intro))
    if iw < 120:
        report.fail(f"introduction is {iw} words (too short to set the chapter up)")
    elif iw > 2500:
        report.warn(f"introduction is {iw} words (long for a chapter opening)")
    else:
        report.ok(f"introduction {iw} words")

    # ---- verses
    marks = list(re.finditer(r"^##\s+Verse\s+(\d+):(\d+)\s*$", raw, re.M))
    if not marks:
        report.fail("no '## Verse N:V' sections")
        return
    numbers = [int(mm.group(2)) for mm in marks]
    if numbers != list(range(1, total + 1)):
        missing = sorted(set(range(1, total + 1)) - set(numbers))
        extra = sorted(set(numbers) - set(range(1, total + 1)))
        report.fail(f"verse sections are {numbers[:8]}{'…' if len(numbers) > 8 else ''}; missing={missing[:8]} extra={extra[:8]}")
    else:
        report.ok(f"all {total} verses present, in order")

    bodies: dict[int, str] = {}
    for i, mm in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        chunk = raw[mm.end() : end]
        chunk = re.sub(r"^\s*---\s*$", "", chunk, flags=re.M)
        bodies[int(mm.group(2))] = chunk.strip()

    for v in sorted(bodies):
        body = bodies[v]
        tag = f"{n}:{v}"
        want = C.normalise(f"> {C.ayah_en(n, v)}")
        got_lines = [ln for ln in body.splitlines() if ln.strip().startswith(">")]
        if not got_lines:
            report.fail(f"{tag}: no '> …' verse line")
        elif C.normalise(" ".join(got_lines)) != want:
            report.fail(f"{tag}: verse line is not the app's wording of {tag}")
        if len(got_lines) > 1:
            report.fail(f"{tag}: {len(got_lines)} quote lines (must be exactly one)")
        if "TODO" in body or "TBD" in body:
            report.fail(f"{tag}: contains TODO/TBD")
        wc = len(C.words(body))
        if wc < 80:
            report.warn(f"{tag}: only {wc} words")
        heads = HEADING.findall(body)
        if not heads:
            report.warn(f"{tag}: no '**UPPERCASE HEADING**'")
        for line in body.splitlines():
            if line.strip().startswith("**") and line.strip().endswith("**") and line.strip() not in ("**",):
                inner = line.strip()[2:-2]
                if inner and inner == inner.lower() and not inner.startswith("http"):
                    report.warn(f"{tag}: heading not uppercase: {inner[:50]!r}")
        # cross-references
        refs = REF.findall(body)
        bare = [b for b in BARE.findall(body) if not re.search(r"\(%s\s+—" % b[0] + r"", body)]
        for c, vv, clause in refs:
            c, vv = int(c), int(vv)
            if not (1 <= c <= 114 and 1 <= vv <= C.meta(c)["verses"]):
                report.fail(f"{tag}: cross-reference {c}:{vv} is not a real verse")
                continue
            target = C.normalise(C.ayah_en(c, vv))
            parts = [C.normalise(p) for p in re.split(r"[…]|\.\.\.", clause) if C.normalise(p)]
            if not all(p in target for p in parts):
                report.fail(f"{tag}: clause for {c}:{vv} is not the app's wording: “{clause[:60]}”")
        if bare:
            report.warn(f"{tag}: {len(bare)} bare cross-reference(s): {', '.join(f'{a}:{b}' for a, b in bare[:4])}")
        if not refs and not bare:
            report.warn(f"{tag}: no cross-reference")
        if not HADITH.search(body) and not AUTHORITY.search(body):
            report.warn(f"{tag}: no named collection and no named early authority")
    if all(not HEADING.findall(b) for b in bodies.values()):
        report.fail("no headings anywhere in the chapter")

    if sources:
        pack = C.ROOT / "tmp" / "evidence" / f"{C.pad3(n)}.md"
        if not pack.exists():
            report.warn(f"no evidence pack at {pack.relative_to(C.ROOT)} (run scripts/tafsir/evidence.py {n})")
        else:
            text = pack.read_text(encoding="utf-8")
            for key in C.ORDER:
                has = key in text
                if not has and "**nothing for this chapter**" not in text.split(key)[0][-200:]:
                    report.warn(f"work '{key}' absent from the evidence pack")

    words = sum(len(C.words(b)) for b in bodies.values()) + iw
    report.ok(f"prose {words:,} words (intro {iw}, verse sections {words - iw:,})")
    for a, b in ((1, 30), (31, 60), (61, 90), (91, 114)):
        pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", nargs="?", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--sources", action="store_true", help="also account for the corpus")
    args = ap.parse_args(argv)
    numbers = (
        [ch["number"] for ch in C.chapters() if (C.ROOT / "tafsir" / f"{C.pad3(ch['number'])}.md").exists()]
        if args.all
        else [args.chapter]
    )
    if numbers == [None]:
        ap.error("give a chapter number or --all")
    report = Report()
    for n in numbers:
        check(n, report, args.sources)
    print(report.text())
    print(f"\nRESULT: {'PASS' if report.fails == 0 else 'FAIL'} — {report.fails} fail, {report.warns} warn")
    return 1 if report.fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
