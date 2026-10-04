# TAFSIR — Continuation Prompt & Operating Manual

**Audience:** the next AI/agent session continuing this project.
**What this is:** a complete description of the task, the exact operations performed, the tools used,
the effort protocol, the pitfalls, and the recovery procedures — sufficient to replicate and continue
the work from the current state without further guidance.
**Companion files:** `SPEC.md` (the binding format spec), `tools/sect.py` (the extractor tool),
`1/al-fatihah.md` and `2/al-baqarah.md` (completed chapters — read a few entries to absorb the house
style before writing).

---

## 0. The task in one paragraph

Produce a **verse-by-verse tafsir of the Qur'an**, one Markdown file per sūrah (`<surah>/<slug>.md`),
in which **every verse gets its own entry** built by reading **seven tafsir sources** — al-Ṭabarī,
al-Qurṭubī, Ibn Kathīr, al-Jalālayn, as-Saʿdī, Maʿārif al-Qurʾān, The Study Quran — and distilling
their **unique** material into a fixed set of labeled blocks with **inline citations**. The chapter is
written **continuously, verse after verse, saving and pushing as you go**, in long runs (50–100+
verses per session, repeated read→write→commit cycles), and **without stopping for check-ins**.

Current state at handover: **Sūrah 1 complete (7,010 words), Sūrah 2 complete (296,808 words,
286 entries), Sūrah 3 not started.** Next action is to open `3/al-imran.md` and begin at 3:1.

### 0.1 Starter message — paste this to the incoming AI session (copy-paste block)

```text
You are continuing a verse-by-verse Qur'an tafsir in this repo (MaxiKen/quran-explained).

1. Read HANDOVER.md and SPEC.md in full — they are the operating manual and the binding format spec.
2. Copy the extractor tool out for convenience:  cp tools/sect.py /home/user/sect.py
3. Run the sanity check in HANDOVER.md §5 Step 0 (git status/log, wc -w 2/al-baqarah.md,
   grep -c '^## 2:' 2/al-baqarah.md, sect.py smoke test). If the workspace looks reset, follow §11 first.
4. Completed so far: 1/al-fatihah.md and 2/al-baqarah.md (286 entries, complete). Do NOT rewrite them.
5. Then write Sūrah 3 (3/al-imran.md) from 3:1, following HANDOVER.md §5 (read→write→commit→push cycle)
   and §7 (blocks, citations, flags, length).
6. Work in one continuous run: aim for 50–100+ verses per session, one commit per verse (or small group),
   push after each. Never pause for check-ins, never stop after a few verses, save as you go.
7. Branch: stay on the session's branch and push to it only (e.g. origin/arena/01a101f2-quran-explained).
   Keep PR #79 (or the open PR from that branch) current.
```

---

## 1. Deliverable & layout

- One book file per chapter: `1/al-fatihah.md`, `2/al-baqarah.md`, `3/al-imran.md`, …
  (lowercase transliterated slug; no spaces).
- Each file opens with a **sūrah header** (see §7.1) and then one entry per verse.
- **Entry heading:** `## N:M` (chapter:verse). Sūrah 1 also puts the Arabic verse text in the
  heading; Sūrah 2 uses the plain number plus an italic English translation on the next line.
  Either is acceptable; the verse number must be present and machine-greppable as `^## N:M`.
- **Inline citations**, bold-bracketed, at the exact point a source's material is used:
  **[Ṭabarī]** **[Qurṭubī]** **[Ibn Kathīr]** **[Jalālayn]** **[Saʿdī]** **[Maʿārif]** **[Study Quran]**.
- **No per-source files. No master merge. No coverage/audit lines.** The chapter file is the product.

**Repo map:**

