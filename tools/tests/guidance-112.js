const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const vc = new VirtualConsole(); const errs=[];
vc.on('jsdomError',e=>errs.push('jsdomError: '+e.message));
vc.on('error',(...a)=>errs.push('console.error: '+a.join(' ')));
(async()=>{
  const dom = await JSDOM.fromURL('http://127.0.0.1:8000/',{
    runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,virtualConsole:vc,
    beforeParse(w){ w.fetch=(i,o)=>fetch(new URL(i,'http://127.0.0.1:8000/'),o);
      w.matchMedia=q=>({matches:false,media:q,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){},onchange:null}); }});
  const w=dom.window;
  await new Promise(r=>w.addEventListener('load',r,{once:true}));
  await new Promise(r=>setTimeout(r,800));
  const R=[]; const ck=(n,c,d)=>R.push({n,ok:!!c,d:d===undefined?'':String(d)});

  await w.eval('loadTafsirData(112)');
  const g = await w.eval('loadGuidanceData(112)');
  ck('guidance_112 loads', !!g);
  ck('guidance covers all 4 verses', w.eval("Object.keys(loadedGuidance[112].verses).join(',')") === '1,2,3,4',
     w.eval("Object.keys(loadedGuidance[112].verses).join(',')"));
  ck('each guidance entry has a range', w.eval("Object.values(loadedGuidance[112].verses).every(v=>/^112:\\d/.test(v.range))"));
  ck('each guidance entry records its sources', w.eval("Object.values(loadedGuidance[112].verses).every(v=>v.draws_on.length>=5)"));

  // the guidance must quote the app's OWN translation wording
  const tr = JSON.parse(await w.eval(`(()=>{
    const out={};
    getChapterVerses(loadedChapters[112]||[]).forEach(v=>out[v.ayah_no_surah]=getVerseEnglish(v));
    return JSON.stringify(out);})()`));
  await w.eval('loadChapterData(112)');
  const pairs = [
    [1, 'Say'], [1, 'One'], [1, 'Indivisible'],
    [2, 'Sustainer'], [2, 'needed by all'],
    [3, 'offspring'], [3, 'nor was He born'],
    [4, 'none comparable to Him'],
  ];
  for (const [a, frag] of pairs) {
    const t = w.eval(`loadedGuidance[112].verses["${a}"].text`);
    ck(`112:${a} quotes the app's translation word "${frag}"`, t.includes(frag));
  }

  // guidance leads, sources folded behind it
  const html = w.eval('renderCommentaryHtml(loadedTafsir[112], getVerseCommentary(loadedTafsir[112],1), 1)');
  const el = w.document.createElement('div'); el.innerHTML = html;
  ck('guidance is the FIRST section', el.firstElementChild.classList.contains('tafsir-guidance'));
  ck('guidance labelled "In plain words"', el.querySelector('.tafsir-guidance .tafsir-source-label').textContent.includes('In plain words'));
  ck('guidance range is its first line', el.querySelector('.tafsir-guidance').firstElementChild.className === 'tafsir-range');
  const det = el.querySelector('details.tafsir-sources');
  ck('six sources folded behind a disclosure', !!det && det.querySelectorAll('.tafsir-entry').length === 6,
     det ? det.querySelectorAll('.tafsir-entry').length : 'no details');
  ck('guidance precedes the sources', html.indexOf('tafsir-guidance') < html.indexOf('tafsir-sources'));
  ck('sources panel names all six', det.textContent.includes('source tafsirs'));

  // verse modal end to end
  w.eval('showExplanation(112,1)'); await new Promise(r=>setTimeout(r,600));
  const body = w.document.getElementById('modalBody').innerHTML;
  ck('modal leads with guidance', body.includes('tafsir-guidance') && body.indexOf('tafsir-guidance') < body.indexOf('tafsir-sources'));
  ck('modal quotes the translation', body.includes('Indivisible'));

  // ebook: all four verses
  const eb = await w.eval(`(async()=>{await loadChapterData(112);
    AppState.currentSurah=112;AppState.currentSurahData=loadedChapters[112];
    await Promise.all([loadTafsirData(112),loadGuidanceData(112)]);
    const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
  ck('ebook has guidance for all 4 verses', (eb.match(/data-source="guidance"/g)||[]).length === 4,
     (eb.match(/data-source="guidance"/g)||[]).length);
  ck('ebook folds sources on all 4', (eb.match(/<details class="tafsir-sources"/g)||[]).length === 4);
  ck('ebook has no coming soon', !eb.includes('coming soon'));

  // No regression where guidance does not exist yet. The control surah is
  // chosen dynamically: the first one that genuinely has no guidance file.
  // Hard-coding a surah here breaks every time that surah gets authored.
  const CTL = await w.eval(`(async()=>{
    for (const n of [3,4,5,6,7,8,9,10,11,12]) {
      if ((await loadGuidanceData(n)) === null) return n;
    }
    return 0;})()`);
  ck('found a control surah with no guidance', CTL > 0, CTL);
  await w.eval(`loadTafsirData(${CTL})`);
  ck(`surah ${CTL} has no guidance`, w.eval(`loadedGuidance[${CTL}]`) === null);
  const h1 = w.eval(`renderCommentaryHtml(loadedTafsir[${CTL}], getVerseCommentary(loadedTafsir[${CTL}],1), 1)`);
  const e1 = w.document.createElement('div'); e1.innerHTML = h1;
  ck(`surah ${CTL} still shows six sources directly`, e1.querySelectorAll('.tafsir-entry').length === 6,
     e1.querySelectorAll('.tafsir-entry').length);
  ck(`surah ${CTL} shows no disclosure`, !e1.querySelector('details.tafsir-sources'));
  ck(`surah ${CTL} primary marked`, e1.firstElementChild.classList.contains('tafsir-entry-primary'));

  let bad=0;
  for(const r of R){ if(!r.ok)bad++; console.log(`${r.ok?'PASS':'FAIL'}  ${r.n}${r.d?'   ['+r.d+']':''}`); }
  console.log(`\n${R.length-bad}/${R.length} checks passed`);
  const rel=errs.filter(e=>!/Could not parse CSS|Not implemented/i.test(e));
  if(rel.length) console.log('\napp errors:\n'+rel.slice(0,6).join('\n'));
  process.exit(bad?1:0);
})().catch(e=>{console.error('HARNESS ERROR:',e);process.exit(2);});
