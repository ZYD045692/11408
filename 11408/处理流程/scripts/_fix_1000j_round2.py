# -*- coding: utf-8 -*-
"""2026-08-17 第二轮：1000题解析册 修复。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
lines = open(F, encoding="utf-8").read().split("\n")
log, skip = [], []
ops = []  # (idx, kind, data)

# 1) L3890 章名错位 → 第18章（先改，防移位）
ops.append((3890, "rep", "## 第18章 多元函数积分学"))
# 2) L3757 前补 第17章
ops.append((3757, "insert_before", "## 第17章 多元函数积分学的预备知识"))
# 3) L4603 乱码重复删除
ops.append((4603, "del_dup", None))
# 4) 吞号提取：L9473/L10910/L12721
ops.append((12721, "extract_label", None))
ops.append((10910, "extract_label", None))
ops.append((9473, "extract_label", None))
# 5) L8917 前补 12. 答案
ops.append((8917, "insert_before", "12. 【答案】 $\\frac{1}{3}$"))
# 6) L2 零基础
ops.append((2, "rep", "## 零基础"))

for ln, kind, data in sorted(ops, key=lambda x: -x[0]):
    cur = lines[ln - 1]
    if kind == "rep":
        lines[ln - 1] = data
        log.append((ln, cur[:35], data[:35]))
    elif kind == "insert_before":
        lines[ln - 1:ln - 1] = [data]
        log.append((ln, "前插", data[:35]))
    elif kind == "del_dup":
        if "5. 【答案】" in cur and "k \\\\ -1" in cur:
            del lines[ln - 1]
            log.append((ln, cur[:30] + "…", "删除乱码重复"))
        else:
            skip.append((ln, cur[:50], "乱码重复行不匹配"))
    elif kind == "extract_label":
        m = re.match(r"^(\$\$\\begin\{aligned\}\d+\.\s*【解析】)(.*)$", cur, re.S)
        if not m:
            skip.append((ln, cur[:50], "吞号块不匹配"))
            continue
        label = cur[:m.start(2)]
        label = re.sub(r"^(\$\$\\begin\{aligned\})", "", label).strip()
        # 构造：`N. 【解析】` 行 + 去掉标签的数学块
        label = label.replace("$$\\begin{aligned}", "").strip()
        if label.startswith("\\begin{aligned}"):
            label = label[len("\\begin{aligned}"):].strip()
        # 重新提取：形如 '2.\ 【解析】'
        mm = re.match(r"^(\d+\.\s*【解析】)", cur[len("$$\\begin{aligned}"):])
        if mm:
            label_line = mm.group(1)
            rest = cur[len("$$\\begin{aligned}"):][len(label_line):]
            new_block = "$$\\begin{aligned}" + rest
            lines[ln - 1] = label_line
            lines[ln:ln] = [new_block]
            log.append((ln, cur[:30] + "…", label_line + " | 块"))
        else:
            skip.append((ln, cur[:50], "标签格式未匹配"))

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("=== 已修改 %d 处 ===" % len(log))
for ln, a, b in log:
    print("L%-6d |%s| -> |%s|" % (ln, a, b))
if skip:
    print("\n=== 跳过 %d ===" % len(skip))
    for ln, a, why in skip:
        print("L%-6d |%s|  (%s)" % (ln, a, why))
