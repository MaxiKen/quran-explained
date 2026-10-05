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

**Run status:** The original Sūrah 2 run through **2:100** and the continuation through **2:200** are
complete. The authorized extension through **2:286** is now appended to `2/al-baqarah.md` and audited.
Every entry in 2:201–2:286 exceeds 800 commentary-prose words and 20 inline source-tag occurrences,
with all seven approved sources cited in each entry. The 2:271–2:280 prose/tag counts are 2:271 855/69;
2:272 860/60; 2:273 842/63; 2:274 849/64; 2:275 945/71; 2:276 839/61; 2:277 834/61;
2:278 861/70; 2:279 839/63; 2:280 853/60. The final six counts are 2:281 862/49; 2:282 1,042/66;
2:283 917/61; 2:284 864/57; 2:285 869/69; 2:286 960/79. Reported chronology at 2:281 is qualified;
the weak wealth/asceticism anecdote at 2:283, disputed Miʿrāj occasion report at 2:285, and Israelite
examples at 2:286 are flagged. Legal digressions in 2:282–2:283 are marked. Earlier digressions at
2:272–2:280 also remain flagged: theology at 2:272, legal discussions at 2:273, 2:275, 2:279, and 2:280,
and Maʿārif’s modern economic excursus at 2:275–2:276. The Study Quran coverage
for 2:281 is in the adjacent 2:280–2:281 block, and its 2:285–2:286 discussion covers both verses;
there is no separate Study Quran block for 2:286. The 2:279 Study Quran discussion remains in the
adjacent 2:278–2:279 block. The Study Quran section for 2:251 is empty, and the Maʿārif excerpt returned
for 2:259 is misaligned with 2:258; neither was cited for those verses. The separate Ṭabarī 2:251
source-accuracy audit remains incomplete: ranges 7000:18000 and 26000:30000 have not been reviewed.
The separate source-accuracy review of **2:121–2:130** also remains pending. Preserve the Sūrah 3 and 4
deletions.

### 0.1 Starter message — current status

```text
You are continuing the tafsir project in this repo (MaxiKen/quran-explained).

1. Read HANDOVER.md and SPEC.md before making any changes.
2. The authorized Sūrah 2 continuation through 2:286 is complete and appended. The six entries
   2:281–2:286 were audited individually; all exceed 800 commentary-prose words and 20 source tags,
   with all seven approved sources represented. Do not generate another Sūrah 2 batch unless asked.
3. Preserve the separate source-accuracy review of 2:121–2:130 and the outstanding Ṭabarī 2:251
   source ranges 7000:18000 and 26000:30000 as follow-up work. These are separate from completed
   length and citation audits.
4. Cite only source-supported material; preserve qualified chronology/report language and the flags
   for weak, Israelite, and digressive material at 2:281–2:286.
5. Keep the already-requested deletions of `3/al-imran.md` and `4/an-nisa.md`; do not restore them.
6. Work only on `arena/01a10a35-quran-explained`. Do not discard user work with a hard reset.
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
├── 2/al-baqarah.md         # complete through 2:286; source-accuracy follow-ups remain pending
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
8. **Ten-verse iterations.** The original run covered 2:1–2:100 and the first continuation covered
   2:101–2:200 in ten consecutive batches of ten. The user has now authorized 2:201–2:286: continue
   in eight batches of ten, followed by the final six verses. Read, write, check, and save each batch,
   then continue immediately in the same run.

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

## 5. Ten-verse operating cycle (used in 2:1–2:100; apply through 2:286)

The workflow below records the protocol used for the completed 2:1–2:100 run and the continuations
through 2:200 and 2:286.

### Step 0 — Workspace sanity check

```bash
cd /home/user/quran-explained
git branch --show-current
git status --short
python3 /home/user/sect.py sizes 2:261 2:262 2:263 2:264 2:265 2:266 2:267 2:268 2:269 2:270
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

For the first continuation, subsequent batches ran from 2:111–2:120 through 2:191–2:200. For the newly
authorized extension, proceed in batches 2:201–2:210, 2:211–2:220, 2:221–2:230, 2:231–2:240,
and so on through 2:271–2:280, followed by the completed final batch 2:281–2:286. Read ten verses per
full iteration, not one verse per iteration.

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

