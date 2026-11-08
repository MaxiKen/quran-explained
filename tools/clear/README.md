# Clear teaching — the written English entries

An English commentary layer, **one entry per verse**, written from a reading of
Fī Ẓilāl al-Qurʾān, in the app's own modern English. It is not on screen in the
Simple view at present: that view shows Quṭb's Urdu on all 114 chapters (see
[Status](#status)). The entries, the gates and the review page stay in the
repository, and `SIMPLE_VIEW_PREFERS` in `js/app.js` brings them back.

**The rules are in [`STYLE.md`](STYLE.md).** That file is the authority:
volume, script, alignment, distinctness, house style, shape and payload layout
are specified there and enforced by `verify.py`.

## The one rule to know before writing

**Every verse gets 420 words of prose, band 400–440.** Not an average, not a
target. A thin verse gets more thought, not fewer words. `verify.py` fails the
file on any entry outside the band.

## Run the gates

```
python3 tools/clear/verify.py                    # the shipped payloads
python3 tools/clear/verify.py --dir work/clear --partial   # work in progress
python3 tools/clear/verify.py --file data/clear_001.json
python3 -m unittest discover -s tools/clear/tests
```

`--partial` accepts a payload that covers verses 1..N of a long sūrah, which is
how a chapter gets written in blocks. Every other rule still applies, and a gap
in the prefix still fails. A sample named `NNN-blockK.json` is always checked
that way, so `verify.py` with no arguments stays green while a chapter is being
written. A file named plainly `NNN.json` must cover the whole sūrah.

| Check | STYLE.md | Enforces |
|---|---|---|
| `words` | §2 | 420 words per verse, band 400–440 |
| `script` | §3 | Latin only; ﷺ the sole exception |
| `aligned` | §4 | every phrase of the app's `ayah_en` appears |
| `distinct` | §5 | no 8-word run shared between siblings |
| `shape` | §6, §7 | dash, semicolon, first person, citation, headings, `In short` |
| `coverage` | §2.3 | one entry per verse, never merged |
| `payload` | §10, §12 | `source`, `basedOn`, and the chapter `notice` |

A violation is a **failure**, not a warning.

The gate reads the translation out of `data/chapter_NNN.js`, so it cannot drift
from what the app displays.

## Writing one sūrah

1. Read the source passages in `data/qutb_NNN.json` beside the translations in
   `data/chapter_NNN.json` (`chapter_NNN.js`).
2. Write one entry per verse to `work/clear/NNN.txt`, using `<<<S:V>>>` markers
   and the body of each entry below its marker (see `work/clear/002.txt`). The
   translation of the verse goes inside `== … ==`; STYLE.md §4 explains why.
   Assemble it with:

   ```
   python3 tools/clear/build.py --surah NNN --from work/clear/NNN.txt \
       --to work/clear --partial
   ```
3. Run the gate. The word count fails first on almost every entry; that is
   normal and it is the point of the rule.
4. Copy the passing file to `data/clear_NNN.json` and
   `tools/clear/samples/NNN.json`, re-run the gate, commit.
5. Confirm the chapter renders left to right in the app and the chapter head
   names clear teaching.

## Status

| Surah | Entries | Words | Shipped |
|---|---|---|---|
| 1 | 7 | 401–439 | `data/clear_001.json` |
| 2 | complete | 400–440 | `data/clear_002.json` |

Both payloads are on disk for chapters 1 and 2. `SIMPLE_VIEW_PREFERS` in
`js/app.js` decides which the Simple view asks for first — `'ur'` (the shipped
setting) puts Quṭb's Urdu on all 114 chapters, `'en'` prefers the written
entries in the two chapters that have them. The other of the two stays loaded
as the fallback, so either can be restored without touching the payloads, and
the chapter head names whichever payload is on screen.

## Review

`preview.html` is a standalone page showing, per verse, the Arabic, the app's
translation, the entry, and the Urdu it was written from. Open it from the
repo root or through the dev server.
