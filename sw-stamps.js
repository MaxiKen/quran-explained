// sw-stamps.js — APPEND-ONLY. Read by sw.js through importScripts().
//
// Parallel runs each land their own lines here, so this file is marked
// `merge=union` in .gitattributes: git concatenates both sides' additions
// instead of forcing one to overwrite the other. The rules:
//
//   * add ONE line per landed batch (RUN_STAMPS) or rewritten payload
//     (RETIRED_PAYLOADS); never edit or delete anyone else's line;
//   * keep every line syntactically valid on its own — union merge only
//     preserves lines, it does not understand JavaScript;
//   * the whole file must stay parseable: each entry is one quoted string
//     with a trailing comma, always.
//
// CACHE_VERSION in sw.js is derived from RUN_STAMPS.join('-'), so a stale
// browser cache is invalidated whenever any run lands new content — without
// every run fighting over a single version constant.

const RUN_STAMPS = [
  'v1.6.9-3-200', // 2026-10-12: chapters 1-3 complete, serial era (see docs/runs/serial-era.md)
  'ch7-1-10-2026-10-12-agent-68ef593f',
  // agents append below, one line per landed batch, e.g.:
  // 'ch4-1-10-2026-10-12-agent-a',
];

// Payloads a run rewrote or cleared. Dropped from every cache when the new
// version activates (data is fetched network-first; this only clears copies an
// older version already left behind). Append-only, same rules as above.
const RETIRED_PAYLOADS = [
  './data/guidance_001.json', // rewritten twice since 2026-10-09
  './data/guidance_002.json', // rewritten twice since 2026-10-09
  // agents append below, e.g. './data/guidance_004.json',
];
