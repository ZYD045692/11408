# -*- coding: utf-8 -*-
# 线代 L7904 补闭合 + 输出内容截断清单
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
lines = open(md, encoding="utf-8").read().split("\n")
for i, l in enumerate(lines):
    if "begin{aligned}" in l and "overset{a_{11}}" in l:
        if l.rstrip().endswith(r"\overset{a_{13$"):
            lines[i] = l.rstrip() + r"}{\longrightarrow}\end{aligned}$"
            print(f"L{i+1} 已补闭合")
        else:
            print(f"L{i+1} 行尾: {l[-40:]!r}")
        break
open(md, "w", encoding="utf-8").write("\n".join(lines))
