# quran-explained

Quran explained verse by verse.

The commentary is written from the ground up, in `tafsir/`, one chapter file at a time, out of
the **eleven** works this repository is written from (`corpus.SOURCE_ALLOWLIST`: the ten tafsirs
plus the study draft `tafsir_initial/`, v7.4). Each chapter is generated against a fixed format and
two gates before it is published to the app. The standard in force is **v8**: the v7.4 source,
register and independence laws remain, and Chapter 1 is the frozen writing-style yardstick — not a
measure of how much content or evidence a verse carries — rather than merely an example. Fifty verses are mapped from the eleven works in one pass; prose is mechanically checked
per verse, automatic drift alarms run in fifty-verse windows, and independent review checkpoints
contain at most fifty verses.

**All generated commentary was cleared on 2026-10-01, and commentary writing is paused.** Nothing the
generator wrote is in the current tree: `tafsir/` holds only `.gitkeep` (Chapters 1 and 2 are gone),
no `data/tafsir_NNN.json` payload exists so every chapter shows the app's “coming soon” note, the
drafting bench `tmp/work/` keeps only its `dig.py` helper, and the review manifests and the owner's
draft-approval receipt that were bound to the cleared prose are removed. The eleven source works,
`data/chapter_NNN.js` and the pipeline scripts are untouched, and the cleared text stays readable in
git history.

**The author is trying a two-phase approach** ([`TAFSIR_EVIDENCE_MAP.md`](TAFSIR_EVIDENCE_MAP.md)):
first an *evidence map* for every verse — heads, with a short summary of the evidence the eleven works
carry under each — and later, chapter by chapter on the author's prompt, commentary built from the
maps, its length decided by the evidence rather than a fixed word range. Two pilot maps exist,
`evidence/103.md` (full depth) and `evidence/108.md` (survey depth). The standing order for commentary
(review in a separate pass, post the statistics, push, carry on without waiting; `TAFSIR_RULES.md` §0.9)
is recorded for when commentary resumes. The Chapter-1 style record
`quality/chapter-001-baseline.json` is kept, but with Chapter 1 gone `quality.py --baseline` reports
`QTY-BASELINE-CHANGED`, so the “Tafsir quality parity” check fails at its baseline step until the record
is re-frozen or retired ([`quality/README.md`](quality/README.md)).

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

**Commentary is paused**, so a bare “continue” does not start it. Phase 1 — the evidence maps — is
piloted at full depth, the author's choice (`TAFSIR_EVIDENCE_MAP.md`; `evidence/103.md` is the model):

```bash
python3 scripts/tafsir/sources.py N --cap-json 0           # the digest for chapter N (git-ignored scratch)
python3 scripts/tafsir/evidencemap.py read N V --full      # every paragraph of every work, numbered
python3 scripts/tafsir/evidencemap.py check N              # validate evidence/NNN.md (--gaps: what is unaccounted)
```

When commentary resumes, a bare “continue” pins the first unwritten verse and goes — the author's
standing order (2026-10-01); the author may re-aim it with `--start C:V` at any time. A run is fifty
verses; `C:V` is a chapter and verse, `N` a chapter, `A`–`B` verses.

```bash
python3 scripts/tafsir/run.py --plan [--start C:V] # pin the next fifty (default: the first unwritten verse)
python3 scripts/tafsir/run.py --build --cap-json 0 # uncapped eleven-source digest + run map
python3 scripts/tafsir/run.py --slice C:V C:V     # a source-reading stretch of the pinned run
python3 scripts/tafsir/scaffold.py N              # create tafsir/NNN.md for a chapter not yet started
python3 scripts/tafsir/batch.py N --from V --to V --draft    # mechanical check of each verse as it lands
python3 scripts/tafsir/quality.py --template N --from A --to B --writer arena-writing-agent
# The independent review pass: a separate, cold pass as reviewer arena-review-agent completes the
# source/claim/evidence ledgers and the rubric from the prose and the source passages only.
python3 scripts/tafsir/batch.py N --from A --to B            # mechanical + independent parity gate
python3 scripts/tafsir/stats.py N --from A --to B --write    # the statistics posted with the push
# Commit and push to the session branch, then carry on with the next run — no waiting.
python3 scripts/tafsir/quality.py --all --push-check         # what CI runs on every push
python3 scripts/tafsir/run.py --status          # written/unwritten, floors and gate state
python3 scripts/tafsir/run.py --check           # RUN COMPLETE requires all fifty accepted

# Whole-chapter publication remains blocked until every verse of the chapter is finished and accepted:
python3 scripts/tafsir/audit.py N
python3 scripts/tafsir/quality.py N
python3 scripts/tafsir/build_data.py N
python3 scripts/tafsir/status.py N
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
* fifty verses are mapped for research speed; no more than fifty new drafts follow
  accepted/owner-approved prose, and each semantic review covers at most fifty verses;
  prose is written in order and mechanically checked per verse, while quantitative drift is still
  tested every fifty verses; every generation stop is reviewed, committed and pushed with its
  statistics, even when the chapter is incomplete, and the run goes on without waiting for
  confirmation; acceptance remains mandatory for publication;
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
