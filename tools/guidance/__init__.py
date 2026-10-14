"""Plain-English commentary pipeline for Quran Explained.

Stages (each is a CLI; see README.md in this folder):

    pack      data/tafsir_NNN.json + data/chapter_NNN.js  ->  work/jobs/*.json
    generate  work/jobs/*.json  + an LLM provider          ->  work/out/*.json
    verify    work/out/*.json   (deterministic gates)      ->  work/reports/*.json
    audit     flagged entries   + an LLM provider          ->  repaired work/out/*.json
    assemble  work/out/*.json                               ->  data/guidance_NNN.json

Everything here is standard-library Python 3.11+. There are no SDK
dependencies: the three provider adapters speak plain HTTPS.
"""
