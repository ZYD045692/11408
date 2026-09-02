# -*- coding: utf-8 -*-
"""验证猜想：task4 报告各行表格里 $ / $$ 不配对（截断导致的未闭合数学块）"""
import glob, os, re
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context")
bad = {"30讲-高数.md", "操作系统.md", "1000题-解析册.md"}
for fn in sorted(glob.glob(os.path.join(BASE, "*.md"))):
    name = os.path.basename(fn)
    if name.startswith("_t"):
        continue
    lines = open(fn, encoding="utf-8").read().split("\n")
    odd_rows = []
    for i, l in enumerate(lines):
        if not l.startswith("|") or l.startswith("|--") or l.startswith("| 图"):
            continue
        dd = l.count("$$")          # $$ 出现次数（奇=未闭合显示公式）
        # 去掉 $$ 后数单个 $
        single = l.replace("$$", "").count("$")
        if dd % 2 or single % 2:
            img = l.split("|")[1].strip()
            odd_rows.append(f"行{i+1}({img}):$$x{dd},$x{single}")
    tag = "打不开" if name in bad else "正常  "
    print(tag, name, f"未闭合行数={len(odd_rows)}", odd_rows[:6])
