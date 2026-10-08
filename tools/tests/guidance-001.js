const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const vc = new VirtualConsole(); const errs = [];
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

(async () => {
  const dom = await JSDOM.fromURL('http://127.0.0.1:8000/', {
    runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (i, o) => fetch(new URL(i, 'http://127.0.0.1:8000/'), o);
      w.matchMedia = q => ({ matches: false, media: q, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {}, onchange: null });
    }
  });
  const w = dom.window;
  await new Promise(r => w.addEventListener('load', r, { once: true }));
  await new Promise(r => setTimeout(r, 800));
  const R = []; const ck = (n, c, d) => R.push({ n, ok: !!c, d: d === undefined ? '' : String(d) });

  const PLAN = await (await fetch('http://127.0.0.1:8000/data/plan.json')).json();

  // ---------- payload ----------
  await w.eval('loadTafsirData(1)');
  const g = await w.eval('loadGuidanceData(1)');
  ck('guidance_001 loads', !!g);
  ck('covers all 7 verses', w.eval("Object.keys(loadedGuidance[1].verses).join(',')") === '1,2,3,4,5,6,7',
     w.eval("Object.keys(loadedGuidance[1].verses).join(',')"));
  ck('every entry has a 1:N range', w.eval("Object.values(loadedGuidance[1].verses).every(v=>/^1:\\d$/.test(v.range))"));
  ck('every entry records 4+ sources drawn on',
     w.eval("Object.values(loadedGuidance[1].verses).every(v=>v.draws_on.length>=4)"));
  ck('all draws_on ids are real sources', w.eval(
    "Object.values(loadedGuidance[1].verses).every(v=>v.draws_on.every(id=>loadedTafsir[1].sources.some(s=>s.id===id)))"));

  // ---------- length against the fitted plan ----------
  for (let a = 1; a <= 7; a++) {
    const t = w.eval(`loadedGuidance[1].verses["${a}"].text`);
    const n = t.trim().split(/\s+/).length;
    const tgt = PLAN['1:' + a].words;
    ck(`1:${a} length ${n}w within 25% of plan (${tgt}w, Tier ${PLAN['1:' + a].tier})`,
       Math.abs(n - tgt) / tgt <= 0.25, `${n} vs ${tgt}`);
  }

  // ---------- it must quote the app's OWN translation ----------
  await w.eval('loadChapterData(1)');
  const pairs = [
    [1, 'In the Name of Allah'], [1, 'Most Compassionate'], [1, 'Most Merciful'],
    [2, 'All praise is for Allah'], [2, 'Lord of all worlds'],
    [3, 'Most Compassionate, Most Merciful'],
    [4, 'Master of the Day of Judgment'],
    [5, 'we worship'], [5, 'ask for help'],
    [6, 'Guide us'], [6, 'Straight Path'],
    [7, 'those You have blessed'], [7, 'displeased'], [7, 'astray'],
  ];
  for (const [a, frag] of pairs) {
    const t = w.eval(`loadedGuidance[1].verses["${a}"].text`);
    ck(`1:${a} quotes the app's translation "${frag}"`, t.includes(frag));
  }

  // ---------- integrity: every named authority must exist in that verse's sources ----------
  // Narrators and collectors only. The six tafsir TITLES are checked separately
  // against the payload's own labels — a work does not cite itself in its body.
  const NAMES = ['Imām Aḥmad', 'at-Tirmidhī', 'Al-Bukhārī', 'Muslim', 'Ibn Mājah',
                 'an-Nasāʾī', 'Abū Dāwūd', 'Ibn ʿAbbās', 'Abū Hurayrah',
                 'Jābir', 'Anas', 'Ibn ʿUmar', 'ad-Daḥḥāk', 'al-Kashshāf',
                 'Rāghib al-Iṣfahānī', 'Abū Jaʿfar aṭ-Ṭabarī',
                 'Abū Ḥanīfah', 'Abū Saʿīd ibn al-Muʿallā',
                 'an-Nawwās ibn Samʿān', 'ʿAdī ibn Ḥātim',
                 'Wāʾil ibn Ḥujr', 'al-Aswad ibn Sarīʿ', 'Qatādah',
                 'Abū al-ʿĀliyah', 'Al-Farrāʾ', 'Abū ʿUbayd'];
  // fold every diacritic and hamza variant down to plain ascii, as the sources write it
  const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[ʿʾʼ`'’‘\-]/g, ' ').replace(/\s+/g, ' ').toLowerCase();

  let attribChecked = 0; const attribBad = [];
  for (let a = 1; a <= 7; a++) {
    const t = w.eval(`loadedGuidance[1].verses["${a}"].text`);
    const blob = norm(w.eval(`getVerseCommentaryAll(loadedTafsir[1],${a}).map(e=>e.text).join(' ')`));
    for (const nm of NAMES) {
      if (t.includes(nm)) {
        attribChecked++;
        const parts = norm(nm).trim().split(' ').filter(x => x.length > 3);
        const base = parts[parts.length - 1];
        if (!blob.includes(base)) attribBad.push(`1:${a} "${nm}" (looked for "${base}")`);
      }
    }
  }
  ck(`every named narrator/collector (${attribChecked} checked) appears in that verse's sources`,
     attribBad.length === 0, attribBad.join('; '));

  // the six tafsir titles I cite must be real sources in the payload
  const cited = ['Maʿārif-ul-Qurʾān', 'Al-Mukhtaṣar', 'Tanwīr al-Miqbās',
                 'Tazkīrul Qurʾān', 'Ibn Kathīr', 'Al-Jalālayn'];
  const labels = norm(w.eval(`loadedTafsir[1].sources.map(s=>s.label).join(' | ')`));
  const badTitles = cited.filter(c => !labels.includes(norm(c).split(' ')[0]));
  ck('every tafsir title cited matches a real source label', badTitles.length === 0, badTitles.join('; '));

  // ---------- rendering ----------
  const html = w.eval('renderCommentaryHtml(loadedTafsir[1], getVerseCommentary(loadedTafsir[1],1), 1)');
  const el = w.document.createElement('div'); el.innerHTML = html;
  ck('guidance is the FIRST section', el.firstElementChild.classList.contains('tafsir-guidance'));
  ck('guidance labelled "In plain words"',
     el.querySelector('.tafsir-guidance .tafsir-source-label').textContent.includes('In plain words'));
  ck('guidance range is its first line',
     el.querySelector('.tafsir-guidance').firstElementChild.className === 'tafsir-range');
  ck('range reads "1:1"', el.querySelector('.tafsir-guidance .tafsir-range').textContent.trim() === '1:1');
  const det = el.querySelector('details.tafsir-sources');
  ck('six sources folded behind a disclosure', !!det && det.querySelectorAll('.tafsir-entry').length === 6,
     det ? det.querySelectorAll('.tafsir-entry').length : 'none');
  ck('guidance precedes the sources', html.indexOf('tafsir-guidance') < html.indexOf('tafsir-sources'));

  // ---------- modal end to end ----------
  w.eval('showExplanation(1,5)'); await new Promise(r => setTimeout(r, 600));
  const body = w.document.getElementById('modalBody').innerHTML;
  ck('modal for 1:5 leads with guidance',
     body.includes('tafsir-guidance') && body.indexOf('tafsir-guidance') < body.indexOf('tafsir-sources'));
  ck('modal quotes the translation', body.includes('we worship'));
  w.eval('closeModal && closeModal()');

  // ---------- ebook ----------
  const ebook = await w.eval(`(async()=>{await loadChapterData(1);
    AppState.currentSurah=1;AppState.currentSurahData=loadedChapters[1];
    await Promise.all([loadTafsirData(1),loadGuidanceData(1)]);
    const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
  ck('ebook carries guidance on all 7 verses', (ebook.match(/data-source="guidance"/g) || []).length === 7,
     (ebook.match(/data-source="guidance"/g) || []).length);
  ck('ebook folds all 7 source panels', (ebook.match(/<details class="tafsir-sources"/g) || []).length === 7);
  ck('ebook has no "coming soon"', !/coming soon/i.test(ebook));

  // ---------- no regression ----------
  await w.eval('loadTafsirData(112)'); await w.eval('loadGuidanceData(112)');
  const h112 = w.eval('renderCommentaryHtml(loadedTafsir[112], getVerseCommentary(loadedTafsir[112],1), 1)');
  ck('surah 112 guidance still renders', h112.includes('tafsir-guidance'));
  ck('surah 112 sources still folded', h112.includes('tafsir-sources'));

  // Pick the control surah dynamically: the first one that genuinely has no
  // guidance file. Hard-coding a surah here breaks every time it gets authored.
  const CTL = await w.eval(`(async()=>{
    for (const n of [3,4,5,6,7,8,9,10,11,12]) {
      if ((await loadGuidanceData(n)) === null) return n;
    }
    return 0;})()`);
  ck('found a control surah with no guidance', CTL > 0, CTL);
  await w.eval(`loadTafsirData(${CTL})`);
  ck(`surah ${CTL} has no guidance`, await w.eval(`loadedGuidance[${CTL}]`) === null);
  const h2 = w.eval(`renderCommentaryHtml(loadedTafsir[${CTL}], getVerseCommentary(loadedTafsir[${CTL}],1), 1)`);
  const e2 = w.document.createElement('div'); e2.innerHTML = h2;
  ck(`surah ${CTL} falls back to six sources shown directly`, e2.querySelectorAll('.tafsir-entry').length === 6,
     e2.querySelectorAll('.tafsir-entry').length);
  ck(`surah ${CTL} has no disclosure`, !e2.querySelector('details.tafsir-sources'));
  ck(`surah ${CTL} first source marked primary`,
     e2.querySelector('.tafsir-entry').classList.contains('tafsir-entry-primary'));

  ck('no jsdom errors', errs.length === 0, errs.join(' | '));

  let pass = 0;
  for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
  console.log(`\n${pass}/${R.length} checks passed`);
  process.exit(pass === R.length ? 0 : 1);
})();