The 2:101–2:200 continuation and the user-authorized 2:201–2:286 extension have been completed without
a mid-batch check-in; the final six verses were saved and audited. The batch procedure above records the
method used. If a later authorized task is interrupted by a hard system/session limit, report the last
saved verse and exact next verse.

## 6. Effort protocol — generation complete; follow-up reviews remain

- **Original target, now met:** Sūrah 2, verses 2:1–2:100, in ten sequential batches of ten.
- **Completed continuation:** Sūrah 2, verses 2:101–2:200, in ten sequential batches of ten.
- **Completed continuation:** Sūrah 2, verses 2:201–2:286, in eight sequential batches of ten and a final six-verse batch. No verse generation remains in the authorized scope.
- **Read ten verses at every iteration.** For each batch, size and read all seven sources for those
  ten verses, then write and check the ten entries before continuing.
- **User instruction fulfilled:** all authorized batches through 2:286 were completed without a mid-batch
  check-in or pause for approval.
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
- For the original 2:1–2:100 run, count the verse body between headings, including translation and
  labels, but excluding the chapter introduction/header and Arabic written in the heading.
- **Continuation clarification for 2:101–2:200:** count at least 800 words of commentary prose only.
  Exclude the English translation, standalone verse-number marker, commentary labels, and inline source
  tags; audit the 20 source-tag occurrences separately. This stricter prose-only rule applies only to
  2:101–2:200 and overrides the general convention above for that range.
- **New continuation, 2:201–2:286:** the user has not specified a prose-only counting exception, so the
  general body-word convention governs the formal 800-word threshold. To avoid any ambiguity, keep at
  least 800 words of commentary prose per entry where supported by the reviewed sources; count source
  tags separately.

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

For each batch, verify its headings and the two minima **entry by entry**. For the original 2:1–2:100
run, the general body-word count includes translations and labels. For 2:101–2:200, apply the stricter
prose-only count: exclude the translation, standalone marker, labels, and source tags; count source tags
separately. For 2:201–2:286, the user has not specified a prose-only exception; apply the general body
count and separately count source tags. Keep commentary prose above 800 words as a safety margin. A batch
average never compensates for an individual verse below a minimum.

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
    citations = sum(len(re.findall(r'\*\*\[' + re.escape(src) + r'\]\*\*', body)) for src in sources)
    if verse <= 100:
        words = len(body.split())
    else:
        lines = []
        for line in body.splitlines():
            if re.fullmatch(r'\s*\d{6}\s*', line):  # standalone repeated verse marker
                continue
            if re.fullmatch(r'\s*\*“.*”\*\s*', line):  # English translation
                continue
            lines.append(line)
        prose = '\n'.join(lines)
        prose = re.sub(r'\*\*\[(?:' + '|'.join(re.escape(s) for s in sources) + r')\]\*\*', '', prose)
        prose = re.sub(r'(?m)^\*\*[^*\n]+\.\*\*', '', prose)  # labels only, not their paragraphs
        words = len(prose.split())
    rows.append((verse, words, citations))
