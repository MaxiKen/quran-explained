#!/usr/bin/env python3
"""lexicon.py — the verse's own wording, and what counts as the same word.

The gate's match rule (TAFSIR_PROMPT.md §5.1) says the commentary explains the
wording the verse's translation carries. A word-study of a word the verse does
not have is therefore wrong — **unless the word is a synonym of one the verse
does have**. In that case the gate adjusts the comparison, keeps going, and
records the verse's own word so the writer can line the prose up with it
(``MTCH-SYNONYM``, informational). A word that is neither the verse's wording
nor a synonym of it fails (``MTCH-WORD``).

Three judgements live here, and they are not the same judgement:

* **explaining a word** — *"the word X means …"*. X may be the verse's word or a
  synonym of it; a synonym is adjusted to the verse's own word and reported as
  information, anything else fails.
* **claiming the verse's wording** — *"the verse says X"*. A claim about the
  quoted line must be true of the line: X has to be the verse's own word, not a
  synonym of it (``MTCH-TERM``).
* **mentioning a term** — an Arabic word carried as a language point with no
  study around it. Matched through its meaning it is information; unmatched it
  warns, because a term the verse does not carry has to earn its place.

Two tables carry the judgement:

``SYNONYM_GROUPS``
    English words these translations use for one meaning — *mercy / compassion /
    grace*, *path / way / road*, *reward / recompense / wage*. Kept tight on
    purpose: a loose group would let a word the verse does not carry through the
    gate, which is the failure this rule exists to catch.

``TRANSLIT_GLOSSES``
    The Qur'anic terms the eleven works transliterate, with the English the
    translations use for them — *raḥmah* → mercy, compassion, grace; *ṣirāṭ* →
    path, way, road. A language point about an Arabic term is honest only when
    its meaning is in the verse, so the term resolves through its gloss.

    python3 scripts/tafsir/match.py --chapter 1 --verse 2 "mercy" "raḥmah" "orchard"

The module also holds the light stemmer the matches run through, so that
*believeth*, *believers* and *believe* are one word.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

# --------------------------------------------------------------- word forms

# Function words carry no meaning to match, and are never headwords.
STOP = {
    "a", "an", "the", "and", "or", "but", "nor", "for", "so", "yet", "of", "to", "in", "on",
    "at", "by", "with", "from", "into", "onto", "upon", "about", "as", "than", "then", "that",
    "this", "these", "those", "it", "its", "he", "she", "they", "them", "their", "his", "her",
    "him", "you", "your", "we", "us", "our", "my", "me", "i", "is", "are", "was", "were", "be",
    "been", "being", "do", "does", "did", "has", "have", "had", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "not", "no", "yes", "if", "when", "where",
    "which", "who", "whom", "whose", "what", "how", "why", "there", "here", "also", "too",
    "very", "same", "own", "one", "two", "all", "any", "some", "both", "each", "every", "more",
    "most", "much", "many", "few", "less", "least", "other", "another", "such", "only", "just",
    "even", "still", "again", "ever", "never", "always", "often", "sometimes", "now", "thus",
}

_FOLD = {"\u02bf": "", "\u02be": "", "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
         "\u2013": "-", "\u2014": "-", "\u00a0": " "}

_SUFFIXES = ("eth", "est", "ing", "edly", "ed", "ly")


def fold(text: str) -> str:
    """Diacritics folded to plain letters: *raḥmah* → *rahmah*, *Āyah* → *Ayah*."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    for a, b in _FOLD.items():
        text = text.replace(a, b)
    return text


def norm(word: str) -> str:
    """The comparison form of a word: folded, lower case, punctuation dropped."""
    word = fold(word or "").strip()
    word = re.sub(r"^[\*\u201c\"'\u02bf\u02be-]+|[\*\u201c\"'\u02bf\u02be-]+$", "", word)
    word = word.lower()
    word = re.sub(r"[^a-z ]+", "", word)          # God's -> gods, Qur'an -> quran, al-Alusi -> alalusi
    return re.sub(r"\s+", " ", word).strip()


def forms(word: str) -> set:
    """The shapes one word may take: itself, its stem, and the variants a stem implies."""
    w = norm(word)
    if not w:
        return set()
    out = {w}
    if w.endswith("ies") and len(w) > 4:
        out.add(w[:-3] + "y")                     # mercies -> mercy
    if w.endswith("e"):
        out.add(w[:-1])
    for suffix in _SUFFIXES:
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            body = w[: -len(suffix)]
            out.add(body)
            out.add(body + "e")
            out.add(body + "y")
            if len(body) > 3 and body[-1] == body[-2]:
                out.add(body[:-1])                # running -> run
            break
    if w.endswith("es") and len(w) > 4:
        out.add(w[:-2])
    if w.endswith("s") and len(w) > 3:
        out.add(w[:-1])
    return out


