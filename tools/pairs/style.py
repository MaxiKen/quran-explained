#!/usr/bin/env python3
"""The house style every phrase explanation follows.

One module, used by the publishing gate (`assemble.py`) and by the authoring
tools in `tools/pairs/authoring/`, so a draft is held to the same rules as the
published data and a rule is written down in one place.

The rules, and why each is here:

- **No Arabic script.** The reader shows the Arabic of the verse next to the
  explanation. An explanation that repeats it in Arabic helps nobody, and the
  Arabic font is for the Qur'an itself.
- **No em dash, no en dash, no semicolon.** The reader's own text and the
  house voice use commas and full stops. A dash is also easy to lose in a
  copy and paste, and a semicolon makes a plain sentence harder to read.
- **One voice.** The explanation speaks for itself. It does not name the
  commentator whose view it reports, the transmitter whose chain it follows,
  or the companion whose report it summarises: those are the raw material,
  not the explanation. Write "a report from one of the companions", "the
  exegetes differed", "the preferred view". Under `tabari-v2` this is a hard
  rule checked by the gate; the older `sense-v1` chapters keep the text they
  were written under, and are held to it when they migrate.
- **Paragraphs are separated by a blank line**, and a paragraph never carries
  a line break inside it. The reader splits an explanation on blank lines and
  renders each part as its own paragraph, so a stray break would show.
- **A sentence starts with a capital letter.**

A figure who belongs to the story the verse tells, such as a prophet, a king
or an angel, is content and may be named. What is not allowed is the name of
the person whose view is being reported.
"""

from __future__ import annotations

import re

ARABIC = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
DASH = re.compile(r"[\u2014\u2013]")
STRAY_BREAK = re.compile(r"(?<!\n)\n(?!\n)")

# "Ibn Abbas", "Said ibn Jubayr", "Umar ibn al-Khattab" and the like: any
# personal name built on "ibn". Such a name is always the source of a view in
# this corpus, never a figure in the story, so it is never allowed.
IBN = re.compile(r"\b(?:Ibn|ibn)\s+(?:al-|bin\s+)?[A-Z\u2019'][\w\u2019'-]*")

# Commentators and transmitters Ṭabarī quotes by name, spelled the way this
# corpus writes them. Divine names (al-Rahman, al-Sami), place names (al-Raji,
# al-Muzdalifa), tribe names (al-Tamimi) and prophet names (al-Khidr) are
# deliberately not in this list.
NAMED_SOURCES = (
    r"al-Tabar[iī]|al-Tabārī|Ibn Jar[iī]r|Abu Ja['’]?far|"
    r"al-Zuhri|al-Hasan\b|al-Husayn\b|al-Suddi|al-Qat[aā]da|al-Dhahhak|"
    r"al-A['’]mash|al-Humaydi|al-Wahb|al-Bayhaqi|al-Nasa['’]i|"
    r"Muj[aā]hid|Ibn Jurayj|Ibn Kath[iī]r|Ibn Mas[uū]d|"
    r"al-Suy[uū]t[iī]|al-Qurtubi|"
    # companions and early figures the material quotes by name
    r"Salman\b|H[aā]tim\b|Umar\b|Uthman\b|\bAli\b|Abu Bakr|Aisha|Hafsa|"
    r"Ubayy\b|Utayba\b|Anas\b|Marwan\b"
)
NAMES = re.compile(r"\b(?:%s)\b" % NAMED_SOURCES, re.I)


def prose_problems(text: str, where: str) -> list[str]:
    """The rules every explanation follows, whatever its length."""
    problems: list[str] = []
    if ARABIC.search(text):
        problems.append("%s: explanation contains Arabic script" % where)
    if DASH.search(text):
        problems.append("%s: explanation contains an em dash or en dash" % where)
    if ";" in text:
        problems.append("%s: explanation contains a semicolon" % where)
    letters = [char for char in text if char.isalpha()]
    if not letters or not letters[0].isupper():
        problems.append("%s: explanation should start with a capital letter" % where)
    for number, part in enumerate(re.split(r"\n\s*\n", text), 1):
        if not part.strip():
            problems.append("%s: explanation has an empty paragraph" % where)
        elif STRAY_BREAK.search(part):
            problems.append("%s: paragraph %d has a stray line break" % (where, number))
    return problems


def name_problems(text: str, where: str) -> list[str]:
    """The one-voice rule: no commentator, transmitter or companion named."""
    problems: list[str] = []
    for pattern in (NAMES, IBN):
        for hit in pattern.finditer(text):
            problems.append("%s: names a source (%s)" % (where, hit.group(0).strip()))
    return problems


def style_problems(text: str, where: str, one_voice: bool = True) -> list[str]:
    """Every style problem in one explanation, as a list of messages."""
    problems = prose_problems(text, where)
    if one_voice:
        problems.extend(name_problems(text, where))
    return problems
