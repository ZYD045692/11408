# -*- coding: utf-8 -*-
# 扫描 origin 中孤立的广告残留 div（无 <img>、无 </div>，后面直接是标题/末尾）
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
]

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    n = len(lines)
    hits = []
    for i, l in enumerate(lines):
        if l.strip() != '<div style="text-align: center;">':
            continue
        j = i + 1
        while j < n and lines[j].strip() == "":
            j += 1
        if j >= n:
            hits.append((i + 1, "<EOF>"))
            continue
        nxt = lines[j].strip()
        if nxt.startswith("<img") or nxt.startswith("</div>") or nxt.startswith("<div"):
            continue  # 有内容的容器，不是孤儿
        # 下一个非空行是标题/例号/空结构 → 判定孤儿
        if nxt.startswith(("#", "例", "【", "考点", "小结", "本章")):
            hits.append((i + 1, nxt[:40]))
    print(f"== {md}")
    for ln, nxt in hits:
        print(f"  L{ln}  下一个非空行: {nxt}")
    if not hits:
        print("  （无孤儿 div）")
