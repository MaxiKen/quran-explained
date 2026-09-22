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

---

# R12. Batch operations manual — how a 50-verse batch is executed

This section is the executable procedure behind every pass-two batch from ch 2
onwards. Follow it exactly; the gates are mandatory, not advisory.

## R12.0. Batch unit and commit discipline

1. **50 verses per batch, one commit per batch.** Ranges are fixed
   (`C:1–50`, `C:51–100`, …). The chapter's final partial batch ships whole —
   never split a batch; take longer instead.
2. This supersedes R9's "commit per chapter" for chapters over 50 verses.
   Chapters of ≤50 verses are a single batch.
3. Commit message format (exact):
   `Pass two Batch <letter>: Ibn Kathir gap-fill for ch <N> (<N>:<A>-<B>)`
   Batch letters continue the alphabet across chapters (ch 2 = A–H,
   ch 3 = I–L, ch 4 = M–P, ch 5 starts at Q…).
4. Work on your assigned branch only; push only to it. The tree must be clean
   before a batch starts and clean after it is pushed.

## R12.1. Prerequisites — build the verse index first

The verse-aligned Ibn Kathir records live in `tafsir-ibn-kathir/NNN.txt`
(`## C:V` sections). Batch work reads them through a JSON index:

```bash
python3 scripts/editorial/ik_index.py   # writes /tmp/ik_idx.json (~68 MB)
cp /tmp/ik_idx.json ~/ik_idx.json       # /tmp may be wiped; keep a persistent copy
```

Index shape: `idx["<ch>"]["<verse>"]` → plain-text record (Arabic collapsed).
Verify: `python3 -c "import json; d=json.load(open('/home/user/ik_idx.json')); print(sorted(d['5'], key=int)[:3])"`.
Byte-identical records across a verse range = one shared block: read once,
place evidence once at the verse it concerns (R1.4).

## R12.2. Step 1 — map the range

```bash
grep -n '^## Verse <N>:' "markdown commentry/<NNN>.md"   # header line numbers
```

Record the batch's first-header line and the next batch's first-header line
(or EOF). Confirm every verse in range already has ≥2 `**Headings**`; log any
`H_MISSING` for repair in the splice script.

## R12.3. Step 2 — whitespace audit (before touching anything)

Save as `/tmp/audit_<batch>.py`, set the two header markers, run it:

```python
import re
P = '/home/user/quran-explained/markdown commentry/<NNN>.md'
lines = open(P, encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if l.startswith('## Verse <N>:<A>'))
end = next(i for i, l in enumerate(lines) if l.startswith('## Verse <N>:<B+1>'))  # or len(lines) at EOF
issues = []
for i in range(start, end):
    l = lines[i]
    if l.startswith('## Verse '):
        if lines[i+1].strip() == '':
            issues.append(('HDR_AFTER_BLANK', i+1, l))
        if lines[i+1].startswith('>'):
            j, blanks = i + 2, 0
            while lines[j].strip() == '':
                blanks += 1; j += 1
            if blanks != 1:
                issues.append((f'QUOTE_AFTER_BLANKS={blanks}', i+1, l))
    if l.strip() == '' and lines[i+1].strip() == '':
        if lines[i-1].strip() != '':
            issues.append(('DOUBLE_BLANK', i+1, repr(lines[i-1][:60])))
    if l.startswith('**') and lines[i-1].strip() != '' and not lines[i-1].startswith('## Verse'):
        issues.append(('H_MISSING_BEFORE', i+1, l[:60]))
for k, ln, ctx in issues:
    print(f'{k} @L{ln}: {ctx}')
print(f'TOTAL: {len(issues)}')
```

Log every flag. Standard repairs, applied first inside the splice script:
`\n\n\n**` → `\n\n**` (with an exact-count assert), blank after `## Verse`
header removed, blank between `---` and next `## Verse` removed.
("After" in the flag name means the blank sits AFTER the header/quote line.)

## R12.4. Step 3 — read IK blocks, then current text, then lock

