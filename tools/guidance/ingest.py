#!/usr/bin/env python3
"""Store a model output that was produced outside generate.py (pasted from a
chat, written by hand, or returned by a batch API) as the result of a job, so
the rest of the pipeline (verify -> audit -> assemble) treats it like any
other output.

    python3 tools/guidance/ingest.py --job 001-002-005 --file work/raw/001-002-005.md --model "claude-sonnet-4-5 (chat)"

The file holds the raw output with the <<<VERSE S:N>>> ... <<<END>>> entries
(or <<<INTRO S>>> ... <<<END>>>) and the optional <<<NOTES>>> block. The job
must exist in work/jobs/SSS.json; the output must carry every verse of the
job, or it is refused.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import WORK, Job, ensure_dir, read_json, read_text, word_count  # noqa: E402
from generate import parse_output  # noqa: E402


def ingest(job_id: str, text: str, *, jobs_dir: str, out_dir: str, model: str, provider: str = 'manual') -> str:
    surah = int(job_id.split('-')[0])
    job_path = os.path.join(jobs_dir, f'{surah:03d}.json')
    if not os.path.exists(job_path):
        raise SystemExit(f'no job file {job_path}: run pack.py --surahs {surah} first')
    jobs = {j['id']: Job.from_json(j) for j in read_json(job_path)}
    job = jobs.get(job_id)
    if not job:
        raise SystemExit(f'job {job_id} not found in {job_path} (ids: {", ".join(sorted(jobs))})')
    parsed = parse_output(text)
    problems = []
    if job.kind == 'intro':
        if not parsed['intro']:
            problems.append('no <<<INTRO>>> block')
    else:
        missing = [v for v in job.verses if v not in parsed['verses'] or not parsed['verses'][v].strip()]
        if missing:
            problems.append('missing entries for ' + ', '.join(f'{surah}:{v}' for v in missing))
        extra = [v for v in parsed['verses'] if v not in job.verses]
        if extra:
            problems.append('entries for verses outside the job: ' + ', '.join(map(str, extra)))
    if problems:
        raise SystemExit('refused: ' + '; '.join(problems))
    record = {
        'job_id': job.id, 'kind': job.kind, 'surah': job.surah,
        'verses': {str(v): parsed['verses'][v] for v in job.verses} if job.kind == 'verses' else {},
        'intro': parsed['intro'] if job.kind == 'intro' else None,
        'notes': parsed['notes'], 'provider': provider, 'model': model,
        'attempts': [{'ingested': True, 'words': word_count(text)}], 'status': 'ok',
        'created': dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
    }
    folder = os.path.join(out_dir, f'{surah:03d}')
    ensure_dir(folder)
    path = os.path.join(folder, f'{job.id}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=1)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--job', required=True, help='job id, e.g. 001-002-005 or 001-intro')
    ap.add_argument('--file', required=True, help='raw output text with the <<<VERSE>>> / <<<INTRO>>> markers')
    ap.add_argument('--model', default='manual')
    ap.add_argument('--provider', default='manual')
    ap.add_argument('--jobs', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--out', default=os.path.join(WORK, 'out'))
    args = ap.parse_args()
    path = ingest(args.job, read_text(args.file), jobs_dir=args.jobs, out_dir=args.out,
                  model=args.model, provider=args.provider)
    print(f'stored {os.path.relpath(path)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
