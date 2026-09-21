# Second Pass — Full-Verse Ibn Kathir Integration Rules

Scope: **all 6,236 verses, in order 001 → 114**, starting again from `001.md`.
This pass does not sample. Every `## Verse C:Y` section is read against its
verse-aligned Ibn Kathir record in `tafsir-ibn-kathir/NNN.txt`. If the record
holds supporting evidence the commentary does not yet carry, it is added —
professionally, in flow, so the whole file reads as one coherent piece.

This file is the rule. `tafsir-ibn-kathir/WORKLOG.md` §3 still applies in full;
what follows extends it for this pass. Where they conflict, this file wins for
pass-two edits.

---

## R1. Coverage — every verse, ascending

1. Work strictly `001.md → 114.md`, verse by verse inside each file.
2. No skipping because a verse looks rich already. Rich sections are checked
   fastest, but they are still checked.
3. Surah-level material in an Ibn Kathir record (names, virtues, revelation
   history of the whole surah) goes once — to the chapter Introduction where
   one exists, otherwise to the first verse it concerns. Never repeated under
   every verse.
4. Shared Ibn Kathir blocks (byte-identical records across a range, e.g.
   14:47–48, 15:94–99): place the evidence once, at the verse the report
   actually concerns. `ik_targets.py` identical `chars` is the signal.

## R2. Evidence test — add what is missing, skip what is made

Add when the record gives, for that ayah, any of:

- a prophetic report (hadith / hadith qudsi) with collection + narrator,
- a Companion / Tabi`i / classical scholar gloss that pins a word or ruling,
- an occasion of revelation or sirah/historical anchor,
- a variant reading or a language point that changes understanding,
- a refusal: where Ibn Kathir declines unauthenticated material, record the
  decline (the 38:22 pattern).

Skip when:

- the section already makes the same point with equal or better evidence,
- the material is paraphrase of the verse rather than backup for it,
- the detail is trivia (word/letter counts, isnad minutiae) with no reader
  payoff. Evidence, not volume.

## R3. Flow — insertions must belong

1. New material reads as part of the section, not as an appended note. No
   `Ibn Kathir says:` labels stapled on the end; weave the attribution into
   the sentence (`Ibn Kathir preserves Ad-Dahhak's report from Ibn Abbas
   that...`).
2. Link with pronouns and transitions. The paragraph before and after an
   insertion must still connect.
3. Simple English. Short sentences. No academic gloss strings.
4. Never contradict or retell differently what an earlier verse in the same
   file already settled. If two verses share a story, tell it once and refer.

## R4. Coherence — the whole file must make sense together

1. After editing a file, read it top to bottom: Introduction → last verse.
   Names, dates, grades and story details must agree throughout.
2. If pass-two evidence corrects an earlier claim (e.g. a grade given loosely
   as unauthenticated where Ibn Kathir gives `Ahmad + At-Tirmidhi, Hasan
   Gharib`), correct the earlier claim in the same edit and say why.
3. No orphan detail: every new name, event or ruling gets the half-sentence of
   context a general reader needs.

## R5. Structure — at least 2 headings per verse

1. Every `## Verse C:Y` section carries **≥2** sub-headings.
2. Form is fixed: a bold line standing alone between blank lines:

   ```
   **The Heading In Title Words**

   Prose starts here...
   ```

   `**Heading**\nText` (no blank line) does **not** render — see
   `REMAINING_WORK.md` §5.4. Always blank line before and after.
3. Headings are short, plain, verse-specific. No generic `Commentary`,
   `Explanation`, `Lesson`. No heading without prose beneath it.
4. Restructuring into headings must not drop, merge away or reorder any
   `(chapter:verse)` citation. Headings split prose; they never delete it.

## R6. Attribution honesty (carried over, enforced)

1. Never invent a hadith number. Cite collection + narrator exactly as the
   source gives them. Grade only when the source grades
   (e.g. `At-Tirmidhi said Hasan Gharib`).
2. Never attribute to the Prophet ﷺ a witness account (`I saw the Messenger
   of Allah...`), a Companion ruling, or a commentator gloss. When the speaker
   is unclear, leave the report out.
3. Witness → witness, Companion → Companion, scholar → scholar. Keep the chain
   visible in one clause (`Muslim recorded Abu Hurayrah saying the Prophet ﷺ
   said...`).

## R7. Qur'an quotations

1. Every Qur'an wording is quoted from `ayah_en` in `data/chapter_NNN.js` —
   never from Ibn Kathir's Darussalam English. His paraphrase is evidence
   *about* the verse, never a substitute for it.
2. Long verses: quote the clause under discussion, not the whole verse.
3. One wording per reference, beside its own reference:
   `(4:51 — *“...”*)`. Multi-reference parentheticals never share one trailing
   quote.
4. Hadith/athar quotations use straight quotes inside emphasis (`*“...”* with
   straight `"` as the existing corpus does); Qur'an wordings use
   `— *“...”*` with curly quotes. Preserve each style where it stands.

## R8. What is never touched

1. The `> ...` verse blockquote under each `## Verse` heading — byte-identical
   always.
2. Any existing `(chapter:verse)` citation — every one present before the edit
   survives it, with its wording intact.
3. Verse counts, file names, section order, app code, translations.

## R9. Verification after every chapter batch

```bash
cd /home/user/quran-explained
python3 scripts/editorial/integrity.py            # 6,236 sections, 0 mismatches
python3 scripts/build_tafsir_json.py              # rebuild payload
python3 scripts/editorial/verify_quotes.py        # RESULT: PASS (re-run after commit — check 2 FAILs until then by design)
python3 scripts/editorial/check_ik_quotes.py      # RESULT: PASS
python3 scripts/factcheck.py                      # diff /tmp/factcheck_issues.json — new AUTH-REVIEW must be your own sentence
```

Bump `sw.js` `CACHE_VERSION` whenever `data/tafsir_*.json` changes.
Commit per chapter (or per small group for short surahs) on this branch only,
then re-run `verify_quotes.py` to confirm the true PASS.

## R10. Progress log

Record each finished chapter in `tafsir-ibn-kathir/WORKLOG.md` §5
(`Insertions completed`) with verse, evidence added, commit hash — same table,
new rows. Chapters remain `51 → 114` from pass one; pass two tracks separately
as `pass-two: ch N done` so the two passes are never confused.

## R11. Tooling pitfalls (paid for on ch 1)

1. **Never issue parallel `edit_file` calls against the same file.** They race
   on one snapshot and only the last write survives — two of three same-file
   edits silently reported success and applied nothing on 001.md. Same file =
   sequential edits, then verify with `git diff`.
2. **A whole-file rebuild must be followed by a paragraph-level check**: every
   pre-edit prose paragraph must appear verbatim post-edit except the sentences
   deliberately changed (recipe: split HEAD and worktree on `\n\n`, compare).
   The 001 rebuild once dropped a space (`thepetition`); the check caught it.
