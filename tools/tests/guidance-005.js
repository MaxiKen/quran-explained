const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
// the preview server may be on any port; BASE overrides
const BASE = process.env.BASE || 'http://127.0.0.1:8000';
const vc = new VirtualConsole(); const errs = [];
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

(async () => {
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
  const R = []; const ck = (n, c, d) => R.push({ n, ok: !!c, d: d === undefined ? '' : String(d) });

  const PLAN = await (await fetch(`${BASE}/data/plan.json`)).json();

  // ---------- payload ----------
  await w.eval('loadTafsirData(5)');
  const g = await w.eval('loadGuidanceData(5)');
  ck('guidance_005 loads', !!g);
  const NENT = g ? Object.keys(g.verses).length : 0;
  ck('5:1-10 are written (10 entries)', NENT === 10, `${NENT} entries`);
  if (NENT > 0) {
    ck('written verses run contiguously from 5:1',
       w.eval("Object.keys(loadedGuidance[5].verses).map(Number).sort((a,b)=>a-b).every((v,i)=>v===i+1)"),
       'gap in verse numbers');
    ck('every entry has a 5:N range',
       w.eval("Object.values(loadedGuidance[5].verses).every(v=>typeof v.range==='string' && v.range.indexOf('5:')===0 && Number(v.range.slice(2))>0)"));
    ck('every entry records 5+ sources drawn on',
       w.eval("Object.values(loadedGuidance[5].verses).every(v=>v.draws_on.length>=5)"));
    ck('all draws_on ids are real sources', w.eval(
      "Object.values(loadedGuidance[5].verses).every(v=>v.draws_on.every(id=>loadedTafsir[5].sources.some(s=>s.id===id)))"));

    // ---------- length against the fitted plan (a floor, never a ceiling) ----------
    const N = w.eval("Object.keys(loadedGuidance[5].verses).length");
    for (let a = 1; a <= N; a++) {
      const t = w.eval(`loadedGuidance[5].verses["${a}"].text`);
      const n = t.trim().split(/\s+/).length;
      const tgt = PLAN['5:' + a].words;
      const floor = Math.round(tgt * 0.75);
      ck(`5:${a} length ${n}w meets the floor (${floor}w of ${tgt}w, Tier ${PLAN['5:' + a].tier})`,
         n >= floor, `${n} vs floor ${floor}`);
      const paras = t.split(/\n\s*\n/).filter(x => x.trim());
      const heads = paras.filter(p => /^\*\*[^*]+?[.?]\*\*$/.test(p.trim()));
      ck(`5:${a} has 3-6 own-line headings`, heads.length >= 3 && heads.length <= 6, `${heads.length}`);
      ck(`5:${a} opens on a plain paragraph`, paras.length > 0 && !paras[0].trim().startsWith('**'));
    }

    // ---------- it must quote the app's OWN translation ----------
    await w.eval('loadChapterData(5)');
    const pairs = [
      [1, 'Honour your obligations'], [1, 'grazing livestock'],
      [2, 'sacred months'], [2, 'garlands'], [2, 'Cooperate with one another'],
      [3, 'carrion'], [3, 'draw lots'], [3, 'perfected your faith'],
      [4, 'birds of prey'], [4, 'mention the Name of Allah'],
      [5, 'People of the Book'], [5, 'dowries'],
      [6, 'up to the elbows'], [6, 'clean earth'],
      [7, 'covenant'], [7, 'hidden in the heart'],
      [8, 'bear true testimony'], [8, 'Be just'],
      [9, 'forgiveness and a great reward'],
      [10, 'residents of the Hellfire'],
    ];
    for (const [a, frag] of pairs.filter(([n]) => n <= N)) {
      const t = w.eval(`loadedGuidance[5].verses["${a}"].text`);
      ck(`5:${a} quotes the app's translation "${frag}"`, t.includes(frag));
    }

    // ---------- every heading has a body that answers it ----------
    for (let a = 1; a <= N; a++) {
      const t = w.eval(`loadedGuidance[5].verses["${a}"].text`);
      const paras = t.split(/\n\s*\n/).filter(x => x.trim());
      let orphan = '';
      for (let i = 0; i < paras.length; i++) {
        if (/^\*\*[^*]+?[.?]\*\*$/.test(paras[i].trim())) {
          const body = (paras[i + 1] || '').trim();
          if (!body || /^\*\*/.test(body)) orphan = paras[i].trim();
        }
      }
      ck(`5:${a} every heading has a body under it`, orphan === '', orphan);
    }

    // ---------- integrity: named authorities exist in that verse's sources ----------
    const NAMES = ['Ibn ʿAbbās', "Ibn 'Abbas", 'Qatādah', 'Mujāhid', "Ibn Jarir", 'Jābir', 'An-Nuʿmān'];
    const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[ʿʾʼ`'’‘\-]/g, ' ').replace(/\s+/g, ' ').toLowerCase();
    let attribChecked = 0; const attribBad = [];
    for (let a = 1; a <= N; a++) {
      const t = w.eval(`loadedGuidance[5].verses["${a}"].text`);
      const blob = norm(w.eval(`getVerseCommentaryAll(loadedTafsir[5],${a}).map(e=>e.text).join(' ')`));
      for (const nm of NAMES) {
        if (t.includes(nm)) {
          attribChecked++;
          const parts = norm(nm).trim().split(' ').filter(x => x.length > 3);
          const base = parts[parts.length - 1];
          if (!blob.includes(base)) attribBad.push(`5:${a} "${nm}" (looked for "${base}")`);
        }
      }
    }
    ck(`every named authority (${attribChecked} checked) appears in that verse's sources`,
       attribBad.length === 0, attribBad.join('; '));

    // ---------- rendering ----------
    const html = w.eval('renderCommentaryHtml(loadedTafsir[5], getVerseCommentary(loadedTafsir[5],1), 1)');
    const el = w.document.createElement('div'); el.innerHTML = html;
    ck('guidance is the FIRST section', el.firstElementChild.classList.contains('tafsir-guidance'));
    ck('guidance labelled "In plain words"',
       el.querySelector('.tafsir-guidance .tafsir-source-label').textContent.includes('In plain words'));
    ck('guidance range is its first line',
       el.querySelector('.tafsir-guidance').firstElementChild.className === 'tafsir-range');
    ck('range reads "5:1"', el.querySelector('.tafsir-guidance .tafsir-range').textContent.trim() === '5:1');
    ck('guidance precedes the sources', html.indexOf('tafsir-guidance') < html.indexOf('tafsir-sources'));

    // ---------- modal end to end ----------
    w.eval('showExplanation(5,' + N + ')'); await new Promise(r => setTimeout(r, 600));
    const body = w.document.getElementById('modalBody').innerHTML;
    ck('modal for the last written verse leads with guidance',
       body.includes('tafsir-guidance') && body.indexOf('tafsir-guidance') < body.indexOf('tafsir-sources'));
    w.eval('closeModal && closeModal()');

    // ---------- ebook ----------
    const ebook = await w.eval(`(async()=>{await loadChapterData(5);
      AppState.currentSurah=5;AppState.currentSurahData=loadedChapters[5];
      await Promise.all([loadTafsirData(5),loadGuidanceData(5)]);
      const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
    ck('ebook carries guidance on every written verse',
       (ebook.match(/data-source="guidance"/g) || []).length === N,
       (ebook.match(/data-source="guidance"/g) || []).length);
    ck('ebook has no "coming soon"', !/coming soon/i.test(ebook));

    // ---------- the guidance must not recite the verse ----------
    await w.eval('loadChapterData(5)');
    const recited = [], merged = [];
    for (let a = 1; a <= w.eval("Object.keys(loadedGuidance[5].verses).length"); a++) {
      const r = JSON.parse(await w.eval(`(function(){
        var h = renderCommentaryHtml(loadedTafsir[5], getVerseCommentary(loadedTafsir[5], ${a}), ${a});
        var box = document.createElement('div'); box.innerHTML = h;
        var t = box.querySelector('.tafsir-guidance .tafsir-text');
        var en = getVerseEnglish(getVerseData(5, ${a})) || '';
        return JSON.stringify({
          recites: !!t && t.textContent.replace(/\\s+/g, ' ').indexOf(en.replace(/\\s+/g, ' ')) === 0,
          verseCardMarkup: !!box.querySelector('.tafsir-guidance .modal-verse-translation, .tafsir-guidance .ebook-translation')
        });})()`));
      if (r.recites) recited.push(`5:${a}`);
      if (r.verseCardMarkup) merged.push(`5:${a}`);
    }
    ck('no guidance card opens by reciting the whole translation', recited.length === 0, recited.join(', '));
    ck('no verse-card markup is folded into the guidance section', merged.length === 0, merged.join(', '));
  }

  // ---------- no regression: an unauthored surah still falls back to its sources ----------
  const CTL = await w.eval(`(async()=>{
    for (const n of [4,6,7,8,9,10,11,12,13,14]) {
      if ((await loadGuidanceData(n)) === null) return n;
    }
    return 0;})()`);
  ck('found a control surah with no guidance', CTL > 0, CTL);
  if (CTL > 0) {
    await w.eval(`loadTafsirData(${CTL})`);
    const h2 = w.eval(`renderCommentaryHtml(loadedTafsir[${CTL}], getVerseCommentary(loadedTafsir[${CTL}],1), 1)`);
    const e2 = w.document.createElement('div'); e2.innerHTML = h2;
    ck(`surah ${CTL} falls back to its sources shown directly`,
       e2.querySelectorAll('.tafsir-entry').length ===
         w.eval(`getVerseCommentaryAll(loadedTafsir[${CTL}], 1).length`),
       e2.querySelectorAll('.tafsir-entry').length);
    ck(`surah ${CTL} has no disclosure`, !e2.querySelector('details.tafsir-sources'));
  }

  ck('no jsdom errors', errs.length === 0, errs.join(' | '));

  let pass = 0;
  for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
  console.log(`\n${pass}/${R.length} checks passed`);
  process.exit(pass === R.length ? 0 : 1);
})();