```
quran-explained/
├── SPEC.md                 # binding format spec (7 sources, blocks, rules)
├── HANDOVER.md             # this file — continuation prompt & operating manual
├── tools/sect.py           # per-verse corpus extractor (all reading goes through it)
├── 1/al-fatihah.md         # ✅ complete
├── 2/al-baqarah.md         # ✅ complete (286 entries)
├── 3/…                     # ⏭️ create 3/al-imran.md and start at 3:1
├── tafsir-al-tabari/       # corpora (read-only): NNN.txt per sūrah
├── tafsir-al-qurtubi/
├── tafsir-ibn-kathir/
├── tafsir-al-jalalayn/
├── tafsir-as-saadi/
├── tafsir-maarif-ul-quran/
└── tafsir_initial/         # Study Quran: NNN.md
```

---

## 2. Non-negotiable decisions (rejected approaches — do not re-litigate)

1. **Verse-by-verse is mandatory.** Passage/rukūʿ-unit organization was proposed and **rejected**.
   Even where the corpora treat several verses as one unit, each verse still gets its own entry.
2. **Exactly seven sources.** Earlier drafts used six, then eleven. The seven are correct.
   - Restored after deletion: **Maʿārif al-Qurʾān** (keep it; do not remove it again).
   - **Deleted permanently: al-Alūsī, al-Baghawī, Ibn ʿAbbās, Ibn ʿUthaymīn** — do not reintroduce,
     do not read their old corpora even if remnants appear on disk.
3. **10-block entry structure** (§7.2), only blocks that carry real content.
4. **Curated depth, not exhaustive.** Unique material only; repeats collapsed; no drop-logs.
5. **English only** in the book text (Arabic kept for the verse itself and indispensable terms).
6. **Length sized to the verse** (§7.3), not fixed.
7. **Weak / Israelite / digressive material is carried with an italic flag** —
   *(weak)*, *(Isrāʾīliyyāt)*, *(digression)* — not silently dropped, not left unflagged.

---

## 3. Corpora (read-only inputs)

All corpora live in the repo. File per sūrah: `NNN.txt` (Arabic sources) / `NNN.md` (Study Quran).
Each Arabic file is divided by Markdown-ish headings of the form `##### N:M` or `## N:M` — the parser
splits on `^#{1,4}\s*N:M\s*$`.

