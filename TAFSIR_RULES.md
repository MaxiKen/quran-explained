# The rules — every one of them, in one list

This is the complete rule set the verse-by-verse corpus is held to: the ten works it may be written
from, the shape of a chapter file, the quoting law, the length floors, the evidence and attribution
law, the phrasing rules, the style rules, the repetition rules, the advisory grounding check, and
the process rules for writing a chapter in batches.

Where each rule lives:

| Where | What it is |
|---|---|
| §0 below | **what this book is** — the standard the whole rule set serves |
| [`TAFSIR_PROMPT.md`](TAFSIR_PROMPT.md) §4–§8 | the rules as written for the writer — the authority on *why* |
| `scripts/tafsir/audit.py` | the same rules mechanised — **76 codes**; the authority on *what actually blocks a chapter* |
| `scripts/tafsir/batch.py` | the same rule set applied to the verses written so far, so a batch can be judged while the chapter is unfinished |
| `scripts/tafsir/selftest.py` | proof that each rule bites: it breaks each one on a scratch copy, and checks that the match rules stay silent on the verse's own wording and on synonyms of it |
| `scripts/tafsir/lexicon.py` | the tables the match rule judges by: the synonym groups and the glosses of the Arabic terms |
| `scripts/tafsir/match.py` | is this word or phrase the verse's own wording, a synonym of it, or neither? |
| `scripts/tafsir/ruletest.py` | proof that the v7 rules (§0) bite, runnable with no chapter on disk |
| [`TAFSIR_PIPELINE.md`](TAFSIR_PIPELINE.md) §5 | the working agreement (who writes what, when a chapter is done) |
| this file | the whole list, in order, with every threshold |

If this file and `audit.py` ever disagree, `audit.py` is what a chapter is judged by.

**Two levels.** `FAIL` means the gate fails and the chapter cannot be published; it must be fixed by
changing the writing, never by changing the rule. `WARN` means the gate still passes but the finding
must be read, and fixed when it is real. `GRD-TOKENS` is advisory by design.

---

## 0. What this book is (standard v7.1, set 2026-09-25)

The chapters are **one author's own commentary book**. The ten works are the research behind it,
not the content of it. The writer reads them, learns what the verse carries and how it has been
read, and then writes **new prose of his own** — his reading, his explanations, his history, his
rulings, his analogies, his application to the reader's life — backed by evidence the reader can
check. What was learned from a source is written as the book's own statement; it is not re-told as
that source's opinion, not compared work by work, and not quoted.

1. **Original writing, learned from the ten.** Every paragraph is the book's own voice. A sentence
   that hands a point to a named work — *"al-Ṭabarī records that…"*, *"according to al-Saʿdī"*,
   *"the words of al-Jalālayn stand beside it"*, *"the commentators say"* — is a summary of a
   source, and **fails** (`STY-PARAPHRASE`), in the introduction and in every verse section. Write
   the reading itself: *"the sentence turns on the second clause, because…"*.
2. **The ten are never quoted.** A quotation beside a work's name **fails** (`SRC-QUOTED`).
   Reporting may quote a *report* in the corpus's straight-quote style — `*"…"*` — when the report
   is itself the evidence and is cited with its collection (a hadith, an athar); the commentarial
   works are used, not quoted.
3. **The sources' contents are taken as they stand.** They are authenticated works. The writer
   does not fact-check them, does not grade their reports (beyond a grade a source itself gives,
   §6.4), does not adjudicate between their chains, and does not need to attribute a point to a
   work for the point to stand. Research is required — **all ten are read for every verse**
   (`SRC-NODIGEST`, `SRC-NOTCHECKED`) — but the reading that comes out is the book's own.
4. **Backed by evidence.** Original does not mean unsupported: every verse still carries checkable
   anchors — Qur'an cross-references, hadith with their collections, named early authorities
   (Companions and Successors as they report), language points (§6, `EVD-*`, `PHR-EVIDENCE`). A
   claim about the verse that nothing in the chapter lets the reader check is not finished prose.
5. **Modern, and for the reader.** The book is written for a reader in the present: each verse
   reaches his own world at least once, plainly, without a label (`STY-APPLICATION` warns when it
   does not), carries the one honest analogy where one exists (`STY-ANALOGY`), and keeps the
   elements — history, report, ruling, lesson, application — shown in the flow rather than
   announced (§8.4).
6. **Paragraphs are full.** Every paragraph of the commentary — the introduction's and every
   verse's — runs **past 120 words** (`WRD-PARA-FLOOR`). A paragraph is a complete movement of
   thought, not a handful of lines; a thought too small to reach 121 words belongs with the
   paragraph beside it. **A heading may carry one paragraph or several** — nothing here says one
   paragraph per heading, and a long thought under one title is free to run in two, three or more
   paragraphs, each of them past 120 words.
7. **Every verse is presented on its own terms (v7.1).** There is no house style: no standard
   diction, no stock opening, no heading template, no fixed arrangement of the section. The
   chapter is a book of 7, 286 or 200 separate readings, and a reader who has read one verse should
   not be able to predict the shape of the next. Concretely, nothing of the *writing* may repeat
   from verse to verse: not a sentence frame that opens paragraphs the same way, not a run of the
   commentary's own wording, not a heading reused or built on a repeated pattern, not the same
   count of headings and paragraphs down every verse of a long chapter. What **may** repeat is what
   is quoted — the verse's own phrases, cited clauses, a report's words — because that is the
   Qur'an and the evidence, not the author's voice.
   The gate proves it (`STY-UNIQUE-VERSE`, fail): the same four-word sentence opening in two verses
   warns and in three fails; the same six words of unquoted prose in two verses warns (and in six
   such phrases fails the chapter) and in three verses fails; a heading reused verbatim fails, two
   verses opening a heading with the same two words warn and three fail; and in a chapter of ten
   verses or more, one arrangement of headings and paragraphs shared by 70% of verses warns and by
   90% fails.

