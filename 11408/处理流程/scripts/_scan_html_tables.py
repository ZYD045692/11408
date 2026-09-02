# -*- coding: utf-8 -*-
"""扫描 8 本 origin：HTML <table> 块内是否含 $ 数学公式"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    tables = []   # (start_line, end_line, has_math, cell_count, rows)
    i = 0
    while i < len(lines):
        if "<table" in lines[i]:
            start = i
            buf = []
            while i < len(lines) and "</table>" not in lines[i]:
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                buf.append(lines[i])  # include closing line
            block = "\n".join(buf)
            has_math = "$" in block
            n_rows = block.count("<tr")
            n_cells = block.count("<td")
            tables.append((start + 1, i + 1, has_math, n_rows, n_cells))
        i += 1
    math_tables = [t for t in tables if t[2]]
    if math_tables:
        print(f"== {f.split('/')[-2]}: HTML表格{len(tables)} 含公式{len(math_tables)}")
        for start, end, _, nr, nc in math_tables:
            print(f"   L{start}-{end}  {nr}行/{nc}格")
