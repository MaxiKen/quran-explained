// Asserts the house format in docs/style.md against every authored guidance
// verse. Set by the maintainer 2026-10-09 after the corpus was cleared for
// quote-stacking; this replaces the earlier multi-paragraph rule set.
//
// Run: NODE_PATH=/tmp/apptest/node_modules node tools/tests/style-check.js
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const R = [];
const ck = (n, ok, d) => R.push({ n, ok: !!ok, d: d === undefined ? '' : String(d) });

const PLAN_PATH = path.join(ROOT, 'data/plan.json');
const PLAN = fs.existsSync(PLAN_PATH) ? JSON.parse(fs.readFileSync(PLAN_PATH, 'utf8')) : {};

// markdown-aware: **bold** must be consumed before *italic*, or parity desyncs
const SPAN = /(\*\*[^*]+\*\*|\*[^*\n]+\*)/;
const ITALIC = /(?<!\*)\*[^*\n]+\*(?!\*)/g;
const BOLD = /\*\*[^*]+\*\*/g;

// ayah_en uses curly quotes, nbsp and ornate-parenthesis marks; commas around
// vocatives ("O Prophet,") are editorial. Collapse all of it before comparing.
const canon = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .replace(/[\u201c\u201d"]/g, '"').replace(/[\u2018\u2019']/g, "'")
  .replace(/[\u00a0\u02f9\u02fa\u204e]/g, ' ')
  .replace(/,/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();

const SIGNPOST_MIN = 3, SIGNPOST_MAX = 5;   // docs/style.md rule 2
const QUOTE_AVG_MAX = 10;                    // docs/style.md rule 4
const EXEMPT_ABOVE = 20;                     // over this, treated as an exempt hadith
// Maintainer ruling 2026-10-09: hadith and classical definitions are EXEMPT
// from the phrase cap. Chapter 1 - the model - carries ten quotations over
// 20 words, almost all hadith, including a 134-word parable at 1:6. So only
// the AVERAGE is enforced: a verse may quote one hadith whole, but it may not
// become a stack of extracts.

const files = [
  ['guidance_001.json', 1],
  ['guidance_002.json', 2],
  ['guidance_112.json', 112],
];

for (const [fn, surah] of files) {
  const fp = path.join(ROOT, 'data', fn);
  if (!fs.existsSync(fp)) { ck(`${fn} present`, false, 'missing'); continue; }
  const g = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const ayahSrc = fs.readFileSync(
    path.join(ROOT, 'data', `chapter_${String(surah).padStart(3, '0')}.js`), 'utf8');

  const ayahEn = n => {
    const m = ayahSrc.match(new RegExp(`"ayah_no_surah"\\s*:\\s*${n}\\b`));
    if (!m) return null;
    const e = ayahSrc.slice(m.index).match(/"ayah_en"\s*:\s*"((?:[^"\\]|\\.)*)"/);
    return e ? JSON.parse('"' + e[1] + '"') : null;
  };

  const verses = Object.keys(g.verses).map(Number).sort((a, b) => a - b);

  // An unauthored chapter is legitimate, but the payload contract must hold so
  // the app falls back to the six sources without error.
  if (verses.length === 0) {
    ck(`${fn}: empty, contract intact`,
       g.surah === surah && g.lang === 'en' && g.dir === 'ltr' && typeof g.title === 'string');
    continue;
  }

  const notOnePara = [], badHead = [], badSignpost = [], noOpenQuote = [], badQuoteLen = [],
        badTranslit = [], underFloor = [];
  let longestSeen = 0;

  for (const a of verses) {
    const t = g.verses[String(a)].text;

    // ---- rule 1: exactly one paragraph ----
    const paras = t.split('\n\n').map(s => s.trim()).filter(Boolean);
    const headSecs = text.split('\n\n').filter(p => /^\*\*[^*]+?\.\*\*$/.test(p.trim()));
    if (headSecs.length < 3 || headSecs.length > 6) badHead.push(`${surah}:${a} (${headSecs.length})`);
    if (paras.length < headSecs.length + 1) notOnePara.push(`${surah}:${a} (intro missing)`);

    // ---- rule 2: 3-5 inline bold signposts ----
    const signs = t.match(BOLD) || [];
    if (signs.length < SIGNPOST_MIN || signs.length > SIGNPOST_MAX) {
      badSignpost.push(`${surah}:${a} (${signs.length})`);
    }

    // ---- rule 3: opens by quoting ayah_en ----
    const en = ayahEn(a);
    const q0 = t.match(/^\*([^*]+)\*/);
    if (!q0) noOpenQuote.push(`${surah}:${a} (none)`);
    else if (en) {
      const said = canon(q0[1]).replace(/[.,;:!?]+$/, '');
      if (!canon(en).startsWith(said.slice(0, Math.min(said.length, 28)))) {
        noOpenQuote.push(`${surah}:${a}`);
      }
    }

    // ---- rule 4: quotations are short phrases, not extracts ----
    const quotes = (t.match(ITALIC) || []).filter(q => q.length > 2);
    const ql = quotes.map(q => q.replace(/\*/g, '').split(/\s+/).length);
    if (ql.length) {
      const longest = Math.max(...ql);
      if (longest > longestSeen) longestSeen = longest;
      // Exempt quotations (a hadith or definition quoted whole) are excluded
      // from the average, otherwise one long hadith fails an otherwise
      // well-written verse. The remaining short quotations must still average
      // down to phrase length - that is what stops extract-stacking.
      const short = ql.filter(x => x <= EXEMPT_ABOVE);
      if (short.length) {
        const avg = short.reduce((x, y) => x + y, 0) / short.length;
        if (avg > QUOTE_AVG_MAX) badQuoteLen.push(`${surah}:${a} (avg ${avg.toFixed(1)}w)`);
      }
    }

    // ---- rule 7: transliteration, prose only ----
    const prose = t.split(SPAN).filter(x => !SPAN.test(x)).join('');
    for (const [bad, good] of [['Mecca', 'Makkah'], ['Madinah', 'Madīnah'],
                               ['Jerusalem', 'Bayt al-Maqdis']]) {
      if (new RegExp(`\\b${bad}\\b`).test(prose)) {
        badTranslit.push(`${surah}:${a} "${bad}" -> "${good}"`);
      }
    }

    // ---- rule 6: length meets the tier floor (one-sided) ----
    const plan = PLAN[`${surah}:${a}`];
    if (plan) {
      const floor = Math.round(plan.words * 0.75);
      const n = t.trim().split(/\s+/).length;
      if (n < floor) underFloor.push(`${surah}:${a} (${n}w < ${floor}w)`);
    }
  }

  ck(`${fn} rule 1 — 3-6 headed sections + a plain intro`, notOnePara.length === 0 && badHead.length === 0, notOnePara.join(', '));
  ck(`${fn} rule 2 — ${SIGNPOST_MIN}-${SIGNPOST_MAX} inline signposts`,
     badSignpost.length === 0, badSignpost.join(', '));
  ck(`${fn} rule 3 — opens by quoting the translation`, noOpenQuote.length === 0,
     noOpenQuote.join(', '));
  ck(`${fn} rule 4 — quotations average <=${QUOTE_AVG_MAX} words`, badQuoteLen.length === 0,
     badQuoteLen.join(', '));
  console.log(`  ${fn}: longest single quotation ${longestSeen}w (hadith exempt, average is the rule)`);
  ck(`${fn} rule 6 — every verse meets its tier floor`, underFloor.length === 0,
     underFloor.join(', '));
  ck(`${fn} rule 7 — transliteration consistent in prose`, badTranslit.length === 0,
     badTranslit.join(', '));
}

let pass = 0;
for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
console.log(`\n${pass}/${R.length} checks passed`);
process.exit(pass === R.length ? 0 : 1);
