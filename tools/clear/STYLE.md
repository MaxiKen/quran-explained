# The clear-teaching brief

This is the complete specification for the English entries in the Simple view
(`data/clear_NNN.json`, one file per sūrah). It is the authority. `verify.py`
enforces every numbered rule in it, and a rule that is not in this file is not
a rule.

Read this before writing an entry, and run `verify.py` before committing one.

---

## 1. What this layer is

An English commentary for every verse of the Qur'an, in the app's own modern
English, written for a reader on a phone who has no Arabic and no background in
Islamic scholarship.

It is written **from a reading** of Fī Ẓilāl al-Qurʾān by Sayyid Quṭb
(1906–1966), in the Urdu rendering held in `data/qutb_NNN.json`. It is not a
translation of that work. The mode is **clear teaching**: the entry explains
what the verse says, informed by Quṭb's reading, in prose that a reader with no
training can follow.

Because it is not a translation, it does not claim to carry everything Quṭb
says. Because it is informed by him, it does not invent meanings he does not
support. The space between those two is where every editorial decision lives,
and §9 says how to decide.

---

## 2. Volume: 420 words per verse

**Every verse gets 420 words of prose. This is a rule, not a target, not an
average, and not a suggestion.**

- The band is **400–440 words** (§2.1). Entry length is measured on prose
  only: heading text, bullet markers and emphasis marks are not counted
  (§2.2).
- Every verse of the Qur'an gets its own entry, 6,236 in total, no verse
  skipped and no verse merged into another (§2.3).
- The count is enforced per verse by `verify.py`, which fails the file rather
  than warning (§8).

The number is fixed because the app's reading time, the reader's expectation
and the page's rhythm all depend on every entry being the same size. A verse
that seems to have less to say is a verse that needs more thought, not fewer
words.

### 2.1 The band

| Count | Result |
|---|---|
| 400–440 | pass |
| 380–399 or 441–460 | fail |
| below 380 or above 460 | fail |

`WORD_TARGET = 420`, `WORD_TOLERANCE = 20`. There is no "close enough": an
entry at 399 fails, and the fix is to add a sentence, not to argue.

### 2.2 How the count is taken

`words()` in `verify.py`:

1. Remove heading markers (`## `) but keep the heading's words, since a
   heading is prose the reader reads.
2. Remove list markers (`- `, `1. `) but keep the item's words.
3. Remove emphasis marks (`**`, `*`) and leave the text.
4. Count whitespace-separated tokens.

A bullet list of four items is prose. A heading is prose. Markup is not.

### 2.3 No merging, ever

Each verse has its own entry even where the source discusses a run of verses
together, and even where the source says almost nothing about a verse.

The source contains 21 passages that give under 100 characters per verse. The
shortest, 15:34–35, is 69 characters over two verses:

> اب اس کا حسد ، بغض اور شرارت کا مزاج سامنے آتا ہے۔
> *"Now his envy, spite and mischievous temperament come to the fore."*

That is one sentence about two verses, and each verse still gets 420 words.
The two entries must not duplicate each other (§5). They differ by doing
different work, under §9: one carries what the source says, the other carries
the reader's situation, the connection to the surrounding passage, or a
question the verse raises. This is the hardest case in the corpus and it is
not an excuse to merge.

### 2.4 When a verse genuinely has more to say

It does not get more words. It gets a denser 420. The cap exists so that a
reader can rely on the page. If a verse has three times the material of its
neighbour, the material is selected against §9, not poured out.

---

## 3. Script: Latin only

**No Arabic, Urdu, Persian or other Arabic-block letters anywhere in the
entry.** The single exception is the salawat sign ﷺ (U+FDFA), which may appear
after the Prophet's name.

- Arabic terms are transliterated with the diacritics the source uses, and set
  in italics: *al-hamd*, *Rabb*, *ṣalāh*, *taqwā*, *al-ghayb*, *Ibn ʿAbbās*,
  *al-Bukhārī*.
- The meaning follows the first use in the entry: *al-hamd* (praise), *Rabb*
  (the one who raises a thing to completion).
- Where the source quotes an Arabic verse, use the English, never the Arabic.

The gate is `ARABIC_RE`, the Arabic-block ranges U+0600–06FF, U+0750–077F,
U+08A0–08FF, U+FB50–FDFF and U+FE70–FEFF. Anything caught there is removed or
transliterated. There is no allowance for "just the one word" and no allowance
for a text that is mostly Latin with a stray Arabic token.

---

## 4. Alignment: the app's translation is the spine

