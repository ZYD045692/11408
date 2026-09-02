# -*- coding: utf-8 -*-
# 线代剩余修复：\|\alpha\$| 碎片、\qua　 全角空格、\Box 闭合、跨行行内公式 → 块级
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲线代/*.md")[0]
lines = open(md, encoding="utf-8").read().split("\n")

# 1) 碎片修复
n1 = 0
for i, l in enumerate(lines):
    new = l
    new = re.sub(r"\\\|\\alpha\$", r"\\|\\alpha\\|", new)      # \|\alpha$| → \|\alpha\|
    new = re.sub(r"\\\|\\beta\$", r"\\|\\beta\\|", new)
    new = re.sub(r"\\\|\\gamma\$", r"\\|\\gamma\\|", new)
    new = new.replace("\\qua　", "\\quad")                     # \qua　 → \quad
    new = re.sub(r"\\Box\\\$", r"\\Box\\end{array}\\right]$", new)  # \Box\$ → 补闭合
    if new != l:
        lines[i] = new
        n1 += 1

# 2) 跨行行内公式 → 块级 $$（奇数 $ 行，含 LaTeX 特征）
n2 = 0
out = []
i = 0
FORMULA_FEAT = re.compile(r"\\(?:begin|end|frac|left|right|underline|overbrace|xrightarrow|overset|longrightarrow|alpha|beta|gamma|lambda|matrix|aligned|array)")

while i < len(lines):
    l = lines[i]
    dollars = l.count("$") - 2 * l.count("$$")
    if dollars % 2 == 1 and "$$" not in l:
        # 可能是跨行公式；收集到 $ 平衡
        block = [l]
        j = i + 1
        total = dollars
        while j < len(lines) and total % 2 == 1:
            d2 = lines[j].count("$") - 2 * lines[j].count("$$")
            total += d2
            block.append(lines[j])
            j += 1
        joined = "\n".join(block)
        # 只有含公式特征才合并
        if total % 2 == 0 and FORMULA_FEAT.search(joined):
            # 去掉首尾多余 $（保留内容）
            joined = joined.replace("$", "")
            out.append("$$")
            out.append(joined)
            out.append("$$")
            i = j
            n2 += 1
            continue
    out.append(l)
    i += 1

open(md, "w", encoding="utf-8").write("\n".join(out))
print(f"碎片修复 {n1} 行, 跨行合并 {n2} 处")
