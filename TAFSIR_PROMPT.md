# The generation prompt — one chapter of verse-by-verse tafsir

This is the prompt. Hand it to whoever (or whatever) writes a chapter, together with:

* the chapter number,
* `TAFSIR_PIPELINE.md` (the runbook: what the tools are and how to run them),
* the repository itself, so `scripts/tafsir/*` and the tafsir sources are on disk.

Nothing else is needed. The chapter is written from the sources that discuss *that verse*, in
the format below, and it is not finished until `scripts/tafsir/audit.py N` prints **PASS**.

---

## 1. The job

Write the verse-by-verse tafsir for **one chapter** of the Qur'an, in simple English, from the
**eleven** works this corpus is written from (`tafsir-*/NNN.txt` and `tafsir_initial/NNN.md`; the
list is `corpus.SOURCE_ALLOWLIST` and nothing outside it is a source):

| Work | In the repo | What it is for |
|---|---|---|
| `tafsir-al-tabari` | Arabic | the maʾthūr root: reports, chains, the first generations |
| `tafsir-al-qurtubi` | Arabic | rulings, occasions, disagreements |
| `tafsir-al-baghawi` | Arabic | the maʾthūr tradition, concisely |
| `tafsir-ibn-kathir` | English | reports with grading; the one a reader can quote back |
| `tafsir-al-alusi` | Arabic | language, grammar, the later scholarly debate |
| `tafsir-al-jalalayn` | English | the plain running sense |
| `tafsir-ibn-abbas` | English | the earliest gloss |
| `tafsir-as-saadi` | Arabic | the modern meaning-first reading |
| `tafsir-ibn-uthaymeen` | Arabic | the modern teaching tafsir (partial coverage — see §7) |
| `tafsir-maarif-ul-quran` | English | the modern reading, fiqh and contemporary questions |
| `tafsir_initial` | English | the study-Quran-style draft, **the eleventh work (v7.2)** — read for its material like the rest, partial coverage, never relayed or quoted |

One file per chapter: `tafsir/NNN.md`.

The reader is a general Muslim reader with no Arabic and no seminary training. The text must
answer: what does this verse say, what does it mean, what does it ask of me, and what is the
evidence? It must be worth reading twice.

Everything you write about a verse must be traceable to a source that discusses that verse, to
the Qur'an's own text, or to a report the sources carry. No invention, no padding, no
paraphrase of the translation dressed up as commentary.

**Six standing instructions:**

1. **The start is the author's to give; the run is yours to finish.** When the author says
   "continue" and nothing more, the first act is to ask where the run should begin — a chapter, or a
   chapter and verse — and to wait for the answer (v7.5, §0.9). No verse is planned, mapped or
   written before it comes. Once it is in hand, take it as the run's first verse
   (`run.py --plan --start N[:M]`, which pins the fifty; a chapter alone means that chapter's first
   unwritten verse), then write the run in stretches, gate each stretch with `batch.py N --from A
   --to B` as it lands, fix what fails, and start the next stretch — **without stopping to ask, and
   without waiting to be told** — until all fifty verses of the run are written and clean
   (`run.py --check` prints RUN COMPLETE at 50/50; a run left at forty-nine is not finished), and
   the chapter gate `audit.py N` passes for any chapter finished on the way. A run is a marathon,
   not a lap: after the start, the only reasons to pause are a source that cannot be located or a
   contradiction that needs a decision (§10).
2. **All eleven are read for every verse before a word of it is written — and none of them is
   relayed, compared or quoted.** Run the digest for the verse, read what each of the eleven says
   about it (Arabic sources included: read them and put the substance into English), then write
   **the book's own reading** from what you learned. The gate proves the reading mechanically:
   `sources.py` must have pulled the verse's text for all eleven (`SRC-NOTCHECKED`); a sentence that
   hands the point to a work (`STY-PARAPHRASE`) or quotes one (`SRC-QUOTED`) fails; naming a work
   outside the eleven fails (`SRC-BANNED`). Their contents are authenticated, so they are taken as
   they stand — no fact-checking them, no grading their chains, no survey of who said what: the
   evidence the reader checks is the Qur'an, the reports with their collections, and the early
   authorities as the reports carry them.
