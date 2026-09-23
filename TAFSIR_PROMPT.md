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
python3 scripts/tafsir/scaffold.py N               # writes tafsir/NNN.md, quotes already exact
```

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
fixed. `scaffold.py N` writes this skeleton with the verse quotes already byte-exact.

```markdown
# Sūrah <Name> (Chapter N) — Verse-by-Verse Tafsir

## Introduction to the Sūrah

Introduction prose in plain paragraphs, 200–900 words, no headings, no separators.

---

## Verse N:1

> <the canonical translation, exactly as it stands in data/chapter_NNN.js>

**A Heading That Says Something**

Prose under the heading.

**Another Heading That Says Something**

More prose.

---

## Verse N:2
...
```

Rules the auditor enforces:

1. **Title line** exactly `# Sūrah <name_en> (Chapter N) — Verse-by-Verse Tafsir`.
2. **Introduction** under `## Introduction to the Sūrah` on line 3: 200–900 words, plain
   paragraphs, no bold headings inside it, one `---` after it.
3. **Every verse** appears once, ascending, as `## Verse N:V`, and every verse of the chapter
   must be present. No skipped verses, no combined verses, no invented verse numbers.
4. **Verse quote**: one line, starting `> `, byte-identical to that verse's `ayah_en` in
   `data/chapter_NNN.js`, with one blank line above and below.
5. **At least two `**bold headings**` per verse** (soft maximum six), each alone on its line
   with blank lines around it, each followed by prose. No generic headings (`Commentary`,
   `Explanation`, `Summary`, `Note`); say what the paragraph says.
6. **Length follows substance**: 150–650 words of body per verse. Simple verses end near the
   floor. A verse the sources discuss for pages may run to the soft ceiling; never past it, and
   never padded to reach it.
7. **One `---`** between sections. No trailing separator after the last verse.
8. **Hygiene**: no tabs, no trailing spaces, no double blank lines, single newline at the end.
9. **No placeholder** text (`TODO`, `TBD`) may survive into the file.

## 5. Quoting law

* Qur'an wordings come **only** from `data/chapter_NNN.js`. Never from a tafsir's paraphrase,
   never from memory, never retyped if you can copy it.
* A Qur'an quotation is written `(C:V — *“the clause under discussion”*)` with an em dash and
   curly quotes, and the clause must be a verbatim substring of that verse's `ayah_en`.
* Quote the clause under discussion, not a whole long verse.
* A bare citation without a quote is fine and encouraged: `(2:255)`, `(3:8)`.
* Hadith and athar are quoted inside emphasis with straight quotes: `*"..."*`.
* Never re-quote a verse already quoted in the same section; cite it.
* Every citation must point to a real verse: `(2:300)` fails the gate.

## 6. Attribution law — non-negotiable

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

## 7. Style law

Write plain English. Short sentences. Ordinary words. Explain an Arabic term the first time it
appears in the chapter, then use it freely.

Do not write:

* process or meta prose ("this section", "we will now examine", "as mentioned above", "in
  conclusion") — the reader wants the verse, not the writing process;
* filler openers and closers;
* machine clichés ("rich tapestry", "stands as a testament to", "navigate the complexities",
  "underscores the importance");
* the same sentence twice anywhere in the chapter (the auditor compares every sentence), or two
  verse sections built from the same phrasing;
* generic exhortation that would fit any verse — if a paragraph could be pasted under another
  verse unchanged, it is not commentary.

Do write:

* verse-specific detail: the word being explained, the person in the story, the ruling at stake;
* transitions that carry the reader from one paragraph to the next;
* the "so what" sentence when a verse has a practical demand on the reader — once, briefly, in
  plain words.

## 8. Self-check before calling a chapter done

```bash
python3 scripts/tafsir/audit.py N              # must end in RESULT: PASS
python3 scripts/tafsir/build_data.py N         # writes data/tafsir_NNN.json
python3 scripts/tafsir/status.py N             # words per verse, gate verdict
```

Every FAIL must be fixed by changing the writing, not the rule. Warnings must be read; fix the
ones that are real. `FMT-*` and `REF-*` failures mean the file is malformed or a quote is wrong;
`WRD-*`, `EVD-*`, `REP-*` failures mean the writing is thin, unevidenced or repetitive.

When the gate is clean:

1. `python3 scripts/tafsir/build_data.py N` (payload) and confirm `--check` reports no stale file;
2. bump `CACHE_VERSION` in `sw.js`;
3. add the chapter's row to `TAFSIR_WORKLOG.md`;
4. commit on the session branch with the message
   `Tafsir ch N (<Name>): verse-by-verse from all <k> sources`,
   then push — never to another branch.

## 9. Batch discipline for long chapters

One file per chapter, but a chapter may be written in batches of verses (for example 50 verses at
a time). A batch is not finished until its verses pass the gate *and* the file's structure is
intact — a half-written chapter is a failing chapter, so keep the file complete at every commit
or keep batches on a scratch copy and splice them in one by one, auditing after each splice.

## 10. What this pass deliberately does not do

* It does not mirror any single tafsir. It learns from all of them and writes one clear account.
* It does not transliterate long Arabic passages, quote poetry at length, or reproduce the
  academic apparatus of the sources.
* It does not argue theology, or adjudicate between schools on matters the verse does not settle.
* It does not fill silence. Where the sources have little, the section is short and says what is
  known.
