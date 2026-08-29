# PROJECT HANDOFF — Verse-by-Verse Qur'an Tafsir for an App

**Last updated:** 2026-08-29
**Status:** ACTIVE. Chapter 3 (Āl 'Imrān) is in progress. Verses 1–80 are delivered and verified. Verses 81–90 are next.

---

## 0. HOW TO USE THIS FILE

You are an AI agent picking up an ongoing project. **Read this file in full before doing anything.** It contains everything needed to continue without guessing:

- §1–3 tell you what the task is and the rules that bind it.
- §4 gives the exact file format, so your output matches the 38 files already delivered.
- §5 gives the exact step-by-step workflow, including the verification script and a known bug with a known fix.
- §6–7 inventory the workspace and log every file delivered.
- §8 says exactly where work stopped and what comes next.
- §9 lists every pitfall encountered so far. **Do not repeat them.**
- §12 tells you how to update this file when you finish a batch.

**The single most important instruction: do not auto-continue.** The user authorises one batch at a time. See §3.

---

## 1. THE TASK

The user is building the content layer of a **mobile/web Qur'an app**. For each verse of the Qur'an, the app will display one independent, self-contained commentary record. The user supplies a surah name and the complete English translation of that surah. The job is to produce exhaustive verse-by-verse tafsir, ten verses at a time, one output file per batch, formatted so an application can parse it automatically.

The workspace already contains **38 delivered files covering 373 verses and 432,107 words**.

---

## 2. THE GOVERNING PROMPT

The full master prompt is saved verbatim at:

```
/home/user/Prompt.md
```

**Read `/home/user/Prompt.md` in full before writing anything.** It is the user's own specification and is binding. It was saved at the user's request during this session (their message: *"Create a file. [Prompt.md](http://Prompt.md) save the following in it and after that Continue. A new md file"*), with the entire master prompt pasted inline.

Every requirement in §3 below is extracted from that file. Where §3 and `Prompt.md` differ, `Prompt.md` wins.

---

## 3. STANDING RULES

These are the user's explicit standing instructions. They have never been revised or reversed.

### 3.1 Batch and file discipline

- **Ten verses per batch.** If fewer than ten remain in a surah, explain the remainder and say so in the file.
- **Each batch goes in its own new `.md` file. Batches are never merged.**
- **Never auto-continue to the next batch.** The user must ask. Their message *"Continue. A new md file"* authorises **exactly one** batch and is spent the moment that batch is delivered.
- Filename convention (follow it exactly):
  - `chapter-1-al-fatihah-tafsir-1-7.md`
  - `chapter-2-al-baqarah-tafsir-51-60.md`
  - `chapter-3-ali-imran-tafsir-71-80.md`
  - Pattern: `chapter-{N}-{surah-slug}-tafsir-{first}-{last}.md`

### 3.2 The verse separator (critical for app parsing)

After every verse's commentary, emit the marker `===VERSE-END===` **alone on its own line**, unmodified, with nothing else on the line. It must appear **nowhere else** in the file — never inside commentary.

### 3.3 Each verse is independent

- No verse's commentary may depend on another. A reader opening verse 7 cold must understand it.
- **No cross-verse dependency for essential content.** If verse 6 develops an idea from verse 5, verse 6 must re-explain the development itself.
- May reference other verses, but must supply enough context to stand alone. Prefer *"This verse continues the discussion from the previous verse, where Allah…"* over *"As we discussed above…"*.
- Avoid ending a verse with *"As we will see in the next verse…"* unless genuinely useful.

### 3.4 The supplied translation is the reader-facing text

- The user's supplied English translation is the verse opening, **preserved verbatim, byte for byte**. Never silently rewrite it.
- The Arabic and the tafsir sources govern **interpretation**, not the displayed translation.
- Where the supplied translation misses or adds something important, **explain that in the commentary** and say so explicitly. This has been done consistently — see §10.4.

### 3.5 No formal headings inside verse commentary

- **No** `### Historical Context`, `### Linguistic Analysis`, `### Modern Application`, etc., inside a verse's commentary.
- `## Verse N` labels are allowed and required (see §4).
- Flow naturally, like a teacher speaking. Use **bold lead-in phrases** instead of headings.

### 3.6 No fabrication — absolute

Never invent: hadith, Arabic meanings, scholarly quotations, historical events, asbāb al-nuzūl, consensus, scientific discoveries, manuscript evidence, references, page numbers, volumes, or publication details. Where something cannot be established, say so: *"This detail cannot be established with sufficient certainty."*

### 3.7 Certainty must be graded

Distinguish explicitly between: **explicit meaning / strong interpretation / established scholarly position / disputed interpretation / possible interpretation / speculation.** Use the signal phrases: *"The verse clearly indicates…"*, *"The majority of classical scholars understood…"*, *"Some scholars understood this differently…"*, *"One possible interpretation is…"*, *"We cannot establish this with certainty…"*.

### 3.8 Disagreement must be represented fairly

Where genuine scholarly disagreement exists, give the main positions, the evidence for each, and—where the evidence permits—say which is stronger and why. Do not manufacture disagreement. Do not claim consensus without evidence.

### 3.9 Content coverage per verse

Cover whatever is genuinely relevant, with judgement, not mechanically: simple meaning first, then deeper analysis; Arabic vocabulary/grammar/rhetoric in plain language; Qur'an-explains-Qur'an; authentic Sunnah; Companions and Tābi'ūn; classical tafsir; scholarly disagreement; reliable asbāb al-nuzūl; Makki/Madani context; qirā'āt where material; cautious naskh; fiqh; maqāṣid; science and modern knowledge without forcing; contemporary application; spiritual dimension; common misunderstandings.

### 3.10 Depth follows the verse, not a quota

Exhaustive, never padded. Short verse → shorter commentary. A verse carrying a major theological, legal or historical crux → much longer. Do not repeat the same point in different words to add length.

### 3.11 Tone

Warm, natural, simple English. An experienced teacher speaking. Confident where evidence is strong, humble where uncertain. Not robotic, not a Wikipedia article, not a legal document, not a social-media preacher.

### 3.12 Application must be concrete

Never end with *"we should apply this verse in our lives."* Show what it actually looks like, in realistic situations.

---

## 4. THE EXACT FILE FORMAT

Every delivered file follows this structure **exactly**. Reproduce it.

### 4.1 Skeleton

```
# Surah {Name} ({English name}, {number}) — Verse-by-Verse Tafsir, Verses {first}–{last}

<intro: 2–5 paragraphs, NO heading. Orient the reader to this passage: where it sits in
the surah's argument, what changes here, which threads continue from earlier batches.
Name the cruxes this batch contains.>

---

## Verse {N}

**"<verbatim supplied translation, wrapped in straight double quotes, in bold>"**

In simple terms: <one- or two-sentence plain-English restatement.>

<Commentary. Multiple paragraphs. No formal headings. Bold lead-in phrases instead.
Opens with the simplest meaning, builds to deeper analysis, closes with application
and spiritual significance.>

<marker on its own line — see §4.2>

## Verse {N+1}

... (repeat to the end of the batch)

## Synthesis of the Ten Verses

<A natural synthesis. Do NOT re-list every verse. Show the larger picture: the central
message, how the verses develop the theme, the major lessons, the overall spiritual
significance.>

## Principal Sources Consulted

**Primary**
- The Qur'an, with cross-reference particularly to <a long list of chapter:verse refs>
- The supplied English translation, preserved verbatim as the verse opening in every case

**Hadith**
- <collections and narrations actually relied on>

**Classical tafsir**
- <scholars and the specific contribution each makes — e.g. "al-Jalālayn — the note
  that…", "Ibn Kathīr — the argument that…">

**Other works**
- <fiqh, ʿaqīdah, lexicography, qirā'āt, modern scholarship, sīrah>

**A note on honesty in citation.**
<Paragraph stating no page numbers or publication details are given, because this is a
synthesized commentary not a citation apparatus. Then 2–5 paragraphs naming the places
in THIS batch that required particular care, what is established vs disputed vs
unestablished, and the cautions applied. Then a paragraph noting where the supplied
translation added or chose, and flagging each one.>
```

### 4.2 The verse separator

The marker line is the literal string `===VERSE-END===` on a line of its own, with a blank line before it and a blank line after it. Nothing else on that line.

**⚠️ KNOWN BUG — read §9.1.** The workspace write mechanism converts a line consisting solely of that marker into `---`. The write will succeed and the markers will be **silently gone**. You must check for this every single time and repair it with the script in §5.6.

### 4.3 Commentary style conventions

Established across 38 files; keep them.

- **Bold lead-in phrases** open most paragraphs, replacing what would otherwise be a heading. E.g. `**"When Jesus sensed disbelief from his people."**` — the phrase from the verse, quoted, bolded, then discussed. Or `**The crux, stated plainly.**` / `**Now bring this into ordinary life.**` / `**A necessary caution.**`
- **Arabic is given in transliteration with the Arabic root named**, then explained in plain English: *"The root is w-f-y, whose core meaning is completeness, fulfilment…"*
- **Never derive meaning from roots alone.** State that context determines meaning. Root observations are offered as literary/thematic patterns actually present in the text, not as proof.
- **Cross-references are explained, not listed.** Give the verse and say what it contributes.
- **The "simple terms" paragraph is mandatory** and comes immediately after the bold verse opening.
- **Application sections** use phrases like *"Now bring this into our own lives…"* or *"Bring it into the present…"* and give realistic, concrete, contemporary situations.
- **Threads across the surah are traced and named** — recurring words, roots, and motifs picked up as they recur (see §10.3 for those tracked so far).

### 4.4 Length

Delivered batches run **8,500–16,000 words**, averaging ~11,000. Very short batches (fewer than ten verses) run shorter. Let the verse's richness decide.

---

## 5. THE EXACT WORKFLOW

Follow these steps in order, every batch.

### 5.1 Confirm authorisation

Do **not** start unless the user has asked for a batch in this turn or the immediately preceding turn.

### 5.2 Dump the ten verses verbatim

```bash
cd /home/user && python3 -c "
import json
v=json.load(open('verses-3.json'))
for i in range(81,91):
    print(i, '|', v[str(i)])
    print()
"
```

`verses-N.json` is the **sole authority** for verse openings. Keys are **strings** — cast with `int(k)`. Never retype a verse from memory or from the `.md` translation file.

### 5.3 Research the cruxes

Identify the 3–6 genuine cruxes in the batch (the hard words, the disputed readings, the asbāb, the theological flashpoints). Run `web_search` against them — typically two searches in parallel, then a second pair, and occasionally a third. Search for the **linguistic crux and the scholarly dispute**, not for general summaries.

Record the conclusions in the working notes before writing, because the search results are not saved anywhere.

### 5.4 Write the file

`write_file` to `/home/user/chapter-{N}-{slug}-tafsir-{first}-{last}.md`. Copy each verse opening **byte-for-byte** from the JSON dump.

### 5.5 Verify — always

**Never trust the `write_file` success return.** Run the verifier:

```bash
cd /home/user && python3 - <<'PY'
import json, re, glob

f = 'chapter-3-ali-imran-tafsir-81-90.md'          # <-- change this
txt = open(f, encoding='utf-8').read()
v3  = json.load(open('verses-3.json'))              # <-- and this

print('1. MARKERS on own line:', len(re.findall(r'^===VERSE-END===$', txt, re.M)), '(expect 10)')
print('   anywhere:', txt.count('===VERSE-END==='))
lines = txt.split('\n')
print('   blank-isolated:', all(lines[i-1].strip()=='' and lines[i+1].strip()==''
                                for i,l in enumerate(lines) if l=='===VERSE-END==='))
print('   next heading after each:', [lines[i+2][:30] for i,l in enumerate(lines) if l=='===VERSE-END==='])

print('2. HEADINGS:', re.findall(r'^## (.+)$', txt, re.M))
print('   "## Verse N":', len(re.findall(r'^## Verse \d+$', txt, re.M)), '(expect 10)')

print('3. stray U+02DD:', txt.count('\u02dd'), '| brackets:', txt.count('\u02f9'),'/',txt.count('\u02fa'))

blocks = re.split(r'^## Verse (\d+)$', txt, flags=re.M)[1:]
errs = 0
for i in range(0, len(blocks), 2):
    num, body = blocks[i], blocks[i+1]
    first = body.strip().split('\n')[0]
    m = re.match(r'^\*\*"(.*)\*\*$', first)
    if not m:
        print('  NO BOLD OPENING v'+num, repr(first)[:150]); errs += 1; continue
    got = m.group(1).rstrip('"”'); exp = v3[num].rstrip('"”')
    if got != exp:
        errs += 1
        print('  MISMATCH v'+num); print('    got:', repr(got)[:400]); print('    exp:', repr(exp)[:400])
print('4. openings checked', len(blocks)//2, '| errors:', errs)

i = txt.index('## Verse 81')
print('5. intro separator (should be ---):', repr(txt[i-8:i]))
print('6. WORDS:', len(txt.split()))

tot = 0
for p in sorted(glob.glob('chapter-3-ali-imran-tafsir-*.md'),
                key=lambda x:int(re.search(r'-(\d+)-(\d+)\.md$',x).group(1))):
    s = open(p, encoding='utf-8').read()
    n = len(re.findall(r'^===VERSE-END===$', s, re.M)); tot += len(s.split())
    print(f'   {p}: {n} verses, {len(s.split())} w, strays {s.count(chr(0x02dd))}')
print('   CHAPTER TOTAL:', tot, 'words')
PY
```

**All six checks must pass:**
1. 10 markers, each on its own line, blank-isolated, each followed (after a blank) by `## Verse N` or `## Synthesis…`.
2. Headings are exactly `Verse 51 … Verse 60`, `Synthesis of the Ten Verses`, `Principal Sources Consulted`. No other `##` headings.
3. **Zero** stray U+02DD (`˝`). Brackets balanced (˹ count == ˺ count).
4. All 10 openings byte-match `verses-N.json`.
5. The `---` intro separator before `## Verse {first}` is intact.
6. Word count reported.

### 5.6 Repair the marker bug (do this if check 1 returns 0)

The write mechanism silently turns a lone marker line into `---`. Fix with:

```bash
cd /home/user && python3 - <<'PY'
import re
f = 'chapter-3-ali-imran-tafsir-81-90.md'          # <-- change
t = open(f, encoding='utf-8').read()

first_verse = 81                                    # <-- change
reps = []
for m in re.finditer(r'^## (.+)$', t, re.M):
    title = m.group(1)
    if title in (f'Verse {first_verse}', 'Principal Sources Consulted'):
        continue                                    # keep the intro '---' separator
    seg = t[max(0, m.start()-12):m.start()]
    if seg.endswith('\n\n---\n\n'):
        idx = m.start() - len('---\n\n')
        reps.append((idx, idx+3, title))
    else:
        print('NO --- BEFORE:', title, repr(seg))

print('replacements:', [r[2] for r in reps])
for a, b, _ in reversed(reps):
    t = t[:a] + '===VERSE-END===' + t[b:]
open(f, 'w', encoding='utf-8').write(t)
print('written')
PY
```

Then **re-run the full verifier** to confirm 10/10.

### 5.7 Present the file

`present_file` on the new batch file.

### 5.8 Report to the user

A short summary: the file, its word count, the verification result, the surah's running total, then the substantive highlights — the shape of the passage, the cruxes and how they were resolved, three details worth singling out, and what comes next. Do not paste the commentary into chat.

### 5.9 Update this file

Follow §12.

### 5.10 Stop

Do not begin the next batch. Say what comes next and wait.

---

## 6. WORKSPACE INVENTORY

### 6.1 Delivered tafsir files (38)

See §7 for the complete log with counts.

### 6.2 Source and tooling files

| Path | What it is |
|---|---|
| `Prompt.md` | The full master prompt, verbatim, saved at the user's request. **Read before writing.** |
| `PROJECT-HANDOFF.md` | This file. The handoff document. Update after every batch. |
| `verses-2.json` | Al-Baqarah verse lookup, 286 verses. Sole authority for ch.2 openings. |
| `verses-3.json` | Āl 'Imrān verse lookup, 200 verses. Sole authority for ch.3 openings. |
| `build_verses.py` | The canonical parser that builds a `verses-N.json` from a formatted translation `.md`. See §6.4. |
| `chapter-2-al-baqarah-translation-clearquran.md` | Ch.2 translation, 286 verses, verbatim, H1 + source note + `---` + body. |
| `chapter-3-ali-imran-translation-clearquran.md` | Ch.3 translation, 200 verses, same format. |
| `pastes/chapter-2-al-baqarah-41-160-userpaste.md` | Verbatim archive of a user paste. |
| `pastes/chapter-3-ali-imran-1-200-userpaste.md` | Verbatim archive of the user's original ch.3 paste, pre-reformatting. |

`verses.json` was **deleted** — superseded by `verses-2.json`. Any stale reference to it must be repointed.

### 6.3 Translation-file format contract

Required by `build_verses.py`:

```
# Surah {Name} — English Translation (supplied by the user)

**Source note:** <provenance>

<optional standing-constraint note>

---

1. <verse 1 text> 2. <verse 2 text> ...

<Section Heading> 7. <verse 7 text> ...
```

- Body = everything after the **first** `---`. Parser takes index `[1]`.
- Verse labels matched with `(?:^|[\s])(\d{1,3})\.(?=[ \n])`.
- Footnote markers stripped; section headings stripped.
- Values whitespace-normalised onto one line.

### 6.4 Starting a new chapter

1. Save the user's translation as `chapter-{N}-{slug}-translation-clearquran.md` in the format above. Archive the raw paste in `pastes/`.
2. Run `python3 build_verses.py chapter-{N}-{slug}-translation-clearquran.md verses-{N}.json`.
3. The script asserts no missing and no duplicate verses. If it throws, fix the `.md` formatting, not the script.
4. Confirm the stray-U+02DD count is 0 and multi-line values are 0.
5. Point the verifier in §5.5 at the new `verses-{N}.json`.

---

## 7. COMPLETE DELIVERY LOG

### Chapter 1 — al-Fātiḥah: COMPLETE (7 verses)

| File | Verses | Words |
|---|---|---|
| `chapter-1-al-fatihah-tafsir-1-7.md` | 7 | 9,064 |

### Chapter 2 — al-Baqarah: COMPLETE (286 verses, 29 files, 329,586 words)

| File | Words | | File | Words |
|---|---|---|---|---|
| `1-10` | 11,298 | | `151-160` | 9,692 |
| `11-20` | 11,351 | | `161-170` | 9,775 |
| `21-30` | 12,633 | | `171-180` | 10,240 |
| `31-40` | 11,969 | | `181-190` | 11,838 |
| `41-50` | 10,686 | | `191-200` | 9,171 |
| `51-60` | 9,328 | | `201-210` | 9,646 |
| `61-70` | 10,995 | | `211-220` | 18,932 |
| `71-80` | 11,638 | | `221-230` | 15,970 |
| `81-90` | 11,668 | | `231-240` | 13,179 |
| `91-100` | 10,263 | | `241-250` | 12,333 |
| `101-110` | 11,379 | | `251-260` | 14,717 |
| `111-120` | 11,098 | | `261-270` | 9,988 |
| `121-130` | 9,883 | | `271-280` | 9,539 |
| `131-140` | 11,158 | | `281-286` (6 verses) | 9,264 |
| `141-150` | 9,955 | | | |

All prefixed `chapter-2-al-baqarah-tafsir-` and suffixed `.md`. All verified: 10 markers each (6 for the final batch), 0 stray `˝`.

### Chapter 3 — Āl 'Imrān: IN PROGRESS (80 of 200 verses, 8 files, 93,457 words)

| File | Verses | Words | Status |
|---|---|---|---|
| `chapter-3-ali-imran-tafsir-1-10.md` | 10 | 13,262 | Verified, presented |
| `chapter-3-ali-imran-tafsir-11-20.md` | 10 | 12,721 | Verified, presented |
| `chapter-3-ali-imran-tafsir-21-30.md` | 10 | 11,310 | Verified, presented |
| `chapter-3-ali-imran-tafsir-31-40.md` | 10 | 8,991 | Verified, presented |
| `chapter-3-ali-imran-tafsir-41-50.md` | 10 | 8,484 | Verified, presented |
| `chapter-3-ali-imran-tafsir-51-60.md` | 10 | 15,911 | Verified, presented |
| `chapter-3-ali-imran-tafsir-61-70.md` | 10 | 11,276 | Verified, presented |
| `chapter-3-ali-imran-tafsir-71-80.md` | 10 | 11,502 | Verified, presented |

### Grand total: **38 files · 373 verses · 432,107 words**

---

## 8. WHERE I STOPPED AND WHAT IS NEXT

### Stopped at

**Chapter 3, verses 71–80.** Delivered, verified clean, and presented on 2026-08-29.

Chapter 3 stands at **80 of 200 verses complete**.

### Next: Chapter 3, verses 81–90

The user has **not yet authorised** this batch. Wait for *"Continue. A new md file"* or equivalent.

**What is in verses 81–90** (from the surah's own structure, so the next agent can prepare):

- **v81** — the covenant of the prophets: God takes a pledge from every prophet that when a messenger comes confirming what they have, they will believe in him and help him. A major verse for the finality of prophethood and for the continuity of revelation.
- **v82** — whoever turns away after that is a rebel (*fāsiq*).
- **v83** — do they seek a religion other than God's, when everything in the heavens and earth submits to Him?
- **vv84–85** — declare belief in God, in what was sent to us and to the earlier prophets without distinction; whoever seeks a religion other than *islām*, it will not be accepted.
- **vv86–91** — how shall God guide a people who disbelieved after believing and after witnessing that the messenger is true? The repentance of those who disbelieved after believing and then increased in disbelief will not be accepted; those who die as disbelievers — even an earthful of gold would not be accepted from them.

Anticipated cruxes to research: the covenant verse (v81) and its relationship to the finality of prophethood; the grammar of v86's interrogative; whether v89's repentance exception is conditioned; the "earthful of gold" verse (v91) and its bearing on the efficacy of charity without faith; and the question of who exactly vv86–90 address (reported asbāb concern a group who apostatised and returned to Makkah).

### Then

91–100, 101–110, … in tens, to 200. Twelve batches remain in chapter 3 after 81–90.

---

## 9. PITFALLS AND ERRORS — do not repeat these

### 9.1 The marker-stripping bug (CURRENT — affects every write)

The workspace write mechanism converts a line consisting solely of `===VERSE-END===` into `---`. The write **reports success** and the markers are silently gone. This has now happened on **every** one of the last three batches (51–60, 61–70, 71–80) and is expected, not exceptional.

**Always run check 1 of §5.5. If it returns 0, run the repair script in §5.6, then re-run the full verifier.**

Do not try to work around it by writing the markers differently — write them correctly and repair afterwards.

### 9.2 U+02DD (`˝`) contamination — caught four times

Typing the closing half-bracket `˺` (U+02FA) sometimes produces `˝` (U+02DD) instead. They are visually near-identical and the stray character corrupts the verse text.

**A balanced open/close bracket count does NOT catch it — the counts stay equal.** Always run the explicit `txt.count('\u02dd')` check alongside the bracket balance. Must be 0.

Currently 0 across all 38 files.

### 9.3 Straight vs curly apostrophes in verse openings

Caught once (ch.3 v4 had `Allah's` where the source has `Allah’s`). Fixed with `edit_file`.

**Note the harmless case:** legitimate straight apostrophes in surah/name text (*Ali 'Imran*, *Al-`Imrān*). A blanket "count straight apostrophes" check returns ~200 hits and is **not** a failure signal. Only check inside verse openings.

### 9.4 A prior memory entry wrongly claimed a "v9 curly-quote defect"

It was false — re-verification showed 0 mismatches across all ten openings and no edit was needed. **Diff openings byte-for-byte against the JSON. Never judge quote style by eye.**

### 9.5 Verifier false positives

- **"Marker not followed by `## Verse N`"**: the line immediately after a marker is a **blank line**; the heading is the line after that. Check `lines[i+2]`, not `lines[i+1]`.
- **The final marker** is correctly followed by `## Synthesis of the Ten Verses`. Allow it.
- **The mismatch printer crashes** on short tuples — `print(x[2])` raises `IndexError` on a 2-tuple and aborts the run before the word count prints. The script in §5.5 branches on match failure and so is safe.
- **Opening regex:** `^\*\*"(.*)\*\*$` (straight quotes only) has matched every ch.3 opening. Keep the broader `^\*\*[“”"](.+)[“”"]\*\*$` as the general form for other chapters, and compare with `.rstrip('"”')` on both sides.

### 9.6 Parser iterations — four abandoned variants, do not retry

1. Naive split on sentence-terminals — stripped real verse text (corrupted ch.2 vv2, 26, 45, 68, 69, 155, 209, 219).
2. Paragraph-start heading detection requiring `ps > start` — produced **empty strings** for 12 verses.
3. Title-case heading heuristic that failed on headings containing lowercase function words — fixed by expanding `STOPWORDS` with *upon, about, after, against, before, between, during, through, without, within, than, per, via, till, until, up, out, off* **plus clitics** *s, t, re, ve, ll, d, m*.
4. Word regexes `[A-Za-zÀ-ɏ’']+` and `[^\W\d_]+` — mis-split `Ramaḍân` and `Allah’s`. The correct regex is `[^\W\d_'’]+` with `re.UNICODE`.

### 9.7 Blanket heading strip — abandoned

`t.replace(heading,'')` corrupted ch.2 vv133 and v163. Strip only a **trailing** fragment lacking sentence-terminal punctuation. `build_verses.py` already implements the correct version.

### 9.8 Formal `##` heading inside commentary

Happened once (ch.2 v267). Violates §3.5. The verifier's heading list will catch it. Demote bold-only.

### 9.9 Old verifier compared al-Fātiḥah openings against al-Baqarah's lookup

Structurally solved by the per-chapter `verses-2.json` / `verses-3.json`. Always point the verifier at the right JSON.

---

## 10. CONTENT CONVENTIONS ESTABLISHED

### 10.1 Recurring boundaries (honoured in every file)

- No fabricated hadith, chains, pages or references.
- Disputes flagged, not flattened.
- Science illustrative only; never claimed as prediction, never made the foundation of an interpretation.
- **No reading closes repentance.**
- **No one may declare a specific individual an inhabitant of the Fire.**
- Isrā'īliyyāt flagged as such.
- Divine attributes affirmed without *tashbīh* or *taʿṭīl* — the formula used is: *affirm as He stated it, without asking how, without likening it to a creature.*
- The Qur'an's indictments are always of conduct and of a **party**, never of a people or a lineage. No inherited guilt.

### 10.2 Sources cited consistently

Qur'an cross-references; Bukhārī, Muslim, Abū Dāwūd, Tirmidhī, Nasā'ī, Ibn Mājah, Aḥmad, Mālik; al-Ṭabarī, al-Baghawī, Ibn ʿAṭiyyah, Ibn al-Jawzī, al-Zamakhsharī, al-Rāzī, al-Qurṭubī, Ibn Kathīr, al-Jalālayn, al-Bayḍāwī, Abū Ḥayyān, al-Shawkānī, al-Ālūsī, al-Qushayrī, al-Kāshānī, Ibn ʿĀshūr, Ṭabāṭabā'ī, Maududi, Muftī Muḥammad Shafīʿ, Thānawī, Ibn Ḥazm, Ibn Taymiyyah, Ibn al-Qayyim, Ibn Ḥajar, al-Suyūṭī, Ibn Isḥāq, al-Wāḥidī; lexicography via al-Rāghib, Ibn Manẓūr, Lane, al-Fīrūzābādī; modern Qur'anic studies (Neuwirth, Sinai, Marx, Stowasser, Durie, de Blois, Reynolds, Goudarzi).

### 10.3 Threads tracked through Chapter 3 (continue tracing these)

- **Perception vocabulary**: *ulū al-albāb* (3:7) → *ulī al-abṣār* (3:13) → *ulū al-ʿilm* (3:18).
- ***Baṣīrun bi-al-ʿibād*** bookending v15 and v20.
- ***Lā rayba fīh*** — 2:2, 3:9, 3:25.
- **Root *w-f-y*** — *mutawaffīka* "I take you in full" (3:55) → *yuwaffīhim* "He pays them in full" (3:57) → *awfā bi-ʿahdihi* "he fulfils in full" (3:76). God takes in full, pays in full, requires fulfilment in full.
- **Root *n-ṣ-r*** — the disciples as *anṣār* (3:52) vs. the rejecters having no *nāṣir* (3:56).
- **Root *r-b-b*, "lord"** — *arbāban* forbidden of one another (3:64) and of angels and prophets (3:79–80). The two ends of the passage close the same door.
- ***Min ladunka*** — 3:8, 3:38.
- ***Bi-ghayri ḥisāb*** — 2:212, 3:27, 3:37.
- **The three *annā* "how?" questions** — 2:260, 3:40, 3:47.
- **"Son of Mary"** every time he is named — the doctrine carried in the grammar.
- **"By His leave" (*bi-idhnihi*)** as the whole reply to the argument from miracles.
- **Bearing witness** — *al-shāhidīn* (3:53) → *ishhadū bi-annā muslimūn* (3:64) → *wa-antum tashhadūn* (3:70).
- **"While they know" (*wa-hum yaʿlamūn*)** — 3:70, 3:71, 3:75, 3:78. The surah's charge is never ignorance.
- **The surah's precision**: *ṭā'ifah* / *farīq* / *minhum* — a party, never the whole.
- **The surah denies Jesus nothing** before the confrontation at 3:59 and 3:61.

### 10.4 Translation-flag convention

Where the supplied translation adds or chooses, it is flagged in the commentary and again in the "note on honesty in citation" at the file's end. Examples already handled: bracketed additions (*"alone"* 3:51, *"all"* 3:58, *"little"* 3:66, *"to their truth"* 3:70, *"perfect"* 3:63, *"worthy of worship"* 3:62, *"Gentiles"* 3:75); softening (*"made a plan"/"planned"* loses the repeated *makara* at 3:54); and substitution of technical terms for verb phrases (*kāna ḥanīfan musliman* → *"he submitted in all uprightness"* at 3:67, losing both terms; *kūnū rabbāniyyīna* → *"be devoted to the worship of your Lord"* at 3:79, losing the name for a kind of person).

Always say the translation is not **wrong**, only that it has chosen, and that the reader is entitled to know what was chosen.

---

## 11. OPEN ITEMS / PENDING DECISIONS

Raised but never answered by the user. Do not act on them without asking.

1. **JSON / CSV export** keyed `surah` / `verse` / `commentary`, generated by splitting the `.md` files on the marker. Raised many turns ago; unanswered. This is presumably the point of the whole project, so it is likely to be wanted.
2. **Footnote markers** — decision was to strip them from verse text; confirmed in the source note but never explicitly approved by the user.
3. **Filename convention** — whether to drop `tafsir` from batch filenames. Current convention keeps it; 38 files depend on it.
4. **Bracket form** — half-brackets `˹ ˺` (U+02F9 / U+02FA) are retained from the source translation. Flagged once; no ruling.

---

## 12. UPDATE PROTOCOL

At the end of **every** delivered batch, update this file:

1. **Header** — set `Last updated:` and rewrite the one-line `Status:`.
2. **§7 Delivery log** — add the new file's row to the relevant chapter table, update the chapter subtotal and the grand total line (files · verses · words).
3. **§8 Where I stopped** — move the completed batch into "Stopped at", set the new "Next" batch with its verse range and anticipated cruxes, and confirm the user has **not** authorised it.
4. **§10.3 Threads** — append any new recurring word, root or motif traced in the batch.
5. **§9 Pitfalls** — add any new failure mode, especially if the marker bug's behaviour changes.
6. **§11 Open items** — move anything the user has answered out of this section.

Do **not** rewrite §1–§6 or §10.1–§10.2; those are stable. Keep the file's voice factual and terse — it is a machine-and-human handoff, not prose.

---

## IMPORTANT NOTE
It is important that you read through about 6 randomly selected tafsir files already existing ( this include the last one) after understanding the prompt to to learn the general structure. Define don't have any expected words everything. Learn from the existing files. 

*End of handoff document.*
