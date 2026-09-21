#!/usr/bin/env python3
"""Extract hadith evidence for one verse from the offline Ibn Kathir corpus.

Source: SafhaJournal/tafsir-ibn-kathir-english (CC BY 4.0), verse-aligned,
6,236 records, 96.9% verified to quote their own verse. The English is an AI
translation of the public-domain Arabic, so citations are given by collection
and narrator chain -- never by number, because this edition has no numbers.
"""
import re, json, sys

IK = json.load(open("/home/user/ik_src/ik_by_verse.json"))
BAD = {tuple(x) for x in json.load(open("/tmp/ik_badrecs.json"))}

COLL = r"(?:\u1e62a\u1e25\u012b\u1e25\s+)?(?:al-)?(Bukh\u0101r\u012b|Bukhari|Muslim|Tirmidh\u012b|Tirmidhi|Nas\u0101'\u012b|Nasa'i|Ab\u016b\s+D\u0101w\u016bd|Abu Dawud|Ibn\s+M\u0101jah|Ibn Majah|A\u1e25mad|Ahmad|\u1e24\u0101kim|Hakim|Bayhaq\u012b|Bayhaqi|\u1e6cabar\u0101n\u012b|Tabarani|Ibn\s+\u1e24ibb\u0101n|Ibn Hibban|Ibn\s+Khuzaymah|M\u0101lik|Malik|Ab\u016b\s+Ya\u02bfl\u0101|Abu Yala)"
SAID = re.compile(r"(the Messenger of Allah \u066a said|the Prophet \u066a said|the Messenger of God \u066a said|he said:|said:)", re.I)


def norm_coll(c):
    c = c.strip()
    table = {"Bukhari": "al-Bukh\u0101r\u012b", "Tirmidhi": "al-Tirmidh\u012b",
             "Nasa'i": "al-Nas\u0101'\u012b", "Abu Dawud": "Ab\u016b D\u0101w\u016bd",
             "Ibn Majah": "Ibn M\u0101jah", "Ahmad": "Imam A\u1e25mad",
             "Hakim": "al-\u1e24\u0101kim", "Bayhaqi": "al-Bayhaq\u012b",
             "Tabarani": "al-\u1e6cabar\u0101n\u012b", "Ibn Hibban": "Ibn \u1e24ibb\u0101n",
             "Malik": "M\u0101lik", "Abu Yala": "Ab\u016b Ya\u02bfl\u0101"}
    return table.get(c, c)


def reports(ch, v):
    """Return list of (collections, clean_sentence) for verse ch:v."""
    recs = IK.get(str(ch), {}).get(str(v))
    if not recs:
        return []
    a, b, txt = recs[0]
    if (ch, a, b) in BAD:          # alignment not verified -> refuse
        return []
    out = []
    for m in re.finditer(COLL, txt):
        if not SAID.search(txt[max(0, m.start()-260):m.end()+560]):
            continue
        # sentence containing the attribution
        s = txt.rfind(". ", max(0, m.start()-400), m.start())
        e = txt.find(". ", m.end())
        frag = txt[s+2 if s > 0 else max(0, m.start()-200): e+1 if e > 0 else m.end()+400]
        frag = re.sub(r"\s+", " ", frag).strip()
        if not (60 <= len(frag) <= 620):
            continue
        colls = sorted({norm_coll(x) for x in re.findall(COLL, frag)})
        if not colls:
            continue
        out.append((colls, frag))
    # de-dup, prefer longer informative reports
    seen, uniq = set(), []
    for c, f in out:
        k = f[:70]
        if k in seen:
            continue
        seen.add(k); uniq.append((c, f))
    uniq.sort(key=lambda x: -len(x[1]))
    return uniq


if __name__ == "__main__":
    ch, v = int(sys.argv[1]), int(sys.argv[2])
    r = reports(ch, v)
    print(f"### {ch}:{v} -> {len(r)} report(s)")
    for colls, frag in r[:4]:
        print(f"  [{'; '.join(colls)}]")
        print(f"  {frag[:500]}\n")
