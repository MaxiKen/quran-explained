#!/usr/bin/env python3
"""Deterministic gates for generated entries.

    python3 tools/guidance/verify.py --source work  [--surahs 1,2]   # work/out  -> work/reports
    python3 tools/guidance/verify.py --source data  [--surahs 1,2]   # data/guidance_NNN.json

Three outcomes per entry:
    ok    publishable
    flag  publishable, but should go through the LLM audit/repair when the
          budget allows (coverage below threshold, dash/semicolon, long
          sentences, a verbatim run, duplicated material between sibling verses…)
    fail  must not be published (broken structure, Arabic script, names a
          source work, a cross-reference the material never cites, no opening
          quotation of the translation, no Phrase by phrase / In short …)

Coverage is measured with anchors: names, cross-references, numbers and
transliterated terms pulled out of the material. An anchor from a block that
covers several verses is satisfied if it appears in ANY of those verses'
entries, because the material is distributed across them by design.
"""
from __future__ import annotations

import argparse
import glob
import functools
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ARABIC_RE, SAW, WORK, DATA, SOURCE_ORDER, fold, word_count, verse_shares,  # noqa: E402
                    load_tafsir, load_chapter, chapter_meta, range_verses, clean_block,
                    parse_surah_selection, ensure_dir, read_json)

COVERAGE_FLAG = 0.85
COVERAGE_FAIL = 0.50
VERBATIM_RUN = 12          # words copied in a row -> flag
VERBATIM_RUN_FAIL = 24     # -> fail
RATIO_FLAG = 0.25          # entry words / verse's share of material words
PADDING_BASE = 200      # words of structure every entry needs (opening, phrase by phrase, in short)
PADDING_RATIO = 1.5     # flag an entry longer than base + ratio x its material

BANNED = [
    # the eight works and their authors: the entry speaks in its own voice
    r"ibn kathir", r"kathir", r"maarif", r"ma arif", r"mufti", r"muhammad shafi\b", r"shafi usmani", r"wahiduddin", r"tazkirul", r"tazkir",
    r"tanwir", r"miqbas", r"jalalayn", r"jalalain", r"mukhtasar", r"qushayri", r"qushairi", r"wahidi",
    r"lataif", r"asbab al nuzul\b(?! \()",
    # the digest voice
    r"\bthe sources?\b", r"\bthe tafsir", r"\bthe tafseer", r"\bthe commentators\b", r"\bthe commentaries\b",
    r"\bthis commentary\b", r"\btext \d\b", r"\bthe exegetes\b", r"\bclassical scholars (?:note|say|explain)",
]
GENERIC_HEADINGS = {
    'commentary', 'explanation', 'details', 'further notes', 'additional notes', 'additional points',
    'notes', 'overview', 'summary', 'conclusion', 'introduction', 'background', 'context', 'meaning',
    'lessons', 'analysis', 'discussion', 'other points', 'more', 'miscellaneous', 'general',
}
COLLECTORS = {
    'bukhari': 'al-Bukhārī', 'tirmidhi': 'at-Tirmidhī', 'abu dawud': 'Abū Dāwūd', 'nasai': 'an-Nasāʾī',
    'ibn majah': 'Ibn Mājah', 'ibn hibban': 'Ibn Ḥibbān', 'hakim': 'al-Ḥākim', 'bayhaqi': 'al-Bayhaqī',
    'tabarani': 'aṭ-Ṭabarānī', 'daraqutni': 'ad-Dāraquṭnī', 'ibn abi hatim': 'Ibn Abī Ḥātim',
    'ibn jarir': 'Ibn Jarīr', 'tabari': 'aṭ-Ṭabarī', 'abd razzaq': 'ʿAbd ar-Razzāq', 'ibn mardawayh': 'Ibn Mardawayh',
    'abu yala': 'Abū Yaʿlā', 'bazzar': 'al-Bazzār', 'darimi': 'ad-Dārimī', 'ibn khuzaymah': 'Ibn Khuzaymah',
    'ibn mundhir': 'Ibn al-Mundhir', 'abu nuaym': 'Abū Nuʿaym', 'musnad': 'Musnad', 'muwatta': 'Muwaṭṭaʾ',
}
GRADES = {
    'sahih': ['sahih', 'authentic'], 'hasan': ['hasan', 'good chain', 'fair'], 'daif': ['daif', 'weak'],
    'mawdu': ['mawdu', 'fabricated', 'forged'], 'gharib': ['gharib', 'strange'], 'munkar': ['munkar', 'rejected'],
    'mursal': ['mursal'], 'mutawatir': ['mutawatir'],
}

