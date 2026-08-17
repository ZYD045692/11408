// 只验证单行公式，避免跨行误报
const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');

const file = process.argv[2];
const content = fs.readFileSync(file, 'utf-8');
const lines = content.split('\n');
let total = 0, fail = 0;
const failures = [];

for (let i = 0; i < lines.length; i++) {
  const ln = lines[i];
  // 处理单行块级 $$...$$（同一行内）
  const blockSingle = ln.match(/\$\$([^$]+)\$\$/);
  if (blockSingle) {
    total++;
    try { katex.renderToString(blockSingle[1], { throwOnError: true, strict: false, displayMode: true }); }
    catch (e) { fail++; failures.push({ line: i+1, formula: blockSingle[1].slice(0,80), err: e.message.split('\n')[0].slice(0,60) }); }
  }
  // 处理行内 $...$（非贪婪，同一行）
  const inlineRe = /\$([^$]+?)\$/g;
  let m;
  while ((m = inlineRe.exec(ln)) !== null) {
    // 跳过块级内的（单行块级已处理）
    if (blockSingle) continue;
    total++;
    try { katex.renderToString(m[1], { throwOnError: true, strict: false }); }
    catch (e) { fail++; failures.push({ line: i+1, formula: m[1].slice(0,80), err: e.message.split('\n')[0].slice(0,60) }); }
  }
}
console.log(`${file}: TOTAL=${total} FAIL=${fail}`);
for (const f of failures.slice(0, 30)) {
  console.log(`L${f.line}: ${f.formula}`);
  console.log(`   ${f.err}`);
}
