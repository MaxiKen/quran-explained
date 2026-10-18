# Phrase-by-phrase explanations

The reader offers two separate commentary views in a switch: **Phrase by
phrase** appears first, followed by **Full commentary**. Only the selected
view is shown; the full Tafsīr al-Ṭabarī passage is not stacked underneath the
phrase reading.

Phrase by phrase is a concise alternative to the full source commentary. It
pairs each consecutive piece of a verse's English translation with one clear,
naturally flowing paragraph of about 30–85 words. The paragraph should
explain the phrase, not merely restate it. Add a related verse, quotation,
context, history, or illustration only when it genuinely helps, and weave it
into the explanation without a type label or formulaic lead-in.

This layer is authored for the reader and is not an excerpt from or
replacement for Tafsīr al-Ṭabarī. Al-Fātiḥah (Surah 1), Al-Baqarah (Surah 2),
Āl ʿImrān (Surah 3), An-Nisāʾ (Surah 4), Al-Mā’idah (Surah 5),
Al-Anʿām (Surah 6), and Al-Aʿrāf (Surah 7) have been written in this
format; other surahs are not yet authored.

## Source files

`authored/NNN.json` is the hand-written source for one surah. Each verse is
split into consecutive phrases that cover its English translation:

```json
{
  "surah": 1,
  "verses": {
    "7": {
      "phrases": [
        {
          "translation": "the Path of those You have blessed",
          "explanation": "The next words explain what the Straight Path means: the way lived by people who obey Allah. Qur’an 4:69 names the prophets, the truthful, the martyrs, and the righteous among those whom Allah has favored. Their lives make guidance concrete, so the worshipper asks to follow a trustworthy way rather than invent one alone."
        }
      ]
    }
  }
}
```

- `translation` is an exact, consecutive piece of the reader's own `ayah_en`
  string. Phrase entries stay in reading order and together cover every word.
- `explanation` is one substantive paragraph in plain, easy English. Keep it
  short enough to read comfortably, but give each phrase enough context to
  stand as a real explanation, not a one-line gloss.

The phrases may be split into smaller pieces whenever that makes the meaning
clearer. Keep each paragraph focused on its phrase, and do not turn the
alternative reading into a second long commentary.

## Validate and publish

```sh
python3 tools/pairs/assemble.py --check
python3 tools/pairs/assemble.py
python3 tools/pairs/show.py 1 7
cd tools/pairs && python3 -m unittest discover -s tests
```

`assemble.py` checks that every phrase is in the verse, that phrases proceed
from top to bottom without skipping words, and that each explanation is a
single 30–85-word paragraph. It then publishes the data to
`data/pairs_NNN.json`, which the app displays in Phrase by phrase mode.
