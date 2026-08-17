# -*- coding: utf-8 -*-
"""把被误当大纲的正文去 #：
1. 含 ？/? 的标题（复习提示/本章疑难点问答）→ 普通文本
2. 明确的正文段（数据结构"大规模高效排序算法"、高数"有人通俗地念成"）→ 普通文本
保留：一/二/三 题型、例 N.N / 【例 N.N】
"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")

# 明确的正文段（整句段落，非编号问答）
SENTENCE = [
    "3. 大规模高效排序算法：当 n 很大时，应选用时间复杂度为",
    "有人通俗地念成：两个正项级数",
]

for f in sorted(glob.glob("11408/origin/*/*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    n_demote = 0
    for i, l in enumerate(lines):
        m = HEAD.match(l)
        if not m:
            continue
        t = m.group(2).strip()
        # 保留例题标题
        if re.match(r"^(例\s*\d|【例\s*\d)", t):
            continue
        # 保留题型（一、选择题…）
        if re.match(r"^[一二三四]、\s*(选择|填空|解答)", t):
            continue
        if "？" in t or "?" in t:
            lines[i] = t
            n_demote += 1
        elif any(t.startswith(s) for s in SENTENCE):
            lines[i] = t
            n_demote += 1
    if n_demote:
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        print(f"{f.split('/')[-2]}: 去#正文 {n_demote} 处")