1. Dump the batch's IK records to scratch files (one per verse or per shared
   block) and read them all.
2. Read the current commentary for all 50 verses. For speed, print a headings
   map first (verse → heading lines), then read full text in ~6-verse chunks.
3. **Lock decisions per verse before writing anything**: for each verse, note
   the target heading, the 1–3 paragraphs to add, and which cross-references
   they need — or SKIP with a reason (already covered / paraphrase-only /
   trivia per R2). No verse is left unconsidered.

## R12.5. Step 4 — fetch exact Qur'an wordings

Quotations come only from `data/chapter_<NNN>.js` (`var chapterData_N`).
Lookup keys are `"ayah_no_surah": <V>` + `"ayah_en"` (there is no
`verse_number` key). Save as `/tmp/wv.py`:

```python
import re, sys
def w(s, v):
    t = open(f'data/chapter_{s:03d}.js', encoding='utf-8').read()
    m = re.search(r'"ayah_no_surah":\s*%d,\s*"ayah_ar":\s*".*?",\s*"ayah_en":\s*"(.*?)"' % v, t, re.S)
    return m.group(1) if m else 'NOT-FOUND'
for ref in sys.argv[1:]:
    s, v = ref.split(':'); print(f'[{ref}] {w(int(s), int(v))}')
```

```bash
python3 /tmp/wv.py 2:61 2:285 17:90   # all refs the batch will quote
```

Quote the clause under discussion, copied byte-exact (R7). **Watch for
U+00A0 non-breaking spaces inside stored wordings** (seen in 15:6, 21:91):
a quote that looks identical but uses a normal space fails verbatim.
Already-quoted refs are cited bare (`(3:93, quoted above)`), never re-quoted
in the same section.

## R12.6. Step 5 — one splice script for the whole batch

Never hand-edit 50 sections. Write `/tmp/batch_<x>_add.py`:

1. Slice the file from the batch's first `## Verse` header (to next batch's
   header or EOF); apply repairs first with exact-count asserts.
2. Split the slice into verse sections; define `OPS = [(verse, anchor_heading
   | None, [paras])]` — each op inserts its paragraphs before the anchor
   heading (`'\n\n' + anchor`, asserted unique in its section) or, for
   `None`, before the section-closing `---`.
3. **Section-end anchor key must be `'\n\n---'`** (replaced with
   `'\n\n' + paras + '\n\n---'`). Using `'\n---'` leaves a double blank
   above the insert and drops the blank below it (paid for on ch 4 batch P).
4. Insert lists keep their trailing structure so inserted paragraphs never
   abut the next heading (paid for on ch 4 batch N: 83 flags).
5. Never iterate `re.finditer` over a string being mutated in the loop;
   never run an edit and its verification in one parallel block — sequence
   and confirm each step.

## R12.7. Step 6 — pre-check every quote BEFORE running the splice

Extract every `(REF — *“…”*)` from the splice script and confirm the inner
text is a verbatim substring of that verse's `ayah_en`:

```python
import re
scr = open('/tmp/batch_<x>_add.py', encoding='utf-8').read()
qs = re.findall(r'\((\d{1,3}:\d{1,3}) — \*“(.*?)”\*\)', scr)  # non-greedy: inners may nest “…”
def verse(s, v):
    t = open(f'data/chapter_{s:03d}.js', encoding='utf-8').read()
    return re.search(r'"ayah_no_surah":\s*%d,\s*"ayah_ar":\s*".*?",\s*"ayah_en":\s*"(.*?)"' % v, t, re.S).group(1)
bad = [(r, i[:60]) for r, i in qs if i not in verse(*map(int, r.split(':')))]
print(len(qs), 'quotes,', len(bad), 'bad', bad)
```

Fix every `bad` entry (usually spacing/NBSP or a paraphrase slip), then run
the splice script. A greedy `(.*)` here merges multi-quote paragraphs and
reports false misses — always non-greedy.

## R12.8. Step 7 — gates: audit → verifier → diff review