def stem(word: str) -> str:
    w = norm(word)
    for suffix in _SUFFIXES:
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[: -len(suffix)]
    return w[:-1] if w.endswith("s") and len(w) > 3 else w


def content_words(text: str) -> list:
    """The words of a string that carry meaning, normalised."""
    return [norm(w) for w in re.findall(r"[A-Za-z\u0100-\u024f\u1e00-\u1eff'\u02bf\u02be-]+",
                                        text or "")
            if norm(w) and norm(w) not in STOP]


# ------------------------------------------------------- meaning: the tables
# One tuple per meaning: the words these translations use for it.
# A group is a claim that the words mean the same thing *for the verse at hand*;
# keep it tight, because a loose group is a hole in the match rule.

SYNONYM_GROUPS = (
    # --- the readers' vocabulary of the divine names and attributes
    ("mercy", "merciful", "compassion", "compassionate", "grace", "gracious", "kindness",
     "kind", "forgiving", "forgiveness", "pardon", "lenient", "clemency"),
    ("praise", "glory", "glorify", "exalt", "extol", "thanks", "thankful", "gratitude",
     "grateful", "laud", "blessed"),
    ("lord", "master", "owner", "sustainer", "provider", "patron", "sovereign", "king",
     "ruler", "authority"),
    ("god", "deity", "divine"),
    ("worship", "serve", "service", "devotion", "adore", "veneration", "worshipper"),
    ("oneness", "unity", "unique", "uniqueness", "indivisible", "single", "singleness"),
    ("power", "powerful", "might", "mighty", "almighty", "able", "capable", "omnipotent"),
    ("knowledge", "knowing", "know", "knower", "knowledgeable", "aware", "awareness",
     "learned", "inform", "informed"),
    ("wisdom", "wise", "sage", "judgement", "judgment"),
    ("truth", "true", "truthful", "truthfulness", "reality", "honest", "honesty", "verily",
     "sincere", "sincerity"),
    ("falsehood", "false", "lie", "lies", "deception", "vain", "untrue", "idle"),
    ("justice", "just", "fair", "fairness", "equity", "equitable", "judge"),
    ("wrong", "wrongdoing", "wrongdoer", "wrongdoers", "evil", "evildoer", "injustice",
     "oppression", "oppressor", "transgression", "transgressor", "sin", "sinner", "offence",
     "offense", "mischief", "corruption", "wicked", "unjust", "harm", "bad"),
    ("good", "goodness", "righteous", "righteousness", "virtue", "virtuous", "upright",
     "kindness", "excellence", "pious", "piety", "devout", "wholesome", "better"),
    ("path", "way", "road", "route", "course", "track"),
    ("straight", "right", "upright", "level", "direct", "even", "correct"),
    ("guidance", "guide", "guided", "leading", "lead", "direction", "directed", "show"),
    ("error", "astray", "straying", "misguidance", "misled", "wandering", "deviate",
     "deviation", "lost", "gone"),
    ("reward", "recompense", "return", "wage", "wages", "payment", "pay", "prize", "bounty",
     "gain", "profit", "gift"),
    ("punishment", "torment", "penalty", "retribution", "chastisement", "doom", "painful",
     "scourge", "plague", "wrath", "grievous"),
    ("fire", "flame", "flames", "blaze", "hellfire", "hell"),
    ("garden", "gardens", "paradise", "orchard", "groves", "meadow"),
    ("believe", "belief", "faith", "faithful", "believer", "believers", "trusting", "assured",
     "certainty", "convinced"),
    ("disbelieve", "disbeliever", "disbelievers", "unbeliever", "unbelievers", "unbelief",
     "deny", "denier", "deniers", "denial", "reject", "rejection", "infidel", "faithless",
     "ingrate", "ungrateful", "refuse"),
    ("hypocrite", "hypocrites", "hypocrisy", "double-faced"),
    ("polytheist", "polytheists", "polytheism", "idolater", "idolaters", "idol", "idols",
     "associate", "associating", "partners", "partner"),
    ("prophet", "prophets", "messenger", "messengers", "apostle", "envoy", "warner",
     "warner", "send"),
    ("book", "books", "scripture", "scriptures", "writing", "writings", "revelation",
     "revelations", "scroll", "scrolls", "gospel", "torah", "psalms", "quran", "recitation",
     "reading", "revealed"),
    ("sign", "signs", "verse", "verses", "miracle", "miracles", "proof", "proofs", "evidence",
     "token", "tokens", "lesson", "lessons", "portent", "mark", "marks", "indication"),
    ("heaven", "heavens", "sky", "skies", "firmament"),
    ("earth", "land", "ground", "world", "worlds", "globe"),
    ("sea", "seas", "ocean", "river", "rivers", "water", "waters", "rain", "shower", "rainfall"),
    ("people", "mankind", "humankind", "humanity", "human", "humans", "folk", "nation",
     "nations", "community", "communities", "tribe", "tribes", "generation", "generations",
     "children", "offspring", "descendants", "creatures"),
    ("soul", "souls", "self", "selves", "spirit", "spirits", "being", "creature", "person",
     "persons", "life", "lives"),
    ("heart", "hearts", "mind", "minds", "breast", "breasts", "chest", "inner"),
    ("angel", "angels", "archangel", "gabriel", "jibreel", "jibril"),
    ("satan", "devil", "devils", "shaytan", "shaitan", "tempter"),
    ("day", "days", "hour", "resurrection", "hereafter", "judgement", "judgment", "reckoning",
     "account", "accounting", "afterlife", "final", "last"),
    ("death", "die", "died", "dying", "dead", "demise"),
    ("live", "living", "alive", "livelihood", "life", "lives"),
    ("prayer", "prayers", "supplication", "invocation", "call", "calling", "plea"),
    ("charity", "alms", "almsgiving", "giving", "spend", "spending", "expend", "donation",
     "zakat", "sadaqah"),
    ("fast", "fasting", "fasts", "abstain", "abstinence"),
    ("pilgrimage", "hajj", "pilgrim", "pilgrims", "kaaba", "kabah", "makkah", "mecca"),
    ("lawful", "permissible", "allowed", "halal", "legitimate", "clean", "pure", "purify",
     "purified", "cleanse", "cleansed"),
    ("forbidden", "unlawful", "prohibited", "haram", "illicit", "sacred", "inviolable",
     "impure", "foul"),
    ("marriage", "marry", "married", "wedlock", "spouse", "spouses", "wife", "wives",
     "husband", "husbands", "nikah"),
    ("divorce", "divorced", "separation", "separate", "parting", "parting"),
    ("inheritance", "inherit", "heir", "heirs", "legacy", "estate", "will", "bequest"),
    ("interest", "usury", "riba", "usurious"),
    ("covenant", "pledge", "pact", "agreement", "contract", "bond", "oath", "oaths", "promise",
     "promises", "treaty", "charter", "swear", "swore", "vow", "vows"),
    ("patience", "patient", "perseverance", "persevere", "endurance", "endure", "steadfast",
     "steadfastness", "constant", "persistent", "forbearance"),
    ("fear", "afraid", "dread", "awe", "terror", "reverence", "wary", "conscious",
     "godconsciousness", "piety", "godfearing", "taqwa", "cautious"),
    ("provision", "sustenance", "livelihood", "supply", "supplied", "sustains", "sustaining",
     "sustained", "food", "blessing", "blessings", "favour", "favours", "favor", "favors",
     "bounty", "prosperity", "abundance", "riches", "wealth", "riches"),
    ("enemy", "enemies", "foe", "foes", "adversary", "opponent", "rival"),
    ("friend", "friends", "ally", "allies", "companion", "companions", "protector",
     "protectors", "guardian", "guardians", "helper", "helpers", "supporter", "supporters",
     "close", "loved"),
    ("trust", "reliance", "rely", "depend", "dependence", "confidence", "entrust",
     "trustworthy", "loyal", "reliable"),
    ("decree", "destiny", "fate", "measure", "measured", "ordain", "ordained", "predestine",
     "predestined", "willed", "determine", "determined", "portion", "appointed", "term"),
    ("forgive", "forgiving", "pardon", "pardoner", "absolve", "merciful", "mercy", "remit"),
    ("repent", "repentance", "penitent", "turning", "turn", "return", "returning", "remorse",
     "tawbah"),
    ("remember", "remembrance", "reminder", "mention", "mindful", "commemorate", "recall",
     "dhikr"),
    ("obey", "obedience", "obedient", "submit", "submission", "submissive", "surrender",
     "comply", "follow", "follower", "followers"),
    ("dispute", "disputes", "disputing", "argument", "argue", "quarrel", "differ", "difference",
     "disagreement", "contention", "controversy"),
    ("understand", "understanding", "perceive", "comprehend", "grasp", "insight"),
    ("help", "helps", "helper", "helpers", "aid", "assist", "assistance", "support", "succour",
     "succor", "relief", "rescue", "deliver", "deliverance", "salvation", "save", "saviour",
     "savior", "saved"),
    ("command", "commands", "order", "orders", "enjoin", "ordain", "directive", "instruction",
     "instructions", "instruct", "rule", "ruling", "prohibition", "forbidding"),
    ("create", "creator", "created", "creation", "make", "maker", "made", "fashion", "form",
     "formed", "mould"),
    ("give", "gives", "given", "grant", "granted", "bestow", "bestowed", "offer", "offered",
     "provide", "provided", "supply", "present"),
    ("hear", "hears", "hearing", "listener", "listens", "listen", "ear", "ears"),
    ("see", "sees", "seeing", "seer", "sight", "seen", "observe", "observes", "witness",
     "witnesses", "behold", "perceive", "vision", "visible"),
    ("speak", "speaks", "spoke", "speech", "say", "says", "said", "saying", "word", "words",
     "utterance", "declare", "declares", "declared", "proclaim", "proclaims", "tell", "told",
     "tells", "announce", "announces", "recite", "recites", "recited", "recitation", "call"),
    ("write", "writes", "written", "writing", "writings", "scribe", "inscribe", "inscribed",
     "prescribe", "prescribed", "pen", "pens", "record", "recorded", "register", "tablet",
     "tablets"),
    ("relate", "relates", "related", "narrate", "report", "reports", "reported", "narration"),
    ("test", "tests", "tested", "trial", "trials", "try", "tried", "temptation", "tempt",
     "tempted", "affliction", "hardship", "hardships", "difficulty", "persecution", "discord",
     "misery"),
    ("warn", "warns", "warned", "warning", "warnings", "caution", "admonish", "admonition",
     "admonishes", "alert", "warner"),
    ("glad", "tidings", "goodnews", "annunciation", "gospel"),
    ("curse", "cursed", "curses", "accursed", "damned", "condemn", "condemned", "banishment",
     "expelled"),
    ("gather", "gathered", "gathering", "assemble", "assembled", "assembly", "collect",
     "collected", "congregation", "muster", "marshalled", "brought"),
    ("divide", "divided", "division", "distinguish", "distinguished", "sort", "sorted",
     "part", "parts"),
    ("scale", "scales", "balance", "balances", "weight", "weights", "weigh", "weighed"),
    ("intercede", "intercession", "intercessor", "plead", "pleading", "advocate"),
    ("humble", "humility", "humbled", "lowly", "meek", "modest", "modesty"),
    ("poor", "poverty", "needy", "destitute", "indigent", "beggar", "beggars", "orphan",
     "orphans", "fatherless", "widow", "widows"),
    ("slave", "slaves", "servant", "servants", "bond", "bondman", "bondwoman", "maid",
     "captive", "captives"),
    ("wine", "intoxicants", "intoxicant", "drink", "drinks", "intoxication", "gamble",
     "gambling", "lottery", "wager"),
    ("jinn", "jinns", "demon", "demons", "spirits"),
    ("throne", "thrones", "seat", "chair", "dais"),
    ("parable", "parables", "similitude", "likeness", "example", "examples", "metaphor"),
    ("clear", "clarify", "clarified", "explain", "explained", "explanation", "manifest",
     "evident", "plain", "obvious", "distinct", "explicit", "detail", "detailed", "clarity"),
    ("weak", "weakness", "feeble", "frail", "helpless", "powerless"),
    ("strong", "strength", "force", "firm", "steadfast", "solid"),
    ("light", "illumination", "radiance", "glow"),
    ("darkness", "darknesses", "dark", "gloom"),
    ("love", "loves", "loving", "beloved", "affection", "fond"),
    ("mercy", "compassion", "grace", "kindness", "gentleness", "benevolence", "goodwill"),
)

