// 输出所有 FAIL 行号
const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');
const txt = fs.readFileSync(process.argv[2], 'utf-8');
const n = txt.length;
let fail = [], total = 0, inCode = false, i = 0;
function L(pos){ return txt.slice(0,pos).split('\n').length; }
while (i < n) {
  if (txt.startsWith('```', i)) { inCode = !inCode; i += 3; continue; }
  if (inCode) { i++; continue; }
  if (txt[i] === '\\' && txt[i+1] === '$') { i += 2; continue; }
  if (txt[i] === '$') {
    if (txt.startsWith('$$', i)) {
      let j = txt.indexOf('$$', i+2);
      if (j === -1) { total++; fail.push(L(i)); i = n; }
      else { total++; try { katex.renderToString(txt.slice(i+2,j), {throwOnError:true, strict:false, displayMode:true}); } catch(e) { fail.push(L(i)); } i = j+2; }
      continue;
    } else {
      let j = txt.indexOf('$', i+1);
      if (j === -1) { total++; fail.push(L(i)); i = n; }
      else { total++; try { katex.renderToString(txt.slice(i+1,j), {throwOnError:true, strict:false}); } catch(e) { fail.push(L(i)); } i = j+1; }
      continue;
    }
  }
  i++;
}
const uniq = [...new Set(fail)].sort((a,b)=>a-b);
console.log('TOTAL='+total+' FAIL='+fail.length+' 唯一行='+uniq.length);
console.log(uniq.join(','));
