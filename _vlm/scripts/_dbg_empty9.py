# -*- coding: utf-8 -*-
"""检查 9 个无内容 rid 的当前 md 原文是否本身完整"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_apply import find_block_408, find_block_30jiang, find_block_1000, looks_complete

EMPTY = [439, 554, 466, 476, 557, 586, 556, 555, 599]
recs = {}
for line in open("repair/patches.jsonl", encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("rid"):
            recs[r["rid"]] = r

for rid in EMPTY:
    p = recs.get(rid)
    if not p:
        print(rid, "无 patch 记录")
        continue
    md = (V.BOOKS.get(p["book"]) or M.MATH[p["book"]])[0]
    lines = open(md, encoding="utf-8").read().split("\n")
    if p["book"] in V.BOOKS:
        loc = find_block_408(lines, p["sec"], p["num"])
    elif p["book"].startswith("30讲"):
        lec = int(p["sec"].split(" ")[0].replace("第", "").replace("讲", ""))
        loc = find_block_30jiang(lines, lec, p["num"], p["pass"])
    else:
        loc = find_block_1000(lines, p["sec"], p["num"])
    if not loc or loc[0] == "INSERT":
        print(rid, p["book"], p["sec"], p["num"], "定位失败")
        continue
    bi, ei = loc
    body = "\n".join(lines[bi + 1:ei]).strip()
    print(rid, p["sec"], "题" + p["num"], "len", len(body),
          "looks_complete", looks_complete(body),
          "| 尾:", body[-60:].replace("\n", " "))
    print("     初筛理由:", (p.get("reason") or "")[:100])
