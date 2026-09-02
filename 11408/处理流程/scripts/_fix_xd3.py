# -*- coding: utf-8 -*-
# 线代修复：\right 后缺 delimiter → 补 |；\|\alpha$| 碎片
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
lines = open(md, encoding="utf-8").read().split("\n")

n1 = n2 = 0
for i, l in enumerate(lines):
    new = re.sub(r"\\right(?![()\[\]{}\|.\\])", r"\\right|", l)
    if new != l:
        lines[i] = new
        n1 += 1
        l = new
    new = re.sub(r"\\\|\\alpha\$\|", r"\\|\\alpha\\|", l)
    new = re.sub(r"\\\|\\beta\$\|", r"\\|\\beta\\|", new)
    new = re.sub(r"\\\|\\gamma\$\|", r"\\|\\gamma\\|", new)
    if new != l:
        lines[i] = new
        n2 += 1

open(md, "w", encoding="utf-8").write("\n".join(lines))
print(f"\\right补| : {n1} 行, \\|\\alpha$|类: {n2} 行")
