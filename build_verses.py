#!/usr/bin/env python3
"""
Build a {verse_number: verse_text} lookup JSON from a chapter translation file.

Usage:
    python3 build_verses.py chapter-2-al-baqarah-translation-clearquran.md verses-2.json
    python3 build_verses.py chapter-3-ali-imran-translation-clearquran.md verses-3.json

Format contract (identical for every chapter):
  * the .md file is:  <H1 title>  <source note>  ---  <body>
  * the body is split on the FIRST '---' separator; index [1] is the body
  * verse labels are matched with  (?:^|[\\s])(\\d{1,3})\\.(?=[ \\n])
  * section headings (e.g. "Precise and Elusive Verses") are stripped:
    they sit at the start of a paragraph immediately before a verse label
  * values are whitespace-normalised onto a single line, footnote markers
    and the section headings removed
  * keys are STRINGS (cast with int(k) when comparing to a verse number)
"""
import json
import re
import sys

LABEL = re.compile(r'(?:^|[\s])(\d{1,3})\.(?=[ \n])')

STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'nor', 'but', 'so', 'yet', 'for', 'of', 'to',
    'in', 'on', 'at', 'by', 'with', 'from', 'as', 'into', 'onto', 'over', 'under',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'not', 'no',
    'upon', 'about', 'after', 'against', 'before', 'between', 'during', 'through',
    'without', 'within', 'than', 'per', 'via', 'till', 'until', 'up', 'out', 'off',
    's', 't', 're', 've', 'll', 'd', 'm',
}


def is_heading(candidate: str) -> bool:
    """A section heading is short, title-cased, and does not end like a sentence."""
    h = candidate.strip()
    if not h or len(h) > 70:
        return False
    if re.search(r'[.!,”’]$', h):
        return False
    words = re.findall(r"[^\W\d_'’]+", h, re.UNICODE)
    if not words:
        return False
    for w in words:
        if w[0].isupper():
            continue
        if w.lower().strip("’'") in STOPWORDS:
            continue
        return False
    return True


def strip_trailing_heading(text: str) -> str:
    """Headings sometimes sit on the same line as the verse before them."""
    cuts = [m.end() for m in re.finditer(r'[.!?”’]\s+', text)]
    if cuts:
        tail = text[cuts[-1]:].strip()
        if is_heading(tail):
            return text[:cuts[-1]].strip()
    return text


def build(body: str) -> dict:
    matches = list(LABEL.finditer(body))
    out = {}
    for i, m in enumerate(matches):
        start = m.end()
        if i + 1 < len(matches):
            nxt = matches[i + 1]
            ps = body.rfind('\n\n', 0, nxt.start())
            ps = 0 if ps == -1 else ps + 2
            if ps > start and is_heading(body[ps:nxt.start()]):
                end = ps                      # cut before the next heading
            else:
                end = nxt.start()
        else:
            end = len(body)
        out[str(int(m.group(1)))] = strip_trailing_heading(
            re.sub(r'\s+', ' ', body[start:end]).strip()
        )
    return out


def main() -> None:
    md_path, json_path = sys.argv[1], sys.argv[2]
    body = open(md_path, encoding='utf-8').read().split('---', 1)[1]
    verses = build(body)
    nums = sorted(int(k) for k in verses)
    missing = [n for n in range(1, max(nums) + 1) if n not in set(nums)]
    dupes = [n for n in set(nums) if nums.count(n) > 1]
    assert not missing, f'missing verses: {missing}'
    assert not dupes, f'duplicate verses: {dupes}'
    with open(json_path, 'w', encoding='utf-8') as fh:
        json.dump(verses, fh, ensure_ascii=False, indent=1)
    print(f'{md_path} -> {json_path}')
    print(f'  verses: {len(verses)}  (1..{max(nums)})  missing: {missing or "none"}  duplicates: {dupes or "none"}')
    print(f'  stray U+02DD: {sum(v.count(chr(0x02DD)) for v in verses.values())}')
    print(f'  multi-line values: {sum(chr(10) in v for v in verses.values())}')


if __name__ == '__main__':
    main()
