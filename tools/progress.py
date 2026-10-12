#!/usr/bin/env python3
"""Report authoring progress against the plan — claim-aware, safe for parallel runs.

Several agents may work the commentary at the same time, on different chapters,
in any order. To keep their merges from overwriting one another, every agent

  1. claims its ranges here before writing a word, and
  2. records its batches in its own file, `data/runs/<agent>.json` — one file
     per agent, so parallel branches never edit the same bytes.

`docs/progress.md` is GENERATED (`--report`) from the data files and the run
files: it documents every run on record. On any merge conflict in it, re-run
`--report` on the merged tree and take the result.

    python3 tools/progress.py                      # summary
    python3 tools/progress.py 2                    # detail for one surah
    python3 tools/progress.py --next               # every open surah, resume point, claim status
    python3 tools/progress.py --next --agent NAME  # resume points inside NAME's claims
    python3 tools/progress.py --runs               # every run on record
    python3 tools/progress.py --claim 4:1-50 --agent NAME [--branch B] [--note T]
    python3 tools/progress.py --claim 5 --agent NAME          # a whole surah
    python3 tools/progress.py --batch 4:1-10 --agent NAME [--commit SHA] [--note T]
    python3 tools/progress.py --done 4:1-50 --agent NAME      # close a range
    python3 tools/progress.py --done --agent NAME             # close the whole run
    python3 tools/progress.py --check              # overlap + drift; exit 1 on a problem
    python3 tools/progress.py --report             # regenerate docs/progress.md

Claim rules (enforced here, detailed in docs/parallel.md):
  * a chapter has at most one open claim across all agents — `data/guidance_NNN.json`
    is one file per chapter, so two concurrent writers would merge-overwrite it;
  * a range may be any span of one surah (`4:1-50`, `4`, `4:7`); order across
    chapters is free — chapters need not be authored 1 → 114;
  * batches must land inside the agent's own open claims.
"""
import datetime
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(ROOT, 'data', 'runs')
REPORT_PATH = os.path.join(ROOT, 'docs', 'progress.md')
RUN_KEYS = ['agent', 'branch', 'status', 'claimed', 'updated', 'ranges', 'batches', 'notes']


def today():
    return datetime.date.today().isoformat()


# ---------------------------------------------------------------- data loaders

def load_plan():
    return json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))


