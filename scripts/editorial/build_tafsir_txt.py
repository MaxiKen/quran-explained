#!/usr/bin/env python3
"""Clean spa5k/tafsir_api tafsir JSON into per-surah .txt files (any language).

Source : https://github.com/spa5k/tafsir_api  ->  tafsir/<slug>/N.json
Output : one folder per tafsir at the repository root, NNN.txt .. 114.txt,
         formatted exactly like tafsir-ibn-kathir/NNN.txt (same header block,
         same ## surah:ayah sections, same cleaning rules).

SRC below is a sparse checkout of spa5k/tafsir_api holding only the needed
top-level N.json files. Entries whose source dir is absent are skipped with a
note, so the script can be run against a partial checkout.

Registries
----------
English set (built earlier by build_en_tafsir_txt.py):

    tafsir-al-jalalayn          en-al-jalalayn
    tafsir-al-qushairi          en-al-qushairi-tafsir
    tafsir-asbab-al-nuzul       en-asbab-al-nuzul-by-al-wahidi   (surahs 1-77 upstream)
    tafsir-kashani              en-kashani-tafsir
    tafsir-kashf-al-asrar       en-kashf-al-asrar-tafsir         (surahs 1-69 upstream)
    tafsir-al-mukhtasar         en-tafsir-al-mukhtasar
    tafsir-al-tustari           en-tafsir-al-tustari
    tafsir-ibn-abbas            en-tafsir-ibn-abbas
    tafsir-maarif-ul-quran      en-tafsir-maarif-ul-quran
    tafsir-tazkirul-quran       en-tazkirul-quran

Arabic set — the top-10 greats and the modern heavyweights, Arabic editions
(al-Jalalayn and Fatḥ al-Qadīr both included; see build notes):

    tafsir-al-tabari            ar-tafsir-al-tabari              6,236 records (full)
    tafsir-ibn-kathir-ar        ar-tafsir-ibn-kathir             6,236 records (full)
    tafsir-al-qurtubi           ar-tafseer-al-qurtubi            6,236 records (full)
    tafsir-al-kashshaf          al-kashshaf-al-zamakhshari       6,236 records (full)
    tafsir-ad-durr-al-manthur   al-durr-al-manthur               5,284 records
    tafsir-al-baghawi           ar-tafsir-al-baghawi             6,236 records (full)
    tafsir-al-baydawi           tafsir-al-baydawi                3,811 records
    tafsir-al-alusi             tafsir-al-alusi                  6,236 records (full)
    tafsir-al-bahr-al-muhit     al-bahr-al-muhit                 6,236 records (full)
    tafsir-fath-al-qadir        fath-al-qadir-al-shawkani        6,236 records (full)
    tafsir-al-jalalayn-ar       ar-tafsir-al-jalalayn            6,010 records
    tafsir-al-wasit             ar-tafsir-al-wasit               6,236 records (full)
    tafsir-ibn-uthaymeen        tafsir-ibn-uthaymeen             3,456 records
    tafsir-tadabbur-wa-amal     tadabbur-wa-amal                 6,236 records (full)
    tafsir-abu-bakr-al-jazairi  abu-bakr-jabir-al-jazairi        6,236 records (full)
    tafsir-as-saadi             ar-tafsir-as-saadi               6,236 records (full)

(ar-tafseer-al-saddi is a separate condensed Arabic as-Sa'di abridgment from
quran.com - 6,177 records, ~6x shorter - and is deliberately not built here.)

The modern heavyweights Fi Zilal al-Quran, Maarif-ul-Quran, Bayan ul-Quran and
Tazkirul Quran have no Arabic edition upstream (Urdu/English only), so there is
nothing to build for them in this Arabic set.

Verified before cleaning: every record carries exactly the keys text / ayah /
surah and non-empty text; the files carry one record per covered ayah with
ayah numbers running 1..N once sorted numerically (upstream stores them
string-sorted: 1, 10, 100, ...). Partial works keep exactly the records the
source has; missing upstream surah files (English set only) are written as a
header plus an explicit "[No entry ...]" note so every folder holds 114 files.

Cleaning applied: CRLF->LF, control chars stripped, trailing spaces, space
runs, blank-line runs collapsed. No content altered.

--check-ik rebuilds Ibn Kathir from en-tafisr-ibn-kathir and diffs against the
committed tafsir-ibn-kathir/ to prove this pipeline stays byte-for-byte
identical to build_ik_txt.py.
"""
import json, re, pathlib, sys

SRC = pathlib.Path("/tmp/tafsir_api/tafsir")
OUT = pathlib.Path("/home/user/quran-explained")

