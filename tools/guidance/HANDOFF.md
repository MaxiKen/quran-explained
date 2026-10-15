# HANDOFF — continuing the plain-English commentary, session after session

This file is the contract between sessions. A new agent (or a person) who reads
it and follows it will continue the work exactly as it was agreed with the
maintainer, with no design question re-opened and no step skipped. Read all of
it once, then work from §4.

Start of every session:

```bash
bash tools/guidance/resume.sh        # realigns git if the sandbox rewound, tests, progress table, next job
```

Then keep the preview alive with the process tool: `python3 tools/serve.py 8000`
(binds 0.0.0.0, sends no-store headers).

---

## 1. What this is, and where it stands

The app (`index.html`, `js/app.js`) shows the Qur'an with eight classical
tafsīrs per verse (`data/tafsir_NNN.json`: ibn-kathir, maarif, tazkirul,
tanwir, jalalayn, mukhtasar, qushayri, wahidi). The project adds, for every one
of the 6,236 verses and every surah, an original plain-English commentary
written **from** those eight texts, published as `data/guidance_NNN.json` and
rendered by the app above the folded sources under the label
**"Plain-English commentary"** with the disclosure
*"written with AI assistance from eight classical tafsīrs — the sources are below"*.

State (keep §8 current):

| surah | published | how |
|---|---|---|
| 1 Al-Fatihah | 7/7 + intro (24,361 words) | written in-session, through the pipeline, commit `85469f7` |
| 112 Al-Ikhlas | 1/4 (exemplar 112:1, flag) | seeded from `prompts/exemplars/112_001.md`. 112:2–4 are **written and verified** (`work/raw/112-001-004.md`, ok=0 flag=4 fail=0, flags are the virtue reports that belong to the introduction) but held unpublished until the sequence reaches 112: ingest that file, write `112-intro`, assemble. |
| 55 Ar-Rahman | 1/78 (exemplar 55:13) | seeded from `prompts/exemplars/055_013.md` |
| 2 Al-Baqarah | 286/286 + intro | completed, 412,897 verse words; full verification ok=159 flag=128 fail=0, commit `b4846f0` |
| everything else | 0 | pending, in order: 3 (next job `003-intro`), then 4 … 114 |

`python3 tools/guidance/status.py` prints the live version of this table.

### Current continuation and review status (2026-10-15)

- Al-Baqarah is complete: introduction plus 286/286 verse entries. The next
  unfinished job is `003-intro`. Ask `status.py --next` rather than hard-coding
  an old Al-Baqarah job.
- The maintainer required no full published-data verification of Surah 2 until
  verse 286. That instruction was honoured for the concluding work, and the
  final check has now run: **287 entries, ok=159 flag=128 fail=0**. This is a
  completed Surah-2-specific deferral, not a permanent ban on verification.
- Flag repair is now in progress. Seventy originally flagged entries have
  passed scoped checks after repairs. See `FLAG_REVIEW_002.md` for the exact
  batch and the 57 remaining unreviewed baseline flagged entries and one reviewed residual at 2:254. The earlier full
  result below is historical; a new full-chapter result is still pending.
- The 128 flags are **not all coverage noise**. They include long sentences,
  reading grade, matching runs, coverage, length and missing middle sections.
  Flags are publishable under the agreed gates, but remain editorial review
  items. A deterministic pass is not proof of full substantive coverage,
  historical accuracy, hadith authenticity or scholarly approval.
- All 42 pipeline tests passed. All 286 entries and the introduction rendered
  with zero leftover Markdown markers. These checks do not replace a browser
  smoke test or a scholarly/editorial review.
- The layer faithfully explains supplied material, including historical legal
  and economic views. It does not independently update those views into
  present-day law, financial advice or a contemporary fatwa. Do not add modern
  facts or rulings without a separately authorised sourcing change.
- Current completed payload commit: `b4846f0`; completion log: `7c521ba`.
  Work stays on the Arena session branch. No merge into `main` has been
  performed by the agent. After a maintainer merge, a fresh session should
  resume from the merged checkout and its live status, not regenerate Surah 2.

## 2. Decisions that are final — do not re-ask them

Agreed with the maintainer (MaxiKen) in the session that built the pipeline.
They are encoded in `prompts/system.md`, `prompts/verse_job.md`,
`prompts/intro_job.md` and `verify.py`; this list is the human-readable form.

