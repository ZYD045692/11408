# -*- coding: utf-8 -*-
"""解析册 origin：把主号题行 `N. 【答案】...` / `N.【解析】...` / `N. （1）【答案】...`
拆成 `#### N.` 标题 + 原剩余内容降为正文。
- 仅处理行首 `数字+点` 的主号（子题号 `(2)` 等不动，避免误伤解析内步骤编号）。
- 全部篇（基础/强化/综合）统一处理，标题层级 H4 挂在 H3 章/题型下。
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
lines = open(F, encoding="utf-8").read().split("\n")

MAIN = re.compile(r"^(\d+)[.、]\s*(.*)$")

out = []
converted = 0
skipped_empty = 0

for raw in lines:
    m = MAIN.match(raw)
    if m and raw[0].isdigit():
        num, rest = m.group(1), m.group(2)
        out.append("#### %s." % num)
        if rest.strip():
            out.append("")
            out.append(rest)
        else:
            skipped_empty += 1
        converted += 1
        continue
    out.append(raw)

open(F, "w", encoding="utf-8").write("\n".join(out))
print("转换题号:", converted)
print("空剩余跳过:", skipped_empty)
