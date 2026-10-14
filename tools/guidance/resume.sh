#!/usr/bin/env bash
# Bring a fresh (or rewound) sandbox back to a working state and print what to do next.
#
#     bash tools/guidance/resume.sh
#
# 1. If the local HEAD fell behind origin/<current branch> while the files on disk are
#    current (this sandbox rewinds its git history between sessions), realign HEAD to
#    origin without touching the files. Never force-pushes, never switches branch.
# 2. If the pipeline is missing from this branch (a new session starts from main), merge
#    the branch that carries it.
# 3. Run the tests, print the progress table and the next job.
set -euo pipefail
cd "$(dirname "$0")/../.."

PIPELINE_BRANCH="arena/ea88d543-quran-explained"   # where the pipeline and the published chapters were developed
branch="$(git rev-parse --abbrev-ref HEAD)"
echo "branch: $branch"

git fetch -q origin "$branch" 2>/dev/null || true
if git rev-parse -q --verify "origin/$branch" >/dev/null 2>&1; then
  local_head="$(git rev-parse HEAD)"
  remote_head="$(git rev-parse "origin/$branch")"
  if [ "$local_head" != "$remote_head" ] && git merge-base --is-ancestor "$local_head" "$remote_head"; then
    echo "local HEAD $(git rev-parse --short HEAD) is behind origin/$branch $(git rev-parse --short "origin/$branch"): realigning (files untouched)"
    git reset -q --mixed "origin/$branch"
  fi
fi

if [ ! -f tools/guidance/HANDOFF.md ]; then
  echo "pipeline not on this branch: merging origin/$PIPELINE_BRANCH into $branch"
  git fetch -q origin "$PIPELINE_BRANCH"
  git merge --no-edit "origin/$PIPELINE_BRANCH"
fi

mkdir -p work/raw
echo "tests: $(python3 -m unittest discover -s tools/guidance/tests 2>&1 | tail -1)"
echo
python3 tools/guidance/status.py
echo
python3 tools/guidance/status.py --next
echo
echo "uncommitted changes: $(git status --short | wc -l | tr -d ' ')   (preview: start_process 'python3 tools/serve.py 8000')"
