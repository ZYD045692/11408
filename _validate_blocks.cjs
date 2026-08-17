// 校验 md 全文的公式，含跨行 $$...$$ 块。按错误类型分类统计。
const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');
const file = process.argv[2];
const txt = fs.readFileSync(file, 'utf-8');

const stats = {};   // type -> count
const samples = {}; // type -> [line, msg, src]

function classify(msg) {
  if (msg.includes("Can't use function '$'")) return "块内嵌行内$";
  if (msg.includes("Undefined control sequence")) return "未知命令";
  if (msg.includes("Expected & or \\\\ or \\cr or \\end")) return "cases/array未闭合";
  if (msg.includes("Expected 'EOF'")) return "未闭合括号";
  if (msg.includes("Double subscript")) return "双下标";
  if (msg.includes("Missing { inserted")) return "缺{";
  if (msg.includes("Missing } inserted")) return "缺}";
  if (msg.includes("Unsupported")) return "不支持语法";
  return "其他: " + msg.slice(0, 40);
}

function add(type, line, msg, src) {
  stats[type] = (stats[type] || 0) + 1;
  if (!samples[type]) samples[type] = [];
  if (samples[type].length < 2) samples[type].push([line, msg, src]);
}

const blockRe = /\$\$([\s\S]*?)\$\$/g;
let m;
let total = 0;
while ((m = blockRe.exec(txt)) !== null) {
  total++;
  const lineNo = txt.slice(0, m.index).split('\n').length;
  try { katex.renderToString(m[1], { throwOnError: true, strict: false, displayMode: true }); }
  catch (e) { add(classify(e.message), lineNo, e.message, m[1].slice(0, 70)); }
}
console.log(`BLOCK_TOTAL=${total}`);
for (const [t, n] of Object.entries(stats).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${t}: ${n}`);
  for (const [ln, msg, src] of samples[t] || []) {
    console.log(`    L${ln} ${src.replace(/\n/g, ' ')}`);
  }
}
