#!/usr/bin/env python3
"""Render ONE Ibn Kathir report as a clean sentence in house style.

CONSERVATIVE BY DESIGN. Misattributing words to the Prophet (s) is the worst
failure available here, so a report is accepted only when the prophetic-speech
formula directly governs the quote and the quote is clean. This edition has no
hadith numbers, so attribution is by collection and narrator only -- a number is
never invented.

Arabic is stripped before matching: Ibn Kathir interleaves Arabic with its
English gloss, and requiring Arabic-free input discarded ~99% of usable reports.
"""
import re, sys
sys.path.insert(0, "/home/user/quran-explained/scripts/editorial")
from ik_extract import reports

ARABIC = re.compile(r"[\u0600-\u06ff]+")

def strip_ar(t):
    t = ARABIC.sub(" ", t)
    t = re.sub(r"\(\s*\)", " ", t)
    return re.sub(r"\s+", " ", t).strip()

PROPH = re.compile(
    r"(?:the Messenger of Allah|Allah's Messenger|the Messenger of God|"
    r"the Prophet)\s*ﷺ?\s*said\s*[,:]\s*[\"“']?(?P<say>.{30,340}?)[\"”']?\s*(?:\.\s|$)")

# Reject quotes that are witness accounts, rulings or commentary rather than the
# Prophet's own words.
BAD = re.compile(
    r"\b(I saw|I said|we said|I asked|he told me|I bear witness|the same as|"
    r"chain|narrated it|means|meaning|this Ayah|His statement|explains|"
    r"Ugh|liar)\b", re.I)

NARR = re.compile(
    r"\b(?:that|from)\s+(Abu Hurayrah|A'ishah|Ibn 'Abbas|Anas bin Malik|Anas|"
    r"Abu Sa'id Al-Khudri|Abu Sa'id|Jabir|Ubayy bin Ka'b|Ubadah bin As-Samit|"
    r"Abu Dharr|Ibn 'Umar|Ibn Umar|'Ali|'Umar|Mu'adh bin Jabal|Abu Musa|"
    r"Salman|Bilal|Umm Salamah|Abu Umamah|Abdullah bin Mas'ud|Ibn Mas'ud|"
    r"Zayd bin Thabit|Abu Bakr|Abdullah bin 'Amr|Abu Ad-Darda|Thawban)\b")

def render(ch, v, max_len=420):
    for colls, frag in reports(ch, v):
        e = strip_ar(frag)
        m = PROPH.search(e)
        if not m:
            continue
        say = m.group("say").strip().strip('.",\'”“')
        if not (30 <= len(say) <= 280):
            continue
        if BAD.search(say):
            continue
        if any(q in say for q in '"“”'):
            continue                      # nested quote -> unsafe boundary
        narr = NARR.search(e[:m.start()+40])
        coll = " and ".join(colls[:2])
        who = f", narrated by {narr.group(1)}," if narr else ""
        out = re.sub(r"\s+", " ",
            f"Ibn Kathir records{who} that the Prophet ﷺ said: “{say}” "
            f"(reported by {coll}).").strip()
        if len(out) <= max_len:
            return out, colls, (narr.group(1) if narr else None)
    return None, None, None

if __name__ == "__main__":
    for a in sys.argv[1:]:
        ch, v = map(int, a.split(":"))
        s, c, n = render(ch, v)
        print(f"--- {ch}:{v}")
        print(f"    {s}\n" if s else "    (rejected — no clean prophetic saying)")