for verse, words, citations in rows:
    if 1 <= verse <= 286:
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
`2/al-baqarah.md` is complete through 2:286; do not recreate or overwrite it from 2:1. The user-authorized
continuation, including the final six verses, is finished. Preserve the deletions of Sūrahs 3 and 4. The separate source-accuracy reviews of 2:121–2:130 and the
remaining Ṭabarī 2:251 ranges 7000:18000 and 26000:30000 are still pending.

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
- The user-authorized continuation covers **2:101–2:200**. All 100 entries are present in
  `2/al-baqarah.md` and independently audited at ≥800 words of commentary prose and ≥20 inline source
  citations each. Across 2:101–2:200 there are **90,839 prose words** and **5,027 source-tag occurrences**.
  The seven approved tafsīr sources were reviewed for each verse; a separate source-accuracy review of
  2:121–2:130 remains pending. The minimum audited prose/tag counts are:

  | Batch | Verses | Minimum prose words | Minimum source tags |
  |---|---|---:|---:|
  | 11 | 2:101–2:110 | 805 | 34 |
  | 12 | 2:111–2:120 | 807 | 45 |
  | 13 | 2:121–2:130 | 823 | 35 |
  | 14 | 2:131–2:140 | 807 | 40 |
  | 15 | 2:141–2:150 | 822 | 36 |
  | 16 | 2:151–2:160 | 847 | 35 |
  | 17 | 2:161–2:170 | 835 | 37 |
  | 18 | 2:171–2:180 | 851 | 44 |
  | 19 | 2:181–2:190 | 1,091 | 66 |
  | 20 | 2:191–2:200 | 855 | 57 |

  The 2:181–2:190 audit found these per-verse prose/tag counts: 2:181 1,169/67; 2:182 1,162/74;
  2:183 1,163/75; 2:184 1,195/74; 2:185 1,160/72; 2:186 1,117/68; 2:187 1,130/69;
  2:188 1,151/71; 2:189 1,091/66; 2:190 1,140/72.
  The final batch, 2:191–2:200, has per-verse prose/tag counts: 2:191 860/57; 2:192 987/70;
  2:193 985/71; 2:194 882/62; 2:195 929/70; 2:196 954/70; 2:197 859/72; 2:198 855/70;
  2:199 922/63; 2:200 898/67.
- The full continuation 2:101–2:286 is present in `2/al-baqarah.md`; all authorized batches are appended
  and audited. Batch scratch drafts remain untracked, including `.batch-251-260.tmp.md`,
  `.batch-261-270.tmp.md`, `.batch-271-280.tmp.md`, and `.batch-281-286.tmp.md`. Keep the Sūrah 3 and 4
  deletions and all scratch files unstaged and out of chapter-content commits. `/home/user/sect.py` is a
  restored and verified convenience copy of `tools/sect.py`.
- Audit of 2:201–2:210 (commentary-prose words / inline source-tag occurrences): 2:201 903/65;
  2:202 926/63; 2:203 917/61; 2:204 921/69; 2:205 901/75; 2:206 902/70; 2:207 962/74;
  2:208 918/72; 2:209 892/69; 2:210 1,078/73.
- Audit of 2:211–2:220 (commentary-prose words / inline source-tag occurrences): 2:211 853/46;
  2:212 924/59; 2:213 1,029/62; 2:214 881/63; 2:215 886/57; 2:216 876/56; 2:217 844/64;
  2:218 867/59; 2:219 934/71; 2:220 893/68. All seven source sections were read for each verse;
  the weak al-Ṭabarī report at 2:216 and the legal digression in al-Qurṭubī at 2:220 are flagged.
- Audit of 2:221–2:230 (commentary-prose words / inline source-tag occurrences): 2:221 911/57;
  2:222 912/59; 2:223 891/63; 2:224 871/59; 2:225 844/69; 2:226 860/67; 2:227 821/60;
  2:228 856/62; 2:229 837/64; 2:230 907/67. All seven source sections were read for every verse;
  variable juristic interpretations are explicitly identified, and the legal digression on *khulʿ* at
  2:229 is marked.
- Audit of 2:241–2:250 (commentary-prose words / inline source-tag occurrences): 2:241 833/64;
  2:242 841/66; 2:243 834/71; 2:244 872/68; 2:245 860/70; 2:246 825/72; 2:247 866/78;
  2:248 910/68; 2:249 860/69; 2:250 844/83. The report details flagged in this narrative are
  distinguished from what the Qur'an states.
- Audit of 2:251–2:260 (commentary-prose words / inline source-tag occurrences): 2:251 900/58;
  2:252 891/59; 2:253 878/64; 2:254 879/59; 2:255 874/64; 2:256 876/63; 2:257 875/66;
  2:258 873/61; 2:259 876/60; 2:260 855/64. The Study Quran has no separate 2:251 block, and
  the Maʿārif excerpt extracted for 2:259 repeats 2:258 material; neither was cited for those verses.
  Reports about the identities and additional narratives in 2:259–2:260 are qualified as uncertain,
  weak, or Israelite where relevant.
