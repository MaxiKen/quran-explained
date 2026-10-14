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
| 112 Al-Ikhlas | 1/4 (exemplar 112:1, flag) | seeded from `prompts/exemplars/112_001.md` |
| 55 Ar-Rahman | 1/78 (exemplar 55:13) | seeded from `prompts/exemplars/055_013.md` |
| everything else | 0 | pending |

`python3 tools/guidance/status.py` prints the live version of this table.

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
| UI | Label "Plain-English commentary"; disclosure wording above; eight sources folded below. Done in `js/app.js`; `sw.js` cache version bumps when payloads change. |
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
| `pack.py` | builds `work/jobs/NNN.json`: jobs of ≤ 8 verses / ≤ 60 K chars with per-verse material shares. `--estimate` for token/cost numbers. |
| `generate.py` | API path (Anthropic/OpenAI/Gemini). `--show JOB` prints the exact user prompt for a job (the system prompt is `prompts/system.md` + exemplars). `--dry-run` uses the mock writer. |
| `ingest.py` | files an output written outside `generate.py` (by hand, in a chat, from a batch API) as the job's result in `work/out/`. Refuses incomplete jobs. |
| `verify.py` | deterministic gates → `work/reports/NNN.json`; `--source work` for job outputs, `--source data` for published files. Exit 1 on any `fail`. |
| `audit.py` | optional second model pass (needs an API). Not used for Surah 1. |
| `assemble.py` | merges `work/out` into `data/guidance_NNN.json` (merge by default; `fail` entries left out; `--seed-exemplars` publishes the three exemplars). |
| `tests/` | `python3 -m unittest discover -s tools/guidance/tests` (36 tests). |
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

Order is fixed: 1 → 112 → 113 → 114 → 2 → 3 … 111. Take the job it prints.
Do not skip ahead, do not pick favourites.

### 4.2 Read all of the material

```bash
python3 tools/guidance/status.py --material 112-001-004 --part 1   # then --part 2, 3 … until the last
```

Read every part. The tool output truncates silently around 30 K characters, so
never print a block another way; the parts are sized to be safe. While reading,
note: every hadith with its collector and grading as written; every `S:N`
cross-reference as written (the material has typos such as `4:16` for 4:136 and
`87:1-2` for three verses — you may only cite what is written; if a number is
wrong, quote the verse's words without a number); every named person exactly as
spelled; which paragraphs belong to which verse when a block covers several.
For the surah's first job, separate surah-level material (names, virtues, verse
count, revelation) — it goes to the intro job, not to verse 1.

Print the prompt once per job and follow it; it carries the translation to
quote, the per-verse material words and the range notes:

```bash
python3 tools/guidance/generate.py --show 112-001-004
```

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

### 4.4 Gate loop

```bash
python3 tools/guidance/ingest.py --job 112-001-004 --file work/raw/112-001-004.md --model "arena agent (in-session)"
python3 tools/guidance/verify.py --source work --surahs 112
python3 - <<'EOF'
import json; r=json.load(open('work/reports/112.json'))
for v,e in r['verses'].items(): print(v, e['status'], e['words'], 'cov', e['coverage'], 'ratio', e['ratio']); print('  errors', e['errors']); print('  warnings', e['warnings']); print('  missing', e['missing'][:25])
if r.get('intro'): print('intro', r['intro']['status'], r['intro']['errors'], r['intro']['warnings'])
EOF
```

Fix every `error` (→ fail) and every `warning` you can (→ flag), edit the raw
file, re-ingest, re-verify. Loop until `fail=0`. §5 lists what each message
means and the fix that worked. To see the exact copied runs:

```bash
python3 - <<'EOF'
import json, sys; sys.path.insert(0,'tools/guidance'); import verify
from common import strip_arabic_lines
job=[j for j in json.load(open('work/jobs/112.json')) if j['id']=='112-001-004'][0]
rec=json.load(open('work/out/112/112-001-004.json'))
mat='\n'.join(strip_arabic_lines(b['text']) for b in job['blocks'])
for v,md in rec['verses'].items():
    for L,s in verify.verbatim_runs(md, mat): print(v, L, s)
EOF
```

Never publish with `--include-failed`. Never loosen a threshold or a pattern in
`verify.py` to make an entry pass. The only permitted `verify.py` changes are
genuine false positives (a spelling variant, a punctuation form), each with a
test in `tests/test_pipeline.py` — see the commit for `85469f7` for the shape.

### 4.5 Publish

```bash
python3 tools/guidance/assemble.py --surahs 112          # merges into data/guidance_112.json
python3 tools/guidance/verify.py --source data --surahs 112
node /dev/stdin <<'EOF'
// render check: the app's own markdown renderer must leave no raw markdown behind
const fs=require('fs'); const src=fs.readFileSync('js/app.js','utf8');
function grab(n){const i=src.indexOf('function '+n+'(');let d=0,j=i;for(;j<src.length;j++){if(src[j]=='{')d++;else if(src[j]=='}'){d--;if(d==0)break;}}return src.slice(i,j+1);}
eval(grab('escapeHtml')+grab('parseInline')+grab('renderMarkdown'));
const g=JSON.parse(fs.readFileSync('data/guidance_112.json','utf8'));
for (const [k,v] of Object.entries(g.verses)) { const h=renderMarkdown(v.text); console.log(k, 'leftovers', (h.match(/[*#_]{2}|&lt;&lt;&lt;/g)||[]).length, 'h4', (h.match(/<h4/g)||[]).length); }
if (g.intro) console.log('intro leftovers', (renderMarkdown(g.intro).match(/[*#_]{2}/g)||[]).length);
EOF
git add data/guidance_112.json work/raw
git commit -m "Surah 112: plain-English commentary, verses 1-4 and introduction"   # or "…: verses 1-30" for a partial long surah
git push origin <this session's branch>
```

For long surahs publish and push **after every job**; the merged payload is the
state, and `status.py --next` resumes from it after any reset.

When a surah is complete: bump nothing in `sw.js` (the guidance cache key is
already versioned per payload; bump `CACHE_VERSION` only if `js/app.js` or
`index.html` change), add a row to §8, and move on without waiting.

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

Published `flag` entries are fine (they would go to the LLM audit if an API
existed). Published `fail` entries are not possible: `assemble.py` omits them.

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
  `origin/arena/ea88d543-quran-explained` into it (resume.sh does) until the PR is merged.
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
3. A manual dispatch: Actions → Guidance → surahs `112-114,2` (pilot), provider `anthropic`.

Local equivalent on a machine with network access:

```bash
python3 tools/guidance/pack.py --surahs 112-114,2 --shards 4
ANTHROPIC_API_KEY=… python3 tools/guidance/generate.py --surahs 112-114,2 --provider anthropic --concurrency 8
python3 tools/guidance/verify.py --source work --surahs 112-114,2
ANTHROPIC_API_KEY=… python3 tools/guidance/audit.py --surahs 112-114,2 --provider anthropic
python3 tools/guidance/assemble.py --surahs 112-114,2
python3 tools/guidance/verify.py --source data --surahs 112-114,2
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
