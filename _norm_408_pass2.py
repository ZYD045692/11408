# -*- coding: utf-8 -*-
"""408 第二遍：上下文修正跳级。

数字条目/括号条目/上标条目的目标层级 = 最近祖先层级 + 1；
同一类条目连续出现视为兄弟，共享同一层级。
"""
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
NUMITEM = re.compile(r'^\d{1,3}\s*[\\]?\.\s+\S')
PAREN = re.compile(r'^（\s*\d+\s*[）)]\s*\S|^\(\s*\d+\s*\)\s*\S')
SUPER = re.compile(r'^\$\^.*\$\s*\d*\s*[\.．]?\s*\S')
BULLET = re.compile(r'^•\s')

def item_kind(t):
    if SUPER.match(t): return 'super'
    if NUMITEM.match(t): return 'numitem'
    if PAREN.match(t): return 'paren'
    return None

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    stack = []
    prev_cat = None
    prev_target = 0
    changed = 0
    for i, l in enumerate(lines):
        m = HEAD.match(l)
        if not m:
            continue
        L = len(m.group(1))
        t = m.group(2).strip()
        if t.startswith("📑"):
            continue
        cat = item_kind(t)
        if cat:
            if cat == prev_cat:
                target = prev_target
            else:
                while stack and stack[-1] >= L:
                    stack.pop()
                parent = stack[-1] if stack else 1
                target = parent + 1
            while stack and stack[-1] >= target:
                stack.pop()
            stack.append(target)
        else:
            target = L
            while stack and stack[-1] >= target:
                stack.pop()
            stack.append(target)
        if target != L:
            lines[i] = "#" * target + " " + t
            changed += 1
        prev_cat = cat
        prev_target = target
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{os.path.basename(md)}: 调整 {changed} 处")
