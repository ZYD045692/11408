# -*- coding: utf-8 -*-
"""核查 manual_review2 的 4 项：剥掉结尾的图片/ HTML 标签后原文是否其实完整"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_apply import find_block_408, find_block_30jiang, find_block_1000, looks_complete

for line in open("repair/manual_review2.md", encoding="utf-8"):
    m = re.search(r"\*\*(.+?)\*\* (\w) `(.+?)` 题(\S+?)（rid(\d+)）", line)
    if not m:
        continue
    book, ps, sec, num, rid = m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))
    md = (V.BOOKS.get(book) or M.MATH[book])[0]
    lines = open(md, encoding="utf-8").read().split("\n")
    if book in V.BOOKS:
        loc = find_block_408(lines, sec, num)
    elif book.startswith("30讲"):
        lec = int(sec.split(" ")[0].replace("第", "").replace("讲", ""))
        loc = find_block_30jiang(lines, lec, num, ps)
    else:
        loc = find_block_1000(lines, sec, num)
    bi, ei = loc
    body = "\n".join(lines[bi + 1:ei]).strip()
    # 剥掉结尾的 <div>/<img> 块再判断
    stripped = re.sub(r"(\s*<div[^>]*>\s*(<img[^>]*>\s*)*(</div>)?\s*)+$", "", body).rstrip()
    stripped = re.sub(r"(\s*<img[^>]*>\s*)+$", "", stripped).rstrip()
    ok = looks_complete(stripped)
    print(rid, book, sec, "题" + num, "剥标签后完整:", ok, "| 尾:", stripped[-70:].replace("\n", " "))
