# -*- coding: utf-8 -*-
# 修复线代剩余坏公式（OCR 把 $ 混入 \text/\overbrace、\qquad 损坏、\[ 误写、残缺 matrix）
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
txt = open(md, encoding="utf-8").read()

FIXES = [
    # L100: \text{$ 列}). → \text{ 列}).$ （闭$错位）
    (r"a_{ij} = \(\\text\{第 \} i \\text\{ 行\}, \\text\{\$ 列\}\).",
     r"a_{ij} = (\text{第 } i \text{ 行}, \text{第 } j \text{ 列}).$"),
    # L2296: \overbrace{...}^{m$个} → ...^{m\text{个}}$
    (r"\\overbrace\{AA\\cdots A\}\^\{m\$个\}", r"\\overbrace{AA\\cdots A}^{m\\text{个}}$"),
    # L2096: \frac{位于f(x)\text{$下方的点个数}}{总点个数}
    (r"\\frac\{位于f\(x\)\\text\{\$下方的点个数\}\}\{总点个数\}",
     r"\\frac{\\text{位于}f(x)\\text{下方的点个数}}{\\text{总点个数}}$"),
    # L2900: \text{$初等行变换} → \text{初等行变换}
    (r"\\text\{\$初等行变换\}", r"\\text{初等行变换}"),
    # L7906: $\[f(x_1 → $[f(x_1
    (r"\$\\\[f\(x_\{1\}", r"$[f(x_{1}"),
    # L855 类: \[left → [left（公式内 \[ 误写）
    (r"\$\\\[\\left\|\\boldsymbol\{E\}", r"$[\\left|\\boldsymbol{E}"),
    # L5087: \qquadightarrow → \longrightarrow
    (r"\\qquadightarrow", r"\\longrightarrow"),
    (r"\\qquadig", r"\\longrightarrow"),
    # L2239: \left[\begin{array}{c}\Box\$ → 补闭合
    (r"\\left\[\\begin\{array\}\{c\}\\Box\$", r"\\left[\\begin{array}{c}\\Box\\end{array}\\right]$"),
]

n = 0
for pat, rep in FIXES:
    c = len(re.findall(pat, txt))
    txt = re.sub(pat, lambda m: rep, txt)
    if c:
        print(f"OK {c}: {pat[:40]}")
        n += c
    else:
        print(f"-- {pat[:40]}")

open(md, "w", encoding="utf-8").write(txt)
print(f"共修 {n} 处")
