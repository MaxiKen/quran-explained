#!/usr/bin/env python3
"""
Layered fact-check of all 114 tafsir JSONs against ground truth in the repo.

Checks
  1. REF-EXIST   every (NNN:MMM) reference points to an existing verse
  2. QUOTE-MATCH "quoted translation (ref)" actually matches the app's
                 translation of that verse (fuzzy, sliding window, tolerant of
                 partial quotes). If it matches a NEARBY verse better, the ref
                 is likely misnumbered -> reported with the candidate.
  3. TOP-QUOTE   the verse quote at the top of each entry matches the app's
                 translation of that same verse (allows truncation).
  4. HADITH      collection+number within plausible ranges.
  5. AUTHORITY   names attributed with scholarly verbs are on a whitelist
                 (unknown names listed for review, not auto-fail).
  6. META-NUM    "N verses" style claims about surahs match reality.

Full issue list -> /tmp/factcheck_issues.json ; concise stdout summary.
"""

import json, os, re, sys, difflib
from multiprocessing import Pool

OS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(OS)

# ---------------- ground truth ----------------
def load_chapters():
    trans, counts = {}, {}
    for ch in range(1, 115):
        with open(f"data/chapter_{ch:03d}.js", encoding="utf-8") as f:
            txt = f.read()
        payload = txt[txt.index("=") + 1:].strip().rstrip(";")
        data = json.loads(payload)
        verses = {}
        for theme in data:
            for v in theme["verses"]:
                verses[int(v["ayah_no_surah"])] = v["ayah_en"]
        trans[ch] = verses
        counts[ch] = len(verses)
    return trans, counts

TRANS, COUNTS = load_chapters()