def authored():
    """{surah: {ayah: text}} from the guidance files on disk."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'guidance_*.json'))):
        s = int(os.path.basename(f)[9:12])
        d = json.load(open(f, encoding='utf-8'))
        out[s] = {int(k): v.get('text', '') for k, v in d.get('verses', {}).items()}
    return out


def load_runs():
    """{agent: run-dict} from data/runs/*.json — one file per agent."""
    out = {}
    for f in sorted(glob.glob(os.path.join(RUNS_DIR, '*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        agent = d.get('agent') or os.path.basename(f)[:-5]
        d.setdefault('ranges', [])
        d.setdefault('batches', [])
        d.setdefault('notes', '')
        d['_file'] = os.path.relpath(f, ROOT)
        d['_stem'] = os.path.basename(f)[:-5]
        out[agent] = d
    return out


def save_run(run):
    stem = re.sub(r'[^A-Za-z0-9._-]+', '-', run['agent']).strip('-') or 'run'
    run['updated'] = today()
    body = {k: run[k] for k in RUN_KEYS if k in run}
    body.setdefault('batches', [])
    body.setdefault('ranges', [])
    body.setdefault('notes', '')
    os.makedirs(RUNS_DIR, exist_ok=True)
    path = os.path.join(RUNS_DIR, stem + '.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(body, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    return path


# ---------------------------------------------------------------- range plumbing

def parse_ref(ref):
    """'4' -> (4, 1, inf) later clipped; '4:7' -> (4, 7, 7); '4:1-50' -> (4, 1, 50)."""
    m = re.fullmatch(r'(\d+)(?::(\d+)(?:-(\d+))?)?', ref.strip())
    if not m:
        raise SystemExit(f'bad range {ref!r} — use 4, 4:7 or 4:1-50')
    s = int(m.group(1))
    lo = int(m.group(2)) if m.group(2) else 1
    hi = int(m.group(3)) if m.group(3) else (int(m.group(2)) if m.group(2) else None)
    return s, lo, hi


def clip_ref(ref, plan):
    s, lo, hi = parse_ref(ref)
    tot = sum(1 for k in plan if k.startswith(f'{s}:'))
    if not tot:
        raise SystemExit(f'surah {s} is not in data/plan.json')
    if hi is None:
        hi = tot
    if not (1 <= lo <= hi <= tot):
        raise SystemExit(f'{ref} is out of range — surah {s} has 1-{tot}')
    return s, lo, hi


def fmt_ref(s, lo, hi):
    return f'{s}:{lo}' if lo == hi else f'{s}:{lo}-{hi}'


def merge_intervals(items):
    """[{surah, lo, hi, done}] -> same, with overlapping/adjacent intervals of
    equal done-ness merged. Deterministic order: surah, then lo."""
    out = []
    for key in sorted({(r['surah'], bool(r.get('done'))) for r in items}):
        s, done = key
        ivs = sorted((r['lo'], r['hi']) for r in items
                     if r['surah'] == s and bool(r.get('done')) == done)
        lo, hi = ivs[0]
        for a, b in ivs[1:]:
            if a <= hi + 1:
                hi = max(hi, b)
            else:
                out.append(dict(surah=s, lo=lo, hi=hi, done=done))
                lo, hi = a, b
        out.append(dict(surah=s, lo=lo, hi=hi, done=done))
    return out


def open_ranges(runs, agent=None):
    """[(agent, surah, lo, hi)] for claims not yet closed."""
    out = []
    for a, run in runs.items():
        if agent and a != agent:
            continue
        if run.get('status') == 'done':
            continue
        for r in run['ranges']:
            if not r.get('done'):
                out.append((a, r['surah'], r['lo'], r['hi']))
    return out


def all_ranges(runs):
    """[(agent, r)] every range on record, open or closed."""
    return [(a, r) for a, run in runs.items() for r in run['ranges']]


def covers(ranges, s, a):
    return any(r['surah'] == s and r['lo'] <= a <= r['hi'] for r in ranges)


def conflicts_for(s, lo, hi, runs, agent):
    """Open claims by ANOTHER agent on this surah — the merge-unsafe case.

    Even a disjoint span is refused: `data/guidance_NNN.json` is one file per
    chapter, so two concurrent writers would merge-overwrite each other there."""
    return [(a, fmt_ref(rs, rlo, rhi)) for a, rs, rlo, rhi in open_ranges(runs)
            if a != agent and rs == s]


# ---------------------------------------------------------------- CLI pieces

def opt(argv, name):
    if name in argv:
        i = argv.index(name)
        if i + 1 >= len(argv):
            raise SystemExit(f'{name} needs a value')
        return argv[i + 1]
    return None


def refs_after(argv, flag):
    """Positional refs between `flag` and the next --flag (option values skipped)."""
    out = []
    skip = False
    for a in argv[argv.index(flag) + 1:]:
        if skip:
            skip = False
            continue
        if a in ('--agent', '--branch', '--commit', '--note'):
            skip = True
            continue
        if a.startswith('--'):
            break
        out.append(a)
    return out


def require_agent(argv):
    agent = opt(argv, '--agent')
    if not agent:
        raise SystemExit('--agent NAME is required (the name of your data/runs/<agent>.json)')
    if not re.fullmatch(r'[A-Za-z0-9._-]+', agent):
        raise SystemExit('--agent must be letters, digits, dot, underscore or dash')
    return agent


def get_run(runs, agent, branch=None, note=None):
    run = runs.get(agent)
    if run is None:
        run = dict(agent=agent, branch=branch or '', status='in-progress',
                   claimed=today(), updated=today(), ranges=[], batches=[],
                   notes=note or '')
        runs[agent] = run
    else:
        if branch:
            run['branch'] = branch
        if note and not run.get('notes'):
            run['notes'] = note
    return run


def cmd_summary(argv):
    plan = load_plan()
    auth = authored()
    runs = load_runs()
    skip = False
    args = []
    for a in argv:
        if skip:
            skip = False
            continue
        if a in ('--agent', '--branch', '--commit', '--note'):
            skip = True
            continue
        if a.startswith('-'):
            continue
        args.append(a)

    if args:
        s = int(args[0])
        have = auth.get(s, {})
        tot = sum(1 for k in plan if k.startswith(f'{s}:'))
        words = sum(len(t.split()) for t in have.values())
        missing = [a for a in range(1, tot + 1) if a not in have]
        print(f'surah {s}: {len(have)}/{tot} verses authored, {words:,} words')
        for a, r in all_ranges(runs):
            if r['surah'] == s:
                state = 'done' if r.get('done') or runs[a].get('status') == 'done' else 'open'
                print(f'  claim {a}: {fmt_ref(s, r["lo"], r["hi"])} ({state})')
        if missing:
            runs_, start, prev = [], None, None
            for a in missing:
                if start is None:
                    start = prev = a
                elif a == prev + 1:
                    prev = a
                else:
                    runs_.append((start, prev)); start = prev = a
            if start is not None:
                runs_.append((start, prev))
            print('  not yet: ' + ', '.join(
                f'{s}:{a}' if a == b else f'{s}:{a}-{b}' for a, b in runs_))
        return 0

    done = sum(len(v) for v in auth.values())
    total = len(plan)
    done_words = 0
    plan_words = 0
    for k, v in plan.items():
        plan_words += v['words']
        s, a = map(int, k.split(':'))
        if a in auth.get(s, {}):
            done_words += v['words']
    print(f'verses authored: {done}/{total} ({100 * done / total:.2f}%)')
    print(f'planned words:   {done_words:,} of {plan_words:,} '
          f'({100 * done_words / plan_words:.2f}%)')
    print(f'remaining:       {plan_words - done_words:,} words')
    print(f'surahs touched:  {sorted(auth)}')

    if '--next' in sys.argv:
        agent = opt(argv, '--agent')
        print()
        if agent:
            print(f'=== open claims for {agent} ===')
            mine = [(s, lo, hi) for a, s, lo, hi in open_ranges(runs) if a == agent]
            if not mine:
                print('  none — claim work with: '
                      f'python3 tools/progress.py --claim SURAH:LO-HI --agent {agent}')
            for s, lo, hi in mine:
                have = auth.get(s, {})
                tot = sum(1 for k in plan if k.startswith(f'{s}:'))
                missing = [a for a in range(lo, hi + 1) if a not in have]
                nxt = missing[0] if missing else None
                rest = sum(plan[f'{s}:{a}']['words'] for a in missing)
                if nxt:
                    flag = ''
                    if plan.get(f'{s}:{nxt}', {}).get('authored_only'):
                        flag = '  [AUTHORED-ONLY — compose, do not compile]'
                    print(f'  {fmt_ref(s, lo, hi)}: resume at {s}:{nxt}  '
                          f'({len(missing)} verses left in this claim, {rest:,} planned words){flag}')
                else:
                    print(f'  {fmt_ref(s, lo, hi)}: complete on disk — close it with --done')
            thin = [(s, a) for s, lo, hi in mine for a in range(lo, hi + 1)
                    if a not in auth.get(s, {})
                    and plan.get(f'{s}:{a}', {}).get('authored_only')]
            if thin:
                print('  authored-only still open in your claims: '
                      + ', '.join(f'{s}:{a}' for s, a in thin))
            return 0

        print('=== open work, every surah with verses left (order is free) ===')
        claimed_by = {}
        for a, s, lo, hi in open_ranges(runs):
            claimed_by.setdefault(s, []).append((a, lo, hi))
        for s in range(1, 115):
            have = auth.get(s, {})
            tot = sum(1 for k in plan if k.startswith(f'{s}:'))
            if len(have) >= tot:
                continue
            nxt = min(a for a in range(1, tot + 1) if a not in have)
            missing = [a for a in range(1, tot + 1) if a not in have]
            rest = sum(plan[f'{s}:{a}']['words'] for a in missing)
            thin = sum(1 for a in missing if plan.get(f'{s}:{a}', {}).get('authored_only'))
            who = claimed_by.get(s, [])
            tag = ('  [claimed: ' + ', '.join(f'{a} {fmt_ref(s, lo, hi)}'
                                              for a, lo, hi in who) + ']') if who else '  (unclaimed)'
            flag = ''
            if plan.get(f'{s}:{nxt}', {}).get('authored_only'):
                flag = '  [next is AUTHORED-ONLY]'
            elif thin:
                flag = f'  [{thin} authored-only in surah]'
            print(f'  surah {s:3d}: resume at {s}:{nxt:<3d}  '
                  f'{tot - len(have):4d} verses left, {rest:>9,} planned words{flag}{tag}')
    return 0


def cmd_runs(argv=None):
    runs = load_runs()
    auth = authored()
    plan = load_plan()
    if not runs:
        print('no runs on record — create one with --claim … --agent NAME')
        return 0
    for agent in sorted(runs):
        run = runs[agent]
        print(f'{agent}  [{run.get("status", "in-progress")}]  '
              f'branch={run.get("branch") or "?"}  '
              f'claimed={run.get("claimed", "?")}  updated={run.get("updated", "?")}  '
              f'({run["_file"]})')
        if not run['ranges']:
            print('  (no ranges claimed)')
        for r in run['ranges']:
            s, lo, hi = r['surah'], r['lo'], r['hi']
            in_range = [a for a in range(lo, hi + 1) if a in auth.get(s, {})]
            words = sum(len(auth[s][a].split()) for a in in_range)
            tot = hi - lo + 1
            state = 'done' if r.get('done') else 'open'
            print(f'  {fmt_ref(s, lo, hi):12s} {state:4s}  '
                  f'{len(in_range)}/{tot} verses on disk, {words:,} words')
        for b in run['batches']:
            extra = '  ' + b['commit'][:9] if b.get('commit') else ''
            note = f'  — {b["note"]}' if b.get('note') else ''
            print(f'    batch {b.get("date", "?")}  {fmt_ref(b["surah"], b["lo"], b["hi"])}'
                  f'{extra}{note}')
        if run.get('notes'):
            print(f'  notes: {run["notes"]}')
        print()
    return 0


def cmd_claim(argv):
    agent = require_agent(argv)
    refs = refs_after(argv, '--claim')
    if not refs:
        raise SystemExit('--claim needs at least one range: 4:1-50, 4, …')
    plan = load_plan()
    runs = load_runs()
    run = get_run(runs, agent, branch=opt(argv, '--branch'), note=opt(argv, '--note'))
    added = []
    for ref in refs:
        s, lo, hi = clip_ref(ref, plan)
        for other, oref in conflicts_for(s, lo, hi, runs, agent):
            print(f'REFUSED {fmt_ref(s, lo, hi)}: surah {s} has an open claim by '
                  f'{other} ({oref}). One chapter has one open claim at a time, because '
                  f'data/guidance_{s:03d}.json is a single file — wait for that run to '
                  f'--done, or take a different surah.')
            return 1
        for r in run['ranges']:
            if r.get('done') and r['surah'] == s and not (hi < r['lo'] or lo > r['hi']):
                print(f'  note: {fmt_ref(s, lo, hi)} overlaps a closed claim '
                      f'{fmt_ref(s, r["lo"], r["hi"])} of yours — re-authoring is recorded as a new claim')
        run['ranges'].append(dict(surah=s, lo=lo, hi=hi, done=False))
        added.append(fmt_ref(s, lo, hi))
    run['ranges'] = merge_intervals(run['ranges'])
    if run.get('status') == 'done':
        run['status'] = 'in-progress'
    path = save_run(run)
    print(f'claimed {", ".join(added)} for {agent} → {os.path.relpath(path, ROOT)}')
    print('remember: commit and push this file with every batch, so other runs see the claim.')
    return 0


def cmd_batch(argv):
    agent = require_agent(argv)
    refs = refs_after(argv, '--batch')
    if len(refs) != 1:
        raise SystemExit('--batch takes exactly one range')
    s, lo, hi = clip_ref(refs[0], load_plan())
    runs = load_runs()
    run = runs.get(agent)
    if run is None:
        raise SystemExit(f'no run file for {agent} — --claim first')
    inside = any((not r.get('done')) and r['surah'] == s and r['lo'] <= lo and hi <= r['hi']
                 for r in run['ranges'])
    if not inside:
        print(f'REFUSED: {fmt_ref(s, lo, hi)} is not inside an open claim of {agent}. '
              f'Claim it before authoring: --claim {fmt_ref(s, lo, hi)} --agent {agent}')
        return 1
    batch = dict(surah=s, lo=lo, hi=hi, date=today())
    commit = opt(argv, '--commit')
    note = opt(argv, '--note')
    if commit:
        batch['commit'] = commit
    if note:
        batch['note'] = note
    run['batches'].append(batch)
    path = save_run(run)
    print(f'recorded batch {fmt_ref(s, lo, hi)} for {agent} → {os.path.relpath(path, ROOT)}')
    return 0


def cmd_done(argv):
    agent = require_agent(argv)
    refs = refs_after(argv, '--done')
    plan = load_plan()
    runs = load_runs()
    run = runs.get(agent)
    if run is None:
        raise SystemExit(f'no run file for {agent}')
    note = opt(argv, '--note')
    if not refs:
        for r in run['ranges']:
            r['done'] = True
        run['status'] = 'done'
        closed = ['all open ranges']
    else:
        closed = []
        for ref in refs:
            s, lo, hi = clip_ref(ref, plan)
            updated, hit = [], False
            for r in run['ranges']:
                if r.get('done') or r['surah'] != s or hi < r['lo'] or lo > r['hi']:
                    updated.append(r)
                    continue
                hit = True
                # keep any part of the claim outside [lo, hi] open; the covered
                # part becomes a closed record
                if lo > r['lo']:
                    updated.append(dict(surah=s, lo=r['lo'], hi=lo - 1, done=False))
                if hi < r['hi']:
                    updated.append(dict(surah=s, lo=hi + 1, hi=r['hi'], done=False))
                updated.append(dict(surah=s, lo=max(lo, r['lo']), hi=min(hi, r['hi']), done=True))
            if not hit:
                print(f'{fmt_ref(s, lo, hi)} is not an open claim of {agent} — nothing closed')
                continue
            run['ranges'] = updated
            closed.append(fmt_ref(s, lo, hi))
        run['ranges'] = merge_intervals(run['ranges'])
        if not any(not r.get('done') for r in run['ranges']):
            run['status'] = 'done'
    if note:
        run['notes'] = (run.get('notes', '') + f'\n{today()}: {note}').strip()
    path = save_run(run)
    print(f'closed {", ".join(closed)} for {agent} → {os.path.relpath(path, ROOT)}')
    return 0


def cmd_check(argv=None):
    runs = load_runs()
    auth = authored()
    plan = load_plan()
    errors, warnings = [], []

    # 1. one open claim per chapter, across agents
    per_surah = {}
    for a, s, lo, hi in open_ranges(runs):
        per_surah.setdefault(s, []).append((a, lo, hi))
    for s, holders in sorted(per_surah.items()):
        agents = {a for a, _, _ in holders}
        if len(agents) > 1:
            detail = ', '.join(f'{a} {fmt_ref(s, lo, hi)}' for a, lo, hi in holders)
            errors.append(f'surah {s} has open claims from several agents: {detail}')

    # 2. overlapping open ranges within one agent
    for agent, run in runs.items():
        ivs = [(r['surah'], r['lo'], r['hi']) for r in run['ranges'] if not r.get('done')]
        for i, (s1, l1, h1) in enumerate(ivs):
            for s2, l2, h2 in ivs[i + 1:]:
                if s1 == s2 and not (h1 < l2 or h2 < l1):
                    errors.append(f'{agent} has overlapping open claims '
                                  f'{fmt_ref(s1, l1, h1)} and {fmt_ref(s2, l2, h2)}')

    # 3. filename hygiene
    for agent, run in runs.items():
        if run['_stem'] != agent:
            warnings.append(f'{run["_file"]} declares agent {agent!r} — rename the file to match')

    # 4. verses on disk that no run record covers
    claimed = [r for _, r in all_ranges(runs)]
    orphans = {s: [a for a in sorted(verses) if not covers(claimed, s, a)]
               for s, verses in auth.items()}
    for s, lst in sorted(orphans.items()):
        if lst:
            warnings.append(f'{len(lst)} verse(s) of surah {s} on disk are outside every '
                            f'run record (e.g. {s}:{lst[0]}) — claim them retroactively with '
                            f'--claim … --agent <the run that wrote them>')

    # 5. closed claims whose verses are not all on disk
    for agent, run in runs.items():
        for r in run['ranges']:
            if not r.get('done') and run.get('status') != 'done':
                continue
            missing = [a for a in range(r['lo'], r['hi'] + 1)
                       if a not in auth.get(r['surah'], {})]
            if missing:
                warnings.append(f'{agent} closed {fmt_ref(r["surah"], r["lo"], r["hi"])} but '
                                f'{len(missing)} verse(s) are absent (e.g. {r["surah"]}:{missing[0]})')

    # 6. floor sanity over everything authored
    short = []
    for s, verses in auth.items():
        for a, text in verses.items():
            p = plan.get(f'{s}:{a}', {})
            floor = p.get('floor', int(round(p.get('words', 800) * 0.75)))
            if len(text.split()) < floor:
                short.append(f'{s}:{a}')
    if short:
        warnings.append(f'{len(short)} verse(s) under their floor: '
                        + ', '.join(short[:8]) + (' …' if len(short) > 8 else ''))

    for e in errors:
        print('ERROR  ' + e)
    for w in warnings:
        print('warn   ' + w)
    if not errors and not warnings:
        print(f'check ok — {len(runs)} run(s), '
              f'{sum(len(v) for v in auth.values())} verses, no problems')
    elif not errors:
        print(f'check ok with {len(warnings)} warning(s)')
    return 1 if errors else 0


def cmd_report(argv=None):
    plan = load_plan()
    auth = authored()
    runs = load_runs()
    total = len(plan)
    done = sum(len(v) for v in auth.values())
    done_words = 0
    plan_words = 0
    disk_words = 0
    short = 0
    for k, v in plan.items():
        plan_words += v['words']
        s, a = map(int, k.split(':'))
        text = auth.get(s, {}).get(a)
        if text is not None:
            done_words += v['words']
            disk_words += len(text.split())
            floor = v.get('floor', int(round(v['words'] * 0.75)))
            if len(text.split()) < floor:
                short += 1

    L = []
    L.append('<!-- GENERATED FILE — do not edit by hand.')
    L.append('     python3 tools/progress.py --report   regenerates it from data/plan.json,')
    L.append('     data/guidance_*.json and data/runs/*.json. On a merge conflict here,')
    L.append('     re-run the command on the merged tree and commit the result.')
    L.append('     Narrative logs live in docs/runs/; per-run records in data/runs/. -->')
    L.append('')
    L.append('# Progress')
    L.append('')
    L.append(f'Generated {today()} by `tools/progress.py --report`.')
    L.append('')
    L.append('## Corpus')
    L.append('')
    L.append('| | |')
    L.append('|---|---|')
    L.append(f'| Verses authored | **{done:,} of {total:,}** ({100 * done / total:.2f}%) |')
    L.append(f'| Planned words written | **{done_words:,}** of {plan_words:,} '
             f'({100 * done_words / plan_words:.2f}%) |')
    L.append(f'| Words on disk | {disk_words:,} (every verse at or over its floor: '
             f'{"yes" if not short else f"NO — {short} short"}) |')
    L.append(f'| Remaining | {plan_words - done_words:,} planned words |')
    L.append('| Source sets | 8 (six complete + al-Qushayrī 1,287 + al-Wāḥidī 431) |')
    L.append(f'| Runs on record | {len(runs)} |')
    L.append('')
    L.append('`tools/progress.py --next` is authoritative for where to resume; '
             '`tools/progress.py --runs` lists every run. Chapters need **not** be '
             'authored in order — see [`parallel.md`](parallel.md).')
    L.append('')

    # ---- chapters on record
    touched = set(auth) | {r['surah'] for _, r in all_ranges(runs)}
    if touched:
        L.append('## Chapters on record')
        L.append('')
        L.append('| chapter | on disk | planned words on disk | claims |')
        L.append('|---|---|---|---|')
        for s in sorted(touched):
            have = auth.get(s, {})
            tot = sum(1 for k in plan if k.startswith(f'{s}:'))
            w = sum(len(t.split()) for t in have.values())
            cl = []
            for a, r in all_ranges(runs):
                if r['surah'] != s:
                    continue
                state = 'done' if r.get('done') or runs[a].get('status') == 'done' else 'open'
                cl.append(f'{a} {fmt_ref(s, r["lo"], r["hi"])} ({state})')
            if have or cl:
                L.append(f'| {s} | {len(have)}/{tot} | {w:,} | '
                         f'{"; ".join(cl) if cl else "—"} |')
        L.append('')

    # ---- runs: every agent, one section each
    L.append('## Runs — every agent on record')
    L.append('')
    if not runs:
        L.append('*(none yet — `python3 tools/progress.py --claim … --agent NAME` creates one)*')
        L.append('')
    for agent in sorted(runs):
        run = runs[agent]
        L.append(f'### {agent} — {run.get("status", "in-progress")}')
        L.append('')
        L.append(f'*branch* `{run.get("branch") or "?"}` · *claimed* {run.get("claimed", "?")} '
                 f'· *updated* {run.get("updated", "?")} · *record* [`{run["_file"]}`](../{run["_file"]})')
        L.append('')
        if run['ranges']:
            L.append('| range | state | verses on disk | words on disk |')
            L.append('|---|---|---|---|')
            for r in run['ranges']:
                s, lo, hi = r['surah'], r['lo'], r['hi']
                in_range = [a for a in range(lo, hi + 1) if a in auth.get(s, {})]
                w = sum(len(auth[s][a].split()) for a in in_range)
                state = 'done' if r.get('done') else 'open'
                L.append(f'| {fmt_ref(s, lo, hi)} | {state} | '
                         f'{len(in_range)}/{hi - lo + 1} | {w:,} |')
            L.append('')
        if run['batches']:
            L.append('Batches:')
            L.append('')
            for b in run['batches']:
                extra = f' — `{b["commit"][:9]}`' if b.get('commit') else ''
                note = f' — {b["note"]}' if b.get('note') else ''
                L.append(f'- {b.get("date", "?")} · {fmt_ref(b["surah"], b["lo"], b["hi"])}'
                         f'{extra}{note}')
            L.append('')
        if run.get('notes'):
            L.append('> ' + run['notes'].replace('\n', '\n> '))
            L.append('')

    # ---- open work, out of order by design
    claimed_by = {}
    for a, s, lo, hi in open_ranges(runs):
        claimed_by.setdefault(s, []).append((a, lo, hi))
    L.append('## Open work — all surahs with verses left (order is free)')
    L.append('')
    L.append('| surah | resume at | verses left | planned words left | authored-only | claim |')
    L.append('|---|---|---|---|---|---|')
    for s in range(1, 115):
        have = auth.get(s, {})
        tot = sum(1 for k in plan if k.startswith(f'{s}:'))
        if len(have) >= tot:
            continue
        missing = [a for a in range(1, tot + 1) if a not in have]
        nxt = missing[0]
        rest = sum(plan[f'{s}:{a}']['words'] for a in missing)
        thin = sum(1 for a in missing if plan.get(f'{s}:{a}', {}).get('authored_only'))
        who = claimed_by.get(s, [])
        tag = ', '.join(f'{a} {fmt_ref(s, lo, hi)}' for a, lo, hi in who) if who else 'unclaimed'
        L.append(f'| {s} | {s}:{nxt} | {len(missing)} | {rest:,} | '
                 f'{thin or "—"} | {tag} |')
    L.append('')

    # ---- the merge contract, restated where it is read
    L.append('## Why parallel merges do not overwrite each other')
    L.append('')
    L.append('- **Data**: `data/guidance_NNN.json` is one file per chapter and a chapter '
             'has at most one open claim (`tools/progress.py --check` enforces it). A merge '
             'only ever brings the chapters its run owns.')
    L.append('- **Runs**: each agent edits only its own `data/runs/<agent>.json`. '
             'Claims and batch logs merge as whole, disjoint files.')
    L.append('- **This file**: generated. Never hand-edit it; on conflict, re-run '
             '`python3 tools/progress.py --report` and take the result.')
    L.append('- **Cache version**: `sw-stamps.js` is append-only (one stamp per landed '
             'batch) and marked `merge=union` in `.gitattributes`, so stamps concatenate '
             'instead of colliding.')
    L.append('- **Tests**: `tools/tests/guidance-NNN.js` is per chapter and added by its '
             'owner; `guidance-range.js` discovers payloads on its own and needs no edits.')
    L.append('')
    L.append('The full protocol is [`parallel.md`](parallel.md).')
    L.append('')

    with open(REPORT_PATH, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))
    print(f'wrote {os.path.relpath(REPORT_PATH, ROOT)} — '
          f'{done}/{total} verses, {len(runs)} run(s)')
    return 0


def main():
    argv = sys.argv[1:]
    if '--report' in argv:
        return cmd_report()
    if '--check' in argv:
        return cmd_check()
    if '--runs' in argv:
        return cmd_runs()
    if '--claim' in argv:
        return cmd_claim(argv)
    if '--batch' in argv:
        return cmd_batch(argv)
    if '--done' in argv:
        return cmd_done(argv)
    return cmd_summary(argv)


if __name__ == '__main__':
    sys.exit(main())
