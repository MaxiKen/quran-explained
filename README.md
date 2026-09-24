# quran-explained

Quran explained verse by verse.

The commentary is being written again from the ground up, in `tafsir/`, one chapter file at a
time, out of the 28 tafsir works in this repository. Each chapter is generated against a fixed
format and gated by an auditor before it is published to the app.

## Start here

* [`TAFSIR_PROMPT.md`](TAFSIR_PROMPT.md) — the generation prompt and the format, quoting,
  attribution and style rules a chapter must satisfy.
* [`TAFSIR_PIPELINE.md`](TAFSIR_PIPELINE.md) — the repository layout, the sources, the tools and
  the working agreement.
* [`TAFSIR_WORKLOG.md`](TAFSIR_WORKLOG.md) — what is written so far.
* [`UX_UPDATES.md`](UX_UPDATES.md) — the reader app's v2.3 reading-continuity, navigation,
  read-aloud and tafsir-sheet work, plus the v2.2 eBook, themes and accessibility passes.

## Pipeline in one screen

```bash
python3 scripts/tafsir/sources.py 2 --stats      # what the 28 sources have for Sūrah 2
python3 scripts/tafsir/sources.py 2              # digest → tmp/sources/002.txt
python3 scripts/tafsir/scaffold.py 2             # skeleton → tafsir/002.md (quotes byte-exact)
#   ... write the prose from the digest ...
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
  authority; quotations from other verses are bold only, inside their reference;
* every verse carries at least 550 words, rising to seven times the verse's own length for long
  verses, and every verse needs checkable evidence — a Qur'an cross-reference, a report with its
  collection, a named authority, or a language point;
* prose is plain English (mean sentence under 22 words, reading ease 60+) and each verse carries a
  relatable analogy where one fits;
* long chapters are written in batches, gated with `scripts/tafsir/batch.py N` as they land, and
  the writer keeps going batch after batch until the chapter is finished;
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
* `tafsir-*/`, `tafsir_initial/` — the source corpora the commentary is written from.

Serve the folder statically (`python3 -m http.server`) — the service worker and the `data/`
fetches need an origin, not `file://`.
