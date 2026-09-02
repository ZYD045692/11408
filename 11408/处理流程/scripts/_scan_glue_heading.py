# -*- coding: utf-8 -*-
# 标题紧贴HTML块扫描：标题行直接跟在HTML行后(无空行)会被CommonMark吞进HTML块,大纲不显示
# 用法: python _scan_glue_heading.py   (扫8本origin, 有命中即需在该标题前插空行)
import io, sys, re, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

total = 0
for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    in_code = False
    hits = []
    for i, s in enumerate(lines):
        if s.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^#{1,6} ", s) and i > 0 and lines[i-1].strip().startswith("<"):
            hits.append((i+1, lines[i-1].strip()[:40], s[:50]))
    if hits:
        total += len(hits)
        print(f"== {os.path.basename(f)}: {len(hits)} 处 ==")
        for ln, prev, h in hits:
            print(f"  L{ln}: {h!r} <- {prev!r}")
print(f"\n共 {total} 处" + ("（需插空行）" if total else "，干净"))
