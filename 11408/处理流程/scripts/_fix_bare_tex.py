# -*- coding: utf-8 -*-
# 修复 origin 中的裸 LaTeX（不在 $ 内）：\underline{\text{X}}→**X**，\quad→空格，\cdot→·，裸矩阵包$
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

UL = re.compile(r"\\underline\{\\text\{([^{}]*)\}\}")

def in_math(line):
    ranges = []
    i, n = 0, len(line)
    while i < n:
        if line[i] == '$':
            if i + 1 < n and line[i + 1] == '$':
                j = line.find('$$', i + 2)
                if j != -1:
                    ranges.append((i, j + 2)); i = j + 2; continue
                i += 2; continue
            j = line.find('$', i + 1)
            if j != -1:
                ranges.append((i, j + 1)); i = j + 1; continue
        i += 1
    return ranges

def is_math(pos, ranges):
    for a, b in ranges:
        if a <= pos < b:
            return True
    return False

def fix_line(l):
    ranges = in_math(l)
    # 1) \underline{\text{X}} → **X**
    l = UL.sub(lambda m: "**" + m.group(1) + "**", l)
    # 2) 裸 \quad / \qquad → 全角空格
    for m in list(re.finditer(r"\\q(?:uad|quad)", l)):
        if not is_math(m.start(), in_math(l)):
            l = l[:m.start()] + "　" + l[m.end():]
    # 3) 裸 \cdot → ·
    for m in list(re.finditer(r"\\cdot\b", l)):
        if not is_math(m.start(), in_math(l)):
            l = l[:m.start()] + "·" + l[m.end():]
    # 4) 裸 \begin{env}...\end{env} → 包 $；内部单 \ +空格 → \\（避免误改已正确的 \\）
    for m in list(re.finditer(r"\\begin\{(matrix|bmatrix|pmatrix|cases|array|vmatrix)\}.*?\\end\{\1\}", l)):
        if not is_math(m.start(), in_math(l)):
            seg = m.group(0)
            seg = re.sub(r"(?<!\\)\\(?= )", r"\\\\", seg)
            l = l[:m.start()] + "$" + seg + "$" + l[m.end():]
    # 5) 修正多余反斜杠：\\\ → \\
    l = re.sub(r"\\{3}(?= )", r"\\\\", l)
    return l

BOOKS = ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络",
         "27张宇基础30讲（高数）", "27张宇基础30讲线代",
         "27张宇1000题数一【试题册】", "27张宇1000题数一【解析册】"]
ONLY = sys.argv[1] if len(sys.argv) > 1 else None

for b in BOOKS:
    if ONLY and ONLY not in b:
        continue
    md = glob.glob(f"11408/origin/{b}/*.md")[0]
    lines = open(md, encoding="utf-8").read().split("\n")
    n = 0
    for i, l in enumerate(lines):
        new = fix_line(l)
        if new != l:
            lines[i] = new
            n += 1
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{b}: 修改 {n} 行")
