/*
 * guidance-range.js — the render gate for WHATEVER is authored, no per-sūrah edits.
 *
 *   BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-range.js
 *   BASE=... node tools/tests/guidance-range.js 2        # one sūrah
 *
 * `guidance-001.js` is a hand-written suite for one chapter: it names each verse's
 * translation fragments, so it goes stale the moment a batch lands and nobody updates
 * the list. This one reads `data/guidance_*.json`, takes the wording it must find from
 * `data/chapter_NNN.js`, and asserts the reader-visible invariants for every authored
 * verse: the lead is present and walks the verse, the headings are real `<h4>`s in a
 * 3–6 count, the sources are folded after the guidance, the guidance never recites the
 * verse the app already shows, and the app still shows the verse itself.
 *
 * Run it after every batch, next to style-check. It needs the server (see
 * docs/testing.md) and costs a few seconds for a chapter.
 */
const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const BASE = process.env.BASE || 'http://127.0.0.1:8000';
const ONLY = process.argv[2] ? parseInt(process.argv[2], 10) : null;

const vc = new VirtualConsole();
const jserrs = [];
vc.on('jsdomError', e => jserrs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => jserrs.push('console.error: ' + a.join(' ')));

// The same measure the compiler uses: a run of the translation's words, matched after
// case, diacritics and the app's own ˹…˺ markers are stripped. What the harness adds is
// that it reads the run out of the RENDERED guidance, not the JSON, so a render layer
// that mangles or reorders the entry is caught here and nowhere else.
const canon = t => String(t).toLowerCase()
  .replace(/[\u0600-\u06FF\u0700-\u074F]/g, ' ')
  .normalize('NFD').replace(/[\u0300-\u036F\u1DC0-\u1DFF]/g, '')
  .replace(/[^a-z0-9]+/g, '');
