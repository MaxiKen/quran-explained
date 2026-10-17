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

The commentary can be read three ways. The reader chooses, in the verse
pop-up and in the reading edition:

- **Full commentary** — the whole passage as text.
- **Quick read** — the same commentary listed as its parts, each part showing
  its opening line and opening to the full passage. Where Tabarī goes phrase
  by phrase, the phrase is the heading of its group. It is built in the
  browser from the same payload (`buildQuickRead` in `js/app.js`); it is
  Tabarī's own text, shortened, never a paraphrase, and nothing is dropped.
- **Phrase by phrase** — the reader's *own* modern translation, broken into
  the phrases a reader would call phrases, with the words Tabarī says about
  each phrase underneath. The pairing is built by `tools/pairs/build.py` into
  `data/pairs_NNN.json`: Tabarī names a phrase in his own words, and that
  wording is matched against the translation. Nothing is written by the
  builder — it only decides which of the reader's words belong to which of
  Tabarī's paragraphs. Where the two translations do not share their
  wording, the phrase is left without his words rather than given the wrong
  ones; the rest of the commentary is still in the quick read.

The pairing is a floor, not a ceiling: about 45% of the translation's phrases
are matched this way, and the rest would need a model to align where the two
renderings differ. Any model run must write into the same file, and its
output must be checked against the same two rules — the phrase must be the
reader's own words, and the parts must exist in the commentary.

If you are here to continue that project, **everything you need is in
`tools/guidance/HANDOFF.md`**. Read it completely before acting. The design
decisions in its §2 are final; do not ask the maintainer about them again.

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