# The Arabic the eleven works transliterate, with the English the translations use.
TRANSLIT_GLOSSES = {
    "allah": {"allah", "god"},
    "rabb": {"lord", "master", "sustainer", "owner"},
    "rahma": {"mercy", "compassion", "grace", "kindness"},
    "rahman": {"compassionate", "merciful", "gracious"},
    "rahim": {"merciful", "compassionate"},
    "malik": {"king", "master", "owner", "sovereign", "lord"},
    "yawm": {"day"},
    "din": {"religion", "judgement", "judgment", "faith", "way"},
    "sirat": {"path", "way", "road"},
    "mustaqim": {"straight", "right", "upright", "direct"},
    "iman": {"faith", "belief", "believe"},
    "islam": {"submission", "surrender", "peace"},
    "muslim": {"submitting", "submit", "muslim", "muslims"},
    "kufr": {"disbelief", "denial", "ingratitude"},
    "kafir": {"disbeliever", "disbelievers", "unbeliever", "denier", "disbelieve"},
    "mushrik": {"polytheist", "polytheists", "idolater", "idolaters", "associate"},
    "munafiq": {"hypocrite", "hypocrites", "hypocrisy"},
    "mumin": {"believer", "believers", "faithful"},
    "salat": {"prayer", "prayers", "worship"},
    "zakah": {"charity", "alms", "almsgiving"},
    "sawm": {"fasting", "fast"},
    "hajj": {"pilgrimage", "hajj"},
    "sabr": {"patience", "patient", "perseverance", "steadfast"},
    "shukr": {"gratitude", "thankful", "thanks", "grateful"},
    "hamd": {"praise", "thanks"},
    "taqwa": {"piety", "godconsciousness", "righteousness", "fear", "wary", "conscious"},
    "ilm": {"knowledge", "knowing", "know"},
    "hikma": {"wisdom", "wise", "judgement"},
    "haqq": {"truth", "right", "true", "justly"},
    "batil": {"falsehood", "false", "vain"},
    "adl": {"justice", "just", "fair"},
    "zulm": {"wrongdoing", "injustice", "wrong", "oppression", "evil"},
    "zalim": {"wrongdoer", "wrongdoers", "unjust", "evildoer", "oppressor"},
    "aym": {"sign", "signs", "verse", "verses", "miracle"},
    "ayat": {"signs", "verses", "revelations", "miracles"},
    "aya": {"sign", "verse", "miracle"},
    "kitab": {"book", "scripture", "writing"},
    "quran": {"quran", "recitation", "reading"},
    "wahy": {"revelation", "inspiration", "revealed"},
    "rasul": {"messenger", "messengers", "apostle"},
    "nabi": {"prophet", "prophets"},
    "akhira": {"hereafter", "afterlife", "final"},
    "qiyama": {"resurrection", "rising", "judgement", "judgment"},
    "jannah": {"paradise", "garden", "gardens"},
    "jahannam": {"hell", "hellfire", "fire"},
    "nar": {"fire", "flame", "blaze"},
    "malaika": {"angels", "angel"},
    "shaytan": {"satan", "devil", "shaytan"},
    "jinn": {"jinn", "spirits", "demons"},
    "nafs": {"soul", "self", "selves", "life"},
    "qalb": {"heart", "hearts"},
    "rizq": {"provision", "sustenance", "livelihood"},
    "nima": {"blessing", "favour", "favor", "grace"},
    "ajr": {"reward", "wage", "wages", "recompense"},
    "thawab": {"reward", "recompense"},
    "adhab": {"punishment", "torment", "penalty"},
    "hisab": {"reckoning", "account", "accounting"},
    "mizan": {"scales", "balance", "weight"},
    "shafaa": {"intercession", "intercede"},
    "tawba": {"repentance", "turning", "return"},
    "dhikr": {"remembrance", "reminder", "mention"},
    "dua": {"supplication", "call", "prayer", "invocation"},
    "huda": {"guidance", "guide", "leading"},
    "dalal": {"error", "straying", "misguidance", "astray"},
    "ghayb": {"unseen", "hidden", "secret"},
    "arsh": {"throne"},
    "kursi": {"throne", "seat", "chair"},
    "sama": {"heaven", "sky", "heavens"},
    "ard": {"earth", "land", "ground"},
    "insan": {"human", "man", "humanity", "mankind"},
    "nas": {"people", "mankind", "humanity"},
    "qawm": {"people", "nation", "folk"},
    "umma": {"community", "nation", "people"},
    "wali": {"protector", "ally", "guardian", "friend"},
    "ahd": {"covenant", "pledge", "promise"},
    "mithaq": {"covenant", "pledge", "agreement"},
    "amana": {"trust", "faithfulness"},
    "fitna": {"trial", "test", "persecution", "temptation", "discord"},
    "jihad": {"striving", "struggle", "strive"},
    "riba": {"interest", "usury"},
    "sadaqa": {"charity", "alms"},
    "infaq": {"spending", "spend"},
    "halal": {"lawful", "permissible", "allowed"},
    "haram": {"forbidden", "unlawful", "prohibited", "sacred"},
    "tayyib": {"good", "wholesome", "pure", "clean"},
    "khabith": {"evil", "impure", "foul"},
    "nur": {"light"},
    "zulumat": {"darkness", "darknesses"},
    "hayah": {"life", "living"},
    "mawt": {"death", "dead", "die"},
    "shirk": {"polytheism", "associating", "partners"},
    "tawhid": {"oneness", "unity"},
    "ikhlas": {"sincerity", "purity", "devotion"},
    "tawakkul": {"trust", "reliance", "dependence"},
    "ihsan": {"excellence", "goodness", "kindness"},
    "birr": {"righteousness", "goodness", "piety"},
    "fasad": {"corruption", "mischief"},
    "qist": {"justice", "equity", "fairness"},
    "shura": {"consultation", "counsel"},
    "sunnah": {"way", "practice", "path"},
    "khalq": {"creation", "created", "create"},
    "bath": {"resurrection", "raising"},
    "sidq": {"truth", "truthfulness", "honesty"},
    "hilm": {"forbearance", "patience", "gentleness"},
    "raffa": {"kindness", "compassion", "mercy"},
    "hubb": {"love", "loves", "loving"},
    "khawf": {"fear", "afraid", "dread"},
    "khushu": {"humility", "devotion", "reverence"},
    "tasbih": {"glorification", "glory", "praise"},
    "qadar": {"decree", "destiny", "measure"},
    "qada": {"decree", "judgement", "judgment", "decision"},
    "hukm": {"judgement", "judgment", "ruling", "rule", "command"},
    "amr": {"command", "order", "matter", "affair"},
    "bayan": {"clarity", "explanation", "clear"},
    "burhan": {"proof", "evidence"},
    "hujja": {"proof", "argument", "evidence"},
    "bayyina": {"proof", "evidence", "clear"},
    "basira": {"insight", "vision"},
    "fitra": {"nature", "disposition", "innate"},
    "ruh": {"spirit", "soul", "revelation"},
    "sadr": {"breast", "chest"},
    "ayn": {"eye", "eyes", "spring"},
    "yad": {"hand", "hands"},
    "wajh": {"face", "countenance"},
    "lisan": {"tongue", "language"},
    "qalam": {"pen"},
    "lawh": {"tablet", "tablets"},
    "mulk": {"kingdom", "dominion", "sovereignty"},
    "sultan": {"authority", "power"},
    "izza": {"might", "honour", "honor", "glory"},
    "baraka": {"blessing", "blessings"},
    "khayr": {"good", "goodness", "better"},
    "sharr": {"evil", "bad", "harm"},
    "dunya": {"world", "worldly", "life"},
    "ajal": {"term", "appointed", "destined"},
    "fiqh": {"understanding", "jurisprudence"},
    "tafsir": {"explanation", "interpretation", "commentary"},
    "asbab": {"reasons", "causes", "occasions"},
    "nuzul": {"revelation", "revealing", "descent"},
    "hadith": {"report", "reports", "saying", "narration"},
    "athar": {"report", "reports", "narration"},
    "isnad": {"chain", "chains"},
}

