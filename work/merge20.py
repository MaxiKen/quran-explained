#!/usr/bin/env python3
"""Batch 20 (Chapter 3 batch 4) merge: group files -> chapter_3_verse_61_80.md with QC validations."""
import json, re, sys, unicodedata

START, END = 61, 80
GROUPS = [
    "work/group_61_65.md",
    "work/group_66_70.md",
    "work/group_71_75.md",
    "work/group_76_80.md",
]
REFS = "work/references_61_80.md"
OUT = "chapter_3_verse_61_80.md"
JSON_PATH = "chapter_3_translation.json"

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)
items = data["verses"] if isinstance(data, dict) and "verses" in data else data
verses = {int(item["verse"]): item["translation"] for item in items}
missing = [n for n in range(START, END + 1) if n not in verses or not verses[n]]
if missing:
    sys.exit(f"Missing translations in JSON for: {missing}")

body = []
for g in GROUPS:
    with open(g, encoding="utf-8") as fh:
        body.append(fh.read().strip())

full = "\n\n".join(body + [open(REFS, encoding="utf-8").read().strip()]) + "\n"

failures = []

# 1. Sequential ## Verse N headings
heads = [int(h) for h in re.findall(r"^## Verse (\d+)$", full, re.M)]
if heads != list(range(START, END + 1)):
    failures.append(f"Heading sequence mismatch: got {heads[:5]}...{heads[-5:] if heads else []}")

# 2. Exactly one marker per verse, alone on its line
markers = re.findall(r"^(===VERSE-END===)$", full, re.M)
if len(markers) != END - START + 1:
    failures.append(f"Marker count {len(markers)} != {END - START + 1}")
for line in full.splitlines():
    if "===VERSE-END===" in line and line.strip() != "===VERSE-END===":
        failures.append("Marker not alone on its line: " + line[:60])
        break

# 3. Each translation verbatim, exactly once
for n in range(START, END + 1):
    t = verses[n]
    if t not in full:
        failures.append(f"Verse {n}: translation not found verbatim")
    elif full.count(t) != 1:
        failures.append(f"Verse {n}: translation appears {full.count(t)} times")

# 4. References last
rpos = full.find("## References")
if rpos == -1:
    failures.append("Missing ## References section")
else:
    last_marker = full.rindex("===VERSE-END===")
    if not (last_marker < rpos):
        failures.append("References not after last verse marker")

# 5. No banned metadata strings
banned = [
    "Stage 1:", "Stage 2:", "Stage 3:", "Stage 4:", "Stage 5:",
    "Generation log", "Workflow", "Table of contents", "## Overview",
    "<!--", "RUN 19", "RUN 20", "Source:", "Research notes", "TODO", "TBD",
    "not confirmed", "(? ", "??", "placeholder",
]
for b in banned:
    if b in full:
        failures.append(f"Banned string present: {b!r}")

# 6. No leftover proofreading flags
for flag in ['", meaning)', 'paraphrased")']:
    if flag in full:
        failures.append(f"Proofreading flag present: {flag!r}")

# 7. Normalized-repeat audit
def norm(s: str) -> str:
    s = s.replace("˹", "").replace("˺", "")
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).lower().strip()

seen = {}
dups = []
for para in re.split(r"\n\s*\n", full):
    n = norm(para)
    if len(n.split()) < 18:
        continue
    if n in seen:
        dups.append((seen[n], len(n.split()), n[:70]))
    else:
        seen[n] = len(n.split())
for a, b, c in dups:
    failures.append(f"Normalized repeat ({a} and {b} words): {c}")

# 8. Depth floor
body_only = full[:rpos] if rpos != -1 else full
blocks = re.split(r"^## Verse \d+\n", body_only, flags=re.M)
wv = [len(re.split(r"===VERSE-END===", b)[0].split()) for b in blocks[1:]]
if len(wv) == END - START + 1:
    thin = {START + i: w for i, w in enumerate(wv) if w < 600}
    if thin:
        failures.append(f"Thin verses (<600 words): {thin}")
else:
    failures.append(f"Verse block count mismatch: {len(wv)}")

if failures:
    print("MERGE FAILED:")
    for f in failures:
        print(" -", f)
    sys.exit(1)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(full)

words = len(full.split())
print(f"MERGE PASS -> {OUT}")
print(f"Verses: {END - START + 1}, markers: {len(markers)}, words: {words}")
print(f"Words/verse: {sum(wv)//len(wv)} (min {min(wv)})")
