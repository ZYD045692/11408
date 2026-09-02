# -*- coding: utf-8 -*-
"""分类 HTML 表格：真多列表格 vs 单列文本框（注/证盒）"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    tables = []
    i = 0
    while i < len(lines):
        if "<table" in lines[i]:
            start = i
            buf = []
            while i < len(lines) and "</table>" not in lines[i]:
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                buf.append(lines[i])
            block = "\n".join(buf)
            # 解析每行每格
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S)
            max_cols = 0
            n_rows = 0
            for r in rows:
                cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
                max_cols = max(max_cols, len(cells))
                n_rows += 1
            has_math = "$" in block
            if has_math and max_cols >= 2 and n_rows >= 2:
                tables.append((start + 1, i + 1, n_rows, max_cols))
        i += 1
    if tables:
        print(f"== {f.split('/')[-2]}: 真多列表格(含公式) {len(tables)}")
        for start, end, nr, nc in tables:
            print(f"   L{start}-{end}  {nr}行/{nc}列")
