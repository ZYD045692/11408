# -*- coding: utf-8 -*-
"""行数二分：前4行 / 后4行"""
import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context")
src = open(os.path.join(BASE, "1000题-解析册.md"), encoding="utf-8").read()
lines = src.split("\n")
head = [l for l in lines if not l.startswith("|")]
tbl = [l for l in lines if l.startswith("|")]  # [表头, 分隔, 8行数据...]
hdr, rows = tbl[:2], tbl[2:]
def w(name, rs):
    open(os.path.join(BASE, name), "w", encoding="utf-8", newline="\n").write("\n".join(head + hdr + list(rs)))
    print("写出", name)
w("_t7_前4行表格.md", rows[:4])
w("_t8_后4行表格.md", rows[4:])
