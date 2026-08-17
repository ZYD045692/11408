# -*- coding: utf-8 -*-
"""试题册 L462：按 PDF 修复 Q2 选项 (A)-1 (B)1/e (C)1 (D)e"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md"
lines = open(F, encoding="utf-8").read().split("\n")

cur = lines[461]
if "\\frac{1}{e}" in cur and "(D) ." in cur:
    lines[461] = "(A)$-1$　　(B)$\\frac{1}{e}$　　(C)$1$　　(D)$e$"
    print("L462 修复为:", lines[461])
else:
    print("L462 现状:", cur)

open(F, "w", encoding="utf-8").write("\n".join(lines))
