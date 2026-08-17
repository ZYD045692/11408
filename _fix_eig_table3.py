# -*- coding: utf-8 -*-
# 重写特征值表格为规整 8 列 markdown 表格
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")
# 定位表格：含 对应的特征向量 且以 | 开头的那组
start = None
for i, l in enumerate(lines):
    if l.startswith("| 矩阵") and "P^{-1}AP" in l:
        start = i
        break
if start is None:
    print("未找到表格头")
    sys.exit()
end = start
while end < len(lines) and lines[end].startswith("|"):
    end += 1
tbl = [
    "| 矩阵 | A | kA | $A^{k}$ | f(A) | $A^{-1}$ | $A^{r}$ | $P^{-1}AP$ |",
    "|---|---|---|---|---|---|---|---|",
    "| 特征值 | $\\lambda$ | $k\\lambda$ | $\\lambda^{k}$ | $f(\\lambda)$ | $\\frac{1}{\\lambda}$ | $\\frac{\\lvert A \\rvert}{\\lambda}$ | $\\lambda$ |",
    "| 对应的特征向量 | $\\xi$ | $\\xi$ | $\\xi$ | $\\xi$ | $\\xi$ | $\\xi$ | $P^{-1}\\xi$ |",
]
lines[start:end] = tbl
print("表格重写 @ L", start + 1, "原行数", end - start)
open(f, "w", encoding="utf-8").write("\n".join(lines))
