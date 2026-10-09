const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const vc = new VirtualConsole(); const errs = [];
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));
(async () => {
  const dom = await JSDOM.fromURL('http://127.0.0.1:8000/', {
    runScripts:'dangerously', resources:'usable', pretendToBeVisual:true, virtualConsole:vc,
    beforeParse(window){
      window.fetch = (i,init)=>fetch(new URL(i,'http://127.0.0.1:8000/'),init);
      window.matchMedia = q => ({matches:false,media:q,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){},onchange:null});
    }});
  const w = dom.window;
  await new Promise(r => w.addEventListener('load', r, {once:true}));
  await new Promise(r => setTimeout(r, 800));
  const R=[]; const ck=(n,c,d)=>R.push({n,ok:!!c,d:d===undefined?'':String(d)});

  await w.eval('loadTafsirData(2)');
  ck('6 sources in payload', w.eval('loadedTafsir[2].sources.length') === 6, w.eval('loadedTafsir[2].sources.length'));
  ck('source ids', w.eval('JSON.stringify(loadedTafsir[2].sources.map(s=>s.id))') ===
     '["ibn-kathir","maarif","tazkirul","tanwir","jalalayn","mukhtasar"]');
  ck('primary is ibn-kathir', w.eval('loadedTafsir[2].primary') === 'ibn-kathir');

  // accessors
  ck('getVerseCommentary defaults to primary',
     w.eval('getVerseCommentary(loadedTafsir[2],240)') === w.eval('getVerseCommentary(loadedTafsir[2],240,"ibn-kathir")'));
  ck('per-source accessor works', w.eval('getVerseCommentary(loadedTafsir[2],240,"jalalayn").length') > 0);
  const all = JSON.parse(await w.eval('JSON.stringify(getVerseCommentaryAll(loadedTafsir[2],240).map(e=>[e.id,e.range,e.text.length]))'));
  ck('all six return text for 2:240', all.length === 6, JSON.stringify(all.map(a=>a[0])));
  ck('ranges differ across sources (they group differently)', new Set(all.map(a=>a[1])).size > 1,
     JSON.stringify(all.map(a=>a[1])));
  ck('every entry has a range', all.every(a=>/^\d+:\d+/.test(a[1])));

  // range first line for EVERY entry
  const html = w.eval('renderCommentaryHtml(loadedTafsir[2], getVerseCommentary(loadedTafsir[2],240), 240)');
  const el = w.document.createElement('div'); el.innerHTML = html;
  const entries = el.querySelectorAll('.tafsir-entry');
  ck('six entries rendered', entries.length === 6, entries.length);
  let firstIsRange = true, rangeBeforeText = true;
  entries.forEach(sec => {
    if (sec.firstElementChild.className !== 'tafsir-range') firstIsRange = false;
    const kids = [...sec.children].map(c=>c.className||c.tagName);
    if (kids.indexOf('tafsir-range') > kids.findIndex(k=>k==='tafsir-text')) rangeBeforeText = false;
  });
  ck('range is the FIRST element of every entry', firstIsRange);
  ck('range precedes the text in every entry', rangeBeforeText);
  ck('each entry names its source', [...entries].every(s=>s.querySelector('.tafsir-source-label')));
  ck('primary entry marked', entries[0].classList.contains('tafsir-entry-primary'));
  ck('data-source attributes present',
     JSON.stringify([...entries].map(s=>s.dataset.source)) ===
     '["ibn-kathir","maarif","tazkirul","tanwir","jalalayn","mukhtasar"]');
  ck('no bare Arabic left unwrapped', w.eval(`(() => {
     const el=document.createElement('div');
     el.innerHTML=renderCommentaryHtml(loadedTafsir[2],getVerseCommentary(loadedTafsir[2],240),240);
     const walk=n=>{for(const c of n.childNodes){
       if(c.nodeType===3&&/[\\u0600-\\u06FF]/.test(c.nodeValue))return true;
       if(c.nodeType===1&&!c.classList.contains('ar-inline')&&walk(c))return true;}return false;};
     return walk(el)?'BARE':'clean';})()`) === 'clean');

  // corpus
  const corpus = await w.eval(`(async () => {
    const out={v:0,missing:0,uniqVerse:0,diff:[],perVerse:0};
    for(let n=1;n<=114;n++){
      const t=await loadTafsirData(n);
      const ch=chaptersData.find(c=>c.number===n);
      for(let a=1;a<=ch.verses;a++){
        out.v++;
        const es=getVerseCommentaryAll(t,a);
        if(es.length!==6) out.missing++;
        if(new Set(es.map(e=>e.text)).size===6) out.uniqVerse++;
        out.perVerse += es.reduce((s,e)=>s+e.text.split(/\\s+/).length,0);
        for(const e of es) if(!e.range) out.diff.push(n+':'+a);
      }
    }
    return JSON.stringify(out);})()`);
  const c = JSON.parse(corpus);
  ck('all 6,236 verses present', c.v === 6236, String(c.v));
  ck('every verse has all six sources', c.missing === 0, String(c.missing));
  ck('every entry has a range', c.diff.length === 0, c.diff.slice(0,5).join(','));
  ck('all six differ on every verse (100%)', c.uniqVerse === 6236, `${c.uniqVerse}/6236`);
  ck('per-verse words = 12,043,324', c.perVerse === 12043324, c.perVerse.toLocaleString());
  ck('content is 1.92x Ibn Kathir alone', Math.abs(c.perVerse/6281305 - 1.92) < 0.01,
     (c.perVerse/6281305).toFixed(2) + 'x');

  // modal + ebook
  w.eval('showExplanation(2,240)'); await new Promise(r=>setTimeout(r,500));
  const body = w.document.getElementById('modalBody').innerHTML;
  ck('modal shows six entries', (body.match(/class="tafsir-entry/g)||[]).length === 6);
  ck('modal first line is a range', /<section class="tafsir-entry tafsir-entry-primary"[^>]*><p class="tafsir-range"/.test(body));
  const eb = await w.eval(`(async()=>{await loadChapterData(2);
     AppState.currentSurah=2;AppState.currentSurahData=loadedChapters[2];await loadTafsirData(2);
     const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
  ck('ebook shows six entries per verse', (eb.match(/data-source="jalalayn"/g)||[]).length === 286,
     (eb.match(/data-source="jalalayn"/g)||[]).length);
  ck('ebook has no coming soon', !eb.includes('coming soon'));

  // read aloud still reads the primary only
  ck('read aloud uses primary only',
     w.eval('ReadAloud.unitFor(2,240).length') > 1 &&
     !w.eval('JSON.stringify(ReadAloud.unitFor(2,240).map(l=>l.speak))').includes('Al-Mukhta'));
  ck('spoken lines all English',
     JSON.parse(await w.eval('JSON.stringify(ReadAloud.unitFor(2,240).map(l=>l.lang))')).every(l=>l==='en'));

  let bad=0;
  for(const r of R){ if(!r.ok) bad++; console.log(`${r.ok?'PASS':'FAIL'}  ${r.n}${r.d?'   ['+r.d+']':''}`); }
  console.log(`\n${R.length-bad}/${R.length} checks passed`);
  const rel = errs.filter(e=>!/Could not parse CSS|Not implemented/i.test(e));
  if(rel.length) console.log('\napp errors:\n'+rel.slice(0,6).join('\n'));
  process.exit(bad?1:0);
})().catch(e=>{console.error('HARNESS ERROR:',e);process.exit(2);});
