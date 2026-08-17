# -*- coding: utf-8 -*-
"""线代收尾：
1. 正文里的例N.N 提升为标题（父级+1，短标题，题目进正文）
2. 三 二次齐次式等于1 → 正文；重建三节名为「三 二次型的标准形、规范形与惯性定理」
3. 可相似对角化的充分条件 → 正文（实对称矩阵的描述）
4. 第4讲 裸「示例」→ 正文
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
EX = re.compile(r"^例\s*(\d+\.\d+)\s+(\S.*)$")

# 记录每个位置之前的"父级标题层级"（跳过 例/定理 标题）
parent_level = [0] * len(lines)
last_lv, last_is_ex_or_thm = 0, False
for i, l in enumerate(lines):
    m = HEAD.match(l)
    if m:
        lv = len(m.group(1))
        t = m.group(2).strip()
        is_ex = bool(re.match(r"^例\s*\d", t))
        is_thm = bool(re.match(r"^定理\s*\d", t))
        parent_level[i] = last_lv if last_is_ex_or_thm else lv
        last_lv, last_is_ex_or_thm = lv, (is_ex or is_thm)
    else:
        parent_level[i] = last_lv

# 处理
out = []
n_ex = 0
for i, l in enumerate(lines):
    s = l.strip()
    # 1. 提升正文例题
    if not l.startswith("#") and not s.startswith("<") and not s.startswith("!") and not s.startswith("$"):
        m = EX.match(s)
        if m:
            num = m.group(1)
            rest = m.group(2).strip()
            plv = parent_level[i]
            if plv == 4:
                h = "##### "
            elif plv == 5:
                h = "###### "
            elif plv == 3:
                h = "#### "
            else:
                h = "##### "
            out.append(f"{h}例{num}")
            out.append("")
            out.append(rest)
            n_ex += 1
            continue
    out.append(l)

# 2. 三 二次齐次式等于1 → 正文
for i, l in enumerate(out):
    if l == "#### 三 二次齐次式等于1":
        out[i] = "二次齐次式等于1"
        break
# 重建三节名
for i, l in enumerate(out):
    if l == "##### 1 二次型的标准形、规范形":
        out.insert(i, "#### 三 二次型的标准形、规范形与惯性定理")
        out.insert(i+1, "")
        break

# 3. 可相似对角化的充分条件 → 正文
n3 = 0
for i, l in enumerate(out):
    if l == "##### 可相似对角化的充分条件":
        out[i] = "可相似对角化的充分条件"
        n3 += 1

# 4. 第4讲裸「示例」→ 正文
n4 = 0
for i, l in enumerate(out):
    if l == "##### 示例":
        out[i] = "示例"
        n4 += 1

print(f"例题提升 {n_ex} | 二次齐次式降级+重建节 | 充分条件降级 {n3} | 示例降级 {n4}")
open(f, "w", encoding="utf-8").write("\n".join(out))
