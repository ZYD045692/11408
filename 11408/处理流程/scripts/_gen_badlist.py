# -*- coding: utf-8 -*-
# 生成坏公式清单（高数 + 线代），标注截断情况
import io, sys, os, re, glob, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CHK = r'''
const katex = require(process.env.TEMP + '/node_modules/katex');
const fs = require('fs');
const file = process.argv[2];
const lines = fs.readFileSync(file, 'utf-8').split('\n');
for (let i = 0; i < lines.length; i++) {
  const ln = lines[i];
  const blockSingle = ln.match(/\$\$([^$]+)\$\$/);
  if (blockSingle) {
    try { katex.renderToString(blockSingle[1], { throwOnError: true, strict: false, displayMode: true }); }
    catch (e) { console.log(`L${i+1} BLOCK: ${blockSingle[1].slice(0, 50)}`); }
    continue;
  }
  const re = /\$([^$]+?)\$/g;
  let m;
  while ((m = re.exec(ln))) {
    try { katex.renderToString(m[1], { throwOnError: true, strict: false }); }
    catch (e) { console.log(`L${i+1} INLINE: ${m[1].slice(0, 50)}`); }
  }
}
'''
open("_chk2.js", "w", encoding="utf-8").write(CHK)

out = ["# 公式缺失/损坏清单（OCR 内容截断，需对照原书或重新扫描）", ""]

for label, root in [("30讲-高数", "11408/拆分稿/数学/30讲-高数"), ("30讲-线代", "11408/拆分稿/数学/30讲-线代")]:
    out.append(f"## {label}")
    n = 0
    for f in sorted(glob.glob(root + "/*.md")):
        res = subprocess.run(["node", "_chk2.js", f], capture_output=True, text=True, encoding="utf-8", errors="replace")
        for l in res.stdout.strip().split("\n"):
            if l.strip():
                out.append(f"- {os.path.basename(f)} {l}")
                n += 1
    out.append(f"\n共 {n} 处\n")

open("11408/公式待修清单.md", "w", encoding="utf-8").write("\n".join(out))
os.remove("_chk2.js")
print("已生成 11408/公式待修清单.md")
print("\n".join(out[:20]))
