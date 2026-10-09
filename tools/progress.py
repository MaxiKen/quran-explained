#!/usr/bin/env python3
"""Report authoring progress against the plan.

    python3 tools/progress.py            # summary
    python3 tools/progress.py --next     # what to author next, and how big
    python3 tools/progress.py 2          # detail for one surah
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_plan():
    return json.load(open(os.path.join(ROOT, 'data/plan.json'), encoding='utf-8'))


def authored():
    """{surah: set(ayah)} from the guidance files on disk."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'data/guidance_*.json'))):
        s = int(os.path.basename(f)[9:12])
        d = json.load(open(f, encoding='utf-8'))
        out[s] = {int(k) for k in d.get('verses', {})}
    return out


def main():
    plan = load_plan()
    auth = authored()
    args = [a for a in sys.argv[1:] if not a.startswith('-')]

    if args:
        s = int(args[0])
        have = auth.get(s, set())
        tot = sum(1 for k in plan if k.startswith(f'{s}:'))
        words = sum(len(json.load(open(os.path.join(ROOT, f'data/guidance_{s:03d}.json'),
                                    encoding='utf-8'))['verses'][str(a)]['text'].split())
                    for a in sorted(have)) if have else 0
        missing = [a for a in range(1, tot + 1) if a not in have]
        print(f'surah {s}: {len(have)}/{tot} verses authored, {words:,} words')
        if missing:
            runs, start, prev = [], None, None
            for a in missing:
                if start is None:
                    start = prev = a
                elif a == prev + 1:
                    prev = a
                else:
                    runs.append((start, prev)); start = prev = a
            if start is not None:
                runs.append((start, prev))
            print('  not yet: ' + ', '.join(
                f'{s}:{a}' if a == b else f'{s}:{a}-{b}' for a, b in runs))
        return 0

    done = sum(len(v) for v in auth.values())
    total = len(plan)
    done_words = 0
    plan_words = 0
    for k, v in plan.items():
        plan_words += v['words']
        s, a = map(int, k.split(':'))
        if a in auth.get(s, set()):
            done_words += v['words']
    print(f'verses authored: {done}/{total} ({100 * done / total:.2f}%)')
    print(f'planned words:   {done_words:,} of {plan_words:,} '
          f'({100 * done_words / plan_words:.2f}%)')
    print(f'remaining:       {plan_words - done_words:,} words')
    print(f'surahs touched:  {sorted(auth)}')

    if '--next' in sys.argv:
        print('\n=== next unauthored verse, and the size of its surah ===')
        for s in range(1, 115):
            have = auth.get(s, set())
            tot = sum(1 for k in plan if k.startswith(f'{s}:'))
            if len(have) < tot:
                nxt = min(a for a in range(1, tot + 1) if a not in have)
                rest = sum(plan[f'{s}:{a}']['words'] for a in range(1, tot + 1) if a not in have)
                print(f'  resume at {s}:{nxt}  ({tot - len(have)} verses left in surah {s}, '
                      f'{rest:,} planned words)')
                break
    return 0


if __name__ == '__main__':
    sys.exit(main())
