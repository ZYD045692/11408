// 批量校验目录下所有 md 的公式
const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');
const path = require('path');

function walk(dir, files = []) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) walk(p, files);
    else if (p.endsWith('.md')) files.push(p);
  }
  return files;
}

const files = walk(process.argv[2]);
let total = 0, fail = 0;
const badFiles = [];
for (const file of files) {
  const content = fs.readFileSync(file, 'utf-8');
  const lines = content.split('\n');
  let ft = 0, ff = 0;
  for (const ln of lines) {
    const blockSingle = ln.match(/\$\$([^$]+)\$\$/);
    if (blockSingle) {
      ft++;
      try { katex.renderToString(blockSingle[1], { throwOnError: true, strict: false, displayMode: true }); }
      catch (e) { ff++; }
    }
    const inlineRe = /\$([^$]+?)\$/g;
    let m;
    while ((m = inlineRe.exec(ln)) !== null) {
      if (blockSingle) continue;
      ft++;
      try { katex.renderToString(m[1], { throwOnError: true, strict: false }); }
      catch (e) { ff++; }
    }
  }
  total += ft; fail += ff;
  if (ff > 0) badFiles.push({ file, ff });
}
console.log(`TOTAL=${total} FAIL=${fail}`);
for (const b of badFiles.sort((a,b)=>b.ff-a.ff).slice(0,15)) {
  console.log(`  FAIL=${b.ff} ${b.file}`);
}
