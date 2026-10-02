# COMMENTARY PROMPT — Quran Explained, verse-by-verse tafsir

This file is the standing instruction set for continuing the commentary work in this
repository. Read it fully before writing anything. Read `DECISIONS.md` as well; it
records the owner's decisions, and this prompt restates the ones that govern the
craft. When this prompt and any habit disagree, this prompt wins.

## 1. The work

An independent, modern, evidence-rich commentary on the Qurʾān — one file per
chapter: `tafsir/NNN.md` (e.g. `tafsir/002.md` for al-Baqarah). The app renders it
via `data/tafsir_NNN.json`, built with `python3 scripts/tafsir/build_data.py N`.

## 2. The absolute rule: never compose programmatically

The commentary prose is **written, not generated**. Never build verse sections with
builder scripts, template loops, string-assembly helpers, or any program that
produces the commentary text. Programmatic composition flattens the prose into
predictable, repeating structure and is rejected by the owner.

The Python tooling in `scripts/tafsir/` exists for three mechanical jobs only:

- **Gathering** evidence from the corpora (`evidence.py`)
- **Verifying** format and wording (`check.py`, `corpus.py` lookups)
- **Publishing** the app payload (`build_data.py`)

Gathering and verifying may be scripted. **Writing may not.** Every verse section is
drafted as prose, by hand, one at a time, and appended to the chapter file directly.

## 3. Sources — where every claim comes from

- The ten classical corpora in `tafsir-*/NNN.txt` (Ṭabarī, Ibn Kathīr, Qurṭubī,
  Baghawī, Saʿdī, ʿĀlūsī, Uthaymīn, Maʿārif, Tanwīr al-Miqbās from Ibn ʿAbbās, and
  the tenth work) are the only evidence base.
- The app's English Qurʾān text — via `scripts/tafsir/corpus.py` (`ayah_en`) — is
  the only source for verse quote-lines and cross-reference clauses.
- **Nothing is written from memory.** Every report, name, ruling, and quoted clause
  must trace to a corpus paragraph you have actually read this session.
- `tafsir_initial/` is a modern copyrighted study edition: cross-check coverage
  only. Never quote or relay its prose.
- Voice: an independent book. Classical works may be named where they uniquely carry
  a point; early authorities (Ibn ʿAbbās, Mujāhid, Qatādah, al-Ḥasan, al-Suddī,
  al-Rabīʿ, ʿIkrimah, Ibn Isḥāq, …) are named with their reports; ḥadīth
  collections are cited **only when the corpus itself names the collection**. No
  source parades, no isnād dumps.

## 4. Depth — every verse, full depth

- Target **≈800–1,200 words per verse**, 3–5 headings (two headings only for
  genuinely thin material).
- Exhaust the material: reports and their named authorities, occasions of
  revelation, linguistic and grammatical points, legal rulings, creedal points,
  variant readings, disagreements between interpreters and how they are weighed.
- The verse does not determine the size; the available evidence does.

## 5. Style — write like Sūrah 2 vv.1–100

Read at least two finished sections of `tafsir/002.md` (e.g. vv. 2:40 and 2:99)
before drafting, and match that voice:

- Open each verse with your own commentary — what the verse says, what it does,
  where it stands in the sūrah's arc — then weave the reports into the prose.
- Reports are evidence inside an argument, never items in a list. Introduce a
  report, give it, then interpret it. When the interpreters disagree, present the
  disagreement and weigh it, as al-Ṭabarī does.
- Close verses by tying them back into the sūrah's argument.
- **Vary everything**: paragraph openings, paragraph shapes, the order in which
  material is presented, and the number and names of headings. Each verse should
  take its own shape from its own material.
- Banned, because they make the work predictable:
  - opening every paragraph with the same scaffold ("X gives/carries/reads Y its Z");
  - chaining report after report with "and … and … and …" without commentary between;
  - a stock closing formula for every verse ("The verse stands as the sūrah's …");
  - identical heading rhythms from verse to verse.
- Keep the established diction of the book (the sūrah, the house, the standing of
  things) but let sentences breathe — commentary first, report as its proof.

## 6. Format contract (enforced by `check.py`)

- Title: `# Sūrah <name_en> (Chapter N) — Verse-by-Verse Tafsir`
- `## Introduction to the Sūrah` — at least 120 words.
- Per verse: `## Verse N:V`, then **exactly one** quote line `> …` byte-identical
  to the app's wording of that verse, then the body. Never hand-type quote-lines —
  look them up (`ayah_en`) and copy exactly.
