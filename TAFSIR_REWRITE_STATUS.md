# Tafsir Rewrite — Progress Tracker

## The problem being fixed

The commentary in `markdown commentry/*.md` was generated to a target word count, so every verse
received roughly the same amount of text (~1,077 words on average across 6,236 verses) whether or
not the verse needed it. The result is padding, repeated points, boilerplate section headings
repeated verbatim under different verses, and occasionally real content drowned in restatement.

## The standard applied to every chapter

- Each verse gets the length its content honestly needs — short verses short, weighty verses long.
- No point is made twice. If it was already said, it is cut, not restated.
- Section headings that add nothing (e.g. `**Expanded Commentary**`, or a generic heading repeated
  under several verses) are removed; headings that organise real content are kept.
- Simple English throughout. Undefined technical terms are explained in plain words.
- **Preserved in full**: Qur'anic cross-references, hadith citations and grading notes, historical
  accounts and occasions of revelation, scholarly disagreements, stories and parables, prophetic
  biography. These may be rephrased or shortened, never dropped.
- Content is added where a verse genuinely needs it (a short verse carrying a large idea, or a
  section that was too thin to explain the verse clearly).
- Structural contract with `scripts/build_tafsir_json.py` is unchanged: `## Introduction to the Sūrah`
  and `## Sūrah <Name> <chapter>:<verse>` headings, one per verse, in order.

Work is done by reading each chapter and rewriting it by hand — no find-and-replace passes, no
scripted transformations.

## Status

| Chapter | Sūrah | Before (bytes) | After (bytes) | Done |
|---|---|---|---|---|
| 001 | al-Fātiḥah | 51,245 | 40,478 | ✅ |
| 103 | al-ʿAṣr | 23,154 | 7,718 | ✅ |
| 108 | al-Kawthar | 20,266 | 8,623 | ✅ |
| 114 | an-Nās | 48,935 | 31,882 | ✅ |

Remaining: 110 chapters (002–102, 104–107, 109–113).

Chapter 002 is partially done: the introduction and verses 2:1–2:4 were refined in an earlier pass
and are kept; the rest of the chapter (2:5–2:286) still carries the padded text. Chapter 002 is
about 2.2 MB on its own, so it is worked through in verse ranges over several passes rather than in
one go.

## Order of work

Sequential from Sūrah 001, as agreed. Note on pacing: the seven largest chapters — 002, 003, 004,
006, 007, 026, 037 — are about 10 MB of the 40 MB corpus on their own, so each of those takes
several passes (worked through in verse ranges). The short late chapters take a fraction of the
time per chapter; they are done as fast wins alongside the large ones.

## Note on serving the app

Per instruction, only the markdown is edited. The app reads `data/tafsir_NNN.json`, which is built
from the markdown by `python3 scripts/build_tafsir_json.py`. Until that command is run, the app
continues to serve the old text for chapters already rewritten. Run it once when you want the
edited commentary to appear in the app.
