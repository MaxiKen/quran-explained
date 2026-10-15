#!/usr/bin/env python3
"""One call to finish a job: ingest → verify → (assemble → commit → push).

    python3 tools/guidance/finish.py 002-001-001
    python3 tools/guidance/finish.py 002-intro --no-push
    python3 tools/guidance/finish.py 002-001-001 --model "claude (chat)"

Reads work/raw/<job>.md, files it as the job's result, runs the gates and
prints a compact report for the job's entries only. If any entry fails, it
stops there (fix work/raw/<job>.md and run again). Otherwise it merges the job
into data/guidance_NNN.json, commits the payload
and the raw file, pushes to the current branch, and prints the next job in
the same chapter. Full published-data verification is deferred until all
verses and the introduction are complete; follow CHAPTER_RUN.md once then.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import DATA, ROOT, WORK, read_json  # noqa: E402

PY = sys.executable


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    cp = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if check and cp.returncode != 0:
        sys.stdout.write(cp.stdout[-3000:])
        sys.stderr.write(cp.stderr[-3000:])
        raise SystemExit(f'command failed: {" ".join(args)}')
    return cp


def report_lines(report: dict, job_id: str, verses: list[int], is_intro: bool) -> tuple[list[str], bool]:
    lines, failed = [], False
    items = []
    if is_intro:
        items.append(('intro', report.get('intro') or {}))
    for v in verses:
        items.append((str(v), (report.get('verses') or {}).get(str(v)) or {}))
    for label, r in items:
        if not r:
            lines.append(f'  {label}: no report (not ingested?)')
            failed = True
            continue
        st = r.get('status', '?')
        failed = failed or st == 'fail'
        bits = [f'{st.upper():4}', f'{r.get("words", 0):>5} w']
        if 'coverage' in r:
            bits.append(f'cov {r["coverage"]:.2f}')
        if 'ratio' in r:
            bits.append(f'ratio {r["ratio"]:.2f}')
        lines.append(f'  {label:>5}: ' + '  '.join(bits))
        for e in r.get('errors') or []:
            lines.append(f'         FAIL {e}')
        for w in r.get('warnings') or []:
            lines.append(f'         flag {w[:220]}')
        miss = r.get('missing') or []
        if miss:
            lines.append(f'         missing: {", ".join(miss[:14])}' + (' …' if len(miss) > 14 else ''))
    return lines, failed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('job')
    ap.add_argument('--model', default='arena agent (in-session)')
    ap.add_argument('--file', help='default work/raw/<job>.md')
    ap.add_argument('--no-commit', action='store_true')
    ap.add_argument('--no-push', action='store_true')
    args = ap.parse_args()

    job_id = args.job
    surah = int(job_id.split('-')[0])
    is_intro = job_id.endswith('-intro')
    verses: list[int] = []
    if not is_intro:
        a, b = int(job_id.split('-')[1]), int(job_id.split('-')[2])
        verses = list(range(a, b + 1))
    raw = args.file or os.path.join(WORK, 'raw', f'{job_id}.md')
    if not os.path.exists(raw):
        raise SystemExit(f'missing {os.path.relpath(raw)}')

    # 1. ingest
    cp = run([PY, os.path.join(HERE, 'ingest.py'), '--job', job_id, '--file', raw, '--model', args.model], check=False)
    if cp.returncode != 0:
        print(cp.stdout.strip())
        print(cp.stderr.strip()[-2000:])
        return 1
    # 2. verify the job outputs
    run([PY, os.path.join(HERE, 'verify.py'), '--source', 'work', '--surahs', str(surah)], check=False)
    report = read_json(os.path.join(WORK, 'reports', f'{surah:03d}.json'))
    lines, failed = report_lines(report, job_id, verses, is_intro)
    print(f'{job_id}: gates')
    print('\n'.join(lines))
    if failed:
        print('→ fix work/raw/%s.md and run finish.py again (nothing published)' % job_id)
        return 1
    # 3. Assemble only. Full chapter verification must not run per job.
    run([PY, os.path.join(HERE, 'assemble.py'), '--surahs', str(surah)])
    print(f'published → data/guidance_{surah:03d}.json · full verification deferred until chapter completion')
    # 4. commit + push
    if not args.no_commit:
        payload = os.path.join(DATA, f'guidance_{surah:03d}.json')
        run(['git', 'add', payload, raw])
        what = 'introduction' if is_intro else (f'verse {verses[0]}' if len(verses) == 1 else f'verses {verses[0]}-{verses[-1]}')
        words = 0
        if is_intro:
            words = (report.get('intro') or {}).get('words', 0)
        else:
            words = sum(((report.get('verses') or {}).get(str(v)) or {}).get('words', 0) for v in verses)
        msg = f'Surah {surah}: {what} ({words:,} words)'
        cp = run(['git', 'commit', '-q', '-m', msg], check=False)
        if cp.returncode != 0:
            print('nothing to commit' if 'nothing to commit' in cp.stdout + cp.stderr else cp.stderr[-500:])
        else:
            sha = run(['git', 'rev-parse', '--short', 'HEAD']).stdout.strip()
            branch = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()
            pushed = ''
            if not args.no_push:
                cp = run(['git', 'push', '-q', 'origin', branch], check=False)
                pushed = ' · pushed' if cp.returncode == 0 else f' · PUSH FAILED: {cp.stderr.strip()[-300:]}'
            print(f'committed {sha} "{msg}"{pushed}')
    # 5. next
    try:
        from status import next_job
        nj = next_job(order=[surah])
        if nj is None:
            print(f'chapter {surah} complete: follow CHAPTER_RUN.md for the single final verification and file manifest; do not start another chapter')
        else:
            print(f'next: {nj.id}   →   python3 tools/guidance/digest.py {nj.id}')
    except Exception as exc:  # pragma: no cover
        print(f'next: (status unavailable: {exc})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