# The pipeline's own vocabulary: naming one of these is not a word-study of the verse.
CORPUS_TERMS = {"tafsir", "surah", "surahs", "ayah", "ayahs", "ayat", "hadith", "hadiths",
                "athar", "isnad", "sanad", "mushaf", "juz", "asbab", "nuzul",
                "qiraat", "islam", "muslim", "muslims",
                # the disjoint letters that open some sūrahs (Alif-Lãm-Mĩm and the like)
                # are the verses' own wording, not Arabic carried beside an English verse
                "aliflammim", "alif", "lam", "mim"}

# Proper names a chapter's prose is full of: places, people, months, festivals. Naming
# one of these is never a word-study of the verse, so the match rule does not judge it.
NAMEY = {
    "makkah", "mecca", "madinah", "medina", "badr", "uhud", "khandaq", "trench", "arafat",
    "arafah", "mina", "muzdalifah", "safa", "marwa", "kaaba", "kabah", "jerusalem", "sinai",
    "tur", "tursina", "egypt", "babylon", "yathrib", "taif", "hunayn", "khaybar", "tabuk",
    "syria", "shaam", "yemen", "persia", "rome", "abyssinia", "habasha", "najran", "taiif",
    "adam", "nuh", "noah", "ibrahim", "abraham", "ismail", "ishmael", "ishaq", "isaac",
    "yaqub", "jacob", "yusuf", "joseph", "musa", "moses", "harun", "aaron", "dawud", "david",
    "sulayman", "solomon", "ayyub", "job", "yunus", "jonah", "lut", "lot", "isa", "jesus",
    "maryam", "mary", "zakariyya", "zachariah", "yahya", "john", "ilyas", "elijah", "alyasa",
    "elisha", "dhulkifl", "idris", "enoch", "hud", "salih", "shuayb", "jethro", "talut",
    "saul", "dhulqarnayn", "firaun", "pharaoh", "haman", "qarun", "korah", "iblis", "jibril",
    "gabriel", "jibreel", "mikail", "michael", "israfil", "azrail", "harut", "marut",
    "abu", "bakr", "umar", "uthman", "ali", "hamza", "bilal", "khadijah", "aisha", "fatimah",
    "ramadan", "shawwal", "muharram", "rajab", "shaban", "safar", "rabi", "jumada", "dhul",
    "qadah", "hijjah", "ashura", "qibla", "qiblah", "hira", "thawr", "quba", "ridwan",
}

