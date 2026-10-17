# The phrase-by-phrase pairing

`data/pairs_NNN.json` pairs the reader's own modern translation with Ṭabarī's
explanation of it, phrase by phrase.

The reader's verse sheet carries a modern English rendering of the verse.
Ṭabarī's commentary explains the verse's phrases, and names each one in his
own words:

    The statement concerning the explanation of His saying: إِيَّاكَ نَعْبُدُ
    ("You alone we worship")

The pairing is **authored by hand**. For each verse, Ṭabarī's English
commentary is read against the reader's modern translation, and a phrase is
written that says, in plain modern English, what Ṭabarī says about that piece
of the verse. The words Ṭabarī himself uses are never reused as the phrase
line: the line is the author's own.

## The source files

`authored/NNN.json` holds the hand-written pairing, one file per surah.
The filename is always three digits, because the builder reads the surah
number from the first three characters.

    {
      "surah": 90,
      "note": "Authored by reading Tafsir al-Tabari in English ...",
      "verses": {
        "1": {
          "phrases": [
            {
              "translation": "I do swear by this city ˹of Mecca˺—",
              "text": "God swears by this city, and the commentators agree that Mecca is meant.",
              "ar": "لَآ أُقۡسِمُ بِهَٰذَا ٱلۡبَلَدِ",
              "range": [0, 9]
            }
          ]
        }
      }
    }

- `translation` — the reader's own words for that piece of the verse. It is
  copied exactly from the verse's `ayah_en`, so it always reads as the app
  renders it.
- `text` — the modern English line, written by the author. It explains what
  Ṭabarī says about that piece in plain, easy English, and it is never a
  quotation of Ṭabarī's older phrasing.
- `ar` — the Arabic of that piece, taken from the verse.
- `range` — the inclusive range of Ṭabarī's paragraph numbers that speak of
  that piece. The numbering is the same one the quick read uses, so a
  paragraph number means the same thing in both.

A verse may carry more than one phrase. The first phrase holds the
translation; a continuation phrase leaves `translation` empty and its
`text` carries on the explanation.

## The rules

- The translation is split into the clauses a reader would call phrases:
  sentences, and the parts of a sentence that stand on their own.
- Ṭabarī's passage is split into paragraphs, the same way the reader's quick
  read splits it, so a paragraph number means the same thing in both.
- The chains of transmission ("X related to us, saying: ...") carry the
  saying; they are not the explanation of it, and they are not used.
- The Arabic of the phrase is taken from the verse, comparing the Uthmani
  spelling with the imla'i spelling, and the U+0670 dagger alef is accepted
  in either reading.

## The checks

`assemble.py --check` validates the authored layer before anything is
published. It reports:

- a phrase line that is not 3 to 60 words, does not begin with a capital, or
  contains Arabic, an em dash, an en dash or a semicolon;
- a `translation` that is not present in the verse's own `ayah_en`;
- a phrase `ar` that is not present in the verse's Arabic;
- a `range` whose paragraph numbers do not exist, run backwards, or overlap
  out of order;
- and, with `--gaps`, any paragraph of Ṭabarī's commentary that no phrase
  speaks to.

A surah that fails any of these is not published.

## Running it

    python3 tools/pairs/assemble.py --check --gaps   # validate the authored files
    python3 tools/pairs/assemble.py                  # publish data/pairs_NNN.json
    python3 tools/pairs/dump.py 90 8-20              # read Tabari for a verse range
    python3 tools/pairs/show.py 90 8                 # show a verse and its paragraphs
    cd tools/pairs && python3 -m unittest discover -s tests

`assemble.py` writes `data/pairs_NNN.json`, one file per surah. The published
file keeps `translation`, `text` and `ar`, and replaces `range` with
`parts`, the list of the paragraph numbers the quick read should show under
that phrase.

## What it does not do

The builder never writes a sentence. It reads the authored files, checks
them, and republishes them. Every word of the phrase line was written by
hand, by reading Ṭabarī's English commentary against the reader's
translation.
