#!/usr/bin/env python3
"""Where the generation stands, and what to do next.

    python3 tools/guidance/status.py                  # progress table (surahs touched + the next one) and totals
    python3 tools/guidance/status.py --all            # all 114 surahs
    python3 tools/guidance/status.py --next           # the next job to write (packs that surah's jobs if work/ is gone)
    python3 tools/guidance/status.py --next --show    # ... and print the full prompt for it (= generate.py --show)
    python3 tools/guidance/status.py --material 002-001-005 --part 1   # the job's material, Arabic stripped, in parts
    python3 tools/guidance/status.py --export-raw 1   # rebuild work/raw/<job>.md from data/guidance_001.json

Progress is read from data/guidance_NNN.json only, never from work/, so it
survives a wiped sandbox. Order of work: surahs 1 -> 114 in sequence, the
introduction of a surah before its verses. A surah is finished when every verse and the introduction are
published; a verse job is pending while any of its verses is unpublished.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import DATA, WORK, Job, chapter_meta, ensure_dir, read_json, strip_arabic_lines, word_count  # noqa: E402
from generate import load_jobs, render_user  # noqa: E402

ORDER = list(range(1, 115))   # maintainer's decision: strictly 1 -> 2 -> 3 ... 114
CHUNK = 12_000   # the sandbox tool output truncates around 30 K characters; keep every print well under that


def published(surah: int, data_dir: str = DATA) -> tuple[dict[int, str], bool]:
    """verse -> status for the published entries of a surah, and whether it has an intro."""
    path = os.path.join(data_dir, f'guidance_{surah:03d}.json')
    if not os.path.exists(path):
        return {}, False
    g = read_json(path)
    verses = {int(k): (v.get('status') or 'ok') for k, v in (g.get('verses') or {}).items() if (v.get('text') or '').strip()}
    return verses, bool((g.get('intro') or '').strip())


def ensure_jobs(surah: int, jobs_dir: str) -> list[Job]:
    path = os.path.join(jobs_dir, f'{surah:03d}.json')
    if not os.path.exists(path):
        subprocess.run([sys.executable, os.path.join(HERE, 'pack.py'), '--surahs', str(surah), '--out', jobs_dir],
                       check=True, capture_output=True, text=True)
    jobs = load_jobs(jobs_dir, [surah])
    # the introduction first (its material is the opening of the commentaries), then the verse jobs in order
    return sorted(jobs, key=lambda j: (j.kind != 'intro', j.verses[0] if j.verses else 0))


def next_job(order: list[int] | None = None, data_dir: str = DATA, jobs_dir: str | None = None) -> Job | None:
    jobs_dir = jobs_dir or os.path.join(WORK, 'jobs')
    meta = chapter_meta()
    for surah in (order or ORDER):
        done, intro = published(surah, data_dir)
        if len(done) >= meta[surah]['verses'] and intro:
            continue
        for job in ensure_jobs(surah, jobs_dir):
            if job.kind == 'verses' and any(v not in done for v in job.verses):
                return job
            if job.kind == 'intro' and not intro:
                return job
    return None


def table(show_all: bool = False, data_dir: str = DATA) -> str:
    meta = chapter_meta()
    rows, total_pub, total_ok, total_flag = [], 0, 0, 0
    pending_shown = False
    for surah in ORDER:
        done, intro = published(surah, data_dir)
        n = meta[surah]['verses']
        ok = sum(1 for s in done.values() if s == 'ok')
        flag = len(done) - ok
        total_pub += len(done)
        total_ok += ok
        total_flag += flag
        complete = len(done) >= n and intro
        if done or show_all or (not complete and not pending_shown):
            state = 'done' if complete else ('partial' if done else 'next' if not pending_shown else '')
            if not complete and not pending_shown:
                pending_shown = True
                state = state or 'next'
            rows.append(f"{surah:>4}  {meta[surah]['name_en']:<16} {len(done):>4}/{n:<4} ok={ok:<4} flag={flag:<3} intro={'yes' if intro else 'no ':<3} {state}")
    head = 'surah name             published   ok     flag   intro  state'
    foot = f'total: {total_pub}/6236 verses published ({total_pub / 62.36:.1f}%), ok={total_ok}, flag={total_flag}'
    return '\n'.join([head] + rows + [foot])


def material_text(job: Job) -> str:
    parts = []
    for b in job.blocks:
        t = strip_arabic_lines(b.text).strip()
        extra = f'  shared with verses {b.shared_outside}' if b.shared_outside else ''
        parts.append(f"===== {b.source} ({b.range})  {word_count(t)} words{extra} =====\n{t}\n")
    return '\n'.join(parts)


def split_parts(text: str, chunk: int = CHUNK) -> list[str]:
    parts, cur = [], ''
    for para in text.split('\n'):
        if len(cur) + len(para) + 1 > chunk and cur:
            parts.append(cur)
            cur = ''
        cur += para + '\n'
    if cur.strip():
        parts.append(cur)
    return parts


def export_raw(surah: int, jobs_dir: str, raw_dir: str, data_dir: str = DATA) -> list[str]:
    """Rebuild work/raw/<job>.md from the published payload (the NOTES blocks are not stored
    in the payload, so a stub NOTES block says so)."""
    path = os.path.join(data_dir, f'guidance_{surah:03d}.json')
    if not os.path.exists(path):
        raise SystemExit(f'nothing published for surah {surah}')
    g = read_json(path)
    ensure_dir(raw_dir)
    written = []
    stamp = dt.date.today().isoformat()
    for job in ensure_jobs(surah, jobs_dir):
        out = []
        if job.kind == 'intro':
            if (g.get('intro') or '').strip():
                out.append(f"<<<INTRO {surah}>>>\n{g['intro'].strip()}\n<<<END>>>\n")
        else:
            for v in job.verses:
                e = (g.get('verses') or {}).get(str(v))
                if e and (e.get('text') or '').strip():
                    out.append(f"<<<VERSE {surah}:{v}>>>\n{e['text'].strip()}\n<<<END>>>\n")
        if not out:
            continue
        out.append(f"<<<NOTES>>>\n- reconstructed from data/guidance_{surah:03d}.json on {stamp}; the original NOTES block was not stored in the payload\n<<<END>>>\n")
        p = os.path.join(raw_dir, f'{job.id}.md')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('\n'.join(out))
        written.append(p)
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--all', action='store_true', help='list all 114 surahs')
    ap.add_argument('--next', action='store_true', help='print the next pending job')
    ap.add_argument('--show', action='store_true', help='with --next: print the full prompt for the job')
    ap.add_argument('--material', default=None, help='job id: print its material, Arabic lines stripped')
    ap.add_argument('--part', type=int, default=0, help='with --material: which part (1-based); 0 = part 1 plus the part count')
    ap.add_argument('--chunk', type=int, default=CHUNK)
    ap.add_argument('--export-raw', type=int, default=None, metavar='SURAH')
    ap.add_argument('--jobs', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--raw', default=os.path.join(WORK, 'raw'))
    ap.add_argument('--data-dir', default=DATA)
    args = ap.parse_args()

    if args.material:
        surah = int(args.material.split('-')[0])
        jobs = {j.id: j for j in ensure_jobs(surah, args.jobs)}
        if args.material not in jobs:
            print(f'job {args.material} not found (ids: {", ".join(sorted(jobs))})', file=sys.stderr)
            return 2
        parts = split_parts(material_text(jobs[args.material]), args.chunk)
        k = max(1, args.part)
        if k > len(parts):
            print(f'only {len(parts)} parts', file=sys.stderr)
            return 2
        print(f'--- material of {args.material}: part {k}/{len(parts)} ({len(parts[k - 1])} chars) ---')
        print(parts[k - 1])
        if len(parts) > 1 and k < len(parts):
            print(f'--- {len(parts) - k} more part(s): --material {args.material} --part {k + 1} ---')
        return 0

    if args.export_raw:
        for p in export_raw(args.export_raw, args.jobs, args.raw, args.data_dir):
            print('wrote', os.path.relpath(p))
        return 0

    if args.next:
        job = next_job(data_dir=args.data_dir, jobs_dir=args.jobs)
        if not job:
            print('nothing pending: every verse and introduction is published')
            return 0
        done, _ = published(job.surah, args.data_dir)
        todo = [v for v in job.verses if v not in done]
        mat = {v: int(job.material_words.get(v, 0)) for v in job.verses}
        print(f'next job: {job.id}  ({job.kind}, surah {job.surah})')
        if job.kind == 'verses':
            print(f'  verses in job: {job.verses}   still unpublished: {todo}')
            print(f'  material words per verse: {mat}   (target entry length is about 0.6 x material, never shorter than the material deserves)')
        print(f'  material: {sum(word_count(strip_arabic_lines(b.text)) for b in job.blocks)} words in {len(job.blocks)} blocks')
        print(f'  read it:  python3 tools/guidance/digest.py {job.id}            (then --part 2, 3 … until the last part)')
        print(f'  write:    work/raw/{job.id}.md')
        print(f'  finish:   python3 tools/guidance/finish.py {job.id}            (ingest, gates, assemble, commit, push, next)')
        if args.show:
            print('\n' + render_user(job))
        return 0

    print(table(args.all, args.data_dir))
    return 0


if __name__ == '__main__':
    sys.exit(main())
