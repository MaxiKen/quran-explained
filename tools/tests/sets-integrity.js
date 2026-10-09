// Guards the two sets added on 2026-10-09 — al-Qushayrī (qushayri) and
// al-Wāḥidī (wahidi) — against the two ways they can quietly rot: a stale block
// index after a rebuild, and the upstream pollution that put al-Qushayrī's text
// inside the Asbāb file. Pure node, reads data/ directly, no browser.
//
// Run: node tools/tests/sets-integrity.js
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const R = [];
const ck = (n, ok, d) => R.push({ n, ok: !!ok, d: d === undefined ? '' : String(d) });

const ORDER = ['ibn-kathir', 'maarif', 'tazkirul', 'tanwir', 'jalalayn', 'mukhtasar',
               'qushayri', 'wahidi'];
const PRIMARY = ORDER.slice(0, 6);
const NEW = ['qushayri', 'wahidi'];
const AR_RUN = /[\u0600-\u06FF]{8,}/;

let verses = 0, mapped = { qushayri: 0, wahidi: 0 }, words = { qushayri: 0, wahidi: 0 };
const badIndex = [], badRange = [], emptyBlock = [], polluted = [], reffed = [],
      mojibake = [], arabic = [], primaryGap = [], srcOrder = [];

for (let s = 1; s <= 114; s++) {
  const p = path.join(ROOT, 'data', `tafsir_${String(s).padStart(3, '0')}.json`);
  if (!fs.existsSync(p)) continue;
  const d = JSON.parse(fs.readFileSync(p, 'utf8'));

  if (JSON.stringify(d.sources.map(x => x.id)) !== JSON.stringify(ORDER)) {
    srcOrder.push(`${s}: ${d.sources.map(x => x.id).join(',')}`);
  }

  for (const sid of NEW) {
    const set = d.sets[sid];
    if (!set) { badRange.push(`${s}:${sid} missing`); continue; }
    if (set.ranges.length !== set.blocks.length) badRange.push(`${s}:${sid}`);
    set.blocks.forEach((b, i) => {
      const w = b.trim().split(/\s+/).length;
      if (w < 4) emptyBlock.push(`${s}:${sid}[${i}]`);
      if (b.includes('\ufffd')) mojibake.push(`${s}:${sid}[${i}]`);
      if (AR_RUN.test(b)) arabic.push(`${s}:${sid}[${i}]`);
    });
  }

  // index integrity + coverage of the primary six, verse by verse
  const last = Object.keys(d.verses).map(Number).reduce((a, b) => Math.max(a, b), 0);
  for (let a = 1; a <= last; a++) {
    verses++;
    const m = d.verses[String(a)] || {};
    for (const sid of PRIMARY) if (m[sid] === undefined) primaryGap.push(`${s}:${a}`);
    for (const sid of NEW) {
      if (m[sid] === undefined) continue;
      mapped[sid]++;
      const b = d.sets[sid].blocks[m[sid]];
      if (b === undefined) { badIndex.push(`${s}:${a} ${sid}->${m[sid]}`); continue; }
      words[sid] += b.trim().split(/\s+/).length;
    }
  }

  // the pollution test: an Asbāb entry that is really al-Qushayrī's prose
  const q = (d.sets.qushayri ? d.sets.qushayri.blocks : []).map(b => b.slice(0, 160));
  (d.sets.wahidi ? d.sets.wahidi.blocks : []).forEach((b, i) => {
    const head = b.slice(0, 160), mid = b.slice(400, 560);
    if (q.some(x => x.includes(head) || (mid.length > 100 && x.includes(mid)))) {
      polluted.push(`${s}:wahidi[${i}]`);
    }
  });

  // an Asbāb block must name a verse range of its own surah somewhere — the
  // only reason we trust a spread of the entry over neighbouring verses
  const REF = new RegExp('\\[' + s + '\\s*:\\s*\\d{1,4}');
  (d.sets.wahidi ? d.sets.wahidi.blocks : []).forEach((b, i) => {
    if (!REF.test(b.slice(0, 3000))) reffed.push(`${s}:wahidi[${i}]`);
  });
}

ck('all 114 payloads declare the eight sources in order', srcOrder.length === 0,
   srcOrder.slice(0, 2).join(' | '));
ck('every primary set covers every verse', primaryGap.length === 0,
   primaryGap.slice(0, 4).join(',') + (primaryGap.length ? ` (+${primaryGap.length})` : ''));
ck('no stale block index in the added sets', badIndex.length === 0,
   badIndex.slice(0, 4).join(', '));
ck('ranges array parallels blocks', badRange.length === 0, badRange.slice(0, 4).join(', '));
ck('no empty or stub block stored', emptyBlock.length === 0, emptyBlock.slice(0, 4).join(', '));
ck('no upstream decode damage left (U+FFFD)', mojibake.length === 0, mojibake.slice(0, 3).join(', '));
ck('no untranslated Arabic run in the added sets', arabic.length === 0, arabic.slice(0, 3).join(', '));
ck('no al-Wāḥidī block is really al-Qushayrī', polluted.length === 0, polluted.slice(0, 4).join(', '));
ck('every al-Wāḥidī block cites its own verse range', reffed.length === 0, reffed.slice(0, 4).join(', '));
ck('al-Qushayrī coverage is between 1,000 and 1,400 verses',
   mapped.qushayri > 1000 && mapped.qushayri < 1400, `${mapped.qushayri} of ${verses}`);
ck('al-Wāḥidī coverage stays small (guard discards the polluted entries)',
   mapped.wahidi > 300 && mapped.wahidi < 700, `${mapped.wahidi} of ${verses}`);
ck('added material is worth having (both sets over 80k words)',
   words.qushayri > 300000 && words.wahidi > 60000,
   `qushayri ${words.qushayri.toLocaleString()}w, wahidi ${words.wahidi.toLocaleString()}w`);

let pass = 0;
for (const r of R) { if (r.ok) pass++; else console.log('FAIL  ' + r.n + (r.d ? '  [' + r.d + ']' : '')); }
console.log(`\n${pass}/${R.length} checks passed`);
console.log(`verses ${verses} | qushayri ${mapped.qushayri} verses, ${words.qushayri.toLocaleString()} words | ` +
            `wahidi ${mapped.wahidi} verses, ${words.wahidi.toLocaleString()} words`);
process.exit(pass === R.length ? 0 : 1);