Every entry carries the app's own translation of its verse (`ayah_en`, read
from `data/chapter_NNN.js`), word for word, and explains that wording. The
reader must be able to see which English words are being explained.

1. The translation is quoted in the entry, at least once, inside a marked
   span: `==In the Name of Allah—the Most Compassionate== is where the surah
   opens.` The `==` markers separate the translation speaking from the writer
   speaking. They are required because some translations contain an em dash or
   a semicolon of their own, and nested reported speech that quotation marks
   alone cannot delimit. Everything inside `== … ==` is exempt from §6's
   punctuation rules. The span must reproduce `ayah_en` word for word, which
   the gate checks.
2. Each substantive phrase of the translation is taken up and explained. The
   gate splits the translation on dashes and commas and requires every piece
   of two words or more to appear in the entry (§8, `aligned`).
3. The entry never contradicts the translation, and never quietly substitutes
   a different rendering of the verse.
4. The verse's own Arabic is not reproduced. The entry is about the English
   the reader is looking at.

This is what makes the layer *aligned* rather than a free-standing essay: it
is commentary on a specific translation, in that translation's words.

---

## 5. Distinctness: no recycled prose

Each entry is written for its own verse. **No run of eight consecutive words
may appear in two entries of the same sūrah** (`SHINGLE = 8`, overlap
tolerance 5%).

- Do not open two entries with the same sentence shape and only swap a word.
- Do not reuse a paragraph about the sūrah in every verse. Material about the
  sūrah as a whole belongs in the entry for its first verse, or is left out.
- Do not pad a thin verse by restating its neighbour.

The gate compares every pair of siblings on word shingles and fails above 5%
of the shorter entry's shingles. The `==` translation span is excluded from the
comparison, because §4 requires it word for word and two verses the app
translates near-identically (2:134 and 2:141 are the same sentence) would
otherwise fail through no choice of the writer's. The span is still checked
against the translation by §4.

---

## 6. House style

These are the app's rules, and they are enforced.

| Rule | Detail |
|---|---|
| No em dash | `—` is banned in prose. It is permitted **only inside the marked translation span** (§4), which may itself contain one: `==In the Name of Allah—the Most Compassionate==`. |
| No semicolon | `;` is banned in prose. It is permitted only inside the marked translation span, some of which contain one: `==We are definitely with you; we were only mocking.==` |
| No first person singular | "I", "me", "my", "mine" are banned in prose. They are allowed inside a quotation. Say "the reader", "a person", "one". |
| No citation | The entry speaks in one voice. It does not name Quṭb, the tafsīr, Ṭabarī, or "the commentary", and does not say "scholars note" or "the sources say". See §9 for how to handle a view that belongs to him. |
| No generic headings | `Commentary`, `Explanation`, `Notes`, `Overview`, `Summary`, `Details`, `Introduction`, `Conclusion` are banned as headings. A heading says what its section is about. |
| Headings are `##` | Two hashes, sentence case. No `#` and no `###`. |
| No other markup | No links, images, tables, HTML, code blocks, rules or emoji. `**bold**`, `*italic*`, `- ` bullets and `##` headings only. |
| Plain modern English | Short sentences, everyday words, active voice. No *thee*, *thou*, *verily*, *lo*, *unto*, *hath*. No devotional filler ("this beautiful verse", "truly", "indeed", "it is important to note"). |

"Allah" is written as the translation writes it. The Prophet is "the Prophet
ﷺ" or "Muhammad ﷺ". Other prophets take the transliterated name first and the
familiar English in brackets on first mention: "Mūsā (Moses)", "ʿĪsā (Jesus)".

---

## 7. Shape

Every entry has this shape, in this order.

```
## <what the verse does>
prose

## <a heading naming what this section is about>
prose

## <another, if the verse needs it>
prose

## In short
- takeaway
- takeaway
- takeaway
```

- **An opening section**, headed, that gives the reader the verse: what it
  says, who speaks to whom, where it stands, and why it matters. A reader who
  stops after the opening must already have the verse.
- **As many middle sections as the verse needs** to reach 420 words. Each
  heading names its subject and is either a question a reader would ask or the
  part of the verse under discussion. Typical: why it was revealed, the story
  behind it, what the Prophet ﷺ said about it, what the ruling requires, how
  scholars differed, how it connects to its neighbours, the inner meaning.
- **`## In short`**, three to five bullets, the takeaways. Always last. Always
  present.

Sections hold only material that answers their heading. The bullet list is not
a summary that repeats the opening.

---

