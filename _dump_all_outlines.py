# -*- coding: utf-8 -*-
"""把所有书的标题层级导出到 _outlines_dump.txt，按书分组。"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
out = open("_outlines_dump.txt", "w", encoding="utf-8")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    parts = f.replace("\\", "/").split("/")
    book = parts[-2]
    lines = open(f, encoding="utf-8").read().split("\n")
    out.write(f"\n{'='*70}\n# {book}  ({len(lines)} 行)\n{'='*70}\n")
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            lv = len(m.group(1))
            t = m.group(2).strip()
            indent = "  " * (lv - 1)
            out.write(f"{indent}H{lv} L{i}: {t}\n")
out.close()
print("done")
