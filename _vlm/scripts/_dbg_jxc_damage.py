# -*- coding: utf-8 -*-
"""修复 解析册 中 VLM 补丁引入的 JSON 转义腐蚀：
  \r → 换行（行首残留 ightarrow/ight]/ight) 等，需并回上一行并补 \r）
  \n → 换行（行首残留 eq/ne 等，同上）
  \\ → \ （bmatrix 行分隔 \\ 衰减成 \数字，需补回 \\）
  \\n → 字面 \n（应为真实换行）
安全边界：只动数学环境内部或明确的腐蚀行首。"""
import os, sys, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BS = chr(92)

f = glob.glob("11408/origin/*解析册*/*.md")[0]
lines = open(f, encoding="utf-8").read().split("\n")

# ---- 1. 行首腐蚀碎片统计（先只报告）----
FRAG = re.compile(r"^(ight|eq\b|eq\}|eq,|eq\.|neq|abla|u\(|u_|u\+|u=|abla|mid|otimes|subset)")
frag = [(i, l[:40]) for i, l in enumerate(lines) if FRAG.match(l)]
print("行首碎片候选:", len(frag))
for i, s in frag[:40]:
    print("  L%d %s%s" % (i + 1, s, "   <prev: " + lines[i - 1][-40:] if i else ""))