- Audit of 2:261–2:270 (commentary-prose words / inline source-tag occurrences): 2:261 952/64;
  2:262 890/64; 2:263 834/64; 2:264 889/62; 2:265 843/67; 2:266 866/61; 2:267 842/60;
  2:268 837/66; 2:269 852/66; 2:270 821/60. All seven sources were reviewed; the reported date
  donation occasion at 2:267 is qualified because one transmitted chain is weak, and the legal excursus
  on zakat at 2:267 and vow-law details at 2:270 are marked as digressions. The Study Quran 2:263 and
  2:265 discussions are contained in adjacent 2:262–263 and 2:264–265 blocks, respectively.
- Audit of 2:271–2:280 (commentary-prose words / inline source-tag occurrences): 2:271 855/69;
  2:272 860/60; 2:273 842/63; 2:274 849/64; 2:275 945/71; 2:276 839/61; 2:277 834/61;
  2:278 861/70; 2:279 839/63; 2:280 853/60. Every entry exceeds both floors and cites all seven
  sources. Reported occasions at 2:273–2:274 and the historical setting at 2:278 are presented as
  transmitted explanations, not as definitive identifications. The Study Quran discussion at 2:279
  shares a block with 2:278. The source digressions are flagged in the text; no weak report is presented
  as an established fact.
- Audit of the final batch 2:281–2:286 (commentary-prose words / inline source-tag occurrences):
  2:281 862/49; 2:282 1,042/66; 2:283 917/61; 2:284 864/57; 2:285 869/69; 2:286 960/79.
  Each entry includes all seven sources. The chronology attached to 2:281 is qualified; the weak
  wealth/asceticism anecdote at 2:283, the disputed Miʿrāj report at 2:285, and the Israelite examples
  at 2:286 are flagged. The legal excursuses at 2:282–2:283 are marked as digressions. Study Quran's
  2:280–2:281 and 2:285–2:286 blocks were used for adjacent verses; its separate 2:286 section is empty.
- The remaining Ṭabarī 2:251 source-review ranges 7000:18000 and 26000:30000 have not been reviewed;
  that source-accuracy audit remains pending, as does the separate 2:121–2:130 review.
- Work remains on `arena/01a10a35-quran-explained`; commits and any requested pushes must target only
  that branch.

**Next action:**
1. Verse-by-verse generation through 2:286 is complete; no further Sūrah 2 entries are pending.
2. Keep the separate source-accuracy review of 2:121–2:130 on the follow-up list.
3. Complete the remaining Ṭabarī 2:251 review at ranges 7000:18000 and 26000:30000 when that
   follow-up is undertaken; do not conflate it with the completed length/citation audit.
4. Preserve the Sūrah 3 and 4 deletions and never include them in a chapter-content commit.

## 13. One-paragraph restatement for the incoming model

The original Sūrah 2 run through 2:100 and the continuation through 2:200 are complete. The user-authorized
continuation through **2:286** is also complete and appended to `2/al-baqarah.md`; every entry in 2:201–2:286
was audited above 800 commentary-prose words and 20 inline source-tag occurrences, citing all seven approved
tafsīr sources. The final six counts are 2:281 862/49; 2:282 1,042/66; 2:283 917/61; 2:284 864/57;
2:285 869/69; 2:286 960/79. Study Quran's adjacent 2:280–2:281 and 2:285–2:286 blocks cover verses with
no separate section. The separate source-accuracy review of 2:121–2:130 and the remaining Ṭabarī 2:251
ranges 7000:18000 and 26000:30000 remain pending; they are not length/citation-audit exceptions. Preserve
the deletions of `3/al-imran.md` and `4/an-nisa.md`, work only on `arena/01a10a35-quran-explained`, and
push only to that branch if pushing is requested.

## 14. Sūrah 3 (Āl ʿImrān) — progress and open items

**Status:** `3/al-imran.md` covers **3:1–3:50** (50 entries). Five batches written so far, each audited
independently. Commentary-prose words / inline source-tag occurrences:

