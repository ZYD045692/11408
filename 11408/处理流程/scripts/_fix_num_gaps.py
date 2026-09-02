# -*- coding: utf-8 -*-
"""补齐两本数学书的内容区内子项编号：
- 恢复被降级的正文子项标题（1 余子式 / 2 代数余子式 / 2 概念及其敛散性 / 1 空间曲线 / 1 最值的定义）
- 首项无号补 1（排列和逆序 / 初等变换 / 向量的概念和运算 / 线性变换的定义 / 定义 / 正项级数… / 概念×2 / 变力沿曲线做功 / 向量场的通量…）
- 合理重编号：7 不满足消去律→3；4 两个矩阵是否相似→3；3 二次型的标准形→1、惯性定理→2
- 修 OCR 拆分：二 阶常系数齐次→二阶
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def patch(f, jobs):
    lines = open(f, encoding="utf-8").read().split("\n")
    done = {}
    for kind, old, new in jobs:
        # kind: L=行替换（精确整行） P=前缀替换 S=子串替换
        if kind == "L":
            hits = [i for i, l in enumerate(lines) if l == old]
            if len(hits) == 0:
                print(f"  ⚠ 未找到: {old[:40]!r}")
                continue
            if len(hits) > 1 and done.get(old):
                hits = [h for h in hits if lines[h] != new]
            for i in hits:
                lines[i] = new
            done[old] = True
            print(f"  ✅ {old[:36]!r} → {new[:36]!r} (x{len(hits)})")
        elif kind == "P":
            n = 0
            for i, l in enumerate(lines):
                if l.startswith(old):
                    lines[i] = new + l[len(old):]
                    n += 1
            print(f"  ✅ 前缀 {old[:20]!r} → {new[:20]!r} (x{n})")
        elif kind == "S":
            n = 0
            for i, l in enumerate(lines):
                if old in l:
                    lines[i] = l.replace(old, new, 1)
                    n += 1
            print(f"  ✅ 子串 {old[:20]!r} → {new[:20]!r} (x{n})")
    open(f, "w", encoding="utf-8").write("\n".join(lines))

XD = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
GS = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"

print("===== 线代 =====")
patch(XD, [
    # 恢复正文子项标题（节内编号补齐）
    ("L", "1 余子式", "##### 1 余子式"),
    ("L", "2 代数余子式", "##### 2 代数余子式"),
    # 首项补 1
    ("L", "##### 排列和逆序", "##### 1 排列和逆序"),
    ("L", "##### 初等变换", "##### 1 初等变换"),
    ("L", "##### 向量的概念和运算", "##### 1 向量的概念和运算"),
    ("L", "##### 线性变换的定义", "##### 1 线性变换的定义"),
    ("L", "##### 定义", "##### 1 定义"),
    # 重编号
    ("L", "##### 7 不满足消去律", "##### 3 不满足消去律"),
    ("L", "##### 4 两个矩阵是否相似的判别与证明", "##### 3 两个矩阵是否相似的判别与证明"),
    ("L", "##### 3 二次型的标准形、规范形", "##### 1 二次型的标准形、规范形"),
    ("L", "##### 惯性定理", "##### 2 惯性定理"),
])

print("===== 高数 =====")
patch(GS, [
    # 恢复正文子项标题
    ("L", "2 概念及其敛散性", "##### 2 概念及其敛散性"),
    ("L", "1 空间曲线  $F(x, y, z) = 0$", "##### 1 空间曲线  $F(x, y, z) = 0$"),
    ("P", "最值的定义  $\\longrightarrow$ 整体概念，有别于极值", "##### 1 最值的定义"),
    # 首项补 1
    ("L", "##### 正项级数及其敛散性判别", "##### 1 正项级数及其敛散性判别"),
    ("L", "##### 概念", "##### 1 概念"),
    ("L", "##### 变力沿曲线做功", "##### 1 变力沿曲线做功"),
    ("L", "##### 向量场的通量（第二型曲面积分的背景）", "##### 1 向量场的通量（第二型曲面积分的背景）"),
    # 修 OCR 拆分
    ("L", "#### 二 阶常系数齐次线性微分方程", "#### 二阶常系数齐次线性微分方程"),
])
print("done")