# canonical anchor -> spellings that count as a hit (all folded)
ALIASES = {
    'moses': ['musa', 'moses'], 'jesus': ['isa', 'jesus', 'messiah'], 'makkan': ['makki', 'makkan', 'meccan'],
    'madinan': ['madani', 'madinan', 'medinan'], 'abraham': ['ibrahim', 'abraham'],
    'ishmael': ['ismail', 'ishmael'], 'isaac': ['ishaq', 'isaac'], 'jacob': ['yaqub', 'jacob'],
    'joseph': ['yusuf', 'joseph'], 'aaron': ['harun', 'aaron'], 'david': ['dawud', 'david'],
    'solomon': ['sulayman', 'sulaiman', 'solomon'], 'mary': ['maryam', 'mary'], 'zechariah': ['zakariyya', 'zakariya', 'zechariah'],
    'john': ['yahya', 'john the baptist'], 'lot': ['lut', 'lot'], 'job': ['ayyub', 'job'], 'jonah': ['yunus', 'jonah'],
    'noah': ['nuh', 'noah'], 'adam': ['adam'], 'enoch': ['idris', 'enoch'], 'elijah': ['ilyas', 'elijah', 'elias'],
    'elisha': ['yasa', 'elisha'], 'ezra': ['uzayr', 'uzair', 'ezra'], 'gabriel': ['jibril', 'jibreel', 'gabriel'],
    'michael': ['mikail', 'mikal', 'michael'], 'satan': ['shaytan', 'shaitan', 'satan', 'iblis', 'devil'],
    'pharaoh': ['firawn', 'firaun', 'pharaoh'], 'korah': ['qarun', 'korah'], 'saul': ['talut', 'saul'],
    'goliath': ['jalut', 'goliath'], 'nimrod': ['namrud', 'nimrod', 'nimrud'], 'makkah': ['makkah'], 'madinah': ['madinah'],
    'jerusalem': ['jerusalem', 'bayt maqdis', 'quds', 'aqsa'], 'egypt': ['egypt', 'misr'], 'syria': ['sham', 'syria', 'levant'],
    'abyssinia': ['abyssinia', 'habashah', 'ethiopia'], 'byzantines': ['byzantine', 'romans', 'rum'],
    'jews': ['jews', 'jewish', 'yahud'], 'christians': ['christian', 'nasara', 'nazarenes'],
    'children of israel': ['children of israel', 'bani israil', 'israelites', 'banu israil'],
    'hypocrites': ['hypocrite', 'munafiq'], 'quraysh': ['quraysh', 'quraish'], 'thamud': ['thamud'], 'ad': ['people of ad', 'tribe of ad'],
    'midian': ['madyan', 'midian'], 'kabah': ['kabah', 'kaaba', 'kaba'], 'torah': ['torah', 'tawrat', 'taurat'],
    'gospel': ['gospel', 'injil', 'injeel'], 'psalms': ['psalms', 'zabur'], 'ramadan': ['ramadan'], 'hijrah': ['hijrah', 'hijra', 'migration'],
    'badr': ['badr'], 'uhud': ['uhud'], 'khandaq': ['khandaq', 'trench', 'ahzab'], 'hudaybiyyah': ['hudaybiyyah', 'hudaybiyah', 'hudaibiya'],
    'ansar': ['ansar', 'helpers'], 'muhajirun': ['muhajir', 'emigrants'], 'companions': ['companion', 'sahab'],
    'two sahihs': ['two sahihs', 'both sahihs', 'two sahih', 'sahihayn', 'bukhari and muslim', 'muslim and bukhari'],
    'salaf': ['salaf', 'early muslims', 'early scholars', 'early generations', 'earliest generations', 'first generations'],
    'shariah': ['shariah', 'sharia', 'sacred law', 'islamic law', 'revealed law'],
    'paradise': ['paradise', 'jannah', 'garden'], 'hell': ['hell', 'jahannam', 'fire'], 'resurrection': ['resurrection', 'qiyamah', 'day of judgment', 'judgement'],
    'kufr': ['kufr', 'disbelief'], 'shirk': ['shirk', 'associating partners', 'polytheism', 'idolatry'],
    'zakah': ['zakah', 'charity', 'alms'], 'salah': ['salah', 'prayer'], 'hajj': ['hajj', 'pilgrimage'], 'fasting': ['fast', 'sawm', 'siyam'],
    'quran': ['quran'], 'sunnah': ['sunnah', 'sunna'], 'hadith': ['hadith', 'report', 'narration'],
    'fatihah': ['fatihah', 'fatiha', 'opening'], 'basmalah': ['basmalah', 'bismillah'],
    'taqwa': ['taqwa', 'mindful', 'god fearing', 'god consciousness', 'piety', 'fear of allah'], 'iman': ['iman', 'faith', 'belief'],
    'ghayb': ['ghayb', 'unseen'], 'tawhid': ['tawhid', 'oneness'], 'dhikr': ['dhikr', 'remembrance'],
    'tariqah': ['tariqah', 'tariqa', 'the path'], 'dua': ['dua', 'supplication'],
}
_ALIAS_LOOKUP = {}
for canon, spellings in ALIASES.items():
    for sp in spellings:
        _ALIAS_LOOKUP[sp] = canon

TERM_LIST = """iman ihsan taqwa tawhid shirk kufr nifaq zakah salah sawm hajj umrah jihad ghayb qiblah shariah sunnah
hadith fiqh jannah jahannam barzakh qiyamah sirat mizan ruqyah shifa basmalah istiadhah tasbih tahmid takbir tahlil
dhikr wudu ghusl tayammum riba nikah talaq iddah mahr khula hudud qisas diyah shahadah mushrik munafiq kafir muttaqin
muhsin sabr shukr tawakkul tawbah istighfar rahmah barakah fitnah fitrah nafs ruh qalb hidayah ummah israiliyyat
mathani kursi arsh lawh qalam ijma qiyas ijtihad naskh mansukh muhkam mutashabih makki madani tawil
sadaqah khums ghanimah fay jizyah kharaj hijab mahram wali walimah aqiqah udhiyah qurbani ihram talbiyah tawaf say
sai wuquf jamarat halal haram makruh mandub mubah fard wajib sunnah nafl witr tahajjud qunut tashahhud ruku sujud
qiraat huruf muqattaat laylat qadr isra miraj ashura jumuah khutbah adhan iqamah mihrab minbar""".split()

