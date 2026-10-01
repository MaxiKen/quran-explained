# The tafsir pipeline, in four commands

Source of truth: `tafsir/NNN.md` (one chapter per file, the book's own voice).
The app payload `data/tafsir_NNN.json` is **built** from it — never edited
directly.

| Step | Command | What it does |
|---|---|---|
| 1. Evidence | `python3 scripts/tafsir/evidence.py 112` | Reads all eleven works for every verse of the chapter and writes a compact pack to `tmp/evidence/NNN.md`: the paragraphs that carry a report, a reading, an occasion, a ruling or a named authority, each tagged `[work ¶k]`, with a `SIGNALS` index. `--part 1-12`, `--budget 6000`, `--full`. |
| 2. Write | — | Write `tafsir/NNN.md`: introduction, then `## Verse N:V` sections. The verse line is copied from the app's own translation. |
| 3. Check | `python3 scripts/tafsir/check.py 112` | Form and traceability: every verse present and in order, the `> …` line byte-identical to `data/chapter_NNN.js`, every cross-reference clause really the wording of the verse it cites, headings, hygiene. |
| 4. Publish | `python3 scripts/tafsir/build_data.py 112` | Writes `data/tafsir_NNN.json` (`{"surah", "intro", "verses"}`), then `--check` to confirm it is current. Bump `CACHE_VERSION` in `sw.js`. |

`python3 scripts/tafsir/find.py "the Straight Path"` prints ready-made
cross-references — `(1:6 — **“Guide us along the Straight Path”**)` — copied
out of the app's translations, so no Qur'an wording is ever typed by hand.

## The chapter file

```markdown
# Sūrah Al-Ikhlāṣ (Chapter 112) — Verse-by-Verse Tafsir

## Introduction to the Sūrah

prose …

---

## Verse 112:1

> Say, ˹O Prophet,˺ “He is Allah—One ˹and Indivisible˺

**AN UPPERCASE HEADING**

prose, with anchors: a report and its collection, a named early authority, a
language point, and cross-references expanded with the clause they point to.
```

## Rules the writing keeps

1. **The book's own voice.** The eleven works are research, not content: the
   prose never relays a work, never compares works and never quotes them. A
   *report* may be quoted with its collection, and an *early authority*
   (Companion, Successor, first imam) may be named where he carries the point.
2. **Qur'an wording comes from `data/chapter_NNN.js` only** — the verse line,
   every cross-reference clause.
3. **Every verse carries checkable anchors**: a report with its collection, an
   authority, the language the verse turns on, and a cross-reference with its
   clause.
4. **No padding.** The evidence sets an honest length; a thin verse is short,
   a rich verse is long, and nothing is repeated to reach a number.
5. **Model of the corpus**: the ten classical works (`tafsir-*`) plus the study
   draft (`tafsir_initial`). The draft reads as a modern copyrighted commentary
   in a study-edition style; it is a cross-check for coverage, not a source of
   prose.

`tmp/` is scratch (evidence packs), rebuilt with one command and ignored by git.

## Owner decisions — the standing standard (2026-10-01)

These four answers set the standard for every chapter written after Chapter 112:

1. **Depth — evidence-led mix.** Rich verses get the standard treatment
   (~400–550 words, 2–4 headings, all reports worked in); short legal or
   repetitive verses stay lean and earn their length from the material. No
   padding in either direction: a thin verse is short, a rich verse is long.
2. **Voice — independent, with named works where they carry the point.** The
   prose is the book's own voice, but a striking or contested reading may be
   attributed — *"al-Qurṭubī notes…", "Ibn Kathīr adds…"* — to show the
   sourcing. Reports keep their collection; early authorities keep their names.
   Attribution is for the point, not a word-for-word quote of the work.
3. **Order — owner-named.** The writer does not choose the next chapter. The
   owner names a chapter (`112`) or a chapter:verse (`2:1`) and the run begins
   exactly there.
4. **Cadence — autonomous.** Commit and push each chapter as it is finished;
   do not stop to ask whether to continue. The owner reads the pushed result
   and redirects whenever wanted.
