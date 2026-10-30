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

The reader offers two separate commentary views in a switch, in this order:

1. **Phrase by phrase** — selected first in the switch. The verse translation
   is split into short, consecutive pieces, each followed by a substantive,
   plain-English explanation. It is a numbered reading, not a one-line gloss.
2. **Full commentary** — the complete Tafsīr al-Ṭabarī passage as text.

Only the selected view is shown; do not stack the full commentary below the
phrase explanations. Add a related verse, quotation, context, history, or
illustration only when it helps, and weave it naturally into the paragraph
without a type label or formulaic lead-in.

Phrase explanations are authored by hand in `tools/pairs/authored/NNN.json`
and published as `data/pairs_NNN.json` by `tools/pairs/assemble.py`. Each
phrase must be an exact piece of the reader's translation, phrases stay in
order, and they cover all the verse's words. Two length policies are in force,
declared per chapter by `split_policy`:

- **`sense-v1`** (surahs 2 through 43): one paragraph of 45–85 words per
  phrase, whatever the source holds.
- **`tabari-v2`** (surah 1, and every chapter authored from now on): a
  beginner's summary of what Tafsīr al-Ṭabarī discusses for that piece of the
  verse, at the length that material deserves. Each phrase also names the piece
  of the verse's Arabic it explains (`ar`), `tools/pairs/digest.py` measures
  the passage against those spans, and the floor is 40 words with **no
  ceiling**. Phrase boundaries follow Ṭabarī's own units. Several paragraphs
  are allowed once an explanation runs long.

Chapters migrate one at a time and an unmigrated chapter keeps the gates it was
written under, so `python3 tools/pairs/assemble.py --check` passes on the whole
corpus at every commit. It checks phrase order, coverage, Arabic-span coverage
and length under the policy in force. Surahs 1 through 43 are published; later
chapters are not yet authored.

The handoff below is for the separate, withdrawn plain-English commentary
pipeline in `tools/guidance/`, not for this phrase-by-phrase layer. If you are
continuing that historical project, **everything you need is in
`tools/guidance/HANDOFF.md`**. Read it completely before acting.

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
