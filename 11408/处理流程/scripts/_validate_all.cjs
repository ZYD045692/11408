// 全文公式校验：状态机提取 $$...$$ 和 $...$（含跨行行内），逐个 KaTeX
// 用法: node _validate_all.cjs <md>
const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');
const txt = fs.readFileSync(process.argv[2], 'utf-8');
const n = txt.length;

let fail = 0, total = 0;
let inCode = false;
let i = 0;
let firstFails = [];

function render(src, display, line) {
  total++;
  try { katex.renderToString(src, {throwOnError:true, strict:false, displayMode:display}); }
  catch(e) {
    fail++;
    if (firstFails.length < 8) firstFails.push(`L${line} ${display?'BLOCK':'INLINE'} ${e.message.slice(0,45)} | ${src.slice(0,60).replace(/\n/g,' ')}`);
  }
}

while (i < n) {
  if (txt.startsWith('```', i)) { inCode = !inCode; i += 3; continue; }
  if (inCode) { i++; continue; }
  if (txt[i] === '\\' && txt[i+1] === '$') { i += 2; continue; }
  if (txt[i] === '$') {
    if (txt.startsWith('$$', i)) {
      // 找闭 $$
      let j = txt.indexOf('$$', i + 2);
      if (j === -1) { render(txt.slice(i+2), true, txt.slice(0,i).split('\n').length); i = n; }
      else { render(txt.slice(i+2, j), true, txt.slice(0,i).split('\n').length); i = j + 2; }
      continue;
    } else {
      // 找闭 $
      let j = txt.indexOf('$', i + 1);
      if (j === -1) { render(txt.slice(i+1), false, txt.slice(0,i).split('\n').length); i = n; }
      else { render(txt.slice(i+1, j), false, txt.slice(0,i).split('\n').length); i = j + 1; }
      continue;
    }
  }
  i++;
}
console.log(`TOTAL=${total} FAIL=${fail}`);
for (const f of firstFails) console.log('  ' + f);