The codes v7 retired with this standard: `SRC-SPREAD`, `SRC-FAMILY` (the quotas that *required*
five works to be named in each verse) and `SRC-UNUSED` (which asked for works to be named at
chapter level). Naming the ten was the old trade; writing from them is the new one.

v7.1 added one law to the same spirit: **no verse repeats another verse's presentation** (§0.7),
and settled the question of paragraphs — a heading may carry as many paragraphs as the thought
needs, each past 120 words (§0.6).

## 1. Sources — what may be written from (`SRC-*`)

1. **The corpus is eleven works, with one super source.** `corpus.SOURCE_ALLOWLIST`:
   `tafsir_initial`, `tafsir-al-tabari`, `tafsir-al-qurtubi`, `tafsir-al-baghawi`, `tafsir-ibn-kathir`,
   `tafsir-al-alusi`, `tafsir-al-jalalayn`, `tafsir-ibn-abbas`, `tafsir-as-saadi`,
   `tafsir-ibn-uthaymeen`, `tafsir-maarif-ul-quran`. `tafsir_initial/` is the super source — the
   main tafsir intended as the primary foundation, with the other ten as supplementary additions.
   Naming any other tafsir — al-Bayḍāwī, al-Shawkānī, al-Qushayrī, al-Tustarī, Kashānī,
   al-Mukhṭaṣar, al-Wāḥidī, *Bahr al-Muḥīṭ*, *Tazkir al-Qurʾān* and the rest of the deleted folders —
   **fails** (`SRC-BANNED`). Deleting the folder is the only way a work leaves the corpus; a stray folder
   cannot re-enter quietly.
2. **`tafsir_initial/` is now the super source (source #11).** It is the main tafsit, meant to be the
   primary foundation upon which the other ten sources add nuance, detail, and alternative readings.
   Content from `tafsir_initial` should be the starting point; the other ten sources provide
   additions, cross-checks, and supplementary material. Nothing may be cited from `tafsir_initial`
   alone without also consulting the other ten, and conversely, the other ten are meaningless in
   isolation — they all feed into the `tafsir_initial` framework.
3. **All eleven are read for every verse before a word of it is written.** If the source digest has not
   been built, the gate **fails** (`SRC-NODIGEST` → run `sources.py N`); if a work that covers the
   verse was never pulled into it, the gate **fails** (`SRC-NOTCHECKED`). A work with no text for
   that verse anywhere in the repo is a coverage gap and only warns (`SRC-ABSENT`).
4. **The eleven are research, and the prose is the book's own** (§0). No work of the eleven is relayed,
   compared or quoted in a verse section or the introduction: relaying **fails** (`STY-PARAPHRASE`),
   quoting **fails** (`SRC-QUOTED`). There is no quota of names to hit; naming a work in a summary is
   now a failure, not a duty.
5. **A named authority may still be evidence** — a Companion or Successor as the reports carry him
   (*"Ibn ʿAbbās said the word means the covenant itself"*), a hadith with its collection — where
   the authority *is* the proof. The line is simple: an authority may support the reading; a work
   may not speak it.
6. **Before a sentence credits anyone, find the passage**: `python3 scripts/tafsir/verify.py
   "<claim>" --chapter N` (or `--verse C:V`). No hit means no credit — drop the claim or state it
   without a name. This check is not optional (§7 of the prompt).
4. **The ten are research, and the prose is the book's own** (§0). No work of the ten is relayed,
   compared or quoted in a verse section or the introduction: relaying **fails** (`STY-PARAPHRASE`),
   quoting **fails** (`SRC-QUOTED`). There is no quota of names to hit; naming a work in a summary
   is now a failure, not a duty.
5. **A named authority may still be evidence** — a Companion or Successor as the reports carry him
   (*"Ibn ʿAbbās said the word means the covenant itself"*), a hadith with its collection — where
   the authority *is* the proof. The line is simple: an authority may support the reading; a work
   may not speak it.
6. **Before a sentence credits anyone, find the passage**: `python3 scripts/tafsir/verify.py
   "<claim>" --chapter N` (or `--verse C:V`). No hit means no credit — drop the claim or state it
   without a name. This check is not optional (§7 of the prompt).

## 2. Qur'an quoting law (`FMT-QUOTE-*`, `PHR-QUOTE-*`, `REF-*`, `MTCH-*`)

1. **The only source of Qur'an wording is `data/chapter_NNN.js`.** Never from a tafsir's paraphrase,
   never from memory, never retyped if it can be copied.
2. **The verse under discussion** appears once per section as a single `> …` line, blank line above
   and below, identical to that verse's `ayah_en` after whitespace normalisation (the scaffold
   copies it byte-for-byte, so this is a free win). Missing → `FMT-QUOTE`; more than one line →
   `FMT-QUOTE-LINES`; different wording → `FMT-QUOTE-VERBATIM` (all fail).
3. **A phrase of this verse** is written in **bold italics**: `***“the phrase of this verse”***`
   (`***` — curly quotes — `***`). A phrase quoted plainly, or in bold only, **fails**
   (`PHR-QUOTE-STYLE`); wording in that style that is *not* this verse's wording **fails**
   (`PHR-QUOTE-FOREIGN`).
4. **A clause of another verse** is written in **bold only, inside its reference**:
   `(C:V — **“the clause”**)` — em dash, curly quotes. An italic cross-reference quote **fails**
   (`REF-QUOTE-STYLE`).
5. **A quoted cross-reference clause must be verbatim** from that verse's `ayah_en` (whitespace
   normalised) — else `REF-QUOTE` (fail). A citation must point to a real verse: `(2:300)` **fails**
   (`REF-RANGE`). A bare citation with no quote — `(2:255)`, `(3:8)` — is fine and encouraged.
