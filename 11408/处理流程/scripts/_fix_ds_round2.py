# -*- coding: utf-8 -*-
"""2026-08-17 第二轮：2027数据结构 标题级残留修复。
按 agent 报告 + 人工核实逐条修。每处修改前先校验行内容匹配预期，不匹配则跳过并报告。
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/2027数据结构/2027数据结构.md"
lines = open(F, encoding="utf-8").read().split("\n")
log = []
skip = []

def set_line(ln, new, expect=None):
    """若 expect 给出且当前行不匹配 expect，跳过并记录。"""
    cur = lines[ln - 1]
    if expect is not None and cur.strip() != expect.strip():
        skip.append((ln, cur[:70], "期望[%s]" % expect[:40]))
        return
    lines[ln - 1] = new
    log.append((ln, cur[:50], new[:50]))

# ---------- 1. 考点追踪裸行 → ### （41处，pattern-based） ----------
for i, l in enumerate(lines, 1):
    if l.startswith("考点追踪") and not l.startswith("#"):
        new = "### " + re.sub(r"^考点追踪\s*", "考点追踪 ", l)
        set_line(i, new, l)

# ---------- 2. 考纲子项（一）… → ### （29处） ----------
KG = [5, 743, 745, 3706, 3708, 3710, 3712, 3714, 3716, 7064, 7076, 11490, 11492,
      15349, 15351, 15353, 15355, 15357, 15361, 15363, 15365,
      19146, 19148, 19154, 19158, 19162, 19164, 19166, 19170]
for ln in KG:
    cur = lines[ln - 1]
    if not cur.startswith("（"):
        skip.append((ln, cur[:60], "考纲子项未匹配（开头非（一））"))
        continue
    set_line(ln, "### " + cur, cur)

# ---------- 3. 考纲（五）（六）顺序颠倒：L19162/L19164 交换 ----------
a, b = lines[19162 - 1], lines[19164 - 1]
if "（六）基数排序" in a and "（五）" in b:
    lines[19162 - 1], lines[19164 - 1] = b, a
    log.append((19162, a[:30], b[:30]))
    log.append((19164, b[:30], a[:30]))
else:
    skip.append((19162, a[:40], "（五）（六）交换前提不满足"))

# ---------- 4. 裸（N）括号子项 → ##### （10处） ----------
PAREN = [3866, 3873, 3882, 3891, 3899, 4715, 8136, 10888, 10926, 10945]
for ln in PAREN:
    cur = lines[ln - 1]
    if not re.match(r"^（\d）", cur.strip()):
        skip.append((ln, cur[:60], "（N）子项未匹配"))
        continue
    set_line(ln, "##### " + cur.strip(), cur)

# ---------- 5. N. 数字条目升 #### （2处） ----------
# L6656: " $^{*}$3. next 数组的推理公式"
cur = lines[6656 - 1]
set_line(6656, "#### 3. next 数组的推理公式", cur)
# L15133: "10. 【解答】"
cur = lines[15133 - 1]
set_line(15133, "#### 10. 【解答】", cur)

# ---------- 6. 括号条目 H4→H5 （3处） ----------
for ln in [4723, 8180, 8202]:
    cur = lines[ln - 1]
    if not cur.startswith("#### （"):
        skip.append((ln, cur[:60], "期望 #### （N）"))
        continue
    set_line(ln, cur.replace("#### ", "##### ", 1), cur)

# ---------- 7. 节标题缺「一、」前缀（6处） ----------
for ln in [817, 843, 6122, 6231, 19211, 19239]:
    cur = lines[ln - 1]
    if cur.strip() != "#### 单项选择题":
        skip.append((ln, cur[:60], "期望 #### 单项选择题"))
        continue
    set_line(ln, "#### 一、 单项选择题", cur)

# ---------- 8. 归纳总结框内 H4 降为正文（4处） ----------
for ln, txt in [(699, "1. 循环主体中的变量参与循环条件的判断"),
                (714, "2. 循环主体中的变量与循环条件无关"),
                (15294, "1. 关于图的基本操作"),
                (22464, "4. 混合策略：")]:
    cur = lines[ln - 1]
    expect = "#### " + txt
    if cur.strip() != expect:
        skip.append((ln, cur[:60], "期望[%s]" % expect[:40]))
        continue
    set_line(ln, txt, cur)

# ---------- 9. OCR：L8182 考点追踪缺空格 + 树形→中序序列 ----------
cur = lines[8182 - 1]
if cur.strip() == "### 考点追踪由后序序列和树形构造一棵二叉树（2017、2023）":
    set_line(8182, "### 考点追踪 由后序序列和中序序列构造一棵二叉树（2017、2023）", cur)
else:
    skip.append((8182, cur[:60], "OCR行不匹配"))

# ---------- 写回 ----------
open(F, "w", encoding="utf-8").write("\n".join(lines))
print("=== 已修改 %d 处 ===" % len(log))
for ln, a, b in log:
    print("L%-6d |%s|  ->  |%s|" % (ln, a, b))
if skip:
    print("\n=== 跳过 %d 处（预期不匹配，需人工看）===" % len(skip))
    for ln, a, why in skip:
        print("L%-6d |%s|  (%s)" % (ln, a, why))
