# Pass-Two Batch Agent — Self-Contained Instructions

You are a batch agent for the Qur'an commentary project. Everything you need
is in this file. Your coordinator's message gives you four values:
**BRANCH, CHAPTER, START VERSE, FIRST BATCH LETTER**. Do not proceed until
you have all four.

## 0. Assignment slots (filled by the coordinator's message)

- Branch: `________________` — work ONLY here. Commit here, push only here
  (`git push origin <branch>`). Never switch to, create, or push to any
  other branch. Never touch `.git`.
- Chapter: `________` (file `markdown commentry/<NNN>.md`, 3 digits).
- Start verse: `________` (1 unless resuming mid-chapter).
- First batch letter: `________` (each batch takes the next letter: Q, R,
  S…). Batch letters are globally unique — use exactly the letters assigned.

## 1. Setup

```bash
git checkout <branch> && git status   # must be clean before you start
python3 scripts/editorial/ik_index.py # builds /tmp/ik_idx.json (~68 MB)
cp /tmp/ik_idx.json ~/ik_idx.json     # /tmp may be wiped; use the copy
python3 -c "import json; d=json.load(open('/home/user/ik_idx.json')); print(len(d['<ch>']))"
# last number must equal the chapter's verse count
```

Key paths (repo root = your working directory):

| Path | What it is |
|---|---|
| `markdown commentry/<NNN>.md` | YOUR ONLY EDIT TARGET. Commentary, `## Verse C:V` sections each with a `> ...` blockquote, `**Headings**`, prose, closing `---` |
| `tafsir-ibn-kathir/NNN.txt` | Ibn Kathir source (`## C:V` records). Read via `~/ik_idx.json`, not raw |
| `data/chapter_<NNN>.js` | Qur'an text. ONLY source for quoted wordings (`"ayah_no_surah": V` + `"ayah_en"`; there is NO `verse_number` key; files are `var chapterData_N`, 3-digit) |
| `scripts/editorial/verify_quotes.py` | THE gate. See §6 |
| `scripts/editorial/integrity.py`, `check_ik_quotes.py`, `scripts/factcheck.py`, `scripts/build_tafsir_json.py` | Full suite, run at chapter end |
| `tafsir-ibn-kathir/WORKLOG.md` §7 table | Where you log finished batches (chapter end only) |
| `SECOND_PASS_RULES.md` | Full editorial rules; this file's §§2–3 summarise what binds you |

## 2. What you are producing (quality bar — non-negotiable)

For EVERY verse from START VERSE to the chapter's end, in order, with no
sampling: read its Ibn Kathir record against its commentary section and add
whatever verse-aligned evidence is missing — prophetic reports (collection +
narrator), Companion/Tabi`i/scholar glosses, occasions of revelation, variant
readings / language points. SKIP only what the section already covers equally
well, what is mere paraphrase, or what is trivia with no reader payoff.

1. **Every verse considered, ≥2 `**Headings**` per verse.** Heading form is
   fixed: bold line standing alone with a blank line before AND after.
   `**H**\nText` (no blank) does not render — always blank-separate.
2. **Additions read as part of the section**, woven in with attribution in
   the sentence (never an `Ibn Kathir says:` label stapled on). Simple
   English, short sentences. The whole chapter must agree with itself —
   never contradict what an earlier verse settled; tell shared stories once
   and refer.
3. **Attribution honesty.** Never invent a hadith number. Never attribute to
   the Prophet ﷺ a witness account, Companion ruling, or scholar gloss.
   Unclear speaker → leave the report out. Grade only when the source grades.
4. **Never touch:** the `> ...` verse blockquotes (byte-identical always);
   any existing `(chapter:verse)` citation or its wording; verse counts,
   file names, section order, app code, translations.
5. **Qur'an wordings come ONLY from `data/chapter_NNN.js` `ayah_en`** — never
   from Ibn Kathir's English paraphrase. Quote the clause under discussion:
   `(4:51 — *“…”*)`, one wording beside its own reference. Refs already
   quoted in the same section are cited bare: `(3:93, quoted above)`.

## 3. The batch loop (50 verses, one commit per batch)

Ranges are fixed fifties from YOUR start (1–50, 51–100, …); the chapter's
final partial batch ships whole. **Never split a batch; take longer instead.**

### Step 1 — Map the range

```bash
grep -n '^## Verse <N>:' "markdown commentry/<NNN>.md"
```

Record the batch's first-header line and the next header after the batch
(or EOF). Confirm ≥2 headings per verse; log gaps as repairs.

### Step 2 — Whitespace audit BEFORE touching anything

Save as `/tmp/audit_<letter>.py`, set the two `## Verse` markers, run:

```python
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

Log every flag. Standard repairs (applied first in the splice script):
`\n\n\n**` → `\n\n**` with an exact-count assert; blank after `## Verse`
header removed; blank between `---` and the next `## Verse` removed.

### Step 3 — Read everything, then LOCK (this is what makes it fast)

1. Dump the batch's IK records from `~/ik_idx.json` to scratch files and
   read them all. Byte-identical records across verses = ONE shared block:
   read once, place evidence once at the verse it concerns.
2. Read the current commentary for all 50 verses (print a verse→headings map
   first, then read full text in ~6-verse chunks).
3. **Write a lock list before composing anything**: per verse, the target
   heading + the paragraphs to add + refs needed — or SKIP with a reason.
   No verse unconsidered. You never re-read after this point.

### Step 4 — Fetch exact wordings for every ref you will quote

```bash
python3 /tmp/wv.py 2:61 2:285 17:90   # list every ref the batch will quote
```

`/tmp/wv.py` (create once, reuse):

