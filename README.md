# quran-explained

Quran explained verse by verse.

The commentary is being written again from the ground up, in `tafsir/`, one chapter file at a
time, out of the **eleven** works this repository is written from (`corpus.SOURCE_ALLOWLIST`: the
ten tafsirs plus the study draft `tafsir_initial/`, v7.4). Each chapter is generated against a fixed
format and gated by an auditor before it is published to the app. The standard in force is
**v7.4**: the eleven works researched for every verse and named nowhere in the text, each verse
presented on its own terms, every cross-reference expanded with its clause, the register of
§0.11 and the independence law of §0.12 of `TAFSIR_RULES.md`. Chapters 1 and 2 are written and
published (`data/tafsir_001.json`, `data/tafsir_002.json`); chapter 3 is written through 3:14 and
remains unpublished while its later verses are scaffolds. Work moves in **runs of fifty verses**
(`scripts/tafsir/run.py`), mapped from all eleven works in one pass and finished before the writer
pauses.

## Start here

* [`TAFSIR_PROMPT.md`](TAFSIR_PROMPT.md) — the generation prompt and the format, quoting,
  attribution and style rules a chapter must satisfy.
* [`TAFSIR_PIPELINE.md`](TAFSIR_PIPELINE.md) — the repository layout, the sources, the tools and
  the working agreement.
* [`TAFSIR_WORKLOG.md`](TAFSIR_WORKLOG.md) — what is written so far.
* [`TAFSIR_RULES.md`](TAFSIR_RULES.md) — every rule the corpus is held to in one place (format,
  quoting, length, sourcing, attribution, style), each with the `audit.py` code that enforces it.
* [`UX_UPDATES.md`](UX_UPDATES.md) — the reader app's v2.3 reading-continuity, navigation,
  read-aloud and tafsir-sheet work, plus the v2.2 eBook, themes and accessibility passes.

## Pipeline in one screen

```bash
python3 scripts/tafsir/run.py --plan --start 2:1 # the fifty from the start the author names (2 or 2:1)
python3 scripts/tafsir/run.py --build            # map them from all eleven → tmp/runs/
python3 scripts/tafsir/run.py --slice 2:1 2:5    # read the map a stretch at a time
python3 scripts/tafsir/reference.py 2:255        # every cross-reference expanded, ready to paste
#   ... write the prose from the map, splice with scripts/tafsir/assemble.py ...
python3 scripts/tafsir/run.py --check            # RUN COMPLETE when all fifty are written and clean
python3 scripts/tafsir/audit.py 2                # the gate: must print RESULT: PASS
python3 scripts/tafsir/build_data.py 2           # publish → data/tafsir_002.json
python3 scripts/tafsir/status.py 2               # words per verse, gate verdict
```

Excerpts worth knowing:

* the **only** source of Qur'an wording is `data/chapter_NNN.js`; every quoted clause is checked
  verbatim against it;
* the headings are UPPERCASE descriptive titles (never the verse's own words), while every phrase
  of the verse is quoted *inside* the prose in **bold italics**, explained in verse order, and
  backed beside the quote by a cross-reference, a report with its collection, or a named
  authority; quotations from other verses are bold only, inside their reference — and those three
  are the **only** things bold in a chapter file (reports are italic `*"…"*`, the prose itself is
  plain);
* the commentary explains the verse as it is quoted: everything it holds up to explain is the
  verse's own wording or a synonym of it — one word or a whole phrase — and a synonym is adjusted to
  the verse's words while anything else fails;
* every verse carries at least 500 words, rising to eight times the verse's own length for long
  verses, and every verse needs checkable evidence — a Qur'an cross-reference, a report with its
  collection, a named authority, or a language point;
* prose is plain English (mean sentence under 22 words, reading ease 60+) and each verse carries a
  relatable analogy where one fits;
* every cross-reference is **expanded with the clause it points to**, copied from `data/`: a bare
  `(2:255)` warns and three in one section fail (`REF-BARE`), and `scripts/tafsir/reference.py`
  prints the expansion;
* work moves in **runs of fifty verses**, mapped out of all eleven works in one pass
  (`scripts/tafsir/run.py --build`), gated with `scripts/tafsir/batch.py N` as the stretches land,
  and finished — all fifty written and clean (`run.py --check`) — before the writer pauses;
* a chapter is finished when the whole-file auditor is clean, every verse clears its word floor,
  the payload is rebuilt, `sw.js` `CACHE_VERSION` is bumped and `TAFSIR_WORKLOG.md` has the row.

## App structure

* `index.html` — app shell: header navigation cluster, tafsir sheet, read-aloud dock and player orb.
* `js/chapters-meta.js` → `js/reading-memory.js` → `js/router.js` → `js/read-aloud.js` →
  `js/app.js` — load order is significant; the three middle modules must stay before `app.js`.
* `js/reading-memory.js` — remembers where you stopped per screen (anchors, not pixels).
* `js/router.js` — in-app history, back/forward stack, back-button guard, edge-swipe gestures.
* `js/read-aloud.js` — the bottom read-aloud dock and the shared floating player orb.
* `css/styles.css` — the whole design system.
* `data/chapter_NNN.js` — canonical Arabic, translation and audio per verse.
* `data/tafsir_NNN.json` — per-chapter commentary payload, built from `tafsir/NNN.md`. Chapters
  that have not been written yet show a short "coming soon" note rather than breaking the view.
* `tafsir-*/`, `tafsir_initial/` — the eleven source corpora the commentary is written from.

Serve the folder statically (`python3 -m http.server`) — the service worker and the `data/`
fetches need an origin, not `file://`.
