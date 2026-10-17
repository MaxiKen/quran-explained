## Chapter-number sessions (current policy)

Provide a chapter number such as `18` to generate/resume that chapter. Chapters
can be generated out of order in separate sessions. Use
`status.py --next --surah 18`, not global discovery, to select its jobs.
`finish.py` runs work gates and publishes per job; full published-chapter
verification is run **once, only after all verses and the intro are complete**.
Store progress, the verification receipt and an exact created/updated/deleted
file manifest in `tools/guidance/chapters/SSS.md`, not shared progress files.
See [CHAPTER_RUN.md](CHAPTER_RUN.md) and [CONTINUE_PROMPT.md](CONTINUE_PROMPT.md)
for isolated generation and selective merging without overwriting newer main.

# Guidance pipeline — plain-English commentary for every verse

`tools/guidance/` turns the eight tafsīr sources in `data/tafsir_NNN.json`
into one original, simple-English commentary per verse (plus one
introduction per surah), published as `data/guidance_NNN.json` and shown in
the app under the label **Plain-English commentary** above the tafsīr.

> **The corpus changed on 2026-10-17.** The eight sources are no longer in
> `data/tafsir_NNN.json`: the reader's tafsīr is now Tafsīr al-Ṭabarī in
> English with the Arabic original underneath it, imported by `tools/tabari/`.
> The commentary already published was written from the eight and is unchanged,
> but this pipeline cannot be re-run against the current payload — `load_tafsir`
> stops with an explanation instead of writing a commentary from a corpus the
> prompts do not describe. To run it again, give it a copy of the eight-source
> payload. The tests that read that corpus skip themselves with that same
> reason (`tests/test_pipeline.py`), so the suite stays green and says why.

Everything is plain Python 3.11 with no third-party packages. The model
providers are called over HTTPS with `urllib`.

```
pack  ->  generate  ->  verify  ->  audit (optional)  ->  assemble  ->  verify --source data
```

| step | script | what it does |
|---|---|---|
| pack | `pack.py` | groups each surah's verses into jobs (≤ 8 verses, ≤ 60 K chars of material, never splitting a source block's range when it can be avoided) and balances jobs into shards. `--estimate` prints token and cost estimates. |
| generate | `generate.py` | sends one request per job (system prompt = `prompts/system.md` + the exemplars; user prompt = `prompts/verse_job.md` or `intro_job.md` filled with the verses, the app's own translation and the material). Parses the `<<<VERSE S:N>>> … <<<END>>>` entries, retries truncated output, falls back to per-verse jobs, writes `work/out/NNN/<job>.json`. |
| ingest | `ingest.py` | stores an output produced *outside* `generate.py` (pasted from a chat, written by hand, returned by a batch API) as the result of a job, so it goes through the same gates: `ingest.py --job 001-002-005 --file work/raw/001-002-005.md --model "…"`. Refuses outputs that do not carry every verse of the job. |
| verify | `verify.py` | deterministic gates (below). Writes `work/reports/NNN.json`. Exit code 1 on `fail`, or on `flag` with `--strict`. |
| audit | `audit.py` | a second model pass: lists every point in the material and checks it is covered, lists unsupported claims and style violations, then asks the writer model to repair. A repair is kept only if the gates do not get worse. Default: only `flag`/`fail` entries; `--all` audits everything. |
| assemble | `assemble.py` | merges the job outputs into `data/guidance_NNN.json` (minified, one line). `fail` entries are left out so the app falls back to the sources for that verse. |
| status | `status.py` | progress derived from `data/` alone (so it survives a sandbox reset). `--next` prints the first unpublished job in the working order and packs its surah if needed; `--material JOB --part k` prints the job's material in ≤ 12 K-char parts (tool output truncates around 30 K); `--export-raw N` rebuilds `work/raw/NNN-*.md` from the published payload. |
| resume | `resume.sh` | start-of-session script: realigns a rewound checkout with `origin`, merges the pipeline branch in if `HANDOFF.md` is missing, runs the tests, prints the progress table and the next job. |
| digest | `digest.py` | a job's material prepared for complete, fast reading: a per-verse checklist of what the coverage gate will look for, the translations to quote, then the material with Arabic and honorifics removed, referenced verse quotations collapsed to `[Q S:N …]` (`--quote S:N` prints the app's translation) and repeated paragraphs collapsed. |
| finish | `finish.py` | one command per job: ingest → gates (compact report) → assemble → commit → push → next job in the same chapter. Stops at any FAIL. |