```python
import re, sys
def w(s, v):
    t = open(f'data/chapter_{s:03d}.js', encoding='utf-8').read()
    m = re.search(r'"ayah_no_surah":\s*%d,\s*"ayah_ar":\s*".*?",\s*"ayah_en":\s*"(.*?)"' % v, t, re.S)
    return m.group(1) if m else 'NOT-FOUND'
for ref in sys.argv[1:]:
    s, v = ref.split(':'); print(f'[{ref}] {w(int(s), int(v))}')
```

Copy clauses byte-exact. **Stored wordings may contain U+00A0
non-breaking spaces** (seen in 15:6, 21:91) — a lookalike with normal
spaces fails verification.

### Step 5 — ONE splice script for the whole batch (never 50 hand-edits)

Write `/tmp/batch_<letter>_add.py`:

1. Slice the file from the batch's first `## Verse` header (to the next
   batch's header or EOF). Repairs first, exact-count asserts.
2. Split into verse sections; `OPS = [(verse, anchor_heading | None,
   [paras])]`; insert before `'\n\n' + anchor` (asserted unique in its
   section) or, for `None`, before the section-closing `---`.
3. **End-of-section anchor key MUST be `'\n\n---'`**, replaced with
   `'\n\n' + paras + '\n\n---'`. (`'\n---'` corrupts the blank lines —
   paid for on ch 4 batch P.)
4. Inserted paragraphs must never abut the next heading — keep the blank
   line between the last inserted paragraph and the anchor.
5. Never mutate a string while iterating `re.finditer` over it. Never run a
   file edit and its verification in one parallel block — sequence them.

### Step 6 — Pre-check EVERY quote, THEN run the splice

```python
import re
scr = open('/tmp/batch_<letter>_add.py', encoding='utf-8').read()
qs = re.findall(r'\((\d{1,3}:\d{1,3}) — \*“(.*?)”\*\)', scr)  # NON-greedy: inners nest “…”
def verse(s, v):
    t = open(f'data/chapter_{s:03d}.js', encoding='utf-8').read()
    return re.search(r'"ayah_no_surah":\s*%d,\s*"ayah_ar":\s*".*?",\s*"ayah_en":\s*"(.*?)"' % v, t, re.S).group(1)
bad = [(r, i[:60]) for r, i in qs if i not in verse(*map(int, r.split(':')))]
print(len(qs), 'quotes,', len(bad), 'bad', bad)
```

Fix every `bad` entry, then run the splice script. (Greedy `(.*)` merges
multi-quote paragraphs into false misses — always non-greedy.)

### Step 7 — Gates (mandatory, in order)

```bash
python3 /tmp/audit_<letter>.py              # expect TOTAL: 0
python3 scripts/editorial/verify_quotes.py  # expect FAIL showing ONLY gained citations:
```

Pre-commit verdict MUST read: `wordings not verbatim: 0`,
`citations lost: 0`, `Bible citations given a Qur'an quote: 0`,
`hand-written wordings, no adjacent ref` unchanged from HEAD, and
`citations added` = exactly this batch's refs (cross-check the diff's added
`N:M` tokens against your lock list). This FAIL is by design — check 2
fires on any addition versus HEAD.

Then: `git diff --stat` (every deletion must be a blank line or a logged
repair) and read 2–3 inserted passages in place for flow.

### Step 8 — Commit, confirm PASS, push, report

```bash
git add "markdown commentry/<NNN>.md"
git commit -m "Pass two Batch <letter>: Ibn Kathir gap-fill for ch <N> (<N>:<A>-<B>)"
python3 scripts/editorial/verify_quotes.py  # expect RESULT: PASS
git push origin <branch>
```

Report back (see §5), then start the next batch without waiting.

### Step 9 — Chapter end: full suite + WORKLOG trailer

After the last batch: run `integrity.py` (6,236 sections, 0 mismatches),
`build_tafsir_json.py`, `verify_quotes.py` (PASS), `check_ik_quotes.py`
(PASS), `factcheck.py` (diff `/tmp/factcheck_issues.json` — every new
`AUTH-REVIEW` must be your own new sentence). Bump `sw.js`
`CACHE_VERSION` if `data/tafsir_*.json` changed.

Append one row per batch to the `### Pass-two insertions completed` table
in `tafsir-ibn-kathir/WORKLOG.md` (batch letter, span, insertion/repair
counts, refs touched, `all verbatim`, `≥2 H2`, commit hash — mirror
existing rows; stats recipe: `git show --stat` + added-`N:M`-token grep per
commit). Commit the WORKLOG separately
(`Ch <N> pass-two §7 trailer: batches <X>+<Y>+…`), push, report DONE.

## 4. False alarms (do not chase these)

- `��` in terminal output = unrendered UTF-8 (’ “ —), NOT corruption.
  Byte-verify with `repr()` before reacting.
- `git diff --stat` gross add/delete counts may differ ±1 from the script's
  own counts when blank lines shift between hunks. The NET must reconcile;
  all deletions must be blank lines or logged repairs.
- Verifier "citations added" may undercount bare mid-sentence refs. What
  matters: 0 bad / 0 lost / unaccounted-unchanged.

## 5. Report-back format (after EVERY batch, then continue)

`Batch <letter> (<N>:<A>-<B>) shipped: <P> insertions, <R> repairs,
audit 0, verify FAIL(gained <G>, 0 bad/0 lost) → commit <hash> → verify
PASS → pushed.` Then, at chapter end: `Chapter <N> DONE: <batches>,
full suite green, trailer <hash>, pushed.`

## 6. Done criteria

Chapter file's last verse is done, every batch committed and pushed on your
branch with post-commit PASS, WORKLOG rows + trailer commit pushed, tree
clean, and you have reported DONE. You do not merge to `main` — the
coordinator does that.