- Batch 1 (3:1–3:10): 3:1 1,532/31; 3:2 1,366/32; 3:3 1,430/28; 3:4 1,212/26; 3:5 1,150/29;
  3:6 1,456/34; 3:7 4,660/62; 3:8 2,297/37; 3:9 1,438/41; 3:10 1,513/35.
- Batch 2 (3:11–3:20): 3:11 1,467/37; 3:12 1,160/29; 3:13 1,997/45; 3:14 2,301/49; 3:15 2,004/39;
  3:16 1,332/33; 3:17 1,216/32; 3:18 2,113/41; 3:19 1,803/32; 3:20 2,038/40.
- Batch 3 (3:21–3:30): 3:21 1,814/46; 3:22 1,123/35; 3:23 1,509/36; 3:24 1,141/31; 3:25 1,162/30;
  3:26 2,441/44; 3:27 1,748/35; 3:28 2,668/65; 3:29 1,030/26; 3:30 1,459/35.
- Batch 4 (3:31–3:40): 3:31 1,721/43; 3:32 1,056/30; 3:33 1,318/40; 3:34 920/33; 3:35 1,190/32;
  3:36 1,746/47; 3:37 1,721/53; 3:38 1,104/34; 3:39 1,506/44; 3:40 1,286/41.
- Batch 5 (3:41–3:50): 3:41 1,583/42; 3:42 1,464/39; 3:43 865/32; 3:44 2,044/41; 3:45 1,975/43;
  3:46 1,574/46; 3:47 1,418/37; 3:48 1,339/40; 3:49 2,781/54; 3:50 1,988/47.

Every entry clears both floors. Totals for 3:1–3:50: **~83,200** commentary-prose words and **1,933**
inline source tags.

**Source-coverage exceptions (recorded, not fabricated away):** Maʿārif al-Qurʾān has **no separate
section for 3:16, 3:17 or 3:25** — the block `sect.py` returns for 3:16–17 is its 3:15 commentary and the
block for 3:25 is its 3:23–25 commentary, both cited at 3:15 and 3:23–24 respectively and deliberately
not re-cited for their neighbours (§8, pitfall 7). A `*Source note:*` line recording this sits in each of
the three entries (added at batch 5 — earlier batches had omitted it). The same applies at **3:25**, where Maʿārif's 3:23–25 block has
nothing separate for the verse — its substance is cited at 3:23 and 3:24 and a source note says so at
3:25. No other source gap so far.

