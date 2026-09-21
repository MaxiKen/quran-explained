#!/usr/bin/env python3
"""
Check what add_verse_quotes.py wrote.

1. every inserted quote is verbatim from the verse it is attached to
2. no citation was lost, added or renumbered versus the last commit
3. no Bible / non-Quran citation was given a Qur'an wording

    python3 scripts/editorial/verify_quotes.py
"""
import collections
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from verse_quotes import (BOOK_REF, CORPUS, expand_end,  # noqa: E402
                          load_translation, norm)

TOKEN = r"\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?"
ALL_TOK = re.compile(TOKEN)

# deliberate citation corrections, not losses:
#   25:193 "In 6:176" quoted 3:176's wording — Sūrah 6 has 165 verses
#   27:1064 "serve this Lord until certainty comes" is 15:99, not 27:99
INTENTIONAL = {(25, "6:176", "3:176"), (27, "27:99", "15:99")}

# every wording the inserter produced, in all three shapes:
#   (4:51 — *“…”*)   (4:94 gives the rule — *“…”*)   …the command at 7:31 — *“…”*
# the non-greedy body is safe because the translation never contains ”*
PAIR = re.compile(r"(?<![\d:])(\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?)\s*—\s*\*“(.*?)”\*",
                  re.S)


# "(4:94 gives the rule — “…”*)" — the wording is not adjacent to a token, so
# it is checked against every reference in that parenthetical. The tempered
# groups stop at the first ”* so a paren holding two quotes is not merged.
PROSE_PAREN = re.compile(
    r"\((\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?(?:\s*[,;]\s*\d{1,3}:\d{1,3}(?:[–-]\d{1,3})?)*)"
    r"((?:(?!”\*)[^()“])*?)\s*—\s*\*“((?:(?!”\*)[\s\S])*)”\*\)")

# an inserted quote whose opening * went missing
MALFORMED = re.compile(r'(?<!\*)— “(?:(?!\*“)[^”\n])*”\*')


def quoted_pairs(text):
    for m in PAIR.finditer(text):
        yield m.group(1), m.group(2)


def parse(t):
    a, b = t.split(":")
    m = re.match(r"(\d+)(?:[–-](\d+))?$", b)
    x = int(m.group(1))
    y = expand_end(x, int(m.group(2))) if m.group(2) else None
    return int(a), x, y


def main():
    tr = load_translation()
    bad_quote, bad_range, bible, lost, gained = [], [], [], [], []
    old_markers = {}
    n_quotes = 0
    n_prose = 0

    lens = []

    for ch in range(1, 115):
        name = f"markdown commentry/{ch:03d}.md"
        new = (CORPUS / f"{ch:03d}.md").read_text(encoding="utf-8")
        try:
            old = subprocess.run(
                ["git", "show", f"HEAD:{name}"], cwd=ROOT, capture_output=True,
                text=True, check=True).stdout
        except subprocess.CalledProcessError:
            old = ""

        old_markers[ch] = old.count('— *“')
        oldc, newc = collections.Counter(ALL_TOK.findall(old)), \
            collections.Counter(ALL_TOK.findall(new))
        for tok, n in oldc.items():
            if newc[tok] < n and not any(
                    ch == c and tok == o for c, o, _ in INTENTIONAL):
                lost.append((ch, tok, n, newc[tok]))
        for tok, n in newc.items():
            if newc[tok] > oldc[tok] and not any(
                    ch == c and tok == nn for c, _, nn in INTENTIONAL):
                gained.append((ch, tok, oldc[tok], n))

        for m in BOOK_REF.finditer(new):
            if "— *“" in new[m.end():m.end() + 8]:
                bible.append((ch, m.group(0)))

        for _m in PROSE_PAREN.finditer(new):
            toks, _mid, raw = _m.groups()
            if not _mid.strip():
                continue          # wording sits next to its token: PAIR covers it
            n_prose += 1
            quote = re.sub(r"\s+", " ", raw).strip()
            lens.append(len(quote))
            src = ""
            for tk in re.findall(TOKEN, toks):
                s, a, b = parse(tk)
                if s in tr:
                    src += norm(" ".join(tr[s][i] for i in range(a, (b or a) + 1)
                                         if i in tr[s])) + " "
            if norm(quote) not in src:
                bad_quote.append((ch, toks + " [prose]", quote[:90]))

        for tok, raw in quoted_pairs(new):
            n_quotes += 1
            s, a, b = parse(tok)
            quote = re.sub(r"\s+", " ", raw).strip()
            lens.append(len(quote))
            if s not in tr:
                bad_range.append((ch, tok, "no such surah"))
                continue
            hi = b or a
            src = norm(" ".join(tr[s][i] for i in range(a, hi + 1)
                                if i in tr[s]))
            if norm(quote) not in src:
                bad_quote.append((ch, tok, quote[:90]))

    texts = [(CORPUS / f"{c:03d}.md").read_text(encoding="utf-8") for c in range(1, 115)]
    markers = sum(x.count('— *“') for x in texts)
    # the corpus already used this shape for ~260 hand-written quotes
    inherited = sum(old_markers.values())
    markers -= inherited
    malformed = sum(len(MALFORMED.findall(x)) for x in texts)
    print(f"references now carrying wording ...... {markers}")
    print(f"  (plus {inherited} quotes the corpus already had in this shape)")
    print(f"  prose-parenthetical quotes checked . {n_prose}")
    print(f"  (checked verbatim against the verse: {n_quotes})")
    print(f"quote length  median {sorted(lens)[len(lens)//2] if lens else 0}  "
          f"max {max(lens) if lens else 0} chars")
    print(f"markers missing their opening * ...... {malformed}")
    print(f"quotes NOT verbatim in their verse ... {len(bad_quote)}")
    for x in bad_quote[:10]:
        print("    ", x)
    print(f"citations lost versus HEAD ........... {len(lost)}")
    for x in lost[:10]:
        print("    ", x)
    print(f"citations added versus HEAD .......... {len(gained)}")
    for x in gained[:10]:
        print("    ", x)
    print(f"Bible citations given a Qur'an quote . {len(bible)}")
    for x in bible[:10]:
        print("    ", x)
    every = n_quotes + n_prose
    print(f"markers accounted for ................. {every} of {markers}")
    ok = not (bad_quote or bad_range or lost or gained or bible or malformed
              or every != markers)
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