6. **A clause is a clause, not a verse**: over 34 words **fails** (`REF-LONG`), over 22 warns.
7. **Never re-quote a verse already quoted in the same section** — cite it after that
   (`REF-QUOTE-REPEAT`, warn); re-quoting this verse's own line in reference style warns
   (`REF-SELF-QUOTE`). Chapter-wide, the same wording quoted more than four times warns
   (`REP-QUOTE`).
8. **Reports, athar and the words of a named early authority are quoted `*"…"*`** (emphasis,
   straight quotes) — the ten works themselves are never quoted (`SRC-QUOTED`, §0). A passage left
   in curly quotes outside a Qur'an reference warns from 12 words and **fails** at 25
   (`EVD-QUOTE-STYLE`); Qur'an wording put in straight-quote style **fails** (`REF-STRAIGHT-QUOTE`).
9. A Qur'an clause quoted in curly quotes with no reference beside it warns (`REF-UNANCHORED`).
10. **Bold is reserved.** Nothing in a chapter file is bold except three things: an UPPERCASE
    heading (`**TITLE**`), a phrase of this verse (bold italics, `***“…”***`) and a clause quoted
    from another verse (bold only, inside its reference). Any other bold — a name, a term, a word
    the writer wants noticed — **fails** (`MTCH-BOLD`). The reader's key is then unambiguous:
    **bold = Qur'an, italic = report, plain = the commentary.** Reports, athar and the words of a
    named early authority stay `*"…"*` (italic, straight quotes), never bold.
11. **The prose matches the verse it quotes** (`MTCH-WORD`, `MTCH-TERM`) — see §2.1.

## 2.1 The prose explains the verse as it is quoted

The verse line above the section is the translation, and that text is what the commentary explains.
Every quoted phrase is a phrase of it (verbatim, in the right style), and every word explained is a
word the reader can see in it.

A **synonym** here is exactly that: a word *or a whole phrase* the verse does not use but that
**means the same thing** — *"the day of reckoning"* for the verse's "the Day of Judgment", *raḥmah*
for "the Most Merciful", *"the right way"* for "the Straight Path". The judgement is by meaning, not
by spelling.

