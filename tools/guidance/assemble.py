#!/usr/bin/env python3
"""Assemble data/guidance_NNN.json from the job outputs.

    python3 tools/guidance/assemble.py --surahs 1,112          # merge into existing files
    python3 tools/guidance/assemble.py --surahs all --replace  # rebuild the files from work/out only

Every entry is re-run through the deterministic gates on the way in and
carries its status (ok | flag) and coverage. Entries that fail a gate are left
out (and listed) unless --include-failed is given. The file is written as one
line, like the tafsir payloads, and the app reads it as it is.

Payload shape (what js/app.js renders):
    { surah, lang, dir, title, label, generated: {date, model, pipeline},
      intro: markdown | null,
      verses: { "n": { text, draws_on: [source ids], words, status, coverage } } }
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DATA, WORK, SOURCE_ORDER, chapter_meta, load_chapter, load_tafsir, load_guidance,  # noqa: E402
                    parse_surah_selection, word_count, read_json, read_text)
from verify import verify_entries, collect_outputs  # noqa: E402

PIPELINE_VERSION = '1.0'
LABEL = 'Plain-English commentary'


def draws_on(tafsir: dict, verse: int) -> list[str]:
    m = tafsir['verses'].get(str(verse), {})
    return [sid for sid in SOURCE_ORDER if isinstance(m.get(sid), int)]


def assemble_surah(surah: int, out_dir: str, jobs_dir: str, *, replace: bool, include_failed: bool,
                   data_dir: str | None = None) -> tuple[dict, Counter]:
    meta = chapter_meta()[surah]
    tafsir = load_tafsir(surah)
    translations = {int(k): v['en'] for k, v in load_chapter(surah)['verses'].items()}
    job_path = os.path.join(jobs_dir, f'{surah:03d}.json')
    jobs = {j['id']: j for j in read_json(job_path)} if os.path.exists(job_path) else {}

    existing = None if replace else load_guidance(surah, data_dir)
    payload = {
        'surah': surah, 'lang': 'en', 'dir': 'ltr', 'title': meta['name_en'], 'label': LABEL,
        'generated': {'date': dt.date.today().isoformat(), 'model': None, 'pipeline': PIPELINE_VERSION},
        'intro': (existing or {}).get('intro'),
        'verses': dict((existing or {}).get('verses', {})),
    }
    counts = Counter()
    models = Counter()
    intro_out, siblings = collect_outputs(out_dir, surah)
    intro_context = intro_out or payload['intro']
    # entries already published for the surah count as siblings too (merge runs)
    for k, v in (existing or {}).get('verses', {}).items():
        siblings.setdefault(int(k), v.get('text', ''))
    for path in sorted(glob.glob(os.path.join(out_dir, f'{surah:03d}', '*.json'))):
        out = read_json(path)
        if out.get('status') != 'ok':
            counts['job_failed'] += 1
            continue
        job = jobs.get(out['job_id'])
        if not job:
            # a split sub-job or an output without its job file: still usable
            counts['no_job'] += 1
            continue
        models[out.get('model') or '?'] += 1
        if job['kind'] == 'intro':
            if out.get('intro'):
                rep = verify_entries(surah, {}, job['blocks'], translations, intro=out['intro'])['intro']
                if rep['status'] == 'fail' and not include_failed:
                    counts['intro_failed'] += 1
                    print(f'  {surah}:intro failed: ' + '; '.join(rep['errors']))
                else:
                    payload['intro'] = out['intro']
                    counts['intro'] += 1
            continue
        entries = {int(k): v for k, v in out.get('verses', {}).items() if v}
        rep = verify_entries(surah, entries, job['blocks'], translations, intro_context=intro_context,
                             siblings=siblings)['verses']
        for v, md in entries.items():
            r = rep[v]
            if r['status'] == 'fail' and not include_failed:
                counts['fail'] += 1
                print(f'  {surah}:{v} left out: ' + '; '.join(r['errors']))
                continue
            payload['verses'][str(v)] = {
                'text': md,
                'draws_on': draws_on(tafsir, v),
                'words': word_count(md),
                'status': r['status'],
                'coverage': r['coverage'],
            }
            counts[r['status']] += 1
    if models:
        payload['generated']['model'] = ', '.join(sorted(models))
    elif existing and existing.get('generated'):
        payload['generated'] = existing['generated']
    # keep verses in numeric order so diffs stay readable
    payload['verses'] = {k: payload['verses'][k] for k in sorted(payload['verses'], key=int)}
    return payload, counts


def seed_exemplars(data_dir: str | None = None) -> list[str]:
    """Publish the hand-written exemplars in prompts/exemplars/ as real
    entries, so they can be read in the app before any model run. Each file
    is named SSS_VVV.md and verified against the verse's own blocks."""
    from generate import parse_output  # local import: generate imports nothing from here
    from verify import blocks_for_surah
    exdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts', 'exemplars')
    written = []
    by_surah: dict[int, dict[int, str]] = {}
    for path in sorted(glob.glob(os.path.join(exdir, '*.md'))):
        parsed = parse_output(read_text(path))
        surah = int(os.path.basename(path).split('_')[0])
        for v, md in parsed['verses'].items():
            by_surah.setdefault(surah, {})[v] = md
    for surah, entries in by_surah.items():
        meta = chapter_meta()[surah]
        tafsir = load_tafsir(surah)
        translations = {int(k): v['en'] for k, v in load_chapter(surah)['verses'].items()}
        existing = load_guidance(surah, data_dir) or {}
        payload = {
            'surah': surah, 'lang': 'en', 'dir': 'ltr', 'title': meta['name_en'], 'label': LABEL,
            'generated': {'date': dt.date.today().isoformat(), 'model': 'hand-written exemplar',
                          'pipeline': PIPELINE_VERSION},
            'intro': existing.get('intro'),
            'verses': dict(existing.get('verses', {})),
        }
        for v, md in entries.items():
            # names and claims are checked against everything that touches the
            # verse; coverage only against the blocks that belong to it alone
            # (shared range material lives in the sibling entries)
            touching = [b for b in blocks_for_surah(surah) if v in b['verses']]
            own = [b for b in touching if b['verses'] == [v]] or touching
            r_all = verify_entries(surah, {v: md}, touching, translations)['verses'][v]
            errors = [e for e in r_all['errors'] if not e.startswith('coverage')]
            if errors:
                raise SystemExit(f'exemplar {surah}:{v} fails its own gates: {errors}')
            r_own = verify_entries(surah, {v: md}, own, translations)['verses'][v]
            payload['verses'][str(v)] = {
                'text': md, 'draws_on': draws_on(tafsir, v), 'words': word_count(md),
                'status': 'ok' if r_own['coverage'] >= 0.85 and not r_own['warnings'] else 'flag',
                'coverage': r_own['coverage'],
            }
        payload['verses'] = {k: payload['verses'][k] for k in sorted(payload['verses'], key=int)}
        written.append(write_payload(payload, data_dir))
    return written


