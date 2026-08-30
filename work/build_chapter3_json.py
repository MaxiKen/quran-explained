#!/usr/bin/env python3
"""Build chapter_3_translation.json from work/chapter3_raw.txt (user-supplied text).

Strips the edition's section headings and [n] footnote markers, keeping the
translation text (including ˹...˺ brackets) verbatim.
"""
import json, re, sys

RAW = "work/chapter3_raw.txt"
OUT = "chapter_3_translation.json"

HEADINGS = [
    "Allah Almighty",
    "Precise and Elusive Verses",
    "Punishment of the Disbelievers",
    "Allah’s Help at the Battle of Badr",
    "Temporary Pleasures",
    "Everlasting Delight",
    "One God",
    "One Way",
    "Reward of the Rebellious",
    "Rejecting Allah’s Judgment",
    "Allah’s Infinite Power",
    "Taking Disbelievers as Guardians",
    "Allah’s Infinite Knowledge",
    "Accountability for Good and Evil",
    "Obeying Allah and His Messenger",
    "Blessed People",
    "Birth of Mary",
    "Birth of John the Baptist",
    "Mary Chosen over All Women",
    "Birth of Jesus Christ",
    "The Mission and Miracles of Jesus",
    "The Disciples",
    "Conspiracy Against Jesus",
    "Fair Reward",
    "Jesus and Adam",
    "Disputes over Jesus",
    "Devotion to Allah Alone",
    "The Truth About Abraham",
    "Distorting the Truth",
    "Deception Exposed",
    "Honouring Trusts",
    "Breaking Allah’s Covenant",
    "Distorting the Scripture",
    "Prophets Never Claim Divinity",
    "Allah’s Covenant with Prophets",
    "Full Submission",
    "Prophets of Islam",
    "The Only Way",
    "Deviating from the Right Path",
    "Dying in a State of Disbelief",
    "Righteous Giving",
    "Jacob’s Dietary Restriction",
    "Pilgrimage to the Sacred House in Mecca",
    "Rejecting the Truth",
    "Warning Against Evil Influence",
    "Warning Against Disunity",
    "The Joyful and the Miserable",
    "Excellence of the Muslim Nation",
    "Upright People of the Book",
    "Warning Against Hypocrites",
    "Association with Hypocrites",
    "The Battle of Uḥud",
    "The Battle of Badr",
    "Allah Is the Judge",
    "Warning Against Interest",
    "Reward of the Righteous",
    "Battle Between Good and Evil",
    "Reassuring the Believers",
    "Believers Tested",
    "Believers Disheartened",
    "Reward of the Steadfast",
    "Yielding to the Disbelievers",
    "Victory Denied at Uḥud",
    "The Army Retreats",
    "The Deserters",
    "It Is All Destined",
    "Prophet’s Kindness to the Believers",
    "Victory Is from Allah",
    "Spoils of War",
    "Good-Doers and Wrongdoers",
    "The Prophet as a Blessing",
    "Lessons from the Battle of Uḥud",
    "Martyrs Honoured",
    "Disbelievers’ Delusion",
    "Sincerity Test",
    "Reward of the Stingy",
    "Blasphemy Exposed",
    "Rejecting Allah’s Messengers",
    "Death Is Inevitable",
    "Patience Tested",
    "Allah’s Signs",
    "A Prayer of the Righteous",
    "Prayers Answered",
    "Disbelievers’ Brief Enjoyment",
    "Believers’ Everlasting Delight",
    "Believers Among People of the Book",
    "Advice for Success",
]

text = open(RAW, encoding="utf-8").read()

# 1. Remove footnote markers [n]
text = re.sub(r"\[\d+\]", "", text)

# 2. Remove section headings (must all be present; longest first so no
#    heading is left as the tail of a longer one)
for h in sorted(HEADINGS, key=len, reverse=True):
    if h not in text:
        sys.exit(f"HEADING NOT FOUND: {h}")
    # remove "Heading " (with following space) and bare "Heading." occurrences
    text = text.replace(h + " ", "")
    text = text.replace(h, "")

# 3. Normalize whitespace, join lines
text = re.sub(r"\s+", " ", text).strip()

# 4. Split into verses: "N. " tokens
matches = list(re.finditer(r"(?:^|\s)(\d{1,3})\.\s", text))
verses = {}
for i, m in enumerate(matches):
    n = int(m.group(1))
    start = m.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    piece = text[start:end].strip()
    if verses.get(n):
        sys.exit(f"duplicate verse {n}")
    verses[n] = piece

expected = list(range(1, 201))
missing = [n for n in expected if n not in verses]
extra = [n for n in sorted(verses) if n not in expected]
if missing:
    print("MISSING:", missing)
if extra:
    print("EXTRA:", extra)
if missing or extra:
    sys.exit(1)
if not all(verses[n] for n in expected):
    sys.exit("empty verse found")

# 5. Sanity checks
for n in expected:
    t = verses[n]
    if "[" in t or "]" in t:
        sys.exit(f"leftover bracket in v{n}: {t[:60]}")
    if t.startswith(".") or t.endswith(".") is False:
        print(f"note v{n}: boundary check -> {t[-40:]!r}")

json.dump(
    {"chapter": 3, "name": "Ali 'Imran", "verses": [{"verse": n, "translation": verses[n]} for n in expected]},
    open(OUT, "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2,
)
print(f"OK -> {OUT}: {len(verses)} verses")
for n in (1, 4, 7, 36, 55, 96, 175, 185, 200):
    print(f"  v{n}: {verses[n][:90]}...")