1. **A synonym is adjusted, and the section carries on** (`MTCH-SYNONYM`, informational). When a
   headword — one word or a phrase — means what the verse says, the gate resolves it to the verse's
   own wording (*"the day of reckoning"* → the verse's **day**, within "Master of the Day of
   Judgment") and records the adjustment, so the sentence can be lined up with what the reader sees.
   Informational findings do not fail the gate and are shown only under `audit.py N --show-info`.
2. **A headword that means something else fails** (`MTCH-WORD`): *"the word X means …"*,
   *"literally X"*, *"from the root X"*, *"the plural X"*, where X — English or Arabic — says
   something the verse's translation does not. Arabic resolves through its glosses, so *raḥmah*
   passes beside "the Most Merciful" and fails in a verse where nothing there means mercy.
3. **Arabic offered as the verse's own wording fails** (`MTCH-TERM`) even when the meaning is right:
   *"the verse says *kāfir*"* is a claim about the quoted line, and the line says "the disbelievers".
4. **Arabic carried as a free-standing language point warns** (`MTCH-TERM`) when no meaning of it
   appears in the verse, at most twice per section. Proper names are never flagged: a sūrah's name, a
   place, a person, a month, a scholar's surname after *Ibn / al- / Abū*, and the pipeline's own
   words (sūrah, āyah, ḥadīth, tafsīr, isnād).
5. **A bold-italic quote that is not this verse's wording fails** (`PHR-QUOTE-FOREIGN`), the same
   rule the phrase-coverage checks apply from the other side.

The tables behind the judgement live in `scripts/tafsir/lexicon.py`: `SYNONYM_GROUPS` (the English
the translations use for one meaning) and `TRANSLIT_GLOSSES` (the Qur'anic terms the ten works
transliterate, with the English for each). `scripts/tafsir/match.py` answers the question for a word
or a phrase before it is written:

```bash
python3 scripts/tafsir/match.py 1:4 "the day of reckoning" "the day of the harvest"
```

## 3. The shape of a chapter file (`FMT-*`)

1. The file is `tafsir/NNN.md`, one chapter per file, and the title line is exactly
   `# Sūrah <name_en> (Chapter N) — Verse-by-Verse Tafsir` (`FMT-TITLE`). A missing file is
   `FMT-FILE`; both fail.
2. **The introduction** sits under `## Introduction to the Sūrah` on **line 3** (`FMT-INTRO`,
   `FMT-INTRO-POS`, fail), is non-empty (`FMT-INTRO-EMPTY`, fail), is **250–1,500 words**,
   runs in paragraphs of **past 120 words** (`WRD-PARA-FLOOR`) that relay no work (`STY-PARAPHRASE`)
   (`WRD-INTRO`: under 250 fails, over 1,500 warns), carries **no `**bold**` headings**
   (`FMT-INTRO-HEADINGS`, warn) and **no `---` inside it** (`FMT-INTRO-SEP`, fail).
3. **Every verse of the chapter appears once, in ascending order**, with no skipped, combined or
   invented verse numbers (`FMT-VERSES`, fail).
4. **Each verse section** is at least **two paragraphs of prose** (`FMT-PARAGRAPHS`, fail) and opens
   with one blank line after the `## Verse N:V` heading (`FMT-SPACING`, fail).
5. **Headings** (`**TITLE**`, alone on their line, blank line before and after —
   `FMT-HEADING-SHAPE` fails otherwise):
   * written in **UPPERCASE** — any lower-case letter fails (`FMT-HEADING-CASE`);
   * a **descriptive title of the writer's own**, never the verse's own wording — a quoted phrase, or
     a line starting with `“`, fails (`FMT-HEADING-QUOTED`);
   * **six or more words repeated verbatim from the verse fail** (`FMT-HEADING-VERSE`), four or more
     warn;
   * **never generic** — `COMMENTARY`, `EXPLANATION`, `INTRODUCTION`, `OVERVIEW`, `SUMMARY`,
     `LESSON(S)`, `NOTE(S)`, `CONCLUSION`, `REFLECTION(S)`, `ANALYSIS`, `DISCUSSION`, `THE VERSE`
     fail (`FMT-HEADING-GENERIC`);
   * over 12 words warns (`FMT-HEADING-LONG`); the same title twice in one section warns
     (`FMT-HEADING-DUP`);
   * every heading must be followed by prose — an orphan heading fails (`FMT-ORPHAN-HEADING`).
6. **Headings in a section**: at least one (`FMT-HEADINGS`, fail); one only warns
   (`FMT-HEADINGS-FEW`); more than 30 warns (`FMT-HEADINGS-COUNT`). A heading carries **one
   paragraph or several** — the 120-word floor is on each paragraph, never on the heading — and no
   heading is reused or templated from another verse (§0.7, `STY-UNIQUE-VERSE`).
7. **Separators**: exactly one `---` before the next verse (`FMT-SEP`, fail); none after the final
   verse (warn); a `---` with no blank line above it is a markdown setext heading and fails
   (`FMT-SEP`).
8. **No placeholder survives**: `TODO`, `TBD`, `PLACEHOLDER` in a section body fails
   (`FMT-PLACEHOLDER`).
9. **Hygiene** (`FMT-WHITESPACE`, all fail): no tab characters, no trailing whitespace, never more
   than one blank line in a row, the file ends with a single newline and not with a blank line.

## 4. Length (`WRD-*`)

| Rule | Value | Level |
|---|---|---|
| Words per verse | `max(500, 8 × the verse's own word count)`, capped at **4,000** | under the floor: `WRD-FLOOR` **fail** |
| Soft ceiling per verse | 5,000 words — above it, check for padding | `WRD-CEILING` warn |
| **Every paragraph** | **past 120 words** (a paragraph is a movement of thought) | `WRD-PARA-FLOOR` **fail** |
| Introduction | 250 words minimum, 1,500 soft ceiling | `WRD-INTRO` fail / warn |

The numbers live in `audit.py` (`MIN_VERSE_WORDS = 500`, `SCALE_FACTOR = 8.0`,
`SCALE_CAP = 4000`, `MAX_VERSE_WORDS = 5000`) and `scaffold.py` restates the floor in each `TODO`
line, so the writer always sees the floor for the verse in front of him. A fifty-word verse
therefore needs 500 (its scaled floor, 400, sits under the base); a ninety-word verse needs 720+; a
two-hundred-word verse needs 1,600+.

**Length comes from material, never padding**: the phrase-by-phrase reading, the stories and
occasions of revelation, the hadith and athar with narrator and collection, the rulings the verse
settles (stated as the reading, not as a survey of opinions), the cross-references, one analogy, the
history, and where the verse meets the present — all of it in the book's own voice (§0). If a section is under its floor, go back to the digest and use material not
yet used — usually the Arabic sources — never repetition or vague exhortation.

## 5. The phrase-by-phrase reading (`PHR-*`)

1. **Every phrase of the verse is quoted inside the prose and explained there**, in verse order; the
   headings around it carry everything else (setting, story, ruling, disagreement, analogy). No
   phrase quoted at all → `PHR-PHRASE-NONE` (fail).
2. **The cut**: `corpus.split_phrases` proposes one (breaks at strong punctuation `— ; : ? !` and
   before conjunctions, keeps every word, never leaves a fragment, minimum 3 words, preferring
   units of about 4–5, at most 24 units). Re-cut it whenever a more meaningful unit is visible, as long as the quotes
   run in verse order, together account for the whole verse, and copy the verse's own wording.
3. **The verse is not swallowed by one quote**: for a verse of 12 words or more, one quoted stretch
   carrying **65%+ fails** (`PHR-CHUNK`) and 40%+ warns — that is quoting the verse instead of
   reading it.
4. **Coverage**: the prose quotes **at least 90%** of the verse's words (`PHR-PHRASE-COVERAGE`, fail
   under 90%, warn when it is above the floor but incomplete).
5. **No gap over 8 words** may be passed over unquoted (`PHR-PHRASE-GAP`, fail) and **the first and
   last 3 words may not be dropped at the edges** (`PHR-PHRASE-EDGE`, fail).
6. **Every phrase the cutter proposes must be quoted somewhere** (`PHR-PHRASE-MISSING`, fail).
7. **Every quoted phrase carries evidence beside it** — in its own paragraph, or the paragraph
   straight after it: a Qur'an cross-reference, a report with its collection, a named authority
   (a Companion or Successor as the reports carry him), or a language point that changes
   the meaning. Otherwise `PHR-EVIDENCE` (fail). A work of the ten is not an anchor: naming one is
   a summary, and a summary fails (`STY-PARAPHRASE`, §0).

## 6. Evidence and attribution (`EVD-*`)

1. **Every verse carries checkable anchors**: a bare Qur'an cross-reference, a collection, a named
   authority or a language note. None → `EVD-NONE` (fail). Only one *kind* → `EVD-THIN` (warn).
2. **A prophetic report always names its collection** in the same sentence or paragraph
   (`EVD-ATTRIBUTION`, fail): `Ṣaḥīḥ al-Bukhārī 756`, `Muslim records Abū Hurayrah saying…`.
   A prophetic saying whose collection cannot be named does not go in.
3. **Never invent a hadith number.** Every `Collection number` in the prose must appear in a source
   for that verse, in either script — otherwise `EVD-NUMBER` (fail). Numbers come from the source or
   not at all.
