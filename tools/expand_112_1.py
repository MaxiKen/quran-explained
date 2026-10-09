# -*- coding: utf-8 -*-
"""Expand 112:1 to meet its floor. Floor rule: a verse may run long, never short."""
import json, os

ROOT = '/home/user/quran-explained'
PLAN = json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))
path = os.path.join(ROOT, 'data/guidance_112.json')
doc = json.load(open(path, encoding='utf-8'))

t = doc['verses']['1']['text']

# --- 1. the gold-or-silver report, which the existing text only gestures at ---
anchor = 'The question behind all of them is the same, and it is the question the sūrah answers: *where does your God come from?*'
assert anchor in t, 'occasion anchor not found'
add1 = anchor + """

Tanwīr al-Miqbās preserves the sharpest version of the question, on the authority of **Ibn ʿAbbās**: *the people of Quraysh asked the Prophet ﷺ, "O Muhammad! Describe for us your Lord; is He made of gold or silver?" And so Allah revealed this sūrah to describe His attributes and traits.*

Is He made of gold or silver. That is not a theological question. It is a request for a material description — what substance, what shape, what is He out of. And the sūrah's answer refuses the form of the question entirely. It gives no substance, no shape, no genealogy. It gives a Name and a denial.

Ibn Kathīr records the grading of the main report and keeps the disagreement visible: **Ibn Abī Ḥātim** also recorded it, and **at-Tirmidhī** mentioned it as a mursal narration, then said, *"And this is the most correct."*"""
t = t.replace(anchor, add1, 1)

# --- 2. what happened to the sūrah afterwards: the two hadiths on its use ---
tail = 'He is alone in being a deity; there is no deity except Him.'
assert t.rstrip().endswith(tail), 'tail not found'
add2 = """

**What the sūrah became.**

Ibn Kathīr follows the occasion with two reports about how the sūrah was actually used, and both turn on one man's attachment to it.

Al-Bukhārī reported from **ʿAmrah bint ʿAbd ar-Raḥmān**, who used to stay in the apartment of **ʿĀʾishah**, the wife of the Prophet ﷺ, that ʿĀʾishah said: *The Prophet ﷺ sent a man as the commander of a war expedition, and he used to lead his companions in prayer with recitation of the Qurʾān, and he would complete his recitation with "Say: He is Allah, One." So when they returned they mentioned that to the Prophet ﷺ, and he said, "Ask him why he does that." So they asked him, and he said, "Because it is the description of ar-Raḥmān, and I love to recite it." So the Prophet ﷺ said, "Inform him that Allah the Most High loves him."*

Muslim and an-Nasāʾī recorded it too.

Al-Bukhārī records a second, in his Book of Ṣalāh, from **Anas**: *A man from the Anṣār used to lead the people in prayer in the Masjid of Qubāʾ. Whenever he began a sūrah in the recitation of the prayer that he was leading them, he would start by reciting "Say: He is Allah, One" until he completed the entire sūrah. Then he would recite another sūrah along with it. And he used to do this in every rakʿah.*

His companions objected that one sūrah should be enough. What is worth holding is the reason neither man gave — not that it was required, but that he loved it. *It is the description of ar-Raḥmān.*

The sūrah was revealed to answer a demand for a lineage. What it produced instead was the shortest statement of tawḥīd in the Qurʾān, and two men who would not lead a prayer without it."""

t = t.rstrip() + '\n' + add2
t = '\n'.join(ln.rstrip() for ln in t.strip('\n').split('\n'))

bad = [c for c in t if 0x0400 <= ord(c) <= 0x04FF]
assert not bad, f'Cyrillic homoglyphs: {bad}'
doc['verses']['1']['text'] = t

with open(path, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
    fh.write('\n')

print('  verse   tier  words  target  floor   status')
for a, v in sorted(doc['verses'].items(), key=lambda x: int(x[0])):
    n = len(v['text'].split())
    tgt = PLAN[f'112:{a}']['words']
    fl = round(tgt * 0.75)
    print(f'  112:{a}    {PLAN[f"112:{a}"]["tier"]}    {n:5d}  {tgt:6d}  {fl:5d}   '
          f'{"UNDER FLOOR" if n < fl else "ok"}')
print(f'  file: {len(doc["verses"])} verses, '
      f'{sum(len(v["text"].split()) for v in doc["verses"].values()):,} words, '
      f'{os.path.getsize(path):,} bytes')
