# -*- coding: utf-8 -*-
"""修复 解析册 强化篇/高数/第13章 题7 块：
fix.content(rid530) 误混入题8 内容 + 两个 aligned 块缺 \\end{aligned}$$ 收尾。
用 fix.content 的 0-7 行重建块体，补上闭合。"""
import os, sys, glob, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BS = chr(92)

f = glob.glob("11408/origin/*解析册*/*.md")[0]
lines = open(f, encoding="utf-8").read().split("\n")

# 定位 #### 7. 块（在 第13章 区域，即 12059 附近）
bi = None
for i, l in enumerate(lines):
    if i > 12000 and re.match(r"^####\s+7\.\s*$", l):
        bi = i
        break
assert bi and 12040 < bi < 12070, bi
ei = None
for j in range(bi + 1, len(lines)):
    if re.match(r"^####\s+8\.\s*$", lines[j]):
        ei = j
        break
assert ei and ei - bi < 25, ei
assert "8.【答案】0" in "\n".join(lines[bi:ei]), "题8混入特征不在，放弃"
print("块范围:", bi + 1, "-", ei)

# 取 fix.content
c = None
for line in open("_vlm/repair/patches.jsonl", encoding="utf-8"):
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("rid") == 530:
        c = r["fix"]["content"]
assert c
body = c.split("\n")[:8]     # 只要题7的 方法一+方法二
# 给缺闭合的 aligned 块补尾
for k, l in enumerate(body):
    if l.startswith("$$" + BS + "begin{aligned}") and not l.rstrip().endswith("$$"):
        body[k] = l.rstrip() + BS + "end{aligned}$$"
        print("补闭合于 body 行", k)

new_lines = lines[:bi + 1] + [""] + body + [""] + lines[ei:]
open(f, "w", encoding="utf-8", newline="").write("\n".join(new_lines))
print("重建完成，行数", len(lines), "->", len(new_lines))
