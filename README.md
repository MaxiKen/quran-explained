# quran-explained

Quran explained verse by verse.

The commentary is being written again from the ground up, in `tafsir/`, one chapter file at a
time, out of the **eleven** works this repository is written from (`corpus.SOURCE_ALLOWLIST`: the
ten tafsirs plus the study draft `tafsir_initial/`, v7.4). Each chapter is generated against a fixed
format and two gates before it is published to the app. The standard in force is **v8**: the v7.4
source, register and independence laws remain, and Chapter 1 is now the frozen quality floor rather
than merely an example. The source-enriched Chapter 1 is independently approved, frozen and
published in `tafsir/001.md` and `data/tafsir_001.json`; its accepted schema-v2 reviews preserve the
all-source synthesis, substantive-claim, citation and transmitted-evidence decisions. Chapter 2 was
cleared and restarted from the sources; prose now reaches **2:50**, completing the drafting of the
pinned **2:1–2:50** run. Its introduction, 2:1–2:5 and 2:16–2:33 are independently accepted;
2:6–2:15 and 2:34–2:50 remain pending review. The contiguous accepted frontier is 2:5.
All fifty drafts pass the mechanical and review-candidate push gates. Verses 2:51–2:286 remain
scaffolds, and Chapter 2 is not published. Independent acceptance of the current run and the
author’s next start are required before another run is opened. Fifty verses are mapped from the eleven works in one pass, prose is
mechanically checked per verse, automatic drift alarms run in fifty-verse windows, and independent
review checkpoints contain at most fifty verses.

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

The current run is **draft-complete, review-pending**. Existing prose must not be regenerated.

```bash
python3 scripts/tafsir/run.py --plan --start 2:1 # restore the same pin if ignored scratch is absent
python3 scripts/tafsir/run.py --build --cap-json 0 # uncapped eleven-source digest + run map
python3 scripts/tafsir/run.py --slice 2:43 2:50   # source map for the final review checkpoint
python3 scripts/tafsir/batch.py 2 --from 1 --to 50 --push-check
python3 scripts/tafsir/quality.py --all --push-check
# Pending candidates are committed and pushed before owner acceptance.
# A different reviewer completes the pending source/claim/evidence ledgers and rubric.
python3 scripts/tafsir/run.py --status          # REVIEW PENDING until independent acceptance
# After all pending reviews are independently completed and approved:
python3 scripts/tafsir/batch.py 2 --from 1 --to 50
python3 scripts/tafsir/run.py --check           # RUN COMPLETE requires all fifty accepted
# Only then may the author choose the next run’s start.

# Whole-chapter publication remains blocked until all 286 verses are finished and accepted:
python3 scripts/tafsir/audit.py 2
python3 scripts/tafsir/quality.py 2
python3 scripts/tafsir/build_data.py 2
python3 scripts/tafsir/status.py 2
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
* every verse carries at least 700 words, rising to nine times the verse's own length for long
  verses, and every verse needs checkable evidence — a Qur'an cross-reference, a report with its
  collection, a named authority, or a language point;
* prose is plain English and is compared with the frozen Chapter-1 sentence, readability and
  evidence baseline; analogy and application are optional and must add verse-specific clarity;
* every acceptance review fingerprints all available passages from the eleven works, compares the
  full source map with the prose, groups duplicate witnesses into distinct material points, and marks
  each point included or omitted with a reason; changed source
  material invalidates stale approval rather than passing under an old review;
* every named hadith, collection, Companion and Successor statement is located in an allowlisted
  source and relevance-reviewed, just as every Qur'an cross-reference is relevance-reviewed;
* language claims and consequential legal/theological claims receive their own source-backed ledger;
  the reviewer checks the full prose and adds material claims that the conservative detector misses;
* every cross-reference is **expanded with the clause it points to**, copied from `data/`: a bare
  `(2:255)` warns and three in one section fail (`REF-BARE`), and `scripts/tafsir/reference.py`
  prints the expansion;
* fifty verses are mapped for research speed and form the maximum unaccepted review checkpoint;
  prose is written in order and mechanically checked per verse, while quantitative drift is still
  tested every fifty verses; every generation stop is committed and pushed as a clean review
  candidate, even when incomplete or pending, and acceptance remains mandatory for publication;
* a chapter is finished when the mechanical auditor and Chapter-1 parity gate pass, every verse clears its word floor,
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
