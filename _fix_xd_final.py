# -*- coding: utf-8 -*-
"""线代收尾：拆混行标题 + 第3讲「三」节重建"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")

def split_line(idx, title):
    """把 lines[idx] 从标题后拆开：标题行 + 空行 + 原注释正文"""
    l = lines[idx]
    rest = l[len(title):].strip()
    lines[idx] = title
    lines.insert(idx + 1, "")
    if rest:
        lines.insert(idx + 2, rest)

jobs = [
    # 合并同一标题两行
    ("##### 2 n 阶行列式的定义", "##### 2 $n(n \\geqslant 2)$ 阶行列式的定义"),
    ("##### $n(n \\geqslant 2)$ 阶行列式", None),   # 删除
]
for old, new in jobs:
    if old not in lines:
        print(f"⚠ 未找到: {old[:30]!r}")
        continue
    idx = lines.index(old)
    if new is None:
        del lines[idx]
    else:
        lines[idx] = new
    print(f"✅ {old[:30]!r}")

# 拆混行标题
splits = [
    ("##### 1 余子式 “子式 = 行列式”，子式是原行列式的一部分 “子矩阵 = 矩阵”，子矩阵是原矩阵的一部分", "##### 1 余子式"),
    ("##### 2 代数余子式  $\\begin{vmatrix}1 & 2 & 1 \\\\ 2 & 5 & 7 \\\\ -6 & 4 & 9\\end{vmatrix}$", "##### 2 代数余子式"),
    ("##### 1 定义 只要有一个就行  $\\rightarrow$ 住取k行、k列构成的k阶行列式", "##### 1 定义"),
    ("##### 3 正交矩阵 行（列）向量长度为1的单位向量，且相互正交", "##### 3 正交矩阵"),
]
for old, title in splits:
    if old not in lines:
        print(f"⚠ 未找到: {old[:30]!r}")
        continue
    idx = lines.index(old)
    split_line(idx, title)
    print(f"✅ 拆分: {title}")

# 第3讲「三」节重建
repl = {
    "##### 3 极大线性无关组、等价向量组、向量组的秩": "#### 三 极大线性无关组、等价向量组、向量组的秩",
    "###### 1 极大线性无关组": "##### 1 极大线性无关组",
    "###### 3 向量组的秩": "##### 3 向量组的秩",
    "###### 4 有关秩的重要定理和公式": "##### 4 有关秩的重要定理和公式",
}
n = 0
out = []
for l in lines:
    if l in repl:
        out.append(repl[l]); n += 1
        continue
    if l.startswith("② 等价向量组") and not l.startswith("#"):
        rest = l[len("② 等价向量组"):].lstrip(" ——→").strip()
        out.append("##### 2 等价向量组")
        out.append("")
        if rest:
            out.append(rest)
        n += 1
        continue
    out.append(l)
lines = out
print(f"✅ 第3讲重建: {n} 处")

open(f, "w", encoding="utf-8").write("\n".join(lines))
print("done")
