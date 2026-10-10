# Authoring workflow

The loop for one session. Follow it in order; every step exists because
skipping it caused a problem at least once.

## 0. Orient

```bash
git log --oneline -3
python3 tools/progress.py --next
```

`progress.py --next` prints the exact verse to resume at and how much of that
surah is left. **Do not trust the local working tree to be intact** — see
[pitfalls.md](pitfalls.md#the-workspace-can-be-reset). If files look wrong:

```bash
git fetch origin arena/1abff644-quran-explained
git reset --hard origin/arena/1abff644-quran-explained
```

## 1. Start the server

```bash
python3 tools/serve.py 8090 &                 # from the repo root
```

`tools/serve.py` binds `0.0.0.0` and answers every request `no-store`. Do **not**
use `python -m http.server`: it sends `Last-Modified` and no `Cache-Control`, so a
browser may answer a repeat request for `sw.js` out of its own HTTP cache — the worker
then never learns a new version exists, never activates, and keeps serving the payload
it cached, which looks exactly like content that was never written. The harnesses need
this server too. If `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8090/index.html`
is not `200`, start it before doing anything else.

## 2. Pick the range

Read [batching.md](batching.md) for the size rule. Then confirm the size:

```bash
python3 tools/dump_sources.py <surah> <lo> <hi> | grep "range total"
```

Stop at a **thematic boundary**, not an arbitrary verse count. Good boundaries
are the ones the sources themselves mark — Ibn Kathīr and Maʿārif both describe
al-Baqarah's opening as four verses on the believers, two on the disbelievers,
thirteen on the hypocrites. Those are natural stopping points.

## 3. Read before writing

Pick the mode first (see [voice.md](voice.md) — "Two ways a verse gets made").
`python3 tools/progress.py --next` prints whether the resume verse is `authored_only`;
if it is, this step and the next are the authored path, and `compile_guidance.py` will
refuse a spec for it. Plan the run so those verses come in runs of 5–10, not inside a
compiled batch.

**Compiled** (the default for volume): the packet is the reading step.

```bash
PACKET_CAP=4 PACKET_TRUNC=66 python3 tools/verse_packet.py <surah> <lo>-<hi>
```

`PACKET_CAP` (sentences per set) and `PACKET_TRUNC` (words per sentence) shrink only
what is printed, never what the compiler accepts — 5 verses at 4/66 is one screen and
enough to select from; go to 6/120 on a verse that will not compile.

It prints, per verse: the app's own translation (the wording the lead must
quote), the tier, the floor, the flags, and a ranked shortlist of numbered
sentences from all eight sets — `J1.1.2`, `Q3.1.4`, `W104.1.3`. Read the whole
packet before choosing; a compiled verse is a *selection*, and the selection is
the editorial work. Refs are positional, so re-dump the packet rather than
reusing a spec from an earlier session.

**Authored** (rulings in dispute, and verses whose material is thinner than
their floor): read the raw blocks.

```bash
python3 tools/dump_sources.py <surah> <lo> <hi>
```

Ibn Kathīr is filtered to sentences carrying named authorities and definitions;
`--ik` widens it, `--all` prints everything including the Arabic. For a verse
with a very long entry, run a second pass on that verse alone with `--all`.

**Read the output before writing a word.** Writing first and checking after is
how attributions get invented.

## 4. Write

**Compiled** — write a spec, then let the compiler emit the JSON.

```bash
# spec:  ### 2:36 / ~ lead-in / ## Heading / - <ref> …   (the `>` line is added for you)
python3 tools/fill_quotes.py /tmp/b0NN.md                       # pastes each verse's ayah_en
python3 tools/compile_guidance.py <surah> /tmp/b0NN.md --dry    # nothing written
python3 tools/compile_guidance.py <surah> /tmp/b0NN.md

Copy `tools/examples/spec_2-31_2-35.md` to start — it is a five-verse batch that compiles
clean, so it is also the fastest way to confirm your tooling agrees with the docs
(`python3 tools/compile_guidance.py 2 tools/examples/spec_2-31_2-35.md --dry`).

Never type the `> ` line: it is what the lead is validated against, and a mistranscription
surfaces as a coverage failure three steps later. Patch a spec with `if a in s:` + a report
of the misses — a script that `assert`s mid-way never reaches its write, so the file is
silently unchanged and the next gate reads like a regression.
```

