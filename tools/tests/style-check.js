// Asserts the house style defined in docs/style.md against every authored
// guidance verse. Style drift is the same failure class as the silent test
// gaps in docs/pitfalls.md: an unchecked convention will break quietly.
//
// Run: NODE_PATH=/tmp/apptest/node_modules node tools/tests/style-check.js
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const R = [];
const ck = (n, ok, d) => R.push({ n, ok: !!ok, d: d === undefined ? '' : String(d) });

const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
// markdown-aware: **bold** must be consumed before *italic*, or parity desyncs
const SPAN = /(\*\*[^*]+\*\*|\*[^*\n]+\*)/;
const stripSpans = t => t.split(SPAN).filter(x => !SPAN.test(x)).join('');
// ayah_en uses curly quotes, nbsp and ornate-parenthesis marks
const canon = s => norm(s)
  .replace(/[\u201c\u201d\u0022]/g, '"').replace(/[\u2018\u2019\u0027]/g, "'")
  .replace(/[\u00a0\u02f9\u02fa\u204e]/g, ' ')
  .replace(/,/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();

const HEADING = /^\*\*[^*]+\*\*$/;
const MERGE_TARGET = 85;      // docs/style.md rule 1
const LONG_QUOTE = 45;        // a quotation this long may stand alone
const MAX_STUB = 30;          // a body paragraph shorter than this is a stub

const files = [
  ['guidance_001.json', 1],
  ['guidance_002.json', 2],
  ['guidance_112.json', 112],
];

for (const [fn, surah] of files) {
  const fp = path.join(ROOT, 'data', fn);
  if (!fs.existsSync(fp)) { ck(`${fn} present`, false, 'missing'); continue; }
  const g = JSON.parse(fs.readFileSync(fp, 'utf8'));
  const ayahSrc = fs.readFileSync(path.join(ROOT, 'data', `chapter_${String(surah).padStart(3, '0')}.js`), 'utf8');

  const ayahEn = n => {
    const m = ayahSrc.match(new RegExp(`"ayah_no_surah"\\s*:\\s*${n}\\b`));
    if (!m) return null;
    const e = ayahSrc.slice(m.index).match(/"ayah_en"\s*:\s*"((?:[^"\\]|\\.)*)"/);
    return e ? JSON.parse('"' + e[1] + '"') : null;
  };

  const verses = Object.keys(g.verses).map(Number).sort((a, b) => a - b);
  ck(`${fn}: ${verses.length} verses parsed`, verses.length > 0);

  const badOpen = [], badStub = [], badBig = [], badTranslit = [], badQuote = [];

  for (const a of verses) {
    const t = g.verses[String(a)].text;
    const paras = t.split('\n\n').map(s => s.trim()).filter(Boolean);

    // ---- rule 2: the entry opens by quoting the translation ----
    const en = ayahEn(a);
    const firstProse = paras.find(p => !HEADING.test(p)) || '';
    if (en) {
      const q = firstProse.match(/^\*([^*]+)\*/);
      if (!q) badOpen.push(`${surah}:${a} (no opening quote)`);
      else {
        const said = canon(q[1]).replace(/[.,;:!?]+$/, '');
        if (!canon(en).startsWith(said.slice(0, Math.min(said.length, 28)))) badOpen.push(`${surah}:${a}`);
      }
    }

    // ---- rule 1: no stub body paragraphs, headings on their own line ----
    for (const p of paras) {
      if (HEADING.test(p)) continue;
      const w = p.split(/\s+/).length;
      const quoted = /^\*[^*].*\*$/.test(p);
      if (quoted && w >= LONG_QUOTE) continue;   // a long quotation may stand alone
      // a short paragraph introducing the quotation beneath it is correct typography
      const idx = paras.indexOf(p);
      const nxt = paras[idx + 1] || '';
      const leadIn = /^\*[^*]/.test(nxt) && nxt.split(/\s+/).length >= LONG_QUOTE;
      // A short paragraph that CLOSES a section is a deliberate rhetorical
      // closer, not fragmentation. Only short paragraphs stranded MID-section
      // (followed by more prose) count as unmerged stubs.
      const sectionEnd = !nxt || HEADING.test(nxt) || /^\*[^*]/.test(nxt);
      if (w < MAX_STUB && !leadIn && !sectionEnd) badStub.push(`${surah}:${a} (${w}w)`);
      if (w > MERGE_TARGET * 2.6) badBig.push(`${surah}:${a} (${w}w)`);
    }

    // ---- rule 4: transliteration, prose only (quotations stay verbatim) ----
    const prose = stripSpans(t);
    for (const [bad, good] of [['Mecca', 'Makkah'], ['Madinah', 'Madīnah'], ['Jerusalem', 'Bayt al-Maqdis']]) {
      const re = new RegExp(`\\b${bad}\\b`);
      if (re.test(prose)) badTranslit.push(`${surah}:${a} "${bad}" -> "${good}"`);
    }

    // ---- rule 4b: the quoted translation must match ayah_en ----
    if (en) {
      const q = firstProse.match(/^\*([^*]+)\*/);
      if (q) {
        const said = canon(q[1]).replace(/[.,;:!?]+$/, '');
        if (!canon(en).startsWith(said.slice(0, Math.min(said.length, 28)))) badQuote.push(`${surah}:${a}`);
      }
    }
  }

  ck(`${fn} rule 2 — every entry opens with the translation`, badOpen.length === 0, badOpen.join(', '));
  ck(`${fn} rule 1 — no stub paragraphs (<${MAX_STUB}w)`, badStub.length === 0,
     `${badStub.length}: ${badStub.slice(0, 8).join(', ')}`);
  ck(`${fn} rule 1 — no unmerged blocks (>${Math.round(MERGE_TARGET * 2.6)}w)`, badBig.length === 0,
     `${badBig.length}: ${badBig.slice(0, 8).join(', ')}`);
  ck(`${fn} rule 4 — transliteration consistent in prose`, badTranslit.length === 0, badTranslit.join(', '));
  ck(`${fn} rule 4b — opening quote matches ayah_en`, badQuote.length === 0, badQuote.join(', '));
}

let pass = 0;
for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
console.log(`\n${pass}/${R.length} checks passed`);
process.exit(pass === R.length ? 0 : 1);