EN_SET = {
    "tafsir-al-jalalayn":     ("TAFSIR AL-JALALAYN (English)",         "en-al-jalalayn"),
    "tafsir-al-qushairi":     ("TAFSIR AL-QUSHAIRI (English)",         "en-al-qushairi-tafsir"),
    "tafsir-asbab-al-nuzul":  ("ASBAB AL-NUZUL BY AL-WAHIDI (English)", "en-asbab-al-nuzul-by-al-wahidi"),
    "tafsir-kashani":         ("TAFSIR AL-KASHANI (English)",          "en-kashani-tafsir"),
    "tafsir-kashf-al-asrar":  ("KASHF AL-ASRAR TAFSIR (English)",      "en-kashf-al-asrar-tafsir"),
    "tafsir-al-mukhtasar":    ("TAFSIR AL-MUKHTASAR (English)",        "en-tafsir-al-mukhtasar"),
    "tafsir-al-tustari":      ("TAFSIR AL-TUSTARI (English)",          "en-tafsir-al-tustari"),
    "tafsir-ibn-abbas":       ("TAFSIR IBN ABBAS (English)",           "en-tafsir-ibn-abbas"),
    "tafsir-maarif-ul-quran": ("TAFSIR MAARIF-UL-QURAN (English)",     "en-tafsir-maarif-ul-quran"),
    "tafsir-tazkirul-quran":  ("TAZKIRUL QURAN (English)",             "en-tazkirul-quran"),
}

AR_SET = {
    "tafsir-al-tabari":           ("TAFSIR AL-TABARI (Arabic)",            "ar-tafsir-al-tabari"),
    "tafsir-ibn-kathir-ar":       ("TAFSIR IBN KATHIR (Arabic)",           "ar-tafsir-ibn-kathir"),
    "tafsir-al-qurtubi":          ("TAFSIR AL-QURTUBI (Arabic)",           "ar-tafseer-al-qurtubi"),
    "tafsir-al-kashshaf":         ("AL-KASHSHAF AL-ZAMAKHSHARI (Arabic)",  "al-kashshaf-al-zamakhshari"),
    "tafsir-ad-durr-al-manthur":  ("AD-DURR AL-MANTHUR (Arabic)",          "al-durr-al-manthur"),
    "tafsir-al-baghawi":          ("TAFSIR AL-BAGHAWI (Arabic)",           "ar-tafsir-al-baghawi"),
    "tafsir-al-baydawi":          ("TAFSIR AL-BAYDAWI (Arabic)",           "tafsir-al-baydawi"),
    "tafsir-al-alusi":            ("TAFSIR AL-ALUSI (Arabic)",             "tafsir-al-alusi"),
    "tafsir-al-bahr-al-muhit":    ("AL-BAHR AL-MUHIT (Arabic)",            "al-bahr-al-muhit"),
    "tafsir-fath-al-qadir":       ("FATH AL-QADIR AL-SHAWKANI (Arabic)",   "fath-al-qadir-al-shawkani"),
    "tafsir-al-jalalayn-ar":      ("TAFSIR AL-JALALAYN (Arabic)",          "ar-tafsir-al-jalalayn"),
    "tafsir-al-wasit":            ("TAFSIR AL-WASIT (Arabic)",             "ar-tafsir-al-wasit"),
    "tafsir-ibn-uthaymeen":       ("TAFSIR IBN UTHAYMEEN (Arabic)",        "tafsir-ibn-uthaymeen"),
    "tafsir-tadabbur-wa-amal":    ("TADABBUR WA AMAL (Arabic)",            "tadabbur-wa-amal"),
    "tafsir-abu-bakr-al-jazairi": ("ABU BAKR JABIR AL-JAZAIRI (Arabic)",   "abu-bakr-jabir-al-jazairi"),
    "tafsir-as-saadi":            ("TAFSIR AS-SAADI (Arabic)",             "ar-tafsir-as-saadi"),
}

CHECK_IK = ("TAFSIR IBN KATHIR (English)", "en-tafisr-ibn-kathir")