NAME_PREFIX_RE = re.compile(
    r"\b((?:Ab[uūū]|Ibn|Umm|Bint|ʿAbd|'Abd|Abd|Ab[iī])\s+(?:[Aa][lstdrzn]h?-|[Aa]dh-|[Aa]th-|[Aa]sh-)?['ʿʾ`’]?[A-ZĀĪŪḤṢḌṬẒ][\w'ʿʾ`’ĀĪŪāīūḤḥṢṣḌḍṬṭẒẓ-]*"
    r"(?:\s+(?:bin|ibn|b\.)\s+['ʿʾ`’]?[A-ZĀĪŪḤṢḌṬẒ][\w'ʿʾ`’ĀĪŪāīūḤḥṢṣḌḍṬṭẒẓ-]*)?)")
ARTICLE_NAME_RE = re.compile(r"\b((?:[Aa]l|[Aa]t|[Aa]th|[Aa]d|[Aa]dh|[Aa]r|[Aa]z|[Aa]s|[Aa]sh|[Aa]n|[Ee]l)-['ʿʾ`’]?[A-ZĀĪŪḤṢḌṬẒ][\w'ʿʾ`’ĀĪŪāīūḤḥṢṣḌḍṬṭẒẓ]+)")
SAID_RE = re.compile(r"(?<![\w])(['ʿʾ`’]?[A-ZĀĪŪḤṢḌṬẒ][\w'ʿʾ`’ĀĪŪāīūḤḥṢṣḌḍṬṭẒẓ-]+(?:\s+(?:bin|ibn|b\.)\s+['ʿʾ`’]?[A-Z][\w'ʿʾ`’-]+|\s+['ʿʾ`’]?[A-Z][\w'ʿʾ`’-]+)?)\s+(?:said|says|narrated|reported|recorded|commented|stated|mentioned|related|added|explained|replied|asked)\b")
TRANSLIT_RE = re.compile(r"\b[\w'ʿʾ`’-]*[āīūḥṣḍṭẓʿʾĀĪŪḤṢḌṬẒ][\w'ʿʾ`’āīūḥṣḍṭẓ-]*\b")
XREF_RE = re.compile(r"(?<![\d:])(\d{1,3})\s?:\s?(\d{1,3})(?:\s*-\s*(\d{1,3}))?(?![\d:])")  # "68:33", "68 : 33"
NUM_RE = re.compile(r"(?<![\d:.-])(\d{2,5})(?![\d:.-])")
CHAIN_RE = re.compile(r"\b(?:narrated|reported|related|mentioned|stated|recorded)\s+(?:from|that)\b|\bsaid that\b|\bfrom\s+(?:Ab[uū]|Ibn)\b|\binformed\b|\btold\s+(?:us|me)\b", re.I)
RECORDED_RE = re.compile(r"\b(?:recorded|collected|related|reported|narrated|mentioned)\s+by\b|\bin\s+(?:his\s+|the\s+|their\s+)?(?:Sahih|Ṣaḥīḥ|Sunan|Musnad|Jami|Jāmiʿ|Mustadrak|Muwatta|Muwaṭṭaʾ|Tafsir|Tafsīr|Mujam|Muʿjam)\b", re.I)
STOP_NAMES = {fold(x) for x in """Allah He She They It This That Some Others Then The There Here Who What When Where Why How And But So
God Lord Messenger Prophet Scholars People Muslims Believers Prayer Verse Surah Quran Hadith Imam Shaykh Sheikh Companions
Companion Day Night Book Truth Thus Therefore However Also Indeed Moreover Similarly Likewise Finally First Second Third Next Now
You We I If In On At By For With As To Of Or Nor Yet Because Since While Although Though Whereas Whether Both Either Neither
Such Each Every Many Most Several Few Any All Another Other Chapter Ayah Tafsir Commentary Translation Meaning Angel Angels
Hell Paradise Fire Garden Heaven Earth Sun Moon Mercy Grace Peace Blessings Satan Devil Iblis Jews Christians Arabs
Majestic Mighty Exalted Almighty Glorified Blessed Holy Merciful Compassionate Gracious Sublime Highest Imam Imams Sayyidna""".split()}


_BANNED_NAME_RE = re.compile(r"kathir|maarif|jalalayn|jalalain|mukhtasar|qushayr|qushair|wahidi|tanwir|miqbas|tazkir|wahiduddin|mufti|muhammad shafi\b|shafi usmani")


def _is_banned_name(folded_key: str) -> bool:
    """Names of the eight works/authors are not coverage anchors: the entry
    is not allowed to say them, so missing them is not a gap."""
    return bool(_BANNED_NAME_RE.search(folded_key))


_TITLE_RE = re.compile(r"^(?:(?:Then|And|So|Thus|Also|Imam|Imām|Sayyidna|Sayyiduna|Sayyidah|Hafiz|Ḥāfiẓ|Al-Hafiz|Shaykh|Sheikh|Mawlana|Maulana|Allama|Qadi|Qāḍī|Hadrat|Hazrat|Hujjat|Sahabi|Companion)\s+)+", re.I)


def _strip_title(name: str) -> str:
    return _TITLE_RE.sub('', name).strip(" '’`")


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)


def _is_chain_name(sentence: str, m_start: int, m_end: int, names_in_sentence: list[tuple[int, int, str]]) -> bool:
    """True when the name is an intermediate link of a transmission chain
    ('A said that B narrated from C that D said …'): keep only the last name,
    and any name introduced by 'recorded by' or 'in his Sahih'."""
    if not CHAIN_RE.search(sentence) or len(names_in_sentence) < 2:
        return False
    last = max(names_in_sentence, key=lambda t: t[0])
    if (m_start, m_end) == (last[0], last[1]):
        return False
    window = sentence[max(0, m_start - 40):m_start]
    tail = sentence[m_end:m_end + 40]
    if RECORDED_RE.search(window) or re.match(r"\s+(?:recorded|collected|in his)\b", tail, re.I):
        return False
    return True