- Headings are full lines of the form `**UPPERCASE HEADING**` — plain ASCII
  capitals, no diacritics in the heading itself.
- Cross-references: `(C:V — **“clause”**)` where the clause is an **exact
  substring** of the app's English text of C:V. Look the target verse up before
  quoting it; beware hidden no-break spaces in the app text — if a clause fails,
  choose a clean contiguous substring. Prefer clauses without nested quotation
  marks.
- `check.py` warns on verses under 80 words, with no heading, no cross-reference,
  or no named collection/early authority. Keep warnings rare; format FAILs must be
  zero (except the expected missing-verses FAIL until the chapter is complete).
- Note: `check.py`'s authority patterns are diacritic- and case-sensitive; keep
  authority names in their standard mid-sentence form.

## 7. Workflow per batch of ~10 verses

1. **Gather**: `python3 scripts/tafsir/evidence.py N --part A-B --out tmp/evidence/NNN_A-B.md`
2. **Read** the pack. If it is thin for a verse, extract full paragraphs straight
   from the raw corpora, keyed on `^## N:V` headers.
3. **Look up** each verse's quote-line and every planned cross-reference clause
   against `ayah_en` (lookup only — this is verification, not composition).
4. **Write** the verse sections as prose and append them to `tafsir/NNN.md`,
   following the file's existing conventions (`---` separators, one trailing
   newline). Hand-write; no assembly scripts.
5. **Check**: `python3 scripts/tafsir/check.py N`. Fix every FAIL. After any
   append, re-read the appended text from the file itself — never trust a draft
   over the file's actual content.
6. **Commit and push** each batch to the session branch
   (`arena/01a0f8d2-quran-explained`).

## 8. Corpus hazards in chapter 2 (hard-won)

- `tafsir-al-baghawi/002.txt` verse headers are misaligned from 2:17 onward — do
  not use Baghawī for chapter 2.
- `tafsir-al-qurtubi/002.txt` headers are misaligned for vv.62–65; aligned again
  from 2:67.
- `tafsir-ibn-kathir/002.txt` merges adjacent verse sections (e.g. 72/73, 78/79,
  97–102) — before attributing a report, check the Arabic clause it actually
  discusses. Kathīr also quotes the Qurʾān in an older translation: never lift
  verse clauses from Kathīr; re-fetch them from `ayah_en`.
- `tafsir-al-tabari/002.txt` headers are verified aligned (vv.1–110 checked).
- Corpus section placement can differ from thematic placement (e.g. Ṭabarī keeps
  the prayer-help discussion under 2:44) — follow the corpus placement.
- `tmp/` is scratch: evidence packs may need regenerating; never rely on it
  persisting.

## 9. Environment hazards

- The workspace sometimes resets the local branch to the main-merge tip
  (`60ed373`) between turns. Recover with:
  `git fetch origin && git reset --hard origin/arena/01a0f8d2-quran-explained`
  (worktree files usually survive intact; `tmp/` does not).
- Never delete, rename, or move the repository root or its `.git`.

## 10. Publishing a chapter

When — and only when — every verse of the chapter exists and `check.py` passes with
no FAILs:

1. `python3 scripts/tafsir/build_data.py N` (refuses to publish if any verse lacks
   prose or the verse list ≠ 1..total)
2. Bump `CACHE_VERSION` in `sw.js` (currently `quran-reader-v2.5.54`)
3. Commit and push.

## 11. State of the work (2026-10-02)

- **Published**: Chapter 112; Chapter 1 (full-depth, 7,745 words, v2.5.54).
- **Chapter 2**: vv.1–220 are complete at full depth (vv.1–100 owner-approved;
  vv.101–220 written by hand in the same voice, checked clean).
  **vv.221–286 remain to be written.** Continue from `## Verse 2:221`. Chapter 2
  is not published until all 286 verses are done (then §10).
- Earlier programmatic drafts of vv.101–130 were removed at the owner's direction
  (predictable structure); vv.101 onward must be written, not generated.
- Standing warnings (honest, not to be fixed by invention): a few verses —
  e.g. 2:105, 2:122, 2:123, 2:131, 2:149, 2:156 — carry "no named collection
  and no named early authority" because the corpora truly contain no report
  for them; the mufassirūn defer to earlier passages there.

## 12. Cadence and control

- The owner names the chapters. Do not start any chapter unprompted.
- Once a chapter is named, work continuously: no stopping for approval. Commit and
  push per batch; the owner reads the pushed result and redirects.
