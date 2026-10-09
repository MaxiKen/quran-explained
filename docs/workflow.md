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
git fetch origin arena/2c46b8a2-quran-explained
git reset --hard origin/arena/2c46b8a2-quran-explained
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

```bash
python3 tools/dump_sources.py <surah> <lo> <hi>
```

This prints the app's own translation for every verse (the wording you must
quote), the tier and word target, and the six sources. Ibn Kathīr is filtered
to sentences carrying named authorities and definitions; add `--ik` for more
or `--all` for everything including the Arabic.

**Read the output before writing a word.** Writing first and checking after is
how attributions get invented.

For a verse with a very long Ibn Kathīr entry, run a second pass on that verse
alone with `--all`.

## 4. Write

```bash
cp tools/author_template.py /tmp/g0NN.py
# set SURAH and TITLE, fill the VERSES dict
python3 /tmp/g0NN.py
```

Keep the working script in `/tmp`. Only the JSON it writes goes in Git.

Write to the voice in [voice.md](voice.md). The plan target is a **floor**, not a band — meet at least 75% of it. Running long is never a problem; running short is.

## 5. Verify

```bash
npm i jsdom --prefix /tmp/apptest          # once per session; /tmp does not persist
export NODE_PATH=/tmp/apptest/node_modules
for h in sources-all guidance-112 guidance-001 guidance-002; do
  printf "%-16s " "$h:"; node tools/tests/$h.js 2>&1 | tail -1
done
```

Add a `tools/tests/guidance-NNN.js` for each newly authored surah — copy the
closest existing one and change `S`, `LO`, `HI`, `LAST`, the translation
fragments and the `NAMES` list. See [testing.md](testing.md).

**Every harness must pass before committing.** Do not commit on a suite that
is red, even if the failure looks like a stale assertion — fix the assertion
and say what it was.

## 6. Commit and push

```bash
git add -A
git commit -m "..."
git push origin arena/2c46b8a2-quran-explained
```

**Push every run. No exceptions.** The remote branch is the only durable copy;
the workspace has been reset mid-project once already. See
[batching.md](batching.md#push-after-every-run).

## 7. Update progress

`docs/progress.md` is maintained by hand — update the "authored" table and the
next-range line before you push, so the next session starts from truth rather
than from `git log`.