The lead line (`~` before the first heading) **is** the explanation: it has to carry
a quote of every phrase of the translation, in order, with each one explained, so it
runs `LEAD_FLOOR`–`LEAD_CAP` words (240–620 at tier A) and not less than 20% of the
entry. The `>` line is the verse the spec is written against — it is checked against
`data/chapter_NNN.js` and is **not** emitted, because the commentary must not open by
reciting the whole verse. Connectives inside sections get 26. `+auto N` tops a section up
from the packet's leftovers when the shortlist has more worth having than you
picked. Read every line of a `--dry` failure list; the messages say exactly which
sentence was refused and why.

**Authored** — keep a generator script outside the repo and commit only its output.

```bash
cp tools/author_template.py /tmp/g0NN.py
# set SURAH and TITLE, fill the VERSES dict
python3 /tmp/g0NN.py
```

Either way, write to the voice in [voice.md](voice.md). The plan target is a
**floor**, not a band — meet at least 75% of it. Running long is never a problem;
running short is.

## 5. Verify

```bash
npm i jsdom --prefix /tmp/apptest          # once per session; /tmp does not persist
export NODE_PATH=/tmp/apptest/node_modules
python3 tools/verify_verse.py <surah> --all
node tools/tests/style-check.js
node tools/tests/sets-integrity.js
node tools/tests/guidance-range.js          # the batch's entries, as the reader gets them
for h in sources-all guidance-001; do      # the two that boot the app in jsdom
  printf "%-16s " "$h:"
  BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/$h.js 2>&1 | tail -1
done
```

`BASE` is the port the two jsdom harnesses fetch from (default `http://127.0.0.1:8000`);
they take it from the environment precisely because the preview port has moved before and
a hard-wired one fails as `ECONNREFUSED`, which reads like a broken payload. Set it to
whatever `tools/serve.py` is on.

Add a `tools/tests/guidance-NNN.js` for each newly authored surah — copy the
closest existing one (`guidance-001.js`) and change the surah number, the verse
range, the translation fragments and the `NAMES` list. See
[testing.md](testing.md).

**Every harness must pass before committing.** Do not commit on a suite that
is red, even if the failure looks like a stale assertion — fix the assertion
and say what it was.

## 6. Commit and push

```bash
git add -A
git commit -m "..."
git push origin arena/1abff644-quran-explained
```

**Push every run. No exceptions.** The remote branch is the only durable copy;
the workspace has been reset mid-project once already. See
[batching.md](batching.md#push-after-every-run).

## 7. Update progress

Update the state table in `AGENTS.md` and the counts in `docs/progress.md` before
you push, so the next session starts from truth rather than from `git log`. Both
are cheap to get wrong and both are the first thing a new session reads. If you
added a set or changed a band, re-run `tools/tier_verses.py` and record the
tier-change count in the commit message.

## Heading proof and the retired auto fill (2026-10-10)

- **Every heading is written from its own sources.** A heading is a question or a part of the verse that needs explaining. The sentences cited under it must answer that question or explain that part, in full.
- **Real content, not a term.** The gate requires each heading to cite at least two source sentences carrying its key terms, totalling at least 60 words. A key term alone is not enough. The gate measures coverage; the writer must still read the sources in full.
- **The automatic fill is retired.** The compiler no longer appends unlabelled sentences under a generic heading such as "What else the same passage holds". A `+auto` line fails the gate.
- **The sources are read completely before writing.** Comprehensive, detailed and helpful is the standard.
