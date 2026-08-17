# -*- coding: utf-8 -*-
"""试题册 origin：把主号题行 `N. 题目内容` 拆成题号标题 + 内容降为正文。
- 基础篇/强化篇：章节是 H2，题号用 `### N.`（H3）
- 综合篇：题型是 H3，题号用 `#### N.`（H4，与已有 `#### 17.` 解答题一致）
仅处理行首数字+点的主号；已是标题（# 开头）的不动。
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md"
lines = open(F, encoding="utf-8").read().split("\n")

MAIN = re.compile(r"^(\d+)[.、]\s*(.*)$")
PIAN = re.compile(r"^# (基础篇|强化篇|综合篇)\s*$")

out = []
cur_pian = None
converted = 0

for raw in lines:
    m = PIAN.match(raw.strip())
    if m:
        cur_pian = m.group(1)
        out.append(raw)
        continue
    mm = MAIN.match(raw)
    if mm and raw[0].isdigit():
        num, rest = mm.group(1), mm.group(2)
        if cur_pian == "综合篇":
            out.append("#### %s." % num)
        else:
            out.append("### %s." % num)
        if rest.strip():
            out.append("")
            out.append(rest)
        converted += 1
        continue
    out.append(raw)

open(F, "w", encoding="utf-8").write("\n".join(out))
print("转换题号:", converted)
