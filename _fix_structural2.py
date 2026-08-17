# -*- coding: utf-8 -*-
"""结合上下文的合理重建：
A. 线代第3讲：3 极大线性无关组… 提升为「三」节，子项降为 H5，补 2 等价向量组
B. 高数第18讲：三 重积分→一 三重积分；补「二 第一型曲线积分」「三 第一型曲面积分」两节并归位子项
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------- A. 线代第3讲 ----------
f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")
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
    # ② 等价向量组 正文行 → 拆成标题 + 正文
    if l.startswith("② 等价向量组") and not l.startswith("#"):
        rest = l[len("② 等价向量组"):].lstrip(" ——→").strip()
        out.append("##### 2 等价向量组")
        out.append("")
        if rest:
            out.append(rest)
        n += 1
        continue
    out.append(l)
print("线代第3讲:", n)
open(f, "w", encoding="utf-8").write("\n".join(out))

# ---------- B. 高数第18讲 ----------
f = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
lines = open(f, encoding="utf-8").read().split("\n")
mode = None   # None | "sec1" | "sec2" | "sec3"
out = []
n2 = 0
for l in lines:
    if l == "#### 三 重积分":
        out.append("#### 一 三重积分"); mode = "sec1"; n2 += 1
        continue
    if mode == "sec1" and l.strip() == "1 概念" and not l.startswith("#"):
        out.append("##### 1 概念"); n2 += 1
        continue
    if mode == "sec1" and l == "##### 1 概念":
        # 这是「第一型曲线积分」的 1 概念（原错挂在三重积分下）
        out.append("#### 二 第一型曲线积分（对弧长）")
        out.append("")
        mode = "sec2"; n2 += 1
        out.append(l)
        continue
    if mode == "sec2":
        if l == "#### 性质":
            out.append("##### 2 性质"); n2 += 1; continue
        if l == "#### 3 普通对称性与轮换对称性":
            out.append("##### 3 普通对称性与轮换对称性"); n2 += 1; continue
        if l == "#### 4 计算":
            out.append("##### 4 计算"); n2 += 1; continue
        if l == "#### 5 应用":
            out.append("##### 5 应用"); n2 += 1; continue
        if l == "#### 1 概念":
            # 这是「第一型曲面积分」的 1 概念
            out.append("#### 三 第一型曲面积分（对面积）")
            out.append("")
            out.append("##### 1 概念")
            mode = "sec3"; n2 += 1
            continue
    if mode == "sec3":
        if l == "#### 2 性质":
            out.append("##### 2 性质"); n2 += 1; continue
        if l == "#### 3 普通对称性与轮换对称性":
            out.append("##### 3 普通对称性与轮换对称性"); n2 += 1; continue
        if l == "#### 4 计算":
            out.append("##### 4 计算"); n2 += 1; continue
        if l == "#### 5 应用":
            out.append("##### 5 应用"); n2 += 1; continue
        if l.startswith("#### 四 平面第二型曲线积分"):
            mode = None
    out.append(l)
print("高数第18讲:", n2)
open(f, "w", encoding="utf-8").write("\n".join(out))
print("done")
