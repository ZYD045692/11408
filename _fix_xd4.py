# -*- coding: utf-8 -*-
# 修复线代多行 cases 公式组（L3734-3746）：\|\alpha$|、\text{$正交}、行首 $、块级化
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
lines = open(md, encoding="utf-8").read().split("\n")

FIX = [
    (r"\|\alpha\$| = 1", r"\|\alpha\| = 1"),
    (r"\|\beta\$| = 1", r"\|\beta\| = 1"),
    (r"\|\gamma\$| = 1", r"\|\gamma\| = 1"),
    (r"\text{$正交}", r"\text{正交}"),
]
n = 0
for i, l in enumerate(lines):
    new = l
    for old, rep in FIX:
        new = new.replace(old, rep)
    if new != l:
        lines[i] = new
        n += 1

# 多行 cases 块级化：L3734 行首 $ → $$\begin{cases}；后续行行首 $ 删除
start = None
for i, l in enumerate(lines):
    if l.startswith("$a_1^2 + a_2^2"):
        start = i
        break
if start is not None:
    lines[start] = "$$\\begin{cases}" + lines[start][1:]
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == "\\end{cases}$$":
            break
        if lines[j].startswith("$"):
            lines[j] = lines[j][1:]

open(md, "w", encoding="utf-8").write("\n".join(lines))
print(f"碎片修复 {n} 行, cases 块级化")
