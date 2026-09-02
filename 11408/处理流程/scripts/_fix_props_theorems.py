# -*- coding: utf-8 -*-
"""恢复被降级的 性质N / 定理N 子项标题（拆成 标题+正文）"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")

# 性质 1-7（第1讲 二）→ #####，正文保留完整陈述
props = {
    "性质1 ": ("##### 1 行列互换（转置），行列式不变"),
    "性质2 ": ("##### 2 某行（列）全为零，行列式为零"),
    "性质3 ": ("##### 3 某行（列）的公因子可提出"),
    "性质4 ": ("##### 4 某行（列）为两数之和，可拆成两个行列式"),
    "性质5 ": ("##### 5 两行（列）互换，行列式变号"),
    "性质 6 ": ("##### 6 两行（列）相等或对应成比例，行列式为零"),
    "性质7 ": ("##### 7 某行（列）的 k 倍加到另一行（列），行列式不变"),
}
# 定理 1-9（第3讲）→ ######
theorems = {}
for n in range(1, 10):
    theorems[f"定理{n} "] = f"###### 定理 {n}"
    theorems[f"定理 {n} "] = f"###### 定理 {n}"

n = 0
out = []
for l in lines:
    s = l.strip()
    if not l.startswith("#") and not s.startswith("<") and not s.startswith("$") and not s.startswith("!"):
        done = None
        for prefix, h in props.items():
            if s.startswith(prefix):
                out.append(h)
                out.append("")
                rest = s[len(prefix):].strip()
                if rest:
                    out.append(rest)
                done = True
                n += 1
                break
        if done:
            continue
        for prefix, h in theorems.items():
            if s.startswith(prefix):
                out.append(h)
                out.append("")
                rest = s[len(prefix):].strip()
                if rest:
                    out.append(rest)
                done = True
                n += 1
                break
        if done:
            continue
    out.append(l)
print("恢复 性质/定理:", n)
open(f, "w", encoding="utf-8").write("\n".join(out))
