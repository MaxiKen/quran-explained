#!/usr/bin/env python3
"""
Check what add_verse_quotes.py wrote.

1. every wording attached to a reference is verbatim from that verse
2. no citation was lost, added or renumbered versus the last commit
3. no Bible / non-Quran citation was given a Qur'an wording
4. nothing was written with a missing `*`, and no reference lost its wording

    python3 scripts/editorial/verify_quotes.py
"""
import collections
import pathlib
import json
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from verse_quotes import (BOOK_REF, CORPUS, expand_abbrev,  # noqa: E402
                          expand_end, load_translation, norm)

TOKEN = r"\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?"
ALL_TOK = re.compile(TOKEN)
ONE_TOK = re.compile(TOKEN)
PAREN = re.compile(r"\(([^()]*)\)")
MARKER = "— *“"
# a wording, wherever it sits
QUOTE = re.compile(r"— \*“(.*?)”\*", re.S)
BIBLE_Q = re.compile(r"\s*—\s*\*“(.*?)”\*", re.S)
# the Bible passages this project is allowed to quote beside a Bible citation
_BIBLE = json.loads((CORPUS.parent / "data" / "bible_web.json").read_text(encoding="utf-8"))
BIBLE_NORM = [norm(v) for k, v in _BIBLE.items() if not k.startswith("_")]
# the corpus's own older style puts the reference *after* the wording:
#   … a sufficiency — *“And Allah ˹alone˺ is sufficient as a Witness.”* (4:166)
# factcheck.py already validates those; they are not this tool's business
REF_AFTER = re.compile(r"\s*\(\d{1,3}:\d{1,3}")
# an inserted quote whose opening * went missing
MALFORMED = re.compile(r'(?<!\*)— “(?:(?!\*“)[^”\n])*”\*')

# deliberate citation corrections, not losses:
#   25:193 "In 6:176" quoted 3:176's wording — Sūrah 6 has 165 verses
#   27:1064 "serve this Lord until certainty comes" is 15:99, not 27:99
INTENTIONAL = {(25, "6:176", "3:176"), (27, "27:99", "15:99")}


def resolved(text):
    """`(5:17, 18, 40)` is written out in full, so compare resolved refs."""
    return re.sub(r"\(([^()]*)\)",
                  lambda m: "(" + expand_abbrev(m.group(1)) + ")", text)


def parse(tok):
    a, b = tok.split(":")
    m = re.match(r"(\d+)(?:[–-](\d+))?$", b)
    x = int(m.group(1))
    return int(a), x, (expand_end(x, int(m.group(2))) if m.group(2) else None)


def enclosing_paren(text, pos):
    """The parenthetical that really contains `pos`, matched by depth — not the
    last `(` anywhere before it, which may have closed a sentence earlier."""
    st = text.rfind("(", 0, pos)
    if st == -1:
        return None
    depth, i = 0, st
    while i < len(text):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[st + 1:i] if st < pos < i else None
        i += 1
    return None


# a wording cited to a hadith collector is not a claim about a Qur'an verse
HADITH = re.compile(r"\s*\((?:al-|Musnad\s|Ṣaḥīḥ\s)?(?:Tirmidhī|Bukhārī|Muslim|Aḥmad|"
                    r"Ibn\s+Mājah|Abū\s+Dāwūd|Nasāʾī|Ḥākim|Bayhaqī|Dārimī)", re.I)
SENT_END = re.compile(r"[.!?”]\s")


def attributions(text):
    """
    Every (references, wording) pair. A wording sitting inside a parenthetical
    may belong to any reference in that parenthetical — the house style puts one
    trailing quote after a list, and it usually explains the first of them — so
    the whole list is returned and the wording counts as verified if it matches
    any member. Wordings in running prose are credited to the nearest reference
    ahead of them in the same sentence, and are dropped when they belong to a
    hadith or when a sentence break separates them from that reference.
    """
    for qm in QUOTE.finditer(text):
        if REF_AFTER.match(text, qm.end()):
            continue          # reference follows the wording: hand-written style
        if HADITH.match(text, qm.end()):
            continue          # hadith, cited to its own collector
        # anything near a named Bible book belongs to that book, not to a surah:
        # in "(Exodus 32:27 — *“…”*)" the 32:27 is Exodus, not surah 32
        if BOOK_REF.search(text[max(0, qm.start() - 70):qm.end() + 90]):
            continue
        inner = enclosing_paren(text, qm.start())
        # a Bible parenthetical: "Exodus 32:27" is not surah 32 verse 27
        if inner and BOOK_REF.search(inner):
            continue
        toks = [m.group(0) for m in ONE_TOK.finditer(inner)] if inner else []
        if not toks:            # wording in running prose, e.g. "at 7:31 — *“…”*"
            pre = text[:qm.start()]
            cand = list(ONE_TOK.finditer(pre))
            if not cand or SENT_END.search(pre[cand[-1].end():]):
                continue
            toks = [cand[-1].group(0)]
            # the house style also lets a wording introduce the reference that
            # follows it: — *“the warner's question…”* — and the answer (43:23–24)
            tail = text[qm.end():]
            cut = SENT_END.search(tail)
            for pm in PAREN.finditer(tail[:cut.start()] if cut else tail):
                toks += [m.group(0) for m in ONE_TOK.finditer(pm.group(1))]
        yield tuple(dict.fromkeys(toks)), qm.group(1)


