# -*- coding: utf-8 -*-
# 修复特征值表格单元格：|A| 的管道被拆，改成 \lvert A \rvert
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")
pat = re.compile(r"\$\s*\\frac\s*\{\s*\|[^|]*\|\s*\}\s*\{\\lambda\}\s*\$")
n = 0
for i, l in enumerate(lines):
    if pat.search(l):
        lines[i] = pat.sub(lambda m: r"$\frac{\lvert A \rvert}{\lambda}$", l)
        n += 1
print("修复 |A| 单元格:", n)
open(f, "w", encoding="utf-8").write("\n".join(lines))
