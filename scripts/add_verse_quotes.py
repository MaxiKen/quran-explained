#!/usr/bin/env python3
"""
Give every Qur'an cross-reference in the commentary the actual wording it is
there for.

Today most citations are bare:

    ... belief in *jibt* and *ṭāghūt* (4:51)

The reader has no way to know why 4:51 was cited. This script attaches the
relevant part of the verse, lifted verbatim from the translation the app itself
ships (`ayah_en` in `data/chapter_NNN.js`):

    ... belief in *jibt* and *ṭāghūt* (4:51 — *“…yet believe in idols and false
    gods…”*)

Long verses are not dumped whole: the picker finds the sentence of the verse
that the surrounding commentary is actually talking about. References that
already carry their wording are left alone, so the script is safe to re-run.

    python3 scripts/add_verse_quotes.py --report           # counts only
    python3 scripts/add_verse_quotes.py --preview 10       # before/after
    python3 scripts/add_verse_quotes.py --apply            # write markdown
    python3 scripts/add_verse_quotes.py --apply --format before

Then: python3 scripts/build_tafsir_json.py
"""

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from verse_quotes import (BOOK_REF, CORPUS, clean_quote, expand_end,
                          load_translation, norm, pick_quote)

TOKEN = r"\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?"
# (4:51)  (4:51-52)  (2:86; 3:77)  — group(2) is any trailing prose in the paren
PAREN = re.compile(r"\((" + TOKEN + r"(?:\s*[,;]\s*" + TOKEN + r")*)([^()]*)\)")
# a partial range must never match on its own: 53:36 inside 53:36–37
NAKED = re.compile(r"(?<![\d:(–-])(" + TOKEN + r")(?!\d|[–-]\d)")
SENT_END = re.compile(r"[.!?][\"”\)]?[\s]|$")
QUOTEISH = re.compile(r"[“”\"‘’]")

PRE_QUOTED = re.compile(r'["”]\*{0,2}\s*$')
SHORT_TRAILING = 45


class Report:
    def __init__(self):
        self.filled = 0
        self.already = 0
        self.self_ref = 0
        self.duplicate = 0
        self.invalid = 0
        self.whole_verse = 0
        self.prose_paren = 0
        self.complex_paren = 0
        self.naked = 0
        self.bible = 0
        self.samples = []

    def dump(self, fmt, applied):
        print(f"\nreferences given wording ............ {self.filled}")
        print(f"  ...of which the whole verse was used {self.whole_verse}")
        print(f"already carried wording (skipped) ... {self.already}")
        print(f"wording already in the sentence ..... {self.duplicate}")
        print(f"reference to the verse itself ....... {self.self_ref}")
        print(f"  ...of which in-prose mentions ..... {self.naked}")
        print(f"parenthetical that is prose ......... {self.prose_paren}")
        print(f"parenthetical too tangled to touch .. {self.complex_paren}")
        print(f"reference does not exist in Qur'an .. {self.invalid}")
        print(f"Bible / non-Quran citation (skipped) {self.bible}")
        print(f"format: {fmt}    applied: {applied}")


def parse_ref(tok):
    s, rest = tok.split(":")
    m = re.match(r"(\d+)(?:[–-](\d+))?$", rest)
    a = int(m.group(1))
    b = expand_end(a, int(m.group(2))) if m.group(2) else None
    return int(s), a, b


def refs_in_group(body):
    return [t.strip() for t in re.split(r"[,;]\s*", body) if t.strip()]


def contexts(text, i):
    para = text[:i].split("\n\n")[-1]
    tail = re.split(SENT_END, para)
    tight = tail[-1] if tail else para
    return re.sub(r"\s+", " ", tight)[-240:], re.sub(r"\s+", " ", para)[-1400:]


def render_paren(inner, parts, fmt):
    """Rewrite only the tokens, so the original separators survive untouched."""
    quotes = {tok: q for tok, q in parts if q}

    def sub(m):
        q = quotes.get(m.group(0))
        if not q:
            return m.group(0)
        return f'{m.group(0)} — *“{q}”*' if fmt == "inside" else f'*“{q}”* {m.group(0)}'

    return "(" + re.sub(TOKEN, sub, inner) + ")"


