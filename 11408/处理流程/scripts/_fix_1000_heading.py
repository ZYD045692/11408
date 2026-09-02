# -*- coding: utf-8 -*-
"""试题册：
1. 基础篇补插「## 第5章 一元函数微分学的应用（一） ——几何应用」
2. 测试卷 三、解答题 里的题号行统一为 #### 标题
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md"
lines = open(f, encoding="utf-8").read().split("\n")

# --- 1. 补第5章标题 ---
anchor = "1. 函数$y = e^x + \\frac{e^{-x}}{2}$的最小值为___。"
idx = [i for i, l in enumerate(lines) if l.strip() == anchor]
if len(idx) == 1:
    i = idx[0]
    # 前一行为空行；在其与 anchor 之间插入标题
    lines[i:i] = ["## 第5章 一元函数微分学的应用（一） ——几何应用", ""]
    print("基础篇: 已插入 第5章 标题")
else:
    print(f"!! 第5章 anchor 匹配 {len(idx)} 处，跳过")

# --- 2. 解答题题号行统一为 #### ---
promo = re.compile(r"^\d{1,2}(?:\\\.|\.)?\s*\(本题满分\d+分\)")
n = 0
for i, l in enumerate(lines):
    if l.startswith("#"):
        continue
    if promo.match(l.strip()):
        lines[i] = "#### " + l
        n += 1
print(f"解答题题号行提升: {n}")

open(f, "w", encoding="utf-8").write("\n".join(lines))
print("done")
