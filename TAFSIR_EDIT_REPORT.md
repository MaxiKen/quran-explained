# Tafsir Global Edit Report

Final state of the global editorial pass over all 114 surahs (processed in
order, 001–114). Corpus: **6,724,747 → 3,655,817 words (−45.6%)**, with every
verse now carrying real, non-repetitive commentary of a natural length.

## What was found and fixed

1. **Targeted word-count padding.** Every verse in the original corpus had
   been generated to hit a length quota (825–2,138 words per verse, median
   ~1,020) regardless of the verse's weight.
2. **Degenerate generator loop filler** (~250K words): several surahs — most
   severely 37, also 88, 89, 87, 54, 86, 49, 81 — contained word-chain
   paragraphs ("Lasting legacies persist. Persisting legacies continue.
   Continuing legacies abide …") produced while chasing the word target. A
   chain-echo detector (short sentence whose content mostly echoes its
   neighbour's, with a two-sided window) removes the loops and keeps the
   substantive glosses, citations and narration.
3. **Copy-pasted duplicate sections** (~180K words): whole sections pasted
   verbatim across dozens of verses of the same surah (e.g. surah 16 carried
   the same five sections under verses 61–80; surah 21 carried one "Abraham's
   trial" essay under 52 verses; surahs 100–104 carried the same three
   methodology essays under every verse). First occurrence kept, later
   duplicates removed; a per-verse content floor guarantees no verse is left
   thin; pure methodology essays were removed except any sentence carrying a
   citation or cross-reference.
4. **Simple-English pass**: recurring ornate vocabulary mapped to plain
   English (eschatological → Last-Day, polemic → argument, utilise → use,
   elucidate → make clear, "It is worth noting that" → removed, etc.).

## Verification (programmatic, after every step)

- Verse counts unchanged for all 114 surahs; verse quotes byte-identical.
- Every hadith citation and cross-reference present in a surah before editing
  is present after editing (self-references inside removed boilerplate
  exempted). Result: **zero losses**.
- `scripts/build_tafsir_json.py` round-trips the markdown sources exactly
  (all 6,236 verses identical).

## Hand-written passes

- **Surah 1 (al-Fātiḥah)** — intro and all 7 verses fully re-written by hand in
  the target style: simple English, natural length (8,363 → 5,037 words), zero
  repetition. Every hadith (Bukhārī 4474/756/5736/780, Muslim 395a, the
  ḥadīth qudsī of the divided prayer), every cross-reference (27:30, 43:87,
  112:1, 17:110, 15:87, 25:1, 21:107, 9:128, 7:156, 20:5, 40:16, 24:25,
  2:281–282, 39:67, 19:93, 39:2, 47:38, 10:9, 6:153, 2:143, 42:52, 11:56,
  4:69, 2:61, 5:77, 10:44, 13:27, 26:20, 93:7, 28:50), and every story (the
  basmalah dispute, the ruqyah of the stung chief, Jaʿfar al-Ṣādiq's three
  grades, the two-callers parable, the ṣirāṭ of the Hereafter, ʿUmar's daily
  audit) is preserved and verified programmatically.
- **Surah 37 (al-Ṣāffāt)** — the 73 thinnest verse entries (the surah's
  commentary had been almost entirely chain filler) were replaced with
  hand-written compact commentaries (~160 words each), preserving the named
  authorities (Ibn ʿAbbās, Qatādah, Ḥasan, Jalālayn, Maududi, Yūsuf ʿAlī) and
  the ḥadīth of Ḥudhayfah in Ṣaḥīḥ Muslim. Surah 37 total: 211,410 → 58,328
  words of genuine content.

## Tools (in `scripts/`)

- `edit_tafsir.py` — the parallel editorial engine (chain detection, dedup,
  content floor, simple-English map, validation). Run: `python3
  scripts/edit_tafsir.py` (optionally pass surah numbers).
- `resync_markdown.py` — rebuilds `markdown commentry/*.md` from the edited
  JSON so the build script round-trips.
- `thin_37_batch*.py` — the hand-written Surah 37 verse entries.
