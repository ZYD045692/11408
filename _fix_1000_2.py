# -*- coding: utf-8 -*-
"""修正：删除重复的第5章标题；全角括号的解答题题号行补 ####"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md"
lines = open(f, encoding="utf-8").read().split("\n")

# 1. 删除重复的「## 第5章 一元函数微分学的应用（一） ——几何应用」（基础篇）
dup = "## 第5章 一元函数微分学的应用（一） ——几何应用"
idxs = [i for i, l in enumerate(lines) if l == dup]
print(f"第5章标题出现 {len(idxs)} 次 @ {[i+1 for i in idxs]}")
if len(idxs) == 2:
    i2 = idxs[1]
    # 删掉第二处标题及紧随的空行
    del lines[i2:i2+1]
    if i2 < len(lines) and not lines[i2].strip():
        del lines[i2:i2+1]
    print("已删除重复的第5章标题")

# 2. 全角括号解答题题号行补 ####
promo = re.compile(r"^\d{1,2}\.?\\?\s*[（(]本题满分\d+分）?\)?$")
n = 0
for i, l in enumerate(lines):
    if l.startswith("#"):
        continue
    if promo.match(l.strip()):
        lines[i] = "#### " + l
        n += 1
print(f"本次提升解答题题号行: {n}")

open(f, "w", encoding="utf-8").write("\n".join(lines))
print("done")
