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

from __future__ import annotations

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


def gloss_candidates(heading: str) -> list[str]:
    """The ways the heading names the phrase, best first.

    A heading may name the phrase in plain words after the colon, or inside
    brackets, or both. Each candidate is tried in turn.
    """
    if ':' not in heading:
        return []
    after = heading.split(':', 1)[1]
    after = ARABIC.sub(' ', after)
    candidates = []
    plain = after.strip()
    if plain:
        candidates.append(plain)
    for bracket in re.findall(r'\(([^()]*)\)', after):
        bracket = bracket.strip()
        if bracket:
            candidates.append(bracket)
    return candidates


def tokenize(text: str) -> list[tuple[int, int, str]]:
    """The words of the text, with their offsets, without the stop words."""
    out = []
    for match in WORD.finditer(text):
        word = strip_accents(match.group(0).lower().replace('’', "'"))
        word = BRITISH.get(word, word)
        if word and word not in STOP and len(word) > 1:
            out.append((match.start(), match.end(), word))
    return out


def find_span(candidate: str, modern: str, modern_tokens: list[tuple[int, int, str]]):
    """Where the candidate's words fall in the modern translation.

    The longest run of the candidate's own words that appears in the modern
    translation, in order. Returns (words matched, first token, last token).
    """
    gloss = tokenize(candidate)
    if not gloss or not modern_tokens:
        return 0, -1, -1
    words = [t[2] for t in modern_tokens]
    for size in range(min(len(gloss), 6), 1, -1):
        for start in range(0, len(gloss) - size + 1):
            needle = [t[2] for t in gloss[start:start + size]]
            hits = []
            position = 0
            ok = True
            for word in needle:
                while position < len(words) and words[position] != word:
                    position += 1
                if position >= len(words):
                    ok = False
                    break
                hits.append(position)
                position += 1
            if ok:
                # The words must be together in the translation too. A
                # fragment whose words are scattered across the verse is
                # not a match for any one of its phrases.
                if hits[-1] - hits[0] > size:
                    continue
                return size, hits[0], hits[-1]
    # A short name may share only one word with the translation: "the Book",
    # "the Day". One distinctive word, used once, is then enough. A long
    # sentence that happens to share a single word is not.
    if len(gloss) <= 4:
        for start in range(len(gloss) - 1, -1, -1):
            word = gloss[start][2]
            if len(word) < 4:
                continue
            places = [i for i, w in enumerate(words) if w == word]
            if len(places) == 1:
                return 1, places[0], places[0]
    return 0, -1, -1


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


def arabic_span(heading: str, verse_arabic: str) -> str:
    """The Arabic of the phrase, as the heading gives it, when the verse
    carries the same words. The two spellings differ in their vowel marks
    and in the shape of some letters, so they are compared without them."""
    if not verse_arabic:
        return ''
    key = normalise_arabic(verse_arabic)
    best = ''
    for chunk in ARABIC_RUN.findall(heading):
        piece = chunk.strip()
        if len(piece) < 3:
            continue
        if normalise_arabic(piece) in key and len(piece) > len(best):
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


def normalise_arabic(text: str) -> str:
    """Arabic as a key for comparison.

    The reader's verse text is the Uthmani orthography and Tabari's quotation
    is the imla'i one: the same words written with different vowel marks,
    different alefs and a few extra letters. Only the letters themselves
    are kept, so the two can be compared; the text the reader sees is
    never changed.
    """
    letters = []
    for char in text or '':
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


def fragment_candidates(paragraph: str) -> list[str]:
    """The phrases of the verse a paragraph names.

    Tabari quotes the phrase he is speaking about: "As for His word 'the
    Living' (al-Hayy): ...". Every quoted span in a paragraph is a
    candidate name for a phrase of the verse.
    """
    out = []
    for match in QUOTED.finditer(paragraph):
        piece = (match.group(1) or match.group(2) or match.group(3) or '').strip()
        if not piece:
            continue
        if ARABIC.sub('', piece).strip():
            out.append(piece)
    return out


