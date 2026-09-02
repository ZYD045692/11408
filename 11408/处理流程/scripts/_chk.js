const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');
const file = process.argv[2];
const lines = fs.readFileSync(file, 'utf-8').split('\n');
for (let i = 0; i < lines.length; i++) {
  const ln = lines[i];
  const blockSingle = ln.match(/\$\$([^$]+)\$\$/);
  if (blockSingle) {
    try { katex.renderToString(blockSingle[1], { throwOnError: true, strict: false, displayMode: true }); }
    catch (e) { console.log(`L${i+1} BLOCK: ${blockSingle[1].slice(0, 60)} || ${e.message.slice(0, 50)}`); }
    continue;
  }
  const re = /\$([^$]+?)\$/g;
  let m;
  while ((m = re.exec(ln))) {
    try { katex.renderToString(m[1], { throwOnError: true, strict: false }); }
    catch (e) { console.log(`L${i+1} INLINE: ${m[1].slice(0, 60)} || ${e.message.slice(0, 50)}`); }
  }
}
