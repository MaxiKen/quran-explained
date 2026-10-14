#!/usr/bin/env python3
"""LLM coverage audit and repair.

    python3 tools/guidance/audit.py --surahs 1 --provider anthropic              # flagged entries only
    python3 tools/guidance/audit.py --surahs all --provider anthropic --all      # every entry (the "max" tier)
    python3 tools/guidance/audit.py --surahs 1 --dry-run                         # mock

For each entry: the auditor lists every substantive point in the material and
marks it covered / partial / missing, plus any unsupported statement and any
rule violation. If the verdict is "repair", the repair prompt rewrites the
entry with the findings, the deterministic gates run again, and the new text
replaces the old one in work/out when it is no worse. Up to --rounds rounds.

The audit model can differ from the generation model (--model); a cheaper
model is fine for the ledger, the repair should use the generation model.
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
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import WORK, Job, parse_surah_selection, read_prompt, load_chapter, read_json  # noqa: E402
from providers import make_provider, ProviderError  # noqa: E402
from generate import _verses_block, _material_block, load_system_prompt, VERSE_RE  # noqa: E402
from verify import verify_entries, collect_outputs  # noqa: E402

_lock = threading.Lock()


def log(msg):
    with _lock:
        print(msg, flush=True)


def _json_from(text: str) -> dict | None:
    m = re.search(r'\{.*\}', text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        # tolerate trailing commas
        try:
            return json.loads(re.sub(r',\s*([}\]])', r'\1', m.group(0)))
        except json.JSONDecodeError:
            return None


def _rank(status: str) -> int:
    return {'ok': 0, 'flag': 1, 'fail': 2}[status]


class Auditor:
    def __init__(self, auditor, repairer, system: str, rounds: int, max_tokens: int):
        self.intro_context: dict[int, str | None] = {}
        self.siblings: dict[int, dict[int, str]] = {}
        self.auditor = auditor
        self.repairer = repairer
        self.system = system
        self.rounds = rounds
        self.max_tokens = max_tokens
        self.usage = {'input': 0, 'output': 0, 'calls': 0}

    def _use(self, res):
        with _lock:
            self.usage['input'] += res.usage.get('input', 0)
            self.usage['output'] += res.usage.get('output', 0)
            self.usage['calls'] += 1

    def audit_once(self, job: Job, verse: int, entry: str) -> dict | None:
        ref = f'{job.surah}:{verse}'
        prompt = read_prompt('audit.md').format(
            ref=ref, verses_block=_verses_block([a for a in job.ayahs if a['n'] == verse], job.surah),
            material_block=_material_block(job), entry=entry)
        res = self.auditor.complete('You audit commentary entries against their material and answer in JSON only.',
                                    prompt, max_tokens=min(self.max_tokens, 16000), temperature=0.0)
        self._use(res)
        if self.auditor.name == 'mock':
            return {'points': [], 'unsupported': [], 'violations': [], 'verdict': 'pass'}
        return _json_from(res.text)

    def repair_once(self, job: Job, verse: int, entry: str, findings: dict) -> str | None:
        ref = f'{job.surah}:{verse}'
        missing = [p for p in findings.get('points', []) if p.get('covered') in ('no', 'partial')]
        prompt = read_prompt('repair.md').format(
            ref=ref, verses_block=_verses_block([a for a in job.ayahs if a['n'] == verse], job.surah),
            material_block=_material_block(job), entry=entry,
            missing_block='\n'.join(f'- [{p.get("covered")}] {p.get("point")}' for p in missing) or '- none',
            unsupported_block='\n'.join(f'- {u}' for u in findings.get('unsupported', [])) or '- none',
            violations_block='\n'.join(f'- {v}' for v in findings.get('violations', [])) or '- none')
        res = self.repairer.complete(self.system, prompt, max_tokens=self.max_tokens, temperature=0.3)
        self._use(res)
        m = VERSE_RE.search(res.text)
        if not m or res.stop_reason == 'length':
            return None
        return m.group(3).strip()

    def process(self, job: Job, out: dict, verse: int, translations: dict, report: dict) -> dict:
        entry = out['verses'][str(verse)]
        history = []
        for rnd in range(self.rounds):
            try:
                findings = self.audit_once(job, verse, entry)
            except ProviderError as e:
                history.append({'round': rnd, 'error': str(e)[:300]})
                break
            if not findings:
                history.append({'round': rnd, 'error': 'auditor returned no JSON'})
                break
            n_missing = sum(1 for p in findings.get('points', []) if p.get('covered') == 'no')
            n_partial = sum(1 for p in findings.get('points', []) if p.get('covered') == 'partial')
            summary = {'round': rnd, 'points': len(findings.get('points', [])), 'missing': n_missing,
                       'partial': n_partial, 'unsupported': len(findings.get('unsupported', [])),
                       'violations': len(findings.get('violations', [])), 'verdict': findings.get('verdict')}
            needs = findings.get('verdict') == 'repair' or n_missing or n_partial > 1 \
                or findings.get('unsupported') or findings.get('violations') or report['status'] == 'fail'
            if not needs:
                history.append({**summary, 'action': 'pass'})
                break
            try:
                new = self.repair_once(job, verse, entry, findings)
            except ProviderError as e:
                history.append({**summary, 'error': str(e)[:300]})
                break
            if not new:
                history.append({**summary, 'action': 'repair returned nothing usable'})
                break
            trial = dict(out['verses'])
            trial[str(verse)] = new
            rep = verify_entries(job.surah, {int(k): v for k, v in trial.items()}, [b.__dict__ for b in job.blocks],
                                 translations, intro_context=self.intro_context.get(job.surah),
                                 siblings=self.siblings.get(job.surah))['verses'][verse]
            if _rank(rep['status']) <= _rank(report['status']) and rep['coverage'] >= report['coverage'] - 0.02:
                history.append({**summary, 'action': 'repaired', 'status': rep['status'], 'coverage': rep['coverage']})
                entry = new
                report = rep
                out['verses'][str(verse)] = new
            else:
                history.append({**summary, 'action': 'repair rejected by gates', 'gate_errors': rep['errors'][:5]})
                break
        out.setdefault('audit', {})[str(verse)] = {'when': dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
                                                   'auditor': self.auditor.model, 'history': history}
        return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--surahs', default='all')
    ap.add_argument('--jobs', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--out', default=os.path.join(WORK, 'out'))
    ap.add_argument('--provider', default=os.environ.get('GUIDANCE_PROVIDER', 'anthropic'))
    ap.add_argument('--model', default=os.environ.get('GUIDANCE_MODEL'), help='repair model (defaults to provider default)')
    ap.add_argument('--audit-model', default=os.environ.get('GUIDANCE_AUDIT_MODEL'), help='auditor model (defaults to --model)')
    ap.add_argument('--all', action='store_true', help='audit every entry, not only flagged/failed ones')
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--concurrency', type=int, default=int(os.environ.get('GUIDANCE_CONCURRENCY', '6')))
    ap.add_argument('--max-tokens', type=int, default=32000)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    name = 'mock' if args.dry_run else args.provider
    repairer = make_provider(name, args.model)
    auditor = make_provider(name, args.audit_model or args.model)
    system = load_system_prompt()
    aud = Auditor(auditor, repairer, system, args.rounds, args.max_tokens)

    tasks = []
    for s in parse_surah_selection(args.surahs):
        job_path = os.path.join(args.jobs, f'{s:03d}.json')
        if not os.path.exists(job_path):
            continue
        jobs = {j['id']: Job.from_json(j) for j in read_json(job_path)}
        translations = {int(k): v['en'] for k, v in load_chapter(s)['verses'].items()}
        aud.intro_context[s], aud.siblings[s] = collect_outputs(args.out, s)
        for path in sorted(glob.glob(os.path.join(args.out, f'{s:03d}', '*.json'))):
            out = read_json(path)
            job = jobs.get(out['job_id'])
            if not job or job.kind != 'verses' or out.get('status') != 'ok':
                continue
            entries = {int(k): v for k, v in out['verses'].items()}
            reports = verify_entries(s, entries, [b.__dict__ for b in job.blocks], translations,
                                     intro_context=aud.intro_context[s], siblings=aud.siblings[s])['verses']
            for v, rep in reports.items():
                if args.all or rep['status'] != 'ok':
                    tasks.append((path, job, out, v, translations, rep))
    if args.limit:
        tasks = tasks[:args.limit]
    log(f'{len(tasks)} entries to audit with {auditor.name}/{auditor.model} (repair with {repairer.model})')
    if not tasks:
        return 0

    # group by output file so concurrent writers never touch the same file
    by_file: dict[str, list] = {}
    for t in tasks:
        by_file.setdefault(t[0], []).append(t)

    def work(path, group):
        out = group[0][2]
        job = group[0][1]
        for _, _, _, v, translations, rep in group:
            out = aud.process(job, out, v, translations, rep)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        return path, [out['audit'][str(v)]['history'][-1] for _, _, _, v, _, _ in group]

    repaired = passed = other = 0
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        futs = {ex.submit(work, p, g): p for p, g in by_file.items()}
        for fut in as_completed(futs):
            try:
                path, results = fut.result()
            except Exception as e:  # noqa: BLE001
                log(f'  {futs[fut]}: crashed: {e}')
                continue
            for r in results:
                a = r.get('action', '')
                if a == 'repaired':
                    repaired += 1
                elif a == 'pass':
                    passed += 1
                else:
                    other += 1
            log(f'  {os.path.basename(path)}: ' + ', '.join(r.get('action', r.get('error', '?'))[:40] for r in results))
    u = aud.usage
    log(f'audit done: {passed} passed, {repaired} repaired, {other} unresolved · {u["calls"]} calls, '
        f'{u["input"]/1e6:.2f}M in / {u["output"]/1e6:.2f}M out')
    return 0


if __name__ == '__main__':
    sys.exit(main())
