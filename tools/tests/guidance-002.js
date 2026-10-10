/*
 * Chapter 2's authored-layer regression checks for the current 2:36–2:40 batch.
 * The generic guidance-range suite covers layout and rendering for every verse;
 * this focused suite adds the app translation fragments and source-attribution
 * assertions that the generic suite intentionally does not hand-maintain.
 *
 * Run: BASE=http://127.0.0.1:8090 NODE_PATH=/tmp/apptest/node_modules node tools/tests/guidance-002.js
 */
const { JSDOM, VirtualConsole } = require('/tmp/apptest/node_modules/jsdom');
const BASE = process.env.BASE || 'http://127.0.0.1:8000';
const vc = new VirtualConsole();
const errs = [];
vc.on('jsdomError', e => errs.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errs.push('console.error: ' + a.join(' ')));

const BATCH = [36, 37, 38, 39, 40];
const FRAGMENTS = {
  36: ['But Satan deceived them', 'leading to their fall from the', 'Descend from the heavens', 'a residence and provision for your appointed stay'],
  37: ['Then Adam was inspired with words', 'so He accepted his repentance', 'Accepter of Repentance', 'Most Merciful'],
  38: ['We said, Descend all of you', 'guidance comes to you from Me', 'whoever follows it', 'there will be no fear for them', 'nor will they grieve'],
  39: ['those who disbelieve and deny Our signs', 'residents of the Fire', 'They will be there forever'],
  40: ['O children of Israel!', 'Remember My favours upon you', 'Fulfil your covenant and I will fulfil Mine', 'stand in awe of Me'],
};
const NAMES = {
  36: ['Al-Hasan', 'Qatadah', "Abu Ja'far bin Jarir"],
  37: ['Mujahid', "Sa'id bin Jubayr", 'Abu al-Aliyah', 'Al-Hasan', 'Qatadah', 'As-Suddi', 'Ibn Abbas', 'Al-Hakim', 'Ibn Jubayr', 'Al-Bukhari', 'Muslim'],
  38: ['Abu al-Aliyah'],
  39: [],
  40: ['Mujahid', 'Abu al-Aliyah', 'Qatadah', 'Ibn Abbas', 'Ad-Dahhak', 'Muslim'],
};
const fold = s => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[^a-z0-9]+/g, '');
const nameForms = s => [s, s.replace(/\bibn\b/gi, 'bin'), s.replace(/\bbin\b/gi, 'ibn')].map(fold);

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

  const R = [];
  const ck = (n, ok, d = '') => R.push({ n, ok: !!ok, d: String(d) });
  await w.eval('loadChapterData(2)');
  await w.eval('loadTafsirData(2)');
  const g = await w.eval('loadGuidanceData(2)');
  ck('chapter 2 guidance loads', !!g);
  const keys = g ? Object.keys(g.verses).map(Number).sort((a, b) => a - b) : [];
  ck('chapter 2 remains sequential through 2:40', keys.length === 40 && keys.every((a, i) => a === i + 1), keys.length);

  for (const a of BATCH) {
    const v = g && g.verses[String(a)];
    ck(`2:${a} has the correct range and source ids`, !!v && v.range === `2:${a}` &&
      v.draws_on.length >= 5 && v.draws_on.every(id => w.eval(`loadedTafsir[2].sources.some(s=>s.id===${JSON.stringify(id)})`)));
    const text = v ? v.text : '';
    for (const frag of FRAGMENTS[a]) {
      ck(`2:${a} quotes app wording: “${frag}”`, text.includes(frag));
    }

    const sourceText = await w.eval(`getVerseCommentaryAll(loadedTafsir[2], ${a}).map(e=>e.text).join(' ')`);
    const foldedBody = fold(text), foldedSources = fold(sourceText);
    for (const name of NAMES[a]) {
      const forms = nameForms(name);
      ck(`2:${a} attribution “${name}” is in this verse's source`,
        forms.some(f => foldedBody.includes(f)) && forms.some(f => foldedSources.includes(f)));
    }
  }

  ck('no jsdom errors', errs.length === 0, errs.slice(0, 3).join(' | '));
  const failed = R.filter(r => !r.ok);
  for (const r of failed) console.log(`FAIL  ${r.n}${r.d ? `  [${r.d}]` : ''}`);
  console.log(`\n${R.length - failed.length}/${R.length} checks passed`);
  process.exit(failed.length ? 1 : 0);
})();
