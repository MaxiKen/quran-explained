#!/usr/bin/env python3
"""Build the verse-aligned source digest for one chapter.

The generation prompt (TAFSIR_PROMPT.md) says: write each verse from the
tafsir sources that discuss *that* verse, never from memory. This script
produces the material that makes that possible:

    python3 scripts/tafsir/sources.py 1                 # the eleven works, all verses
    python3 scripts/tafsir/sources.py 1 --stats         # sizes first, read second
    python3 scripts/tafsir/sources.py 1 --verse 3       # one verse
    python3 scripts/tafsir/sources.py 1 --slug tafsir-ibn-kathir --slug tafsir-al-tabari
    python3 scripts/tafsir/sources.py 1 --lang en       # English sources only

It writes two files:

    tmp/sources/NNN.txt    human-readable digest, capped per source per verse
    tmp/sources/NNN.json   {verse: {slug: text}} — uncapped, for audit --grounding

The eleven works are ``corpus.SOURCE_ALLOWLIST`` — the ten tafsirs of the
corpus plus the study draft in ``tafsir_initial/``, which since v7.2 is the
eleventh and is digested like the rest (it is read, never relayed or quoted).

Caps exist because a single Arabic source can run to tens of thousands of
characters for one ayah. The cap keeps the digest readable; raise it with
``--cap-ar`` / ``--cap-en`` when a verse needs the full discussion.

``--stats`` prints characters available per source for the chapter, sorted,
so a reader knows where the substance is before opening anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus as C  # noqa: E402


def build(chapter: int, slugs=None, verses_filter=None, lang=None):
    catalog = C.source_catalog()
    if slugs:
        wanted = set(slugs)
        catalog = [s for s in catalog if s["slug"] in wanted]
    if lang:
        catalog = [s for s in catalog if s["lang"] == lang]
    if not catalog:
        raise SystemExit("no sources selected")

    verses = [v["ayah_no_surah"] for v in C.verses(chapter)]
    if verses_filter:
        verses = [v for v in verses if v in set(verses_filter)]

    data = {str(v): {} for v in verses}
    for src in catalog:
        for v in verses:
            text = C.source_verse(src["slug"], chapter, v)
            if text:
                data[str(v)][src["slug"]] = text
    return catalog, data


def digest_text(chapter: int, catalog, data, cap_en: int, cap_ar: int):
    name = C.chapter_name(chapter)
    total = sum(len(t) for per in data.values() for t in per.values())
    out = []
    out.append("=" * 78)
    out.append("SOURCE DIGEST \u2014 S\u016brah %d (%s), %d verses, %d sources, %d chars"
               % (chapter, name, len(data), len(catalog), total))
    out.append("=" * 78)
    out.append("")
    out.append("Sources, in reading order (English first, then Arabic):")
    for i, s in enumerate(catalog, 1):
        chars = sum(len(per.get(s["slug"], "")) for per in data.values())
        out.append("  %2d. %-26s %-3s %8d chars" % (i, s["slug"], s["lang"], chars))
    out.append("")

    for v in sorted(data, key=int):
        out.append("-" * 78)
        out.append("VERSE %d:%s \u2014 CANONICAL TRANSLATION (the only wording you may quote)"
                   % (chapter, v))
        out.append(C.ayah_en(chapter, int(v)))
        out.append("-" * 78)
        for s in catalog:
            text = data[v].get(s["slug"])
            if not text:
                continue
            cap = cap_ar if s["lang"] == "ar" else cap_en
            body = text if len(text) <= cap else text[:cap].rstrip() + "\n[...truncated]"
            out.append("")
            out.append("### %s [%s]" % (s["slug"], s["lang"]))
            out.append(body)
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("chapter", type=int)
    ap.add_argument("--verse", type=int, action="append", dest="verses")
    ap.add_argument("--slug", action="append", dest="slugs")
    ap.add_argument("--lang", choices=["en", "ar"])
    ap.add_argument("--cap-en", type=int, default=2400)
    ap.add_argument("--cap-ar", type=int, default=700)
    ap.add_argument("--stats", action="store_true", help="print sizes, write nothing")
    ap.add_argument("--stdout", action="store_true", help="print the digest, write no files")
    ap.add_argument("--out", help="override the digest path")
    ap.add_argument("--cap-json", type=int, default=0,
                    help="cap each source's text in the .json digest too (0 = uncapped). "
                         "Use on long chapters: the grounding check reads names, not length.")
    args = ap.parse_args(argv)

    catalog, data = build(args.chapter, args.slugs, args.verses, args.lang)

    if args.stats:
        print("S\u016brah %d \u2014 source sizes for this chapter" % args.chapter)
        rows = []
        for s in catalog:
            chars = sum(len(per.get(s["slug"], "")) for per in data.values())
            present = sum(1 for per in data.values() if per.get(s["slug"]))
            rows.append((chars, present, s))
        for chars, present, s in sorted(rows, reverse=True, key=lambda r: r[0]):
            print("  %8d chars  %2d/%2d verses  %-26s %s"
                  % (chars, present, len(data), s["slug"], s["lang"]))
        empty = [s["slug"] for chars, present, s in rows if not chars]
        if empty:
            print("  no material: " + ", ".join(sorted(empty)))
        return 0

    if args.stdout:
        print(digest_text(args.chapter, catalog, data, args.cap_en, args.cap_ar))
        return 0

    C.TMP_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = C.TMP_DIR / "sources"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = Path(args.out) if args.out else out_dir / ("%s.txt" % C.pad3(args.chapter))
    json_path = out_dir / ("%s.json" % C.pad3(args.chapter))
    if args.cap_json:
        for per_source in data.values():
            for slug, text in list(per_source.items()):
                lang = (C.source_by_slug(slug) or {}).get("lang")
                cap = args.cap_json if lang == "en" else max(600, args.cap_json // 3)
                if len(text) > cap:
                    per_source[slug] = text[:cap]
    txt_path.write_text(digest_text(args.chapter, catalog, data, args.cap_en, args.cap_ar),
                        encoding="utf-8")
    json_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    covered = sum(1 for v in data if data[v])
    print("wrote %s (%d bytes)" % (txt_path.relative_to(C.REPO), txt_path.stat().st_size))
    print("wrote %s (%d bytes)" % (json_path.relative_to(C.REPO), json_path.stat().st_size))
    print("verses with at least one source: %d/%d" % (covered, len(data)))
    for v in sorted(data, key=int):
        if not data[v]:
            print("  no source material for %d:%s \u2014 handle from the Qur'an and the neighbouring verses"
                  % (args.chapter, v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
