# -*- coding: utf-8 -*-
"""高数 origin：删除重复节标题 + 修复缺失空格"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = glob.glob("11408/origin/*高数*/*.md")[0]
raw = open(F, "rb").read().decode("utf-8")
raw = raw.replace("\r\n", "\n")
lines = raw.split("\n")

# 找重复标题
last_key = None
last_i = None
n = 0
for i, l in enumerate(lines):
    m = re.match(r"^(#### [一二三四五六七八九十])\S", l)
    if m:
        k = m.group(1)
        if k == last_key:
            if all(not lines[j].strip() for j in range(last_i+1, i)):
                lines[i] = None
                n += 1
        last_key = k
        last_i = i
    else:
        if l.strip() and not re.match(r"^#{1,5}\s", l):
            last_key = None

lines = [l for l in lines if l is not None]
print(f"删重复: {n}")

# 修复 ###N -> ### N
n2 = 0
for i, l in enumerate(lines):
    m = re.match(r"^(#####)(\d)\s", l)
    if m and not l[len(m.group(1)):].startswith(" "):
        lines[i] = f"{m.group(1)} {l[len(m.group(1)):]}"
        n2 += 1
print(f"修空格: {n2}")

result = "\n".join(lines)
open(F, "w", encoding="utf-8").write(result)
print("完成")