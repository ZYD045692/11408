# -*- coding: utf-8 -*-
# 扫描所有 origin 文件标题层级，输出结构与异常
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27李良概统基础",
    "11408/origin/27李良概统强化",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')

# 展开：文件直接列出；目录 → glob 内所有 .md
import glob
BOOKS_FILES = []
for b in BOOKS:
    if os.path.isdir(b):
        BOOKS_FILES += sorted(glob.glob(os.path.join(b, "*.md")))
    elif os.path.exists(b):
        BOOKS_FILES.append(b)

for md in BOOKS_FILES:
    print("=" * 70)
    print(os.path.basename(md))
    lines = open(md, encoding="utf-8").read().split("\n")
    # 统计每级标题数量
    cnt = {1:0,2:0,3:0,4:0,5:0,6:0}
    prev = 0
    jumps = []   # 层级跳级
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if not m:
            continue
        lv = len(m.group(1))
        cnt[lv] += 1
        text = m.group(2).strip()
        if prev and lv > prev + 1:
            jumps.append((i, prev, lv, text))
        prev = lv
    print("各级标题数:", {k: cnt[k] for k in range(1, 7)})
    print("跳级(级别跨2级或以上):")
    if jumps:
        for i, plv, lv, t in jumps:
            print(f"  L{i}: {plv}->{lv}  {t[:50]}")
    else:
        print("  (无)")