# The commentators' names, as a sentence may carry them: a bare surname is still a name.
SCHOLAR_SURNAMES = {"kathir", "kathir", "tabari", "tabaris", "qurtubi", "qurtubis", "baghawi",
                    "baghawis", "alusi", "alusi", "saadi", "saadis", "uthaymeen", "uthaymin",
                    "jalalayn", "mahalli", "suyuti", "raghib", "zamakhshari", "baydawi",
                    "shawkani", "qushayri", "tustari", "kashani", "mukhtasar", "hikmat",
                    "hurayrah", "abbas", "masud", "abbas", "khuzaymah", "hibban", "tirmidhi",
                    "bukhari", "muslim", "nasai", "dawud", "majah", "ahmad", "hanifah"}

# ---- names: a sūrah's name is not a word-study -------------------------------

SURAH_NAMES = set()
for _n in C.chapter_numbers():
    try:
        for _w in re.findall(r"[a-z]+", fold(C.chapter_name(_n)).lower()):
            if len(_w) > 2:
                SURAH_NAMES.add(_w)          # Al-Baqarah -> baqarah; Al-Ikhlas -> ikhlas
    except Exception:                        # pragma: no cover - a name that will not resolve
        continue

# --------------------------------------------------------------- the lookups

_GROUPS = [{norm(w) for w in group if norm(w)} for group in SYNONYM_GROUPS]