## Running

Locally (needs the provider key in the environment):

```bash
python3 tools/guidance/pack.py --surahs 2 --shards 1
ANTHROPIC_API_KEY=… python3 tools/guidance/generate.py --surahs 2 --provider anthropic --concurrency 8
python3 tools/guidance/verify.py --source work --surahs 2
ANTHROPIC_API_KEY=… python3 tools/guidance/audit.py --surahs 2 --provider anthropic
python3 tools/guidance/assemble.py --surahs 2

# Only once, after the introduction and ALL verses are complete:
python3 tools/guidance/verify.py --source data --surahs 2
```

The legacy Actions workflow is not the default for isolated chapter sessions.
Do not use a partial/limited/sharded generation run to trigger full verification.
It must first support the complete-chapter guard, single final-check receipt and
chapter-local manifest described in CHAPTER_RUN.md.

On GitHub: **Actions → Guidance (plain-English commentary) → Run workflow**
with the surah selection, provider, model, QA tier and shard count. The
workflow packs, generates in parallel shards, verifies, audits, assembles,
runs the tests and commits the `data/guidance_*.json` files to the branch it
was run on. Run it per chapter group (for example `1-10`, `11-20`, …, or
`all` with 20 shards) to get one commit per group.

Offline smoke test of the whole chain (mock provider, no API calls):

```bash
python3 tools/guidance/generate.py --surahs 112 --dry-run
python3 -m unittest discover -s tools/guidance/tests
```

Writing without an API (what was done for Surah 1): `generate.py --show JOB`
prints the exact prompt, the entries are written by hand (or in a chat) into
`work/raw/JOB.md` with the same `<<<VERSE S:N>>>` markers, and `ingest.py`
files them as the job's result; `verify.py --source work`, `assemble.py` and
`verify.py --source data` then run unchanged. `work/raw/` is tracked in git
(the rest of `work/` is scratch), so the hand-written entries survive resets.

Continuing in a new session: `HANDOFF.md` is the complete operating manual
(state, final decisions, the authoring loop, gate cheat-sheet, sandbox quirks,
progress log); `CONTINUE_PROMPT.md` is the message to paste into a new session;
use the chapter-scoped startup in `CHAPTER_RUN.md` rather than the legacy
global `resume.sh` helper.

Useful switches: `generate.py --show 112-001-004` prints the exact prompt a
job receives; `--limit 3` runs three jobs; `--only ID,ID` runs specific jobs;
`--skip-published` skips verses already in `data/`; `--force` re-runs jobs
that already have output.

## What an entry looks like

Every verse gets its own self-contained entry in Markdown (subset:
`###` headings, `**bold**`, `- ` bullets, `1. ` lists, `> ` quotes):

1. an opening that says what the verse is saying and quotes the app's own
   translation (`ayah_en`);
2. `### Phrase by phrase` – the verse's phrases in bold, each explained;
3. adaptive `###` sections with specific headings drawn from the material
   (reasons for revelation, hadiths, differences of opinion, the inner
   reading, lessons, links to other verses);
4. `### In short` – two to five bullets.

Rules the writer follows (see `prompts/system.md` for the full guide):

- **Everything in the material, nothing outside it.** Every point, report,
  opinion and story in the eight sources is carried over; nothing is added
  from outside. Shared range material (a block covering 55:1-13, say) is
  distributed across the verses it belongs to, so no two entries repeat
  each other. Material that belongs to the whole surah goes into the
  introduction.
- **Anonymous sources.** The eight works and their authors are never named;
  the text speaks in one integrated voice. Companions, early scholars,
  hadith collectors and gradings are kept exactly as the material gives
  them. Isnād chains are dropped.
