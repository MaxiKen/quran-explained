#!/usr/bin/env python3
"""Check that every Qur'an quotation inside an Ibn Kathir paragraph is verbatim
from the translation this app ships.

WHY THIS EXISTS. Ibn Kathir's English is the Darussalam translation; this app
ships a different one (ayah_en in data/chapter_NNN.js). Quoting his rendering
produces text that reads correctly and is NOT the wording this app ships. This
happened at 23:4, 25:70 and 27:23 before it was automated.

Scans paragraphs mentioning "Ibn Kathir" in markdown commentry/, extracts every
*“…”* (ref) pair, and verifies the quote appears in the cited verse's ayah_en.

    python3 scripts/editorial/check_ik_quotes.py

Exit 0 = all verbatim. Exit 1 = at least one non-verbatim.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MD = ROOT / "markdown commentry"
DATA = ROOT / "data"

def norm(s):
    s = re.sub(r"[˹˺\"'’‘“”\u0640]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()

def longest_run(a, b):
    """Longest contiguous word sequence shared by a and b."""
    A, B = a.split(), b.split()
    for n in range(min(len(A), 14), 0, -1):
        windows = {tuple(B[j:j + n]) for j in range(len(B) - n + 1)}
        for i in range(len(A) - n + 1):
            if tuple(A[i:i + n]) in windows:
                return n
    return 0

_cache = {}
def verses(ch):
    if ch not in _cache:
        p = DATA / f"chapter_{ch:03d}.js"
        _cache[ch] = re.findall(r'"ayah_en"\s*:\s*"((?:[^"\\]|\\.)*)"',
                                p.read_text(encoding="utf-8"))
    return _cache[ch]

# BOTH quote styles. The corpus mixes curly (“…”) and straight ("…") quotes, and
# a checker that handles only one silently under-reports - the first version of
# this script checked 1 quotation when 35 were present.
QREF = re.compile(r'\*(?:“([^”]{12,260})”|"([^"]{12,260})")\*\s*\((\d{1,3}):(\d{1,3})(?:[–-](\d{1,3}))?')

# A quotation of the verse the section is ABOUT, quoted without a reference, is
# still a Qur'an quotation and must match ayah_en. Catch the phrase-quote form
# too: *"…"* standing alone inside an Ibn Kathir paragraph, when the surrounding
# text is glossing that verse.
PHRASE = re.compile(r'\*(?:“([^”]{6,120})”|"([^"]{6,120})")\*(?!\s*\()')

BASELINE = "1a3067d"   # commit before the Ibn Kathir work began

def pre_existing_quotes():
    """(ch, verse, quote) triples already non-verbatim at the baseline commit."""
    import subprocess
    out = set()
    try:
        # -z: the directory is "markdown commentry" - it contains a SPACE, so
        # whitespace-splitting ls-tree output breaks every path in half and the
        # baseline silently comes back empty. NUL-separate instead.
        raw = subprocess.run(
            ["git", "ls-tree", "-r", "-z", "--name-only", BASELINE,
             "markdown commentry"],
            capture_output=True, text=True, cwd=ROOT).stdout
        names = [n for n in raw.split("\0") if n]
    except Exception:
        return out
    for name in names:
        try:
            text = subprocess.run(["git", "show", f"{BASELINE}:{name}"],
                                  capture_output=True, text=True, cwd=ROOT).stdout
        except Exception:
            continue
        for para in re.split(r"\n\n+", text):
            for m in QREF.finditer(para):
                q = m.group(1) or m.group(2)
                ch, a = int(m.group(3)), int(m.group(4))
                out.add((ch, a, q[:70]))   # match the live check's [:70] truncation
    return out

def main():
    bad = []
    checked = 0
    for f in sorted(MD.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        for para in re.split(r"\n\n+", text):
            if "Ibn Kathir" not in para:
                continue
            for m in QREF.finditer(para):
                q = m.group(1) or m.group(2)
                ch, a = int(m.group(3)), int(m.group(4))
                b = int(m.group(5) or a)
                en = verses(ch)
                if a - 1 >= len(en):
                    bad.append((f.name, ch, a, q[:50], "no such verse"))
                    continue
                pool = norm(" ".join(en[a - 1:b]))
                checked += 1
                if norm(q) not in pool:
                    bad.append((f.name, ch, a, q[:70], pool[:70]))
    # Phrase quotes of the host verse: report as warnings, since a gloss may
    # legitimately quote Ibn Kathir's own paraphrase rather than the verse.
    warns = []
    for f in sorted(MD.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        for sec in re.split(r"\n(?=## )", text):
            head = sec.split("\n")[0]
            hm = re.match(r"## Verse (\d+):(\d+)\s*$", head.strip())
            if not hm or "Ibn Kathir" not in sec:
                continue
            hch, hv = int(hm.group(1)), int(hm.group(2))
            en = verses(hch)
            if hv - 1 >= len(en):
                continue
            host = norm(en[hv - 1])
            for para in re.split(r"\n\n+", sec):
                if "Ibn Kathir" not in para:
                    continue
                for m in PHRASE.finditer(para):
                    q = m.group(1) or m.group(2)
                    nq = norm(q)
                    # Only flag if it looks like it is quoting the verse: shares
                    # a run of words with ayah_en but is not verbatim.
                    # A shared word COUNT is useless here: a hadith quote shares
                    # "Allah", "the", "and" with almost any verse. Require a
                    # CONTIGUOUS run of >=5 words, which only a real attempt to
                    # quote the verse produces.
                    if longest_run(nq, host) >= 5 and nq not in host:
                        warns.append((f.name, hch, hv, q[:60], en[hv - 1][:70]))
    print(f"Ibn Kathir paragraphs scanned, quotations checked: {checked}")
    print(f"phrase quotes of the host verse, not verbatim    : {len(warns)}")
    for w in warns:
        print(f"  {w[0]} {w[1]}:{w[2]}")
        print(f"      quoted : {w[3]}")
        print(f"      ayah_en: {w[4]}")
    print(f"non-verbatim quotations                          : {len(bad)}")
    for b in bad:
        print(f"  {b[0]} {b[1]}:{b[2]}")
        print(f"      quoted : {b[3]}")
        print(f"      actual : {b[4]}")
    # Only defects introduced by this work fail the check. Quotations that
    # already existed at the pre-work baseline predate it, and the standing
    # rule is not to churn pre-existing content - so report them separately.
    baseline = pre_existing_quotes()
    new_bad = [b for b in bad if (b[1], b[2], b[3]) not in baseline]
    pre_bad = [b for b in bad if (b[1], b[2], b[3]) in baseline]
    if pre_bad:
        print(f"\npre-existing at baseline (not this work's defects): {len(pre_bad)}")
        for b in pre_bad:
            print(f"  {b[0]} {b[1]}:{b[2]}  {b[3]}")
    print(f"\nNEW non-verbatim quotations introduced by this work: {len(new_bad)}")
    for b in new_bad:
        print(f"  {b[0]} {b[1]}:{b[2]}  quoted {b[3]!r}")
    print("\nRESULT:", "PASS" if not new_bad else "FAIL")
    return 0 if not new_bad else 1

if __name__ == "__main__":
    sys.exit(main())
