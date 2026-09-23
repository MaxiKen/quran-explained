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
28 tafsir works in this repository (`tafsir-*/NNN.txt`, plus the study-Quran draft in
`tafsir_initial/NNN.md`). One file per chapter: `tafsir/NNN.md`.

The reader is a general Muslim reader with no Arabic and no seminary training. The text must
answer: what does this verse say, what does it mean, what does it ask of me, and what is the
evidence? It must be worth reading twice.

Everything you write about a verse must be traceable to a source that discusses that verse, to
the Qur'an's own text, or to a report the sources carry. No invention, no padding, no
paraphrase of the translation dressed up as commentary.

## 2. Build the inputs first

```bash
cd /home/user/quran-explained

python3 scripts/tafsir/sources.py N --stats        # where the material is, before reading
python3 scripts/tafsir/sources.py N                # writes tmp/sources/NNN.txt + NNN.json
python3 scripts/tafsir/scaffold.py N               # writes tafsir/NNN.md: exact quotes + phrase headings
```

The scaffold hands you two free wins. The verse quote is copied byte-for-byte from
`data/chapter_NNN.js`, so it cannot fail the verbatim check. And the verse is already cut into
phrase headings by `corpus.split_phrases`, in verse order, covering every word — so the
phrase-coverage rule passes from the first line you write. Re-cut a proposal when you can see a
better unit, and check your cut with `python3 scripts/tafsir/scaffold.py N --stdout | head -40`.

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
| A named classical authority's ruling or reading (al-Ṭabarī, al-Qurṭubī, Ibn Kathīr, al-Shāfiʿī, Abū Ḥanīfah, Mālik, al-Zamakhsharī, al-Rāzī) | the reader can follow the disagreement |
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
fixed. `scaffold.py N` writes this skeleton with the verse quotes *and* the phrase headings
already cut for you.

```markdown
# Sūrah <Name> (Chapter N) — Verse-by-Verse Tafsir

## Introduction to the Sūrah

Introduction prose in plain paragraphs, 250–1,500 words, no headings, no separators.

---

## Verse N:1

> <the canonical translation, exactly as it stands in data/chapter_NNN.js>

**“first phrase of the verse”**

Prose explaining that phrase.

**“second phrase of the verse”**

Prose explaining that phrase.

---

## Verse N:2
...
```

Rules the auditor enforces:

1. **Title line** exactly `# Sūrah <name_en> (Chapter N) — Verse-by-Verse Tafsir`.
2. **Introduction** under `## Introduction to the Sūrah` on line 3: 250–1,500 words, plain
   paragraphs, no bold headings inside it, one `---` after it.
3. **Every verse** appears once, ascending, as `## Verse N:V`, and every verse of the chapter
   must be present. No skipped verses, no combined verses, no invented verse numbers.
4. **Verse quote**: one line, starting `> `, byte-identical to that verse's `ayah_en` in
   `data/chapter_NNN.js`, with one blank line above and below.
5. **Every phrase of the verse is quoted and explained** (see §5). Phrase headings are written
   `**“phrase”**` with curly quotes, alone on their line, blank line before and after, and one
   after another in verse order. Descriptive `**bold headings**` may be added inside a phrase's
   block for a story, a ruling or a list; they must not be generic (`Commentary`, `Explanation`,
   `Summary`, `Note`) and must each be followed by prose.
6. **Length follows substance, and the floor is high.** Every verse carries at least **500
   words**, and the floor rises with the verse: `max(500, 6 × the verse's own word count)`, up to
   3,000. A ninety-word verse therefore needs 540+ words; a two-hundred-word verse needs 1,200+.
   The soft ceiling is 4,000 words — above that, check for padding.
7. **One `---`** between sections. No trailing separator after the last verse.
8. **Hygiene**: no tabs, no trailing spaces, no double blank lines, single newline at the end.
9. **No placeholder** text (`TODO`, `TBD`) may survive into the file.

### 4.1 Where the length comes from

Length is not padding. It comes from the material this corpus now has:

* the phrase-by-phrase explanation itself, which quotes each phrase and then unpacks its words;
* the stories and occasions of revelation the sources carry for that verse;
* the hadith and athar, told in full, with narrator and collection;
* the rulings and disagreements, with the scholars named;
* the cross-references that let the Qur'an explain the verse;
* one relatable analogy, and the practical lesson the verse asks of the reader.

If a section is under the floor, the answer is never repetition or vague exhortation. Go back to
the digest and use material you have not used yet — the Arabic sources usually carry more for
that verse than the English ones do.

## 5. Splitting a verse into phrases, and quoting each one

Every verse is read as a series of meaningful units, and each unit is quoted as a heading and then
explained. This is the backbone of the chapter format.

**How to cut a verse.** `scaffold.py N` proposes the cut with `corpus.split_phrases`, which breaks
at strong punctuation (— ; : ? !) and before conjunctions, keeps every word of the verse, and
never leaves a fragment. Re-cut the proposal whenever you can see a more meaningful unit, as long
as two things stay true:

* the phrases run in verse order and together account for the whole verse;
* each heading is the verse's own wording, copied, not paraphrased.

