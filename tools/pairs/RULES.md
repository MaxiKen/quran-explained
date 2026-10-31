# Phrase-by-phrase authoring rules

These are the rules a phrase explanation is written under. They are binding:
the publishing gate (`assemble.py`) enforces the ones that can be checked by
machine, and the authoring tools in `authoring/` enforce the same rules while
a chapter is being written, so that a mistake is caught at the draft and not
at the gate.

Where a rule is checked, the file and the check are named. Where it cannot
be checked by machine, it says so, because the difference matters: a rule the
tools cannot see is a rule a human still has to keep.

## 1. Which policy a chapter is written under

Two policies are in force. A chapter declares one in `split_policy`, and a
verse may declare its own, so a chapter migrating one verse at a time carries
both policies at once.

| policy | chapters | length | paragraphs |
| --- | --- | --- | --- |
| `sense-v1` | 3 to 43, as first written | 45 to 85 words, fixed | one |
| `tabari-v2` | 1 (al-Fātiḥa), 2 (al-Baqara), and every new chapter | derived from Ṭabarī: floor 40 words, **no ceiling** | as many as the argument needs |

- Chapters migrate one at a time. A chapter that has not migrated keeps the
  gates it was written under, so `assemble.py --check` passes on the whole
  corpus at every commit.
- New chapters are written under `tabari-v2`.
- The rules in section 2 hold under both policies. The rules in sections 3
  and 4 are the length rules, and they differ.

## 2. The rules every explanation follows

### 2.1 It is written for a reader meeting the verse for the first time

- Plain modern English, about the reading level of a good newspaper. Short
  sentences, everyday words, active voice.
- Explain the phrase in its context, including the terms a reader needs.
  Define a technical word the first time it appears.
- Do not merely repeat the translation, and do not pad with general praise
  of the verse. A phrase that says nothing the translation does not already
  say has not earned its place.
- Say "you" only where the verse itself speaks to the reader or to the
  believers. Otherwise stay neutral. Never "I".

### 2.2 One voice

The explanation speaks for itself. It does not name the commentator whose
view it reports, the transmitter whose chain it follows, or the companion
whose report it summarises. Those are the raw material, not the explanation.

- Write "a report from one of the companions", "the exegetes differed", "the
  preferred view", "one of the early scholars held".
- A figure who belongs to the story the verse tells may be named, because the
  name is the content: a prophet, an angel, a king, a man the verse is
  about.
- **Under `tabari-v2` this is checked**: no patronymic (`Ibn Abbas`,
  `Said ibn Jubayr`, `Umar ibn al-Khattab`) and none of the commentators,
  companions or caliphs the material quotes by name. The list lives in
  `style.py` and the gate applies it.
- The `sense-v1` chapters were written before this rule was enforceable and
  still name their sources. They keep their text until they migrate, and
  they are held to the rule when they do.

### 2.3 The shape of the prose

- No Arabic script anywhere. Transliterate when a term needs it: "fatha",
  "tasbih", "tawbah". The Arabic font belongs to the Qur'an.
- No em dash, no en dash, no semicolon. Commas and full stops carry the
  prose. A colon introduces a list.
- A sentence starts with a capital letter.
- Paragraphs are separated by a blank line, and a paragraph never has a line
  break inside it. The reader renders each paragraph separately, so a stray
  break would show.
- Several paragraphs are allowed under `tabari-v2`, and are expected once an
  explanation runs long. Break at the joints of the argument, not to
  decorate.

### 2.4 What it says

- Every substantive point Ṭabarī makes about that piece of the verse appears
  in the explanation: the meaning, the disagreement and its sides, the
  verdict preferred and why, the reading, the grammar, the occasion, the
  context a beginner needs.
- Nothing is added that the material does not support. No outside hadith, no
  verse Ṭabarī does not cite, no dates, numbers or names from memory.
- Where the material carries more than one interpretation, give all of them
  with the reason each side gives, and say which one is preferred if the
  material says so. Never flatten a real difference into one comfortable
  answer.
- Keep the hedge. If the material says "it is said" or "some reported", the
  explanation keeps that.
- Keep historical identifications historical. A reading attributed to a
  reciter or a report traced to a companion belongs to the past it came
  from, and is not a generalisation about people today.

### 2.5 The labels

- A phrase label is an exact, consecutive piece of the reader's English
  translation of the verse. The labels cover every word of the translation
  once, in order, with nothing skipped.
- Under `tabari-v2` the phrase also names the piece of the verse's Arabic it
  explains, in `ar`. The Arabic spans are exact, consecutive pieces of the
  verse's Arabic, covering it once in order. That span is what the source is
  measured against, and it is not published to the reader.

## 3. Length under `sense-v1` (chapters 3 to 43)

- Each phrase explanation is **45 to 85 words** in **one paragraph**. The
  label does not count.
- Split at meaningful internal boundaries when a verse has distinct
  components, even when the whole verse is also a coherent sentence.
- Do not split merely to raise the number of entries. A verse with no
  meaningful internal boundary has one unit.
- Checked by `assemble.py`.

## 4. Length under `tabari-v2` (al-Fātiḥa, al-Baqara, and new chapters)

Length is **derived from the source, not chosen**. An explanation is a
beginner's summary of what Ṭabarī says about that piece of the verse, and it
is as long as what he says deserves.