**Corpus notes for batch 5 (verify before re-citing):** ibnkathir 3:42 = 3:43 = 3:44 (5,533),
ibnkathir 3:45 = 3:46 = 3:47 (4,489) and ibnkathir 3:48 = 3:49 = 3:50 (5,195) — three shared blocks,
assigned by content with a source note in each entry. qurtubi 3:45 = 3:46 (9,897) and
qurtubi 3:48 = 3:49 (6,322). maarif 3:45 = 3:46 (2,643) and maarif 3:48 = 3:49 = 3:50 (1,697).
**study 3:41 is zero-length** (its note on Zachariah's sign sits in the 3:40–41 block, cited at 3:40);
study 3:46 (167) and study 3:43 (392) are very short. Ṭabarī 3:49 (19,904), 3:42 (13,257), 3:44 (13,568)
and 3:41 (11,891) are the largest blocks in the batch. Useful material beyond the 3,000-char truncation:
Ṭabarī 3:49 has the story of the clay bird made for the schoolboys, the "which bird is strongest?"
exchange, and the disagreement over *al-akmah* (Mujāhid = night-blind, Qatādah/Ibn ʿAbbās = born blind,
al-Suddī/al-Ḥasan = blind, ʿIkrimah = bleary-eyed); Qurṭubī 3:45 has the long *al-Masīḥ* / Dajjāl
lexicography and the descent of Jesus at the white minaret east of Damascus; Qurṭubī 3:48 has the four
named raisings of the dead (Sām b. Nūḥ among them — flag as Isrāʾīliyyāt) and the weak Bayhaqī report
of the two-rakʿah prayer with seven names.

**Corpus notes for batch 4 (verify before re-citing):** ibnkathir 3:31 = 3:32 (2,691) and
ibnkathir 3:38 = 3:39 = 3:40 (5,245) — shared, assigned by content with a source note in each entry.
qurtubi 3:35 = 3:36 (10,492) and qurtubi 3:37 = 3:38 (11,672) — shared likewise. maarif 3:31 = 3:32
(1,747); maarif 3:33 = 3:34 (586) is a single unit on why these prophets are named, cited at 3:33 with
a source note at 3:34; maarif 3:35 = 3:36 (1,143). **saadi 3:33 through 3:55 is a single 8,925-char
block** — assign by content and note it. **study 3:34 and study 3:39 are zero-length**: SQ comments on
3:33–34 and 3:38–39 as units, so their notes are split between the paired verses with a source note in
each. study 3:31 (2,310) and 3:37 (3,084) are the longest SQ blocks in the batch. Ṭabarī 3:37 (22,723)
and 3:39 (22,380) are the largest entries in the batch; read in chunks.

**Corpus notes for batch 3 (verify before re-citing):** tabari 3:21 = 3:22 (5,899), qurtubi 3:21 = 3:22
(9,574 — six *masāʾil*, mostly on commanding right), ibnkathir 3:21 = 3:22 (1,690), saadi 3:21 = 3:22
(320), maarif 3:21 = 3:22 (1,096); ibnkathir 3:23 = 3:24 = 3:25 (2,749), saadi 3:23 = 3:24 = 3:25 (888),
maarif 3:23 = 3:24 = 3:25 (860); ibnkathir 3:26 = 3:27 (4,246), saadi 3:26 = 3:27 (1,588);
ibnkathir 3:29 = 3:30 (2,937), saadi 3:29 = 3:30 (1,202), maarif 3:28 = 3:29 = 3:30 (13,016 — a long
excursus on *muwālāt / muwāsāt / mudārāt / muʿāmalāt*, assigned to 3:28 with the closing paragraph used
at 3:29–30). Tabari 3:27 (14,598) and qurtubi 3:26 (10,442) are the largest entries in the batch; read
in chunks. Tabari 3:23 and 3:26 contain long grammatical discussions (iʿrāb of *li-yawmin*; the *mīm*
of *Allāhumma*) and should be read to the end of the relevant *masʾala*.

**Corpus notes for the next batches (verify before re-citing):** duplicate/shared blocks confirmed by
reading — ibnkathir 3:14 = 3:15 (7,099 chars) covering 3:14–15; ibnkathir 3:16 = 3:17 (3,002) covering
3:16–17; ibnkathir 3:18 = 3:19 = 3:20 (7,844) covering 3:18–20; qurtubi 3:16 = 3:17 (6,562);
saadi 3:10 = 3:11 (419), 3:12 = 3:13 (563), 3:14 = 3:15 (999), 3:16 = 3:17 (717); maarif 3:15 = 3:16 =
3:17 (5,808); maarif 3:11 (265) is only a sequence note pointing forward to 3:12. Ṭabarī 3:13 (20,156),
3:14 (22,627) and Qurṭubī 3:14 (23,533) are the largest entries in the batch — read in chunks.

**Branch:** this session operates on `arena/16244062-quran-explained`, not the `arena/01a10a35-quran-explained`
named in §§5, 10 and 13. Do **not** "correct" the branch with `git reset --hard` or `git checkout`.

**Unresolved constraint conflict — needs user confirmation before further Sūrah 3 work.** §§5, 10 and 13
record a standing instruction to preserve the PR #84 deletion of `3/al-imran.md`. The user then instructed
that Sūrah 3 begin at **3:1**, which required recreating that file. It was recreated as a clean new file —
never restored from git history — and committed. The deletion of `4/an-nisa.md` is untouched. The Sūrah 3
half of the deletion constraint is therefore **overridden in the branch history and still awaits the user's
acknowledgement**; do not silently re-delete the file, and do not treat the conflict as settled.

**Pending follow-ups carried over from Sūrah 2:** the source-accuracy review of 2:121–2:130, and the
Ṭabarī 2:251 review ranges 7000:18000 and 26000:30000.
