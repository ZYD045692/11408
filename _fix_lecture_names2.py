# -*- coding: utf-8 -*-
"""高数：把 第5~7、9~10、13~15讲 的讲名从下一行纯文本合并到 ## 同一行"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = glob.glob("11408/origin/*高数*/*.md")[0]
print("文件:", F)

raw = open(F, "rb").read().decode("utf-8")
raw = raw.replace("\r\n", "\n")
lines = raw.split("\n")

NAMES = {
    5:"一元函数微分学的应用（一）——几何应用",
    6:"一元函数微分学的应用（二）——中值定理、微分等式与微分不等式",
    7:"一元函数微分学的应用（三）——物理应用与经济应用",
    9:"一元函数积分学的计算",
    10:"一元函数积分学的应用（一） ——几何应用",
    13:"多元函数微分学",
    14:"二重积分",
    15:"微分方程",
}

out = []
fixed = 0

for i, line in enumerate(lines):
    m = re.match(r"^## 第(\d+)讲\s*$", line)
    if m:
        no = int(m.group(1))
        expected = NAMES.get(no)
        if expected:
            # 替换当前行为 ## 第N讲 讲名
            out.append(f"## 第{no}讲 {expected}")
            # 跳过下一行（讲名所在行）
            fixed += 1
            continue
    out.append(line)

# 但上面跳过了讲名行后，out 中会少一行的内容——不对，continue 会跳过 append(line)，
# 但下一行讲名会被正常 append（因为没有匹配 `^## 第`）
# 所以讲名行还在正文中。我需要主动跳过讲名行。

# 重新来过——用更直接的方式
out = []
fixed = 0
skip = 0

for i, line in enumerate(lines):
    if skip > 0:
        skip -= 1
        continue
    m = re.match(r"^## 第(\d+)讲\s*$", line)
    if m:
        no = int(m.group(1))
        expected = NAMES.get(no)
        if expected:
            out.append(f"## 第{no}讲 {expected}")
            # 跳过下一行（纯讲名行）
            skip = 1
            fixed += 1
            continue
    out.append(line)

result = "\n".join(out)
open(F, "w", encoding="utf-8").write(result)
print(f"已修 {fixed} 讲讲名")