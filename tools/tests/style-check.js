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

    // ---- rule 4 (maintainer, 2026-10-09, rewritten 2026-10-10): the opening
    // paragraph WALKS the verse. Every meaningful phrase of the app's translation
    // is quoted in order and explained where it stands, with links to the verse
    // before and after where the sources make one; the lead therefore has to do
    // the most work in the entry. Evidence (hadith, cross-references, rulings,
    // occasion, theology) is what the headed sections carry. The commentary must
    // not open by quoting the whole verse in one line. Mirrors verify_verse.py.
    const plan4 = PLAN[`${surah}:${a}`] || {};
    const LEAD_FLOOR = { A: 240, B: 170, C: 110 };
    const en = ayahEn(a) || '';
    const tot = en.split(/\s+/).filter(w => folded(w)).length;
    const need4 = tot >= 8 ? 5 : Math.max(1, Math.min(tot, 3));
    const intro = paras.length && !/^\*\*/.test(paras[0]) ? paras[0] : '';
    const bodyWords = t.trim().split(/\s+/).length;
    if (!intro) badLead.push(`${surah}:${a} (no opening paragraph)`);
    else {
      const words = intro.trim().split(/\s+/).length;
      const minLead = plan4.lead_floor || LEAD_FLOOR[plan4.tier] || 170;   // the plan is the one source of the number
      if (words < minLead) badLead.push(`${surah}:${a} (lead ${words}w < ${minLead}w)`);
      const minShare = Math.floor(0.20 * bodyWords);
      if (words < minShare) badLead.push(`${surah}:${a} (lead is ${words}w of ${bodyWords}w, needs ${minShare}w)`);
      const tF = folded(intro);
      let run = 0;
      const ws4 = en.split(/[\s,.:;!?\u2013\u2014\u02bb\u2019"'()\u02f9\u02fa]+/).map(folded).filter(Boolean);
      outer: for (let i = 0; i < ws4.length; i++) {
        for (let j = ws4.length; j > i; j--) {
          if (j - i <= run) continue outer;
          if (tF.includes(ws4.slice(i, j).join(''))) { run = j - i; continue outer; }
        }
      }
      if (run < need4) badLead.push(`${surah}:${a} (lead quotes only ${run}w of ayah_en)`);
      // phrase coverage + order
      const chunks = (() => {
        const raw = en.replace(/[\u02f9\u02fa\u02bb]/g, '')
          .split(/[,;:.!?\u2026\u2013\u2014\u201c\u201d\u2018\u2019]/).map(x => x.trim()).filter(x => folded(x));
        const out = [];
        for (const c of raw) {
          const n = c.split(/\s+/).filter(w => folded(w)).length;
          if (out.length && n < 3) out[out.length - 1] += ' ' + c;
          else out.push(c);
        }
        if (out.length > 1 && out[0].split(/\s+/).filter(w => folded(w)).length < 3) {
          out[0] += ' ' + out[1]; out.splice(1, 1);
        }
        return out;
      })();
      let at = 0, ordered = true;
      for (const c of chunks) {
        const key = folded(c);
        const i = tF.indexOf(key);
        if (i < 0) badLead.push(`${surah}:${a} (lead skips "${c}")`);
        else if (i < at) ordered = false;
        else at = i + key.length;
      }
      if (!ordered) badLead.push(`${surah}:${a} (lead quotes the verse out of order)`);
      const ital = intro.match(/^\s*\*([^*]+)\*/);
      if (ital && run >= Math.max(need4, tot - 1)) {
        badLead.push(`${surah}:${a} (lead opens by quoting the whole verse)`);
      }
      const q = intro.split(/(?<=[.?!])\s+/).filter(Boolean);
      if (q.length && q.every(x => x.trim().endsWith('?'))) badLead.push(`${surah}:${a} (lead is all questions)`);
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
      const floor = plan.floor !== undefined ? plan.floor : Math.round(plan.words * 0.75);
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