def bible_markers(text):
    """Count of wordings that belong to a Bible citation.

    They are checked against the Bible passage rather than a surah, so they
    must not be counted as unaccounted. A citation may be parenthetical
    ("(Genesis 1:1–5 — *“…”*)") or in running prose ("Deuteronomy 14:1 — *“…”*"),
    so both the enclosing parenthetical and the text just ahead are checked.
    """
    n = 0
    for m in re.finditer(re.escape(MARKER), text):
        inner = enclosing_paren(text, m.start())
        if (inner and BOOK_REF.search(inner)) or \
                BOOK_REF.search(text[max(0, m.start() - 60):m.start()]):
            n += 1
    return n


def verse_text(tr, tok):
    s, a, b = parse(tok)
    if s not in tr:
        return None
    return norm(" ".join(tr[s][i] for i in range(a, (b or a) + 1) if i in tr[s]))


def audit(text, tr, ch, inherited_sigs=()):
    """inherited_sigs: wordings HEAD already had, in the corpus's own looser
    style — reported separately, never as a failure of this change."""
    bad, matched, lens, old_bad = [], 0, [], []
    for toks, raw in attributions(text):
        matched += 1
        quote = re.sub(r"\s+", " ", raw).strip()
        lens.append(len(quote))
        # norm() maps punctuation to spaces, so a closing full stop in the
        # commentary leaves a trailing space behind — drop it before comparing
        q = norm(re.sub(r"[.,;:!?”\"']+$", "", quote.strip())).strip()
        hit = None
        for tok in toks:
            src = verse_text(tr, tok)
            if src is not None and q and q in src.strip():
                hit = tok
                break
        if hit:
            continue
        tok = toks[-1]
        src = verse_text(tr, tok)
        item = (ch, " + ".join(toks), quote[:90] if src else "no such surah")
        if (toks, norm(raw)) in inherited_sigs:
            old_bad.append(item)
        else:
            bad.append(item)
    return bad, matched, lens, old_bad


def main():
    tr = load_translation()
    bad_quote, bible, lost, gained, malformed = [], [], [], [], 0
    total = matched_total = 0
    old_total = old_matched = 0
    inherited = 0
    lens = []
    old_sigs = set()
    inherited_bad = []

    for ch in range(1, 115):
        name = f"markdown commentry/{ch:03d}.md"
        new = (CORPUS / f"{ch:03d}.md").read_text(encoding="utf-8")
        try:
            old = subprocess.run(["git", "show", f"HEAD:{name}"], cwd=ROOT,
                                 capture_output=True, text=True,
                                 check=True).stdout
        except subprocess.CalledProcessError:
            old = ""

        oldc = collections.Counter(ALL_TOK.findall(resolved(old)))
        newc = collections.Counter(ALL_TOK.findall(resolved(new)))
        for tok, n in oldc.items():
            if newc[tok] < n and not any(
                    ch == c and tok == o for c, o, _ in INTENTIONAL):
                lost.append((ch, tok, n, newc[tok]))
        for tok, n in newc.items():
            if newc[tok] > oldc[tok] and not any(
                    ch == c and tok == nn for c, _, nn in INTENTIONAL):
                gained.append((ch, tok, oldc[tok], n))

        # a wording next to a Bible citation must be that Bible passage, not a
        # Qur'an verse — the shape of the two citations is identical
        for m in BOOK_REF.finditer(new):
            qm = BIBLE_Q.match(new, m.end())
            if not qm:
                continue
            said = norm(qm.group(1)).strip()
            if not any(said in src for src in BIBLE_NORM):
                bible.append((ch, m.group(0)))

        # a wording inside a Bible parenthetical is checked against the Bible
        # passage, not against a surah, so it is not "unaccounted" here
        total += new.count(MARKER) - bible_markers(new)
        old_total += old.count(MARKER) - bible_markers(old)
        ob, om, osig, _ = audit(old, tr, ch)
        old_matched += om
        old_sigs |= {(tuple(ts), norm(q)) for ts, q in attributions(old)}
        b, mt, ln, _ = audit(new, tr, ch, old_sigs)
        bad_quote += b
        inherited_bad += ob
        matched_total += mt
        lens += ln
        malformed += len(MALFORMED.findall(new))

    inherited = old_total
    new_quotes = total - inherited
    unaccounted = total - matched_total
    was_unaccounted = old_total - old_matched

    print(f"references carrying wording .......... {new_quotes} new, "
          f"{inherited} already in HEAD")
    print(f"wordings checked against their verse . {matched_total}")
    if lens:
        print(f"quote length  median {sorted(lens)[len(lens) // 2]}  "
              f"max {max(lens)} chars")
    print(f"wordings not verbatim in their verse . {len(bad_quote)}")
    for x in bad_quote[:10]:
        print("    ", x)
    print(f"  plus {len(inherited_bad)} older hand-written wordings that do not "
          f"match\n    their own verse (pre-date this work; listed, not failed)")
    for x in inherited_bad[:5]:
        print("    ", x)
    print(f"markers missing their opening * ...... {malformed}")
    print(f"citations lost versus HEAD ........... {len(lost)}")
    for x in lost[:10]:
        print("    ", x)
    print(f"citations added versus HEAD .......... {len(gained)}")
    for x in gained[:10]:
        print("    ", x)
    print(f"Bible citations given a Qur'an quote . {len(bible)}")
    for x in bible[:10]:
        print("    ", x)
    print(f"hand-written wordings, no adjacent ref {unaccounted} "
          f"(was {was_unaccounted})")

    ok = not (bad_quote or lost or gained or bible or malformed
              or unaccounted > was_unaccounted)
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
