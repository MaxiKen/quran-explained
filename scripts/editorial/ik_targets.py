#!/usr/bin/env python3
"""Rank the best Ibn Kathir insertion targets for a chapter.

Pairs each evidence-free commentary section with the Ibn Kathir record for the
same verse and scores it by how much *citable* material it contains - named
collections, named transmitters, and revelation-history markers. This is a
reading aid: insertion stays hand-written.

Usage: python3 scripts/editorial/ik_targets.py CH [N]
"""
import re, sys, json, pathlib

ROOT = pathlib.Path("/home/user/quran-explained")
IDX = json.load(open("/tmp/ik_idx.json"))
ARABIC = re.compile(r"[\u0600-\u06ff]+")

NONQ = re.compile(
    r"(Bukh[āa]r[īi]|Muslim|Tirmidh[īi]|Nas[āa]ʾ[īi]|Ab[ūu]\s+D[āa]w[ūu]d|"
    r"Ibn\s+M[āa]jah|Musnad|Aḥmad|Ḥ[āa]kim|Ibn Kathir|"
    r"Ibn ʿAbb[āa]s|Ibn Masʿ[ūu]d|aṭ-Ṭabar[īi]|At-Tabari|ar-R[āa]z[īi]|"
    r"al-Qurṭub[īi]|Ibn Taymiyyah|al-Ḥasan al-Baṣr[īi]|Muj[āa]hid|Qat[āa]dah|"
    r"as-Sudd[īi]|aḍ-Ḍaḥḥ[āa]k|Ikrimah|"
    r"occasion of revelation|revealed (?:when|about|concerning|after))", re.I)

COLL = re.compile(r"(Al-Bukhari|Muslim|At-Tirmidhi|An-Nasa'i|Abu Dawud|"
                  r"Ibn Majah|Imam Ahmad|Al-Hakim|Ibn Hibban|Ibn Khuzaymah|"
                  r"Abu Ya'la|Ad-Darimi|Ibn Marduwyah|Ibn Jarir)\b")
REC = re.compile(r"recorded|reported|narrated|transmits|said that", re.I)
ASBAB = re.compile(r"(revealed (?:when|about|concerning|after|in|on)|"
                   r"reason behind revealing|was revealed|occasion)", re.I)
SAY = re.compile(r"(the Messenger of Allah|Allah's Messenger|the Prophet)\s*ﷺ?\s*said", re.I)

def clean(t):
    return re.sub(r"\s+", " ", ARABIC.sub(" ", t)).strip()

def main():
    ch = int(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    md = (ROOT / "markdown commentry" / f"{ch:03d}.md").read_text(encoding="utf-8")
    rows = []
    for sec in re.split(r"\n(?=## )", md):
        m = re.match(r"## Verse (\d+):(\d+)\s*$", sec.split("\n")[0].strip())
        if not m: continue
        v = int(m.group(2))
        lines = sec.split("\n")[1:]
        i = 0
        while i < len(lines) and (lines[i].startswith(">") or not lines[i].strip()): i += 1
        body = "\n".join(lines[i:])
        if NONQ.search(body): continue                 # already has evidence
        ik = IDX.get(str(ch), {}).get(str(v))
        if not ik: continue
        e = clean(ik)
        score = (len(COLL.findall(e)) * 3
                 + len(REC.findall(e))
                 + len(ASBAB.findall(e)) * 4
                 + len(SAY.findall(e)) * 2)
        if score:
            rows.append((score, v, len(e), len(COLL.findall(e)),
                         bool(ASBAB.search(e)), bool(SAY.search(e))))
    rows.sort(reverse=True)
    print(f"ch {ch}: {len(rows)} evidence-free sections with citable Ibn Kathir material\n")
    print(f"{'score':>5} {'verse':>6} {'chars':>7} {'coll':>4}  asbab  prophetic")
    for s, v, ln, c, a, p in rows[:n]:
        print(f"{s:>5} {ch}:{v:<4} {ln:>7} {c:>4}  {'yes' if a else '  -'}    {'yes' if p else '  -'}")

main()