- **Plain modern English**, short sentences, no em dashes or semicolons
  outside quotations, no Arabic script (only transliteration, with the
  diacritics the sources use; ﷺ after the Prophet's name), "Allah",
  prophets as "Mūsā (Moses)".
- **Original wording.** No run of twelve or more words copied from a source
  outside an explicit quotation.
- **Length is proportional to the material about the verse**: no bands, no
  cap, and no padding. Three sources (Tanwīr, Jalālayn, Mukhtaṣar) gloss
  every verse separately; Ibn Kathīr, Maʿārif and Tazkirul write about
  passages, so a passage block is attributed to its verses by where it quotes
  each verse in Arabic (`common.verse_shares`; what cannot be located is
  split evenly, a refrain block counts in full for each verse it lists, and
  the sūrah introduction at the top of Ibn Kathīr's opening block is kept
  apart). The per-verse figure is shown to the writer as "Material about
  this verse: about N words" and is the yardstick for the length gates: an
  entry much shorter than 0.25 × its material, or longer than
  200 + 1.5 × its material, is flagged for audit. Across the Qurʾān the
  median verse has ≈560 words of material about it; a quarter have under
  300 (entries of two or three short paragraphs) and a tenth have over 1,850.

The three hand-written exemplars in `prompts/exemplars/` (1:2 – a long
verse; 112:1 – one verse of a four-verse job with shared material; 55:13 –
a refrain) are appended to the system prompt and are the calibration target.

## Gates (`verify.py`)

`fail` (entry is not published):

- structure: missing opening, `### Phrase by phrase`, `### In short`; empty
  section; stray `<<<` markers
- Arabic script; a named tafsīr work or author; digest voice ("the sources
  say", "the commentators")
- opening does not quote at least five consecutive words of the app's
  translation
- names a hadith collector, grading or cross-reference that is not in the
  material
- verbatim run of 24+ words from the material outside a quotation
- coverage below 50 % when the material has at least eight anchors

`flag` (published, listed for audit): coverage below 85 %, em dash or
semicolon outside quotes, a generic heading, verbatim run of 12–23 words,
average sentence over 25 words, Flesch–Kincaid grade over 12, length ratio
under 0.25 of the material, duplication with a sibling entry over 10 %, no
middle sections although the material is long, author-voice phrases.

"Anchors" are the proper names, numbers, cross-references and technical
terms found in the material; coverage is the share of them that appear in
the job's entries (plus the introduction, for the blocks that open a
surah). Spellings are folded before matching (Hurayrah/Hurairah,
ʿAbd Allāh/Abdullah, Mūsā/Moses, Makkī/Makkan …).

## Layout

```
tools/guidance/
  common.py        paths, loaders, cleaning, folding, job building
  pack.py          jobs + shards + estimates
  generate.py      prompt rendering, provider calls, parsing, retries
  ingest.py        store an externally produced output as a job result
  verify.py        gates and reports
  audit.py         LLM audit + repair
  assemble.py      data/guidance_NNN.json writer
  status.py        progress from data/, next job, material in readable parts, raw export
  digest.py        checklist + cleaned material per job, --quote S:N
  finish.py        ingest, gates, assemble, commit, push, next job in one call
  resume.sh        start-of-session: realign git, tests, status, next job
  HANDOFF.md       operating manual for continuing the work in a new session
  CONTINUE_PROMPT.md  the prompt to paste into a new session
  providers.py     Anthropic / OpenAI / Gemini / mock, urllib only
  mock_writer.py   placeholder writer for dry runs
  prompts/         system.md, verse_job.md, intro_job.md, audit.md, repair.md, exemplars/
  tests/           python3 -m unittest discover -s tools/guidance/tests
work/              scratch (gitignored): jobs/, shards.json, out/, reports/
work/raw/          tracked: the hand-written / pasted entries, one file per job
```

## Published payload

```json
{"surah":112,"lang":"en","dir":"ltr","title":"Al-Ikhlas","label":"Plain-English commentary",
 "generated":{"date":"2026-10-14","model":"…","pipeline":"guidance/1"},
 "intro":"markdown…",
 "verses":{"1":{"text":"markdown…","draws_on":["ibn-kathir","maarif",…],"words":971,"status":"ok","coverage":0.93}}}
```

`draws_on` lists the sources that had material for the verse; the app shows
them under the entry.
