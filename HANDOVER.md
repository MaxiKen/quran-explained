# TAFSIR — Continuation Prompt & Operating Manual

**Audience:** the next AI/agent session continuing this project.
**What this is:** a complete description of the task, the exact operations performed, the tools used,
the effort protocol, the pitfalls, and the recovery procedures — sufficient to replicate and continue
the work from the current state without further guidance.
**Companion files:** `SPEC.md` (the binding format spec), `tools/sect.py` (the extractor tool), and
`1/al-fatihah.md` (the available completed-chapter style reference). The original Sūrah 2 run through
2:100 is complete (see §12); removals of Sūrahs 3 and 4 are included in the open PR and must stay out of chapter-content commits.

---

## 0. The task in one paragraph

Produce a verse-by-verse Qur'an tafsir, one Markdown file per sūrah, by reading all seven named tafsir
sources and distilling their unique material into labeled blocks with accurate inline citations. Every
verse entry has a **minimum of 800 words and 20 inline source-citation occurrences**; going above both
limits is recommended and advised whenever the sources support further useful exposition. Count every
source tag occurrence, including repeats and multiple tags supporting one point. Never invent citations
or pad with duplicated prose to satisfy a numerical floor.

**Run status:** The original Sūrah 2 run through **2:100** is complete. In the user-authorized
continuation, **2:101–2:130** have now been written and independently audited for at least 800 words of
commentary prose and 20 inline source-citation occurrences per verse. Continue through **2:200**, beginning
at **2:131**, in seven remaining ten-verse batches. Preserve the deletions of Sūrahs 3 and 4.

### 0.1 Starter message — current continuation

```text
You are continuing the verse-by-verse tafsir in this repo (MaxiKen/quran-explained).

1. Read HANDOVER.md and SPEC.md before making any changes.
2. The first run is complete through 2:100 and the continuation is complete through 2:130. Continue
   with 2:131–2:200 in seven consecutive batches of ten, saving and auditing each batch before proceeding.
3. For 2:101–2:200, every entry must have at least 800 words of commentary prose and 20 inline
   source-attribution occurrences. Exclude the translation, marker, labels, and tags from the prose count;
   count each exact source-tag occurrence, including repeats. Qur'anic references do not count.
4. Read all seven approved source corpora per verse, cite only supported material, preserve required
   weak/Israelite/digressive flags, and do not pad or invent citations.
5. Keep the already-requested deletions of `3/al-imran.md` and `4/an-nisa.md`; do not restore them.
6. Work only on `arena/01a10a35-quran-explained`. Do not discard user work with a hard reset. If a hard
   limit prevents completion, report the last saved verse and exact next verse.
```

---

## 1. Deliverable & layout

- One Markdown book per chapter: `<surah>/<slug>.md`.
- Every verse receives its own heading, machine-greppable as `## N:M`; the current file is
  `2/al-baqarah.md`.
- The seven source tags are **[Ṭabarī]**, **[Qurṭubī]**, **[Ibn Kathīr]**, **[Jalālayn]**,
  **[Saʿdī]**, **[Maʿārif]**, and **[Study Quran]**. Cite at the point of use.
- The chapter-level source list does not count toward a verse's citation minimum.
- Do not create per-source files or generated audit files; the chapter file is the deliverable.

**Current repo map:**

```text
quran-explained/
├── SPEC.md                 # binding length, citation, format, and batch rules
├── HANDOVER.md             # operating manual and current progress
├── tools/sect.py           # per-verse source extractor
├── 1/al-fatihah.md         # completed style reference
├── 2/al-baqarah.md         # complete through 2:130; next continuation batch is 2:131–2:140
├── 3/ and 4/               # intentionally absent after user's deletion request
└── tafsir-* / tafsir_initial/ # read-only corpora for seven sources
```

## 2. Non-negotiable decisions

1. **Verse-by-verse is mandatory.** A passage may span adjacent verses, but every verse still gets its
   own numbered entry.
2. **Exactly seven sources.** Use al-Ṭabarī, al-Qurṭubī, Ibn Kathīr, al-Jalālayn, as-Saʿdī, Maʿārif
   al-Qurʾān, and The Study Quran. Do not reintroduce the removed corpora.
3. **Minimums apply to every entry individually:** at least 800 words and at least 20 source-citation
   occurrences. It is recommended and advised to exceed both thresholds when supported.