4. **Grade only what the source grades** (`At-Tirmidhī said ḥasan gharīb`, `a chain al-Ṭabarī grades
   weak`).
5. **Never promote a witness account, a Companion's ruling or a commentator's gloss to a prophetic
   saying.** Speaker → speaker: Companion → Companion, scholar → scholar, Prophet ﷺ → Prophet ﷺ.
6. **Never attribute a point to a source that does not make it.** Find the passage first
   (`verify.py`); a sentence that borrows authority it does not have is the worst failure this
   corpus can have, because it is invisible on re-reading. Under v7 few sentences carry a work's
   name at all (§0); the ones that name an early authority must still be true to what the reports
   carry.

## 7. One reading, in the book's own voice (`STY-SOURCE-PARADE`)

The ten works are **witnesses inside one argument**, not ten speakers taking turns — and since
v7 they are not speakers at all: they are research, and the book says the reading itself (§0). What
remains checkable is the shape of the prose, in every verse section:

| Check | Warn | Fail |
|---|---|---|
| Sentences in a row that open with a named authority | — | 3 (`STY-SOURCE-PARADE`) |
| Share of a section's sentences opening with a named authority | above 18% | above 30% |
| Share of a section's paragraphs opening with a named authority | above 30% | above 45% |

A "source-led" sentence is one whose first three words name a work (or a first-generation figure).
Under v7 there is no reason for one to appear at all: the reading is the book's own (§0), a named
work inside a summary fails (`STY-PARAPHRASE`), and what remains is the early authorities cited as
evidence — a Companion or Successor as the reports carry him. Cite such an authority where it is the
proof, inside a sentence that is already making the point, not as a roll-call; where several carry
the same reading, one mention covers them all, and duplicated source records count as one witness.

**And the section must reason, not just report**: at least **4 sentences per verse** must analyse
(*because*, *since*, *so that*, *which means*, *the point*, *what follows*, *therefore*,
*the difference*, *what turns on*) — fewer than 4 fails (`STY-ANALYSIS-FLOOR`), fewer than 8 warns.

## 8. Plain English, and one analogy (`STY-*`)

1. **Diction** (`STY-DICTION`): plain words only. "so" not "subsequently", "show" not "demonstrate",
   "start" not "commence", "use" not "utilise", "about" not "with regard to", "but" not
   "notwithstanding". The gate keeps a list (`utilise`, `endeavour`, `commence`, `subsequent`,
   `notwithstanding`, `aforementioned`, `thereof`, `wherein`, `thereby`, `whereby`, `elucidate`,
   `explicate`, `paradigm`, `juxtapose`, `myriad`, `plethora`, `facilitate`, `cognizant`, `requisite`,
   `henceforth`, `peruse`, `ascertain`, `albeit`, `hitherto`, `dichotomy`, `instantiate`,
   `delineate`, `promulgate`, `expound`, `propound`, `eschew`, `imbue`, `engender`, `encapsulate`,
   `vis-à-vis`, `inter alia`, `prima facie`, `de facto`, `a priori`, `ipso facto`, `erstwhile`,
   `veritable`, `multifaceted`). Six or more **fail**; fewer warn.
2. **Chapter style metrics** (measured on prose only, once the chapter has 20+ sentences and 800+
   words):

   | Measure | Target | Warn | Fail |
   |---|---|---|---|
   | Mean sentence length | under 22 words | above 26 (`STY-SENTENCE`) | above 32 |
   | Sentences over 40 words | under 8% | above 12% (`STY-SENTENCE-LONG`) | above 25% |
   | Reading ease (Flesch) | 60+ | below 55 (`STY-READABILITY`) | below 45 |
   | Words of 12+ letters | under 1% | above 2% (`STY-LONGWORDS`) | — |

3. **Arabic terms are welcome** — *raḥmah*, *ṣirāṭ*, *tawḥīd* — as long as each is explained the
   first time in the chapter and used naturally after that.
4. **The elements are shown, never labelled** (`STY-LABELS`, fail): no `Lesson:`,
   `Modern application:`, `History:`, `Context:`, `Ruling:`, `Explanation:`, `Cross-reference:`,
   `Takeaway:`, `Moral:`, `Insight:`, `Note:`, `Background:`, `Analogy:`, `Application:`,
   `Element:`, `Modern science:` — nothing that exists only to announce what kind of content
   follows. The history arrives as narrative, the lesson as the conclusion a paragraph reaches, the
   application as something the reader recognises in his own week.
5. **One relatable analogy per verse** where one honest comparison exists, drawn from ordinary life
   (a market, a road, a garden, a workshop, rain, a boat, a letter, a journey) and fitting the
   verse's own point. Missing in a verse warns (`STY-ANALOGY`); chapter-wide, fewer than **40%** of
   verses carrying one **fails**, fewer than 60% warns.