def extract_anchors(text: str) -> dict[str, str]:
    """folded key -> display form. Keys are matched against folded entries.
    Cross-references are 'xref:S:N', numbers 'num:N', everything else a name
    or term in folded spelling (or its canonical alias)."""
    anchors: dict[str, str] = {}
    # drop lines that are mostly Arabic: they are quotations the English repeats
    lines = [ln for ln in text.split('\n') if not (ln.strip() and len(ARABIC_RE.findall(ln)) > 0.5 * len(ln.strip()))]
    clean = '\n'.join(lines)
    for m in XREF_RE.finditer(clean):
        s, a = int(m.group(1)), int(m.group(2))
        if 1 <= s <= 114 and 1 <= a <= 286:
            anchors[f'xref:{s}:{a}'] = f'{s}:{a}' + (f'-{m.group(3)}' if m.group(3) else '')
    no_xref = XREF_RE.sub(' ', clean)
    for m in NUM_RE.finditer(no_xref):
        n = m.group(1)
        before = no_xref[max(0, m.start() - 1):m.start()]
        after = no_xref[m.end():m.end() + 1]
        if before == '(' or after == ')' or before == '\n' or m.start() == 0:
            continue  # footnote / list numbers
        anchors[f'num:{n}'] = n
    translit_counts: Counter = Counter(fold(t.strip("'’`-")) for t in TRANSLIT_RE.findall(no_xref))
    sentences = re.split(r'(?<=[.!?])\s+|\n+', no_xref)
    for sent in sentences:
        found: list[tuple[int, int, str]] = []
        for rx in (NAME_PREFIX_RE, ARTICLE_NAME_RE, SAID_RE):
            for m in rx.finditer(sent):
                name = m.group(1).strip(" '’`")
                if not name:
                    continue
                found.append((m.start(1), m.end(1), name))
        # dedupe overlapping spans, longest first
        found.sort(key=lambda t: (t[0], -(t[1] - t[0])))
        kept: list[tuple[int, int, str]] = []
        for s_, e_, nm in found:
            if kept and s_ < kept[-1][1]:
                continue
            kept.append((s_, e_, nm))
        for s_, e_, nm in kept:
            if _is_chain_name(sent, s_, e_, kept):
                continue
            nm = _strip_title(nm)
            key = fold(nm)
            if not key or key in STOP_NAMES or len(key) < 3:
                continue
            # 'said' pattern catches sentence-initial common words; keep only Arabic-looking ones
            if nm.lower() in {'the', 'he', 'she', 'they', 'it', 'this', 'that', 'some', 'others', 'allah', 'god'}:
                continue
            key = _ALIAS_LOOKUP.get(key, key)
            if _is_banned_name(key):
                continue
            anchors.setdefault(key, nm)
        for m in TRANSLIT_RE.finditer(sent):
            tok = m.group(0).strip("'’`-")
            key = fold(tok)
            if len(key) < 4 or key in STOP_NAMES or key.isdigit():
                continue
            if tok[:1].islower() and translit_counts.get(key, 0) < 2:
                continue  # a one-off italicised gloss, not a term the entry must carry
            key = _ALIAS_LOOKUP.get(key, key)
            if _is_banned_name(key):
                continue
            anchors.setdefault(key, tok)
    # plain-spelled technical terms and the alias table, when present in the material
    folded = ' ' + fold(no_xref) + ' '
    for term in TERM_LIST:
        if re.search(r'\b' + re.escape(term) + r'\b', folded):
            anchors.setdefault(_ALIAS_LOOKUP.get(term, term), term)
    for canon, spellings in ALIASES.items():
        for sp in spellings:
            if canon in ('hadith', 'quran', 'salah', 'zakah', 'hajj', 'fasting', 'paradise', 'hell', 'resurrection',
                         'iman', 'taqwa', 'kufr', 'shirk', 'companions', 'sunnah', 'satan', 'jews', 'christians', 'hypocrites'):
                continue  # too common to be informative on their own
            if re.search(r'(?<!abu )(?<!ibn )(?<!umm )(?<!bint )\b' + re.escape(sp) + r'\b(?! ibn )', folded):
                anchors.setdefault(canon, sp)
                break
    return anchors


@functools.lru_cache(maxsize=None)
def surah_names(surah: int) -> frozenset:
    meta = chapter_meta().get(surah, {})
    names = set()
    for raw in (meta.get('name_en', ''), meta.get('meaning', '')):
        f = fold(raw)
        if f:
            names.add(f)
            names.add(f.replace('-', ' '))
            names.add(f.replace(' ', '-'))
    return frozenset(names)


