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
  ck('5:1-50 are written (50 entries)', NENT === 50, `${NENT} entries`);
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
      [11, 'held their hands back'], [11, 'put their trust'],
      [12, 'twelve leaders'], [12, 'a good loan'],
      [13, 'hardened their hearts'], [13, 'Allah loves the good-doers'],
      [14, 'hostility and enmity'], [14, 'the Day of Judgment'],
      [15, 'a light and a clear Book'], [15, 'disregarding much'],
      [16, 'ways of peace'], [16, 'Straight Path'],
      [17, 'Allah is the Messiah'], [17, 'Most Capable of everything'],
      [18, 'the children of Allah'], [18, 'the final return'],
      [19, 'a deliverer of good news'], [19, 'after an interval'],
      [20, 'made you sovereign'], [20, 'He raised prophets'],
      [21, 'Holy Land'], [21, 'become losers'],
      [22, 'enormously powerful'], [22, 'until they leave'],
      [23, 'through the gate'], [23, 'Put your trust in Allah'],
      [24, 'both you and your Lord'], [24, 'staying right here'],
      [25, 'no control over anyone'], [25, 'rebellious people'],
      [26, 'forbidden to them for forty years'], [26, 'grieve for the rebellious people'],
      [27, 'two sons'], [27, 'sincerely devout'],
      [28, 'I will not raise mine'], [28, 'Lord of all worlds'],
      [29, 'destined to the Fire'], [29, 'reward of the wrongdoers'],
      [30, 'convinced himself'], [30, 'becoming a loser'],
      [31, 'a crow digging'], [31, 'became regretful'],
      [32, 'as if they killed all of humanity'], [32, 'whoever saves a life'],
      [33, 'wage war against Allah'], [33, 'exile from the land'],
      [34, 'repent before you seize them'], [34, 'Most Merciful'],
      [35, 'seek what brings you closer'], [35, 'so you may be successful'],
      [36, 'in the world twice over'], [36, 'painful punishment'],
      [37, 'never be able to'], [37, 'everlasting punishment'],
      [38, 'male and female thieves'], [38, 'Almighty, All-Wise'],
      [39, 'mends their ways'], [39, 'All-Forgiving, Most Merciful'],
      [40, 'belongs to Allah'], [40, 'forgives whoever He wills'],
      [41, 'race to disbelieve'], [41, 'tremendous punishment in the Hereafter'],
      [42, 'consume forbidden gain'], [42, 'loves those who are just'],
      [43, 'the Torah containing'], [43, 'not true believers'],
      [44, 'containing guidance and light'], [44, 'are truly the disbelievers'],
      [45, 'life for a life'], [45, 'are truly the wrongdoers'],
      [46, 'confirming the Torah revealed before him'], [46, 'a guide and a lesson'],
      [47, 'let the people of the Gospel judge'], [47, 'are truly the rebellious'],
      [48, 'a supreme authority on them'], [48, 'regarding your differences'],
      [49, 'do not follow their desires'], [49, 'indeed rebellious'],
      [50, 'judgment of pre-Islamic ignorance'], [50, 'people of sure faith'],
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
