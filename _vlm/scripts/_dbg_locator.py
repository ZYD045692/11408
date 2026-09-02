# -*- coding: utf-8 -*-
"""在备份解析册上测试 find_block_1000 的落点"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
from _repair_apply import find_block_1000

lines = open(os.path.join(V.VLM, "md_backup", "1000题-解析册.md"), encoding="utf-8").read().split("\n")
for sec, num in [("强化篇/高数/第13章 多元函数微分学", "33"),
                 ("强化篇/高数/第13章 多元函数微分学", "10"),
                 ("基础篇/概率论/第2章 一维随机变量及其分布", "13")]:
    loc = find_block_1000(lines, sec, num)
    if loc[0] == "INSERT":
        i = loc[1]
        print(f"{sec} 题{num}: INSERT@L{i} 前={lines[i-1][:30]!r} 后={lines[i][:30]!r}")
    elif loc:
        bi, ei = loc
        print(f"{sec} 题{num}: 块 L{bi}~L{ei} head={lines[bi][:30]!r}")
    else:
        print(f"{sec} 题{num}: None")
