# Commentary harnesses

Each harness boots the real app in jsdom against a running static server and
asserts against what it actually renders — no logic is re-implemented here.

    python3 -m http.server 8000 --bind 0.0.0.0   # from the repo root
    npm i jsdom                                   # once, anywhere on NODE_PATH
    node tools/tests/sources-all.js               # six-source layer, full corpus
    node tools/tests/guidance-112.js              # authored layer, surah 112
    node tools/tests/guidance-001.js              # authored layer, surah 1
    node tools/tests/guidance-112.js              # 27 checks

`sources-all.js` covers all 114 payloads and the read-aloud path. The two
`guidance-*` harnesses each check that the authored layer loads, that every
verse is covered, that the commentary **quotes the app's own stored
translation wording**, that the guidance renders first with its range on the
first line, that the six classical texts fold behind a disclosure, and that a
surah with no guidance file yet still shows all six sources directly.

`guidance-001.js` adds two checks the others do not have:

- every verse's length is within 25% of the target `tools/tier_verses.py`
  assigned it in `data/plan.json`
- every narrator and collector named in the guidance appears in that verse's
  own source text, with diacritics folded away so that "Imām Aḥmad" matches
  the sources' "Imam Ahmad". The six tafsir titles are matched against the
  payload's `sources[].label` instead, since a work does not cite itself.
