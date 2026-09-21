#!/usr/bin/env python3
"""Render an Ibn Kathir hadith report as ONE clean sentence in house style.

CONSERVATIVE BY DESIGN. The source edition has no hadith numbers, so
attribution is by collection and narrator. Misattributing words to the
Prophet (s) is the worst failure mode here, so a report is accepted ONLY
when the prophetic-speech formula directly governs the quote and the quote
is clean. Everything ambiguous is rejected rather than guessed.
"""
import re, sys
sys.path.insert(0, "/home/user/quran-explained/scripts/editorial")
from ik_extract import reports

# The subject of "said" must be the Prophet, and the quote must follow at once.
PROPH_SAYS = re.compile(
    r"(?:the Messenger of Allah \u066a|the Messenger of God \u066a|the Prophet \u066a|"
    r"the Messenger of Allah|the Messenger of God|the Prophet)\s+"
    r"(?:\ufdfa\s*)?said\s*:\s*[\"\u201c]?(?P<say>.{30,340}?)[\"\u201d]?\s*(?:\.|,\s|\u201d|$)",
    re.I)

# Reject if the quote is a first-person witness account or carries a chain.
BAD_INSIDE = re.compile(
    r"\b(I saw|I said|we said|I asked|he told me|from Abu al-|from Nafi|the same as|"
    r"chain|narrated it|I bear witness|Ugh)\b", re.I)

NARR = re.compile(
    r"from (Ab[ūu] Hurayrah|Abu Hurayrah|\u02bf\u0100\u02bEishah|A'ishah|"
    r"Ibn \u02bfAbb\u0101s|Ibn Abbas|Anas ibn M\u0101lik|Anas bin Malik|"
    r"Ab[ūu] Sa\u02bf\u012bd|Abu Sa'id|J\u0101bir|Ubayy ibn Ka\u02bfb|"
    r"\u02bfUb\u0101dah ibn al-\u1e62\u0101mit|Ubadah ibn al-Samit|Ab[ūu] Dharr|"
    r"Ibn \u02bfUmar|Ibn Umar|\u02bfAl\u012b|\u02bfUmar|Mu\u02bf\u0101dh ibn Jabal|"
    r"Ab[ūu] M[ūu]s[āa]|Salm\u0101n|Bil\u0101l|Umm Salamah|Ab[ūu] Um\u0101mah|"
    r"\u02bfAbdull\u0101h ibn Mas\u02bf[ūu]d|Ibn Mas'ud|Zayd ibn Th\u0101bit|Ab[ūu] Bakr)",
    re.I)

def render(ch, v, max_len=430):
    for colls, frag in reports(ch, v):
        m = PROPH_SAYS.search(frag)
        if not m:
            continue
        say = re.sub(r"\s+", " ", m.group("say")).strip().strip('.,"\u201d')
        if not (30 <= len(say) <= 300):
            continue
        if BAD_INSIDE.search(say):
            continue
        if say.count('"') or say.count('\u201c') or say.count('\u201d'):
            continue                      # nested quote -> boundary unsafe
        narr = NARR.search(frag[:m.start()+40])
        coll = " and ".join(colls[:2])
        who = f", narrated by {narr.group(1)}," if narr else ""
        out = re.sub(r"\s+", " ",
            f"Ibn Kathir records{who} that the Prophet \u066a said: "
            f"\u201c{say}\u201d (reported by {coll}).").strip()
        if len(out) <= max_len:
            return out, colls, (narr.group(1) if narr else None)
    return None, None, None

if __name__ == "__main__":
    for a in sys.argv[1:]:
        ch, v = map(int, a.split(":"))
        s, c, n = render(ch, v)
        print(f"--- {ch}:{v}")
        print(f"    {s}\n" if s else "    (rejected - no clean prophetic saying)")
