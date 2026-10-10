# Commentary harnesses

Each harness boots the real app in jsdom against a running static server and
asserts against what it actually renders — no logic is re-implemented here.

    python3 tools/serve.py 8090                   # no-store preview/test server
    npm i jsdom --prefix /tmp/apptest
    export NODE_PATH=/tmp/apptest/node_modules
    export BASE=http://127.0.0.1:8090
    node tools/tests/sources-all.js               # eight-source layer, full corpus
    node tools/tests/guidance-001.js              # authored layer, surah 1
    node tools/tests/guidance-002.js              # authored layer, surah 2 (partial)

`sources-all.js` covers all 114 payloads and the read-aloud path. The two
`guidance-*` harnesses each check that the authored layer loads, that every
verse is covered, that the commentary **quotes the app's own stored
translation wording**, that the guidance renders first with its range on the
first line, that the six classical texts fold behind a disclosure, and that a
surah with no guidance file yet still shows all six sources directly.

`guidance-002.js` covers a **partially authored** surah: verses 1-8 carry
guidance, while verses 9, 100 and 286 are asserted to yield no guidance and
to fall back to the six sources directly with the first one marked primary.
The ebook is asserted to carry guidance on exactly the eight authored verses.
Its `HI`, translation pairs, authority list, and fallback list move at each batch boundary.

`guidance-001.js` and `guidance-002.js` add two checks the others do not have:

- every verse's length **meets the floor** set by `tools/tier_verses.py` in
  `data/plan.json` — 75% of the verse's target. Running long is fine; running
  short fails. The maintainer set this on 2026-10-09, reversing an earlier
  two-sided 25% band
- every narrator and collector named in the guidance appears in that verse's
  own source text, with diacritics folded away so that "Imām Aḥmad" matches
  the sources' "Imam Ahmad". Two names carry a romanisation variant
  (Ibn Marduwayh / Ibn Marduwyah, Murrah al-Hamadhani / al-Hamadani) and are
  matched against both spellings. Where the prose cites a neighbouring verse's
  entry — "recorded by Ibn Kathir at 2:4" — that verse's sources are folded
  into the blob. The six tafsir titles are matched against the payload's
  `sources[].label` instead, since a work does not cite itself.
