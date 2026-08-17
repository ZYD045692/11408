# -*- coding: utf-8 -*-
"""扫描正文/表格中的字面反斜杠n（OCR 换行残留），排除代码块内合法 \n"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

for f in sorted(glob.glob("11408/origin/*/*.md")):
    in_code = False
    hits = []
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        s = l.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if "\\n" in l:
            hits.append((i, l.strip()[:90]))
    if hits:
        print(f"== {f.split('/')[-2]}: {len(hits)} 处")
        for i, t in hits[:10]:
            print(f"  L{i}: {t}")