def process(text, tr, fmt, include_self, include_naked, report, preview=0):
    edits = []
    off_limits = []
    for m in BOOK_REF.finditer(text):
        s = m.group(0)
        off_limits.append((m.end() - len(s.split()[-1]), m.end()))
    line_starts, o = [], 0
    for ln in text.split("\n"):
        line_starts.append(o)
        o += len(ln) + 1

    def line_head(i):
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= i:
                lo = mid
            else:
                hi = mid - 1
        return text[line_starts[lo]:i].lstrip()

    def cur_verse(i):
        head = text[:i].rsplit("\n## ", 1)[-1]
        m = re.match(r"Verse (\d+):(\d+)", head)
        return (int(m.group(1)), int(m.group(2))) if m else None

    paren_spans = []
    for m in PAREN.finditer(text):
        paren_spans.append(m.span())
        if line_head(m.start()).startswith(("#", ">")):
            continue
        tokens, trailing = m.group(1), m.group(2)
        if any(a <= m.start(1) < b for a, b in off_limits):
            report.bible += 1
            continue
        if "“" in trailing or '"' in trailing or PRE_QUOTED.search(
                text[max(0, m.start() - 4):m.start()]):
            report.already += 1
            continue
        prose_tail = trailing.strip()
        if prose_tail and (len(prose_tail) > SHORT_TRAILING
                           or re.search(TOKEN, prose_tail)):
            # "(9:80 is this verse, and … at 9:81's own verses)" — leave it
            report.complex_paren += 1
            continue
        tight, wide = contexts(text, m.start())
        cur = cur_verse(m.start())
        parts = []
        touched = False
        for tok in refs_in_group(tokens):
            s, a, b = parse_ref(tok)
            if s not in tr or a not in tr[s]:
                report.invalid += 1
                parts.append((tok, None))
                continue
            if not include_self and cur and s == cur[0] and a <= cur[1] <= (b or a):
                report.self_ref += 1
                parts.append((tok, None))
                continue
            q, sc, _, _ = pick_quote(tr, s, a, b, tight, wide)
            q = clean_quote(q or "")
            if not q:
                parts.append((tok, None))
                continue
            if norm(q)[:40] and norm(q)[:40] in norm(tight):
                report.duplicate += 1
                parts.append((tok, None))
                continue
            report.filled += 1
            if sc == 0:
                report.whole_verse += 1
            if len(report.samples) < 500:
                report.samples.append((tok, sc, tight[-90:], q))
            parts.append((tok, q))
            touched = True
        if touched:
            if prose_tail:
                report.filled -= sum(1 for _t, q in parts if q) - 1
                report.prose_paren += 1
                quote = next(q for _t, q in parts if q)
                edits.append((m.start(), m.end(),
                              f"({m.group(1)}{m.group(2).rstrip()} — "
                              f"*“{quote}”*)"))
            else:
                edits.append((m.start(), m.end(),
                              render_paren(m.group(1), parts, fmt)))

    if include_naked:
        for m in NAKED.finditer(text):
            if any(a <= m.start() < b for a, b in paren_spans):
                continue
            if line_head(m.start()).startswith(("#", ">")):
                continue
            # "7:59 has it as *“the torment…”*" — wording already on the page
            rest = text[m.end():m.end() + 220]
            cut = SENT_END.search(rest)
            window = rest[:cut.start()] if cut else rest
            if QUOTEISH.search(window):
                report.already += 1
                continue
            if any(a <= m.start() < b for a, b in off_limits):
                report.bible += 1
                continue
            if PRE_QUOTED.search(text[max(0, m.start() - 4):m.start()]):
                report.already += 1
                continue
            tight, wide = contexts(text, m.start())
            s, a, b = parse_ref(m.group(1))
            if s not in tr or a not in tr[s]:
                report.invalid += 1
                continue
            cur = cur_verse(m.start())
            if not include_self and cur and s == cur[0] and a <= cur[1] <= (b or a):
                report.self_ref += 1
                continue
            q, sc, _, _ = pick_quote(tr, s, a, b, tight, wide)
            q = clean_quote(q or "")
            if not q or (norm(q)[:40] and norm(q)[:40] in norm(tight)):
                continue
            report.filled += 1
            report.naked += 1
            if len(report.samples) < 500:
                report.samples.append((m.group(1) + " [prose]", sc, tight[-90:], q))
            edits.append((m.start(), m.end(), f'{m.group(1)} — *“{q}”*'))

    if preview:
        show = []
        for st, en, rep in sorted(edits)[:preview]:
            show.append((re.sub(r"\s+", " ", text[max(0, st - 160):st]), rep))
    else:
        show = []

    for st, en, rep in sorted(edits, reverse=True):
        text = text[:st] + rep + text[en:]
    return text, show


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--format", choices=["inside", "before"], default="inside")
    ap.add_argument("--include-self", action="store_true")
    ap.add_argument("--no-prose-refs", action="store_true",
                    help="only touch parenthetical citations")
    ap.add_argument("--chapter", type=int, default=0)
    args = ap.parse_args()

    tr = load_translation()
    rep = Report()
    changed = 0
    for ch in ([args.chapter] if args.chapter else range(1, 115)):
        path = CORPUS / f"{ch:03d}.md"
        src = path.read_text(encoding="utf-8")
        new, show = process(src, tr, args.format, args.include_self,
                            not args.no_prose_refs, rep, args.preview)
        for ctx, r in show:
            print(f"\n--- {ch:03d} ---\n  …{ctx}\n  → {r}")
        if new != src:
            changed += 1
            if args.apply:
                path.write_text(new, encoding="utf-8")

    print(f"\nchapters that change: {changed}")
    rep.dump(args.format, args.apply)


if __name__ == "__main__":
    main()