4. **Count source attributions, not Qur'anic references.** Each individual inline source tag counts
   once each time it appears. Repeated tags count again; a multi-source attribution uses separate tags
   and each tag counts. Do not bundle several source names in one bracket.
5. **Read all seven sources for every verse.** Cite only material actually found in that source; never
   add tags solely to hit the count.
6. **Unique material only.** Collapse repeated reports and copied commentary; retain real differences
   between sources, without duplicating prose.
7. **English prose only**, with Arabic retained for the verse and indispensable terms. Keep weak,
   Israelite, or digressive material only with the required flags.
8. **Ten-verse iterations.** The original run covered 2:1–2:100; the current continuation covers
   2:101–2:200 in ten consecutive batches of ten. Read, write, check, and save each batch, then
   continue immediately in the same run.

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

## 5. Ten-verse operating cycle (used in 2:1–2:100; apply to 2:101–2:200)

The workflow below records the protocol used for the completed 2:1–2:100 run. The same procedure
applies to the user-authorized continuation, 2:101–2:200.

### Step 0 — Workspace sanity check

```bash
cd /home/user/quran-explained
git branch --show-current
git status --short
python3 /home/user/sect.py sizes 2:101 2:102 2:103 2:104 2:105 2:106 2:107 2:108 2:109 2:110
```

The fixed session branch is `arena/01a10a35-quran-explained`. Inspect pre-existing staged changes
before saving. The completed earlier run restored only `2/al-baqarah.md` through 2:100; deletions of
Sūrahs 3 and 4 remain in the PR and must not be mixed into chapter-content commits. Do not run a
destructive reset to make the tree appear clean.

### Step 1 — Size the next ten verses together

First continuation batch:

```bash
python3 /home/user/sect.py sizes 2:101 2:102 2:103 2:104 2:105 2:106 2:107 2:108 2:109 2:110
```

Subsequent batches use 2:111–2:120, 2:121–2:130, and so on through 2:191–2:200. Read ten verses
per iteration, not one verse per iteration.

### Step 2 — Read all seven sources for the ten-verse batch

Use the source sizes to plan output and read every verse from all seven source corpora. Read Jalālayn,
Study Quran, Saʿdī, and other short sources efficiently in batches where practical. For long Ṭabarī
and Qurṭubī sections, use `showc` in manageable chunks and capture only relevant unique material.
Ibn Kathīr is OCR'd: extract the sense and never reproduce garbled text. Maʿārif may bleed across
verse boundaries; search adjacent context where needed. A zero-length Study Quran section may mean
the verse is covered in a neighboring block.

Keep a batch-level scratch outline of each verse's meanings, context, reports, rulings, doctrine,
language, cross-references, readings, stories, reflections, and which source supports each point.
Do not attribute material to a source whose section was empty or unread.

### Step 3 — Write all ten entries in the batch

Use the labeled blocks in §7.2. Every verse needs at least 800 words and 20 individual inline source
tags; above both is recommended and advised. Make the prose useful and accurate rather than padding
it. If a true evidence/word-count exception cannot be resolved from the corpora, do not fabricate;
flag it for review and continue with the next verse.

### Step 4 — Append, audit, and save the batch

Append the ten entries to `2/al-baqarah.md` (creating the chapter header on the first iteration).
Before moving on, verify that all ten headings appear once, and count **each entry separately** for
words and source tags. A sample audit script is in §9. Inspect the diff for unsupported attributions,
misleading claims, duplicated material, and unflagged weak reports. Save the complete ten-verse batch
before starting the next one. The project convention is one commit per batch; only push to the fixed
session branch if the configured remote accepts it.

### Step 5 — Continue immediately

For the current continuation, proceed to the next ten-verse batch without pausing for a check-in; the
ten batches end at 2:200. Save at every clean ten-verse boundary and continue immediately. If a hard
system/session limit prevents completion, report the last saved verse and exact next verse.

## 6. Effort protocol — original run complete; continuation active

- **Original target, now met:** Sūrah 2, verses 2:1–2:100, in ten sequential batches of ten.
- **Current target:** Sūrah 2, verses 2:101–2:200, in ten sequential batches of ten.
- **Read ten verses at every iteration.** For each batch, size and read all seven sources for those
  ten verses, then write and check the ten entries before continuing.
- **One continuous run:** finish all ten iterations without a mid-batch check-in or pause for approval.
  Do not stop merely because an iteration is complete.
