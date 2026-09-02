# -*- coding: utf-8 -*-
"""修复两处真乱码：
1. 线代 L413: A\\quad 貼 a\\  錶 =\\beta → A\\alpha = \\beta（书中句义：矩阵A作用在向量α上得β）
2. 解析册 L15441: 表格格子 p_{\\cdo·/td> → p_{ij}</td>（联合分布表 p_{ij}）
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def patch(md, pairs):
    txt = open(md, encoding="utf-8").read()
    ok = 0
    for old, new in pairs:
        if old not in txt:
            print(f"  ⚠ 未找到: {old[:40]!r}")
            continue
        txt = txt.replace(old, new, 1)
        ok += 1
    open(md, "w", encoding="utf-8").write(txt)
    print(f"{md.split('/')[-2]}: 修复 {ok}/{len(pairs)}")

patch("11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md", [
    ("A\\quad 貼 a\\  錶 =\\beta", "A\\alpha = \\beta"),
])

patch("11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md", [
    ("p_{\\cdo·/td>", "p_{ij}</td>"),
])
