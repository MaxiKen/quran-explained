#!/usr/bin/env python3
"""Show, for one chapter, the commentary sections that lack external evidence
next to what Ibn Kathir offers for the same verse.

Usage: python3 scripts/editorial/ik_review.py CH [LIMIT]

This is a READING aid, not a generator. Insertion is done by hand; automated
placement was tried four times and produced unusable or misattributed prose.
"""
import re, sys, json, pathlib

ROOT = pathlib.Path("/home/user/quran-explained")
IDX = json.load(open("/tmp/ik_idx.json"))
ARABIC = re.compile(r"[\u0600-\u06ff]+")
# NON-Qur'an evidence only. Qur'an cross-references do not count: after the
# quoting pass almost every section has one, so filtering on them finds nothing.
EVID = re.compile(
    r"(Bukh[āa]r[īi]|Muslim|Tirmidh[īi]|Nas[āa]ʾ[īi]|Ab[ūu]\s+D[āa]w[ūu]d|"
    r"Ibn\s+M[āa]jah|Musnad|Aḥmad|Ḥ[āa]kim|Ibn Kathir|"
    r"Ibn ʿAbb[āa]s|Ibn Masʿ[ūu]d|aṭ-Ṭabar[īi]|At-Tabari|ar-R[āa]z[īi]|"
    r"al-Qurṭub[īi]|Ibn Taymiyyah|al-Ḥasan al-Baṣr[īi]|Muj[āa]hid|Qat[āa]dah|"
    r"as-Sudd[īi]|aḍ-Ḍaḥḥ[āa]k|Ikrimah|"
    r"occasion of revelation|revealed (?:when|about|concerning|after))", re.I)

def clean(t):
    t = ARABIC.sub(" ", t)
    t = re.sub(r"\(\s*\)", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def main():
    ch = int(sys.argv[1]); limit = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    md = (ROOT / "markdown commentry" / f"{ch:03d}.md").read_text(encoding="utf-8")
    shown = 0
    for sec in re.split(r"\n(?=## )", md):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", sec.split("\n")[0].strip())
        if not m:
            continue
        v = int(m.group(2))
        lines = sec.split("\n")[1:]
        i = 0
        while i < len(lines) and (lines[i].startswith(">") or not lines[i].strip()):
            i += 1
        body = "\n".join(lines[i:])
        if EVID.search(body):
            continue                        # already has evidence
        ik = clean(IDX.get(str(ch), {}).get(str(v), ""))
        if not ik:
            continue
        shown += 1
        print("=" * 78)
        print(f"### {ch}:{v}   (commentary {len(body.split())} words, no evidence)")
        print("-" * 78)
        print("IBN KATHIR:", ik[:1400])
        print()
        if shown >= limit:
            break
    print(f"[shown {shown} evidence-free sections for ch {ch}]")

main()
