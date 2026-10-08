const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const vc = new VirtualConsole(); const errs = [];
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

const S = 2, LO = 1, HI = 7;          // verses authored so far
const LAST = 286;                      // verses in the surah

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
  await w.eval(`Promise.all([loadTafsirData(${S}), loadGuidanceData(${S})])`);

  ck(`guidance_${String(S).padStart(3,'0')} loads`, await w.eval(`!!loadedGuidance[${S}]`));
  ck(`covers exactly verses ${LO}-${HI}`,
     w.eval(`Object.keys(loadedGuidance[${S}].verses).join(',')`) === Array.from({length: HI-LO+1}, (_,i)=>LO+i).join(','),
     w.eval(`Object.keys(loadedGuidance[${S}].verses).join(',')`));
  ck('every entry has a correct range', w.eval(`Object.entries(loadedGuidance[${S}].verses).every(([a,v])=>v.range==="${S}:"+a)`));
  ck('every entry records 5+ sources drawn on', w.eval(`Object.values(loadedGuidance[${S}].verses).every(v=>v.draws_on.length>=5)`));
  ck('all draws_on ids are real sources', w.eval(`Object.values(loadedGuidance[${S}].verses).every(v=>v.draws_on.every(id=>loadedTafsir[${S}].sources.some(s=>s.id===id)))`));

  for (let a = LO; a <= HI; a++) {
    const n = w.eval(`loadedGuidance[${S}].verses["${a}"].text.trim().split(/\\s+/).length`);
    const tgt = PLAN[`${S}:${a}`].words;
    ck(`${S}:${a} length ${n}w within 25% of plan (${tgt}w, Tier ${PLAN[`${S}:${a}`].tier})`,
       Math.abs(n - tgt) / tgt <= 0.25, `${n} vs ${tgt}`);
  }

  // ---------- quotes the app's own translation ----------
  await w.eval(`loadChapterData(${S})`);
  const pairs = [
    [1, 'Alif-Lãm-Mĩm'],
    [2, 'This is the Book'], [2, 'no doubt about it'], [2, 'mindful'],
    [3, 'the unseen'], [3, 'establish prayer'], [3, 'what We have provided'],
    [4, 'revealed before you'], [4, 'sure faith in the Hereafter'],
    [5, 'guided by their Lord'], [5, 'successful'],
    [6, 'persist in disbelief'], [6, 'whether you warn them or not'],
    [7, 'sealed their hearts'], [7, 'sight is covered'], [7, 'tremendous punishment'],
  ];
  for (const [a, frag] of pairs) {
    ck(`${S}:${a} quotes the translation "${frag}"`, w.eval(`loadedGuidance[${S}].verses["${a}"].text`).includes(frag));
  }

  // ---------- integrity: named authorities must appear in that verse's sources ----------
  // Narrators and collectors only. The six tafsir TITLES are verified separately
  // against the payload's labels — a work does not cite itself in its own body.
  const NAMES = ['Al-Qurṭubī', 'Imām Aḥmad', 'Muslim', 'at-Tirmidhī',
    'an-Nasāʾī', 'Ibn Mājah', 'Al-Bukhārī', 'Abū Hurayrah', 'Ibn Masʿūd', 'al-Ḥākim',
    'Ad-Dārimī', 'ash-Shaʿbī', 'aṭ-Ṭabarānī', 'Ibn Ḥibbān', 'Ibn Marduwayh',
    'Usayd ibn Ḥuḍayr', 'As-Suddī', 'Abū Mālik', 'Abū Ṣāliḥ', 'Ibn ʿAbbās',
    'Murrah al-Hamadhānī', 'Abū ad-Dardāʾ', 'Mujāhid', 'Saʿīd ibn Jubayr', 'Nāfiʿ',
    'ʿAṭāʾ', 'Abū al-ʿĀliyah', 'ar-Rabīʿ ibn Anas', 'Muqātil ibn Ḥayyān', 'Qatādah',
    'Ismāʿīl ibn Abī Khālid', 'Ibn Abī Ḥātim', 'Abū Jaʿfar ar-Rāzī', 'Abū Isḥāq',
    'Abū al-Aḥwaṣ', 'ʿAlī ibn Abī Ṭalḥah', 'Maʿmar', 'az-Zuhrī', 'Ibn Jarīr',
    'Qatādah ibn Diʿāmah', 'ʿAbdullāh ibn Masʿūd', 'Ibn Jurayj', 'ʿAbdullāh ibn Kathīr',
    'Al-Aʿmash', 'Ḥudhayfah', 'Kaʿb ibn al-Ashraf', 'Ḥuyayy ibn Akhṭab', 'Judayy ibn Akhṭab',
    'ʿUtbah ibn Rabīʿah', 'Shaybah ibn Rabīʿah', 'al-Walīd ibn al-Mughīrah',
    'Abū Jahl', 'Abū Lahab'];
  const TITLES = ['Maʿārif-ul-Qurʾān', 'Tazkīrul Qurʾān', 'Al-Mukhtaṣar', 'Tanwīr al-Miqbās',
                  'Al-Jalālayn', 'Ibn Kathīr'];
  // fold diacritics/hamzas AND drop spaces, so "Ibn Masʿūd" matches the sources' "Ibn Mas'ud"
  const norm = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[\u02bf\u02be\u02bc`'\u2019\u2018\-\s]/g, '').toLowerCase();

  // same person, different romanisation in the source corpus
  const VARIANTS = {
    'Ibn Marduwayh':       ['marduwyah', 'marduwayh'],
    'Murrah al-Hamadhānī': ['al-hamadani', 'alhamadhani'],
  };
  let checked = 0; const bad = [];
  for (let a = LO; a <= HI; a++) {
    const t = w.eval(`loadedGuidance[${S}].verses["${a}"].text`);
    // include sources for any verse in this surah that the prose explicitly cites
    const also = new Set([a]);
    for (const m of t.matchAll(new RegExp(`\\b${S}:(\\d+)\\b`, 'g'))) also.add(Number(m[1]));
    const blob = norm([...also].map(n =>
      w.eval(`getVerseCommentaryAll(loadedTafsir[${S}],${n}).map(e=>e.text).join(' ')`)).join(' '));
    for (const nm of NAMES) {
      if (!t.includes(nm)) continue;
      checked++;
      const parts = nm.normalize('NFD').replace(/[\u0300-\u036f]/g, '').split(/\s+/).filter(x => x.length > 3);
      const base = norm(parts[parts.length - 1] || nm);
      const ok = VARIANTS[nm] ? VARIANTS[nm].some(v => blob.includes(norm(v)))
                              : base.length > 2 && blob.includes(base);
      if (!ok) bad.push(`${S}:${a} "${nm}" (wanted "${base}")`);
    }
  }
  ck(`every named authority (${checked} checked) appears in that verse's sources`, bad.length === 0, bad.join('; '));

  const labels = norm(w.eval(`loadedTafsir[${S}].sources.map(s=>s.label).join(' | ')`));
  const badTitles = TITLES.filter(t => !labels.includes(norm(t).split(' ')[0]));
  ck('every tafsir title cited matches a real source label', badTitles.length === 0, badTitles.join('; '));

  // ---------- rendering ----------
  const html = w.eval(`renderCommentaryHtml(loadedTafsir[${S}], getVerseCommentary(loadedTafsir[${S}],${LO}), ${LO})`);
  const el = w.document.createElement('div'); el.innerHTML = html;
  ck('guidance is the FIRST section', el.firstElementChild.classList.contains('tafsir-guidance'));
  ck('guidance range is its first line', el.querySelector('.tafsir-guidance').firstElementChild.className === 'tafsir-range');
  ck(`range reads "${S}:${LO}"`, el.querySelector('.tafsir-guidance .tafsir-range').textContent.trim() === `${S}:${LO}`);
  const det = el.querySelector('details.tafsir-sources');
  ck('six sources folded behind a disclosure', !!det && det.querySelectorAll('.tafsir-entry').length === 6,
     det ? det.querySelectorAll('.tafsir-entry').length : 'none');

  // ---------- PARTIAL FILE: unauthorised verses must fall back ----------
  for (const a of [8, 9, 100, 286]) {
    const g = w.eval(`renderGuidanceHtml(loadedGuidance[${S}], ${a})`);
    ck(`${S}:${a} (not yet authored) yields no guidance`, g === '', JSON.stringify(g).slice(0, 60));
    const h = w.eval(`renderCommentaryHtml(loadedTafsir[${S}], getVerseCommentary(loadedTafsir[${S}],${a}), ${a})`);
    const e = w.document.createElement('div'); e.innerHTML = h;
    ck(`${S}:${a} falls back to six sources directly`, e.querySelectorAll('.tafsir-entry').length === 6,
       e.querySelectorAll('.tafsir-entry').length);
    ck(`${S}:${a} shows no disclosure`, !e.querySelector('details.tafsir-sources'));
    ck(`${S}:${a} first source marked primary`, e.querySelector('.tafsir-entry').classList.contains('tafsir-entry-primary'));
  }

  // ---------- modal ----------
  w.eval(`showExplanation(${S},3)`); await new Promise(r => setTimeout(r, 600));
  const body = w.document.getElementById('modalBody').innerHTML;
  ck('modal for 2:3 leads with guidance', body.includes('tafsir-guidance') && body.indexOf('tafsir-guidance') < body.indexOf('tafsir-sources'));
  ck('modal quotes the translation', body.includes('establish prayer'));

  // ---------- ebook: mixed authored / unauthorised ----------
  const ebook = await w.eval(`(async()=>{await loadChapterData(${S});
    AppState.currentSurah=${S};AppState.currentSurahData=loadedChapters[${S}];
    await Promise.all([loadTafsirData(${S}),loadGuidanceData(${S})]);
    const d=document.createElement('div');renderCompleteCommentary(d);return d.innerHTML;})()`);
  const gcount = (ebook.match(/data-source="guidance"/g) || []).length;
  ck(`ebook carries guidance on exactly the ${HI - LO + 1} authored verses`, gcount === HI - LO + 1, gcount);
  ck('ebook has no "coming soon"', !/coming soon/i.test(ebook));

  ck('no jsdom errors', errs.length === 0, errs.join(' | '));

  let pass = 0;
  for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
  console.log(`\n${pass}/${R.length} checks passed`);
  process.exit(pass === R.length ? 0 : 1);
})().catch(e => { console.error('HARNESS ERROR:', e); process.exit(2); });
