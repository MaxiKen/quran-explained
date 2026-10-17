"""Reading the commentary, for the phrase-by-phrase pairing.

The pairing in `authored/` is written by reading Tafsir al-Tabari in English
against the reader's modern translation. This module is what that reading
needs: the passage as the reader sees it, the paragraphs it is made of, the
verse's own translation and Arabic, and the tools to line them up.

Nothing here writes a pairing. It reads the material and checks it.
"""

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""Pair the app's modern translation with Tabari's own explanation.

The reader's verse sheet carries a modern English rendering of the verse.
Tabari's commentary carries, in the same verse, the explanation of the
verse's phrases — and each of those phrases is named in his own words:

    The statement concerning the explanation of His saying: إِيَّاكَ نَعْبُدُ
    ("You alone we worship").

Where the two renderings share their wording, the phrase in the modern
translation can be found by matching Tabari's own words against it. This
module does that, and nothing else: it never writes a sentence of its own,
it only decides which of the reader's words belong to which of Tabari's
explanations.

The output is one file per surah, `data/pairs_NNN.json`:

    {"surah": 1, "verses": {"1": {"phrases": [
        {"text": "…the reader's own words…",
         "ar": "…the Arabic of that phrase…",
         "parts": [3, 4]}]}}}

`parts` are paragraph numbers in the Tabari passage, so the app can show his
own words without a second copy of them being stored. A phrase with no
matching explanation carries an empty list: that is the honest answer, and
the passage is not lost — the reader still sees the whole of it.
"""

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The reader marks the words of the translation that are the Arabic of the
# verse with these. They are removed for matching and put back for display.
MARK_OPEN = '˹'
MARK_CLOSE = '˺'

# The formula that opens a phrase in Tabari's text.
FORMULA = re.compile(
    r'^(?:The\s+)?'
    r'(?:explanation|exposition|discourse|statement|discussion|interpretation|'
    r'meaning|purpose|significance|word|words|saying|utterance|purport)\b'
    r'[^:]{0,160}:', re.I)

# Lines that never open a phrase, however they are worded.
NOT_A_PHRASE = re.compile(
    r'^(?:\(\d+\)|\d+\s+[—–-])|'
    r'(?:Mention of who said|The mention of who|'
    r'In the printed edition|in the manuscript|in the copy of|'
    r'and in the margin|as it is written in|'
    r'.*\brelated (?:to us|to me)\b)', re.I)

ARABIC = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]+')
# The same, but a phrase of Arabic keeps the spaces between its words.
ARABIC_RUN = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]+(?:[  ]+[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]+)*')

STOP = set("""a an the of and or but so then that this these those is are was were be been being
am do does did to in on at by for with without from as it its he she they them his her their we us our
you your i me my not no nor if than there here what which who whom whose when while because
except without unless whether perhaps beside besides within upon through throughout against toward
towards unlike like plus minus versus per among despite whereas since until whenever wherever
whatever whoever however moreover nevertheless therefore thus hence yet still even only just
such very more most less least all any both each other another same only just also too can could
will would shall should may might must have has had having done said says say one two
into upon unto about over under again further once him himself herself themselves""".split())

WORD = re.compile(r"[A-Za-zÀ-ɏ'’-]+")

# The reader's translation is in British English, Tabari's is in American.
# Without this the two never meet: "favours" and "favors" are the same word.
BRITISH = {
    'favour': 'favor', 'favours': 'favors', 'favoured': 'favored', 'favouring': 'favoring',
    'favourable': 'favorable', 'unfavourable': 'unfavorable', 'favouritism': 'favoritism',
    'honour': 'honor', 'honours': 'honors', 'honoured': 'honored', 'honourable': 'honorable',
    'labour': 'labor', 'labours': 'labors', 'laboured': 'labored', 'labouring': 'laboring',
    'neighbour': 'neighbor', 'neighbours': 'neighbors', 'neighbouring': 'neighboring',
    'neighbourhood': 'neighborhood', 'behaviour': 'behavior', 'behavioural': 'behavioral',
    'colour': 'color', 'colours': 'colors', 'coloured': 'colored', 'colourless': 'colorless',
    'demeanour': 'demeanor', 'endeavour': 'endeavor', 'endeavours': 'endeavors',
    'valour': 'valor', 'vigour': 'vigor', 'splendour': 'splendor', 'flavour': 'flavor',
    'flavours': 'flavors', 'vapour': 'vapor', 'odour': 'odor', 'armour': 'armor',
    'harbour': 'harbor', 'parlour': 'parlor', 'tumour': 'tumor', 'clamour': 'clamor',
    'ardour': 'ardor', 'rigour': 'rigor', 'humour': 'humor', 'saviour': 'savior',
    'succour': 'succor', 'realise': 'realize', 'realised': 'realized', 'realises': 'realizes',
    'recognise': 'recognize', 'recognised': 'recognized', 'recognises': 'recognizes',
    'apologise': 'apologize', 'apologised': 'apologized', 'organise': 'organize',
    'organised': 'organized', 'criticise': 'criticize', 'criticised': 'criticized',
    'emphasise': 'emphasize', 'emphasised': 'emphasized', 'characterise': 'characterize',
    'summarise': 'summarize', 'summarised': 'summarized', 'memorise': 'memorize',
    'categorise': 'categorize', 'civilise': 'civilize', 'colonise': 'colonize',
    'baptise': 'baptize', 'specialise': 'specialize', 'standardise': 'standardize',
    'utilise': 'utilize', 'authorise': 'authorize', 'authorised': 'authorized',
    'legalise': 'legalize', 'moralise': 'moralize', 'neutralise': 'neutralize',
    'hospitalise': 'hospitalize', 'paralyse': 'paralyze', 'idealise': 'idealize',
    'signalise': 'signalize', 'visualise': 'visualize', 'verbalise': 'verbalize',
    'minimise': 'minimize', 'maximise': 'maximize', 'popularise': 'popularize',
    'urbanise': 'urbanize', 'synchronise': 'synchronize', 'dramatise': 'dramatize',
    'harmonise': 'harmonize', 'analyse': 'analyze', 'analysed': 'analyzed',
    'analyses': 'analyzes', 'catalyse': 'catalyze', 'organisation': 'organization',
    'realisation': 'realization', 'civilisation': 'civilization', 'normalisation': 'normalization',
    'centre': 'center', 'centres': 'centers', 'metre': 'meter', 'metres': 'meters',
    'litre': 'liter', 'litres': 'liters', 'theatre': 'theater', 'fibre': 'fiber',
    'calibre': 'caliber', 'sombre': 'somber', 'spectre': 'specter', 'grey': 'gray',
    'programme': 'program', 'dialogue': 'dialog', 'catalogue': 'catalog',
    'practise': 'practice', 'licence': 'license', 'defence': 'defense',
    'offence': 'offense', 'pretence': 'pretense', 'travelling': 'traveling',
    'travelled': 'traveled', 'cancelled': 'canceled', 'cancelling': 'canceling',
    'modelling': 'modeling', 'labelling': 'labeling', 'fulfil': 'fulfill',
    'skilful': 'skillful', 'wilful': 'willful', 'marvellous': 'marvelous',
    'per cent': 'percent', 'enquiry': 'inquiry', 'sceptical': 'skeptical',
    'sceptic': 'skeptic', 'aluminium': 'aluminum', 'jewellery': 'jewelry',
    'kerb': 'curb', 'tyre': 'tire', 'plough': 'plow', 'storey': 'story',
    'gaol': 'jail', 'mould': 'mold', 'sulphur': 'sulfur', 'cheque': 'check',
    'moustache': 'mustache', 'pyjamas': 'pajamas', 'speciality': 'specialty',
    'aeroplane': 'airplane', 'counsellor': 'counselor', 'jeweller': 'jeweler',
    'levelled': 'leveled', 'signalled': 'signaled', 'totalled': 'totaled',
    'dialled': 'dialed', 'fuelled': 'fueled', 'equalled': 'equaled',
    'marshalled': 'marshaled', 'barrelled': 'barreled', 'counselling': 'counseling',
}


def strip_accents(word: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn')

def is_phrase_opening(line: str) -> bool:
    """True when the line opens a phrase of the verse."""
    if not line or len(line) >= 320 or ':' not in line:
        return False
    if NOT_A_PHRASE.search(line):
        return False
    match = FORMULA.search(line)
    if not match:
        return False
    if len(match.group(0)) - 1 > 90:
        return False
    if len(line) - len(match.group(0)) > 220:
        return False
    return True

def paragraphs_of(text: str) -> list[str]:
    """The passage as the reader sees it: one entry per paragraph."""
    out = []
    for part in (text or '').split('\n\n'):
        part = part.strip()
        if not part or re.fullmatch(r'[-*_—–=\s]{3,}', part):
            continue
        out.append(part)
    return out

def tokenize(text: str) -> list[tuple[int, int, str]]:
    """The words of the text, with their offsets, without the stop words."""
    out = []
    for match in WORD.finditer(text):
        word = strip_accents(match.group(0).lower().replace('’', "'"))
        word = BRITISH.get(word, word)
        if word and word not in STOP and len(word) > 1:
            out.append((match.start(), match.end(), word))
    return out

def clean_modern(text: str) -> tuple[str, list[tuple[int, int]]]:
    """The modern translation without the reader's markers, and the map back
    to the original offsets."""
    out = []
    mapping = []
    for index, char in enumerate(text):
        if char in (MARK_OPEN, MARK_CLOSE):
            continue
        out.append(char)
        mapping.append(index)
    mapping.append(len(text))
    return ''.join(out), mapping

def arabic_in(piece: str, verse_arabic: str) -> bool:
    """Whether the verse carries these Arabic words.

    The reader's verse is the Uthmani orthography and the commentary quotes
    the imla'i one. The dagger alef of the Uthmani stands sometimes for a
    written alif and sometimes for a long vowel the other spelling leaves
    out, so both readings are tried.
    """
    if not piece or not verse_arabic:
        return False
    for dagger in ('drop', 'alef'):
        if normalise_arabic(piece, dagger) in normalise_arabic(verse_arabic, dagger):
            return True
    return False

def arabic_span(heading: str, verse_arabic: str) -> str:
    """The Arabic of the phrase, as the heading gives it, when the verse
    carries the same words. The two spellings differ in their vowel marks
    and in the shape of some letters, so they are compared without them."""
    if not verse_arabic:
        return ''
    best = ''
    for chunk in ARABIC_RUN.findall(heading):
        piece = chunk.strip()
        if len(piece) < 3:
            continue
        if arabic_in(piece, verse_arabic) and len(piece) > len(best):
            best = piece
    return best

# Arabic letters that differ only in shape between the reader's text and
# Tabari's quotation, and the vowel marks that one of them carries.
ARABIC_NORMALISE = {
    # The Uthmani text writes the dagger alef small and high; it is the
    # same letter as the plain alef of the imla'i spelling.
    '\u0670': '\u0627', '\u0671': '\u0627', '\u0622': '\u0627', '\u0623': '\u0627',
    '\u0625': '\u0627', '\u0649': '\u064A', '\u0624': '\u0648',
}

def normalise_arabic(text: str, dagger: str = 'drop') -> str:
    """Arabic as a key for comparison.

    The reader's verse text is the Uthmani orthography and Tabari's quotation
    is the imla'i one: the same words written with different vowel marks,
    different alefs and a few extra letters. Only the letters themselves
    are kept, so the two can be compared; the text the reader sees is
    never changed.
    """
    letters = []
    for char in text or '':
        if char == '\u0670':      # the dagger alef, in either reading
            if dagger == 'alef':
                letters.append('\u0627')
            continue
        if not ('\u0620' <= char <= '\u064a' or '\u066e' <= char <= '\u06d3'
                or '\u06f0' <= char <= '\u06fa' or '\u0750' <= char <= '\u077f'
                or '\u08a0' <= char <= '\u08ff' or '\ufb50' <= char <= '\ufdff'
                or '\ufe70' <= char <= '\ufeff'):
            continue
        letters.append(ARABIC_NORMALISE.get(char, char))
    return ''.join(letters)

# The reader's translation is punctuated for reading. A phrase of the verse
# is a clause of it: a sentence, or a part of one that stands on its own.
SENTENCE_BREAK = re.compile(r'(?<=[.!?])\s+(?=[A-Z\u201c"])')
DASH_BREAK = re.compile(r'\s*[\u2014\u2013]\s*')
COLON_BREAK = re.compile(r'(?<=[;:])\s+')
# A comma only ends a phrase when what follows starts a clause of its own.
CLAUSE_WORD = re.compile(
    r'^(and|but|or|so|then|yet|nor|for|while|when|because|although|though|whereas|'
    r'who|whom|which|that|as|since|until|unless|after|before|if|meaning|namely)\b', re.I)

def _split_commas(sentence: str) -> list[str]:
    """Break a sentence at the commas that end a clause."""
    pieces = []
    start = 0
    for match in re.finditer(r',\s+', sentence):
        after = sentence[match.end():]
        if not CLAUSE_WORD.match(after):
            continue
        before = sentence[start:match.start()]
        if len(before.split()) < 4:
            continue
        pieces.append(sentence[start:match.end()])
        start = match.end()
    pieces.append(sentence[start:])
    return pieces

def _break_sentence(sentence: str) -> list[str]:
    """One sentence, broken into the phrases that stand on their own."""
    pieces = []
    for colon_part in COLON_BREAK.split(sentence):
        for dash_part in DASH_BREAK.split(colon_part):
            for comma_part in _split_commas(dash_part):
                piece = comma_part.strip()
                if piece:
                    pieces.append(piece)
    return pieces

def split_clauses(text: str) -> list[dict]:
    """The modern translation as the clauses a reader would call phrases."""
    if not text:
        return []
    pieces = []
    offset = 0
    for match in SENTENCE_BREAK.finditer(text):
        pieces.extend(_break_sentence(text[offset:match.start()]))
        offset = match.end()
    pieces.extend(_break_sentence(text[offset:]))

    out = []
    position = 0
    for piece in pieces:
        index = text.find(piece, position)
        if index < 0:
            index = position
        out.append({'text': piece, 'start': index, 'end': index + len(piece)})
        position = index + len(piece)
    return [c for c in out if re.search(r'[A-Za-z\u0600-\u06FF]', c['text'])]



QUOTED = re.compile(r'"([^"\n]{3,200})"|\u201c([^\u201d\n]{3,200})\u201d|\(([^()\n]{3,200})\)')

def read_chapter(surah: int) -> dict:
    """The reader's own verse data: the modern translation and the Arabic."""
    path = os.path.join(ROOT, 'data', 'chapter_%03d.js' % surah)
    with open(path, encoding='utf-8') as handle:
        source = handle.read()
    verses = {}
    pattern = (r'"ayah_no_surah":\s*(\d+),\s*\n\s*"ayah_ar":\s*"(.*?)",\s*\n'
               r'\s*"ayah_en":\s*"(.*?)"')
    for match in re.finditer(pattern, source, re.S):
        verses[match.group(1)] = {'ar': match.group(2), 'en': match.group(3)}
    return verses

def quick_label(paragraph: str) -> str:
    """The opening line of a paragraph, the way the reader's quick read
    shows it: the first sentence, cut short with an ellipsis."""
    text = (paragraph or '').strip()
    dot = text.find('. ')
    first = text[:dot + 1] if dot > 0 else text
    if len(first) > 200:
        cut = first[:200]
        space = cut.rfind(' ')
        first = (cut[:space] if space > 120 else cut).rstrip() + '\u2026'
    return first

