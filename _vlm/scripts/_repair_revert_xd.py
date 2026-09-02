# -*- coding: utf-8 -*-
"""把线代 题1.5/1.7/1.8 (rid215/217/218) 块体回退为备份版本（备份完整且合法，重放内容反而损坏）。"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from _repair_apply import find_block_30jiang

BOOK_MD = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
BAK = "_vlm/md_backup/30讲-线代.md"
REVERT = {"1.5": 1, "1.7": 1, "1.8": 1}   # num -> 讲

cur = open(BOOK_MD, encoding="utf-8").read().split("\n")
bak = open(BAK, encoding="utf-8").read().split("\n")
for num, lec in REVERT.items():
    lc = find_block_30jiang(cur, lec, num, "A")
    lb = find_block_30jiang(bak, lec, num, "A")
    assert lc and lc[0] != "INSERT" and lb and lb[0] != "INSERT", num
    cb, ce = lc
    bb, be = lb
    cur = cur[:cb + 1] + bak[bb + 1:be] + cur[ce:]
    print(f"题{num}: 回退为备份块体（{be-bb-1} 行）")
open(BOOK_MD, "w", encoding="utf-8", newline="").write("\n".join(cur))
print("done")
