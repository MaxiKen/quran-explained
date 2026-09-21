# Tafsir Global Edit Report

Final state of the global editorial work over all 114 surahs (processed in
order, 001–114). Corpus after the full pipeline: **6,724,747 → 2,638,219
words (−60.8%)**, 6,236 verse sections, every verse carrying real,
verse-specific commentary of a natural length.

The work happened in three waves:

1. **First editorial pass** (deterministic, `scripts/edit_tafsir.py`): removed
   length-quota padding, generator word-chain loop filler (~250K words),
   copy-pasted duplicate sections (~180K words) and ornate vocabulary, while
   programmatically preserving every verse quote, hadith citation,
   cross-reference and story.
2. **Hand-written passes**: Surah 1 (all 7 verses + intro) and Surah 37
   (73 thinnest verse entries) rewritten by hand; a full-corpus fact check
   verified all 10,000+ quoted-translation + reference pairs, all hadith
   ranges and all dated claims, fixing 4 content errors along the way.
3. **Second editorial pass** (maintainer): a corpus-wide rewrite to natural
   length and clean prose (3.68M → 2.72M words at the time of that pass), a
   deepening pass for verses left thin, and small transliteration/reference
   corrections — built on top of the first pass and the fact-check fixes.

## Content-adequacy audit (re-run on the final corpus)

The audit question was whether any verse's commentary is not genuinely
verse-specific and sufficient. Results on the current corpus:

- **Duplication scan** (4-char token Jaccard > 0.60, neighbouring verses):
  **zero surahs above 20% duplicated prose** — the template sections that had
  lived under Surah 16 verses 54–128, Surahs 100–104 (every verse), Surah 21
  and Surah 88 are all gone.
- **Length floor**: median verse entry 426 words; the shortest entry in the
  corpus is 104 words (S70:v39) and reads as dense, verse-specific commentary
  — no verse is padded and none is empty.
- **Fact check** (`scripts/factcheck.py`): 0 broken references, 0 wrong
  references, 0 quote mismatches, 0 top-quote mismatches, 0 hadith-range
  errors across the whole corpus. Numbered hadith citations: 631 unique
  (937 mentions) across Bukhārī, Muslim, Tirmidhī, Nasāʾī, Abū Dāwūd,
  Ibn Mājah and the Muwaṭṭa.
- **Markdown ↔ data round-trip**: `scripts/build_tafsir_json.py` rebuilds the
  committed `data/tafsir_*.json` from `markdown commentry/*.md` with **zero
  file changes** — the two layers are in sync.

## Verification (programmatic, after every step)

- Verse counts unchanged for all 114 surahs; verse quotes preserved.
- Every hadith citation and cross-reference present before an edit is present
  after it (self-references inside removed boilerplate exempted).
- App payload: 15.73 MB for 6,236 verses across 114 files
  (`data/tafsir_XXX.json`).

## Hand-written passes (retained in the final corpus)

- **Surah 1 (al-Fātiḥah)** — intro and all 7 verses fully re-written by hand:
  simple English, natural length, zero repetition, every hadith
  (Bukhārī 4474/756/5736/780, Muslim 395a, the ḥadīth qudsī of the divided
  prayer), every cross-reference and every story preserved.
- **Surah 37 (al-Ṣāffāt)** — the 73 thinnest verse entries (the surah's
  commentary had been almost entirely chain filler) replaced with hand-written
  compact commentaries, preserving the named authorities (Ibn ʿAbbās, Qatādah,
  Ḥasan, Jalālayn, Maududi, Yūsuf ʿAlī) and the ḥadīth of Ḥudhayfah in
  Ṣaḥīḥ Muslim.

## Tools (in `scripts/`)

- `edit_tafsir.py` — the parallel editorial engine (chain detection, dedup,
  content floor, simple-English map, validation).
- `chain_cleanup.py` — the second pass's generator echo-link remover (never
  touches a citation, hadith reference, Qur'an reference or quotation).
- `factcheck.py` — the corpus-wide citation auditor (references, quotes,
  hadith ranges, authority review).
- `build_tafsir_json.py` — builds `data/tafsir_*.json` from the markdown.
- `resync_markdown.py` — rebuilds `markdown commentry/*.md` from the JSON.
- `thin_37_batch*.py` — the hand-written Surah 37 verse entries.