_SYN_INDEX = {}
for _i, _group in enumerate(_GROUPS):
    for _w in _group:
        _SYN_INDEX.setdefault(_w, set()).add(_i)

_TERMS = {}
for _term, _glosses in TRANSLIT_GLOSSES.items():
    _key = norm(_term)
    _meanings = {norm(g) for g in _glosses if norm(g)}
    for _variant in {_key, _key + "h", _key.rstrip("h"), _key.replace("a", "aa")}:
        if _variant:
            _TERMS.setdefault(_variant, set()).update(_meanings)
_GLOSS_TO_TERMS = {}
for _term, _glosses in _TERMS.items():
    for _g in _glosses:
        _GLOSS_TO_TERMS.setdefault(_g, set()).add(_term)


def synonyms(word: str) -> set:
    """Every word the tables treat as the same meaning as this one (one hop wide)."""
    keys = forms(word) | {norm(word)}
    out = set()
    for key in keys:
        for i in _SYN_INDEX.get(key, ()):
            out |= _GROUPS[i]
        out |= _TERMS.get(key, set())
        for term in _GLOSS_TO_TERMS.get(key, ()):
            out.add(term)
    for word_ in list(out):                  # one further hop, through the other table
        for key in forms(word_) | {norm(word_)}:
            out |= _TERMS.get(key, set())
            for term in _GLOSS_TO_TERMS.get(key, ()):
                out.add(term)
    out.discard(norm(word))
    return {w for w in out if w}