- **Save as you go:** save at every ten-verse boundary and continue immediately. Where practical,
  commit each batch to the current branch; never commit or push to another branch.
- **Per-entry floors:** at least 800 words and at least 20 source-citation occurrences for each
  verse. Aim above both. An average across a batch is not enough.
- **Source honesty is mandatory:** do not invent a claim or tag to meet a quota. If a genuine shortage
  remains after reading all sources, flag it accurately and continue.
- If a hard tool or session limit forces a stop, stop only at a saved ten-verse boundary when possible;
  report the last completed verse and the exact next verse.

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

### 7.3 Minimum length and citation count

- Each verse entry must contain **at least 800 words**. The count is per entry, not an average.
- Each verse entry must contain **at least 20 inline source citations**. Count every individual
  source-tag occurrence, including repeats and each tag in a multi-source attribution.
- It is recommended and advised to exceed both limits wherever the source material supports more
  useful explanation.
- Do not add filler or misattribute claims to satisfy a quota. Accurate synthesis takes precedence;
  document a genuine exception rather than fabricate evidence.
- Count the verse body between its heading and the next verse heading. Include translation and labels;
  exclude chapter introduction/header and any Arabic written in the heading.

### 7.4 Citations

- Cite at the exact point of use with a separate tag for every cited tafsir source: `... **[Ṭabarī]**`
  or `... **[Qurṭubī]** **[Ibn Kathīr]**`.
- The minimum is 20 source-tag occurrences in each verse entry. Repeated occurrences count again;
  separate tags in a multi-source attribution each count once. Do not put multiple source names in one
  bracket, and do not count Qur'anic references, hadith collection names, a source list, or an author's
  bare mention as a tafsir-source citation.
- Attribute accurately. If a source did not support the claim or its section is empty/unread, do not
  cite it. A citation count is not a substitute for reading.
- Qurʾānic references use sūra:āya format, e.g. `(2:255)`; source tags remain separate.

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

## 9. Quality control (per ten-verse batch and per chapter)

For each batch, verify its ten headings and the two minima **entry by entry**. For the current first
batch, expected verse numbers are 1–10; adjust the range for later batches.

```bash
python3 - <<'PY'
from pathlib import Path
import re
text = Path('2/al-baqarah.md').read_text(encoding='utf-8')
parts = re.split(r'(?m)^## 2:(\d+)\b.*$', text)
sources = ['Ṭabarī', 'Qurṭubī', 'Ibn Kathīr', 'Jalālayn', 'Saʿdī', 'Maʿārif', 'Study Quran']
rows = []
for i in range(1, len(parts), 2):
    verse, body = int(parts[i]), parts[i + 1]
    words = len(body.split())
    citations = sum(len(re.findall(r'\*\*\[' + re.escape(src) + r'\]\*\*', body)) for src in sources)
    rows.append((verse, words, citations))
for verse, words, citations in rows:
    if 1 <= verse <= 100:
        print(f'2:{verse}: {words} words, {citations} source citations',
              'BELOW MINIMUM' if words < 800 or citations < 20 else '')
PY
```

Also verify no missing or duplicate headings within the batch; check the diff for unsupported citations,
placeholders, copied claims, unflagged weak reports, and accidental edits to the read-only corpora.
Before declaring the 100-verse run complete, confirm that every heading `## 2:1` through `## 2:100`
appears exactly once and all 100 entries meet both minimums. Report total words/citations and per-entry
exceptions (there should be none).

## 10. Git & PR conventions

- **Work only on the fixed session branch:** `arena/01a10a35-quran-explained`. Never switch to,
  create, or push any other branch.
- Save after each ten-verse iteration. If pushing is requested/appropriate, use only
  `git push origin arena/01a10a35-quran-explained`.
- Commit messages:
  - `Chapter N: add N:V (seven sources)`
  - `Chapter N: add N:V-N:W (seven sources)`
  - fixes: descriptive, e.g. `Chapter 2: fix 2:50 attribution (Muslim, not Tabari)`
- Use `gh` for pull-request work when the user asks for it; do not assume a PR number from this older handover.
- Keep generated artifacts out of git beyond the two deliverables per chapter and `tools/`.

---

## 11. Workspace-reset recovery

If files appear missing or the tree looks reset, inspect before acting:

```bash
cd /home/user/quran-explained
git branch --show-current
git status --short
git log --oneline -5
```

