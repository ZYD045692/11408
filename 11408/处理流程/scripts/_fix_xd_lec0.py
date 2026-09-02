# -*- coding: utf-8 -*-
"""线代 origin 第0讲结构修复 + 全部7讲讲名并入##标题（参考高数格式 ## 第N讲 讲名）:
1) 7讲: `## 第N讲` + 裸讲名行 -> `## 第N讲 讲名`（删裸名行）
2) 第0讲节号: `### 对象（元素）：向量`->`### 一 ...`, `### 运算`->`### 二 运算`（按书PDF p8-9）
3) 第0讲3个练习框进大纲: `注 练习：...` -> `##### 练习：...`（父节H4+1, 书中第0讲无例0.x, 练习即其例题）
内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
shutil.copy(path, "_backup_round2/线代_before_lec0fix.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(pred, desc):
    hits = [i for i in range(len(lines)) if pred(lines[i])]
    assert hits, f"锚点找不到: {desc}"
    return hits[0]

# ---------- 1) 讲名并入 ## 标题 ----------
NAMES = {
    0: ("零基础课 ——线性代数入门", "零基础课——线性代数入门"),
    1: ("行列式", "行列式"),
    2: ("矩阵", "矩阵"),
    3: ("向量组", "向量组"),
    4: ("线性方程组", "线性方程组"),
    5: ("特征值与特征向量", "特征值与特征向量"),
    6: ("二次型", "二次型"),
}
for no, (raw, canon) in NAMES.items():
    i = find(lambda s, n=no: s.strip() == f"## 第{n}讲", f"## 第{no}讲")
    # 下方3行内找裸讲名行
    j = None
    for k in range(i + 1, min(i + 4, len(lines))):
        if lines[k].strip():
            j = k
            break
    assert j is not None and lines[j].strip() == raw, f"第{no}讲讲名行不符: {lines[j]!r}"
    lines[i] = f"## 第{no}讲 {canon}"
    # 删名行 + 相邻一个空行（优先删名行后的空行）
    if j + 1 < len(lines) and not lines[j + 1].strip():
        del lines[j:j + 2]
    else:
        del lines[j]
        if i + 1 < len(lines) and not lines[i + 1].strip():
            del lines[i + 1]
    print(f"OK: ## 第{no}讲 {canon}")

# ---------- 2) 第0讲节号 ----------
i = find(lambda s: s.strip() == "### 对象（元素）：向量", "对象节")
lines[i] = "### 一 对象（元素）：向量"
print(f"OK L{i+1}: ### 一 对象（元素）：向量")
i = find(lambda s: s.strip() == "### 运算", "运算节")
lines[i] = "### 二 运算"
print(f"OK L{i+1}: ### 二 运算")

# ---------- 3) 练习框 -> ##### 标题（父节须为H4） ----------
LX = [
    ("注 练习：计算如下式子", "##### 练习：计算如下式子"),
    ("注 练习：计算下列式子.", "##### 练习：计算下列式子"),
    ("注 练习：按要求解下列方程组.", "##### 练习：按要求解下列方程组"),
]
for raw, head in LX:
    i = find(lambda s, r=raw: s.strip() == r, raw)
    # 断言最近上方标题是 #### (H4)
    ph = next(lines[k] for k in range(i - 1, -1, -1) if lines[k].startswith("#"))
    assert ph.startswith("#### ") and not ph.startswith("##### "), f"练习父节非H4: {ph!r}"
    lines[i] = head
    print(f"OK L{i+1}: {head}  (父节: {ph.strip()})")

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n全部修复写盘完成")