def is_name(word: str) -> bool:
    """A proper name — a sūrah's name, a place, a person, a scholar — is not a word-study."""
    tokens = re.findall(r"[a-z]+", fold(word or "").lower())
    if not tokens:
        return True
    if norm(word) in SURAH_NAMES or any(t in SURAH_NAMES for t in tokens):
        return True
    if all(t in NAMEY or t in SCHOLAR_SURNAMES or t in CORPUS_TERMS for t in tokens):
        return True
    return len(tokens) == 1 and tokens[0] in SCHOLAR_SURNAMES


def verse_index(verse_text: str) -> dict:
    """``form -> (kind, the verse's own word)`` for everything the verse carries.

    ``kind`` is ``"word"`` for the verse's own wording and ``"synonym"`` for a word
    these tables give the same meaning as one the verse has. The verse's own words
    are registered first, so *Judgment* is always *Judgment* and never *day*.
    """
    index, words = {}, content_words(verse_text)
    for word in words:
        for form in forms(word) | {word}:
            index.setdefault(form, ("word", word))
    for word in words:
        for syn in synonyms(word):
            for form in forms(syn) | {syn}:
                index.setdefault(form, ("synonym", word))
    return index


def lookup(word: str, index: dict):
    """``(kind, verse_word)`` — how the verse carries this word, if it does.

    ``kind`` is ``"word"`` (the verse's own wording), ``"synonym"`` (the same
    meaning, written differently — adjust and continue) or ``None`` (not the
    verse's wording at all).
    """
    for key in ({norm(word)} | forms(word)):
        if key in index:
            return index[key]
    return (None, None)


