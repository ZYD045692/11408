# -*- coding: utf-8 -*-
"""线代 origin 题目化收尾修复（交叉验证发现的6处）:
题1.5层级错、答1.70/5.84粘连、答1.10/2.10数学块包裹、例6.2丢标题。
内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
shutil.copy(path, "_backup_round2/线代_before_tifix2.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(anchor, start=0):
    hits = [i for i in range(start, len(lines)) if anchor in lines[i]]
    assert hits, f"锚点找不到: {anchor[:40]!r}"
    return hits[0]

# 1. 题1.5: #### 1.5 行列式 -> ##### 1.5 + 正文"行列式"
i = find("#### 1.5 行列式")
print(f"OK L{i+1}: #### 1.5 行列式 -> ##### 1.5")
lines[i:i+1] = ["##### 1.5", "", "行列式"]

# 2. 答1.70 -> 1.7, 正文补答案 0
i = find("##### 1.70")
assert lines[i+2].strip() == "或 4 解"
print(f"OK L{i+1}: ##### 1.70 -> ##### 1.7 + 答案0")
lines[i] = "##### 1.7"
lines[i+2] = "0 " + lines[i+2].strip()

# 3. 答1.10: 数学块包裹拆出
i = find("$1.10  \\lambda \\neq 1$ 解 方程组的系数行列式为")
print(f"OK L{i+1}: 拆包 -> ##### 1.10")
lines[i:i+1] = ["##### 1.10", "", r"$\lambda \neq 1$ 解 方程组的系数行列式为"]

# 4. 答2.10: aligned块拆出
i = find(r"$$\begin{aligned}2.10\quad")
s = lines[i]
inner = s.replace(r"$$\begin{aligned}2.10\quad", "", 1)
inner = inner.replace(r"\quad 解 \quad 因为 \end{aligned}$$", "", 1)
print(f"OK L{i+1}: 拆包 -> ##### 2.10")
lines[i:i+1] = ["##### 2.10", "", "$" + inner + "$ 解 因为"]

# 5. 答5.84 -> 5.8, 正文补答案 4
i = find("##### 5.84")
assert lines[i+2].strip().startswith("解")
print(f"OK L{i+1}: ##### 5.84 -> ##### 5.8 + 答案4")
lines[i] = "##### 5.8"
lines[i+2] = "4 " + lines[i+2].strip()

# 6. 例6.2: 补标题(内容完好,只丢标题行)
i_img = find('<img src="imgs/img_175.jpg">')
i = i_img - 4
assert lines[i].strip() == "化二次型", lines[i]
print(f"OK L{i+1}前: 插入 ###### 例6.2")
lines[i:i] = ["###### 例6.2", ""]

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n全部修复写盘完成")