// identical tokenisation and same rule as tools/verify_verse.en_run, including the
// short-verse concession (a 3-word translation cannot be quoted 5 words deep):
//   need = 5 when the verse has 8+ words, else max(1, min(words, 3))
const PUNCT = /[.,;:!?\u2013\u2014()\[\]{}\u02bb\u2019"'\u02bf]/g;
function quoteRun(en, text) {
  const ws = en.replace(PUNCT, ' ').split(/\s+/).filter(Boolean).map(canon);
  const c = canon(text);
  let best = 0;
  for (let i = 0; i < ws.length; i++) {
    for (let j = i + 1; j <= ws.length; j++) {
      if (c.includes(ws.slice(i, j).join(''))) best = Math.max(best, j - i);
      else break;
    }
  }
  return { run: best, need: ws.length >= 8 ? 5 : Math.max(1, Math.min(ws.length, 3)) };
}

(async () => {
  const plan = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/plan.json'), 'utf8'));
  const files = fs.readdirSync(path.join(ROOT, 'data'))
    .filter(f => /^guidance_\d{3}\.json$/.test(f))
    .map(f => ({ s: parseInt(f.slice(9, 12), 10), f }))
    .filter(o => !ONLY || o.s === ONLY);

  const dom = await JSDOM.fromURL(BASE, {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (i, o) => fetch(new URL(i, BASE), o);
      w.matchMedia = q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, onchange: null });
    }
  });
  const w = dom.window;
  await new Promise(r => w.addEventListener('load', r, { once: true }));
  await new Promise(r => setTimeout(r, 800));

  const R = [];
  const ck = (n, ok, d) => R.push({ n, ok: !!ok, d: d === undefined ? '' : String(d) });

  for (const { s, f } of files) {
    const g = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', f), 'utf8'));
    const verses = Object.entries(g.verses || {}).map(([a, v]) => [parseInt(a, 10), v]);
    if (!verses.length) {
      // An empty chapter is a legitimate state (docs/progress.md), and the reader's
      // fallback is the path being exercised, so assert that instead of prose.
      await w.eval(`loadTafsirData(${s})`);
      const a0 = 1;
      ck(`${s}: no guidance file entries, so its sets are shown in full and unfolded`,
         await w.eval(`(()=>{const h=renderCommentaryHtml(loadedTafsir[${s}], getVerseCommentary(loadedTafsir[${s}],${a0}),${a0});
           const d=document.createElement('div'); d.innerHTML=h;
           return !d.querySelector('.tafsir-guidance') && !d.querySelector('details.tafsir-sources')
             && d.querySelectorAll('.tafsir-entry').length===getVerseCommentaryAll(loadedTafsir[${s}],${a0}).length;})()`),
         'placeholder chapter');
      continue;
    }

    await w.eval(`loadChapterData(${s})`);
    await w.eval(`loadTafsirData(${s})`);
    const gg = await w.eval(`loadGuidanceData(${s})`);
    ck(`${s}: the app loads its guidance file`, !!gg && Object.keys(gg.verses).length === verses.length);

    const en = {};
    for (const [a] of verses) en[a] = await w.eval(`getVerseEnglish(getVerseData(${s}, ${a})) || ''`);

    const bad = { lead: [], run: [], heads: [], recital: [], floor: [], draws: [], fold: [], verseBlock: [], chrome: [] };
    for (const [a, v] of verses) {
      const html = await w.eval(`renderCommentaryHtml(loadedTafsir[${s}], null, ${a})`);
      const doc = new dom.window.DOMParser().parseFromString(html, 'text/html');
      const guid = doc.querySelector('.tafsir-guidance');
      const text = guid ? guid.textContent.replace(/\s+/g, ' ').trim() : '';
      const lead = (html.split(/<h4/)[0] || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

      if (!guid || !lead.length) bad.lead.push(`${s}:${a}`);
      else {
        const q = quoteRun(en[a], lead);
        if (q.run < q.need) bad.run.push(`${s}:${a} ${q.run}w<${q.need}w`);
        const whole = en[a].split(/\s+/).slice(0, 12).join(' ');
        if (whole && lead.replace(/^[^A-Za-z]*/, '').startsWith(whole)) bad.recital.push(`${s}:${a}`);
        if (/<audio|class="[^"]*(arabic-text|modal-verse|ebook-translation)[^"]*"/.test(html.split('</section>')[0])) bad.chrome.push(`${s}:${a}`);
      }
      const nh = doc.querySelectorAll('.tafsir-guidance h4').length;
      if (nh < 3 || nh > 6) bad.heads.push(`${s}:${a}(${nh})`);

      const p = plan[`${s}:${a}`];
      if (p) {
        const floor = p.floor !== undefined ? p.floor : Math.round(p.words * 0.75);
        const n = v.text.trim().split(/\s+/).length;
        if (n < floor) bad.floor.push(`${s}:${a} ${n}<${floor}`);
        const need = p.tier === 'C' ? 4 : 5;
        if ((v.draws_on || []).length < need) bad.draws.push(`${s}:${a}(${v.draws_on.length}<${need})`);
      } else bad.floor.push(`${s}:${a} no plan row`);

      const det = doc.querySelectorAll('details.tafsir-sources');
      if (!det.length) bad.fold.push(`${s}:${a} no sources panel`);
      else {
        const gi = html.indexOf('tafsir-guidance'), si = html.indexOf('class="tafsir-sources"');
        if (si >= 0 && si < gi) bad.fold.push(`${s}:${a} sources before guidance`);
      }

      // the verse block is the reader's, guidance or no guidance (maintainer, 2026-10-10):
      // the app's own English must still be under the Arabic in the modal, in full.
      await w.eval(`showExplanation(${s}, ${a})`);
      const shown = await w.eval(`(()=>{const c=document.getElementById('modalVerseCard');
        const t=c&&c.querySelector('.modal-verse-translation');
        return {hidden: !c||c.hidden, ar: !!(c&&c.querySelector('.modal-verse-arabic')),
                en: t?t.textContent.trim():''};})()`);
      if (shown.hidden || !shown.ar || shown.en !== en[a].trim()) bad.verseBlock.push(`${s}:${a}`);
    }

    const nm = {
      lead: 'every authored verse renders guidance that opens with a lead paragraph',
      run: 'each lead quotes the app\'s own translation for as long as verify_verse requires',
      heads: 'every entry has 3–6 real <h4> headings',
      recital: 'no lead opens by reciting the whole translation',
      chrome: 'no verse-card or recital markup inside the guidance block',
      floor: 'every entry is at or over its plan floor (0.75× target; thin verses are authored-only, not exempted)',
      draws: 'every entry records the sets it was drawn on (5+ at A/B, 4+ at C)',
      fold: 'the source sets are folded in a panel after the guidance',
      verseBlock: 'the verse card still shows the English translation for a guided verse',
    };
    for (const k of Object.keys(nm)) ck(`${s}: ${nm[k]}`, bad[k].length === 0, bad[k].slice(0, 6).join(' ') + (bad[k].length > 6 ? ` (+${bad[k].length - 6})` : ''));
  }

  ck('no jsdom errors', jserrs.length === 0, jserrs.slice(0, 2).join(' | '));

  const fail = R.filter(r => !r.ok);
  for (const r of R) console.log(`${r.ok ? ' ok ' : 'FAIL'}  ${r.n}${r.d ? '  — ' + r.d : ''}`);
  console.log(`\n${R.length - fail.length}/${R.length} checks passed`);
  process.exit(fail.length ? 1 : 0);
})();