```bash
python3 /tmp/audit_<batch>.py            # expect TOTAL: 0
python3 scripts/editorial/verify_quotes.py  # expect FAIL with ONLY gained citations:
```

Pre-commit verdict must show: `wordings not verbatim: 0`,
`citations lost: 0`, `Bible citations given a Qur'an quote: 0`,
`hand-written wordings, no adjacent ref` unchanged from HEAD, and
`citations added` consisting solely of this batch's refs (spot-check the
diff's added `N:M` tokens against the lock list). The FAIL is the guard
working (check 2 fires on any addition vs HEAD) — see WORKLOG §7 note.

Then review: `git diff --stat` (all deletions must be blank lines or logged
repairs), and read 2–3 inserted passages in place for flow (R3).

## R12.9. Step 8 — commit, confirm PASS, push

```bash
git add "markdown commentry/<NNN>.md" && git commit -m "Pass two Batch <X>: Ibn Kathir gap-fill for ch <N> (<N>:<A>-<B>)"
python3 scripts/editorial/verify_quotes.py  # expect RESULT: PASS
git push origin <session-branch>
```

Full R9 suite (`integrity.py`, `build_tafsir_json.py`, `check_ik_quotes.py`,
`factcheck.py` + `sw.js` bump if the payload changed) runs at chapter end,
before the trailer commit. `factcheck.py`: diff `/tmp/factcheck_issues.json` —
each new `AUTH-REVIEW` must be your own new sentence.

## R12.10. Step 9 — chapter-end trailer in WORKLOG §7

After the last batch of a chapter ships, append one table row per batch under
`### Pass-two insertions completed`, then commit the WORKLOG separately
(`Ch <N> pass-two §7 trailer: batches <X>+<Y>+…`) and push. Per-batch stats:

```bash
for c in <hash1> <hash2>; do git show --stat --format='%h %s' $c | head -5
git show --unified=0 $c -- "markdown commentry/<NNN>.md" | grep '^+' | grep -v '^+++' \
  | grep -oE '[0-9]{1,3}:[0-9]{1,3}' | sort -u | tr '\n' ' '; echo; done
```

Row format mirrors existing rows: batch letter, verse span, insertion/repair
counts, refs touched, `all verbatim`, `≥2 H2` confirmation, commit hash.

## R12.11. Why batches go fast (do not skip these)

1. **Decide everything before writing anything.** The lock list (R12.4.3) turns
   the batch into mechanical execution; no verse is re-read.
2. **One script, not fifty edits.** The splice script (R12.6) applies a whole
   batch in one run with asserts that fail loudly on any anchor drift.
3. **Verify mechanically, in layers.** Quote pre-check → audit → verifier →
   diff review catches every defect class before commit; post-commit
   re-verification is then a formality.
4. **Know the false alarms.** `��` in terminal output is unrendered UTF-8
   (’ “ —), not corruption — byte-verify with `repr()` before reacting.
   `git diff --stat` gross insertions/deletions can differ ±1 from the script's
   own counts when blank lines shift between hunks; the net must reconcile.
   Verifier "citations added" may undercount bare mid-sentence refs; what
   matters is 0 bad / 0 lost / flat unaccounted.

# R13. Multi-agent split

Chapters are the unit of parallelism. Each agent owns whole chapters;
ranges never overlap and no agent touches another's chapter file.

1. The coordinator assigns chapters and one branch per agent, all cut from
   the same `main`. Agents never switch to, create, or push to any other
   branch.
2. Batch letters are global and assigned by the coordinator up front
   (ch 5 = Q–S, ch 6 = T–V, …) so commit subjects never collide.
3. Each agent appends only its own chapters' rows to the WORKLOG §7 table at
   chapter end. If two agents finish simultaneously, the second to push
   rebases onto the first's trailer commit — rows are append-only, so this
   is always trivial.
4. The coordinator merges branches to `main` in chapter order after each
   chapter's full R9 suite passes on its branch.
5. Every agent reads this file end-to-end before starting; the gates in
   R12.8–R12.9 are identical on every branch and non-negotiable.
