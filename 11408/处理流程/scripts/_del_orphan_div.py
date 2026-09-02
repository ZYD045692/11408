# -*- coding: utf-8 -*-
# 删除孤儿 div（广告页图片容器残留）：<div style="text-align: center;"> 单独一行，
# 后面无 <img>/</div>，下一个非空行是标题/例号/EOF
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
]

def is_orphan(lines, j, n):
    if j >= n:
        return True
    nxt = lines[j].strip()
    if nxt.startswith("<img") or nxt.startswith("</div>") or nxt.startswith("<div"):
        return False
    if nxt.startswith(("#", "例", "【")):
        return True
    return False

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    n = len(lines)
    out = []
    removed = 0
    i = 0
    while i < n:
        l = lines[i]
        if l.strip() == '<div style="text-align: center;">':
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if is_orphan(lines, j, n):
                # 删除 div + 中间空行，out 末尾保留恰好一个空行
                while out and out[-1].strip() == "":
                    out.pop()
                out.append("")
                i = j
                removed += 1
                continue
        out.append(l)
        i += 1
    open(md, "w", encoding="utf-8").write("\n".join(out))
    print(f"{md.split('/')[-2]}: 删除孤儿 div {removed} 处")
