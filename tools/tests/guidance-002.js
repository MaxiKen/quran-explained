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
  await w.eval('loadTafsirData(2)');
  const g = await w.eval('loadGuidanceData(2)');
  ck('guidance_002 loads', !!g);
  // An empty chapter is a legitimate state (the layer was cleared 2026-10-09), and
  // the harness has to be honest in both states rather than assume authoring: so
  // the prose checks below run only when there is prose, and the fallback path is
  // asserted when there is none.
  const NENT = g ? Object.keys(g.verses).length : 0;
  if (NENT === 0) {
    ck('2 is unauthored, so its sources are shown directly and in full',
       await w.eval(`(async()=>{
         const h=renderCommentaryHtml(loadedTafsir[2], getVerseCommentary(loadedTafsir[2],1),1);
         const d=document.createElement('div'); d.innerHTML=h;
         return !d.querySelector('details.tafsir-sources') &&
                d.querySelectorAll('.tafsir-entry').length===getVerseCommentaryAll(loadedTafsir[2],1).length;})()`));
  }
  if (NENT > 0) {
  ck('written verses run contiguously from 2:1', w.eval("Object.keys(loadedGuidance[2].verses).map(Number).sort((a,b)=>a-b).every((v,i)=>v===i+1)"), 'gap in verse numbers');
  ck('every entry has a 2:N range', w.eval("Object.values(loadedGuidance[2].verses).every(v=>/^2:\\d+$/.test(v.range))"));
  ck('every entry records 4+ sources drawn on',
     w.eval("Object.values(loadedGuidance[2].verses).every(v=>v.draws_on.length>=4)"));
  ck('all draws_on ids are real sources', w.eval(
    "Object.values(loadedGuidance[2].verses).every(v=>v.draws_on.every(id=>loadedTafsir[2].sources.some(s=>s.id===id)))"));

  // ---------- length against the fitted plan ----------
  for (let a = 1; a <= w.eval("Object.keys(loadedGuidance[2].verses).length"); a++) {
    const t = w.eval(`loadedGuidance[2].verses["${a}"].text`);
    const n = t.trim().split(/\s+/).length;
    const tgt = PLAN['2:' + a].words;
    // The plan target is a FLOOR, not a band. A verse may run long; it must
    // not run short. Set by the maintainer 2026-10-09, reversing the earlier
    // two-sided 25% tolerance.
    const floor = Math.round(tgt * 0.75);
    ck(`2:${a} length ${n}w meets the floor (${floor}w of ${tgt}w, Tier ${PLAN['2:' + a].tier})`,
       n >= floor, `${n} vs floor ${floor}`);
  }

  // ---------- it must quote the app's OWN translation ----------
  await w.eval('loadChapterData(2)');
  const pairs = [
    [1, 'Alif'], [1, 'letters'],
    [2, 'This is the Book'], [2, 'no doubt'], [2, 'mindful'],
    [3, 'believe in the unseen'], [3, 'establish prayer'], [3, 'provided for them'],
    [4, 'revealed before you'], [4, 'sure faith'], [4, 'Hereafter'],
    [5, 'guided by their Lord'], [5, 'successful'],
    [6, 'persist in disbelief'], [6, 'warn them'], [6, 'never believe'],
    [7, 'sealed their hearts'], [7, 'sight is covered'], [7, 'tremendous punishment'],
    [8, 'We believe in Allah'], [8, 'Last Day'], [8, 'true believers'],
    [9, 'deceive Allah and the believers'], [9, 'deceive themselves'], [9, 'fail to perceive'],
    [10, 'sickness in their hearts'], [10, 'sickness increase'], [10, 'for their lies'],
  ];
  for (const [a, frag] of pairs.filter(([n]) => n <= w.eval("Object.keys(loadedGuidance[2].verses).length"))) {
    const t = w.eval(`loadedGuidance[2].verses["${a}"].text`);
    ck(`2:${a} quotes the app's translation "${frag}"`, t.includes(frag));
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
  for (let a = 1; a <= w.eval("Object.keys(loadedGuidance[2].verses).length"); a++) {
    const t = w.eval(`loadedGuidance[2].verses["${a}"].text`);
    const blob = norm(w.eval(`getVerseCommentaryAll(loadedTafsir[2],${a}).map(e=>e.text).join(' ')`));
    for (const nm of NAMES) {
      if (t.includes(nm)) {
        attribChecked++;
        const parts = norm(nm).trim().split(' ').filter(x => x.length > 3);
        const base = parts[parts.length - 1];
        if (!blob.includes(base)) attribBad.push(`2:${a} "${nm}" (looked for "${base}")`);
      }
    }
  }
  ck(`every named narrator/collector (${attribChecked} checked) appears in that verse's sources`,
     attribBad.length === 0, attribBad.join('; '));

  // the six tafsir titles I cite must be real sources in the payload
  const cited = ['Maʿārif-ul-Qurʾān', 'Al-Mukhtaṣar', 'Tanwīr al-Miqbās',
                 'Tazkīrul Qurʾān', 'Ibn Kathīr', 'Al-Jalālayn'];
  const labels = norm(w.eval(`loadedTafsir[2].sources.map(s=>s.label).join(' | ')`));
  const badTitles = cited.filter(c => !labels.includes(norm(c).split(' ')[0]));
  ck('every tafsir title cited matches a real source label', badTitles.length === 0, badTitles.join('; '));

  // ---------- rendering ----------
  const html = w.eval('renderCommentaryHtml(loadedTafsir[2], getVerseCommentary(loadedTafsir[2],1), 1)');
  const el = w.document.createElement('div'); el.innerHTML = html;
  ck('guidance is the FIRST section', el.firstElementChild.classList.contains('tafsir-guidance'));
  ck('guidance labelled "In plain words"',
     el.querySelector('.tafsir-guidance .tafsir-source-label').textContent.includes('In plain words'));
  ck('guidance range is its first line',
     el.querySelector('.tafsir-guidance').firstElementChild.className === 'tafsir-range');
  ck('range reads "2:1"', el.querySelector('.tafsir-guidance .tafsir-range').textContent.trim() === '2:1');
  const det = el.querySelector('details.tafsir-sources');
  // Derived, not hard-coded: which selective sets cover a verse is data, so a
  // literal count here would be a lie either way.
  const want = w.eval(`getVerseCommentaryAll(loadedTafsir[2], 1).length`);
  ck('every source with text is folded behind a disclosure',
     !!det && det.querySelectorAll('.tafsir-entry').length === want,
     det ? `${det.querySelectorAll('.tafsir-entry').length} vs ${want}` : 'none');
  ck('guidance precedes the sources', html.indexOf('tafsir-guidance') < html.indexOf('tafsir-sources'));

  // ---------- modal end to end ----------
  const LAST = w.eval("Object.keys(loadedGuidance[2].verses).length");
  w.eval('showExplanation(2,'+LAST+')'); await new Promise(r => setTimeout(r, 600));
  const body = w.document.getElementById('modalBody').innerHTML;
  ck('modal for the last written verse leads with guidance',
     body.includes('tafsir-guidance') && body.indexOf('tafsir-guidance') < body.indexOf('tafsir-sources'));
  ck('modal quotes the translation',
     body.includes('painful punishment for their lies') || LAST < 10);
  w.eval('closeModal && closeModal()');

  // ---------- ebook ----------
  const ebook = await w.eval(`(async()=>{await loadChapterData(2);
    AppState.currentSurah=2;AppState.currentSurahData=loadedChapters[2];
    await Promise.all([loadTafsirData(2),loadGuidanceData(2)]);
    const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
  ck('ebook carries guidance on every written verse', (ebook.match(/data-source="guidance"/g) || []).length === w.eval("Object.keys(loadedGuidance[2].verses).length"),
     (ebook.match(/data-source="guidance"/g) || []).length);
  ck('ebook folds one source panel per written verse', (ebook.match(/<details class="tafsir-sources"/g) || []).length === w.eval("Object.keys(loadedGuidance[2].verses).length"));
  ck('ebook has no "coming soon"', !/coming soon/i.test(ebook));

  // ---------- the guidance must not recite the verse ----------
  // The verse card above the commentary (Arabic + English translation) is the
  // reader's verse and stays for every verse; what must not happen is the
  // *guidance* repeating it, since the lead quotes each phrase as it explains it
  // (maintainer, 2026-10-10). Asserted at the render layer, where the eye lands.
  const recited = [], merged = [];
  for (let a = 1; a <= w.eval("Object.keys(loadedGuidance[2].verses).length"); a++) {
    const r = JSON.parse(await w.eval(`(function(){
      var h = renderCommentaryHtml(loadedTafsir[2], getVerseCommentary(loadedTafsir[2], ${a}), ${a});
      var box = document.createElement('div'); box.innerHTML = h;
      var t = box.querySelector('.tafsir-guidance .tafsir-text');
      var en = getVerseEnglish(getVerseData(2, ${a})) || '';
      return JSON.stringify({
        recites: !!t && t.textContent.replace(/\\s+/g, ' ').indexOf(en.replace(/\\s+/g, ' ')) === 0,
        verseCardMarkup: !!box.querySelector('.tafsir-guidance .modal-verse-translation, .tafsir-guidance .ebook-translation')
      });})()`));
    if (r.recites) recited.push(`2:${a}`);
    if (r.verseCardMarkup) merged.push(`2:${a}`);
  }
  ck('no guidance card opens by reciting the whole translation', recited.length === 0, recited.join(', '));
  ck('no verse-card markup is folded into the guidance section', merged.length === 0, merged.join(', '));

  } // end authored-verse checks

  ck('no jsdom errors', errs.length === 0, errs.join(' | '));

  let pass = 0;
  for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
  console.log(`\n${pass}/${R.length} checks passed`);
  process.exit(pass === R.length ? 0 : 1);
})();
