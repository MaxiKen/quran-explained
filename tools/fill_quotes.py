#!/usr/bin/env python3
"""Fill the app's own `> ` verse line into a compiled spec, so nobody transcribes it.

    python3 tools/fill_quotes.py /home/user/proto/b006.md      # edits in place

A hand-written spec quotes the translation in two places: the `> ` line (which the
compiler validates the lead against) and the `~` lead (which has to quote every phrase
of it, in order). Typing the `> ` line is the one step in the loop with no gate on it —
a mistranscribed word there fails as a *coverage* error three steps later and sends you
looking at the wrong file. This inserts the exact string from the chapter data instead.

Idempotent: a `### s:a` already followed by a `> ` line is left alone.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_verse as VV  # noqa: E402


def fill(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    out, i, added = [], 0, 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        m = re.match(r'^### (\d+):(\d+)\s*$', ln)
        if m:
            s, a = int(m.group(1)), int(m.group(2))
            nxt = lines[i + 1] if i + 1 < len(lines) else ''
            if not nxt.startswith('> '):
                out.append('> ' + VV.chapter(s)[a]['ayah_en'])
                added += 1
        i += 1
    open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return added, len(re.findall(r'^### ', '\n'.join(out), re.M))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        added, heads = fill(p)
        print(f'{p}: {heads} verse blocks, {added} `> ` lines inserted')
