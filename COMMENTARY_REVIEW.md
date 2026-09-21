# Commentary review — findings

Scope: all 6,236 verse sections in `markdown commentry/`, reviewed against four
questions — is it simple enough, does it make sense, does it explain the verse,
is it comprehensive, is it backed with evidence.

Method: every section was parsed and measured programmatically. Where a number
mattered it was re-checked by reading real sections, because the first evidence
measurement turned out to be wrong (see the caveat at the end).

---

## 1. Four structural defects — found and fixed

These are committed in `9035c7a`.

### 1.1 The verse was displayed twice on the commentary page (reported bug)

Both render surfaces printed the English translation from the structured data
and then the commentary, which opens with the same verse as a blockquote:

| Surface | Code |
|---|---|
| Verse modal | `showExplanation()` → `modal-verse-translation` + `renderMarkdown(explanation)` |
| Full commentary | `openCompleteCommentary()` → `ebook-translation` + `renderMarkdown(commentary)` |

The markdown keeps its blockquote on purpose — `scripts/editorial/integrity.py`
prints `PROBLEM` for any section without one, and the quote pickers read the
verse wording from it. So the fix is at render time: `getVerseCommentary()` now
runs `stripLeadingVerseQuote()`, which drops only the **first** contiguous run
of `>` lines and leaves any genuine blockquote further down intact.

### 1.2 39 sections repeated their own verse 2–3 times

45 duplicate blockquotes removed. Chapter 4 ×34 sections, chapter 36 ×4,
chapter 77 ×1. Example, 4:31 before the fix:

```
## Verse 4:31
> If you avoid the major sins forbidden to you, …
> If you avoid the major sins forbidden to you, …
> If you avoid the major sins forbidden to you, …
```

### 1.3 43 headings with no prose under them

Across 24 sections (chapters 4, 36, 7, 77). 4:31 carried four in a row before
its first paragraph. The detector only counts a heading as orphan when the next
non-blank line is another heading or the end of the section, so the last heading
of each run keeps its prose.

### 1.4 One prose paragraph that was verbatim the verse

6:146 opened with a standalone paragraph reproducing the verse's first sentence
word for word, adding nothing. Removed.

**Nothing was lost.** Before deleting, all 45 blockquotes, all 43 headings and
that paragraph were checked for references — none contained one. Re-scan after:
0 duplicate-verse sections, 0 orphan headings.

---

## 2. Simplicity — good

Measured on the commentary's own prose: headings counted as text, and the
inserted verse quotations (`— *“…”*`) removed, since those are translation text
rather than writing under review. That body is 2,700,972 words.

| Measure | Value |
|---|---|
| Sentences | 113,025 |
| Mean sentence length | 23.9 words |
| Median sentence length | 22 words |
| 95th percentile | 47 words |
| Longest | 162 words |
| Sentences over 40 words | 11,507 (10.2%) |
| Words of 12+ letters | 29,137 (1.08% of prose words) |

A median of 22 words with only 1% long words reads as plain English. The tail is
the thing to watch: 10.2% of sentences run past 40 words and the longest is 162,
and those are concentrated in the heavily-worked chapters.

## 3. Comprehensiveness — uneven across chapters

Measured on the full section body including the inserted verse quotations
(3,198,340 words). The prose-only figure in §2 is 2,700,972.

| Measure | Value |
|---|---|
| Sections | 6,236 |
| Total words | 3,198,340 |
| Median per section | 483 |
| 5th percentile | 189 |
| Shortest | 118 |
| Longest | 2,216 |
| Under 250 words | 814 sections |
| Under 400 words | 2,313 sections |

The real problem is not the thin tail — it is the spread between chapters:

| Thinnest | Median words/verse | | Richest | Median words/verse |
|---|---|---|---|---|
| ch 37 | 183 | | ch 4 | 1,189 |
| ch 26 | 225 | | ch 36 | 843 |
| ch 27 | 241 | | ch 7 | 776 |
| ch 74 | 253 | | ch 41 | 776 |
| ch 69 | 264 | | ch 6 | 737 |

Chapter 4 gets 6.5× the words per verse that chapter 37 gets. Chapters 4, 36, 42
and 43 were rewritten in earlier passes; the rest were not, and the difference
is visible.

## 4. Evidence — strong on Qur'an, thin on hadith and named scholars

| Evidence kind | Sections carrying it | Share |
|---|---|---|
| Qur'an cross-reference | 5,381 | 86.3% |
| Language / root discussion | 1,644 | 26.4% |
| Hadith | 1,004 | 16.1% |
| Named scholar | 521 | 8.4% |
| Bible (where the corpus raises it) | 38 | — |

How many kinds each section carries:

| Kinds | Sections | Share |
|---|---|---|
| 0 | 539 | 8.6% |
| 1 | 3,346 | 53.7% |
| 2 | 1,869 | 30.0% |
| 3 | 432 | 6.9% |
| 4 | 52 | 0.8% |
| 5 | 0 | 0% |

Reading of this: the commentary is well anchored in the Qur'an explaining itself
— 86% of sections cross-reference. But **no section carries all five kinds**, and
over half carry exactly one. Hadith appears in one verse in six, and a named
scholar in one in twelve. For a work that aims to be "backed with all kinds of
evidences", the hadith and scholar layers are the gap.

### 539 sections with no pinpoint evidence

Of those, 187 still cite a sūrah by name in prose ("in the sūrah of the Cow,
after the change of the direction of prayer…") — anchored, but not to a verse
the reader can check. **352 have no external anchor at all**, and they cluster:

| Chapter | Sections with no anchor |
|---|---|
| 26 | 85 |
| 9 | 28 |
| 27 | 26 |
| 20 | 22 |
| 37 | 20 |
| 74 | 19 |

This is the same chapter set as the thin-commentary list. Chapter 26 (al-Shuʿarāʾ)
is the weakest in the corpus on both measures at once.

---

## 5. Suggested order of work

1. **Chapter 26** — 227 verses, median 225 words, 85 with no anchor. The single
   worst chapter on both axes.
2. **Hadith layer** — 16.1% coverage. Raising chapters 3, 9, 20, 27 would move
   the number most, since those are long chapters already carrying prose.
3. **Named scholars** — 8.4%. The classical voices (al-Ṭabarī, al-Rāzī,
   al-Qurṭubī, Ibn Kathīr) are cited where they were cited; the sections that
   have none have none at all.
4. **The 352 unanchored sections** — each needs at least one checkable
   cross-reference.
5. **Sentence-length tail** — 11,507 sentences over 40 words, concentrated in
   chapters 4, 36, 7, 41.

---

## Caveat on method

The first evidence measurement used the pattern `\(\d+:\d+\)`, which requires a
closing bracket immediately after the numbers. Since the quoting work, most
references read `(4:160 — *“We forbade the Jews certain foods…”*)`, where the
bracket is far away. That pattern silently missed **2,566 sections** and
understated Qur'an cross-referencing as 2,857 sections instead of 5,381.

The corrected pattern is `\d+:\d+(?!\d|[–-]\d)` — a `surah:verse` token not
followed by another digit or a range dash. Every number in §4 above uses the
corrected form. This is recorded because the same mistake is easy to repeat: any
count of references must be taken against the *expanded* text, not the old bare
`(c:v)` shape.