Good cuts for `1:1`: `“In the Name of Allah”` and `“the Most Compassionate, Most Merciful”`.
Good cuts for `2:255` include `“Allah! There is no god ˹worthy of worship˺ except Him, the
Ever-Living, All-Sustaining.”` and `“Who could possibly intercede with Him without His
permission?”`. A cut that separates a phrase from the word it leans on ("Neither drowsiness" /
"nor sleep overtakes Him") is a bad cut; merge it back.

**How to write each phrase.** Take the phrase apart in order: what the words mean, what the
grammar does (a definite article, a word placed first, a pronoun that shifts), what the early
authorities said about it, what it implies for how a person lives. Then move to the next phrase.
Each phrase should normally carry one to four paragraphs, and a phrase heading without real prose
under it fails the gate.

**What the auditor checks** (`FMT-PHRASE-*`, `REF-PHRASE*`):

| Check | Rule |
|---|---|
| Phrase headings exist | at least one, or `FMT-PHRASE-NONE` |
| Every heading is a phrase of the verse | compared with the stored translation, punctuation and the ˹…˺ brackets ignored; otherwise `REF-PHRASE` |
| Headings stand in verse order | otherwise `REF-PHRASE-ORDER` |
| The headings cover the verse | at least 90% of the verse's words, or `FMT-PHRASE-COVERAGE` |
| No phrase is skipped over | any unquoted run longer than 8 words fails (`FMT-PHRASE-GAP`) |
| Nothing is dropped at the edges | the first or last 3 words unquoted fails (`FMT-PHRASE-EDGE`) |

## 6. Quoting law

* Qur'an wordings come **only** from `data/chapter_NNN.js`. Never from a tafsir's paraphrase,
   never from memory, never retyped if you can copy it.
* A Qur'an quotation is written `(C:V — *“the clause under discussion”*)` with an em dash and
   curly quotes, and the clause must be a verbatim substring of that verse's `ayah_en`.
* Quote the clause under discussion, not a whole long verse.
* A bare citation without a quote is fine and encouraged: `(2:255)`, `(3:8)`.
* Hadith and athar are quoted inside emphasis with straight quotes: `*"..."*`.
* Never re-quote a verse already quoted in the same section; cite it.
* Every citation must point to a real verse: `(2:300)` fails the gate.

## 7. Attribution law — non-negotiable

1. **Never invent a hadith number.** Give collection and narrator as the source gives them
   (`Ṣaḥīḥ al-Bukhārī 756`, `Muslim records Abū Hurayrah saying…`). If the source carries no
   number, the commentary carries no number.
2. **Grade only what the source grades** (`At-Tirmidhī said ḥasan gharīb`, `a report whose chain
   al-Ṭabarī grades weak`).
3. **Never promote a witness account, a Companion's ruling, or a commentator's gloss to a
   prophetic saying.** Speaker → speaker: Companion → Companion, scholar → scholar, Prophet ﷺ →
   Prophet ﷺ.
4. **A prophetic saying always names its collection** in the same section. If you cannot say
   where it comes from, leave it out.
5. **Never attribute a point to a source that does not make it.**

## 8. Style law — plain words, short sentences, one good analogy

Write for a reader who has no Arabic and no seminary training: a shopkeeper, a student, a nurse
reading on a phone between tasks. Every sentence should be understandable on one reading.

**The numbers the gate measures** (chapter-wide, on prose only):

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
python3 scripts/tafsir/audit.py N              # must end in RESULT: PASS
python3 scripts/tafsir/status.py N             # words per verse against its floor, gate verdict
python3 scripts/tafsir/build_data.py N         # writes data/tafsir_NNN.json
python3 scripts/tafsir/build_data.py N --check # the payload matches the markdown
```

`status.py` prints each verse's words beside its floor (`min/med/max`), which is the fastest way
to find the sections that are still thin before the auditor tells you.

Every FAIL must be fixed by changing the writing, not the rule. Warnings must be read; fix the
ones that are real. The code groups mean: `FMT-*` and `REF-*` — the file is malformed, a quote is
wrong, or a phrase of the verse is missing; `WRD-*` — the section is under its floor; `EVD-*` — a
claim has no evidence or a report has no collection; `REP-*` — the chapter repeats itself;
`STY-*` — the prose is long-winded, formal, or carries no analogy.

When the gate is clean:

1. `python3 scripts/tafsir/build_data.py N` (payload) and confirm `--check` reports no stale file;
2. bump `CACHE_VERSION` in `sw.js`;
3. add the chapter's row to `TAFSIR_WORKLOG.md`;
4. commit on the session branch with the message
   `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`,
   then push — never to another branch.

## 10. Batch discipline for long chapters

One file per chapter, but a chapter may be written in batches of verses (for example 50 verses at
a time). A batch is not finished until its verses pass the gate *and* the file's structure is
intact — a half-written chapter is a failing chapter, so keep the file complete at every commit
or keep batches on a scratch copy and splice them in one by one, auditing after each splice.

## 11. What this pass deliberately does not do

* It does not mirror any single tafsir. It learns from all of them and writes one clear account.
* It does not transliterate long Arabic passages, quote poetry at length, or reproduce the
  academic apparatus of the sources.
* It does not argue theology, or adjudicate between schools on matters the verse does not settle.
* It does not fill silence. Where a phrase has little material, the prose under it stays honest
  and brief rather than padded — the verse's floor is met from the material the sources do carry:
  its context, its cross-references, its rulings, and the reports attached to it.
