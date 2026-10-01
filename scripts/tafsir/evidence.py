#!/usr/bin/env python3
"""Build the evidence pack the writer reads: one compact file per chapter.

    python3 scripts/tafsir/evidence.py 112                # the whole chapter
    python3 scripts/tafsir/evidence.py 2 --part 1-12      # a range of verses
    python3 scripts/tafsir/evidence.py 112 --budget 6000 # leaner
    python3 scripts/tafsir/evidence.py 112 --full         # no per-verse cap

The pack is a *reading* document, not a published one: it says which work and
which paragraph each excerpt comes from, so a claim can be traced back. The
commentary that comes out of it is the book's own voice.

How an excerpt is chosen, per work and verse:

1. the work's passage for that verse is split into paragraphs;
2. a paragraph already used anywhere in this pack (the works repeat a
   whole-surah passage under every verse) is dropped;
3. paragraphs that carry a report, a reading, an occasion of revelation, a
   ruling or a named early authority score highest; the opening paragraph is
   always kept, because that is where the work states what the verse means;
4. the work's budget is filled in order, and what was left out is listed by
   paragraph number so nothing disappears silently.

The pack also prints a ``SIGNALS`` line per verse: the collections, authorities,
readings and ruling terms the passages actually contain. It is an index, not
evidence by itself.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402

# per-work character budget for one verse (the pack's default depth)
BUDGETS = {
    "tabari": 2400,
    "qurtubi": 2400,
    "kathir": 2400,
    "uthaymeen": 1800,
    "alusi": 1600,
    "baghawi": 1400,
    "saadi": 1200,
    "maarif": 1400,
    "jalalayn": 800,
    "abbas": 700,
    "initial": 900,
}

MARKERS = {
    "report": r"روى|رَوَى|أخرج|أَخْرَجَ|أخرجه|حديث|الحديث|رواه|متفق|أثر|عن أبي|عن ابن|عن رسول|قال النبي|ﷺ|hadith|narrat|reported|Bukh|Muslim|Tirmidh|Nasa|Abu Dawud|Ibn Majah|Ahmad",
    "reading": r"قراءة|قراءات|قرأ|القراء|متواتر|شاذ|الكسائي|أبو عمرو|نافع|عاصم|حمزة|ورش|حفص|reading|recit",
    "occasion": r"نزلت|أنزلت|سبب نزول|سبب النزول|سُئل|سألوا|سألوه|asked|revealed|occasion",
    "ruling": r"حكم|أحكام|حلال|حرام|واجب|فرض|مكروه|مستحب|يجب|يجوز|لا يجوز|حرم|فقه|ruling|permissible|forbidden|lawful",
    "language": r"معنى|المعنى|لغة|اللغة|أصل|الآية|تأويل|إعراب|التفسير|أي:|meaning|root|grammar|lexic",
    "authority": r"ابن عباس|مجاهد|قتادة|الحسن|عكرمة|الضحاك|السدي|الكلبي|ابن مسعود|أبي بن كعب|أُبي|عائشة|أبو هريرة|علي بن أبي|ابن عمر|زيد بن أسلم|الربيع|شهر بن حوشب|أبو صالح|Ibn Abbas|Mujahid|Qatada|Hasan|Ikrima|Suddi|Masud|Ubayy|Aisha|Abu Hurayra",
    "crossref": r"سورة|السورة|الآية في|قوله تعالى|كما قال|surah|See |cf\.",
}

SIGNAL_TERMS = {
    "collections": r"صحيح البخاري|البخاري|صحيح مسلم|مسلم|أبو داود|أبي داود|الترمذي|النسائي|ابن ماجه|أحمد|الدارمي|مالك|الطبراني|الحاكم|ابن أبي شيبة|عبد الرزاق|Bukhari|Muslim|Tirmidhi|Nasa'i|Abu Dawud|Ibn Majah|Ahmad|Tabarani|Hakim|Darimi|Malik",
    "authorities": r"ابن عباس|مجاهد|قتادة|الحسن البصري|عكرمة|الضحاك|السدي|الكلبي|ابن مسعود|أبي بن كعب|عائشة|أبو هريرة|علي بن أبي طالب|ابن عمر|زيد بن أسلم|أبو العالية|الربيع بن أنس|Ibn 'Abbas|Ibn Abbas|Mujahid|Qatada|Ikrima|Suddi|Mas'ud|Ubayy|A'isha|Abu Hurayra",
    "readings": r"قراءة|قراءات|متواتر|شاذ|الكسائي|أبو عمرو|نافع|عاصم|حمزة|ورش|حفص",
    "rulings": r"حكم|أحكام|واجب|فرض|حرام|حلال|مكروه|مستحب|يجوز|لا يجوز",
    "occasions": r"نزلت|أنزلت|سبب نزول|سألوا|سألوه|asked",
    "hadith_refs": r"رقم|حديث رقم|صحيح|سنن|مسند",
    "cross_refs": r"﴿[\d\u0660-\u0669]+\s*:\s*[\d\u0660-\u0669]+﴾|\b\d{1,3}:\d{1,3}\b",
}

HEAD = "# Evidence pack — Sūrah {n} {name} ({verses} verses)\n"


def score(para: str, index: int, total: int) -> tuple:
    hits = []
    for kind, pattern in MARKERS.items():
        if re.search(pattern, para):
            hits.append(kind)
    weight = (
        ("report" in hits) * 4
        + ("reading" in hits) * 3
        + ("occasion" in hits) * 3
        + ("ruling" in hits) * 2
        + ("authority" in hits) * 2
        + ("language" in hits) * 1
    )
    opening = 6 if index == 0 else 0
    length = min(len(para) // 400, 3)
    return (opening + weight + length, -index)


def trim(para: str, room: int) -> tuple[str, int]:
    """Cut a paragraph to ``room`` characters at a sentence boundary."""
    if len(para) <= room:
        return para, 0
    cut = para[: room + 1]
    stops = [m.end() for m in re.finditer(r"[.!؟?]\s", cut)]
    if stops and stops[-1] > room * 0.5:
        cut = cut[: stops[-1]]
    else:
        cut = cut[:room].rsplit(" ", 1)[0]
    return cut.rstrip() + " […]", len(para) - len(cut)


def pack_chapter(n: int, lo: int, hi: int, budgets: dict[str, int], total_budget: int) -> str:
    meta = C.meta(n)
    out = [HEAD.format(n=n, name=meta["name_en"], verses=meta["verses"])]
    out.append(
        "<!-- Working document, not the book: it may name the works. Every excerpt is\n"
        "     tagged [work ¶k] with k counted from the top of that work's passage for the\n"
        "     verse. The commentary written from this pack is the book's own voice. -->\n"
    )

    sections = {key: C.source_sections(n, key) for key in C.SOURCES}
    sections["initial"] = C.source_sections(n, "initial")

    # what each work holds for the whole chapter
    coverage = ["## What the works hold\n"]
    for key in C.ORDER:
        got = sections.get(key, {})
        if not got:
            coverage.append(f"- `{key}` — **nothing for this chapter**")
            continue
        chars = sum(len(v) for v in got.values())
        missing = [v for v in range(lo, hi + 1) if v not in got]
        note = f", nothing for {', '.join(map(str, missing))}" if missing else ""
        coverage.append(f"- `{key}` — {chars:,} chars over {len(got)} verse section(s){note}")
    out.append("\n".join(coverage) + "\n")

    used: dict[str, set[str]] = {key: set() for key in C.ORDER}
    whole_surah_intro = C.initial_intro(n)

    for v in range(lo, hi + 1):
        out.append(f"\n## {n}:{v}\n")
        out.append(f"> {C.ayah_en(n, v)}\n")
        out.append(f"*Arabic:* {C.ayah_ar(n, v)}\n")
        out.append(f"`[{meta['name_en']} · {meta['meaning']} · {meta['type']} · verse {v} of {meta['verses']}]`\n")

        signals: list[str] = []
        body: list[str] = []
        spent = 0
        for key in C.ORDER:
            if key not in sections or v not in sections[key]:
                continue
            text = sections[key][v]
            if key == "initial" and len(text) > 4000:
                text = text  # kept whole: the draft's block for this verse
            paras = C.paragraphs(text)
            fresh = []
            for i, para in enumerate(paras):
                norm = C.normalise(para)
                if norm in used[key]:
                    continue
                fresh.append((i, para, norm))
            if not fresh:
                continue
            for kind, pattern in SIGNAL_TERMS.items():
                found = re.findall(pattern, text)
                if found:
                    uniq = sorted({f if isinstance(f, str) else f[0] for f in found})
                    signals.append(f"{kind}: {', '.join(uniq[:8])}")
            budget = budgets.get(key, 1200)
            room = min(budget, max(0, total_budget - spent)) if total_budget else budget
            chosen = sorted(fresh, key=lambda row: score(row[1], row[0], len(paras)), reverse=True)
            picked: list[tuple[int, str]] = []
            for i, para, norm in chosen:
                if room <= 0:
                    break
                cut, _ = trim(para, room) if len(para) > room else (para, 0)
                picked.append((i, cut))
                room -= len(cut)
                spent += len(cut)
                used[key].add(norm)
            if not picked:
                continue
            picked.sort()
            body.append(f"### {key}  ({len(picked)} of {len(paras)} paragraph(s))\n")
            for i, para in picked:
                shown = " ".join(para.split())
                body.append(f"[{key} ¶{i + 1}] {shown}\n")

        if signals:
            merged: dict[str, list[str]] = {}
            for item in signals:
                kind, _, terms = item.partition(": ")
                bucket = merged.setdefault(kind, [])
                for term in terms.split(", "):
                    if term not in bucket:
                        bucket.append(term)
            out.append(
                "**SIGNALS** — "
                + " · ".join(f"{kind}: {', '.join(terms[:10])}" for kind, terms in merged.items())
                + "\n"
            )
        if not body:
            out.append("*(no text in the ten works for this verse)*\n")
        out.extend(body)
        out.append(f"*Source text shown for this verse: {spent:,} chars.*\n")

    if whole_surah_intro:
        out.append("\n## Sūrah-level draft note (study draft, research reading only)\n")
        out.append(whole_surah_intro[:6000] + "\n")

    return "\n".join(line for line in out if line is not None) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--part", help="verse range, e.g. 1-12 (default: all)")
    ap.add_argument("--budget", type=int, default=9000, help="max chars of source text per verse (0 = no cap)")
    ap.add_argument("--work-budget", type=float, default=1.0, help="scale every per-work budget (e.g. 0.6)")
    ap.add_argument("--full", action="store_true", help="no cap at all (slow: read per verse)")
    ap.add_argument("--out", type=Path, help="write here (default tmp/evidence/NNN[_a-b].md)")
    args = ap.parse_args(argv)

    n = args.chapter
    total = C.verse_count(n)
    lo, hi = 1, total
    if args.part:
        a, _, b = args.part.partition("-")
        lo, hi = int(a), int(b or a)
    if not (1 <= lo <= hi <= total):
        ap.error(f"part {lo}-{hi} is outside 1-{total}")

    budgets = {k: int(v * args.work_budget) for k, v in BUDGETS.items()}
    total_budget = 0 if args.full else args.budget
    text = pack_chapter(n, lo, hi, budgets, total_budget)

    out = args.out
    if out is None:
        suffix = "" if (lo, hi) == (1, total) else f"_{lo}-{hi}"
        out = C.ROOT / "tmp" / "evidence" / f"{C.pad3(n)}{suffix}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    try:
        shown = out.resolve().relative_to(C.ROOT)
    except ValueError:
        shown = out
    print(f"{shown}  —  {len(text):,} chars, verses {lo}-{hi} of {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