## 8. The gates

`verify.py` runs every rule above and **fails** on any violation. Nothing here
is a warning. A file is not committed until it reports `all clear`.

```
python3 tools/clear/verify.py                 # the tracked samples
python3 tools/clear/verify.py --dir work/clear
python3 tools/clear/verify.py --file data/clear_002.json
```

| Check | Rule | Failure |
|---|---|---|
| `words` | §2 | count outside 400–440 |
| `script` | §3 | any Arabic-block letter except ﷺ |
| `aligned` | §4 | a phrase of the translation absent from the entry |
| `distinct` | §5 | ≥5% shingle overlap between siblings |
| `shape` | §6, §7 | em dash, semicolon, first person, citation, bad heading, missing `In short`, other markup |
| `coverage` | §2.3 | wrong number of entries for the sūrah's verses |

The gate reads the translation from `data/chapter_NNN.js` so it can never drift
from what the app displays, and it counts words the way §2.2 defines so that
the number is the same one the writer aimed at.

---

## 9. Deciding what goes in

The hard part of this layer is not the English. It is choosing, honestly, what
belongs in a fixed 420 words when the source has more or less to say.

**Order of what fills an entry:**

1. **What the verse says and does.** Always first, always present. The reader
   must be able to understand the verse from it.
2. **What the source says about it.** Quṭb's reading, in plain English,
   including the difficulty he raises and the answer he gives.
3. **What the verse needs to be understood.** The occasion, the context in the
   passage, the cross-reference, the term explained.
4. **The reader's position.** What the verse asks of the person reading it,
   expressed as the verse's own implication rather than as a sermon.

**When the source says less than 420 words' worth:** items 1, 3 and 4 carry the
entry. Do not invent meanings, stories, hadith, dates, numbers or rulings that
the source does not carry. Deepen rather than add: explain the translation's
choice of words more closely, place the verse more precisely, follow the logic
of the passage further.

**When the source says more:** select against the order above. Everything the
reader needs to understand the verse stays. Material that repeats, digresses or
serves the source's own age stays out. Selection is the writer's judgment and
is recorded in the entry's notes where it is contested.

**Where a reading is Quṭb's own:** the house style bans naming the source, so a
view that is distinctly his is stated as a reading a thoughtful reader may hold
("one reading of this verse is…"), not as settled fact, and not as the only
reading where the tradition has others. Never attribute a contested view to the
text itself.

**What is never written:** anything the source does not carry, presented as
though it did. No hadith from memory, no dates, no numbers, no name the source
does not give, no ruling it does not state. The entry's authority is that it
reports a reading faithfully in clear language, not that it adds to it.

---

## 10. Attribution

The payload carries `source: "Clear teaching"` and a `basedOn` line naming Fī
Ẓilāl al-Qurʾān, which the chapter head displays. The entries themselves do not
name the source (§6). The upstream caveat recorded in `ATTRIBUTION.md` — that
the edition was withdrawn from upstream's default distribution after
objections about the author's ʿaqīdah — is stated once per chapter, not per
entry.

---

## 11. Workflow for one sūrah

1. Read the sūrah's source passages in `data/qutb_NNN.json` alongside
   `data/chapter_NNN.js` for the translations.
2. Write one entry per verse, in order, to `work/clear/NNN.json` in the payload
   shape (§12).
3. Run `python3 tools/clear/verify.py --dir work/clear`. Fix every failure.
   The word count will fail first, on almost every entry; that is normal and it
   is the point of the rule.
4. Copy the passing file to `data/clear_NNN.json` and to
   `tools/clear/samples/NNN.json`.
5. Re-run the gate, commit, and confirm in the app that the chapter renders
   left to right with the English entries and that the chapter head names
   clear teaching.

---

## 12. Payload shape

```json
{
  "surah": 1,
  "lang": "en",
  "dir": "ltr",
  "source": "Clear teaching",
  "basedOn": "Fī Ẓilāl al-Qurʾān — Sayyid Quṭb (1906-1966), read from the Urdu rendering",
  "blocks": ["## <entry for verse 1>", "..."],
  "ranges": ["1:1", "1:2", "..."],
  "verses": {"1": 0, "2": 1, "..."}
}
```

`blocks[i]` is the entry for the verse whose index is `i`. `ranges` names the
verse each block covers, and `verses` maps a verse number to its block index.
For this layer the two are always one to one: a block covers exactly the verse
it is named for, which is what §2.3 requires. `lang: "en"` and `dir: "ltr"` are
what make the reader lay the entry out left to right.
