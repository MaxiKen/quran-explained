# Remaining work — quran-explained commentary review

Handover notes for continuing the commentary review in a new session.
Written after the batch that emptied the verse-reference-density queue (`99482b0`).

The goal of this project, in the user's words: go through **all 114 chapters** and confirm the
commentary is comprehensive and proportionate to each verse's own length and context (history,
Hadith, rulings, cross-references, story), written in **simple terms a general reader understands**.

---

## 1. Ground rules the user set (do not break these)

1. **Never edit a verse because its text is "too long" or "too wordy".** The user said plainly:
   *"Don't touch any verse because it's words is too much. I will only allow it if the contents
   isn't clear to understand."* Clarity fixes only, never length fixes.
2. **Never drop a reference.** Every `(chapter:verse)` citation that exists in a section must still
   exist after an edit. This is machine-checked on every batch (see §4).
3. **No filler.** An addition must carry real content, not words added to reach a target.
4. **Natural length per verse.** No word-count targets, no padding. The old "≥6× the verse's word
   count" figure was an internal heuristic, not a requirement, and content correctness outranks it.
5. **Keep the elements that matter**: plain meaning, key Arabic word, occasion/sīrah context, Hadith,
   rulings, cross-references, story, theology, application, variant readings, flow, parables/oaths.
6. **Simple English.** Avoid academic word-by-word gloss strings.
7. Work in order 001 → 114, fast, in parallel batches where possible. The live preview must stay up.
8. Status reports must be in plain language (the user said "I don't understand this" to a jargon-heavy
   report) and **must always state what work remains**.

---

## 2. What is already finished

- **Verse-reference-density queue: empty.** No paragraph anywhere in the 6,236 commentary sections
  carries five or more `(chapter:verse)` citations any more. It started at 186 sections.
- **Structural passes done** (whitespace only, no words changed): 160 + 251 + 43 sections had walls of
  citations broken into normal paragraphs.
- **List paragraphs rewritten** into plain sentences: all of 7:197, 77:45, 34:28, 25:76, 4:138, 36:80,
  34:36, 25:77, 22:76, 71:25, 45:3, 38:65, 36:67, 36:51, 36:25, 30:1, 2:262, 2:215, 2:163, 2:141,
  19:98, 18:56, 17:111, plus 2:130, 2:164, 2:173, 2:179, 4:30, 4:36, 4:39, 4:62, 4:143, 5:9, 5:78,
  5:96, 6:14, 6:60, 7:64, 7:191, 7:195, 7:203, 11:1, 21:64, 25:41, 25:62, 34:25, 34:29, 34:30, 36:10,
  36:26, 36:30, 36:34, 36:52, 36:80, 41:49, 48:1, 49:17, 51:14, 51:44, 69:16, 71:19, 72:25, 77:34,
  78:1, 79:14, 114:4.
- **Heading rendering fixed** across the whole corpus: 3,008 sub-headings in 917 sections were being
  rendered as ordinary bold text; each now sits in its own block and renders as a heading.
- **"By this" stiff phrasing**: 42 verses reworded (2:36, 2:39, 2:92, 2:130, 2:173, 2:206, 2:225, 2:231,
  2:277, 3:52, 6:43, 12:12, 13:12, 19:31, 19:41, 19:49, 19:60, 19:88, 19:93, 19:96, 22:42, 23:14, 24:8,
  28:48, 41:8, 41:11, 41:35, 42:41, 45:16, 58:22, 59:20, 77:47, 78:1, 78:8, 78:10, 78:13, 78:17, 78:32,
  79:5, 79:27, 79:43, 111:2).
- **Coverage audit passed**: every verse the app displays (`data/tafsir_NNN.json`) has its own
  commentary section — no gaps in any of the 114 chapters.
- **Long-thin queue closed earlier** as "no padding possible": 2:282, 2:187, 48:29, 74:31, 2:259.
  Do not re-open these to pad them.
- **The long-sentence queue was cancelled by the user** (covered by rule 1).

### 2.1 Every cross-reference now carries its verse wording

The user asked that every Qur'an reference in the commentary show *why it is there*: the actual
wording of the verse, quoted from the translation the app itself ships (`ayah_en` in
`data/chapter_NNN.js`, all 6,236 verses), not from anywhere else. A long verse is not dumped
whole — only the sentence the commentary is actually talking about.

`scripts/add_verse_quotes.py` did this. It picks the wording by matching the words around the
citation against the sentences of the cited verse (light stemming, two shared words required
before a narrow pick is trusted, whole verse only as a last resort). Three shapes were handled:

    (4:51)                          → (4:51 — *“…yet believe in idols and false gods…”*)
    (4:94 gives the rule)           → (4:94 gives the rule — *“…verify it…”*)
    …the command at 7:31            → …the command at 7:31 — *“…”*

Result: **21,764 references given wording**, on top of the 10,449 that already carried one.
Median quote is 117 characters, the longest 479. Deliberately left alone:

- **1,046 references to the verse being commented on** — its wording is in the blockquote three
  lines above. Pass `--include-self` if that is ever wanted.
- **51 Bible citations** (`Mark 12:29`, `Genesis 1:1`, `John 20:17` …). These look exactly like
  Qur'an references and several point at verses that exist, so they are matched by book name and
  skipped. Never remove that guard.
- **479 parentheticals too tangled to touch** — long asides holding two or more references.

Two bad citations were corrected while scanning: `6:176` → `3:176` (25:193 quotes 3:176's
wording; Sūrah 6 has 165 verses) and `27:99` → `15:99` (27:1064, "serve this Lord until
certainty comes"; Sūrah 27 has 93 verses).

Re-run order is always: `scripts/add_verse_quotes.py --apply` → `scripts/build_tafsir_json.py`
→ `scripts/editorial/verify_quotes.py`. The inserter is idempotent (a second `--apply` reports
zero references to fill) and the verifier fails the build if any quote is not verbatim in its
own verse, any citation moved, or any Bible citation was touched.

Current metrics: **6,236 sections · 0 quote mismatches · 0 suspect parentheticals · payload ≈19.46 MB.**
(The payload grew from ≈16.44 MB when every bare cross-reference was given its verse wording — see §2.1.)
Fully rewritten chapters: 42 and 43. Sūrah 36 (Yāsīn) and chapter 4 have had the most individual work.

---

## 3. What remains (in priority order)

### 3.1 Terse citation style — the big one (3,119 sections)
These sections use the older, terse style: `The sūrah says X (4:45)` where the citation is not
attached to a statement, and paragraphs read as lists. This is the same defect the user approved
fixing; it just was not caught by the density test because each paragraph is short.

The heaviest offenders (number = bare citations in one section):

| verse | count | verse | count | verse | count |
|---|---|---|---|---|---|
| 4:139 | 33 | 4:146 | 27 | 36:45 | 24 |
| 36:49 | 30 | 4:68 | 24 | 4:87 | 23 |
| 36:50 | 29 | 36:77 | 23 | 4:49 | 23 |
| 36:60 | 28 | 36:43 | 23 | 36:33 | 23 |

Suggested pace (the user asked for volume): treat the **50 worst sections per batch**, rewrite each
dense paragraph in plain sentences with every citation kept, then run the verification checklist in §4.
Re-measure with `scripts/editorial/queue.py` (or the bare-citation scan shown in §5.4).

### 3.2 "By this" leftovers (43 verses) — probably nothing to do
After the 42 rewrites, 43 commentary-voice uses of "by this" remain, but they are ordinary English of
the form "by this + noun" and read fine, e.g. 11:22 *"the phrase … is used by this sūrah a few verses
earlier"*, 33:7 *"the community addressed by this sūrah"*, 29:48 *"the answer supplied by this verse"*,
44:58 *"encompassed by this verse"*, 12:82 *"completed by this verse"*. The user's original 13-item list
was 2:22, 4:161, 11:22, 11:118, 12:82, 29:48, 33:7, 41:8, 42:41, 44:58 (+ 3 more). Of those, 41:8 and
42:41 have been reworded and the rest are in this "reads fine" group. Confirm with the user before
touching them: they are not unclear, so rule 1 may apply.

### 3.3 Optional item (not started)
A Tirmidhī reference at **7:10** was discussed as a possible Hadith addition but never added.

### 3.4 Recurring verification the user cares about
Re-run at the end of any batch and report in plain words: coverage of all 114 chapters, reference
retention, quote integrity, and what remains un-done.

---

## 4. Standard workflow for every edit batch

```bash
cd /home/user/quran-explained

# 1. pick the target paragraphs (worst first)
python3 scripts/editorial/queue.py            # density queue (currently empty)
python3 scripts/editorial/dense.py 6 4:139 36:49   # show every paragraph with >=6 refs
python3 scripts/editorial/tailinfo.py 4:139   # worst paragraph + refs found only there
python3 scripts/editorial/dump.py 4:139       # full section text + its reference list

# 2. build the replacement text (JSON spec) with an editor; three supported shapes:
#    - scripts/editorial/mk_tail.py     spec {"verse": {"paragraphs":[...], "whole":false, "idx":-1}}
#    - scripts/editorial/patchpara2.py  spec {"4:139": {"keep":[...], "replace":{"12":"new text"}}}
#      (keeps untouched paragraphs by index, replaces the ones you name — the safest option)
#    - scripts/editorial/editphrases.py spec [{"verse":"2:39","old":"…","new":"…"}]  (phrase-level)

# 3. verify references were not lost — READ THE WHOLE OUTPUT, never pipe it to tail
python3 scripts/editorial/checkrefs.py rewNNN.json      # must end: sections missing anything: 0

# 4. apply, rebuild, verify
python3 scripts/editorial/apply_rewrites2.py rewNNN.json # prints "applied N, refused M" (M must be 0)
python3 scripts/build_tafsir_json.py                     # prints total payload size
python3 scripts/editorial/integrity.py                   # must be: sections seen: 6236 quote mismatches: 0
python3 scripts/editorial/scan.py 4                      # must be: SUSPECT parentheticals: 0
for c in $(seq 1 114); do python3 scripts/editorial/scan.py $c | head -1; done | sort | uniq -c

# 5. commit + push (this branch only)
git add -A && git commit -m "…" && git push origin arena/01a0bf1e-quran-explained
```

Whitespace-only structural passes use `scripts/editorial/bulksplit.py <out.json> <threshold> <cap>`:
it splits paragraphs holding more references than `cap` into smaller blocks at sentence boundaries,
never inside a quotation. Always diff-check it first — the section text must be **word-for-word
identical** before and after (comparison recipe in §5.3).

---

## 5. Pitfalls already paid for (do not re-learn these)

1. **`checkrefs.py` counts one reference per bracket.** `(36:26 records the welcome, and 36:27 states
   his place)` registers only 36:26. When you rewrite a paragraph that listed references, give each
   reference **its own brackets**: `(36:26 records the welcome) and (36:27 states his place)`. It
   requires the literal string `(C:Y` to appear in the new text; the words after it are free.
2. **Never pipe `checkrefs.py` into `tail`.** The final line reports how many sections lost something;
   a truncated view once hid a missing reference. Read the full output.
3. **`patchpara2.py` indices are positional.** `dense.py`/`tailinfo.py`/`dump.py` show them; the
   paragraph you want is often *not* the last one (a first attempt at 4:121 and 36:68 rewrote the last
   paragraph, left the dense one, and duplicated material — it had to be redone).
4. **Sub-headings must be their own block.** The app only renders a heading when the bold line stands
   alone between blank lines (`js/app.js` `renderMarkdown`). Write `**Heading**\n\nText`, never
   `**Heading**\nText`. `^(\*\*[^*]+\*\*)\n(?=[^\n])` finds violations; currently there are none.
5. **`mk_tail.py` `idx` semantics**: `ps[:idx] + [new] + ps[idx+1:]`; default `-1` replaces the last
   paragraph and keeps the rest. Never let an edit drop the tail of a section.
6. **JSON specs**: escape newlines (`\n`) — raw newlines in a heredoc-produced JSON raise
   `Invalid control character`. Round-trip through `json.load`/`json.dump` when patching.
7. **Run everything from the repo root** (`cd /home/user/quran-explained`); `mk_*`/`patch*` scripts
   resolve `markdown commentry/` relative to the repo, or use absolute paths.
8. **Never re-run an apply of a stale batch** after later batches edited the same sections, and never
   re-run a `mk_*` script that reads the live corpus after its output has been applied.
9. **Partial applies are normal**: if `apply_rewrites2.py` refuses some sections, fix those references,
   re-apply only the refused ones in a follow-up commit. Do not re-apply the whole batch.
10. **Two corruption bugs** in an older apply script produced doubled `##` headers and a dropped
    separator; they are fixed, but the rule stands: after every apply, confirm the per-file section
    count and `integrity.py` still show **6,236 sections**.

---

## 6. Useful one-off scans

```bash
# sections whose paragraphs hold N references (the density metric)
python3 - <<'PY'
import re, pathlib
CORPUS=pathlib.Path("markdown commentry"); REF=re.compile(r"\(\d{1,3}:\d{1,3}(?:-\d{1,3})?\)")
def body(s):
    out=[];started=False
    for l in s.split("\n")[1:]:
        if not started:
            if l.startswith(">") or not l.strip() or l.strip()=="---": continue
            started=True
        out.append(l)
    t="\n".join(out).rstrip(); return t[:-3].rstrip() if t.endswith("---") else t
from collections import Counter
c=Counter()
for ch in range(1,115):
    for s in re.split(r"\n(?=## )", (CORPUS/f"{ch:03d}.md").read_text(encoding="utf-8")):
        if not re.match(r"## Verse \d+:\d+\s*$", s.split("\n")[0].strip()): continue
        ps=[p for p in re.split(r"\n\s*\n", body(s)) if p.strip()]
        c[max((len(REF.findall(p)) for p in ps), default=0)]+=1
print(dict(sorted(c.items(), reverse=True)[:8]))
PY

# sections that still lean on terse "(verse)" citations (the §3.1 queue)
# bare = (C:Y) or (C:Y-Z) with nothing after it; plain = (C:Y followed by words
```

---

## 7. Repo facts worth knowing

- Commentary source of truth: `markdown commentry/NNN.md`, sections `## Verse C:Y`, then a `>` line
  with the verse, then the body. Sub-headings are `**Like This**` blocks.
- `python3 scripts/build_tafsir_json.py` regenerates `data/tafsir_NNN.json` (the app's data) from the
  markdown. Payload sits around 16.44 MB.
- The app is a static site (`index.html`, `js/app.js`); a preview server can be started with
  `python3 -m http.server 8000 --bind 0.0.0.0` from the repo root.
- Branch for this work: `arena/01a0bf1e-quran-explained` (PR #51, base `main`).