6. **Do not write**: process or meta prose ("this section", "we will now examine", "as mentioned
   above", "in conclusion"); filler openers, closers and clichés; the same sentence twice anywhere
   in the chapter; generic exhortation that would fit any verse unchanged.
7. **Do write**: verse-specific detail (the word explained, the person in the story, the ruling at
   stake); transitions between paragraphs; the "so what" sentence once, briefly, where the verse
   makes a practical demand.

## 9. Repetition, filler and machine prose (`REP-*`)

1. **No duplicated sentence** anywhere in the chapter, comparing sentences of 10 words or more —
   `REP-SENTENCE` (fail).
2. **No templated sections**: 8-gram phrasing overlap between two verse sections **fails** above
   30% (`REP-TEMPLATE`) and warns above 18%.
3. **No filler or meta prose** (`REP-FILLER`, fail): "this section/file/document/draft/commentary/
   payload", "in this chapter we", "as we have seen/said/noted/mentioned/discussed", "the
   audit/prompt/generator/source digest/worklog", "audit.py", "TAFSIR_PROMPT", `TODO`/`TBD`/
   `PLACEHOLDER`/"to be written"/"lorem ipsum", "as an AI"/"language model", "it is worth noting",
   "it is important to note", "in conclusion", "to sum up", "to summarize", "let us now
   look/examine/consider/turn", "we will now see/explore/examine/look at". Clichés and vague
   generalities warn: "delve into", "rich tapestry", "stands as a testament", "testament to",
   "navigate the complexities", "underscores the importance", "plays a crucial/vital role",
   "throughout history", "since time immemorial", "countless generations".

## 10. Grounding — advisory (`GRD-TOKENS`)

Distinctive proper names and italicised foreign terms in a section should appear in that verse's
source digest (`tmp/sources/NNN.json`, built by `sources.py N`). When at least 5 such tokens are
present and half or more are absent from the digest, the section warns (`GRD-TOKENS`). It is
advisory because English renderings of Arabic names legitimately differ; it is meant to catch a
name that came from nowhere. Run `sources.py N` before `audit.py N` for the full picture
(`--no-grounding` skips it).

## 11. Process — how a chapter is written and when it is done

**Standing instructions (prompt §1):**

1. A chapter is **generated in batches and the writer continues on his own until the end**: write a
   batch, run the batch gate, fix what fails, start the next batch, keep going — without stopping to
   ask, and without waiting to be told. Stopping mid-chapter is only for a real blockage (a source
   that cannot be located, a contradiction that needs a decision), never for a check-in.
2. **All ten works are read for every verse before a word of it is written.** Reading is research,
   not relay: what is learned is written as the book's own reading (§0), backed by evidence — the
   ten are never summarised or quoted (`STY-PARAPHRASE`, `SRC-QUOTED`), and their contents are
   taken as they stand rather than fact-checked.
3. **Spread the work, and write a long list of verses at a time** — several batches in flight at
   once, the largest stretches the material supports, and a short chapter in a single pass. Gate in
   parallel with `batch.py N --ranges A-B,C-D,E-F`.

**Batch discipline (prompt §10):**

4. Each batch: `batch.py N --from A --to B` (or `--ranges`), fix every FAIL, read every warning, then
   go straight on to the next batch. `batch.py N --progress` shows how far the chapter has come.
5. **Never leave a half-written verse**: a section is either the scaffold's `TODO` text or finished
   prose; drafts live in the scratch area, never in the chapter file.
6. **Re-read §4–§8 of the prompt before each batch** — the standard is the same for verse 200 as for
   verse 1.
7. **A batch is done when it is clean**, with no known problem carried forward. Commit per batch (or
   per two), on the session branch, with `Tafsir ch N (<Name>): verses A-B`; the payload, the
   `sw.js` bump and the worklog row wait for the end of the chapter.
8. **A chapter is done** when all of these hold:
   * `python3 scripts/tafsir/audit.py N` ends `RESULT: PASS` (no FAIL);
   * `python3 scripts/tafsir/status.py N` shows every verse above its own floor;
   * `python3 scripts/tafsir/build_data.py N` writes `data/tafsir_NNN.json` and `--check` reports no
     stale payload — and the payload is never built from a scaffold (`build_data.py` refuses a
     chapter with `TODO` verses);
   * `sw.js` `CACHE_VERSION` is bumped;
   * `TAFSIR_WORKLOG.md` has the chapter's row (generated with `status.py --md`, not typed by hand);
   * commit `Tafsir ch N (<Name>): verse-by-verse from all <k> sources` and push to the session
     branch only.
9. **`python3 scripts/tafsir/selftest.py`** must show every rule caught whenever `audit.py` changes
   (a `MISS` is a rule the gate does not enforce, a `FIRE` a rule firing where it must not); the
   cases for the v7 rules (§0) are also in **`python3 scripts/tafsir/ruletest.py`**, which runs on
   synthetic prose and therefore works while no chapter is on disk.

**Working agreement (pipeline §5):**

10. One chapter, one file, `tafsir/NNN.md`; never edit another chapter's file in the same change.
11. Parallel work splits **by chapter**, never by verse within one file — two writers on one file
    overwrite each other.
12. Only chapters that pass `audit.py` get a payload, a worklog row and a commit.
13. Chapter order is ascending, 001 → 114.

## 12. What the pass deliberately does not do (prompt §11)

1. It does not mirror, summarise or quote any of the ten: it learns from all of them and writes
   one clear account in the book's own voice (§0) — and no verse of it is presented in the shape or
   the diction of the one before (§0.7).
2. It does not transliterate long Arabic passages, quote poetry at length, or reproduce the academic
   apparatus of the sources.
3. It does not argue theology, or adjudicate between schools on matters the verse does not settle.
4. It does not fill silence: where a phrase has little material, the prose stays honest and brief
   rather than padded — the verse's floor is met from the material the sources do carry.

---

## Appendix A — every gate code, and what it means

`level` is the level the code is raised at; `fail/warn` means both variants exist.

| Code | Level | Rule |
|---|---|---|
| `FMT-FILE` | fail | `tafsir/NNN.md` does not exist |
| `FMT-TITLE` | fail | title line is not `# Sūrah <name> (Chapter N) — Verse-by-Verse Tafsir` |
| `FMT-INTRO` | fail | `## Introduction to the Sūrah` missing |
| `FMT-INTRO-POS` | fail | introduction heading not on line 3 |
| `FMT-INTRO-EMPTY` | fail | empty introduction |
| `FMT-INTRO-HEADINGS` | warn | `**bold**` inside the introduction |
| `FMT-INTRO-SEP` | fail | `---` inside the introduction |
| `FMT-VERSES` | fail | verse headings not 1..N, ascending, one each |
| `FMT-SPACING` | fail | no blank line after the verse heading or the quote |
| `FMT-QUOTE` | fail | missing the `> …` verse line |
| `FMT-QUOTE-LINES` | fail | the verse quote is more than one line |
| `FMT-QUOTE-VERBATIM` | fail | quote differs from `data/chapter_NNN.js` |
| `FMT-PLACEHOLDER` | fail | `TODO`/`TBD`/`PLACEHOLDER` left in a section |
| `FMT-PARAGRAPHS` | fail | fewer than 2 prose paragraphs in a verse section |
| `FMT-HEADINGS` | fail | no headings in the section |
| `FMT-HEADINGS-FEW` | warn | only one heading |
| `FMT-HEADINGS-COUNT` | warn | more than 30 headings (soft) |
| `FMT-HEADING-SHAPE` | fail | heading not alone on its line with blank lines around |
| `FMT-HEADING-CASE` | fail | heading contains a lower-case letter |
| `FMT-HEADING-QUOTED` | fail | heading is the verse's own quoted wording |
| `FMT-HEADING-GENERIC` | fail | heading is a generic label |
| `FMT-HEADING-VERSE` | fail/warn | heading repeats the verse verbatim (6+ words / 4+) |
| `FMT-HEADING-LONG` | warn | heading over 12 words |
| `FMT-HEADING-DUP` | warn | heading repeated inside one section |
| `FMT-ORPHAN-HEADING` | fail | heading with no prose under it |
| `FMT-SEP` | fail/warn | separator wrong: none/two between verses, tight above, trailing at the end |
| `FMT-WHITESPACE` | fail | tab, trailing space, double blank line, wrong final newline |
| `WRD-FLOOR` | fail | verse below `max(500, 8 × verse words)`, capped 4,000 |
| `WRD-CEILING` | warn | verse above 5,000 words (check for padding) |
| `WRD-PARA-FLOOR` | fail | a paragraph of the commentary (introduction or verse) is 120 words or fewer |
| `STY-UNIQUE-VERSE` | fail/warn | a verse repeats another verse's presentation (v7.1): a shared opening frame, a recurring run of unquoted prose, a reused or templated heading, one arrangement used by most verses of a long chapter |
| `WRD-INTRO` | fail/warn | introduction under 250 words / over 1,500 |
| `PHR-PHRASE-NONE` | fail | no phrase of the verse quoted in the prose |
| `PHR-QUOTE-STYLE` | fail | this verse's phrase not in bold italics (or non-own wording in that style) |
| `PHR-QUOTE-FOREIGN` | fail | bold-italic quote that is not this verse's wording |
| `PHR-PHRASE-COVERAGE` | fail/warn | under 90% of the verse's words quoted / incomplete |
| `PHR-PHRASE-GAP` | fail | more than 8 words passed over unquoted |
| `PHR-PHRASE-EDGE` | fail | first or last 3 words never quoted |
| `PHR-PHRASE-MISSING` | fail | a phrase of the verse is never quoted in the prose |
| `PHR-CHUNK` | fail/warn | one quoted stretch swallows 65%+ / 40%+ of a 12+-word verse |
| `PHR-EVIDENCE` | fail | a quoted phrase has no evidence beside it |
| `REF-RANGE` | fail | citation is not a real verse of the Qur'an |
| `REF-QUOTE` | fail | cross-reference quote is not verbatim |
| `REF-QUOTE-STYLE` | fail | cross-reference quote is italic instead of bold only |
| `REF-LONG` | fail/warn | cross-reference clause over 34 words / over 22 |
| `REF-QUOTE-REPEAT` | warn | the same verse quoted twice in one section |
| `REF-SELF-QUOTE` | warn | this verse's own wording re-quoted in reference style |
| `REF-UNANCHORED` | warn | Qur'an clause in curly quotes with no reference beside it |
| `REF-STRAIGHT-QUOTE` | fail | Qur'an wording in hadith-style straight quotes |
| `EVD-NONE` | fail | no checkable anchor in the section |
| `EVD-THIN` | warn | only one kind of evidence |
| `EVD-ATTRIBUTION` | fail | prophetic report without its collection |
| `EVD-NUMBER` | fail | a hadith number that appears in no source for the verse |
| `EVD-QUOTE-STYLE` | fail/warn | report/athar in curly quotes (25+ words / 12+) |
| `STY-LABELS` | fail | an element is labelled instead of shown |
| `STY-SOURCE-PARADE` | fail/warn | section written source by source (§7 thresholds) |
| `STY-ANALYSIS-FLOOR` | fail/warn | fewer than 4 / fewer than 8 sentences that reason |
| `STY-ANALOGY` | fail/warn | no analogy in this verse / chapter share below 60% / below 40% |
| `STY-APPLICATION` | warn | the verse never reaches the reader's own world (v7) |
| `STY-DICTION` | fail/warn | 6+ formal words / 1–5 formal words |
| `STY-SENTENCE` | fail/warn | mean sentence over 32 / over 26 words |
| `STY-SENTENCE-LONG` | fail/warn | over 25% / over 12% of sentences past 40 words |
| `STY-READABILITY` | fail/warn | Flesch below 45 / below 55 |
| `STY-LONGWORDS` | warn | over 2% of words are 12+ letters |
| `REP-SENTENCE` | fail | the same sentence (10+ words) appears twice in the chapter |
| `REP-TEMPLATE` | fail/warn | 8-gram overlap with another section above 30% / above 18% |
| `REP-QUOTE` | warn | the same wording quoted more than 4 times in the chapter |
| `REP-FILLER` | fail/warn | filler, meta prose, machine voice or cliché (§9) |
| `SRC-BANNED` | fail | a work outside the ten is cited |
| `SRC-NODIGEST` | fail | `tmp/sources/NNN.json` missing: the ten were never pulled |
| `SRC-NOTCHECKED` | fail | a work that covers the verse was never pulled for it |
| `SRC-ABSENT` | warn | no text for this verse anywhere in the repo (upstream gap) |
| `STY-PARAPHRASE` | fail | the prose relays a point to a named work (§0; v7) |
| `SRC-QUOTED` | fail | a work of the ten is quoted beside its name (v7) |
| ~~`SRC-SPREAD`~~, ~~`SRC-FAMILY`~~, ~~`SRC-UNUSED`~~ | retired | the old naming quotas; naming a work to summarise it is now a failure (v7) |
| `MTCH-BOLD` | fail | bold used outside the three markers (heading, this verse's phrase, another verse's clause) |
| `MTCH-WORD` | fail | a headword that neither is the verse's wording nor means the same thing as anything in it |
| `MTCH-TERM` | fail/warn | Arabic offered as the verse's own wording (fail) / Arabic carried as a language point with no meaning in the verse (warn) |
| `MTCH-SYNONYM` | info | the headword means what the verse says in other words: the comparison is adjusted to the verse's own wording |
| `GRD-TOKENS` | warn | named/foreign terms not found in the verse's sources (advisory) |

**The codes number 75 in all**: 27 `FMT-*`, 9 `PHR-*`, 3 `WRD-*`, 5 `EVD-*`, 8 `REF-*`,
3 `REP-*`, 8 `STY-*`, 7 `SRC-*`, 4 `MTCH-*`, 1 `GRD-*`.

## Appendix B — the numbers, in one table

| Rule | Value |
|---|---|
| Sources allowed | the 10 of `corpus.SOURCE_ALLOWLIST`, nothing else |
| Works named per verse | none required; a named work in a summary fails (`STY-PARAPHRASE`, v7) |
| Verse floor | `max(500, 8 × verse words)`, capped 4,000 |
| Verse soft ceiling | 5,000 |
| Paragraph floor | past 120 words, introduction and verses alike; a heading may carry several paragraphs (`WRD-PARA-FLOOR`) |
| No house style across verses | 4-word opening frame in 2 verses: warn / 3: fail; 6-word free-prose run in 2: warn / 3: fail; reused heading: fail; 2-word heading opening in 2: warn / 3: fail; one arrangement at 70% of a 10+-verse chapter: warn / 90%: fail (`STY-UNIQUE-VERSE`) |
| Introduction | 250–1,500 words |
| Phrase coverage | ≥ 90%, no unquoted gap over 8 words, edges within 3 words |
| One quoted run | ≤ 40% of a 12+-word verse (warn), ≤ 65% (fail) |
| Cross-reference clause | ≤ 22 words (warn), ≤ 34 (fail) |
| Report quotes | straight quotes; curly-quoted passages warn at 12 words, fail at 25 |
| Source-led sentences | warn above 18%, fail above 30%; 3 in a row fails |
| Source-led paragraphs | warn above 30%, fail above 45% |
| Reasoning sentences per verse | ≥ 4 (fail below), ≥ 8 preferred |
| Analogy | warn if a verse has none; fail if under 40% of verses have one |
| Mean sentence | target < 22, warn > 26, fail > 32 words |
| Sentences over 40 words | target < 8%, warn > 12%, fail > 25% |
| Reading ease | target 60+, warn < 55, fail < 45 |
| Words of 12+ letters | target < 1%, warn > 2% |
| Duplicate sentence | 10+ words, anywhere in the chapter |
| Section template overlap | warn > 18%, fail > 30% (8-grams) |
| **v7.1 — no house style** | same 4-word sentence opening in 2 verses: warn; 3: fail. Same 6 words of unquoted prose in 2 verses: warn (>6 such phrases: chapter warn); 3: fail. Heading reused verbatim: fail. Same 2-word heading opening in 2 verses: warn; 3: fail. One arrangement (headings × paragraphs) in a chapter of 10+ verses: warn at 70% of verses, fail at 90% (`STY-UNIQUE-VERSE`) |
| Headings per verse | ≥ 1 (fail 0, warn 1), soft maximum 30; ≤ 12 words |
| Bold | only the UPPERCASE headings, this verse's phrases (bold italics), other verses' clauses (bold only) |
| Explained words | must be the verse's wording, or mean the same thing — one word or a whole phrase; a synonym is adjusted to the verse's own word (`MTCH-SYNONYM`) |
| Reports | italic `*"…"*`, never bold |

## Appendix C — the commands

```bash
# inputs
python3 scripts/tafsir/sources.py N --stats          # where the material is
python3 scripts/tafsir/sources.py N                  # digest → tmp/sources/NNN.{txt,json}
python3 scripts/tafsir/scaffold.py N                 # skeleton → tafsir/NNN.md (quotes byte-exact)
python3 scripts/tafsir/scaffold.py N --phrases       # the phrase cut each verse is measured against
python3 scripts/tafsir/verify.py "<claim>" --chapter N   # is a named claim the reports carry? (v7)

# while writing
python3 scripts/tafsir/batch.py N --from A --to B         # gate this batch
python3 scripts/tafsir/batch.py N --ranges A-B,C-D,E-F    # several batches at once, in parallel
python3 scripts/tafsir/batch.py N --progress              # how far the chapter has come

# when the chapter is finished
python3 scripts/tafsir/audit.py N                    # must end in RESULT: PASS
python3 scripts/tafsir/status.py N                   # words per verse against its floor
python3 scripts/tafsir/build_data.py N               # → data/tafsir_NNN.json
python3 scripts/tafsir/build_data.py N --check       # payload matches the markdown
python3 scripts/tafsir/selftest.py                   # does the gate catch each rule?
python3 scripts/tafsir/ruletest.py                   # the v7 rules, with no chapter needed
```
