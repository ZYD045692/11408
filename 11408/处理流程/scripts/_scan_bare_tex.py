# -*- coding: utf-8 -*-
"""扫描 origin 中不在 $ 内的裸 LaTeX 命令（Obsidian 无法渲染）。"""
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LATEX_CMDS = re.compile(
    r"\\(?:begin|end|frac|sqrt|int|iint|oint|sum|prod|lim|left|right|text|mathbf"
    r"|boldsymbol|displaystyle|quad|qquad|times|cdot|leq|geq|partial|mathrm"
    r"|overrightarrow|underline|matrix|cases|pmatrix|bmatrix|dfrac|tfrac|limits"
    r"|choose|atop|longrightarrow|rightarrow|Rightarrow|Leftrightarrow|sim|approx"
    r"|neq|equiv|infty|pi|alpha|beta|gamma|lambda|sigma|mu|theta|Omega|Phi|Sigma"
    r"|Gamma|Delta|varepsilon|varphi|ldots|cdots|dots|cdotp|text|tan|sin|cos|log"
    r"|ln|lim|max|min|exp|det|int_|to)"
)


def in_math(line):
    ranges = []
    i, n = 0, len(line)
    while i < n:
        if line[i] == '$':
            if i + 1 < n and line[i + 1] == '$':
                j = line.find('$$', i + 2)
                if j != -1:
                    ranges.append((i, j + 2))
                    i = j + 2
                    continue
                i += 2
                continue
            j = line.find('$', i + 1)
            if j != -1:
                ranges.append((i, j + 1))
                i = j + 1
                continue
        i += 1
    return ranges


def in_ranges(pos, ranges):
    for a, b in ranges:
        if a <= pos < b:
            return True
    return False


total = 0
for b in ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络",
          "27张宇基础30讲（高数）", "27张宇基础30讲线代",
          "27张宇1000题数一【试题册】", "27张宇1000题数一【解析册】"]:
    md = glob.glob(f"11408/origin/{b}/*.md")[0]
    n_bare = 0
    samples = []
    for i, l in enumerate(open(md, encoding="utf-8").read().split("\n"), 1):
        ranges = in_math(l)
        for m in LATEX_CMDS.finditer(l):
            if not in_ranges(m.start(), ranges):
                n_bare += 1
                if len(samples) < 3:
                    samples.append((i, l[max(0, m.start() - 22):m.end() + 22]))
    print(f"{b}: 裸LaTeX {n_bare}")
    for ln, s in samples:
        print(f"    L{ln}: ...{s}...")
    total += n_bare
print(f"\n总计: {total}")