| # | decision |
|---|---|
| Length | **Proportional to the material.** No fixed bands, no cap. Target ≈ 0.6 × the words of material about the verse (`pack.py OUTPUT_RATIO`), plus ~120 words of structure. A length is a floor, never a band: if the material is rich, the entry is long (1:1 has 7,000 words). Thin verses (three glosses, ~60 words) get a short entry, not padding. `verify` flags < 0.25 × material and > 200 + 1.5 × material. |
| Voice | **Anonymous, single integrated voice.** Never name the eight works or their authors (Ibn Kathīr, Mufti Shafīʿ / Maʿārif, Wahiduddin Khan / Tazkirul, Tanwīr al-Miqbās, Jalālayn, Mukhtaṣar, Qushayrī / Laṭāʾif, Wāḥidī / Asbāb). Never say "the sources", "the commentators", "Text 3". People the texts themselves quote (Ibn ʿAbbās, Qatādah, al-Qurṭubī, Ibn Jarīr, ar-Rāghib, ash-Shāfiʿī as a jurist…) are named exactly as the material names them. The maintainer wrote "fully autonomous" for this question; it was read as "fully anonymous" and implemented as a flag — if they ever ask for attribution instead, that is a prompt/verify change, not a rewrite. |
| Structure | Fixed opening (what the verse says, quoting at least five consecutive words of the app's own `ayah_en` translation) → `### Phrase by phrase` (each phrase of the translation in bold quotes, explained) → adaptive `###` headings taken from the material, question-style preferred (*Why single out that day?*) → `### In short`, 2–5 bullets. Markdown subset only: `###`, `**`, `- `, `1. `, `> `. No tables, links, HTML, rules. |
| Register | Plain modern English. Short sentences where possible (verify flags avg > 25 words). |
| Arabic | **No Arabic script** (only ﷺ). Transliteration with diacritics as the material uses them (ṣaḥīḥ, Ibn ʿAbbās, ar-Raḥmān). Prophets as "Mūsā (Moses)" on first mention. "Allah", not "God", except inside a quotation. |
| Hadith | Paraphrased simply; keep the collector and the grading **when the material gives them** (al-Bukhārī, Muslim, Aḥmad, at-Tirmidhī ḥasan ṣaḥīḥ…); drop isnād chains. Never add a collector, a grade or a cross-reference the material does not have — verify fails those. |
| Sources | **"Just put the contents. Use everything."** All eight, nothing quarantined: Qushayrī/Maybudī allusive readings, Tanwīr's Isrāʾīliyyāt, Maʿārif's rulings and excursions, all included, faithfully, with the material's own qualifiers ("it is said", "weak chain") kept as content. |
| Ranges | **One self-contained entry per verse.** Material that covers a range is distributed across the verses it covers (each verse carries the part about it; the prompt shows `shared_outside` and per-verse `material_words`). Never duplicate the same paragraph across sibling verses; never leave a range's content out. |
| Introductions | Every surah also gets an introduction (`<<<INTRO S>>>` job): names and meanings, revelation, virtues, verse count, what it covers, connection to the previous surah, `### In short`. Surah-level material in verse 1's blocks belongs here, not in 1:1. |
| UI | Label "Plain-English commentary"; disclosure wording above; eight sources folded below. Done in `js/app.js`; `data/*.json` is network-first with offline fallback, so payload-only updates do not require a `sw.js` cache-version bump. App-shell changes require cache-version review. |
| Files & git | Minified single-line JSON per surah; `.gitattributes` marks them; `ATTRIBUTION.md` section; **commit per chapter (or per job for long surahs), push every time**; one PR at the end from this branch. |
| Originality | Fail any entry with ≥ 24 words copied in a row from the material outside a quotation; flag ≥ 12. Quoted Qur'an passages followed by `(S:N)` and quotes ≤ 200 chars are exempt. |
| Exclusions | None. |
| Calibration | Exemplars `prompts/exemplars/001_002.md`, `112_001.md`, `055_013.md` were approved; Surah 1 is the extended calibration set. Read 1:4 (mid-size), 1:6 (argued) and 1:1 (maximum) before writing anything. |

Maintainer's standing rules from the repository's history, still binding: sources
are read **completely** before writing; open by explaining the verse and quote the
app translation's actual words; no fabrication, no unsourced claims, nothing from
the writer's own knowledge; carry scholarly disagreement honestly and attribute
it the way the material does; ﷺ after the Prophet's name; no em dashes or
semicolons outside quotations.

## 3. Tools (all in `tools/guidance/`, Python 3.11, stdlib only)

| tool | what it does |
|---|---|
| `status.py` | progress table from `data/`; `--next` the next pending job (packs the surah if `work/` is gone); `--material JOB --part k` prints a job's material, Arabic stripped, in ≤ 12 K-char parts; `--export-raw N` rebuilds `work/raw/*.md` from a published surah. |
| `resume.sh` | start-of-session: git realignment, tests, status, next job. |
| `digest.py` | a job's material prepared for complete, fast reading: per-verse checklist of the anchors the coverage gate wants, the translations to quote, then the material with Arabic/honorifics removed, referenced verse quotations collapsed to `[Q S:N …]` and repeated paragraphs collapsed. 27 K-char parts. `--quote S:N` prints the app's translation of any verse. |
| `finish.py` | one command per job: ingest → gates (compact report for the job only) → assemble → verify data → commit → push → next job. Stops at any FAIL. |
| `pack.py` | builds `work/jobs/NNN.json`: jobs of ≤ 8 verses / ≤ 60 K chars with per-verse material shares. `--estimate` for token/cost numbers. |
| `generate.py` | API path (Anthropic/OpenAI/Gemini). `--show JOB` prints the exact user prompt for a job (the system prompt is `prompts/system.md` + exemplars). `--dry-run` uses the mock writer. |
| `ingest.py` | files an output written outside `generate.py` (by hand, in a chat, from a batch API) as the job's result in `work/out/`. Refuses incomplete jobs. |
| `verify.py` | deterministic gates → `work/reports/NNN.json`; `--source work` for job outputs, `--source data` for published files. Exit 1 on any `fail`. |
| `audit.py` | optional second model pass (needs an API). Not used for Surah 1. |
| `assemble.py` | merges `work/out` into `data/guidance_NNN.json` (merge by default; `fail` entries left out; `--seed-exemplars` publishes the three exemplars). |
| `tests/` | `python3 -m unittest discover -s tools/guidance/tests` (42 tests as of 2026-10-15). |
| `../serve.py` | preview server, `python3 tools/serve.py 8000`. |
| `CONTINUE_PROMPT.md` | the message the maintainer pastes to start a new session; it points here. |
| `/AGENTS.md` | repository-root summary of the non-negotiables for any agent; it points here. |

`work/` is scratch and disappears with the sandbox, **except `work/raw/`**, which
is tracked in git so hand-written entries survive between sessions.

## 4. The authoring loop (what was done for Surah 1; do exactly this)

The sandbox has no route to any LLM API (only github.com, pypi.org,
registry.npmjs.org), and the GitHub token cannot read secrets or dispatch
workflows. So unless §7 becomes possible, **the agent is the writer**: it reads
the material and writes the entries itself, and everything else is the pipeline.

### 4.1 Pick the job

```bash
python3 tools/guidance/status.py --next
```

Order is fixed by the maintainer: **1 → 2 → 3 … 114, in sequence** (the
`ORDER` list in `status.py`). Within a surah: the introduction job first
(`NNN-intro`), then the verse jobs in verse order. Take the job it prints. Do
not skip ahead, do not pick favourites. A surah is published incrementally:
`assemble.py` merges each finished job into `data/guidance_NNN.json`, so
Al-Baqarah appears in the app verse-group by verse-group while it is being
written, and verses not yet published fall back to the sources.

### 4.2 Read all of the material (the fast way)

```bash
python3 tools/guidance/digest.py 002-001-001            # part 1 of N (27 K-char parts: as much as one tool result shows)
python3 tools/guidance/digest.py 002-001-001 --part 2   # … until the last part; issue the parts as parallel tool calls
python3 tools/guidance/digest.py --quote 6:101          # the app's translation of a verse the material cites
```

The digest is the full material with only what the entry must never carry
removed (Arabic script, honorific formulas, a source's sign-off) or made
retrievable (`[Q 6:101 "first words …"]` for a quoted verse with a reference,
`[≈ repeats …]` for a paragraph that repeats an earlier one). It starts with a
**checklist per verse**: the verses cited, collectors, grades, numbers, names and
terms that the coverage gate will look for. Write with the checklist beside
you: every item appears once, in your own words, in the entry of the verse it
belongs to. That is what makes an entry pass at the first attempt. The digest
also prints the translation to quote, so `generate.py --show` is not needed.
`status.py --material` still prints the untouched text if something looks odd.

Rules of reading, unchanged: every hadith with its collector and grading as
written; every `S:N` reference as written (the material has typos such as
`4:16` for 4:136 and `87:1-2` for three verses: cite only what is written, or
quote the verse's words without a number); every named person as spelled;
which paragraphs belong to which verse when a block covers several. For a
surah's first job, surah-level material (names, virtues, verse count,
revelation) goes to the intro job, not to verse 1.

### 4.3 Write `work/raw/<job>.md`

One file per job, with the exact markers:

```
<<<VERSE 112:1>>>
…entry…
<<<END>>>

<<<VERSE 112:2>>>
…
<<<END>>>

<<<NOTES>>>
- one line per point left out and why (surah-level → intro; belongs to another verse; broken text)
<<<END>>>
```

Intro jobs use `<<<INTRO 112>>>` … `<<<END>>>` and the same NOTES block.

Writing rules in the order they bite:

1. Opening paragraph quotes ≥ 5 consecutive words of the app's `ayah_en`
   (punctuation/em dash/brackets inside the quote are fine; verify normalises them).
2. Everything in the material about this verse goes in, once, in your own words.
   Cover the arguments, the examples, the rulings, the allusive readings, the
   poetry (paraphrased), the disagreements with their holders.
3. Nothing from outside the material. No names, dates, collectors, grades,
   verse numbers or "well-known" facts of your own. If you remember a better
   attribution than the material gives, you still write the material's.
4. Hadith: paraphrase, keep collector + grade, drop chains. Verse quotations:
   quote, with the reference the material gives, in the form `(2:255)` or `(41:34-36)`.
5. Lists of names are the only thing you may reproduce; **change their order or
   group them** so no 12-word run matches the material.
6. Plain English, short sentences, no em dashes, no semicolons (outside quotes),
   no Arabic script, no "the sources / the commentators / as we saw / let us".
7. Length: about 0.6 × the verse's material words, more if the material is dense
   with distinct points, never padded. Check `material words per verse` from
   `status.py --next`.
8. Shared blocks: give each verse its own part; refer to a sibling verse in one
   clause if needed ("the full hadith is under 1:2") rather than repeating it.
9. If a verse's entry already exists as an approved exemplar (1:2, 112:1,
   55:13), paste the exemplar's entry unchanged into the job file for that verse
   and write the others.

Commit the raw file as soon as a verse is finished (cheap insurance against a
sandbox reset): `git add work/raw && git commit -m "raw: 112-001-004 wip"`.

### 4.4 Finish the job: one command

```bash
python3 tools/guidance/finish.py 002-001-001
```

It ingests `work/raw/002-001-001.md`, runs the gates and prints, for the job's
entries only: status, words, coverage, ratio, every FAIL message, every flag,
and the missing anchors. If anything fails it stops (nothing is published):
edit the raw file and run it again. If nothing fails it merges the job into
`data/guidance_002.json`, verifies the published file, commits the payload and
the raw file (`Surah 2: verses 8-13 (6,120 words)`), pushes to the current
branch, and prints the next job. Then go straight to the next job's digest.

#### When the maintainer explicitly defers full-data verification

`finish.py` currently runs full published-data verification after **every job**.
Do not call it during an explicit deferral. The manual equivalent used to
complete Surah 2 is:

```bash
python3 tools/guidance/ingest.py --job JOB --file work/raw/JOB.md
python3 tools/guidance/verify.py --source work --surahs S
# Inspect the job report. Correct every failure and substantive omission.
python3 tools/guidance/assemble.py --surahs S
# Inspect the assembled result, then commit its payload and raw draft.
git add data/guidance_SSS.json work/raw/JOB.md
git commit -m "Surah S: completed job"
git push origin SESSION_BRANCH
```

`JOB`, `S`, `SSS` and `SESSION_BRANCH` are placeholders, not literal commands.
Assembly re-runs the gates and omits failed entries. Do not override it with
`--include-failed`. Once the requested endpoint is reached, run
`verify.py --source data --surahs S`, correct failures, run tests and the
render check, and record the full result in §8. Without an explicit deferral,
`finish.py` remains the documented default. Its repeated full check can be
slow (the complete Surah-2 check took about 24 minutes).

Fix every FAIL. Fix a flag when it is a real gap (a missing name you can
place, a verbatim run you can rephrase). Do not chase coverage noise (nisba-only
anchors, volume references, honorifics, a source's sign-off): a `flag` is
published and marked, a `fail` never is. §5 lists what each message means and
the fix that worked. Never publish with `--include-failed`. Never loosen a
threshold or a pattern in `verify.py` to make an entry pass. The only
permitted `verify.py` changes are genuine false positives (a spelling variant,
a punctuation form), each with a test in `tests/test_pipeline.py`.

For long surahs this means a push after every job: the merged payload is the
state, and `status.py --next` resumes from it after any reset. When a surah is
complete, add a row to §8 and move on without waiting. Bump nothing in
`sw.js` for payloads (only if `js/app.js` or `index.html` change).

Occasionally (once per surah is enough) run the render check so the app's
own markdown renderer is known to leave no raw markdown behind:

```bash
node - <<'EOF'
const fs=require('fs'); const src=fs.readFileSync('js/app.js','utf8');
function grab(n){const i=src.indexOf('function '+n+'(');let d=0,j=i;for(;j<src.length;j++){if(src[j]=='{')d++;else if(src[j]=='}'){d--;if(d==0)break;}}return src.slice(i,j+1);}
eval(grab('escapeHtml')+grab('parseInline')+grab('renderMarkdown'));
const g=JSON.parse(fs.readFileSync('data/guidance_002.json','utf8'));
for (const [k,v] of Object.entries(g.verses)) { const h=renderMarkdown(v.text); const n=(h.match(/[*#_]{2}|&lt;&lt;&lt;/g)||[]).length; if(n) console.log(k,'leftovers',n); }
if (g.intro) console.log('intro leftovers', (renderMarkdown(g.intro).match(/[*#_]{2}/g)||[]).length);
EOF
```

### 4.5 Throughput rules (how "extreme speed" is achieved without losing content)

- One job = three tool calls: the digest parts (in parallel), one `write_file`
  of the whole job, one `finish.py`. Never print an entry back, never re-read
  material you have already read, never run `--show`.
- Write the whole job in one go, all verses, from the checklist and the
  material. Length stays proportional to the material (≈ 0.6 ×, more when the
  points are dense); nothing is dropped to go faster, and nothing is padded.
- Go on to the next job in the same turn. Report to the maintainer at the end
  of the turn, not after every job.
- Commit and push happen inside `finish.py`; the raw file for a half-written
  long job can be committed early (`git add work/raw && git commit -m "raw: wip"`).

### 4.6 End of session

Everything committed and pushed; §8 updated; one-paragraph report to the
maintainer: surahs/verses done, words, ok/flag counts, anything that needs a
human decision.

## 5. Gate cheat-sheet (every message seen so far, with the fix that worked)

| message | cause | fix |
|---|---|---|
| `names a source or speaks as a digest: "…"` (fail) | one of the eight works/authors, or "the sources/commentators/Text n" | remove the name; say what it says in your own voice. `Abū Naṣr al-Qushayrī` in a hadith attribution is also caught — drop the name, keep the fact. Imam ash-Shāfiʿī as a jurist is allowed. |
| `names a collector the material does not: X` (fail) | collector not in this job's material, or a spelling the folder cannot match | use only collectors the material names; spelling variants (Marduwyah/Mardawayh) are now matched by consonant skeleton |
| `cross-reference S:N is not in the material` (fail) | a verse number you added or corrected | cite only numbers written in the material (`68 : 33` with spaces counts); otherwise quote words without a number |
| `no quotation of the translation in the opening` (fail) | opening lacks ≥ 5 consecutive words of `ayah_en` | quote the translation verbatim in the first paragraph |
| `Arabic script` (fail) | any Arabic letters | transliterate; ﷺ is the only exception |
| `missing "### Phrase by phrase" / "### In short"` (fail) | structure | exact headings |
| `copies the material verbatim (N words in a row)` (fail ≥ 24, flag ≥ 12) | paraphrase too close, or a list in the material's order | rephrase; reorder/group lists of names; quote a Qur'an passage with its `(S:N)` if it must stand verbatim |
| `coverage NN% (k of n anchors missing)` (flag < 85 %, fail < 50 %) | named people, numbers, terms, cross-refs from the material are absent | add the missing points; `missing` lists them. Noise like `Holy Qur'an`, `1:12`, `For Allah` can be ignored |
| `uses a grading the material does not (gharib)` (flag) | the word "strange" (alias of gharīb) or another grade word | use "odd", or the material's grade |
| `author voice: "let us"/"as we saw"` (flag) | digest phrasing | rewrite ("do not allow us", "above") |
| `em/en dash used` / `semicolon` (flag) | punctuation outside quotes | full stops, commas, colons |
| `long sentences (avg > 25)` / `reading grade > 12` (flag) | style | shorten where it does not cost content; acceptable to publish as `flag` |
| `padding` / `thin` (flag) | > 200 + 1.5 × material, or < 0.25 × material | cut repetition, or cover more of the material |
| `duplication with verse N` (flag) | same 10-word shingles in sibling entries | give each verse its own part of a shared block |

Published `flag` entries are permitted by the agreed publication gate, not
certified free of editorial problems. Inspect the reasons and repair real gaps
or matching passages when possible. A second-model audit has not been run for
Surah 2. `assemble.py` omits failing entries unless explicitly overridden, which
is forbidden by this contract.

## 6. Environment quirks (all hit before; do not rediscover them)

- **No LLM API from the sandbox.** Outbound only github.com, api.github.com,
  codeload.github.com, pypi.org, files.pythonhosted.org, registry.npmjs.org.
- **GitHub token is an integration token**: `gh secret list`, `gh api …/actions/secrets`,
  workflow dispatch → HTTP 403. Actions can only be triggered by the maintainer (§7).
- **Tool output truncates around 30 K chars**, silently dropping the middle. Use
  `status.py --material … --part k`; never `cat` a tafsir block.
- **`work/` (except `work/raw/`) and `/tmp` vanish** between sessions. Repack with
  `pack.py --surahs N` (status.py does it for you). Re-ingest from `work/raw` if
  `work/out` is needed again.
- **Local git history can rewind to the branch base between sessions while the
  files stay current.** `resume.sh` realigns (`git reset --mixed origin/<branch>`).
  If a push is rejected: `git fetch`, `git reset --mixed origin/<branch>`, recommit.
  **Never force-push.**
- **Sessions are pinned to one branch.** Work only on the session's branch; a new
  session's branch starts from `main`, so merge
  `origin/arena/e527c26f-quran-explained` into it (resume.sh does) until the PR is merged.
- Single-line JSON > 1 MB shows as an empty diff on GitHub; verify remote content
  with `gh api repos/MaxiKen/quran-explained/contents/data/guidance_NNN.json?ref=<branch> --jq .size`.
- The corpus names the eight works inside the texts (Maʿārif cites "Ibn Kathir"
  660 times); `verify.extract_anchors` skips those names so they are not coverage
  anchors, and the banned-name gate stops you repeating them.
- Known data quirks: `mukhtasar` block `2:3-4` holds only 2:4's text; 1:2
  `jalalayn` is misfiled basmalah commentary; 1:2 `qushayri` is Maybudī-style
  Persian-inflected text; stray `ﷺ` lines and U+FFFD characters occur. Coverage
  gaps caused by such quirks show as `flag`, not `fail`.

## 7. The API / GitHub Actions path (when the maintainer enables it)

`.github/workflows/guidance.yml` (workflow_dispatch: surahs, provider, model,
tier, shards, concurrency, replace, dry_run) runs `pack → generate → verify →
audit → assemble` and commits the payloads to the branch. It needs:

1. Repository secrets `ANTHROPIC_API_KEY` and/or `OPENAI_API_KEY` / `GEMINI_API_KEY`.
2. The workflow file on the default branch (it is only registered once it is on `main`).
3. A manual dispatch: Actions → Guidance → the next unfinished surah (currently `3`), provider `anthropic`. Do not regenerate completed chapters unless explicitly requested.

Local equivalent on a machine with network access:

```bash
python3 tools/guidance/pack.py --surahs 3 --shards 4
ANTHROPIC_API_KEY=… python3 tools/guidance/generate.py --surahs 3 --provider anthropic --concurrency 8
python3 tools/guidance/verify.py --source work --surahs 3
ANTHROPIC_API_KEY=… python3 tools/guidance/audit.py --surahs 3 --provider anthropic
python3 tools/guidance/assemble.py --surahs 3
python3 tools/guidance/verify.py --source data --surahs 3
```

Estimates (`pack.py --estimate`, whole Qur'an): 1,536 jobs, ~10.7 M input
tokens, ~5.4 M output tokens; claude-sonnet-4-5 ≈ $117 (+$89 audit),
gpt-5 ≈ $69, gemini-2.5-pro ≈ $69, haiku/flash/mini $14–39. After a model run,
spot-read at least three entries per surah against §2 before pushing.

Model output and hand-written output are interchangeable: both end up in
`work/out/` and go through the same gates.

## 8. Progress log (append a row per surah or partial push)

| date | surah | verses | words | gates | commit | by |
|---|---|---|---|---|---|---|
| 2026-10-14 | 1 | 1–7 + intro | 24,361 + 1,686 | ok=5 flag=3 fail=0 | 85469f7 | arena agent (in-session) |
| 2026-10-14 | 112 | 2–4 drafted, not published (order changed to 1→114) | 2,474 | ok=0 flag=4 fail=0 (coverage: virtue reports reserved for the intro) | work/raw/112-001-004.md | arena agent (in-session) |
| 2026-10-14 | 2 | intro + 1–22 (of 286) | 2,239 intro + ~35,300 verses | ok=14 flag=8 fail=0 (flags: coverage noise from isnād names / nisbas, long sentences) | d57f043 (last of 13 pushes, one per job) | arena agent (in-session, digest→write→finish loop) |
| 2026-10-14 | 2 | intro + 1–121 (of 286) | 2,239 intro + ~176,500 verses | ok=91 flag=31 fail=0 (flags: coverage noise, long sentences, a few 12–14-word stock-phrase runs) | e38be8e (one push per job, ~60 pushes) | arena agent (in-session, digest→write→finish loop) |
| 2026-10-14 | 2 | intro + 1–171 (of 286) | 2,298 intro + ~253,000 verses | ok=108 flag=64 fail=0 on the full `verify --source data` run at session end (flags: narrator-list runs, coverage noise, long sentences) | dac32325 (one push per job; publish = assemble + commit + push, per-job `verify --source work` gate, full verify-data once per session ≈ 8 min at 172 entries) | arena agent (in-session, digest→write→gate→publish loop) |
| 2026-10-14 | 2 | intro + 1–221 (of 286) | 2,298 intro + ~334,000 verses | ok=110 flag=112 fail=0 on the full `verify --source data` run after the block 172–221 (flags: verbatim narrator-list runs, long sentences, reading grade, coverage 0.80–0.85 noise) | f713f4cf (per-job gate + publish; full verify-data once at the end ≈ 14 min at 222 entries) | arena agent (in-session, digest→write→gate→publish loop) |

| 2026-10-15 | 2 | intro + 1–233 (of 286) | 21,633 new words in 222–233 | new entries ok=11 flag=1 fail=0 from per-job work gates. Full verify-data deferred until 286 by maintainer instruction. | f50dea5 (per-job publish and push on arena/e527c26f-quran-explained) | arena agent (in-session) |

| 2026-10-15 | 2 | intro + 1–257 (of 286) | 23,992 new words in 234–257 | new entries ok=18 flag=6 fail=0 from per-job work gates. Full verify-data remains deferred until 286 as instructed. | 307e0db (per-job publish and push on arena/e527c26f-quran-explained) | arena agent (in-session) |

| 2026-10-15 | 2 | intro + 1–266 (of 286) | 10,878 new words in 258–266 | New work entries ok=5 flag=4 fail=0. Remaining flags are coverage noise (editorial numbers, damaged name, generic words). Full verify-data remains deferred until 286 as instructed. | cd5f83c (per-job publish and push on arena/e527c26f-quran-explained) | arena agent (in-session) |

| 2026-10-15 | 2 | complete: intro + 1–286 | 412,897 verse words total; 25,310 new words in 267–286 | Full published-data verification, run only after 286: 287 entries, ok=159 flag=128 fail=0. All 42 pipeline tests pass. All 286 verses and introduction render with zero leftover Markdown markers. | b4846f0 (seven sequential job pushes for 267–286 on arena/e527c26f-quran-explained) | arena agent (in-session) |

| 2026-10-15 | 2 | flag repair batch 1: 3, 4, 6, 16, 20, 22, 23, 29, 33, 40, 167, 202, 205, 206, 241, 279 | prose and structure repairs, no new verses | 16 entries pass scoped unchanged gates with sibling context. 112 baseline flagged entries remain. Interrupted full recheck was terminated without a result. See FLAG_REVIEW_002.md. | current flag-repair commit | arena agent (in-session) |

| 2026-10-15 | 2 | flag repair batch 2: 139, 146, 157, 160, 162, 175, 182, 207–212, 214, 216, 218 | substantive section rewrites and matching repairs | 16 additional entries pass scoped gates; matching also checked against all chapter material. 96 baseline flagged entries await repairs. Full chapter verification remains explicitly deferred until all 128 are addressed. | current batch-2 commit | arena agent (in-session) |

| 2026-10-15 | 2 | flag repair batch 3: 94, 107, 112, 114, 118, 121, 144, 192 | sentence splitting and source-matching paraphrases | Eight entries pass scoped unchanged gates and chapter-material matching checks. 88 baseline flagged entries remain. Complete verification remains deferred until all 128 are addressed. | current batch-3 commit | arena agent (in-session) |

| 2026-10-15 | 2 | flag repair batch 4: 147, 153, 154, 161, 166, 168, 169, 172 | matching paraphrases and clarified phrasing | Eight scoped passes, no chapter-material matching runs. 80 baseline flagged entries remain. Full verification deferred until all 128 are addressed. | current batch-4 commit | arena agent (in-session) |

| 2026-10-15 | 2 | flag repair batch 5: 31, 98, 109, 120, 148–152, 171, 179, 252, 254, 265, 266 | fifteen entries edited and source-reviewed | 14 scoped passes; 254 retains a documented truncated-transliteration coverage flag. All 15 have no errors or chapter-material matching runs. Campaign: 62 scoped passes, 1 reviewed residual, 65 unreviewed. Full verification deferred until every baseline entry is addressed. | current batch-5 commit | arena agent (in-session) |

| 2026-10-15 | 2 | flag repair batch 6: 155, 156, 158, 159, 163, 165, 170, 174 | matching-run paraphrases and prose clarification | All 8 pass scoped unchanged gates and chapter-material matching checks. Campaign: 70 scoped passes, 1 reviewed residual, 57 awaiting review. Complete verification still deferred until all 128 are addressed. | current batch-6 commit | arena agent (in-session) |

## 9. Calibration — read before writing

- `prompts/exemplars/001_002.md` — approved by the maintainer; the voice.
- `data/guidance_001.json` (or `work/raw/001-*.md`): 1:4 for a 2,300-word entry
  with rulings and an argument; 1:6 for a 2,600-word entry built on one long
  excursion (degrees of guidance); 1:1 and 1:7 for the top end (7,000 words,
  dozens of named positions, hadiths and rulings, all from the material).
- `prompts/system.md` and `prompts/verse_job.md` — the prompt the writer follows.

## 10. Mistakes already made once (do not repeat)

- Writing "aṭ-Ṭabarī" from memory when the material said "Ibn Jarir" → fail. Write the material's name.
- Citing 4:136 for the "O you who believe, believe" verse because the material's `4:16` was obviously a typo → fail. Quote the words, no number.
- Naming "Abū Naṣr al-Qushayrī" as a narrator → banned-name fail. Omit the name.
- Reproducing a 34-name list in the material's order → verbatim fail. Group and reorder.
- The word "strange" → spurious gharīb-grading flag. Use "odd".
- "do not let us turn aside" → "author voice: let us" flag. Rephrase.
- Putting surah-level material (names, virtues, verse count) into 1:1 instead of the intro → duplication. Intro job owns it.
- Trusting that `work/` or `/tmp` would still be there next session. Only `work/raw/` and `data/` persist (through git).
- Assuming a long quoted Qur'an passage would be exempt from the verbatim gate without its `(S:N)` reference. Add the reference.
- Writing the phrases "the source" or "the commentators" in an entry (even as ordinary English: "the source of guidance") → "names a source / speaks as a digest" FAIL. Use "where guidance comes from", "scholars agree".
- Reproducing a rhetorical list, a name list or a one-sentence definition in the material's order → 12+-word verbatim flag (24+ fails). Reorder items, split the sentence, change connectives; the `verify.verbatim_runs` snippet in §5 shows exactly which runs.
- A quoted Qur'an passage longer than 200 chars containing a semicolon → semicolon flag. Quote the shorter half and paraphrase the rest, keeping the `(S:N)`.
- A replace-pair polish script with ONE pair that is not in the file (a no-op or dummy pair) → the `assert` aborts the whole script before anything is written, and the re-run of finish.py is wasted. Check every pair, never include placeholders.
- Stopping a running `finish.py` from the UI does not kill it: it kept running in the background and committed+pushed `58ddac5` while the next check showed HEAD unchanged. After any interrupted finish run, `git log`/`git ls-remote` before doing anything else, and expect the publish to have landed.
- Qushayrī/Maybudī homily sentences, maarif legal/analogy sentences and Ibn-Kathīr-style "X said that Y said" chains survive a faithful first draft as 12–17-word runs (9 in 2:120 alone). Restructure clause order, split litanies into short sentences, turn nouns into verbs: synonym swaps do not break the run.
- Naming a collector (Ibn Abī Ḥātim, Ibn Jarīr …) that the job checklist does not list → only safe after confirming the name is in the material (`verify.fold(mat)` substring check). Garbled spellings in the material are not recognised: write "the Ṣaḥīḥ records…".
- A verse number of an adjacent verse written bare ("114", "118", "120") shows up as a missing anchor; write it as "(2:114)" once and it is covered.