3. **No verse is presented like the last (v7.1).** There is no house style of shape in this book: no stock way to open a paragraph, no heading template, no fixed arrangement. (The diction of the book's own voice is one — instruction 6.)
   Before writing a verse, look at how the previous three were built and build this one
   differently — two movements instead of three, a heading carrying three paragraphs instead of
   one, a verse that opens on the history where the last opened on the phrase. The gate fails a
   repeated sentence frame (three verses), a run of six words of unquoted prose recurring in three
   verses, a heading reused or templated, and (in chapters of ten verses or more) one arrangement
   used by most verses (`STY-UNIQUE-VERSE`). Only quoted matter — the verse's own phrases, cited
   clauses, a report's words — is allowed to come again.
4. **Work in runs of fifty verses, mapped once and finished before you pause (v7.2), cut from the
   author's start (v7.5).** The run is the unit of work and it may span chapters: the writer never
   picks its first verse, and never moves it to the frontier. It begins where the author said —
   `run.py --plan --start N[:M]` (a chapter alone means that chapter's first unwritten verse) — and
   that call pins the fifty; every later `--check`, `--status` and `--slice` reads the same pinned
   run. Then `run.py --build`: the whole run is pulled out of all eleven works in one pass, so the
   sources are opened once for fifty verses instead of once per verse, and the map is then read in
   slices. Write, gate and fix until **every one of the fifty is written and clean** (`run.py
   --check` prints RUN COMPLETE at 50/50); that is what "the run is finished" means. Speed comes
   from the map being in hand and from working several stretches of the run in parallel — `batch.py
   N --ranges A-B,C-D,E-F` gates them at once — never from lowering the standard.

5. **A tafsir, not talk (v7.3).** What is written is an exposition that teaches the verse, in simple
   English and with real substance: the wording explained phrase by phrase; what has been
   transmitted about it — the occasion of revelation, the reports, and the early authority the
   reading comes from (a Companion, a Successor, one of the first imams), named where it carries the
   point; the language the verse turns on — the term, its root, the grammar or the reading that
   changes the sense, explained in the sentence that uses it; what the verse settles in creed, law
   and conduct, stated as the reading rather than as a survey of opinions; where the Book says the
   same thing elsewhere, every citation with its clause; and the reasoning — why the words carry
   the reading given, and what turns on it. Two floors are mechanical: every verse carries a
   cross-reference with its clause (`REF-NONE`) and a transmitted reading, an early authority named
   or a report with its collection (`EVD-TAFSIR`). Simple English is the sentence, not the
   substance: the terms a tafsir needs (*tawḥīd*, *naskh*, *qirāʾah*, *sabab al-nuzūl*) are
   explained once and then used. A general reflection that would fit any verse, an address to the
   reader, a rhetorical question, and praise of the text in place of its explanation are not the
   commentary.

6. **The register of the book (v7.4).** The diction was set by studying the professional English style
   of a published tafsir (*Illuminating Discourses on the Noble Qur'an*) — its style of writing and
   choice of words only; nothing of its content enters this book, and it is never named or quoted in
   it. Write that register: plain declaratives, one idea to a sentence; **third person throughout**
   — the verse and the people it speaks about are the subject, never "you", never an authorial "we";
   no contractions (*does not*, *cannot*, *it is*), no exclamation, no hype words, no praise of the
   text; a question raised only where it is answered in the same movement; terms of art glossed once
   in place (*taqwā*, *shirk*, *sunnah*) and then used; evidence in plain reporting language —
   *"Abū Hurayrah reports that the Prophet said, '…' (Muslim)"*, *"It is sunnah to…"*. The gate
   enforces it on the commentary's own words, with quotations stripped first: `STY-CONTRACTION`,
   `STY-EXCLAIM`, `STY-HYPE`, `STY-QUESTION` (three questions in one section fails). Read §0.11 of
   `TAFSIR_RULES.md` before the first sentence of a chapter.
7. **The book quotes no book (v7.4).** This is an independent book: it names, summarises, paraphrases
   and quotes no work — not the eleven behind it, not any other book. What may be quoted is what
   those books quote as evidence, in the same shape they quote it: the Qur'an in this book's citation
   form (every clause verbatim, §0.8); a report — hadith or athar — in the straight-quote style with
   its collection named in the same sentence; a transmitted reading attributed to an early authority
   by name. Everything else is the book's own statement. The gate: `IND-WORK` (a work named),
   `IND-QUOTE` (a quotation hanging on no reference), with `SRC-BANNED`, `STY-PARAPHRASE` and
   `SRC-QUOTED` behind them (§0.12 of `TAFSIR_RULES.md`).

## 2. Build the inputs first

```bash
cd /home/user/quran-explained

python3 scripts/tafsir/run.py --plan --start 2:1   # the fifty from the author's start: a chapter (2)
                                                   # or a chapter:verse (2:1); ask for it, never pick it
python3 scripts/tafsir/run.py --build              # all eleven works for the run, mapped in one pass
python3 scripts/tafsir/run.py --slice 2:1 2:5      # read the map a stretch at a time
python3 scripts/tafsir/run.py --check              # RUN COMPLETE only when all fifty are clean

python3 scripts/tafsir/sources.py N --stats        # where the material is, before reading
python3 scripts/tafsir/sources.py N                # writes tmp/sources/NNN.txt + NNN.json
python3 scripts/tafsir/scaffold.py N               # writes tafsir/NNN.md with byte-exact verse quotes
python3 scripts/tafsir/scaffold.py N --phrases     # the phrase cut each verse is measured against
python3 scripts/tafsir/reference.py 2:255          # ready-made citations for a cross-reference
python3 scripts/tafsir/reference.py --scan N       # every bare citation in tafsir/NNN.md + its expansion
python3 scripts/tafsir/assemble.py N               # splice tmp/work/cN_v*.md drafts into the chapter
python3 scripts/tafsir/verify.py "<claim>" --chapter N   # confirm a source really makes a point
```

The scaffold hands you one free win: the verse quote is copied byte-for-byte from
`data/chapter_NNN.js`, so it cannot fail the verbatim check. The headings are yours to write, and
so is the phrase-by-phrase reading: `scaffold.py N --phrases` prints, for every verse, the units
`corpus.split_phrases` proposes — a plan to work from, not headings to paste.

For a single verse or a single source, read the digest directly:

```bash
python3 scripts/tafsir/sources.py N --verse V --slug tafsir-ibn-kathir --cap-en 12000 --stdout
```

`tmp/sources/NNN.txt` is the working document. It carries the canonical translation of every
verse and, under it, what each source says about that verse. Caps keep it readable; raise
`--cap-en` / `--cap-ar` when a verse needs the full discussion.

## 3. Read like a researcher, not a summariser

Work through the digest verse by verse, and for each verse collect **evidence**, not prose:

| Look for | Why it belongs in the section |
|---|---|
| Occasion of revelation (asbāb al-nuzūl) | fixes the historical setting |
| A prophetic report with its collection, narrator, and grade when the source gives one | the strongest anchor a verse can have |
| A Companion's or Successor's gloss (Ibn ʿAbbās, Qatādah, Mujāhid, al-Suddī, ʿIkrimah) | shows how the first generations read the words |
| A lexical or grammatical point that changes meaning (root, pronoun, word order, the definite article) | explains the verse rather than describing it |
| Variant readings (qirāʾāt) and **why** the difference matters | shows the text's depth without disputing it |
| A named classical authority's ruling or reading (al-Ṭabarī, al-Qurṭubī, Ibn Kathīr, al-Shāfiʿī, Abū Ḥanīfah, Mālik) | the reader can follow the disagreement |
| A modern reading — al-Saʿdī, Ibn ʿUthaymīn, Maʿārif al-Qurʾān — on what the verse asks of a reader now | ties the verse to the life being lived today |
| A cross-reference that lets the Qur'an explain itself | the standard of evidence in this corpus |
| A refusal — where a source declines unauthenticated material | equally worth recording, honestly |

Arabic sources are first-class material here. Read them and translate the substance accurately
into the book's own English. Do not machine-translate a paragraph and paste it in; that produces
prose no reader wants.

**What you do with the research (v7).** The eleven are what the book was learned from — they are not
its voices. Nothing you write relays a work's opinion, compares the works, or quotes one of them:
*"al-Ṭabarī records that…"*, *"according to al-Saʿdī"*, *"the commentators say"* all fail
(`STY-PARAPHRASE`), and a quotation beside a work's name fails (`SRC-QUOTED`). Their contents are
authenticated: take them as they stand, without fact-checking them, grading their chains, or
surveying who said what. Where the material holds two readings that matter, state the readings as
facts about the verse — which one the wording supports, and what turns on it — not as a dispute
between books. What survives from the research as a *name* is evidence: a Companion or Successor as
the reports carry him, a hadith with its collection, held to what it actually says.

**Watch for duplicated source records.** Some upstream files repeat the same text across
different tafsir names (for example, several English sources carry an identical Sufi passage for
Sūrah 1, and al-Baghawī and al-Saʿdī repeat their whole-sūrah introduction under every verse).
When two sources say the same thing, that is one witness, not two.

## 4. Write it in the chapter format

The file is parsed by `scripts/tafsir/build_data.py` and checked by `audit.py`, so the shape is
fixed. `scaffold.py N` writes this skeleton with the verse quotes already in place; the headings
and the prose are yours, and `scaffold.py N --phrases` shows the phrase cut each verse is
measured against.

```markdown
# Sūrah <Name> (Chapter N) — Verse-by-Verse Tafsir

## Introduction to the Sūrah

Introduction prose in plain paragraphs, 250–1,500 words, no headings, no separators.

---

## Verse N:1

> <the canonical translation, exactly as it stands in data/chapter_NNN.js>

**A DESCRIPTIVE TITLE: THE SETTING, THE STORY, OR WHAT THIS PARAGRAPH SETTLES**

Prose. The verse's own words are quoted *inside* the paragraph in **bold italics** —
***“the first phrase of the verse”*** — and explained here, with the evidence for it beside the
quote: a cross-reference (C:V — **“clause”**), a hadith with its collection, or a named authority.

**ANOTHER DESCRIPTIVE TITLE**

Prose. Whatever the verse still needs: the history behind it, the ruling it carries, the next
phrase quoted and explained, the analogy.

---

## Verse N:2
...
```

The heading is never the verse's phrase, and it is written in **UPPERCASE**. It names what the
paragraph does — much as the old commentary on this site titled its paragraphs. The phrases live
*inside* the paragraphs, and not every paragraph carries one: context, history, reports and rulings
are headings of their own.

Three markers carry the quoting — **and they are the only three things in the whole file that may be
bold**:

| What is quoted | How it is written |
|---|---|
| A phrase of the verse being explained | **bold italics**: `***“the phrase of this verse”***` |
| A clause of any other verse (a cross-reference) | **bold only**: `(C:V — **“the clause”**)` |
| A heading | **UPPERCASE**, **bold**, no quotes, never the verse's words |
| A report, an athar, a scholar's words | *italics with straight quotes*: `*"what was said"*` — never bold |

Anything else in bold — a name emphasised, a term of art, a phrase the writer wants the reader to
notice — fails `MTCH-BOLD`. The commentary's own voice carries no emphasis at all: **bold is the
Qur'an's, italics are the report's, plain text is the writer's**.

A cross-reference is **always expanded** (v7.2): the citation carries the clause under discussion,
copied from `data/chapter_NNN.js` — `(2:255 — **“Allah! There is no god ˹worthy of worship˺ except
Him”**)`. A bare `(2:255)`, or a list like `(2:156, 245, 281)`, is a number the reader cannot read:
one or two in a section warn (`REF-BARE`) and three in one section fail. `scripts/tafsir/reference.py
2:255` prints the clauses ready to paste, and `--scan N` finds every bare citation in a chapter and
prints its replacement (`--write` applies them). Never type a clause by hand — a typed clause is how
`REF-QUOTE` failures happen.

Rules the auditor enforces:

1. **Title line** exactly `# Sūrah <name_en> (Chapter N) — Verse-by-Verse Tafsir`.
2. **Introduction** under `## Introduction to the Sūrah` on line 3: 250–1,500 words, plain
   paragraphs, no bold headings inside it, one `---` after it.
3. **Every verse** appears once, ascending, as `## Verse N:V`, and every verse of the chapter
   must be present. No skipped verses, no combined verses, no invented verse numbers.
4. **Verse quote**: one line, starting `> `, byte-identical to that verse's `ayah_en` in
   `data/chapter_NNN.js`, with one blank line above and below.
5. **Headings are UPPERCASE descriptive titles, never the verse's own phrases** (see §5). A heading
   is a short title of its own — `**THE SETTING AT MOUNT SAFA**`, `**WHY THE DIRECTION CHANGED**`,
   `**WHAT THE MIDDLE COMMUNITY MEANS**` — alone on its line, blank line before and after, and
   answered by prose. A heading with a lower-case letter fails `FMT-HEADING-CASE`, and
   `**“phrase of the verse”**` fails `FMT-HEADING-QUOTED`. Titles must not be generic
   (`COMMENTARY`, `EXPLANATION`, `SUMMARY`, `NOTE`) and each must be followed by real prose.
6. **Every phrase of the verse is quoted inside the prose and explained, in verse order, with
   evidence** (see §5). Not every heading carries a phrase: a paragraph of context, history or
   ruling may quote none.
7. **Length follows substance, and the floor is high.** Every verse carries at least **500
   words**, and the floor rises steeply with the verse: `max(500, 8 × the verse's own word count)`,
   up to 4,000. A fifty-word verse therefore needs 500 (its scaled floor, 400, sits under the base);
   a ninety-word verse needs 720+; a two-hundred-word verse needs 1,600+.
   The soft ceiling is 5,000 words — above that, check for padding. These numbers live in
   `audit.py` (`MIN_VERSE_WORDS`, `SCALE_FACTOR`, `SCALE_CAP`) and `scaffold.py` restates them in
   each TODO line, so a writer always sees the floor for the verse in front of them. Go up when
   the material is there, never sideways: a verse with a long discussion in al-Ṭabarī and al-Alūsī
   should be written long because the material is long.
8. **One `---`** between sections. No trailing separator after the last verse.
9. **Hygiene**: no tabs, no trailing spaces, no double blank lines, single newline at the end.
10. **No placeholder** text (`TODO`, `TBD`) may survive into the file.
11. **Bold is reserved, and the prose explains the verse as quoted** (see §5.1). Nothing is bold
    except the three markers above; and no sentence explains a word — English or Arabic — that the
    verse's translation does not carry. A word-study of a word the reader cannot see in the verse
    line fails (`MTCH-BOLD`, `MTCH-WORD`, `MTCH-TERM`).

### 4.1 Where the length comes from

Length is not padding. It comes from the material this corpus now has:

* the phrase-by-phrase explanation itself, which quotes each phrase and then unpacks its words;
* the stories and occasions of revelation the sources carry for that verse;
* the hadith and athar, told in full, with narrator and collection;
* what the early authorities carried — the Companion or Successor the reading is learned from,
  named where it carries the point (`EVD-TAFSIR`);
* the language the verse turns on — the term and its root, the grammar or the reading that changes
  the sense, explained in the sentence that uses it;
* the rulings the verse settles, stated as the reading — and where two readings genuinely differ,
  the difference and what turns on it;
* the cross-references that let the Qur'an explain the verse;
* one relatable analogy, and the practical lesson the verse asks of the reader;
* the history the sources carry: what was happening when the verse came, who it was spoken to,
  what happened next;
* where the verse meets the present: the working of the natural world a reader can see for
  himself, and the plain application to a household, a wage, a neighbour, a grief — the book is
  written for a reader now, and every verse reaches him at least once (`STY-APPLICATION`).

And every paragraph of it — here and in the introduction — runs past 120 words (`WRD-PARA-FLOOR`):
a paragraph is a complete movement of thought, so a thought too small to reach 121 words belongs
with the paragraph beside it.

**The register: plain sentences, full substance (v7.3).** Simple English governs the sentence — short
clauses, everyday words — and not the content. The reader is entitled to the transmitted reading,
the language point, the ruling, the cross-reference and the reasoning, and the prose delivers them
without the vocabulary of the seminary standing unexplained. What it never does is replace that
substance with general reflection: a paragraph that could sit under any verse unchanged, an address
to the reader, a rhetorical question, or praise of the text ("what a beautiful verse") is talk, not
tafsir, and the gate warns for it (see the filler list). If a paragraph is under the verse's floor
and there is nothing more to say about the verse, the answer is to go back to the digest and find
the material that has not been used — never to widen the sentence.

**Paragraphs under a heading.** Nothing requires one paragraph per heading. A heading introduces a
movement of thought, and that movement may run in two paragraphs or five; what the gate checks
(`WRD-PARA-FLOOR`) is that **every paragraph runs past 120 words**, wherever it sits. Use the
freedom: a long explanation reads better split where the thought turns than crammed into one block.

### 4.2 The elements are shown, never labelled

A verse is expected to carry, as the material allows: its historical setting and what followed
it; reports with their collections; cross-references that let the Qur'an explain itself; rulings
where a ruling is in view; a lesson; a plain explanation a beginner can follow without the
vocabulary of the seminary; one simple analogy; and the point at which the verse touches life
today. These are the substance of the section — and they are **never announced**. No `Lesson:`,
no `Modern application:`, no `History:`, no `Cross-reference:`, no `Explanation:`, no
`Takeaway:`. The reader should meet the history as narrative, the lesson as a conclusion the
paragraph arrives at, the application as something he recognises in his own week. `STY-LABELS`
fails a chapter that labels any of them. The test is simple: if a heading or a sentence exists
only to announce what kind of content follows, delete it and let the content speak.

### 4.3 One reading — the book's own, with the research behind it

The eleven works are what the book was **learned from**, not what it speaks about. A section is an
argument about what the verse says and asks, written in the book's own voice; what the reader can
check — cross-references, reports with their collections, early authorities — is the evidence
carrying it. A sentence that hands the point to a work (*"al-Ṭabarī records that…"*, *"according to
al-Saʿdī"*, *"the commentators say"*) fails (`STY-PARAPHRASE`), and quoting one fails
(`SRC-QUOTED`). What fails just as surely is the other old shape: a paragraph that opens with a
work's name and paraphrases it, then another paragraph for the next work — a report on a library,
not tafsir.

Write so that a reader follows **the verse**, and nothing else:

* open paragraphs with the point being made — never with a work's name;
* where the material holds two readings that matter, state the readings themselves, which one the
  wording supports, and what turns on it — the reader is reading the verse, not a dispute between
  books;
* a Companion or Successor may be named as evidence for a reading (Ibn ʿAbbās, Mujāhid, Qatādah, as
  the reports carry them) — one mention, where the reading needs it, never a roll-call;
* keep an argument running across the paragraphs of a section: the phrase, what it means, what the
  grammar does, what follows for the reader;
* use the Qur'an and the report to settle questions, not just to decorate a paragraph;
* analyse — say why a reading is right, what it implies, what changes if it is not.

The gate counts it. In every verse section, `STY-PARAPHRASE` fails the first sentence that hands a
point to a work, `SRC-QUOTED` fails a quotation beside a work's name, and `STY-SOURCE-PARADE` still
fails a run of three sentences opening with a named authority (or more than 30% of the section's
sentences, or 45% of its paragraphs — warns from 18% / 30%); `STY-ANALYSIS-FLOOR` fails a section
with fewer than four sentences that reason about the verse (*because*, *so that*, *which means*,
*the point*, *what follows*) and warns below eight.

If a section is under the floor, the answer is never repetition or vague exhortation. Go back to
the digest and use material you have not used yet — the Arabic sources usually carry more for
that verse than the English ones do.

## 5. The verse's phrases live in the prose — and every one is backed by evidence

The verse is read as a series of meaningful units, and each unit is quoted **inside the
paragraph** that explains it. This is the backbone of the chapter, and it is not the same thing as
the headings. A heading names the paragraph; the phrase is quoted *in* the paragraph, explained
there, and supported there by evidence. Several paragraphs in a verse may carry no phrase at all —
they carry the setting, the story, the ruling, the disagreement, the analogy.

**Two floors per verse (v7.3).** Every verse carries at least one cross-reference to another verse,
expanded with the clause it points to — without one the gate fails (`REF-NONE`) — and at least one
transmitted reading: an early authority named (a Companion, a Successor, one of the first imams) or a
report with its collection, without which it also fails (`EVD-TAFSIR`). The cross-reference belongs
in the paragraph it explains, beside the phrase it illuminates, not in a list at the end; the
transmitted reading is named where it carries the point, in the book's own sentence, never as a
work-by-work survey.

**How to cut a verse.** `scaffold.py N --phrases` prints the cut `corpus.split_phrases` proposes,
which breaks at strong punctuation (— ; : ? !) and before conjunctions, keeps every word of the
verse and never leaves a fragment. Re-cut it whenever you can see a more meaningful unit, as long
as three things stay true:

* the quoted phrases run in verse order and together account for the whole verse;
* each phrase is the verse's own wording, copied — not paraphrased;
* no single quote swallows the verse: a stretch longer than about half of a verse of twelve words
  or more is a sign that the verse is being quoted instead of explained.

Good cuts for `1:1`: `“In the Name of Allah”` and `“the Most Compassionate, Most Merciful”`. Good
cuts for `2:255` include `“Allah! There is no god ˹worthy of worship˺ except Him, the Ever-Living,
All-Sustaining.”` and `“Who could possibly intercede with Him without His permission?”`. A cut that
separates a phrase from the word it leans on ("Neither drowsiness" / "nor sleep overtakes Him") is
a bad cut; merge it back.

**Marking the quotes.** This verse's own phrase, wherever it appears in the prose, is written in
bold italics: ***“the phrase of this verse”***. A clause quoted from any other verse is written in
bold only, inside its reference: (C:V — **“the clause”**). A phrase of this verse quoted plainly, or
in bold only, fails (`PHR-QUOTE-STYLE`); anything else in bold fails (`MTCH-BOLD`); an italic
cross-reference quote fails (`REF-QUOTE-STYLE`). Headings carry no quotes at all, and they are
UPPERCASE. A bold-italic quote is **always this verse's own words**: wording in that style that the
verse does not contain fails (`PHR-QUOTE-FOREIGN`).

### 5.1 The prose matches the verse it quotes

The reader's verse line is the translation above the section — that text, and no other, is what the
commentary explains. Every phrase quoted is a phrase of that translation, and everything the prose
holds up to explain **means the same thing as something in it**. A synonym here is exactly that: a
word *or a phrase* the verse does not use but that says what it says — *"the day of reckoning"* for
the verse's "the Day of Judgment", *raḥmah* for "the Most Merciful", *"the right way"* for "the
Straight Path".

* a headword that **means the same as** the verse's wording passes: the gate adjusts the comparison
  to the verse's own words and records it (`MTCH-SYNONYM`, informational), so the writer can line
  the sentence up with what the reader sees;
* a headword that means **something else** fails (`MTCH-WORD`): *"the word X means …"*,
  *"literally X"*, *"from the root X"*, *"the plural X"*, where X — English or Arabic — says
  something the verse's translation does not;
* **Arabic offered as the verse's own wording** fails (`MTCH-TERM`) even when the meaning is right:
  *"the verse says *kāfir*"* is a claim about the quoted line, and the line says "the disbelievers";
* Arabic carried as a free-standing language point warns (`MTCH-TERM`) when no meaning of it appears
  in the verse; when it does, the gate records the adjustment (`MTCH-SYNONYM`, informational).

When in doubt about a word before writing it:

```bash
python3 scripts/tafsir/match.py 1:4 "the day of reckoning" "the day of the harvest"
```

**How to write each phrase.** Take it apart in order: what the words mean, what the grammar does
(a definite article, a word placed first, a pronoun that shifts), what the early authorities said
about it, what it implies for how a person lives. Each phrase should normally carry one to four
paragraphs. Moving through the verse this way is the spine of the section; the headings around it
carry everything else the sources hold for that verse.

**Evidence beside every quote.** A quoted phrase is never left to stand on its own. The paragraph
holding it — or the paragraph straight after it — must carry one of:

* a Qur'an cross-reference, the standard of evidence here: `(C:V — **“clause”**)`;
* a prophetic report with its collection, narrator and grade when the source gives one;
* a named authority — a Companion or Successor (Mujāhid, Qatādah, al-Suddī,
  ʿIkrimah) as the works report him — whose reading is being reported;
* a lexical or grammatical point that changes the meaning.

**What the auditor checks** (`PHR-*`, `FMT-HEADING-*`):

| Check | Rule |
|---|---|
| Headings are UPPERCASE | any lower-case letter in a heading fails `FMT-HEADING-CASE` |
| Heading is a title, not a quote | a heading that is the verse's own phrase fails `FMT-HEADING-QUOTED` |
| This verse's phrases are bold italics | a phrase of the verse quoted plainly, or in bold only, fails `PHR-QUOTE-STYLE` |
| A bold-italic quote is this verse's wording | wording in that style that the verse does not contain fails `PHR-QUOTE-FOREIGN` |
| Other references are bold only | an italic cross-reference quote fails `REF-QUOTE-STYLE` |
| Nothing else is bold | any other bold fails `MTCH-BOLD` |
| Explained words mean the verse's | a headword that means the same as the verse's wording is adjusted to it (`MTCH-SYNONYM`, info); one that means something else fails (`MTCH-WORD`) |
| Arabic is not the verse's wording | Arabic offered as the verse's wording fails `MTCH-TERM` |
| Heading is not a copy | six or more words of the verse verbatim in a heading fails `FMT-HEADING-VERSE` (four or more warns) |
| Headings are real titles | generic labels and headings over twelve words warn; two or more per verse |
| The verse is quoted in the prose | at least 90% of its words, or `PHR-PHRASE-COVERAGE` |
| Every phrase is quoted somewhere | an unquoted phrase fails `PHR-PHRASE-MISSING` |
| Nothing is skipped | any unquoted run longer than 8 words fails (`PHR-PHRASE-GAP`) |
| Nothing is dropped at the edges | the first or last 3 words unquoted fails (`PHR-PHRASE-EDGE`) |
| The verse is split, not quoted whole | one quoted stretch carrying over half of a 12-word-plus verse fails `PHR-CHUNK` |
| Every quoted phrase is evidenced | a quote with no cross-reference, report, authority or language note beside it fails `PHR-EVIDENCE` |
| A clause is a clause | a cross-reference quote over 34 words fails `REF-LONG` (over 22 warns) |
| A verse is quoted once per section | the same verse quoted twice in one section warns (`REF-QUOTE-REPEAT`) |

## 6. Quoting law

* Qur'an wordings come **only** from `data/chapter_NNN.js`. Never from a tafsir's paraphrase,
   never from memory, never retyped if you can copy it.
* A quotation from **another** verse is written `(C:V — **“the clause under discussion”**)` — em
   dash, curly quotes, bold only — and the clause must be a verbatim substring of that verse's
   `ayah_en`. **Every** reference is written this way (v7.2): a bare citation, or a bare list of
   citations, is `REF-BARE` — a warning at one or two in a section, a failure from three.
* A phrase of **this** verse is written `***“the phrase of this verse”***` — bold italics — and must
   be a substring of this verse's `ayah_en` (the gate reports a foreign quote in that style).
* Quote the clause under discussion, not a whole long verse.
* A citation without its wording is **not** a cross-reference (v7.2). `scripts/tafsir/reference.py
   --find "<wording>"` finds the verse that carries a phrase, and `reference.py C:V` prints the
   clauses of a verse ready to paste.
* Hadith and athar are quoted inside emphasis with straight quotes: `*"..."*` — italic, never
  bold. Bold belongs to Qur'anic wording alone: this verse's phrase in bold italics, another verse's
  clause in bold only. Nothing else in the file is bold (`MTCH-BOLD`).
* Never re-quote a verse already quoted in the same section; cite it.
* Quotations from reports, athar and scholars are marked `*"..."*` (emphasis, straight quotes). A
  passage left in curly quotes outside a Qur'an reference is flagged: `EVD-QUOTE-STYLE` fails at 25
  words, warns at 12.
* Every citation must point to a real verse: `(2:300)` fails the gate.

## 7. Attribution law — non-negotiable

1. **Never invent a hadith number.** Give collection and narrator as the source gives them
   (`Ṣaḥīḥ al-Bukhārī 756`, `Muslim records Abū Hurayrah saying…`). If the source carries no
   number, the commentary carries no number.
2. **A number comes from the source or not at all.** `audit.py` reads every `Collection number`
   in the prose and fails (`EVD-NUMBER`) when that number appears in no source for the verse, in
   either script.
2. **Grade only what the source grades** (`At-Tirmidhī said ḥasan gharīb`, `a report whose chain
   al-Ṭabarī grades weak`).
3. **Never promote a witness account, a Companion's ruling, or a commentator's gloss to a
   prophetic saying.** Speaker → speaker: Companion → Companion, scholar → scholar, Prophet ﷺ →
   Prophet ﷺ.
4. **A prophetic saying always names its collection** in the same section. If you cannot say
   where it comes from, leave it out.
5. **Never attribute a point to a source that does not make it.** Under v7 few sentences carry a
   work's name at all (§3); the ones that name an early authority or a collection must be true to
   what the reports carry. Before a sentence credits anyone, find the passage. The digest is the
   first place to look; when the digest is thin, search the raw sources:

   ```bash
   python3 scripts/tafsir/verify.py "Musaylimah" --chapter 1     # does any source carry this?
   python3 scripts/tafsir/verify.py "مالك" --verse 1:4            # Arabic works too
   ```

   The tool prints every hit as `source chapter:verse snippet`. No hit means no credit: drop the
   claim, or state it without a name. A sentence that borrows authority from a source that never
   made the point is the worst failure this corpus can have, because it is invisible on re-reading.
   This check is not optional, and it is the reason `verify.py` exists.

## 8. Style law — plain words, short sentences, one good analogy

Write for a reader who has no Arabic and no seminary training: a shopkeeper, a student, a nurse
reading on a phone between tasks. Every sentence should be understandable on one reading.

**The numbers the gate measures** (on prose only; `batch.py` reports them for the stretch being
gated while the chapter is still being written, and `audit.py` for the whole chapter at the end):

| Measure | Target | Warn | Fail |
|---|---|---|---|
| Mean sentence length | under 22 words | above 26 | above 32 |
| Sentences over 40 words | under 8% | above 12% | above 25% |
| Reading ease (Flesch) | 60+ | below 55 | below 45 |
| Words of 12+ letters | under 1% | above 2% | — |

Short sentences are not childish. They are the difference between a reader who keeps going and one
who puts the phone down.

**Diction.** Say "so" not "subsequently", "show" not "demonstrate", "start" not "commence",
"use" not "utilise", "about" not "with regard to", "but" not "notwithstanding". The auditor fails
a chapter that leans on formal vocabulary (`STY-DICTION`). An Arabic term may be named where the
verse's own quoted phrase carries the point — *raḥmah* beside "the Most Compassionate" — but the
prose explains the wording the reader can see, not the Arabic behind it: a term the verse line does
not carry may not be the thing being explained (`MTCH-WORD`), and Arabic may never stand in for the
verse's wording (`MTCH-TERM`).

**Analogy.** Every verse should carry one simple comparison that a reader can picture, drawn from
ordinary life: a market, a road, a garden, a workshop, rain, a boat, a letter, a journey. The
comparison must fit the verse's own point, not decorate it. At least half of a chapter's verses
must carry one, or the chapter fails (`STY-ANALOGY`); leave a verse out only when no honest
comparison exists.

Worked examples from chapter 1:

* the basmalah as a traveller who names the owner of the river before his first stroke;
* "All praise is for Allah" as streams that all lead back to one spring;
* al-Raḥmān as rain that falls on good ground and on rock alike, and al-Raḥīm as the same rain
  turned into a harvest;
* the Day of Judgement as a market that trades all year and then closes for one final audit;
* "You alone we ask for help" as a new worker who accepts the foreman's orders before asking for
  the tools;
* the two ways of going astray as one traveller who refuses to board the train he has studied and
  another who never reads the timetable.

**Do not write:**

* process or meta prose ("this section", "we will now examine", "as mentioned above", "in
  conclusion") — the reader wants the verse, not the writing process;
* filler openers, closers and clichés ("rich tapestry", "stands as a testament to", "navigate the
  complexities", "it is worth noting");
* the same sentence twice anywhere in the chapter (the auditor compares every sentence), or two
  verse sections built from the same phrasing;
* generic exhortation that would fit any verse — if a paragraph could be pasted under another
  verse unchanged, it is not commentary.

**Do write:**

* verse-specific detail: the word being explained, the person in the story, the ruling at stake;
* transitions that carry the reader from one paragraph to the next;
* the "so what" sentence when the verse has a practical demand on the reader — once, briefly, in
  plain words.

## 9. Self-check before calling a chapter done

```bash
# while the run is being written, gate each stretch (see §10)
python3 scripts/tafsir/run.py --status              # how much of the fifty-verse run is written
python3 scripts/tafsir/run.py --check               # RUN COMPLETE only when all fifty are clean
python3 scripts/tafsir/batch.py N --from A --to B   # only the verses written so far
python3 scripts/tafsir/batch.py N --ranges A-B,C-D,E-F   # several stretches at once, in parallel
python3 scripts/tafsir/batch.py N --progress        # how far the chapter has come

# when the last verse is written, the whole chapter must pass
python3 scripts/tafsir/audit.py N              # must end in RESULT: PASS
python3 scripts/tafsir/status.py N             # words per verse against its floor, gate verdict
python3 scripts/tafsir/build_data.py N         # writes data/tafsir_NNN.json
python3 scripts/tafsir/build_data.py N --check # the payload matches the markdown
```

`status.py` prints each verse's words beside its floor (`min/med/max`), which is the fastest way
to find the sections that are still thin before the auditor tells you.

Every FAIL must be fixed by changing the writing, not the rule. Warnings must be read; fix the
ones that are real. The code groups mean: `FMT-*` — the file's shape is wrong (a heading that is
the verse's own wording, a missing quote line, bad spacing); `PHR-*` — a phrase of the verse is not
quoted, is quoted out of order, is swallowed by one long quote, or is quoted without evidence
beside it; `MTCH-*` — the file's emphasis, or the words the prose explains, do not match the verse
it quotes (bold used outside the three markers, a headword that neither is the verse's wording nor
means the same thing, Arabic offered as the verse's own wording — while an honest synonym is
adjusted to the verse's own words and recorded as information, `MTCH-SYNONYM`); `REF-*` — a citation or a quote from another
verse is wrong; `WRD-*` — the section is
under its floor; `EVD-*` — a claim has no evidence, a report has no collection, or the verse carries no transmitted
reading at all (`EVD-TAFSIR`); `REF-NONE` — the verse carries no cross-reference to another verse; `REP-*` — the
chapter repeats itself; `STY-*` — the prose is long-winded, formal, carries no analogy, or
announces its own elements (`STY-LABELS`); `SRC-*` — a work outside the eleven is cited, a work of the eleven is
summarised or quoted instead of written from, or the digest for a verse was never built.

When the gate is clean:

1. `python3 scripts/tafsir/build_data.py N` (payload) and confirm `--check` reports no stale file;
2. bump `CACHE_VERSION` in `sw.js`;
3. add the chapter's row to `TAFSIR_WORKLOG.md`;
4. commit on the session branch with the message
   `Tafsir ch N (<Name>): verse-by-verse, written from the eleven works`,
   then push — never to another branch.

### The rules are tested, not assumed

`python3 scripts/tafsir/selftest.py` breaks each rule of §4-§8 on a scratch copy of a written chapter —
a lowercase heading, a mis-quoted verse, a bad citation, a labelled paragraph, a source-by-source
section — and checks that the gate reports the code the rule promises. It prints one row per rule and
exits non-zero if any rule is not enforced. Run it whenever `audit.py` changes.

## 10. Run discipline — fifty verses, mapped once, finished before you pause

The **run of fifty verses** is the unit of work (v7.2); the chapter is the unit of delivery, and a
run may span chapters. What matters is the standing instruction:

> **Map the run, write it, gate it, fix what fails — and do not pause or stop until all fifty
> verses of the run are written and clean (`run.py --check` prints RUN COMPLETE). Do not stop to ask
> for permission or confirmation. Keep going on your own until every verse of the chapter is written
> and the whole chapter passes `audit.py N`.**

Stopping mid-run is only justified when a verse has a genuine problem — a source that cannot be
located, a contradiction between sources that needs a decision — or when the file would be left in a
state that cannot be repaired by the next stretch. Wanting a check-in is not a reason to stop, and
neither is the size of the chapter. A 286-verse sūrah is finished by the same instruction that
finishes a 7-verse one: map the run, write it, gate it, continue to the end of the fifty.

### The run loop

```bash
# once per run of fifty verses (see §2) — the sources are opened once, not per verse.
# The start comes from the author (ask when the instruction is only "continue"); --plan pins the
# fifty, and every later --check/--status/--slice reads that same pinned run.
python3 scripts/tafsir/run.py --plan --start 2:1
python3 scripts/tafsir/run.py --build
python3 scripts/tafsir/run.py --slice 2:1 2:5    # read the map a stretch at a time

# then, for each stretch of the run (the material decides the size of a stretch: verses that carry
# a whole page of law each move a few at a time, short verses move in tens)
python3 scripts/tafsir/batch.py N --from 6 --to 20     # gate just this stretch
python3 scripts/tafsir/batch.py N --ranges 6-20,21-35,36-50   # three stretches at once, in parallel
python3 scripts/tafsir/run.py --status                 # the run's fifty: written, failing, pending

# when the last verse of the run is written:
python3 scripts/tafsir/run.py --check                  # RUN COMPLETE — the fifty are done
python3 scripts/tafsir/audit.py N                      # the whole chapter must pass
python3 scripts/tafsir/build_data.py N
python3 scripts/tafsir/build_data.py N --check
```

`batch.py` runs the same rule set as `audit.py` but reports only the verses that are written, so a
finished stretch is judged on its own. It prints per-verse words against floors, phrase coverage,
whether the verse carries an analogy, and the stretch's sentence-length and reading-ease numbers —
then tells you the next verse to write. Run it, fix every FAIL, and go straight on.

### Spreading the work

The stretches of a run are independent of each other, so they are produced and checked in parallel,
not one at a time:

* **Keep several stretches in flight.** While one range is being gated, the next (and the next) is
  being drafted; independent steps belong in the same pass, not in a queue. The map is already in
  hand — that is what makes the parallel drafting cheap.
* **Gate in parallel.** `batch.py N --ranges A-B,C-D,E-F` audits every range at once (`--jobs`
  controls how many run together) and prints one report per range plus a combined verdict, so a
  whole run's worth of finished stretches can be checked in a single call.
* **Only real dependencies serialise.** A stretch depends on the map and the chapter file, not on
  the stretch before it. Do not wait for one stretch to pass before drafting the next.
* **The run does not stop at a stretch boundary.** Fifty verses are finished before the writer
  pauses: `run.py --check` is the test, and it is run before any pause.

### Rules that hold at every commit

1. **Never leave a half-written verse.** A verse's section is either the scaffold's `TODO` text or
   finished prose. Drafts live in the scratch area (`tmp/work/`), spliced in with `assemble.py`.
2. **Re-read §4 to §8 before each stretch.** The standard is the same for verse 200 as for verse 1.
   Gate drift starts when the writer stops looking at the rule book.
3. **A stretch is done when it is clean.** No FAIL, and every warning read. Do not carry a known
   problem forward into the next stretch; it gets harder to see later.
4. **Commit per stretch** (or per run) on the session branch, with the message
   `Tafsir ch N (<Name>): verses A-B`. The chapter is unfinished at this point: the payload is not
   built, `sw.js` is not bumped, and the worklog row is not added.
5. **The chapter is done** when `audit.py N` passes in full, `status.py N` shows every verse above
   its floor, `build_data.py N --check` reports no stale payload, `sw.js` `CACHE_VERSION` is
   bumped, and `TAFSIR_WORKLOG.md` has the row. Then commit and push, and move to the next chapter
   in the same way.
6. **Progress is visible** through `run.py --status`, `batch.py N --progress` and the worklog's
   "in progress" section; nobody has to ask how far the run has come.

### Choosing how much to write in one pass

**A stretch is as long as the material allows, and the run always reaches fifty.** The stretch is a
unit of the work, not a ration: short verses move in tens, and verses that carry a whole page of law
each (the legal passages of al-Baqarah, the inheritance verses of al-Nisāʾ) are handled a few at a
time — but still several stretches in flight, and always until the fifty are done. Whatever the
size, the loop is the same: read the map, write, gate, fix, continue.

## 11. What this pass deliberately does not do

* It does not mirror any single tafsir. It learns from all of them and writes one clear account.
* It does not transliterate long Arabic passages, quote poetry at length, or reproduce the
  academic apparatus of the sources.
* It does not argue theology, or adjudicate between schools on matters the verse does not settle.
* It does not fill silence. Where a phrase has little material, the prose under it stays honest
  and brief rather than padded — the verse's floor is met from the material the sources do carry:
  its context, its cross-references, its rulings, and the reports attached to it.
* It does not write about words the reader cannot see. The commentary explains the verse as it is
  translated and quoted above the section; the Arabic behind a rendering is named only where it
  serves that explanation, never studied in place of it (`MTCH-WORD`, `MTCH-TERM`).
