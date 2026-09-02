# -*- coding: utf-8 -*-
"""解析册 7 处 LaTeX 定点修复（行号锚定 + 断言）"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BS = chr(92)

f = glob.glob("11408/origin/*解析册*/*.md")[0]
lines = open(f, encoding="utf-8").read().split("\n")
n0 = len(lines)

def sub_line(ln, old, new, cnt=1):
    i = ln - 1
    assert old in lines[i], f"L{ln} 找不到锚: {old[:50]!r}"
    lines[i] = lines[i].replace(old, new, cnt)

# 1) L3390 & L3406: 计算竖线应为 \big|（否则最后 \right| 无配对）
for ln in (3390, 3406):
    sub_line(ln, BS + "ln x" + BS + "right|_{0}^{1}", BS + "ln x" + BS + "big|_{0}^{1}")

# 2) L11183: aligned 缺 \end{aligned}（闭合 $$ 在下一行）
i = 11183 - 1
assert lines[i].rstrip().endswith("rho g h .") or "rho g h" in lines[i], lines[i][-40:]
lines[i] = lines[i].rstrip() + " " + BS + "end{aligned}"

# 3) L12063: 缺 \end{aligned}$$
i = 12063 - 1
assert lines[i].rstrip().endswith("\\frac{(e-1)^{2}}{8}."), lines[i][-40:]
lines[i] = lines[i].rstrip() + BS + "end{aligned}$$"

# 4) L16010: 多余 } + 全角逗号移出数学环境
sub_line(16010, "{{0}}&{{0}}} " + BS + BS + "{{{0}}}", "{{0}}&{{0}} " + BS + BS + "{{{0}}}")
sub_line(16010, BS + "end{bmatrix}，$$", BS + "end{bmatrix}$$，")

# 5) L16016: {{5}}} → {{{5}}}
sub_line(16016, "&{{5}}}" + BS + "end{bmatrix}", "&{{{5}}}" + BS + "end{bmatrix}")

# 6) L17606: 孤儿 \end{aligned}
sub_line(17606, "." + BS + "end{aligned}$$", ".$$")

open(f, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("修复完成，行数", n0, "->", len(lines))