# ---------------- normalisation ----------------
def norm(t):
    t = t.replace("˹", "").replace("˺", "").replace("‘", "'").replace("’", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = re.sub(r"[^A-Za-z0-9' ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t

def best_window_ratio(qn, tn):
    """best fuzzy ratio of qn against any contiguous window of tn"""
    qw, tw = qn.split(), tn.split()
    if not qw or not tw:
        return 0.0, ""
    n = len(qw)
    best, bs = 0.0, ""
    for step in (max(1, n // 6),):
        lo = 0
        while lo < len(tw):
            hi = min(len(tw), lo + int(n * 1.35))
            window = " ".join(tw[lo:hi])
            r = difflib.SequenceMatcher(None, qn, window).ratio()
            if r > best:
                best, bs = r, window
            lo += max(step, n // 3)
    # also whole-string comparison for short verses
    r = difflib.SequenceMatcher(None, qn, tn).ratio()
    if r > best:
        best, bs = r, tn
    return best, bs

# ---------------- citation parsing ----------------
LDQ, RDQ = chr(0x201C), chr(0x201D)
QUOTE_REF = re.compile(
    "[" + LDQ + '\"]' + "([^" + LDQ + RDQ + '\"]' + "{12,420}?)['\"' + RDQ + ']'"
    + r"\s*\*{0,2}\s*\((\d{1,3}):(\d{1,3})\)")
REF = re.compile(r"\((\d{1,3}):(\d{1,3})\)")
HADITH = re.compile(
    r"(Ṣaḥīḥ|Sahih|Sunan|Jāmiʿ|Jamiʿ|Musnad|Mustadrak|Muwaṭṭa|Muwatta|Sunan Abū Dāwūd|"
    r"al-Bukhārī|Bukhārī|Muslim|al-Tirmidhī|Tirmidhī|Abū Dāwūd|Abu Dawud|al-Nasāʾī|Nasāʾī|"
    r"Ibn Mājah|Aḥmad|Aḥmad ibn Ḥanbal|al-Ḥākim|Ḥākim|al-Dārimī|al-Bayhaqī|Dārussalām)\s*(no\.?\s*)?(\d{1,5})([a-z]{1,2})?\b")
SURAHT_VERSES = re.compile(r"[Ss]ūrah\s+\d{1,3}\s+(?:has|comprises|contains|spans)\s+(\d{1,4})\s+verses|(\d{1,4})\s+verses\s+(?:long|in all|altogether)")
AUTHOR_VERB = re.compile(
    r"\b((?:al-)?[A-ZĀĪŪṢḤḌṬẒ][A-Za-zāīūṣḥḍṭẓʿʼ'āīūĀĪŪ-]{2,}(?:\s+(?:al-[A-Za-zāīūṣḥḍṭẓʿʼ-]{2,}|ibn|ibn\s+[A-ZĀĪŪ][A-Za-zāīūṣḥḍṭẓʿʼ-]+|dīn)){0,3})\s+"
    r"(reads?|said|says|notes?|noted|explains?|explained|defines?|defined|reports?|reported|counts?|counted|understands?|understood|identifies?|identified|adds?|added|observes?|observed|comments?|commented|gloss(es)?|translates?|translated|argues?|argued|holds?|held|prefers?|preferred|writes?|wrote|recorded|describes?|described|suggests?|suggested|sums?|summed|maintains?|maintained|points? out)\b")

AUTHORITIES = set("""Ibn Abbas Ibn ʿAbbās Mujāhid Mujahid Qatādah Qatadah Ḥasan al-Baṣrī Ḥasan al-Basri
Saʿīd ibn Jubayr Ikrimah ʿIkrimah al-Ḍaḥḥāk al-Dahhak al-Suddī Suddi ʿAṭāʾ Ata Ibn Masʿūd Ubayy ibn Kaʿb
Zayd ibn Thābit Abū Hurayrah Ibn ʿUmar ʿĀʾishah Aisha Anas Jābir al-Shaʿbī ʿAlī ʿUmar Abū Bakr ʿUthmān
Uthman Ḥudhayfah Abū Saʿīd al-Khudrī Abū al-Dardāʾ Ubayy Saʿd Sahl ibn Saʿd ʿImrān ibn Ḥuṣayn Buraydah
Abū Mūsā al-Ashʿarī Ibn Sirīn ʿUrwa ʿAṭāʾ ibn Abī Rabāḥ Ibrāhīm al-Nakhaʿī al-Kalbī Muqātil Abū Ṣāliḥ
al-Rabīʿ ibn Anas Saʿīd ibn al-Musayyib al-Ḥakam ʿAtiyyah al-Rabī Jaʿfar al-Ṣādiq al-Junayd Sahl al-Tustarī
Ibn ʿArabī al-Qāshānī al-Kashānī Rūzbihān al-Sulamī al-Rāzī Fakhr al-Dīn al-Rāzī al-Ṭabarī Tabari
Ibn Kathīr al-Qurṭubī Qurtubi al-Zamakhsharī Zamakhshari al-Bayḍāwī al-Wāḥidī al-Suyūṭī Suyuti Ibn ʿĀshūr
al-Ālūsī al-Alusi Ibn al-Qayyim Ibn Taymiyyah al-Ghazālī Ghazali al-Jurjānī al-Zajjāj al-Farrāʾ al-Khalīl
Sībawayh Ibn Sīdah al-Rāghib al-Iṣfahānī al-Thaʿālibī Jalālayn Ibn ʿAṭiyyah Abu al-Suʿūd al-Khāzin
al-Baghawī al-Māwardī al-Mawardi Ibn al-Jawzī al-Qushayrī al-Ṭūsī al-Tabrisī Sayyid Quṭb Sayyid Qutb
Maududi Mawdūdī Islahi Yūsuf ʿAlī Yusuf Ali Muhammad Asad Pickthall Khattab Nasr Haleem Daryabadi
Nöldeke Noldeke Wansbrough Neuwirth Bell Watt Goldziher Schacht Motzki Rippin McAuliffe Izutsu Hodgson
Hourani Rahman Cragg Murad Brown Jallad Ḥasan ʿAlawāʾ? al-Maḥallī Maḥallī Fīrūzābādī Ibn Manẓūr Ibn Fāris
al-Wāqidī Ibn Isḥāq Ibn Hishām al-Balādhurī Ibn Saʿd Masʿūdī Musaylimah Ḍaḥḥāk Mukātil Ḥumayd ʿAbd al-Razzāq
al-Khaṭṭābī? Mālik al-Shāfiʿī Abū Ḥanīfah Aḥmad ibn Ḥanbal Abū Dāwūd Nasāʾī Tirmidhī Muslim Bukhārī
ʿAbdullāh ibn ʿUmar al-Akhfash Kisaʾī? Ibn ʿĀmir? Ibn Muḥṣin? al-Kisāʾī Ibn Kathir Ṭabarī ʿAbd Allah
ʿAbdullah Zayd Thābit Musʿab Abū Lahab Abū Jahl Firʿawn Pharaoh Iblīs Jibrīl Mīkāl Isrāfīl ʿAzrāʾīl
Mūsā Moses ʿĪsā Jesus Abraham Ibrāhīm Noah Nūḥ Jonah Yūnus Elias Ilyās Idrīs Hūd Ṣāliḥ Lot Lūṭ
Yaʿqūb Yūsuf David Dāwūd Solomon Sulaymān Ayyūb Zakariyyā Yaḥyā Muḥammad Ismāʿīl Isḥāq
al-Bukhari""".split())

HADITH_RANGES = {
    "bukhari": 7563, "muslim": 8200, "tirmidhi": 3956, "abudawud": 5274,
    "nasai": 5758, "ibnmajah": 4341, "muwatta": 3000, "ahmad": 28000,
    "hakim": 8800, "darimi": 3694, "bayhaqi": 30000,
}

def hadith_ok(coll, num):
    c = coll.lower()
    for key, mx in HADITH_RANGES.items():
        if key in c:
            return 1 <= num <= mx
    return True  # unknown collection -> not range-checked

PAIR_STATS = {"pairs": 0}

def check_surah(ch):
    issues = []
    d = json.load(open(f"data/tafsir_{ch:03d}.json", encoding="utf-8"))
    blocks = [("intro", d["intro"])] + [(vn, v) for vn, v in d["verses"].items()]

    for vn, text in blocks:
        # 1+2: quote/ref pairs
        for m in QUOTE_REF.finditer(text):
            PAIR_STATS["pairs"] += 1
            quote, rs, rv = m.group(1), int(m.group(2)), int(m.group(3))
            if not (1 <= rs <= 114) or rv not in TRANS.get(rs, {}):
                issues.append(["REF-EXIST", vn, f"{rs}:{rv} does not exist", quote[:70]])
                continue
            t = norm(TRANS[rs][rv])
            qn = norm(quote)
            r, win = best_window_ratio(qn, t)
            if r < 0.55:
                # search for a better-matching verse in the same surah
                best_other, best_rv, best_r = 0.0, None, 0.0
                for cand in TRANS[rs]:
                    rr, _ = best_window_ratio(qn, norm(TRANS[rs][cand]))
                    if rr > best_r:
                        best_r, best_rv = rr, cand
                if best_r >= 0.72 and best_rv != rv:
                    issues.append(["REF-WRONG", vn, f"quote attached to {rs}:{rv} matches {rs}:{best_rv} better ({best_r:.2f} vs {r:.2f})", quote[:70]])
                else:
                    issues.append(["QUOTE-MISMATCH", vn, f"{rs}:{rv} ratio {r:.2f}", quote[:70]])
            elif r < 0.72:
                issues.append(["QUOTE-WEAK", vn, f"{rs}:{rv} ratio {r:.2f} (may be partial/paraphrase)", quote[:70]])
        # 3: top quote
        if vn != "intro" and text.startswith(">"):
            q = text.split("\n")[0][1:].strip()
            try:
                want = int(vn)
            except ValueError:
                want = None
            if want and want in TRANS[ch]:
                r, _ = best_window_ratio(norm(q), norm(TRANS[ch][want]))
                if r < 0.75:
                    issues.append(["TOP-QUOTE", vn, f"header quote vs translation ratio {r:.2f}", q[:70]])
        # 4: hadith ranges
        for m in HADITH.finditer(text):
            coll, num = m.group(1), int(m.group(3))
            if not hadith_ok(coll, num):
                issues.append(["HADITH-RANGE", vn, f"{coll} {num} outside plausible range", ""])
        # 5: authorities
        STOPWORDS = {"qur", "book", "the", "god", "they", "some", "prophet", "others",
                     "commentators", "arabic", "early", "many", "most", "readers", "allah",
                     "scholars", "exegetes", "jurists", "muslims", "arabs", "people",
                     "generations", "believers", "arab", "readerss", "he", "it", "qur",
                     "verse", "verses", "word", "words", "tradition", "traditions",
                     "commentary", "translators", "translation", "lexicons", "grammarians"}
        for m in AUTHOR_VERB.finditer(text):
            name = m.group(1)
            parts = [p.lower() for p in re.split(r"\s+", name.replace("al-", " ")) if p]
            if any(p in STOPWORDS for p in parts):
                continue
            if not any(p.casefold() in {a.casefold() for a in AUTHORITIES} for p in parts):
                issues.append(["AUTH-REVIEW", vn, name, m.group(2)])
        # 6: "N verses" claims
        for m in SURAHT_VERSES.finditer(text):
            n = int(m.group(1) or m.group(2))
            if n not in (0,) and 100 <= n <= 300 and n not in COUNTS.values():
                issues.append(["META-NUM", vn, f"claims {n} verses", ""])
    return ch, issues

def main():
    with Pool(10) as p:
        results = p.map(check_surah, range(1, 115))
    all_issues = {ch: iss for ch, iss in results}
    with open("/tmp/factcheck_issues.json", "w") as f:
        json.dump(all_issues, f, indent=1)
    # summary
    from collections import Counter
    cats = Counter()
    for ch, iss in results:
        for i in iss:
            cats[i[0]] += 1
    print("ISSUE COUNTS:", dict(cats))
    for cat in ["REF-EXIST", "REF-WRONG", "QUOTE-MISMATCH", "TOP-QUOTE", "HADITH-RANGE"]:
        print(f"\n== {cat} ==")
        shown = 0
        for ch, iss in results:
            for i in iss:
                if i[0] == cat and shown < 40:
                    print(f" S{ch}:v{i[1]}: {i[2]} | {i[3]}")
                    shown += 1
    auth = []
    for ch, iss in results:
        for i in iss:
            if i[0] == "AUTH-REVIEW":
                auth.append((ch, i[2]))
    from collections import Counter as C2
    print("\n== AUTH-REVIEW (unique names) ==")
    for name, cnt in C2(n for _, n in auth).most_common(50):
        srcs = sorted({ch for ch, n in auth if n == name})
        print(f"  {cnt:3d}x {name}  (S{srcs[:6]})")

if __name__ == "__main__":
    main()
