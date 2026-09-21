#!/usr/bin/env python3
"""Extract hadith evidence for one verse from the committed Ibn Kathir source.

Reads ONLY tafsir-ibn-kathir/ (the cleaned spa5k/tafsir_api records committed in
9faa9ee). This edition cites hadith by collection and narrator and carries no
hadith numbers, so nothing here may invent one.
"""
import re, json, pathlib

IDX_PATH = pathlib.Path("/tmp/ik_idx.json")
_idx = None

COLL = (r"(?:Sahih\s+)?(?:Al-|al-)?(Bukhari|Muslim|Tirmidhi|Nasa'i|Abu Dawud|"
        r"Ibn Majah|Ahmad|Hakim|Bayhaqi|Tabarani|Ibn Hibban|Ibn Khuzaymah|"
        r"Malik|Abu Yala|Abd bin Humayd|Ibn Abi Hatim|Ibn Jarir|Fath Al-Bari)")
COLL_RE = re.compile(COLL)
SAID_RE = re.compile(
    r"(the Messenger of Allah\s*ﷺ?\s*said|the Messenger of God\s*ﷺ?\s*said|"
    r"the Prophet\s*ﷺ?\s*said|Allah's Messenger\s*ﷺ?\s*said|he said)", re.I)

CANON = {"Bukhari":"al-Bukhari","Muslim":"Muslim","Tirmidhi":"al-Tirmidhi",
 "Nasa'i":"al-Nasa'i","Abu Dawud":"Abu Dawud","Ibn Majah":"Ibn Majah",
 "Ahmad":"Imam Ahmad","Hakim":"al-Hakim","Bayhaqi":"al-Bayhaqi",
 "Tabarani":"al-Tabarani","Ibn Hibban":"Ibn Hibban","Ibn Khuzaymah":"Ibn Khuzaymah",
 "Malik":"Malik","Abu Yala":"Abu Ya'la","Abd bin Humayd":"'Abd bin Humayd",
 "Ibn Abi Hatim":"Ibn Abi Hatim","Ibn Jarir":"Ibn Jarir","Fath Al-Bari":"Fath al-Bari"}

def idx():
    global _idx
    if _idx is None:
        _idx = json.load(open(IDX_PATH))
    return _idx

def text(ch, v):
    return idx().get(str(ch), {}).get(str(v))

def reports(ch, v):
    """[(collections, sentence), ...] for verse ch:v."""
    t = text(ch, v)
    if not t:
        return []
    out = []
    for m in COLL_RE.finditer(t):
        win = t[max(0, m.start()-300):m.end()+600]
        if not SAID_RE.search(win):
            continue
        s = t.rfind(". ", max(0, m.start()-420), m.start())
        e = t.find(". ", m.end())
        frag = t[s+2 if s > 0 else max(0, m.start()-220): e+1 if e > 0 else m.end()+420]
        frag = re.sub(r"\s+", " ", frag).strip()
        if not (60 <= len(frag) <= 700):
            continue
        colls = sorted({CANON.get(c, c) for c in COLL_RE.findall(frag)})
        if colls:
            out.append((colls, frag))
    seen, uniq = set(), []
    for c, f in out:
        k = f[:80]
        if k not in seen:
            seen.add(k); uniq.append((c, f))
    uniq.sort(key=lambda x: -len(x[1]))
    return uniq

if __name__ == "__main__":
    import sys
    ch, v = map(int, sys.argv[1].split(":"))
    r = reports(ch, v)
    print(f"### {ch}:{v} -> {len(r)} report(s)")
    for c, f in r[:3]:
        print(f"  [{'; '.join(c)}]\n  {f[:420]}\n")