### 4.1 What is measured

`digest.py` reads the passage and classifies it paragraph by paragraph:

| class | weight | counts as a point about the verse |
| --- | --- | --- |
| meaning | 1.0 | yes |
| judgment | 1.0 | yes |
| disagreement | 1.0 | yes |
| reading (qira'at) | 0.8 | yes |
| grammar | 0.6 | yes |
| context | 0.6 | yes |
| other, chain, apparatus | 0.25 | no |

A chain of transmitters, poetry quoted as linguistic evidence and the
translator's apparatus say who reported a reading or how a manuscript spells
it, not what the verse means. They are measured, and they are not counted as
points.

### 4.2 The rule

- **Target: 15 words for every point Ṭabarī makes.**
- **Floor: 40 words**, or 60% of the target when the target is larger.
- **No ceiling.** A phrase carrying nine opinions gets the room to report
  them. The gate never rejects an explanation for being long.
- **The working curve** a draft is written to is
  `round(1.1 × max(110, round(15 × points)))`: the target plus a tenth,
  because a plain summary nearly always needs a little more room than the
  raw ratio suggests, and never less than 110 words, because a piece of the
  Qur'an is never worth less than that.
- The curve is a **target, not a cap**. The gate enforces the floor only.
  The authoring tools hold a draft to the curve with a working margin of
  `max(12, 12% of the curve)` while it is being written, and
  `authoring/audit.py` reports where a published chapter sits against it.
- Short means the material was not used, and long means padding. Both are
  wrong. Neither is a matter of taste, and neither is a rule of a range: the
  range 45 to 85 words belongs to `sense-v1` alone.

### 4.3 Where a verse is split

- Phrase boundaries follow Ṭabarī's own units. Where he changes topic inside
  a verse, that is a boundary.
- **A split has to be worth making**: a phrase must carry at least
  `digest.MIN_SPLIT_POINTS` (1.5) substantive points of Ṭabarī's own
  discussion to stand alone. He gives `يَوْمِ` in 1:4 seventeen words and no
  discussion of its own, because it belongs to the expression `يَوْمِ
  الدِّينِ` either side of it, so that piece is merged rather than split.
- Where a piece fails that test, join it to the neighbour Ṭabarī discusses
  it with and write one explanation for the joined piece. Do not invent
  content to justify keeping a split.
- The rule is not applied to a verse's only phrase, which has nothing to be
  merged into.
- Checked by `assemble.py`.

### 4.4 What the summary leaves out

- The chains of transmitters. Keep who said what and what was decided, drop
  who heard it from whom.
- Poetry quoted as linguistic evidence, except where the argument needs it.
- The translator's editorial footnotes.
- These are what the measurement discounts, and they are not what a reader is
  owed.

## 5. How a chapter is written

The procedure is the same for every verse. The tools named here are in
`tools/pairs/authoring/`, and each one is a rule made executable.

1. **Read the source.** `python3 tools/pairs/authoring/measure.py SURAH VERSE
   --full` prints what Ṭabarī holds for the verse, paragraph by paragraph and
   classified, with the points each paragraph carries.
2. **Decide the split.** The same command prints every candidate piece of
   the verse with its points and the curve each piece would need. A piece
   marked "merge with a neighbour" carries less of Ṭabarī's own discussion
   than it can stand on, so it is joined to the neighbour it belongs with.
3. **Write each phrase** as a beginner's summary of what Ṭabarī discusses
   for that piece, to the curve, in one voice, under the house style.
4. **Write it in.** `python3 tools/pairs/authoring/author.py DRAFT.json`
   checks every phrase in the batch against the style, the floor, the curve,
   the split rule, the Arabic spans and the English labels, and writes
   nothing at all if any of them fails.
5. **Check the chapter.** `python3 tools/pairs/authoring/audit.py SURAH`
   reports the chapter against the curve and the house style.
6. **Publish and verify.**

```sh
python3 tools/pairs/assemble.py --check    # validate, write nothing
python3 tools/pairs/assemble.py            # publish data/pairs_NNN.json
python3 -m unittest discover -s tools/pairs/tests
python3 tools/pairs/verify.py --confirm-human-review
```

## 6. What the checks cover, and what they cannot

Checked by machine, on every publish:

- the structure of the authored file, and the policy each verse is held to;
- the labels: exact, consecutive pieces of the reader's translation, covering
  the verse once in order;
- the Arabic spans under `tabari-v2`: exact, consecutive, covering the verse
  once in order;
- the house style: no Arabic script, no dash, no semicolon, a capital
  letter, no stray line break, and under `tabari-v2` no named source;
- the length: the floor and the proportional target under `tabari-v2`, the
  45 to 85 word band and the single paragraph under `sense-v1`;
- the split rule: no piece of a verse stands on less of Ṭabarī's own
  discussion than it can carry.

Not checked by machine, and the writer's own responsibility:

- that the explanation is accurate to the material, and adds nothing;
- that the boundaries are the ones a reader would call natural;
- that the English is simple and reads naturally;
- that the summary is fair to a disagreement it reports.

`verify.py --confirm-human-review` records that this reading was done. It is
not a formality: it is the part of the work no script can do.
