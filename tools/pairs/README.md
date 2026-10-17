# The phrase-by-phrase pairing

`data/pairs_NNN.json` pairs the reader's own modern translation with Ṭabarī's
explanation of it, phrase by phrase.

The reader's verse sheet carries a modern English rendering of the verse.
Ṭabarī's commentary explains the verse's phrases, and names each one in his
own words:

    The statement concerning the explanation of His saying: إِيَّاكَ نَعْبُدُ
    ("You alone we worship")

Where the two renderings share their wording, the phrase in the modern
translation can be found by matching Ṭabarī's own words against it. That
match is all this tool does: it never writes a sentence of its own, it only
decides which of the reader's words belong to which of Ṭabarī's paragraphs.

## The rules

- The translation is split into the clauses a reader would call phrases —
  sentences, and the parts of a sentence that stand on their own.
- Ṭabarī's passage is split into paragraphs, the same way the reader's quick
  read splits it, so a paragraph number means the same thing in both.
- A paragraph names the phrases of the verse in the words it quotes. Each
  quoted fragment is matched against the translation; the phrase that holds
  the match is the phrase that paragraph is about.
- The matched words must be *together* in the translation. A fragment whose
  words are scattered across the verse is not a match for any one phrase.
- The two translations are written in different English — the reader's is
  British, Ṭabarī's is American — so the spellings are brought together
  before matching.
- The chains of transmission ("X related to us, saying: ...") carry the
  saying; they are not the explanation of it, and they are left out.
- The Arabic of the phrase is taken from Ṭabarī's quotation when the verse
  carries the same words, comparing the Uthmani spelling of the verse with
  the imla'i spelling of the quotation.

## What it does not do

Where the two translations do not share their wording, the phrase is left
without Ṭabarī's words. About 45% of the translation's phrases are matched
this way; the rest would need a model to align. The builder never guesses:
a phrase with no match stays empty, and the whole of Ṭabarī's commentary is
still in the reader's quick read.

A model run may fill the rest, but it must write into the same file and hold
to the same two rules: the phrase must be the reader's own words, and the
parts must be paragraphs that exist in the commentary.

## Running it

    python3 tools/pairs/build.py            # every surah
    python3 tools/pairs/build.py 2,114      # two surahs
    cd tools/pairs && python3 -m unittest discover -s tests

The output is `data/pairs_NNN.json`, one file per surah.
