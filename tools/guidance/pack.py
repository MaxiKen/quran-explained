#!/usr/bin/env python3
"""Build generation jobs from the eight-source payloads.

    python3 tools/guidance/pack.py --surahs all            # work/jobs/*.json
    python3 tools/guidance/pack.py --surahs 1,112-114 --estimate
    python3 tools/guidance/pack.py --surahs all --shards 8 # + work/shards.json

A job is a run of consecutive verses whose source blocks overlap (Ibn Kathīr,
Maʿārif and Tazkīrul comment on ranges), capped at MAX_JOB_VERSES verses /
MAX_JOB_CHARS characters so one request can write all of its entries in a
single response. Every surah also gets one `intro` job.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (WORK, MAX_JOB_CHARS, MAX_JOB_VERSES, build_jobs, ensure_dir,  # noqa: E402
                    parse_surah_selection)

# USD per million tokens, list prices as of mid-2026 — check your provider's
# current sheet before trusting a number here; the estimate is for planning.
PRICES = {
    'claude-sonnet-4-5':   (3.00, 15.00),
    'claude-haiku-4-5':    (1.00, 5.00),
    'gpt-5':               (1.25, 10.00),
    'gpt-5-mini':          (0.25, 2.00),
    'gemini-2.5-pro':      (1.25, 10.00),
    'gemini-2.5-flash':    (0.30, 2.50),
}
# Output is proportional to the material: measured against the hand-written
# exemplars the rewrite runs at roughly 0.55 output tokens per source token
# (the Arabic quotations and the chains of transmitters drop out, overlapping
# glosses merge, plain English is a little longer per idea).
OUTPUT_RATIO = 0.6
SYSTEM_PROMPT_TOKENS = 9_000   # style guide + exemplars; cached after the first call


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--surahs', default='all')
    ap.add_argument('--out', default=os.path.join(WORK, 'jobs'))
    ap.add_argument('--max-verses', type=int, default=MAX_JOB_VERSES)
    ap.add_argument('--max-chars', type=int, default=MAX_JOB_CHARS)
    ap.add_argument('--strip-arabic', action='store_true', help='drop mostly-Arabic lines from the material (~15%% fewer input tokens)')
    ap.add_argument('--no-intro', action='store_true')
    ap.add_argument('--shards', type=int, default=0, help='also write work/shards.json balancing jobs into N shards')
    ap.add_argument('--estimate', action='store_true', help='print token and cost estimates and exit without writing')
    args = ap.parse_args()

    surahs = parse_surah_selection(args.surahs)
    total_jobs = total_verses = total_in = 0
    biggest = (0, '')
    per_surah = {}
    all_jobs = []
    for s in surahs:
        jobs = build_jobs(s, max_verses=args.max_verses, max_chars=args.max_chars,
                          strip_arabic=args.strip_arabic, with_intro=not args.no_intro)
        per_surah[s] = jobs
        for j in jobs:
            total_jobs += 1
            total_verses += len(j.verses)
            total_in += j.est_tokens
            if j.est_tokens > biggest[0]:
                biggest = (j.est_tokens, j.id)
            all_jobs.append(j)

    out_tokens = int(total_in * OUTPUT_RATIO)
    print(f'surahs: {len(surahs)}  jobs: {total_jobs}  verses: {total_verses}')
    print(f'material: ~{total_in/1e6:.2f}M input tokens (largest job {biggest[1]} ≈ {biggest[0]:,} tokens)')
    print(f'expected output: ~{out_tokens/1e6:.2f}M tokens (≈ {out_tokens*0.75/1e6:.2f}M words, '
          f'{out_tokens*0.75/max(1,total_verses):.0f} words per verse on average)')
    if args.estimate:
        print()
        print(f'{"model":<20}{"generation":>12}{"+ audit on all":>16}{"batch (-50%)":>14}')
        for model, (pin, pout) in PRICES.items():
            # every call carries the system prompt; providers cache it at ~10% of price
            sys_cost = total_jobs * SYSTEM_PROMPT_TOKENS * pin * 0.1 / 1e6
            gen = total_in * pin / 1e6 + out_tokens * pout / 1e6 + sys_cost
            # audit re-reads material + draft and writes a short ledger; repair rewrites ~25% of verses
            audit = (total_in + out_tokens) * pin / 1e6 + 0.15 * out_tokens * pout / 1e6 \
                + 0.25 * (total_in * pin / 1e6 + out_tokens * pout / 1e6)
            print(f'{model:<20}{gen:>11.0f}${gen+audit:>15.0f}${(gen+audit)/2:>13.0f}$')
        return 0

    ensure_dir(args.out)
    for s, jobs in per_surah.items():
        path = os.path.join(args.out, f'{s:03d}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([j.to_json() for j in jobs], f, ensure_ascii=False)
    print(f'wrote {len(per_surah)} job files to {args.out}')

    if args.shards > 0:
        # longest-processing-time first, balanced by estimated tokens
        shards = [{'id': i, 'jobs': [], 'tokens': 0} for i in range(args.shards)]
        for j in sorted(all_jobs, key=lambda j: -j.est_tokens):
            sh = min(shards, key=lambda x: x['tokens'])
            sh['jobs'].append(j.id)
            sh['tokens'] += j.est_tokens
        path = os.path.join(WORK, 'shards.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(shards, f)
        print('shards: ' + ', '.join(f'#{s["id"]}={len(s["jobs"])} jobs/{s["tokens"]/1e3:.0f}k tok' for s in shards))
    return 0


if __name__ == '__main__':
    sys.exit(main())
