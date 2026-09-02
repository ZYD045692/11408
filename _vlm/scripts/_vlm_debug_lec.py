# -*- coding: utf-8 -*-
"""调试：高数 md 第7/11/12/17讲的 基础习题精练 节长什么样。"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
text = open("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", encoding="utf-8").read()
blocks = re.split(r"(?m)^## 第(\d+)讲\s*(.*)$", text)
for k in range(1, len(blocks), 3):
    lec, name, body = int(blocks[k]), blocks[k+1].strip(), blocks[k+2]
    if lec not in (7, 11, 12, 17):
        continue
    m = re.search(r"(?m)^### 基础习题精练\s*$", body)
    print(f"== 第{lec}讲 {name} == 习题精练标题: {'有' if m else '无'}")
    if m:
        seg = body[m.start():m.start()+300]
        print("  节首300字:", seg.replace("\n", "⏎")[:280])
    else:
        # 找相近标题
        cand = re.findall(r"(?m)^#{2,4}\s+.*习题.*$", body)
        print("  含'习题'的标题:", cand)