Do not use `git reset --hard`, `git checkout`, or other destructive recovery until the current diff and
staged changes have been reviewed and preserved. The current branch is fixed to
`arena/01a10a35-quran-explained`. Restore the helper tool with:

```bash
cp tools/sect.py /home/user/sect.py
python3 /home/user/sect.py sizes 2:1 2:2 2:3
```

The deletions of `3/al-imran.md` and `4/an-nisa.md` are intentional, committed in PR #84, and must be preserved.
`2/al-baqarah.md` is complete through 2:130; do not recreate or overwrite it from 2:1. The current
user-authorized continuation is 2:101–2:200, with 2:131–2:200 still to be written and Sūrahs 3 and 4
remaining deleted.

## 12. Current state & exact next action (2026-10-05)

**Current state:**
- `1/al-fatihah.md` remains the completed style reference; `SPEC.md` remains the binding format and
  acceptance spec.
- `2/al-baqarah.md` now contains complete commentary for **2:1–2:100**, written and audited in ten
  consecutive ten-verse batches. Every verse heading from `## 2:1` through `## 2:100` appears exactly
  once; all 100 entries meet both per-verse minimums. There are no exceptions.
- Final count: **115,639 whitespace-separated words** and **2,853 inline source-attribution occurrences**
  across the 100 entries. The lowest word count is 821 (2:14); the lowest citation count is 20, met by
  2:21, 2:25, 2:28, 2:31–2:34, 2:37–2:38, and 2:46–2:48, 2:50. Counts include repeated tags from the
  seven approved tafsīr sources; Qur'anic cross-references are excluded.
- Per-batch audit minima (lowest words / lowest citations among each ten verses):

  | Batch | Verses | Minimum words | Minimum citations |
  |---|---|---:|---:|
  | 1 | 2:1–2:10 | 840 | 22 |
  | 2 | 2:11–2:20 | 821 | 21 |
  | 3 | 2:21–2:30 | 883 | 20 |
  | 4 | 2:31–2:40 | 838 | 20 |
  | 5 | 2:41–2:50 | 864 | 20 |
  | 6 | 2:51–2:60 | 899 | 26 |
  | 7 | 2:61–2:70 | 902 | 25 |
  | 8 | 2:71–2:80 | 860 | 28 |
  | 9 | 2:81–2:90 | 909 | 27 |
  | 10 | 2:91–2:100 | 926 | 24 |

- Content was committed in ten batch commits on `arena/01a10a35-quran-explained`; the final content
  commit is `823c730` (`Chapter 2: add 2:91-2:100 (seven sources)`). An additional audit fix for 2:33
  is `29b55cd`.
- The user-authorized continuation covers **2:101–2:200**. Verses **2:101–2:130** are now present in
  `2/al-baqarah.md` and independently audited at ≥800 words of commentary prose and ≥20 inline source
  citations each. Minimum audited prose/citation counts are 805/34 for 2:101–2:110, 806/45 for
  2:111–2:120, and 823/35 for 2:121–2:130. Continue without a check-in at 2:131.
- The Sūrah 3 and 4 deletions are part of the open PR and must remain; keep them out of chapter-content
  commits. `/home/user/sect.py` is the convenience copy of `tools/sect.py`.
- Work remains on `arena/01a10a35-quran-explained`, with PR #84 open; new commits and pushes on this
  branch update that PR.

**Next action:**
1. Continue at **2:131**. Write, audit, and save 2:131–2:140, then proceed immediately through 2:200.
2. For every verse in 2:101–2:200, verify ≥800 words of commentary prose and ≥20 inline source tags
   independently; exclude the translation, marker, labels, and source tags from the prose count.
3. Commit the completed batch at each ten-verse boundary. Preserve the deletions of Sūrahs 3 and 4.

## 13. One-paragraph restatement for the incoming model

The first Sūrah 2 run is complete through 2:100; the user-authorized continuation covers 2:101–2:200,
with commentary written and audited through 2:130. Continue at 2:131 in ten-verse batches. Each entry
must independently meet 800 words of commentary prose and 20 inline source citations; exclude the
translation, marker, labels, and source tags from the prose count. Read all seven approved tafsīr sources,
count every exact source-tag occurrence including repeats, and do not count Qur'anic cross-references as
citations. Save and audit each batch, then continue without a check-in. Preserve `3/al-imran.md` and
`4/an-nisa.md` as deleted, work only on `arena/01a10a35-quran-explained`, and push only to that branch.
