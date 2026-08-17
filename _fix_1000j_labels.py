# -*- coding: utf-8 -*-
"""提取被吞进 $$ 块的题号标签：2./40./29. 【解析】"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
lines = open(F, encoding="utf-8").read().split("\n")

PREFIX = "$$\\begin{aligned}"
targets = []
for i, l in enumerate(lines, 1):
    if l.startswith(PREFIX) and "【解析】" in l:
        m = re.match(re.escape(PREFIX) + r"(.*?)【解析】(.*)$", l, re.S)
        if m and re.match(r"^\d+\.", m.group(1).strip()):
            targets.append((i, m))

for ln, m in sorted(targets, reverse=True):
    pre = m.group(1).strip()                # '2.\ '
    pre = re.sub(r"\\?\s*$", "", pre).strip()  # '2.'
    label = pre + " 【解析】"
    rest = m.group(2)
    new_block = PREFIX + rest
    lines[ln - 1] = label
    lines[ln:ln] = [new_block]
    print("L%d -> |%s| |%s|" % (ln, label, new_block[:45]))

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("done, targets:", [t[0] for t in targets])
