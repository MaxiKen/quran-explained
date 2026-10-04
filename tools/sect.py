#!/usr/bin/env python3
"""Per-verse section extractor for the tafsir corpora.

Usage:
  python3 sect.py sizes [S:]V [S:]V ...
  python3 sect.py show <verse> [src ...]        # verse in surah 2 unless S:V given
  python3 sect.py showc <verse> <src> <a> <b>   # chars [a:b) of the section
Sources: tabari qurtubi ibnkathir jalalayn saadi maarif study

Works whether the script sits outside the repo (e.g. /home/user/sect.py, with the repo
as its sibling) or inside it (e.g. <repo>/tools/sect.py). The repo is located by
searching for the corpora directory.
"""
import re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))


def _find_repo():
    cands = [
        os.path.join(ROOT, 'quran-explained'),  # script outside repo, repo as sibling
        ROOT,                                    # script at repo root or in tools/
        os.path.dirname(ROOT),                   # script in a subdirectory of the repo
    ]
    for c in cands:
        if os.path.isdir(os.path.join(c, 'tafsir-al-tabari')):
            return c
    return cands[0]


REPO = _find_repo()

SRC_PATHS = {
    'tabari':    ('tafsir-al-tabari', 'txt'),
    'qurtubi':   ('tafsir-al-qurtubi', 'txt'),
    'ibnkathir': ('tafsir-ibn-kathir', 'txt'),
    'jalalayn':  ('tafsir-al-jalalayn', 'txt'),
    'saadi':     ('tafsir-as-saadi', 'txt'),
    'maarif':    ('tafsir-maarif-ul-quran', 'txt'),
    'study':     ('tafsir_initial', 'md'),
}

_cache = {}


def _arabic_sections(path, surah):
    text = open(path, encoding='utf-8').read()
    parts = re.split(r'(?m)^#{1,4}\s*(\d+):(\d+)\s*$', text)
    out = {}
    # parts: [pre, s, v, body, s, v, body, ...]
    for i in range(1, len(parts) - 2, 3):
        s, v, body = parts[i], parts[i + 1], parts[i + 2]
        out[f"{s}:{v}"] = body.strip('\n')
    return out


def _study_sections(path, surah):
    text = open(path, encoding='utf-8').read()
    chunks = text.split('\n***\n')
    out = {}
    cur_key, buf = None, []
    for ch in chunks:
        m = re.match(r'\s*> \*\*(\d+)\*\*', ch)
        if m:
            if cur_key:
                out[cur_key] = '\n***\n'.join(buf).strip('\n')
            cur_key = f"{surah}:{m.group(1)}"
            buf = [ch]
        elif cur_key:
            buf.append(ch)
    if cur_key:
        out[cur_key] = '\n***\n'.join(buf).strip('\n')
    return out


def sections(src, surah=2):
    key = (src, surah)
    if key in _cache:
        return _cache[key]
    d, ext = SRC_PATHS[src]
    path = os.path.join(REPO, d, f'{surah:03d}.{ext}')
    if src == 'study':
        secs = _study_sections(path, surah)
    else:
        secs = _arabic_sections(path, surah)
    _cache[key] = secs
    return secs


def _parse_v(tok, default_surah=2):
    if ':' in tok:
        s, v = tok.split(':')
        return int(s), int(v)
    return default_surah, int(tok)


def cmd_sizes(args):
    verses = [_parse_v(a) for a in args]
    srcs = list(SRC_PATHS)
    print(f"{'verse':>8}" + ''.join(f"{s:>11}" for s in srcs))
    for s, v in verses:
        row = f"{s}:{v:<6}"
        for src in srcs:
            sec = sections(src, s).get(f"{s}:{v}")
            row += f"{(len(sec) if sec else 0):>11}"
        print(row)


def cmd_show(args):
    if not args:
        return
    s, v = _parse_v(args[0])
    srcs = args[1:] or list(SRC_PATHS)
    for src in srcs:
        sec = sections(src, s).get(f"{s}:{v}") or ''
        print(f"\n########## {src} {s}:{v} ({len(sec)} chars) ##########\n{sec}")


def cmd_showc(args):
    s, v = _parse_v(args[0])
    src = args[1]
    a = int(args[2]) if len(args) > 2 else 0
    b = int(args[3]) if len(args) > 3 else 2000
    sec = sections(src, s).get(f"{s}:{v}") or ''
    print(f"##### {src} {s}:{v} [{a}:{b}] of {len(sec)} #####")
    print(sec[a:b])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'sizes':
        cmd_sizes(args)
    elif cmd == 'show':
        cmd_show(args)
    elif cmd == 'showc':
        cmd_showc(args)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