def anchor_present(key: str, folded_entry: str) -> bool:
    if key.startswith('xref:'):
        ref = key[5:]
        return re.search(r'(?<![\d:])' + re.escape(ref) + r'(?![\d])', folded_entry) is not None
    if key.startswith('num:'):
        n = key[4:]
        if re.search(r'(?<!\d)' + re.escape(n) + r'(?!\d)', folded_entry):
            return True
        return _number_words(int(n)) in folded_entry if n.isdigit() and int(n) <= 1000 else False
    spellings = ALIASES.get(key, [key])
    for sp in spellings:
        if re.search(r'\b' + re.escape(sp) + r'\b', folded_entry):
            return True
    # tolerate a different final letter (Hurayrah/Hurayra, Qatadah/Qatada)
    if len(key) >= 5 and re.search(r'\b' + re.escape(key[:-1]) + r'\w?\b', folded_entry):
        return True
    # 'ahmad ibn hanbal' is satisfied by 'ahmad', 'jabir ibn abdullah' by 'jabir',
    # 'abu jafar ibn jarir' by 'ibn jarir'
    if ' ibn ' in key:
        head = key.split(' ibn ')[0]
        if head.split()[0] not in ('abu', 'ibn', 'abd', 'umm', 'bint') and len(head) >= 4 \
                and re.search(r'\b' + re.escape(head) + r'\b', folded_entry):
            return True
        tail = 'ibn ' + key.split(' ibn ')[-1]
        if len(tail) >= 8 and re.search(r'\b' + re.escape(tail) + r'\b', folded_entry):
            return True
    return False


_SMALL = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
          'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
_TENS = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']


def _number_words(n: int) -> str:
    if n < 20:
        return _SMALL[n]
    if n < 100:
        return _TENS[n // 10] + ('' if n % 10 == 0 else ' ' + _SMALL[n % 10])
    if n < 1000:
        return _SMALL[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' ' + _number_words(n % 100))
    return 'thousand'


# --------------------------------------------------------------------------
# entry analysis
# --------------------------------------------------------------------------
def split_sections(md: str) -> tuple[str, list[tuple[str, str]]]:
    """-> (opening, [(heading, body), …])."""
    parts = re.split(r'^###\s+(.+?)\s*$', md.strip(), flags=re.M)
    opening = parts[0].strip()
    sections = []
    for i in range(1, len(parts), 2):
        sections.append((parts[i].strip(), parts[i + 1].strip() if i + 1 < len(parts) else ''))
    return opening, sections


def _norm_quote(s: str) -> str:
    s = s.replace('˹', ' ').replace('˺', ' ')
    s = re.sub(r"[^\w\s'’-]", ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


def has_translation_quote(opening: str, translation: str) -> bool:
    tw = _norm_quote(translation).split()
    ow = _norm_quote(opening)
    if not tw:
        return True
    need = min(5, len(tw))
    for i in range(0, len(tw) - need + 1):
        run = ' '.join(tw[i:i + need])
        if run in ow:
            return True
    return False


def _syllables(word: str) -> int:
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w:
        return 0
    groups = re.findall(r'[aeiouy]+', w)
    n = len(groups)
    if w.endswith('e') and not w.endswith('le') and n > 1:
        n -= 1
    return max(1, n)


def readability(text: str) -> dict:
    prose = re.sub(r'^###.*$', '', text, flags=re.M)
    prose = re.sub(r'^\s*[-\d]+[.)]?\s+', '', prose, flags=re.M)
    sentences = [s for s in re.split(r'[.!?]["”’)]*(?:\s+|$)', prose) if _words(s.lower())]
    words = _words(prose.lower())
    if not sentences or not words:
        return {'sentences': 0, 'avg_sentence': 0, 'fk_grade': 0}
    syl = sum(_syllables(w) for w in words)
    asl = len(words) / len(sentences)
    fk = 0.39 * asl + 11.8 * (syl / len(words)) - 15.59
    return {'sentences': len(sentences), 'avg_sentence': round(asl, 1), 'fk_grade': round(fk, 1)}


def _shingles(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + n]) for i in range(0, max(0, len(words) - n + 1))}


def verbatim_runs(entry: str, material: str, n: int = VERBATIM_RUN) -> list[int]:
    """Lengths of word runs the entry shares verbatim with the material,
    ignoring block quotations and the bold translation phrases."""
    body = '\n'.join(ln for ln in entry.split('\n') if not ln.lstrip().startswith('>'))
    body = re.sub(r'\*\*"[^"]*"\*\*', ' ', body)
    # a quoted Qur'an passage followed by its reference may be long: "..." (2:255) / (41:34-36)
    body = re.sub(r'"[^"\n]{0,900}"\s*\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)', ' ', body)
    body = re.sub(r'"[^"\n]{0,200}"', ' ', body)  # anything else explicitly quoted
    ew = _words(fold(body))
    mw = _words(fold(material))
    if len(ew) < n or len(mw) < n:
        return []
    ms = _shingles(mw, n)
    runs, i = [], 0
    while i <= len(ew) - n:
        if tuple(ew[i:i + n]) in ms:
            j = i + n
            while j < len(ew) and tuple(ew[j - n + 1:j + 1]) in ms:
                j += 1
            runs.append((j - i, ' '.join(ew[i:i + 8]) + '…'))
            i = j
        else:
            i += 1
    return runs


def duplication(a: str, b: str, n: int = 10) -> float:
    aw, bw = _words(fold(a)), _words(fold(b))
    sa, sb = _shingles(aw, n), _shingles(bw, n)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / min(len(sa), len(sb))


