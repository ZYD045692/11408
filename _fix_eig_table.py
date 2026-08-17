# -*- coding: utf-8 -*-
"""把「常用矩阵的特征值与特征向量」HTML 表格转成 Markdown 管道表格（Obsidian 渲染 $ 公式）"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")
old = None
for i, l in enumerate(lines):
    if l.startswith("<table") and "对应的特征向量" in l and "$A^{k}$" in l:
        old = i
        break
if old is None:
    print("未找到该表格")
    sys.exit()

new_tbl = [
    "| 矩阵 | A | kA | $A^{k}$ | f(A) | $A^{-1}$ | $A^{r}$ | $P^{-1}AP$ |",
    "|---|---|---|---|---|---|---|---|",
    "| 特征值 | $\\lambda$ | $k\\lambda$ | $\\lambda^{k}$ | $f(\\lambda)$ | $\\frac{1}{\\lambda}$ | $\\frac{|A|}{\\lambda}$ | $\\lambda$ |",
    "| 对应的特征向量 | $\\xi$ | $\\xi$ | $\\xi$ | $\\xi$ | $\\xi$ | $\\xi$ | $P^{-1}\\xi$ |",
]
lines[old] = "\n".join(new_tbl)
print("已转换 L", old + 1)
open(f, "w", encoding="utf-8").write("\n".join(lines))
