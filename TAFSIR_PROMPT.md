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
**ten** tafsir works this corpus is written from (`tafsir-*/NNN.txt`; the list is
`corpus.SOURCE_ALLOWLIST` and nothing outside it is a source):

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

One file per chapter: `tafsir/NNN.md`.

The reader is a general Muslim reader with no Arabic and no seminary training. The text must
answer: what does this verse say, what does it mean, what does it ask of me, and what is the
evidence? It must be worth reading twice.

Everything you write about a verse must be traceable to a source that discusses that verse, to
the Qur'an's own text, or to a report the sources carry. No invention, no padding, no
paraphrase of the translation dressed up as commentary.

**Two standing instructions:**

1. **The chapter is generated in batches, and you continue on your own until the end.** Write a
   batch, run the batch gate, fix what fails, start the next batch, and keep going — without
   stopping to ask, and without waiting to be told — until every verse of the chapter is written
   and `audit.py N` passes. A chapter is a marathon, not a lap: the only reasons to pause are a
   source that cannot be located or a contradiction that needs a decision (§10).
2. **All ten are read for every verse before a word of it is written — and at least five are
   named in its prose.** Run the digest for the verse, read what each of the ten says about it
   (Arabic sources included: read them and put the substance into English), then write. The gate
   proves this mechanically: `sources.py` must have pulled the verse's text for all ten
   (`SRC-NOTCHECKED`), and the section must name at least five of the ten, with at least one
   classical and at least one modern (`SRC-SPREAD`, `SRC-FAMILY`). Naming a work outside the ten
   fails (`SRC-BANNED`). Reading is not the same as listing: a work is named where its point is
   used, never as a roll-call.
3. **Spread the work, and write a long list of verses at a time.** The parallel rule exists for
   **speed** and for **scale**: batches do not depend on one another, so several are written and
   gated at once, and a single pass should cover a very long list of verses — **the whole chapter
   where the material allows it**, not a handful at a time. Draft the next range while the last is
   being gated, and audit many finished ranges in one call with `batch.py N --ranges A-B,C-D,E-F`
   (the ranges run in parallel). A chapter is never produced one small batch at a time just because
   that was the earlier habit: cover as much of the chapter in one pass as you can hold at the
   standard, and go straight on to the rest.

## 2. Build the inputs first