def check_markdown(md: str, kind: str) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    if re.search(r'^#{1,2}\s', md, re.M):
        errors.append('uses # or ## headings (only ### is allowed)')
    if re.search(r'<[a-zA-Z/][^>]*>', md):
        errors.append('contains HTML')
    if re.search(r'\]\(', md) or re.search(r'^\s*\|.*\|\s*$', md, re.M) or '```' in md:
        errors.append('contains a link, table or code block')
    if re.search(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$', md, re.M):
        errors.append('contains a horizontal rule')
    stripped = md.replace(SAW, '')
    if ARABIC_RE.search(stripped):
        errors.append('contains Arabic script')
    if '<<<' in md or '>>>' in md:
        errors.append('contains a stray output marker')
    if re.search(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]', md):
        warnings.append('contains an emoji or symbol')
    unquoted = re.sub(r'"[^"\n]*"|“[^”\n]*”', '', md)  # the translation may be quoted with its own dashes
    if '—' in unquoted or '–' in unquoted:
        warnings.append(f'em/en dash used {unquoted.count("—") + unquoted.count("–")}×')
    semis = len(re.findall(r';(?!\S)', unquoted))
    if semis:
        warnings.append(f'semicolon used {semis}×')
    opening, sections = split_sections(md)
    heads = [h.lower().rstrip('.:') for h, _ in sections]
    if not opening:
        errors.append('no opening paragraph before the first heading')
    if kind == 'verse':
        if 'phrase by phrase' not in heads:
            errors.append('missing "### Phrase by phrase"')
        if 'in short' not in heads:
            errors.append('missing "### In short"')
        elif heads[-1] != 'in short':
            warnings.append('"In short" is not the last section')
        for h, body in sections:
            if h.lower().rstrip('.:') == 'in short':
                bullets = [ln for ln in body.split('\n') if ln.strip().startswith(('-', '*'))]
                if len(bullets) < 2:
                    warnings.append('"In short" has fewer than two bullets')
                elif len(bullets) > 6:
                    warnings.append('"In short" has more than five bullets')
            if h.lower().rstrip('.:') == 'phrase by phrase':
                if not re.search(r'\*\*["“]', body):
                    errors.append('"Phrase by phrase" does not use bold quoted phrases')
    else:
        if 'in short' not in heads:
            warnings.append('intro has no "### In short"')
    for h, body in sections:
        if h.lower().rstrip('.:') in GENERIC_HEADINGS:
            warnings.append(f'generic heading "{h}"')
        if not body.strip():
            errors.append(f'empty section "{h}"')
        if len(h) > 110:
            warnings.append(f'very long heading "{h[:40]}…"')
    folded = ' ' + fold(md) + ' '
    for pat in BANNED:
        m = re.search(pat, folded)
        if m:
            errors.append(f'names a source or speaks as a digest: "{m.group(0).strip()}"')
            break
    digest = re.findall(r"\b(?:as we (?:saw|said|noted|mentioned|discussed|have seen|shall see|will see)|we (?:will|shall) (?:see|discuss|return|come)|let us|in this (?:entry|section|commentary)|as (?:mentioned|noted|discussed) (?:above|earlier|below))\b",
                        re.sub(r'"[^"]*"', '', md), re.I)
    if digest:
        warnings.append(f'author voice: "{digest[0]}"')
    return errors, warnings


def _skeleton(name: str) -> str:
    """Consonant skeleton of a folded name: 'ibn marduwyah' -> 'bn mrdwh'. Used only as a
    fallback so spelling variants of the same name are not reported as fabrications."""
    return ' '.join(re.sub(r'[aeiouy]', '', w) for w in name.split())


def _skeleton_set(folded_text: str) -> set[str]:
    words = folded_text.split()
    out = set()
    for i, w in enumerate(words):
        out.add(_skeleton(w))
        if i + 1 < len(words):
            out.add(_skeleton(w + ' ' + words[i + 1]))
        if i + 2 < len(words):
            out.add(_skeleton(' '.join(words[i:i + 3])))
    return out


def check_fabrication(md: str, material: str, surah: int, job_verses: list[int]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    mat_refs = set()
    for m in XREF_RE.finditer(material):
        s, a = int(m.group(1)), int(m.group(2))
        b = int(m.group(3)) if m.group(3) else a
        if 1 <= s <= 114:
            for v in range(a, min(b, a + 60) + 1):
                mat_refs.add((s, v))
    for m in XREF_RE.finditer(md):
        s, a = int(m.group(1)), int(m.group(2))
        if s == surah:
            continue
        if not (1 <= s <= 114):
            continue
        if (s, a) not in mat_refs:
            errors.append(f'cross-reference {s}:{a} is not in the material')
    fm = ' ' + fold(material) + ' '
    fe = ' ' + fold(md) + ' '
    mat_skeletons = None
    for key, display in COLLECTORS.items():
        if re.search(r'\b' + re.escape(key) + r'\b', fe) and not re.search(r'\b' + re.escape(key) + r'\b', fm):
            # transliteration variants ("Ibn Marduwyah" / "Ibn Mardawayh"): compare consonant skeletons
            if mat_skeletons is None:
                mat_skeletons = _skeleton_set(fm)
            if _skeleton(key) in mat_skeletons:
                continue
            errors.append(f'names a collector the material does not: {display}')
    for grade, spellings in GRADES.items():
        in_entry = any(re.search(r'\b' + re.escape(sp) + r'\b', fe) for sp in spellings)
        in_mat = any(re.search(r'\b' + re.escape(sp) + r'\b', fm) for sp in spellings)
        if in_entry and not in_mat:
            warnings.append(f'uses a grading the material does not ({grade})')
    return errors, warnings


def verify_entries(surah: int, entries: dict[int, str], blocks: list[dict], translations: dict[int, str],
                   intro: str | None = None, intro_context: str | None = None,
                   siblings: dict[int, str] | None = None) -> dict:
    """entries: verse -> markdown. blocks: [{source, range, verses, text}] every
    block that covers any of these verses. `intro` is verified as the surah
    introduction; `intro_context` (or `intro`) only widens the coverage union
    for blocks that open the surah. `siblings` are entries of the same surah
    written in other jobs: they are not verified, but a block that also
    covers them is matched against them too, so a block straddling two jobs
    is judged on everything written for it. A block that covers verses no
    entry exists for (an unfinished surah) is not counted for coverage.
    Returns {verses: {n: report}, intro: report|None}."""
    reports: dict[int, dict] = {}
    job_verses = sorted(entries)
    folded_entries = {v: ' ' + fold(t) + ' ' for v, t in entries.items()}
    folded_siblings = {v: ' ' + fold(t) + ' ' for v, t in (siblings or {}).items() if v not in entries}
    all_material = '\n\n'.join(b['text'] for b in blocks)

    # coverage per block, satisfied across the verses the block covers
    missing_by_verse: dict[int, list[str]] = {v: [] for v in job_verses}
    anchors_by_verse: dict[int, int] = {v: 0 for v in job_verses}
    share_words: dict[int, float] = {v: 0.0 for v in job_verses}
    partial_by_verse: dict[int, int] = {v: 0 for v in job_verses}
    intro_text = intro_context or intro
    folded_intro = ' ' + fold(intro_text) + ' ' if intro_text else ''
    for b in blocks:
        covered = [v for v in b['verses'] if v in entries]
        if not covered:
            continue
        shares = b.get('shares') or {}
        for v in covered:
            share_words[v] += float(shares.get(v, shares.get(str(v), word_count(b['text']) / max(1, len(b['verses'])))))
        unwritten = [v for v in b['verses'] if v not in entries and v not in folded_siblings]
        if unwritten:
            for v in covered:
                partial_by_verse[v] += 1
            continue
        anchors = extract_anchors(b['text'])
        union = ' '.join(folded_entries[v] for v in covered)
        union += ' '.join(folded_siblings[v] for v in b['verses'] if v in folded_siblings)
        if 1 in b['verses'] and folded_intro:
            # the opening blocks carry the surah's names, virtues and period,
            # which are written into the introduction, not into verse 1
            union += folded_intro
        for v in covered:
            anchors_by_verse[v] += len(anchors)
        own_names = surah_names(surah)
        for key, display in anchors.items():
            if key.startswith(f'xref:{surah}:') and int(key.rsplit(':', 1)[1]) in entries:
                continue  # the verse's own number
            if key in own_names:
                continue  # the surah's own name ('this surah' is enough inside it)
            if not anchor_present(key, union):
                for v in covered:
                    missing_by_verse[v].append(display)

    for v in job_verses:
        md = entries[v]
        errors, warnings = check_markdown(md, 'verse')
        opening, _ = split_sections(md)
        if not has_translation_quote(opening, translations.get(v, '')):
            errors.append('opening does not quote the translation word for word')
        e2, w2 = check_fabrication(md, all_material, surah, job_verses)
        errors += e2
        warnings += w2
        total = anchors_by_verse[v]
        missing = missing_by_verse[v]
        cov = 1.0 if total == 0 else 1 - len(missing) / total
        if cov < COVERAGE_FAIL and total >= 8:
            errors.append(f'coverage {cov:.0%}: most of the material is missing')
        elif cov < COVERAGE_FLAG:
            warnings.append(f'coverage {cov:.0%} ({len(missing)} of {total} anchors missing)')
        runs = verbatim_runs(md, all_material)
        if any(r[0] >= VERBATIM_RUN_FAIL for r in runs):
            worst = max(runs)
            errors.append(f'copies the material verbatim ({worst[0]} words in a row: "{worst[1]}")')
        elif len(runs) >= 2:
            warnings.append(f'{len(runs)} verbatim runs of {VERBATIM_RUN}+ words ("{runs[0][1]}")')
        elif runs:
            warnings.append(f'one verbatim run of {runs[0][0]} words ("{runs[0][1]}")')
        rd = readability(md)
        if rd['avg_sentence'] > 25:
            warnings.append(f'long sentences (avg {rd["avg_sentence"]} words)')
        if rd['fk_grade'] > 12:
            warnings.append(f'reading grade {rd["fk_grade"]}')
        words = word_count(md)
        ratio = words / max(1.0, share_words[v])
        if ratio < RATIO_FLAG and share_words[v] > 400:
            warnings.append(f'entry is short for its material ({words} words for ~{share_words[v]:.0f} words of material)')
        if words > PADDING_BASE + PADDING_RATIO * share_words[v]:
            warnings.append(f'entry is long for its material ({words} words for ~{share_words[v]:.0f} words of material): check for padding')
        for other in job_verses:
            if other <= v:
                continue
            d = duplication(md, entries[other])
            if d > 0.10:
                warnings.append(f'{d:.0%} of the text is duplicated in verse {other}')
        _, sections = split_sections(md)
        if share_words[v] > 700 and len(sections) <= 2:
            warnings.append('no middle sections despite substantial material')
        status = 'fail' if errors else ('flag' if warnings else 'ok')
        reports[v] = {'ref': f'{surah}:{v}', 'status': status, 'words': words, 'coverage': round(cov, 3),
                      'anchors': total, 'missing': missing[:40], 'ratio': round(ratio, 2),
                      'readability': rd, 'errors': errors, 'warnings': warnings,
                      'unjudged_blocks': partial_by_verse[v]}

    intro_report = None
    if intro is not None:
        errors, warnings = check_markdown(intro, 'intro')
        e2, w2 = check_fabrication(intro, all_material, surah, job_verses)
        errors += e2
        warnings += w2
        rd = readability(intro)
        status = 'fail' if errors else ('flag' if warnings else 'ok')
        intro_report = {'ref': f'{surah}:intro', 'status': status, 'words': word_count(intro),
                        'readability': rd, 'errors': errors, 'warnings': warnings}
    return {'verses': reports, 'intro': intro_report}


# --------------------------------------------------------------------------
# sources of entries: work/out or data/guidance
# --------------------------------------------------------------------------
@functools.lru_cache(maxsize=8)
def blocks_for_surah(surah: int) -> list[dict]:
    t = load_tafsir(surah)
    n = chapter_meta()[surah]['verses']
    chapter = load_chapter(surah)['verses']
    out = []
    for sid in SOURCE_ORDER:
        st = t['sets'].get(sid)
        if not st:
            continue
        for idx, label in enumerate(st['ranges']):
            verses = [v for v in range_verses(label) if 1 <= v <= n]
            text = clean_block(st['blocks'][idx])
            shares, intro_w, located = verse_shares(text, surah, verses, sid, chapter, label)
            out.append({'source': sid, 'range': label, 'verses': verses, 'text': text,
                        'shares': shares, 'intro_words': intro_w, 'located': located})
    return out


def collect_outputs(out_dir: str, surah: int) -> tuple[str | None, dict[int, str]]:
    """(intro, {verse: markdown}) from every successful output of the surah."""
    intro, verses = None, {}
    for path in sorted(glob.glob(os.path.join(out_dir, f'{surah:03d}', '*.json'))):
        try:
            out = read_json(path)
        except json.JSONDecodeError:
            continue
        if out.get('status') != 'ok':
            continue
        if out.get('intro'):
            intro = out['intro']
        for k, v in (out.get('verses') or {}).items():
            if v:
                verses[int(k)] = v
    return intro, verses


def load_intro_output(out_dir: str, surah: int) -> str | None:
    return collect_outputs(out_dir, surah)[0]


def verify_work(surahs: list[int], out_dir: str, jobs_dir: str, reports_dir: str) -> dict:
    summary = Counter()
    for s in surahs:
        job_path = os.path.join(jobs_dir, f'{s:03d}.json')
        if not os.path.exists(job_path):
            continue
        jobs = {j['id']: j for j in read_json(job_path)}
        translations = {int(k): v['en'] for k, v in load_chapter(s)['verses'].items()}
        surah_report = {'surah': s, 'jobs': {}, 'verses': {}, 'intro': None}
        intro_text, siblings = collect_outputs(out_dir, s)
        for path in sorted(glob.glob(os.path.join(out_dir, f'{s:03d}', '*.json'))):
            out = read_json(path)
            job = jobs.get(out['job_id'])
            if not job or out.get('status') == 'failed':
                continue
            if job['kind'] == 'intro':
                rep = verify_entries(s, {}, job['blocks'], translations, intro=out.get('intro', ''))
                surah_report['intro'] = rep['intro']
                summary[rep['intro']['status']] += 1
                continue
            entries = {int(k): v for k, v in out.get('verses', {}).items()}
            rep = verify_entries(s, entries, job['blocks'], translations, intro_context=intro_text, siblings=siblings)
            for v, r in rep['verses'].items():
                surah_report['verses'][str(v)] = r
                summary[r['status']] += 1
            surah_report['jobs'][out['job_id']] = {v: r['status'] for v, r in rep['verses'].items()}
        ensure_dir(reports_dir)
        with open(os.path.join(reports_dir, f'{s:03d}.json'), 'w', encoding='utf-8') as f:
            json.dump(surah_report, f, ensure_ascii=False, indent=1)
    return summary


def verify_data(surahs: list[int], reports_dir: str | None, data_dir: str | None = None) -> dict:
    summary = Counter()
    for s in surahs:
        path = os.path.join(data_dir or DATA, f'guidance_{s:03d}.json')
        if not os.path.exists(path):
            continue
        g = read_json(path)
        entries = {int(k): v['text'] for k, v in g.get('verses', {}).items() if v.get('text')}
        if not entries and not g.get('intro'):
            continue
        translations = {int(k): v['en'] for k, v in load_chapter(s)['verses'].items()}
        blocks = [b for b in blocks_for_surah(s) if any(v in entries for v in b['verses'])]
        rep = verify_entries(s, entries, blocks, translations, intro=g.get('intro') or None)
        for v, r in rep['verses'].items():
            summary[r['status']] += 1
            if r['status'] != 'ok':
                print(f"  {r['ref']}: {r['status']} " + '; '.join(r['errors'] + r['warnings']))
        if rep['intro']:
            summary[rep['intro']['status']] += 1
        if reports_dir:
            ensure_dir(reports_dir)
            with open(os.path.join(reports_dir, f'data_{s:03d}.json'), 'w', encoding='utf-8') as f:
                json.dump({'surah': s, 'verses': {str(k): v for k, v in rep['verses'].items()}, 'intro': rep['intro']},
                          f, ensure_ascii=False, indent=1)
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--source', choices=['work', 'data'], default='work')
    ap.add_argument('--surahs', default='all')
    ap.add_argument('--out', default=os.path.join(WORK, 'out'))
    ap.add_argument('--jobs', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--reports', default=os.path.join(WORK, 'reports'))
    ap.add_argument('--strict', action='store_true', help='exit 1 on flags as well as fails')
    ap.add_argument('--data-dir', default=DATA, help='where guidance_NNN.json files live (default data/)')
    args = ap.parse_args()
    surahs = parse_surah_selection(args.surahs)
    if args.source == 'work':
        summary = verify_work(surahs, args.out, args.jobs, args.reports)
    else:
        summary = verify_data(surahs, args.reports, args.data_dir)
    total = sum(summary.values())
    print(f'verified {total} entries: ok={summary["ok"]} flag={summary["flag"]} fail={summary["fail"]}')
    if summary['fail'] or (args.strict and summary['flag']):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
