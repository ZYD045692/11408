# -*- coding: utf-8 -*-
"""高数第二轮：
1. 修正 ##### #### 概念 → ##### 概念（重复前缀）
2. 第16讲：各节下 H4 子项 → H5（常数项级数/级数敛散性/幂级数/四/五 各节）
3. 第18讲：五 第二型曲面积分 下 H4 子项 → H5
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
lines = open(f, encoding="utf-8").read().split("\n")

# 1. 修正重复前缀
n_dup = 0
for i, l in enumerate(lines):
    if l.startswith("##### #### "):
        lines[i] = "##### " + l[len("##### #### "):]
        n_dup += 1
print("修正重复前缀:", n_dup)

HEAD = re.compile(r"^(#{2,6})\s+(.*)$")

# 2. 第16讲：节标题集合；节与节之间（含节后到下一节前）的 H4 → H5
sec16 = [
    "常数项级数的概念与性质",
    "级数敛散性的判别方法",
    "幂级数及其收敛域",
    "四 幂级数求和函数（解答题/客观题）",
    "五 函数展开成幂级数",
]
# 第16讲范围
i16 = next(i for i, l in enumerate(lines) if l.startswith("## 第16讲"))
i16e = next(i for i in range(i16 + 1, len(lines)) if lines[i].startswith("## 第17讲"))
n16 = 0
seg_start = None
for i in range(i16, i16e):
    m = HEAD.match(lines[i])
    if not m:
        continue
    t = m.group(2).strip()
    if m.group(1) == "####" and t in sec16:
        seg_start = t
        continue
    # 在任一节之后、遇到 H3/H2 之前，H4 子项 → H5
    if seg_start is not None and m.group(1) == "####":
        # 遇到新的节或 H3 时 seg_start 不变，但这里只处理 H4
        if t in sec16:
            continue
        lines[i] = "##### " + t
        n16 += 1
    if m.group(1) in ("###", "##"):
        seg_start = None
print("第16讲降H5:", n16)

# 3. 第18讲：五 第二型曲面积分 下的 H4 子项 → H5（到 六 空间第二型曲线积分 前）
i18 = next(i for i, l in enumerate(lines) if l.startswith("## 第18讲"))
i18e = len(lines)
n18 = 0
in_five = False
for i in range(i18, i18e):
    m = HEAD.match(lines[i])
    if not m:
        continue
    t = m.group(2).strip()
    if m.group(1) == "####" and t.startswith("五 第二型曲面积分"):
        in_five = True
        continue
    if in_five:
        if m.group(1) == "####" and t.startswith("六 "):
            in_five = False
            continue
        if m.group(1) == "####":
            lines[i] = "##### " + t
            n18 += 1
        if m.group(1) in ("###",):
            in_five = False
print("第18讲降H5:", n18)

open(f, "w", encoding="utf-8").write("\n".join(lines))
print("done")