def write_payload(payload: dict, data_dir: str | None = None) -> str:
    path = os.path.join(data_dir or DATA, f'guidance_{payload["surah"]:03d}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
        f.write('\n')
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--surahs', default='all')
    ap.add_argument('--out', default=os.path.join(WORK, 'out'))
    ap.add_argument('--jobs', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--replace', action='store_true', help='ignore the existing guidance file instead of merging into it')
    ap.add_argument('--include-failed', action='store_true')
    ap.add_argument('--data-dir', default=DATA, help='where guidance_NNN.json files live (default data/)')
    ap.add_argument('--seed-exemplars', action='store_true',
                    help='publish the hand-written exemplars from prompts/exemplars/ and exit')
    args = ap.parse_args()
    if args.seed_exemplars:
        for path in seed_exemplars(args.data_dir):
            print(f'wrote {os.path.relpath(path)}')
        return 0
    total = Counter()
    written = 0
    for s in parse_surah_selection(args.surahs):
        if not glob.glob(os.path.join(args.out, f'{s:03d}', '*.json')):
            continue
        payload, counts = assemble_surah(s, args.out, args.jobs, replace=args.replace,
                                         include_failed=args.include_failed, data_dir=args.data_dir)
        if not payload['verses'] and not payload['intro']:
            continue
        path = write_payload(payload, args.data_dir)
        written += 1
        total.update(counts)
        n = chapter_meta()[s]['verses']
        print(f'surah {s:>3}: {len(payload["verses"])}/{n} verses{" + intro" if payload["intro"] else ""} '
              f'-> {os.path.relpath(path)} ({os.path.getsize(path)/1024:.0f} KB)')
    print(f'{written} files written · entries ok={total["ok"]} flag={total["flag"]} '
          f'left out (fail)={total["fail"]} intro={total["intro"]} failed jobs={total["job_failed"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
