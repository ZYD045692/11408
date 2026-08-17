# -*- coding: utf-8 -*-
"""修复 HTML 表格单元格里的字面 \\n（OCR 换行残留 → 空格）"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    changed = 0
    for i, l in enumerate(lines):
        if "<td" not in l and "<th" not in l:
            continue
        if "\\n" not in l:
            continue
        # 只处理表格行
        new = re.sub(r"\\n", " ", l)
        if new != l:
            lines[i] = new
            changed += 1
    if changed:
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        print(f"{f.split('/')[-2]}: 修表格 {changed} 行")
