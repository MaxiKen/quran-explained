#!/usr/bin/env python3
"""Build a per-verse index from the committed tafsir-ibn-kathir/*.txt source.

Replaces the earlier index that read the rejected SafhaJournal corpus. This one
reads only files under tafsir-ibn-kathir/, which are the cleaned
spa5k/tafsir_api records committed in 9faa9ee.
"""
import re, json, pathlib

SRC = pathlib.Path("/home/user/quran-explained/tafsir-ibn-kathir")
OUT = pathlib.Path("/tmp/ik_idx.json")

def build():
    idx = {}
    for f in sorted(SRC.glob("[0-9][0-9][0-9].txt")):
        ch = int(f.stem)
        t = f.read_text(encoding="utf-8")
        parts = re.split(r"^## (\d+:\d+)\s*$", t, flags=re.M)
        rec = {}
        for i in range(1, len(parts), 2):
            ref, body = parts[i], parts[i+1]
            v = int(ref.split(":")[1])
            rec[v] = re.sub(r"\s+", " ", body).strip()
        idx[ch] = rec
    json.dump(idx, open(OUT, "w"))
    n = sum(len(v) for v in idx.values())
    print(f"surahs: {len(idx)}  verses: {n}  -> {OUT} ({OUT.stat().st_size//1024//1024} MB)")
    return idx

if __name__ == "__main__":
    build()