```bash
cd /home/user/quran-explained

python3 scripts/tafsir/sources.py N --stats        # where the material is, before reading
python3 scripts/tafsir/sources.py N                # writes tmp/sources/NNN.txt + NNN.json
python3 scripts/tafsir/scaffold.py N               # writes tafsir/NNN.md with byte-exact verse quotes
python3 scripts/tafsir/scaffold.py N --phrases     # the phrase cut each verse is measured against
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

Arabic sources are first-class material here. Read them, translate the substance accurately, and
attribute the point to the work it came from. Do not machine-translate a paragraph and paste it
in; that produces prose no reader wants.

If sources disagree, say so, name the sides, and state what turns on it. Do not smooth a real
disagreement into a single silent voice.

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

Three markers carry the quoting:

| What is quoted | How it is written |
|---|---|
| A phrase of the verse being explained | **bold italics**: `***“the phrase of this verse”***` |
| A clause of any other verse (a cross-reference) | **bold only**: `(C:V — **“the clause”**)` |
| A heading | **UPPERCASE**, no quotes, never the verse's words |

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

### 4.1 Where the length comes from

Length is not padding. It comes from the material this corpus now has:

* the phrase-by-phrase explanation itself, which quotes each phrase and then unpacks its words;
* the stories and occasions of revelation the sources carry for that verse;
* the hadith and athar, told in full, with narrator and collection;
* the rulings and disagreements, with the scholars named;
* the cross-references that let the Qur'an explain the verse;
* one relatable analogy, and the practical lesson the verse asks of the reader;
* the history the sources carry: what was happening when the verse came, who it was spoken to,
  what happened next;
* where the verse meets the present: a modern reading of it (al-Saʿdī, Ibn ʿUthaymīn, Maʿārif
  al-Qurʾān), the working of the natural world a reader can see for himself, and the plain
  application to a household, a wage, a neighbour, a grief.

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

### 4.3 One reading, many witnesses — interweave, never report per source

The ten works are **witnesses inside one reading**, not ten speakers taking turns. A section is an
argument about what the verse says and asks; the sources are the evidence that carries it. Name a
work where its point is used, inside the sentence that needs it — *"the pairing is deliberate, which
is why al-Qurṭubī reads the two names of mercy as a softening of the warning that a Lord carries"* —
and let the next sentence draw the conclusion. What fails is the other shape: a paragraph that opens
with a work's name and paraphrases it, then another paragraph for the next work, and so on. That is a
report on a library, not tafsir, however accurate each paragraph is.

Write so that a reader follows **the verse**, not the bibliography:

* open paragraphs with the point being made, not with an authority's name;
* weigh the sources against each other where they differ — say which reading is stronger and what
  turns on it; where they agree, say so once and move on (two sources saying the same thing are one
  witness, not two);
* keep an argument running across the paragraphs of a section: the phrase, what it means, what the
  grammar does, what follows for the reader;
* use the Qur'an and the report to settle questions, not just to decorate a paragraph;
* analyse — say why a reading is right, what it implies, what changes if it is not.

The gate counts it. In every verse section, `STY-SOURCE-PARADE` fails when three sentences in a row
open with a work's name, when more than 30% of the section's sentences do, or when more than 45% of
its paragraphs do (warns from 18% / 30%); `STY-ANALYSIS-FLOOR` fails a section with fewer than four
sentences that reason about the verse (*because*, *so that*, *which means*, *the point*, *what
follows*) and warns below eight.

If a section is under the floor, the answer is never repetition or vague exhortation. Go back to
the digest and use material you have not used yet — the Arabic sources usually carry more for
that verse than the English ones do.

## 5. The verse's phrases live in the prose — and every one is backed by evidence

The verse is read as a series of meaningful units, and each unit is quoted **inside the
paragraph** that explains it. This is the backbone of the chapter, and it is not the same thing as
the headings. A heading names the paragraph; the phrase is quoted *in* the paragraph, explained
there, and supported there by evidence. Several paragraphs in a verse may carry no phrase at all —
they carry the setting, the story, the ruling, the disagreement, the analogy.

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
in bold only, fails (`PHR-QUOTE-STYLE`); an italic cross-reference quote fails
(`REF-QUOTE-STYLE`). Headings carry no quotes at all, and they are UPPERCASE.

**How to write each phrase.** Take it apart in order: what the words mean, what the grammar does
(a definite article, a word placed first, a pronoun that shifts), what the early authorities said
about it, what it implies for how a person lives. Each phrase should normally carry one to four
paragraphs. Moving through the verse this way is the spine of the section; the headings around it
carry everything else the sources hold for that verse.

**Evidence beside every quote.** A quoted phrase is never left to stand on its own. The paragraph
holding it — or the paragraph straight after it — must carry one of:

* a Qur'an cross-reference, the standard of evidence here: `(C:V — **“clause”**)`;
* a prophetic report with its collection, narrator and grade when the source gives one;
* a named authority — one of the ten above, or a Companion or Successor (Mujāhid, Qatādah, al-Suddī,
  ʿIkrimah) as the ten report him — whose reading is being reported;
* a lexical or grammatical point that changes the meaning.

**What the auditor checks** (`PHR-*`, `FMT-HEADING-*`):

| Check | Rule |
|---|---|
| Headings are UPPERCASE | any lower-case letter in a heading fails `FMT-HEADING-CASE` |
| Heading is a title, not a quote | a heading that is the verse's own phrase fails `FMT-HEADING-QUOTED` |
| This verse's phrases are bold italics | a phrase of the verse quoted plainly, or in bold only, fails `PHR-QUOTE-STYLE` |
| Other references are bold only | an italic cross-reference quote fails `REF-QUOTE-STYLE` |
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
   `ayah_en`.
* A phrase of **this** verse is written `***“the phrase of this verse”***` — bold italics — and must
   be a substring of this verse's `ayah_en` (the gate reports a foreign quote in that style).
* Quote the clause under discussion, not a whole long verse.
* A bare citation without a quote is fine and encouraged: `(2:255)`, `(3:8)`.
* Hadith and athar are quoted inside emphasis with straight quotes: `*"..."*`.
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
5. **Never attribute a point to a source that does not make it.** Before a sentence credits
   anyone — a commentator, a collection, a Companion — find the passage. The digest is the first
   place to look; when the digest is thin, search the raw sources:

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

**The numbers the gate measures** (on prose only; `batch.py` reports them for the batch while the
chapter is still being written, and `audit.py` for the whole chapter at the end):

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
a chapter that leans on formal vocabulary (`STY-DICTION`). Arabic terms are welcome — *raḥmah*,
*ṣirāṭ*, *tawḥīd* — as long as each is explained the first time in the chapter and used naturally
after that.

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
# while the chapter is being written, gate each batch (see §10)
python3 scripts/tafsir/batch.py N --from A --to B   # only the verses written so far
python3 scripts/tafsir/batch.py N --ranges A-B,C-D,E-F   # several batches at once, in parallel
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
beside it; `REF-*` — a citation or a quote from another verse is wrong; `WRD-*` — the section is
under its floor; `EVD-*` — a claim has no evidence or a report has no collection; `REP-*` — the
chapter repeats itself; `STY-*` — the prose is long-winded, formal, carries no analogy, or
announces its own elements (`STY-LABELS`); `SRC-*` — a work outside the ten is cited, fewer than
five of the ten are named, or the digest for a verse was never built.

When the gate is clean:

1. `python3 scripts/tafsir/build_data.py N` (payload) and confirm `--check` reports no stale file;
2. bump `CACHE_VERSION` in `sw.js`;
3. add the chapter's row to `TAFSIR_WORKLOG.md`;
4. commit on the session branch with the message
   `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`,
   then push — never to another branch.

### The rules are tested, not assumed

`python3 scripts/tafsir/selftest.py` breaks each rule of §4-§8 on a scratch copy of a written chapter —
a lowercase heading, a mis-quoted verse, a bad citation, a labelled paragraph, a source-by-source
section — and checks that the gate reports the code the rule promises. It prints one row per rule and
exits non-zero if any rule is not enforced. Run it whenever `audit.py` changes.

## 10. Batch discipline — and keep going until the chapter is finished

A chapter is written one file (`tafsir/NNN.md`), but a long chapter is written in **batches of
verses**. The batch is the unit of work; the chapter is the unit of delivery. What matters is the
standing instruction:

> **Write a batch, gate the batch, fix what fails, then start the next batch immediately.
> Do not stop between batches to ask for permission or confirmation. Keep going on your own
> until every verse of the chapter is written and the whole chapter passes `audit.py N`.**

Stopping mid-chapter is only justified when a verse has a genuine problem — a source that cannot
be located, a contradiction between sources that needs a decision — or when the file would be left
in a state that cannot be repaired by the next batch. Wanting a check-in is not a reason to stop,
and neither is the size of the chapter. A 286-verse sūrah is finished by the same instruction that
finishes a 7-verse one: generate the batch, gate it, continue to the end.

### The batch loop

```bash
# once per chapter (see §2)
python3 scripts/tafsir/sources.py N
python3 scripts/tafsir/scaffold.py N

