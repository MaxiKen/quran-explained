#!/usr/bin/env python3
"""Batch 7 merge: group files -> chapter_2_verse_121_140.md with QC validations."""
import json, re, sys

START, END = 121, 140
GROUPS = [
    "work/group_121_125.md",
    "work/group_126_130.md",
    "work/group_131_135.md",
    "work/group_136_140.md",
]
REFS = "work/references_121_140.md"
OUT = "chapter_2_verse_121_140.md"
JSON_PATH = "chapter_2_translation.json"

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
    "<!--", "RUN 8", "Source:", "Research notes",
]
for b in banned:
    if b in full:
        failures.append(f"Banned metadata string present: {b!r}")

# 6. No leftover flags from earlier proofreading
for flag in ['", meaning)"', 'paraphrased")']:
    if flag in full:
        failures.append(f"Proofreading flag present: {flag!r}")

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
