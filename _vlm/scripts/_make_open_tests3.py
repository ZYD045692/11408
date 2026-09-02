# -*- coding: utf-8 -*-
"""逐行二分：行2/3/4 各自单独成文件"""
import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context")
src = open(os.path.join(BASE, "1000题-解析册.md"), encoding="utf-8").read()
lines = src.split("\n")
head = [l for l in lines if not l.startswith("|")]
tbl = [l for l in lines if l.startswith("|")]
hdr, rows = tbl[:2], tbl[2:]
for i, r in enumerate(rows):
    name = f"_t9_行{i+1}.md"
    open(os.path.join(BASE, name), "w", encoding="utf-8", newline="\n").write("\n".join(head + hdr + [r]))
    print("写出", name, r.split("|")[1].strip())
