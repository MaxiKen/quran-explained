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

// ayah_en uses curly quotes, nbsp and ornate-parenthesis marks; commas around
// vocatives ("O Prophet,") are editorial. Collapse all of it before comparing.
const canon = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .replace(/[\u201c\u201d"]/g, '"').replace(/[\u2018\u2019']/g, "'")
  .replace(/[\u00a0\u02f9\u02fa\u204e]/g, ' ')
  .replace(/,/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();

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

  const notOnePara = [], badHead = [], badTranslit = [], underFloor = [], badLead = [];

  const folded = s => canon(s).replace(/[^a-z0-9]/g, '');
  for (const a of verses) {
    const t = g.verses[String(a)].text;

    // ---- rule 1: plain intro + 3-6 headed sections ----
    const paras = t.split('\n\n').map(s => s.trim()).filter(Boolean);

    // ---- rule 4 (maintainer, 2026-10-09): the opening paragraph EXPLAINS ----
    // A lead that only sets a mood, or only asks, left readers with no account
    // of the verse; 90 words at tier A and 60 elsewhere, the app's own wording
    // quoted inside it, and not a paragraph made entirely of questions.
    const plan4 = PLAN[`${surah}:${a}`] || {};
    const intro = paras.length && !/^\*\*/.test(paras[0]) ? paras[0] : '';
    const need4 = (() => {
      const en = ayahEn(a) || '';
      const tot = en.split(/\s+/).filter(w => canon(w).replace(/[^a-z0-9]/g, '')).length;
      return tot >= 8 ? 5 : Math.max(1, Math.min(tot, 3));
    })();
    if (plan4.tier !== 'C' || true) {
      const minLead = plan4.tier === 'A' ? 90 : 60;
      if (!intro) badLead.push(`${surah}:${a} (no opening paragraph)`);
      else {
        const words = intro.trim().split(/\s+/).length;
        if (words < minLead) badLead.push(`${surah}:${a} (${words}w lead < ${minLead}w)`);
        const enF = folded(ayahEn(a) || '');
        const tF = folded(intro);
        let run = 0;
        for (const ws of (ayahEn(a) || '').split(/\s+/).map(w => folded(w)).filter(Boolean)
                        .reduce((acc, w) => (acc.push(w), acc), [])) {
          void ws;
        }
        // longest run of consecutive ayah_en words present in the lead
        const ws4 = (ayahEn(a) || '').split(/[\s,.:;!?\u2013\u2014\u02bb\u2019"'()]+/).map(folded).filter(Boolean);
        outer: for (let i = 0; i < ws4.length; i++) {
          for (let j = ws4.length; j > i; j--) {
            if (j - i <= run) continue outer;
            if (tF.includes(ws4.slice(i, j).join(''))) { run = j - i; continue outer; }
          }
        }
        if (run < need4) badLead.push(`${surah}:${a} (lead quotes only ${run}w of ayah_en)`);
        const q = intro.split(/(?<=[.?!])\s+/).filter(Boolean);
        if (q.length && q.every(x => x.trim().endsWith('?'))) badLead.push(`${surah}:${a} (lead is all questions)`);
      }
    }
    const headSecs = t.split('\n\n').filter(p => /^\*\*[^*]+?\.\*\*$/.test(p.trim()));
    if (headSecs.length < 3 || headSecs.length > 6) badHead.push(`${surah}:${a} (${headSecs.length})`);
    if (paras.length < headSecs.length + 1) notOnePara.push(`${surah}:${a} (intro missing)`);

    // ---- rule 3: transliteration, prose only ----
    const prose = t.split(SPAN).filter(x => !SPAN.test(x)).join('');
    for (const [bad, good] of [['Mecca', 'Makkah'], ['Madinah', 'Madīnah'],
                               ['Jerusalem', 'Bayt al-Maqdis']]) {
      if (new RegExp(`\\b${bad}\\b`).test(prose)) {
        badTranslit.push(`${surah}:${a} "${bad}" -> "${good}"`);
      }
    }

    // ---- rule 2: length meets the tier floor (one-sided) ----
    const plan = PLAN[`${surah}:${a}`];
    if (plan) {
      const floor = Math.round(plan.words * 0.75);
      const n = t.trim().split(/\s+/).length;
      if (n < floor) underFloor.push(`${surah}:${a} (${n}w < ${floor}w)`);
    }
  }

  ck(`${fn} rule 1 — 3-6 headed sections + a plain intro`, notOnePara.length === 0 && badHead.length === 0, notOnePara.join(', '));
  ck(`${fn} rule 2 — every verse meets its tier floor`, underFloor.length === 0,
     underFloor.join(', '));
  ck(`${fn} rule 3 — transliteration consistent in prose`, badTranslit.length === 0,
     badTranslit.join(', '));
  ck(`${fn} rule 4 — the opening paragraph explains the verse`, badLead.length === 0,
     badLead.join(', '));
}

let pass = 0;
for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
console.log(`\n${pass}/${R.length} checks passed`);
process.exit(pass === R.length ? 0 : 1);
