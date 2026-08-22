/* Show verse text + current tafsir for a range.
   Usage: node /tmp/show.js <chapter> <from> <to> [--v]   (--v = verse text only) */
const fs = require('fs');
const path = require('path');
const repo = path.resolve(__dirname, '..');
const ch = process.argv[2], from = +process.argv[3], to = +process.argv[4];
const verseOnly = process.argv.includes('--v');
const pad = String(ch).padStart(3, '0');

function load(file, varName) {
  const sandbox = {};
  new Function(`${fs.readFileSync(file, 'utf8')}\nthis.__out = ${varName};`).call(sandbox);
  return sandbox.__out;
}
const verses = {};
for (const theme of load(path.join(repo, 'data', `chapter_${pad}.js`), `chapterData_${ch}`)) {
  for (const v of theme.verses) verses[v.ayah_no_surah] = v.ayah_en;
}
const tafsir = load(path.join(repo, 'data', `tafsir_${pad}.js`), `tafsirData_${ch}`);

for (let i = from; i <= to; i++) {
  console.log(`\n######## ${ch}:${i} ########`);
  console.log(`[VERSE] ${verses[i]}`);
  if (!verseOnly) console.log(`[TAFSIR]\n${tafsir[i]}`);
}
