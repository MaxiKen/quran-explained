#!/usr/bin/env python3
"""Run generation jobs against an LLM provider.

    python3 tools/guidance/generate.py --surahs 1,112 --provider anthropic --concurrency 8
    python3 tools/guidance/generate.py --shard 3 --provider openai --model gpt-5
    python3 tools/guidance/generate.py --surahs 1 --dry-run        # mock provider, no key

Inputs  work/jobs/NNN.json (from pack.py)
Outputs work/out/NNN/<job-id>.json, one per job, resumable: a job whose output
        exists and is not failed is skipped unless --force.

A job whose response is cut off (max tokens) or is missing a verse is retried
once; if it still fails, it is split into one job per verse with the same
material and each is run on its own.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK, Job, Block, ensure_dir, parse_surah_selection, read_prompt, load_guidance, read_json, read_text  # noqa: E402
from providers import make_provider, ProviderError  # noqa: E402

VERSE_RE = re.compile(r'<<<\s*VERSE\s+(\d+)\s*:\s*(\d+)\s*>>>\s*(.*?)\s*<<<\s*END\s*>>>', re.S)
INTRO_RE = re.compile(r'<<<\s*INTRO\s+(\d+)\s*>>>\s*(.*?)\s*<<<\s*END\s*>>>', re.S)
NOTES_RE = re.compile(r'<<<\s*NOTES\s*>>>\s*(.*?)\s*(?:<<<\s*END\s*>>>|\Z)', re.S)

_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


# --------------------------------------------------------------------------
# prompt rendering
# --------------------------------------------------------------------------
def load_system_prompt() -> str:
    system = read_prompt('system.md').rstrip() + '\n'
    exemplars = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts', 'exemplars', '*.md')))
    if exemplars:
        system += '\n# Example entries\n\nThese entries were written under these rules from material of the sizes given. Match their voice, shape and density. Do not copy their sentences.\n'
        for path in exemplars:
            system += '\n' + read_text(path).strip() + '\n'
    return system


def _verses_block(ayahs: list[dict], surah: int) -> str:
    out = []
    for a in ayahs:
        out.append(f'## {surah}:{a["n"]}\nArabic: {a["ar"]}\nTranslation: "{a["en"]}"')
        if a.get('theme'):
            out[-1] += f'\nPlace in the surah\'s outline: {a["theme"]}'
    return '\n\n'.join(out)


def _context_block(job: Job) -> str:
    if not job.context_before and not job.context_after:
        return ''
    lines = ['# Around these verses (for placement only, not to be written)', '']
    if job.context_before:
        lines.append('Before: ' + ' · '.join(f'{job.surah}:{a["n"]} "{a["en"]}"' for a in job.context_before))
    if job.context_after:
        lines.append('After: ' + ' · '.join(f'{job.surah}:{a["n"]} "{a["en"]}"' for a in job.context_after))
    return '\n'.join(lines) + '\n\n'


def _material_block(job: Job) -> str:
    parts = []
    for b in job.blocks:
        cover = b.range
        note = ''
        if b.shared_outside:
            inside = [v for v in b.verses if v in job.verses]
            note = (f'. This text also covers {job.surah}:{",".join(str(v) for v in b.shared_outside)}, written in another job: '
                    f'use only what concerns {job.surah}:{",".join(str(v) for v in inside)}')
        parts.append(f'## {b.label} (covers {cover}{note})\n\n{b.text}')
    return '\n\n'.join(parts)


def render_user(job: Job) -> str:
    meta = job.meta
    if job.kind == 'intro':
        themes = '\n'.join(f'- verses {t["verses"][0]}' + (f'-{t["verses"][-1]}' if len(t['verses']) > 1 else '')
                           + f': {t["description"]}' for t in job.themes)
        return read_prompt('intro_job.md').format(
            surah=job.surah, name_en=meta['name_en'], meaning=meta['meaning'], type=meta['type'],
            n_verses=meta['verses'], themes_block=themes,
            verses_block=_verses_block(job.ayahs, job.surah), material_block=_material_block(job))
    verse_list = ', '.join(f'{job.surah}:{v}' for v in job.verses)
    return read_prompt('verse_job.md').format(
        surah=job.surah, name_en=meta['name_en'], meaning=meta['meaning'], type=meta['type'],
        n_verses=meta['verses'], verse_list=verse_list,
        verses_block=_verses_block(job.ayahs, job.surah), context_block=_context_block(job),
        material_block=_material_block(job))


# --------------------------------------------------------------------------
# output parsing
# --------------------------------------------------------------------------
def parse_output(text: str) -> dict:
    verses = {}
    for m in VERSE_RE.finditer(text):
        verses[int(m.group(2))] = m.group(3).strip()
    intro = None
    im = INTRO_RE.search(text)
    if im:
        intro = im.group(2).strip()
    nm = NOTES_RE.search(text)
    notes = nm.group(1).strip() if nm else ''
    return {'verses': verses, 'intro': intro, 'notes': notes}


def _max_tokens_for(provider_name: str, model: str, requested: int) -> int:
    caps = {'anthropic': 64000, 'openai': 128000, 'gemini': 65536, 'mock': 1_000_000}
    return min(requested, caps.get(provider_name, requested))


# --------------------------------------------------------------------------
# running
# --------------------------------------------------------------------------
class Runner:
    def __init__(self, provider, system: str, out_dir: str, max_tokens: int, temperature: float):
        self.provider = provider
        self.system = system
        self.out_dir = out_dir
        self.max_tokens = _max_tokens_for(provider.name, provider.model, max_tokens)
        self.temperature = temperature
        self.usage = {'input': 0, 'cached': 0, 'output': 0, 'calls': 0}
        self.lock = threading.Lock()

    def _call(self, job: Job) -> tuple[dict, dict, str]:
        user = render_user(job)
        res = self.provider.complete(self.system, user, max_tokens=self.max_tokens, temperature=self.temperature)
        with self.lock:
            for k in ('input', 'cached', 'output'):
                self.usage[k] += res.usage.get(k, 0)
            self.usage['calls'] += 1
        return parse_output(res.text), res.usage, res.stop_reason

    def _complete(self, job: Job, parsed: dict, stop: str) -> list[str]:
        problems = []
        if stop == 'length':
            problems.append('response cut off at max tokens')
        if job.kind == 'intro':
            if not parsed.get('intro'):
                problems.append('no <<<INTRO>>> block')
        else:
            missing = [v for v in job.verses if v not in parsed['verses'] or not parsed['verses'][v]]
            if missing:
                problems.append('missing verses ' + ','.join(map(str, missing)))
            extra = [v for v in parsed['verses'] if v not in job.verses]
            if extra:
                problems.append('unexpected verses ' + ','.join(map(str, extra)))
        return problems

    def run(self, job: Job, *, attempts: int = 2) -> dict:
        started = time.time()
        record = {'job_id': job.id, 'kind': job.kind, 'surah': job.surah, 'verses': {}, 'intro': None,
                  'notes': '', 'provider': self.provider.name, 'model': self.provider.model,
                  'attempts': [], 'status': 'ok', 'created': dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z'}
        last_problems: list[str] = []
        for attempt in range(attempts):
            try:
                parsed, usage, stop = self._call(job)
            except ProviderError as e:
                record['attempts'].append({'error': str(e)[:500]})
                last_problems = [str(e)[:200]]
                continue
            problems = self._complete(job, parsed, stop)
            record['attempts'].append({'usage': usage, 'stop': stop, 'problems': problems})
            if not problems:
                record['verses'] = {str(k): v for k, v in parsed['verses'].items()}
                record['intro'] = parsed['intro']
                record['notes'] = parsed['notes']
                record['seconds'] = round(time.time() - started, 1)
                return record
            # keep whatever verses came back complete, in case the split below needs fewer calls
            for v, md in parsed['verses'].items():
                if v in job.verses and md and stop != 'length':
                    record['verses'].setdefault(str(v), md)
            last_problems = problems
        if job.kind == 'verses' and len(job.verses) > 1:
            # split into single-verse jobs, keeping the full material
            log(f'  {job.id}: splitting ({"; ".join(last_problems)})')
            for v in job.verses:
                if str(v) in record['verses']:
                    continue
                sub = Job(id=f'{job.id}#{v}', kind='verses', surah=job.surah, verses=[v],
                          blocks=[Block(source=b.source, label=b.label, range=b.range, verses=b.verses, text=b.text,
                                        shared_outside=[x for x in b.verses if x != v]) for b in job.blocks],
                          ayahs=[a for a in job.ayahs if a['n'] == v],
                          context_before=[a for a in job.ayahs if a['n'] < v][-2:] or job.context_before,
                          context_after=[a for a in job.ayahs if a['n'] > v][:2] or job.context_after,
                          meta=job.meta)
                sub_rec = self.run(sub, attempts=attempts)
                record['attempts'].append({'split': v, 'status': sub_rec['status']})
                if sub_rec['status'] == 'ok' and str(v) in sub_rec['verses']:
                    record['verses'][str(v)] = sub_rec['verses'][str(v)]
                    if sub_rec['notes'] and sub_rec['notes'].lower() != 'none':
                        record['notes'] += f'\n[{job.surah}:{v}] ' + sub_rec['notes']
            missing = [v for v in job.verses if str(v) not in record['verses']]
            record['status'] = 'ok' if not missing else 'failed'
            if missing:
                record['error'] = 'missing verses after split: ' + ','.join(map(str, missing))
        else:
            record['status'] = 'failed'
            record['error'] = '; '.join(last_problems)
        record['seconds'] = round(time.time() - started, 1)
        return record


def load_jobs(jobs_dir: str, surahs: list[int]) -> list[Job]:
    jobs = []
    for s in surahs:
        path = os.path.join(jobs_dir, f'{s:03d}.json')
        if not os.path.exists(path):
            continue
        for d in read_json(path):
            jobs.append(Job.from_json(d))
    return jobs


def already_published(job: Job) -> bool:
    g = load_guidance(job.surah)
    if not g:
        return False
    if job.kind == 'intro':
        return bool(g.get('intro'))
    verses = g.get('verses', {})
    return all(str(v) in verses and verses[str(v)].get('text') and verses[str(v)].get('status', 'ok') != 'fail'
               for v in job.verses)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--surahs', default=None, help="e.g. 1,112-114 or all")
    ap.add_argument('--shard', type=int, default=None, help='run the jobs of this shard from --shards-file')
    ap.add_argument('--shards-file', default=os.path.join(WORK, 'shards.json'))
    ap.add_argument('--jobs', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--out', default=os.path.join(WORK, 'out'))
    ap.add_argument('--provider', default=os.environ.get('GUIDANCE_PROVIDER', 'anthropic'))
    ap.add_argument('--model', default=os.environ.get('GUIDANCE_MODEL'))
    ap.add_argument('--concurrency', type=int, default=int(os.environ.get('GUIDANCE_CONCURRENCY', '6')))
    ap.add_argument('--max-tokens', type=int, default=32000)
    ap.add_argument('--temperature', type=float, default=0.4)
    ap.add_argument('--timeout', type=int, default=900)
    ap.add_argument('--limit', type=int, default=0, help='run at most N jobs (smoke tests)')
    ap.add_argument('--only', default=None, help='comma-separated job ids')
    ap.add_argument('--force', action='store_true', help='re-run jobs that already have output')
    ap.add_argument('--skip-published', action='store_true', help='skip jobs whose verses are already in data/guidance_NNN.json')
    ap.add_argument('--dry-run', action='store_true', help='use the mock provider')
    ap.add_argument('--show', default=None, help='print the rendered prompt for this job id and exit')
    args = ap.parse_args()

    if args.show:
        surah = int(args.show.split('-')[0])
        for j in load_jobs(args.jobs, [surah]):
            if j.id == args.show:
                print(render_user(j))
                return 0
        print(f'job {args.show} not found in {args.jobs}', file=sys.stderr)
        return 2

    provider_name = 'mock' if args.dry_run else args.provider
    provider = make_provider(provider_name, args.model, timeout=args.timeout)
    system = load_system_prompt()

    if args.shard is not None:
        shards = read_json(args.shards_file)
        wanted = set(shards[args.shard]['jobs'])
        surahs = sorted({int(j.split('-')[0]) for j in wanted})
        jobs = [j for j in load_jobs(args.jobs, surahs) if j.id in wanted]
    else:
        surahs = parse_surah_selection(args.surahs or 'all')
        jobs = load_jobs(args.jobs, surahs)
    if args.only:
        only = set(x.strip() for x in args.only.split(','))
        jobs = [j for j in jobs if j.id in only]

    todo = []
    for j in jobs:
        path = os.path.join(args.out, f'{j.surah:03d}', f'{j.id}.json')
        if not args.force and os.path.exists(path):
            try:
                if read_json(path).get('status') == 'ok':
                    continue
            except json.JSONDecodeError:
                pass
        if args.skip_published and already_published(j):
            continue
        todo.append(j)
    if args.limit:
        todo = todo[:args.limit]
    log(f'{len(todo)} jobs to run with {provider.name}/{provider.model}, concurrency {args.concurrency} '
        f'({len(jobs) - len(todo)} skipped as done)')
    if not todo:
        return 0

    runner = Runner(provider, system, args.out, args.max_tokens, args.temperature)
    started = time.time()
    done = failed = 0

    def work(job: Job):
        rec = runner.run(job)
        ensure_dir(os.path.join(args.out, f'{job.surah:03d}'))
        with open(os.path.join(args.out, f'{job.surah:03d}', f'{job.id}.json'), 'w', encoding='utf-8') as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        return rec

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        futures = {ex.submit(work, j): j for j in todo}
        for fut in as_completed(futures):
            job = futures[fut]
            try:
                rec = fut.result()
            except Exception as e:  # noqa: BLE001 — a crashed worker must not kill the run
                failed += 1
                log(f'  {job.id}: crashed: {e}')
                continue
            done += 1
            if rec['status'] != 'ok':
                failed += 1
            words = sum(len(t.split()) for t in rec['verses'].values()) + len((rec.get('intro') or '').split())
            elapsed = time.time() - started
            rate = done / elapsed * 60 if elapsed else 0
            log(f'[{done}/{len(todo)}] {job.id} {rec["status"]} {words}w {rec.get("seconds", 0)}s '
                f'· {rate:.1f} jobs/min · out {runner.usage["output"]/1e3:.0f}k tok')
    u = runner.usage
    log(f'done: {done - failed} ok, {failed} failed, {u["calls"]} calls, input {u["input"]/1e6:.2f}M '
        f'(cached {u["cached"]/1e6:.2f}M), output {u["output"]/1e6:.2f}M tokens, {(time.time()-started)/60:.1f} min')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