| # | Book | Folder | Language / notes |
|---|------|--------|------------------|
| 1 | *Jāmiʿ al-Bayān* — al-Ṭabarī | `tafsir-al-tabari/` | Arabic; includes editor footnotes (isnād criticism). Huge: sūrah 2 file alone is multi-MB; individual verses range from ~0.5k to ~69k characters. |
| 2 | *al-Jāmiʿ li-Aḥkām al-Qurʾān* — al-Qurṭubī | `tafsir-al-qurtubi/` | Arabic; fiqh-heavy ("masāʾil"); some verse blocks cover several verses as one (e.g. 2:275–279 is one 63k block). |
| 3 | *Tafsīr al-Qurʾān al-ʿAẓīm* — Ibn Kathīr | `tafsir-ibn-kathir/` | English (OCR'd). Watch for OCR noise; **extract sense, never copy garbled strings**. |
| 4 | *Tafsīr al-Jalālayn* | `tafsir-al-jalalayn/` | English. Short and dense; usually `< 1.2k` chars. |
| 5 | *Taysīr al-Karīm al-Raḥmān* — as-Saʿdī | `tafsir-as-saadi/` | Arabic. Short; often shares one block across neighbouring verses (e.g. 2:267–268, 2:270–271, 2:284–286). |
| 6 | *Maʿārif al-Qurʾān* — Muftī Muḥammad Shafīʿ | `tafsir-maarif-ul-quran/` | English with embedded Arabic. Sections **bleed across verse boundaries**; the `{N}` marker may be missing — search by keyword. |
| 7 | *The Study Quran* — Nasr et al. | `tafsir_initial/` | English. Block structure: verse banner `> **N**`, blocks separated by `\n***\n`. Some verses have a **zero-char section** (verse covered inside a neighbouring block). |

Older corpora (`tafsir/` legacy) may exist on disk but are **not** part of the work — ignore them.

---

## 4. The tool: `tools/sect.py`

A single-file Python 3 script (no dependencies) that splits each corpus by verse and prints any
character-range of any source's section for any verse. **This is the workhorse — every reading and
every size check goes through it.**

Canonical copy: **`tools/sect.py` in this repo**. For convenience copy it out and run from anywhere:

```bash
cp tools/sect.py /home/user/sect.py     # the working path used in all examples below
```

### Modes

```bash
# 1) sizes — character count of each source's section for a list of verses
python3 /home/user/sect.py sizes 287 288 289            # default surah = 2
python3 /home/user/sect.py sizes 3:1 3:2 3:3 3:4        # any surah via S:V

# 2) show — print sections in full (small sources together, big ones separately)
python3 /home/user/sect.py show 259 jalalayn study
python3 /home/user/sect.py show 259 tabari | head -c 1400

# 3) showc — print chars [a:b) of one source's section (chunked reading of big sources)
python3 /home/user/sect.py showc 259 tabari 0 2600
python3 /home/user/sect.py showc 259 tabari 2600 5200
```

### Reading several sources programmatically (for Saʿdī / Maʿārif or custom scans)

```python
from importlib.machinery import SourceFileLoader
m = SourceFileLoader('sect', '/home/user/sect.py').load_module()
for src in ['saadi', 'maarif']:
    s = m.sections(src)['2:257']        # keys are "N:M"
    print(f'=== {src} ({len(s)} chars) ===')
    print(s)
```

### Full source (canonical copy is `tools/sect.py`; reproduced here so nothing is lost)

```python
#!/usr/bin/env python3
"""Per-verse section extractor for the tafsir corpora.

Usage:
  python3 sect.py sizes [S:]V [S:]V ...
  python3 sect.py show <verse> [src ...]        # verse in surah 2 unless S:V given
  python3 sect.py showc <verse> <src> <a> <b>   # chars [a:b) of the section
Sources: tabari qurtubi ibnkathir jalalayn saadi maarif study
"""
import re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))


def _find_repo():
    cands = [
        os.path.join(ROOT, 'quran-explained'),  # script outside repo, repo as sibling
        ROOT,                                    # script at repo root or in tools/
        os.path.dirname(ROOT),                   # script in a subdirectory of the repo
    ]
    for c in cands:
        if os.path.isdir(os.path.join(c, 'tafsir-al-tabari')):
            return c
    return cands[0]


REPO = _find_repo()

SRC_PATHS = {
    'tabari':    ('tafsir-al-tabari', 'txt'),
    'qurtubi':   ('tafsir-al-qurtubi', 'txt'),
    'ibnkathir': ('tafsir-ibn-kathir', 'txt'),
    'jalalayn':  ('tafsir-al-jalalayn', 'txt'),
    'saadi':     ('tafsir-as-saadi', 'txt'),
    'maarif':    ('tafsir-maarif-ul-quran', 'txt'),
    'study':     ('tafsir_initial', 'md'),
}

_cache = {}


def _arabic_sections(path, surah):
    text = open(path, encoding='utf-8').read()
    parts = re.split(r'(?m)^#{1,4}\s*(\d+):(\d+)\s*$', text)
    out = {}
    # parts: [pre, s, v, body, s, v, body, ...]
    for i in range(1, len(parts) - 2, 3):
        s, v, body = parts[i], parts[i + 1], parts[i + 2]
        out[f"{s}:{v}"] = body.strip('\n')
    return out


def _study_sections(path, surah):
    text = open(path, encoding='utf-8').read()
    chunks = text.split('\n***\n')
    out = {}
    cur_key, buf = None, []
    for ch in chunks:
        m = re.match(r'\s*> \*\*(\d+)\*\*', ch)
        if m:
            if cur_key:
                out[cur_key] = '\n***\n'.join(buf).strip('\n')
            cur_key = f"{surah}:{m.group(1)}"
            buf = [ch]
        elif cur_key:
            buf.append(ch)
    if cur_key:
        out[cur_key] = '\n***\n'.join(buf).strip('\n')
    return out


def sections(src, surah=2):
    key = (src, surah)
    if key in _cache:
        return _cache[key]
    d, ext = SRC_PATHS[src]
    path = os.path.join(REPO, d, f'{surah:03d}.{ext}')
    if src == 'study':
        secs = _study_sections(path, surah)
    else:
        secs = _arabic_sections(path, surah)
    _cache[key] = secs
    return secs


def _parse_v(tok, default_surah=2):
    if ':' in tok:
        s, v = tok.split(':')
        return int(s), int(v)
    return default_surah, int(tok)


def cmd_sizes(args):
    verses = [_parse_v(a) for a in args]
    srcs = list(SRC_PATHS)
    print(f"{'verse':>8}" + ''.join(f"{s:>11}" for s in srcs))
    for s, v in verses:
        row = f"{s}:{v:<6}"
        for src in srcs:
            sec = sections(src, s).get(f"{s}:{v}")
            row += f"{(len(sec) if sec else 0):>11}"
        print(row)


def cmd_show(args):
    if not args:
        return
    s, v = _parse_v(args[0])
    srcs = args[1:] or list(SRC_PATHS)
    for src in srcs:
        sec = sections(src, s).get(f"{s}:{v}") or ''
        print(f"\n########## {src} {s}:{v} ({len(sec)} chars) ##########\n{sec}")


def cmd_showc(args):
    s, v = _parse_v(args[0])
    src = args[1]
    a = int(args[2]) if len(args) > 2 else 0
    b = int(args[3]) if len(args) > 3 else 2000
    sec = sections(src, s).get(f"{s}:{v}") or ''
    print(f"##### {src} {s}:{v} [{a}:{b}] of {len(sec)} #####")
    print(sec[a:b])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'sizes':
        cmd_sizes(args)
    elif cmd == 'show':
        cmd_show(args)
    elif cmd == 'showc':
        cmd_showc(args)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
```

> The canonical, executable copy is **`tools/sect.py`** (identical to the listing above). Copy it to
> `/home/user/sect.py` when convenience matters: `cp tools/sect.py /home/user/sect.py`.

---

## 5. The operating cycle (what you actually do, per verse)

### Step 0 — Workspace sanity check (always, at the start of a session)

```bash
cd /home/user/quran-explained
git status --short          # should be clean; untracked leftovers => see §11
git log --oneline -3        # expect the newest "Chapter N: add N:V" commit
wc -w 2/al-baqarah.md && grep -c '^## 2:' 2/al-baqarah.md   # last chapter's counters
python3 /home/user/sect.py sizes 2:257                       # tool smoke test
```
If anything is missing/odd — **recover first** (§11) before writing anything.

### Step 1 — Size the next batch

```bash
python3 /home/user/sect.py sizes 3:1 3:2 3:3 3:4 3:5 3:6 3:7 3:8 3:9 3:10
```
Read ~10 verses' sizes at a time. This tells you which sources are heavy for those verses and how
much chunked reading each will need.

### Step 2 — Read all seven sources for the verse (the reading discipline)

Order that works best (cheap → expensive):

1. **Jalālayn + Study Quran together**, in full:
   `python3 /home/user/sect.py show 3:1 jalalayn study`
2. **Ṭabarī**: head first (`showc 3:1 tabari 0 1500`), then further chunks **only as needed**.
   Sections can run to tens of thousands of chars — read the head, skim forward, take what is unique.
3. **Qurṭubī**: same pattern (head, then chunks). Much of Qurṭubī's bulk is fiqh *masāʾil*; capture the
   rulings and the distinctive reports.
4. **Ibn Kathīr**: read what is legible; extract sense; **never copy OCR-garbled strings**.
5. **Saʿdī**: read whole (usually short). Read via the `importlib` pattern when combined output truncates.
6. **Maʿārif**: read whole or in chunks; remember sections **bleed across verse boundaries** — search
   by keyword if the expected verse text is absent.

Reading is done in **small chunks** with explicit ranges, e.g.:
```bash
python3 /home/user/sect.py showc 3:1 tabari 0 2000
python3 /home/user/sect.py showc 3:1 tabari 2000 4000
python3 /home/user/sect.py showc 3:1 qurtubi 0 2400
```
The `| head -c N` idiom (with its harmless `BrokenPipeError`) is fine for a quick view.

**Discipline:** while reading, keep a running mental (or scratch) list of unique points per source —
you will cite each point to its source, so note *who* said what as you read.

### Step 3 — Write the entry

Build the entry as a Python string, following §7 (blocks, citations, flags, length). Only include a
block if the reading actually supplied content for it; **Meaning** and **Reflection** always.

### Step 4 — Append, verify, commit, push (one command block)

Append-only heredoc pattern (proven; do not use `"""` inside the entry):

```bash
cd /home/user/quran-explained && python3 - <<'PY'
entry = '''

## 3:1

*"Alif Lam Mim."*

**Meaning.** ... **[Ṭabarī]** ... **[Jalālayn]** ...
'''
open('3/al-imran.md','a').write(entry)
print(len(entry))
PY
wc -w 3/al-imran.md && grep -c '^## 3:' 3/al-imran.md \
 && git add -A && git commit -q -m "Chapter 3: add 3:1 (seven sources)" \
 && git push -q origin HEAD && git log --oneline -1
```

- One commit per verse as a rule; one commit for a small group (2–4 verses) is fine when you wrote
  them in one pass (message: `Chapter 3: add 3:5-3:8 (seven sources)`).
- **Grouped verses** are common and accepted (1:2–1:4, 2:262–263, 2:278–279 were committed together).
- The verify step (word count + heading count + `git log -1`) is not optional: it catches the silent
  failure modes (entry not written, heading typo, push rejected).

**Inserting into the middle of a file** (only needed for gap-filling a missed verse):

```python
p = '2/al-baqarah.md'
s = open(p, encoding='utf-8').read()
marker = '\n\n## 2:124\n'
assert s.count(marker) == 1          # fail loudly rather than corrupt silently
s = s.replace(marker, entry + '\n\n## 2:124\n', 1)
open(p, 'w', encoding='utf-8').write(s)
```

### Step 5 — Continue immediately

Next verse. No pause, no summary-to-user required mid-chapter, no check-in. Repeat until the sūrah
is complete or the session's hard limit forces a stop (§6).

---

## 6. Effort protocol — "keep going" (this is the part the user most cares about)

- **Never stop after a few verses.** The user's explicit instruction: *"You're to do everything
  without stopping. Do it in a run. Generate, save (don't stop), continue generating."*
- **Long runs are expected: 50–100+ verses in a single session.** The rhythm is
  *read-10-verses-worth → write → save/commit → continue with the next batch* — repeated cycles,
  **not** one giant read followed by a giant write.
- **Save as you go.** Commit (and push) every verse or small group. Never hold hours of work
  unsaved; the workspace can reset (§11).
- **Never pause for confirmation** between verses or after a batch. Do not present partial chapters
  for review. Do not ask whether to continue.
- When a session's budget is exhausted, stop **only** at a clean, pushed save point and state the
  exact file path, latest commit hash and the next verse to be written — the next session continues
  from there without re-reading completed entries.
- **Do not rewrite old entries** after a workspace reset or a reconnect; the pushed content is the
  source of truth.

---

## 7. Writing standard

### 7.1 Sūrah header (top of every chapter file)

Follow the existing files. Pattern (adapt the facts to the sūrah):

```markdown
# Sūrah 3 — Āl ʿImrān (The Family of ʿImrān)

*200 verses; Madinan. …key facts, names, counts, reported merits, one or two source citations…*

**Sources cited inline:** **[Ṭabarī]** *Jāmiʿ al-Bayān* · **[Qurṭubī]** *al-Jāmiʿ li-Aḥkām al-Qurʾān* ·
**[Ibn Kathīr]** *Tafsīr al-Qurʾān al-ʿAẓīm* · **[Jalālayn]** *Tafsīr al-Jalālayn* · **[Saʿdī]** *Taysīr
al-Karīm al-Raḥmān* · **[Maʿārif]** *Maʿārif al-Qurʾān* · **[Study Quran]** *The Study Quran* (2015).

…a short "The sūrah." paragraph on its structure, themes and context [with citations]…

---

## 3:1
…
```

### 7.2 The ten blocks (only those with content; Meaning & Reflection always)

| Block | Content |
|---|---|
| **Meaning.** | Phrase-by-phrase exposition of the verse — the core. |
| **Context.** | Occasion of revelation / background where the sources give one. |
| **Ḥadīth & āthār.** | Prophetic traditions and sayings of Companions/Successors. |
| **Rulings.** | Legal deductions (fiqh) — only for verses that carry them. |
| **Belief.** | Doctrinal points the verse establishes. |
| **Language.** | Lexical/grammatical notes where the meaning turns on the Arabic. |
| **Cross-references.** | Other Qurʾānic verses that explain or echo this one. |
| **Readings.** | Variant *qirāʾāt*, only where the sense changes. |
| **Stories & occasions.** | Narratives the verse refers to or that the sources attach to it. |
| **Reflection.** | Wisdom, spiritual counsel, practical application — always present. |

Blocks may be merged or renamed slightly when a verse demands (e.g. "Readings" appears as
"**Readings.**", a ḥadīth-heavy block may be titled "**Ḥadīth & āthār — ʿĀshūrāʾ.**"); keep the
bold-label convention.

### 7.3 Length — sized to the verse

- Short verses: ~120–350 words; typical verses: ~350–800; weighty legal/narrative verses
  (2:255, 2:282, 2:285–286, 3:7): ~1,200–2,500 words.
- Observed chapter averages: ch.1 ≈ 1,000 words/verse; ch.2 ≈ 1,040 words/verse
  (296,808 words ÷ 286) — so the target is **substantial**, not skimpy.
- A chapter is "done" when **every** verse has an entry, not when the budget feels spent.

### 7.4 Citations

- Cite at the point of use: `... **[Ṭabarī]**` or `... **[Qurṭubī]** **[Ibn Kathīr]`.
- Attribute accurately. If a point is shared by several sources, cite the ones actually read.
  Do not invent attributions to sources whose sections were empty or unread.
- Qurʾān references given as `(2:255)`; sūra:āya format, no parentheses around the citation name.

### 7.5 Flags

- *(weak)* — a ḥadīth/report the source or its editor grades weak.
- *(Isrāʾīliyyāt)* — Israelite lore carried from the earlier scriptures.
- *(digression)* — a source's aside (polemic, grammar digression, pastoral tangent) worth keeping
  but marked as off the verse's line.
- Flags are italic, in parentheses, placed at the end of the affected material's first sentence or
  clause.

### 7.6 Prose rules

- Unique material only: collapse once whatever later sources copy from earlier ones.
- Every kept point must be a **standalone comprehensible summary** — full sentences, names, numbers
  intact; no cryptic stubs, no bare references.
- Don't log what you dropped. Drop it silently (except flagged categories above).
- Don't quote long Arabic; translate and paraphrase. Arabic stays for verse text and key terms.
- Keep the sources' own disagreements visible ("X said…, Y said…") — the tafsir's value is showing
  the range of readings, not flattening them.

---

## 8. Corpus pitfalls & proven workarounds

1. **Combined `show` of several big sources truncates.** Use `showc`/`head -c` for Ṭabarī and
   Qurṭubī; read Saʿdī and Maʿārif individually via the `importlib` pattern.
2. **`BrokenPipeError` from `| head`** is harmless — ignore it (the tool catches nothing, Python
   prints a traceback; the output before it is valid).
3. **Negative-slice bug:** `t[i-800:i+2200]` around a `find()` near position 0 yields empty output —
   guard with `max(0, i-800)` or positive offsets.
4. **Arabic keyword `find()` often returns −1** (diacritic/spelling variants, e.g. `يمحق` for `يَمْحَقُ`).
   Search short distinctive fragments or read chunks sequentially instead.
5. **Ibn Kathīr is OCR'd** — numerals and names are sometimes garbled. Extract the sense; never copy
   garbled strings into the book.
6. **Maʿārif sections bleed across verse boundaries** and its `{N}` markers are unreliable; search by
   content keyword. Its `002.txt` is ~1.7 MB — never `cat` a whole file; always go through `sect.py`.
7. **Shared/duplicate blocks are normal.** Later sources repeat a whole commentary block under every
   verse heading it covers (e.g. Saʿdī 2:267–268 is one block; Qurṭubī 2:275–279 is one 63k block;
   Ibn Kathīr 2:250–2:252 is one 4,045-char block). **Assign the content to the verses it actually
   discusses** and don't re-read the same block for the neighbouring verse; if a source's section for
   a verse is a duplicate with no new content for that verse, simply don't cite it there.
8. **Study Quran zero-char sections** occur (e.g. 2:39, 2:68–71, 2:73, 2:150, 2:160, 2:173,
   2:192–194, 2:227, 2:251): the verse is covered inside a neighbouring block. Check `sizes` and
   read the neighbouring verse's block if the verse matters.
9. **Ṭabarī/Qurṭubī editor footnotes** are interleaved. They can be genuinely useful (grading of a
   report) — use them for *(weak)* flags — but don't mistake them for the matn.
10. **Sūrah headers of the corpora**: chapter files are `NNN.txt` / `NNN.md`; `sect.py` builds the
    path from the surah number. Sūrah 3 = `003.txt`. Verify with
    `python3 /home/user/sect.py sizes 3:1`.

---

## 9. Quality control (per chapter)

Run before declaring a sūrah complete:

```bash
# 1) every verse present exactly once?
grep -o '^## 3:[0-9]*' 3/al-imran.md | sed 's/## //' | awk -F: '{print $2}' | sort -n > /tmp/v.txt
python3 - <<'PY'
nums = [int(x) for x in open('/tmp/v.txt')]
n = 200                                   # verses in this sūrah
print('missing:', [i for i in range(1, n+1) if i not in nums])
print('dups   :', sorted({i for i in nums if nums.count(i) > 1}))
print('count  :', len(nums), 'max', max(nums))
PY

# 2) counters
wc -w 3/al-imran.md && grep -c '^## 3:' 3/al-imran.md

# 3) leftover warts (bad attributions, placeholders)
grep -n 'sic\|TODO\|FIXME\|PLACEHOLDER' 3/al-imran.md

# 4) push state
git log --oneline -5 && git status --short
```

When a gap is found, fill it with the middle-insert pattern (§5, Step 4) and commit:
`Chapter 3: add 3:122-123 (fill gap; seven sources)`.

---

## 10. Git & PR conventions

- **Work on the session's own branch only** (this project has used
  `arena/01a101f2-quran-explained`; the previous session's branch was similar). Never switch to,
  create, or push any other branch.
- Push frequently: `git push -q origin HEAD` (equals `git push origin <current-branch>`).
- Commit messages:
  - `Chapter N: add N:V (seven sources)`
  - `Chapter N: add N:V-N:W (seven sources)`
  - fixes: descriptive, e.g. `Chapter 2: fix 2:50 attribution (Muslim, not Tabari)`
- Keep a PR open and current. **Post-merge note:** PR #79 was merged into `main` on 2026-10-04
  (merge commit `fd42f04`); `main` now carries sūrahs 1–2, `HANDOVER.md`, `tools/sect.py` and the
  seven corpora, and the legacy static app (`index.html`, `css/`, `js/`, `data/`, …) is retired from
  `main`. Continue on your own session branch and open a **new** PR from it.
  `gh pr view 79` to check; open a new PR from the session branch if none exists.
- Keep generated artifacts out of git beyond the two deliverables per chapter and `tools/`.

---

## 11. Workspace-reset recovery (this happens; be ready)

The whole workspace has been reset to the base commit more than once (repos and helper files vanish).
Symptoms: `2/` gone, `1/` and `SPEC.md` present as **untracked** stale copies, `git log` showing the
old base merge `cd27ba8`, `tafsir-*` folders present but stale, `/home/user/sect.py` missing.

Proven recovery (works, order matters):

```bash
cd /home/user/quran-explained
rm -rf 1 SPEC.md            # stale untracked leftovers from the base checkout
git fetch origin
git reset --hard origin/<session-branch>     # e.g. origin/arena/01a101f2-quran-explained

# verify: numbers must match the handover state (see §12)
wc -w 2/al-baqarah.md && grep -c '^## 2:' 2/al-baqarah.md

# restore the tool
cp tools/sect.py /home/user/sect.py
python3 /home/user/sect.py sizes 2:257       # smoke test: 10038/1508/1884/546/697/226/815
```

After recovery: **do not rewrite or re-generate completed entries.** Only continue from the next
unwritten verse.

---

## 12. Current state & exact next action (as of handover)

**Completed:**
- `1/al-fatihah.md` — 7,010 words; seven-source regeneration; headings `## 1:1`–`## 1:7`.
- `2/al-baqarah.md` — **296,808 words; 286 entries; 2:1–2:286 complete**, QC'd (gap at 2:122–123
  filled; 2:50 attribution fixed). Last content commit: **`96d773a`** (pushed).
- Continuation pack: **`HANDOVER.md`** (this file), **`tools/sect.py`**, and the SPEC pointer —
  commit **`c2caf5f`** (pushed). All of the above is **merged into `main`** (PR #79, merge commit
  `fd42f04`, 2026-10-04).

**Not started:** Sūrah 3 (Āl ʿImrān, 200 verses).

**Next action, precisely:**
1. Run the Step 0 sanity check (§5).
2. `git checkout` nothing — you are already on the session branch; `git pull`/fetch if needed.
3. Create the header of `3/al-imran.md` per §7.1.
4. `python3 /home/user/sect.py sizes 3:1 3:2 3:3 3:4 3:5` (surah 3 works — verified; 3:1–3:2 share
   Qurṭubī's block at 9,947 chars, Maʿārif 5,100 at 3:1, Study Quran starts empty at 3:1 and 3:2).
5. Begin the 3:1 entry (the *ḥurūf muqaṭṭaʿāt*, `الم`), then continue **without stopping**.

**Progress counters to keep updating in each handover state note:** cumulative words, entries, last
commit — they are the receipt that the save-as-you-go protocol is working.

---

## 13. One-paragraph restatement for the incoming model

You are continuing a verse-by-verse Qur'an tafsir built from seven named sources into one Markdown
file per sūrah. Every verse gets an entry with labeled blocks (Meaning and Reflection always; others
as content allows), inline **[Source]** citations, flags for weak/Israelite/digressive material, and
length sized to the verse. You read the corpora with `tools/sect.py` in small chunks, write the entry
with a Python append, then commit and push it immediately, then go straight to the next verse —
dozens to a hundred or more per session, saving as you go, never pausing for check-ins, never
stopping because a batch is finished. If the workspace resets, recover with fetch + reset to the
session branch and continue from the next unwritten verse. The work is complete for Sūrahs 1 and 2;
you begin at **3:1**.