# then, for each stretch of verses (as long as the chapter allows: a short chapter is one pass,
# a long one is taken in the largest stretches the material supports)
python3 scripts/tafsir/batch.py N --from 6 --to 20     # gate just this batch
python3 scripts/tafsir/batch.py N --ranges 6-20,21-35,36-50   # three batches at once, in parallel
python3 scripts/tafsir/batch.py N --progress           # how far the chapter has come

# when the last verse is written:
python3 scripts/tafsir/audit.py N                      # the whole chapter must pass
python3 scripts/tafsir/build_data.py N
python3 scripts/tafsir/build_data.py N --check
```

`batch.py` runs the same rule set as `audit.py` but reports only the verses that are written, so a
finished batch is judged on its own. It prints per-verse words against floors, phrase coverage,
whether the verse carries an analogy, and the batch's sentence-length and reading-ease numbers —
then tells you the next verse to write. Run it, fix every FAIL, and go straight on to the next
batch.

### Spreading the work

Batches are independent of each other, so they are produced and checked in parallel, not one at a
time:

* **Keep several batches in flight, and make each one long.** While one range is being gated, the
  next (and the next) is being drafted; independent steps belong in the same pass, not in a queue.
  The point of the rule is throughput: a 286-verse chapter should move in tens of verses at a time,
  and a 7-verse chapter should be finished in a single pass.
* **Gate in parallel.** `batch.py N --ranges A-B,C-D,E-F` audits every range at once (`--jobs`
  controls how many run together) and prints one report per range plus a combined verdict, so a
  whole chapter's worth of finished batches can be checked in a single call.
* **Only real dependencies serialise.** A batch depends on the scaffold and the source digest, not
  on the batch before it. Do not wait for one batch to pass before drafting the next.

### Rules that hold at every commit

1. **Never leave a half-written verse.** A verse's section is either the scaffold's `TODO` text or
   finished prose. Drafts live in the scratch area, not in the chapter file.
2. **Re-read §4 to §8 before each batch.** The standard is the same for verse 200 as for verse 1.
   Batch gates drift when the writer stops looking at the rule book.
3. **A batch is done when it is clean.** No FAIL, and every warning read. Do not carry a known
   problem forward into the next batch; it gets harder to see later.
4. **Commit per batch** (or per two batches) on the session branch, with the message
   `Tafsir ch N (<Name>): verses A-B`. The chapter is unfinished at this point: the payload is not
   built, `sw.js` is not bumped, and the worklog row is not added.
5. **The chapter is done** when `audit.py N` passes in full, `status.py N` shows every verse above
   its floor, `build_data.py N --check` reports no stale payload, `sw.js` `CACHE_VERSION` is
   bumped, and `TAFSIR_WORKLOG.md` has the row. Then commit and push, and move to the next chapter
   in the same way.
6. **Progress is visible between batches** through `batch.py N --progress` and the worklog's "in
   progress" section; nobody has to ask how far the chapter has come.

### Choosing how much to write in one pass

**As much as the chapter allows, and the whole chapter wherever possible.** The range is a unit of
work, not a ration: a short chapter of six or seven verses is written in one pass, and a long
chapter is taken in the largest stretches the material supports — several tens of verses at once,
or the rest of the chapter, when the verses are short and the digest is in hand. Verses that carry a
whole page of law each (the legal passages of al-Baqarah, the inheritance verses of al-Nisāʾ) are
handled in smaller groups, but still several at a time and in parallel with the next group. Whatever
the size, the loop is the same: write, gate, fix, continue — and keep several groups in flight.

## 11. What this pass deliberately does not do

* It does not mirror any single tafsir. It learns from all of them and writes one clear account.
* It does not transliterate long Arabic passages, quote poetry at length, or reproduce the
  academic apparatus of the sources.
* It does not argue theology, or adjudicate between schools on matters the verse does not settle.
* It does not fill silence. Where a phrase has little material, the prose under it stays honest
  and brief rather than padded — the verse's floor is met from the material the sources do carry:
  its context, its cross-references, its rulings, and the reports attached to it.
