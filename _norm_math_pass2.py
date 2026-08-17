# -*- coding: utf-8 -*-
"""30讲数学 第二遍：纯上下文定级（不依赖源层级）。

结构锚点：第N讲=H2, 三件套=H3, 习题/解答=H4（固定并截断栈）。
内容标题：
  - cn/other/example：新内容节，弹栈到 <4，target=栈顶+1（即精讲下=H4，讲下=H3）
  - num：若栈顶==4(在节内) → H5；否则→H4/H3；同类连续(num→num)共享层级
"""
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
LEC  = re.compile(r'^第\s*\d+\s*讲')
BASE = re.compile(r'^基础知识结构$|^基础内容精讲$|^基础习题精练$')
TXHW = re.compile(r'^(习题|解答)$')
CN   = re.compile(r'^[一二三四五六七八九十]+\s*\S')
NUM  = re.compile(r'^\d+\s*\S')
EX   = re.compile(r'^例\s*\d')

def cat_of(t):
    if CN.match(t):  return 'cn'
    if NUM.match(t): return 'num'
    if EX.match(t):  return 'example'
    return 'other'

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
        t = m.group(2).strip()
        if t.startswith("📑"):
            continue
        if LEC.match(t):
            target = 2
        elif BASE.match(t):
            target = 3
        elif TXHW.match(t):
            target = 4
        else:
            cat = cat_of(t)
            if cat == 'num':
                if stack and stack[-1] == 4 and prev_cat == 'cn':
                    target = 5
                elif cat == prev_cat:
                    target = prev_target
                else:
                    while stack and stack[-1] >= 4:
                        stack.pop()
                    target = (stack[-1] if stack else 2) + 1
            else:
                if cat == prev_cat:
                    target = prev_target
                else:
                    while stack and stack[-1] >= 4:
                        stack.pop()
                    target = (stack[-1] if stack else 2) + 1
            while stack and stack[-1] >= target:
                stack.pop()
            stack.append(target)
            prev_cat = cat
            prev_target = target
            if target != len(m.group(1)):
                lines[i] = "#" * target + " " + t
                changed += 1
            continue
        # 结构锚点
        while stack and stack[-1] >= target:
            stack.pop()
        stack.append(target)
        prev_cat = None
        prev_target = target
        if target != len(m.group(1)):
            lines[i] = "#" * target + " " + t
            changed += 1
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{os.path.basename(md)}: pass2 调整 {changed} 处")