def pair_verse(modern: str, arabic: str, passage: str) -> list[dict]:
    """The phrases of the modern translation, each with the words Tabari says
    about that phrase.

    Every phrase of the translation is returned, whether or not Tabari has
    something to say about it. A phrase with no explanation carries an empty
    list of parts: that is the honest answer, and none of his text is lost
    by it.
    """
    parts = paragraphs_of(passage)
    clauses = split_clauses(modern)
    if not parts or not clauses:
        return []

    clean, mapping = clean_modern(modern)
    modern_tokens = tokenize(clean)
    if not modern_tokens:
        return []

    # The phrases Tabari names, and the paragraph each name stands in.
    groups = []
    for index, paragraph in enumerate(parts):
        heading = paragraph if is_phrase_opening(paragraph) else ''
        groups.append({'heading': heading, 'start': index,
                       'end': len(parts) if not heading else index})
    for number, group in enumerate(groups):
        if group['heading']:
            continue
        for earlier in reversed(groups[:number]):
            if earlier['heading']:
                group['start'] = earlier['start']
                break
    for number, group in enumerate(groups):
        if not group['heading']:
            continue
        end = len(parts)
        for later in groups[number + 1:]:
            if later['heading']:
                end = later['start']
                break
        group['end'] = end

    def clause_of(start_char: int) -> int:
        for position, clause in enumerate(clauses):
            if clause['start'] <= start_char < clause['end']:
                return position
        return -1

    found = {}
    for index, paragraph in enumerate(parts):
        # The chain of transmission that carries the saying is not the
        # explanation of the phrase; it is the road it travelled.
        if NOT_A_PHRASE.search(paragraph) and not is_phrase_opening(paragraph):
            continue
        candidates = list(fragment_candidates(paragraph))
        if is_phrase_opening(paragraph):
            candidates = gloss_candidates(paragraph) + candidates
        for candidate in candidates:
            size, first, last = find_span(candidate, clean, modern_tokens)
            if size == 0:
                continue
            start_char = mapping[modern_tokens[first][0]]
            position = clause_of(start_char)
            if position < 0:
                continue
            entry = found.setdefault(position, {'parts': [], 'ar': ''})
            if index not in entry['parts']:
                entry['parts'].append(index)
            if not entry['ar']:
                piece = arabic_span(paragraph, arabic)
                if piece:
                    entry['ar'] = piece
            break

    phrases = []
    for position, clause in enumerate(clauses):
        record = {'text': clause['text'], 'ar': '', 'head': '', 'parts': []}
        entry = found.get(position)
        if entry:
            record['parts'] = entry['parts']
            record['ar'] = entry['ar']
            group = groups[entry['parts'][0]]
            record['head'] = group['heading']
        phrases.append(record)
    return phrases


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


def build_surah(surah: int) -> dict:
    tafsir_path = os.path.join(ROOT, 'data', 'tafsir_%03d.js' % surah)
    if not os.path.exists(tafsir_path):
        tafsir_path = os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah)
    with open(tafsir_path, encoding='utf-8') as handle:
        tafsir = json.load(handle)
    chapter = read_chapter(surah)
    verses = {}
    for ayah, entry in tafsir['verses'].items():
        passage = tafsir['sets']['tabari']['blocks'][entry['tabari']]
        verse = chapter.get(ayah, {})
        phrases = pair_verse(verse.get('en', ''), verse.get('ar', ''), passage)
        if phrases:
            verses[ayah] = {'phrases': phrases}
    return {'surah': surah, 'verses': verses}


def write_all(only=None) -> int:
    """Write `data/pairs_NNN.json` for every surah."""
    written = 0
    for surah in range(1, 115):
        if only and surah not in only:
            continue
        path = os.path.join(ROOT, 'data', 'tafsir_%03d.json' % surah)
        if not os.path.exists(path):
            continue
        data = build_surah(surah)
        if not data['verses']:
            continue
        out = os.path.join(ROOT, 'data', 'pairs_%03d.json' % surah)
        with open(out, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False, separators=(',', ':'))
        written += 1
    return written


if __name__ == '__main__':
    import sys
    wanted = None
    if len(sys.argv) > 1:
        wanted = {int(part) for part in sys.argv[1].split(',')}
    count = write_all(wanted)
    print('wrote %d file(s)' % count)
