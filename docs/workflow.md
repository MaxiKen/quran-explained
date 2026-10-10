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
git fetch origin arena/525a7113-quran-explained
git reset --hard origin/arena/525a7113-quran-explained
```

## 1. Start the server

```bash
python3 -m http.server 8000 --bind 0.0.0.0    # from the repo root
```

Must bind `0.0.0.0`, not `127.0.0.1`, or the user gets no preview. The
harnesses also need it. If `curl http://127.0.0.1:8000/` returns `000`, the
server is not running — start it before doing anything else.

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

**Compiled** (the default for volume): the packet is the reading step.

```bash
python3 tools/verse_packet.py <surah> <lo>-<hi>
```

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
# /tmp/b0NN.md:  ### 1:1 / > the verse's translation / ~ lead-in / ## Heading. / - <ref>
python3 tools/compile_guidance.py <surah> /tmp/b0NN.md --dry    # nothing written
python3 tools/compile_guidance.py <surah> /tmp/b0NN.md
```

The lead line (`~` before the first heading) is where the explanation goes and has
a 150-word budget; connectives inside sections get 26. `+auto N` tops a section up
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
for h in sources-all guidance-001; do      # the two that boot the app in jsdom
  printf "%-16s " "$h:"; node tools/tests/$h.js 2>&1 | tail -1
done
```

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
git push origin arena/525a7113-quran-explained
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