def _positions(verse_words: list, wanted: list):
    """The verse's own words, in verse order, that answer a list of matched words."""
    span, cursor = [], 0
    for word in wanted:
        found = None
        for i in range(cursor, len(verse_words)):
            if verse_words[i] == word:
                found = i
                break
        if found is None:                     # the same word may repeat; take the first left
            for i, w in enumerate(verse_words):
                if w == word:
                    found = i
                    break
        if found is None:
            return None
        span.append(found)
        cursor = found + 1
    return span


def _verse_phrase(verse_text: str, words: set):
    """The shortest phrase of the verse that carries all of these words — what the verse says."""
    if not words:
        return ""
    best = None
    for phrase in C.split_phrases(verse_text) or [verse_text]:
        present = set(content_words(phrase))
        if words <= present and (best is None or len(present) < len(best[1])):
            best = (phrase, present)
    return C.loose_norm(best[0]) if best else ""


def match_head(head: str, verse_text: str, index: dict = None):
    """``(kind, verse_wording, verse_phrase)`` for a word or a *phrase* the prose holds up.

    A headword is the verse's own wording when its words — a synonym of it when
    every word of the head is one the verse carries, directly or by meaning, and
    in verse order. Anything else is not the verse's wording at all. The second
    element is what the verse actually says, so the gate can tell the writer
    which words to line the sentence up with.

    The same judgement covers a phrase: *"the day of reckoning"* is a synonym of
    the verse's *"the Day of Judgment"* — different words, one meaning — while
    *"the day of the harvest"* is neither.
    """
    hnorm = norm(head)
    if not hnorm:
        return ("word", "", "")
    verse_words = content_words(verse_text)
    if hnorm in C.loose_norm(verse_text):
        return ("word", hnorm, _verse_phrase(verse_text, set(content_words(head))) or hnorm)
    index = verse_index(verse_text) if index is None else index
    wanted, kinds = [], []
    for word in content_words(head):
        kind, verse_word = lookup(word, index)
        if kind is None:
            return (None, None, None)
        wanted.append(verse_word)
        kinds.append(kind)
    if not wanted:
        return ("word", "", "")
    unique = [w for i, w in enumerate(wanted) if i == 0 or w != wanted[i - 1]]
    span = _positions(verse_words, unique)
    if span is None:
        return (None, None, None)             # the words are there, the verse does not say them so
    wording = " ".join(verse_words[i] for i in span)
    phrase = _verse_phrase(verse_text, set(unique)) or wording
    if norm(phrase) == norm(verse_text):
        phrase = wording
    if all(k == "word" for k in kinds) and norm(phrase) == hnorm:
        return ("word", phrase, phrase)
    return ("synonym", wording, phrase)


def analyse(head: str, verse_text: str, index: dict = None, skip=None):
    """``(unmatched, adjusted)`` for a headword against a verse.

    ``unmatched`` — words the verse does not carry in any form, or by any synonym:
    the failures. ``adjusted`` — ``(word used, the verse's own word)``: the same
    meaning written differently, which the prose should line up with the verse.
    ``skip`` is an optional predicate for words the caller does not want judged
    (proper names, the works of the eleven).
    """
    index = verse_index(verse_text) if index is None else index
    unmatched, adjusted = [], []
    for word in content_words(head):
        if is_name(word) or (skip and skip(word)):
            continue
        kind, verse_word = lookup(word, index)
        if kind is None:
            unmatched.append(word)
        elif kind == "synonym" and norm(word) != norm(verse_word):
            adjusted.append((word, verse_word))
    return unmatched, adjusted


def glosses(word: str) -> set:
    """The English meanings the tables hold for an Arabic term (or an English word)."""
    out = set()
    for key in forms(word) | {norm(word)}:
        out |= _TERMS.get(key, set())
    return out
