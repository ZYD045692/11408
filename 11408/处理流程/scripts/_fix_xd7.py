# -*- coding: utf-8 -*-
# 修复高数两处跨行垃圾块：
#   A. 第15讲 特解规则 k=cases（17623-17632 附近，```c 包住数组）
#   B. 第18讲 例18.15 被毁曲线积分式（```c 块，无法恢复的重复垃圾）
import io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

md = glob.glob("11408/origin/27张宇基础30讲（高数）/*.md")[0]
lines = open(md, encoding="utf-8").read().split("\n")

# ---------- A. k=cases 特解规则 ----------
# 找 " $ \left\{\begin{array}{l}" 且下一行含 "e^{ax} 照抄（若没有" 的块
start = None
for i, l in enumerate(lines):
    if "\\left\\{\\begin{array}{l}" in l and i + 1 < len(lines) and "e^{ax} 照抄" in lines[i + 1]:
        start = i
        break
if start is not None:
    # 找块结束：\end{array} $ 按最高次写一般式
    end = None
    for j in range(start, len(lines)):
        if "\\end{array} $ 按最高次写一般式" in lines[j]:
            end = j
            break
    if end is not None:
        new_block = [
            r" $ \left\{\begin{array}{l}",
            r"e^{ax} \text{ 照抄（若没有 } e^{ax} \text{，表明 } \alpha=0 \text{），} \\",
            r"l = \max\{m, n\}, Q_l^{(1)}(x), Q_l^{(2)}(x) \text{ 分别为 } x \text{ 的两个不同的 } l \text{ 次多项式，} \\",
            r"k = \begin{cases} 0, & \alpha \pm \beta i \neq r_{1,2}, \\ 1, & \alpha \pm \beta i = r_{1,2}. \end{cases} \\",
            r"\end{array}\right. $ 按最高次写一般式",
        ]
        lines = lines[:start] + new_block + lines[end + 1:]
        print(f"A. 已重建特解规则块 L{start+1}-L{end+1}")
    else:
        print("A. 未找到 \end{array} $ 按最高次写一般式")
else:
    print("A. 未找到 e^{ax} 照抄 数组块")

# ---------- B. 第18讲 被毁曲线积分式 ----------
start = None
for i, l in enumerate(lines):
    if l.strip() == "```c" and i + 2 < len(lines) and "\\oint_{\\partial D}" in lines[i + 2]:
        start = i
        break
if start is not None:
    # 找 ``` 结束
    end = None
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == "```":
            end = j
            break
    if end is not None:
        new_block = [
            "",
            r"$$\begin{aligned}",
            r"\oint_{\partial D}\left|x\right|\mathrm{d}y+\left|y\right|\mathrm{d}x",
            r"&=\oint_{L_{1}+L_{2}+L_{3}}\left|x\right|\mathrm{d}y+\left|y\right|\mathrm{d}x\\",
            r"&=\int_{L_{1}+L_{2}}\left|x\right|\mathrm{d}y+\left|y\right|\mathrm{d}x\\",
            r"&=-\int_{L_{1}+L_{2}}y\,\mathrm{d}x\\",
            r"&=-2\int_{0}^{1}y\,\mathrm{d}x\\",
            r"&=-\int_{\frac{\pi}{2}}^{0}2\sin^{3}t\,\mathrm{d}(\cos^{3}t)\\",
            r"&=2\int_{0}^{\frac{\pi}{2}}\sin^{3}t\cdot3\cos^{2}t(-\sin t)\,\mathrm{d}t",
            r"\end{aligned}$$",
            "",
        ]
        lines = lines[:start] + new_block + lines[end + 1:]
        print(f"B. 已重建曲线积分式 L{start+1}-L{end+1}")
    else:
        print("B. 未找到 ``` 结束")
else:
    print("B. 未找到 \\oint_{\\partial D} 代码块")

open(md, "w", encoding="utf-8").write("\n".join(lines))
print("完成")
