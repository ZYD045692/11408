# -*- coding: utf-8 -*-
# 撤销 \right 补| 的误伤：\right|arrow → \rightarrow
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
txt = open(md, encoding="utf-8").read()
n = txt.count(r"\right|arrow")
txt = txt.replace(r"\right|arrow", r"\rightarrow")
open(md, "w", encoding="utf-8").write(txt)
print(f"恢复 \\rightarrow {n} 处")
