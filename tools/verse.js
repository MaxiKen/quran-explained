/* Look up the exact English text the app uses for any verse.
   Usage: node /tmp/verse.js 7:156 4:69 40:16 ... */
const fs = require('fs');
const path = require('path');
const repo = path.resolve(__dirname, '..');

function get(ch, ay) {
  const file = path.join(repo, 'data', `chapter_${String(ch).padStart(3, '0')}.js`);
  const src = fs.readFileSync(file, 'utf8');
  const sandbox = {};
  new Function(`${src}\nthis.__out = chapterData_${ch};`).call(sandbox);
  for (const theme of sandbox.__out) {
    for (const v of theme.verses) {
      if (Number(v.ayah_no_surah) === Number(ay)) return v.ayah_en;
    }
  }
  return null;
}

for (const arg of process.argv.slice(2)) {
  const [c, a] = arg.split(':');
  console.log(`--- Quran ${c}:${a} ---`);
  console.log(get(c, a));
  console.log();
}
