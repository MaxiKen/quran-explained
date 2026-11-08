# Clear-teaching commentary (work in progress)

An English commentary layer for the Simple view: one entry per verse, written
from a reading of Fī Ẓilāl al-Qurʾān, in the app's own modern English.

**Mode: clear teaching.** The entry explains what the verse says to a reader
with no Arabic and no background. It is informed by Quṭb, and where it reports
his reading it says so, but it is not a translation of him and does not claim
to carry everything he says. When Quṭb and the entry diverge, that is a
decision, not an accident.

## What an entry must be

- **One entry per verse.** 6,236 in total, no verse skipped, no two verses
  sharing an entry. Distinctness is checked mechanically.
- **Aligned to the app's translation.** Each entry quotes the app's own
  `ayah_en` word for word, in order, so the reader can see which words are
  being explained.
- **Latin script only.** No Arabic or Urdu letters. The one exception is the
  salawat sign ﷺ. Arabic terms appear transliterated and italicised, with the
  meaning given at first use: *al-hamd* (praise).
- **No citation.** The entry speaks in one voice. It does not say "Qutb
  says", "the tafsir says", "scholars note". If a reading belongs to Quṭb it
  is stated as a reading, not attributed by name.
- **House style.** No em dash. No semicolon. No first person singular. No
  generic headings (Commentary, Explanation, Notes). Headings are `##`.

## Shape

```
## <what the verse does>        a section heading in sentence case
prose
## <a question a reader would ask>
prose
## In short
- bullet
- bullet
```

Sections are optional, the opening and In short are not. An entry runs as long
as the verse needs and no longer. A one-line verse gets a short entry.

## The four gates

```
python3 tools/clear/verify.py --dir work/clear
```

- `script`     no Arabic-block letters except ﷺ
- `distinct`   no run of 8 words shared between sibling verses
- `aligned`    every phrase of the app's translation appears in the entry
- `shape`      heading levels, dash, semicolon, citation, first person

A violation is a failure, not a warning. The gate reads the translation
straight out of `data/chapter_NNN.js`, so it cannot drift from the app.

## Status

| Surah | Entries | Gate |
|---|---|---|
| 1 | 7 | ok |

Nothing is wired into the reader. `work/clear/001.json` is a sample for
judging the voice, and the reader already renders an `en` payload (left to
right, headings and lists) if one is placed beside the Urdu.
