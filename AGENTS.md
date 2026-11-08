# Agent instructions for this repository

This is a static Qur'an reader (no build step) whose tafsīr is **Tafsīr
al-Ṭabarī in English**, complete on every verse, with the Arabic original of
the commentary underneath each verse. The payload is `data/tafsir_NNN.json`,
imported from tafseerquran.com by `tools/tabari/`. The eight classical tafsīrs
the reader used to carry are gone.

There was also a second layer: an original **plain-English commentary** for
every verse and every surah, published as `data/guidance_NNN.json`. It was
written from those eight earlier tafsīrs, so it went when they went: the
files are deleted, the reader no longer shows the layer, and the tafsīr stands
alone. The pipeline in `tools/guidance/` is kept for the record — it holds
the verification gates and the account of how the layer was made — and it
stops with an explanation rather than running against a corpus the reader no
longer carries.

The reader offers two separate commentary views in a switch, **Simple** first:

1. **Simple** — Fī Ẓilāl al-Qurʾān by Sayyid Quṭb in Urdu, the passage he
   writes for each run of verses. The payload is `data/qutb_NNN.json`, imported
   from spa5k/tafsir_api by `tools/qutb/`. Upstream repeats one passage for
   every verse it covers; the reader stores each passage once (`blocks`), names
   the verses it covers (`ranges`), and maps them (`verses`), so a run is shown
   in full at its first verse and the later verses point back to it rather
   than printing the same paragraphs again.
2. **Full commentary** — the complete Tafsīr al-Ṭabarī passage in English, with
   the Arabic original underneath it.

Only the selected view is shown; the two are never stacked.

`tools/pairs/` still holds the phrase-by-phrase pipeline from an earlier
layer (hand-written `authored/NNN.json`, published as `data/pairs_NNN.json`).
That layer is **not wired into the reader any more** — no `data/pairs_*.json`
is shipped and the switch no longer offers it — and it is kept for the record
only. Do not treat its rules as binding on the current views.

The authoring briefs that are binding on commentary text are: the one for
Tafsīr al-Ṭabarī in `tools/tabari/README.md`, the payload rules in
`tools/qutb/README.md` for the Urdu Simple view (verbatim text, verbatim
upstream passages, no rewriting, translation or summary of the Urdu), and
**`tools/clear/STYLE.md` for the written English entries**.

`tools/clear/STYLE.md` is the authority for the English entries in
`data/clear_NNN.json`, one per verse. Its first rule is a hard one: **every
verse gets 420 words of prose, band 400–440, no merges and no exceptions.**
`python3 tools/clear/verify.py` fails a payload that breaks any rule in the
file, and `python3 -m unittest discover -s tools/clear/tests` proves the gates
reject each violation. Do not commit a `data/clear_NNN.json` that has not
passed both.

These entries are **not on screen at present**. `SIMPLE_VIEW_PREFERS` in
`js/app.js` is `'ur'`, so the Simple view shows Quṭb's Urdu on all 114
chapters; the entries stay in the repository and `'en'` prefers them in the two
chapters that have them. The gate rules above still bind whatever is committed
to `data/clear_NNN.json`, and a payload that has silently gone stale against a
change of translation is a bug whether or not it is rendered.

To refresh the Simple payload from upstream:

```
python3 tools/qutb/importer.py --src <clone>/tafsir/tafsir-fe-zalul-quran-syed-qatab
python3 tools/qutb/verify.py --data data
python3 -m unittest discover -s tools/qutb/tests
```

`importer.py --check` re-derives every file and reports whether the committed
payload still matches its source; `verify.py` is the reader-side gate (coverage
of every verse, contiguous ranges, one block per passage, Arabic-script text).
`.github/workflows/qutb-import.yml` runs the same steps when
`tools/qutb/plan.json` says `run: true`.

The handoff below is for the separate, withdrawn plain-English commentary
pipeline in `tools/guidance/`. If you are continuing that historical project,
**everything you need is in `tools/guidance/HANDOFF.md`**. Read it completely
before acting.

## Chapter-number sessions

A chapter number alone (for example `18`) authorizes generation/resumption of
that chapter's introduction and all verses. Chapters may be generated in any
order, in separate concurrent sessions. Read `tools/guidance/CHAPTER_RUN.md`
for the authoritative chapter-isolated workflow and merge-safe file manifest.
Work only on the requested chapter and the session's assigned branch.

Start with `git status --short`, record the starting commit, run the pipeline
tests, then `python3 tools/guidance/status.py --next --surah N`.
Within that chapter: introduction first, then verse jobs in verse order.
Read all digest parts, write each raw draft, and use `finish.py JOB` for
work-output gates, assembly, commit and push. It no longer performs full
published-data verification per job or advances to another chapter.

**Run FULL CHAPTER VERIFICATION once, only after the introduction and every
verse are fully generated and all intended repairs are finished.** Never run
it on a partial chapter, per job, per batch, per push or per session. Record
its result and payload hash in `tools/guidance/chapters/SSS.md`; reuse the
receipt on resume. Scoped/work-output checks remain mandatory throughout.

End each chapter with an exact list of all created/updated/deleted files,
including chapter-local progress/verification/merge notes. Stage only that
chapter's payload, raw files and report. Do not update shared instruction files
or global progress logs in routine content sessions. Inspect inherited branch
changes before proposing a chapter-only merge; do not overwrite newer main.

Current checkpoint (2026-10-15): Surahs 1 and 2 are complete. All 128
baseline Al-Baqarah flags have been addressed. Complete published-data
verification, run after that review, found 272 ok, 15 reviewed residual flags
and zero failures across 287 entries. Gates are unchanged. No further chapter is authorized until the user supplies its number;
a main merge always needs separate authorization. See FLAG_REVIEW_002.md for the review dispositions.

Non-negotiables (details and reasons in the handoff):

- Write only from the material in the job. No outside knowledge, names, grades or verse numbers.
- Never name the eight works or their authors; one anonymous voice.
- No Arabic script (ﷺ only), no em dashes or semicolons outside quotes, plain English.
- Length is proportional to the material (≈ 0.6 ×), never a band, never padded.
- Every verse gets its own self-contained entry; every surah gets an introduction. Chapters are selected by the user in any order; keep verse order within each chapter.
- Never publish a `fail`; never use `--include-failed`; never relax `verify.py` to pass an entry.
- Work only on the session's branch, commit after every job, push every time, never force-push.
- Keep the selected chapter’s `tools/guidance/chapters/SSS.md` progress and file manifest current before stopping; do not edit shared HANDOFF progress for routine chapter runs.

The paste-able prompt for starting a new session is `tools/guidance/CONTINUE_PROMPT.md`.
