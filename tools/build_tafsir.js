/* Merge authored plain-text tafsir batches into data/tafsir_XXX.js
   Usage: node /tmp/build_tafsir.js <chapterNum> <batchFile>
   Batch file format:
     ===<verse>===
     paragraph text
     (blank line)
     paragraph text
   Existing keys are replaced; untouched keys are preserved; output is
   written as `var tafsirData_N = { ... };` with 2-space JSON indentation
   and keys in ascending numeric order (matching the original files). */
const fs = require('fs');
const path = require('path');

const num = process.argv[2];
const batchFile = process.argv[3];
const repo = path.resolve(__dirname, '..');
const target = path.join(repo, 'data', `tafsir_${String(num).padStart(3, '0')}.js`);

const varName = `tafsirData_${num}`;
const src = fs.readFileSync(target, 'utf8');
const sandbox = {};
// eslint-disable-next-line no-new-func
new Function(`${src}\nthis.__out = ${varName};`).call(sandbox);
const data = sandbox.__out;

const raw = fs.readFileSync(batchFile, 'utf8');
const parts = raw.split(/^===(\d+)===$/m);
let updated = 0;
for (let i = 1; i < parts.length; i += 2) {
  const key = parts[i].trim();
  let body = parts[i + 1];
  body = body.replace(/\r/g, '').replace(/^\n+/, '').replace(/\n+$/, '');
  body = body.split('\n').map(l => l.replace(/[ \t]+$/, '')).join('\n');
  body = body.replace(/\n{3,}/g, '\n\n');
  if (!body) throw new Error(`Empty body for verse ${key}`);
  data[key] = body;
  updated++;
}

const ordered = {};
Object.keys(data).sort((a, b) => Number(a) - Number(b)).forEach(k => { ordered[k] = data[k]; });
fs.writeFileSync(target, `var ${varName} = ${JSON.stringify(ordered, null, 2)};\n`);
console.log(`${path.basename(target)}: updated ${updated} entries, total ${Object.keys(ordered).length}`);
