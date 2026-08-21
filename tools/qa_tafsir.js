/* QA sweep for a rewritten tafsir file.
   Usage: node tools/qa_tafsir.js <chapterNum> */
const fs = require('fs');
const path = require('path');
const repo = path.resolve(__dirname, '..');
const num = process.argv[2];
const pad = String(num).padStart(3, '0');
const file = path.join(repo, 'data', `tafsir_${pad}.js`);
const sandbox = {};
new Function(`${fs.readFileSync(file, 'utf8')}\nthis.__out = tafsirData_${num};`).call(sandbox);
const data = sandbox.__out;

const patterns = {
  'vague-quran-ref': /(the Quran says elsewhere|another verse says|elsewhere in the Quran, it says)/i,
  'unattributed-scholars': /(scholars say|it is said that|commentators say|some say\b|many scholars|scholars have said|classical scholars)/i,
  'grouped-attribution': /including al-Tabari, al-Qurtubi, and Ibn Kathir/i,
  'html-markup': /<[a-zA-Z/][^>]*>/,
};
const collections = /(Sahih al-Bukhari|Sahih Muslim|Jami' at-Tirmidhi|Sunan Abi Dawud|Sunan an-Nasa'i|Sunan Ibn Majah|Musnad Ahmad)/g;

let issues = 0;
const keys = Object.keys(data);
for (const k of keys) {
  const v = data[k];
  if (typeof v !== 'string') { console.log(`NON-STRING value at key ${k}`); issues++; continue; }
  for (const [name, re] of Object.entries(patterns)) {
    const m = v.match(re);
    if (m) { console.log(`${name} @ ${k}: ...${v.slice(Math.max(0, v.indexOf(m[0]) - 50), v.indexOf(m[0]) + m[0].length + 30).replace(/\n/g, ' ')}...`); issues++; }
  }
  let m;
  collections.lastIndex = 0;
  while ((m = collections.exec(v)) !== null) {
    if (!/^\s+\d/.test(v.slice(m.index + m[0].length))) {
      console.log(`hadith-without-number @ ${k}: ${m[0]}`); issues++;
    }
  }
}
const contiguous = keys.every((k, i) => Number(k) === i + 1);
const words = keys.map(k => String(data[k]).split(/\s+/).length);
console.log(`keys=${keys.length} contiguous=${contiguous}`);
console.log(`words: min=${Math.min(...words)} max=${Math.max(...words)} avg=${Math.round(words.reduce((a, b) => a + b, 0) / words.length)}`);
console.log(issues === 0 ? 'QA CLEAN' : `QA ISSUES: ${issues}`);