NAMES = {1:"Al-Fatihah",2:"Al-Baqarah",3:"Aal-Imran",4:"An-Nisa",5:"Al-Maidah",
6:"Al-Anam",7:"Al-Araf",8:"Al-Anfal",9:"At-Tawbah",10:"Yunus",11:"Hud",12:"Yusuf",
13:"Ar-Rad",14:"Ibrahim",15:"Al-Hijr",16:"An-Nahl",17:"Al-Isra",18:"Al-Kahf",
19:"Maryam",20:"Ta-Ha",21:"Al-Anbiya",22:"Al-Hajj",23:"Al-Muminun",24:"An-Nur",
25:"Al-Furqan",26:"Ash-Shuara",27:"An-Naml",28:"Al-Qasas",29:"Al-Ankabut",
30:"Ar-Rum",31:"Luqman",32:"As-Sajdah",33:"Al-Ahzab",34:"Saba",35:"Fatir",
36:"Ya-Sin",37:"As-Saffat",38:"Sad",39:"Az-Zumar",40:"Ghafir",41:"Fussilat",
42:"Ash-Shura",43:"Az-Zukhruf",44:"Ad-Dukhan",45:"Al-Jathiyah",46:"Al-Ahqaf",
47:"Muhammad",48:"Al-Fath",49:"Al-Hujurat",50:"Qaf",51:"Adh-Dhariyat",52:"At-Tur",
53:"An-Najm",54:"Al-Qamar",55:"Ar-Rahman",56:"Al-Waqiah",57:"Al-Hadid",
58:"Al-Mujadilah",59:"Al-Hashr",60:"Al-Mumtahinah",61:"As-Saff",62:"Al-Jumuah",
63:"Al-Munafiqun",64:"At-Taghabun",65:"At-Talaq",66:"At-Tahrim",67:"Al-Mulk",
68:"Al-Qalam",69:"Al-Haqqah",70:"Al-Maarij",71:"Nuh",72:"Al-Jinn",73:"Al-Muzzammil",
74:"Al-Muddaththir",75:"Al-Qiyamah",76:"Al-Insan",77:"Al-Mursalat",78:"An-Naba",
79:"An-Naziat",80:"Abasa",81:"At-Takwir",82:"Al-Infitar",83:"Al-Mutaffifin",
84:"Al-Inshiqaq",85:"Al-Buruj",86:"At-Tariq",87:"Al-Ala",88:"Al-Ghashiyah",
89:"Al-Fajr",90:"Al-Balad",91:"Ash-Shams",92:"Al-Layl",93:"Ad-Duha",94:"Ash-Sharh",
95:"At-Tin",96:"Al-Alaq",97:"Al-Qadr",98:"Al-Bayyinah",99:"Az-Zalzalah",
100:"Al-Adiyat",101:"Al-Qariah",102:"At-Takathur",103:"Al-Asr",104:"Al-Humazah",
105:"Al-Fil",106:"Quraysh",107:"Al-Maun",108:"Al-Kawthar",109:"Al-Kafirun",
110:"An-Nasr",111:"Al-Masad",112:"Al-Ikhlas",113:"Al-Falaq",114:"An-Nas"}

CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

def clean(t):
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = CTRL.sub("", t)
    t = re.sub(r"[ \t]+\n", "\n", t)          # trailing spaces
    t = re.sub(r"[ \t]{2,}", " ", t)          # runs of spaces
    t = re.sub(r"\n{3,}", "\n\n", t)          # collapse blank runs
    t = re.sub(r"^\u00a0+", "", t, flags=re.M)
    return t.strip()

def records(data):
    """Accept both upstream shapes: bare list, or {"ayahs": [...], ...}."""
    if isinstance(data, list):
        return data
    return data.get("ayahs", [])

def build_one(title, upstream, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    stats = []
    for ch in range(1, 115):
        src = SRC / upstream / f"{ch}.json"
        if src.exists():
            recs = records(json.load(open(src, encoding="utf-8")))
            recs.sort(key=lambda r: int(r["ayah"]))
            parts = [f"{title} — Surah {ch}: {NAMES[ch]}",
                     f"Source: spa5k/tafsir_api · tafsir/{upstream}/{ch}.json",
                     f"Verses: {len(recs)}", "=" * 60, ""]
            for r in recs:
                parts.append(f"## {ch}:{r['ayah']}")
                parts.append(clean(r["text"]))
                parts.append("")
        else:
            parts = [f"{title} — Surah {ch}: {NAMES[ch]}",
                     f"Source: spa5k/tafsir_api · tafsir/{upstream}/{ch}.json",
                     "Verses: 0", "=" * 60, "",
                     f"[No entry: the upstream source has no file for this surah ({upstream}/{ch}.json).]"]
        body = "\n".join(parts).rstrip() + "\n"
        (out_dir / f"{ch:03d}.txt").write_text(body, encoding="utf-8")
        stats.append((ch, sum(1 for p in parts if p.startswith("## ")), len(body)))
    return stats

def report(name, stats):
    tot_v = sum(s[1] for s in stats)
    tot_b = sum(s[2] for s in stats)
    print(f"{name:28s} surahs {len(stats):3d}  verse-sections {tot_v:5d}  size {tot_b/1024/1024:7.2f} MB", flush=True)

def check_ik():
    """Prove this pipeline reproduces tafsir-ibn-kathir/ byte-for-byte."""
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="ik_check_"))
    title, upstream = CHECK_IK
    build_one(title, upstream, tmp)
    ref = OUT / "tafsir-ibn-kathir"
    bad = [ch for ch in range(1, 115)
           if (tmp / f"{ch:03d}.txt").read_bytes() != (ref / f"{ch:03d}.txt").read_bytes()]
    print("check-ik:", "MATCH 114/114 byte-for-byte" if not bad else f"MISMATCH in {bad}")
    return not bad

def main():
    if "--check-ik" in sys.argv:
        sys.exit(0 if check_ik() else 1)
    total = 0
    for name, (title, upstream) in {**EN_SET, **AR_SET}.items():
        if not (SRC / upstream).exists():
            print(f"{name:28s} SKIPPED (source not in checkout: {upstream})")
            continue
        stats = build_one(title, upstream, OUT / name)
        report(name, stats)
        total += sum(s[2] for s in stats)
    print(f"total built                    {total/1024/1024:.2f} MB")

if __name__ == "__main__":
    main()
