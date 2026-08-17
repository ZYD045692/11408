# -*- coding: utf-8 -*-
"""1000题两本 origin 标题层级规范化。

  篇(基础篇/强化篇/综合篇) -> H1
  第N章 / 零 基础 / 测试卷N -> H2
  一、选择题 / 二、填空题 / 三、解答题(含说明文字) -> H3
  N. (本题满分…) -> H4
  N. 【答案|解析|分析】 / (N) 【答案】 / 【注】 / 方法一 / 线性代数 / 题干行 -> 普通文本
"""
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
PIAN = re.compile(r'^(基础篇|强化篇|综合篇)\s*$')
ZHANG = re.compile(r'^第\s*\d+\s*章\s*\S')
LING = re.compile(r'^零\s*基础')
TEST = re.compile(r'^测试卷[一二三四]\s*$')
TXTYPE = re.compile(r'^[一二三]、\s*(选择题|填空题|解答题)')
BMF = re.compile(r'^\d{1,2}\s*[\\]?\.\s*[（(]本题满分')
ANSWER = re.compile(r'^\d{1,3}\s*[\\]?\.\s*【(?:答案|解析|分析)】|^\d{1,3}\s*[\\]?\.\s*（\d+）【答案】|^\(\d+\)\s*【答案】|^【注】|^方法[一二三四五]')
SUBJ = re.compile(r'^(线性代数|高等数学|概率论与数理统计|数理统计)\s*$')
STEM = re.compile(r'^\d{1,2}\s*[\\]?\.\s*(设|求|已知|证明|计算|当|若)')

def classify(t):
    if PIAN.match(t):  return ('keep', 1)
    if ZHANG.match(t): return ('keep', 2)
    if LING.match(t):  return ('keep', 2)
    if TEST.match(t):  return ('keep', 2)
    if TXTYPE.match(t): return ('keep', 3)
    if BMF.match(t):   return ('keep', 4)
    if ANSWER.match(t) or SUBJ.match(t) or STEM.match(t): return ('text', None)
    return ('skip', None)

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    keep = {}; n_text = n_skip = 0
    skipped = {}
    new = []
    for l in lines:
        m = HEAD.match(l)
        if not m:
            new.append(l); continue
        t = m.group(2).strip()
        if t.startswith("📑"):
            new.append(l); continue
        kind, arg = classify(t)
        if kind == 'keep':
            keep[arg] = keep.get(arg, 0) + 1
            new.append("#" * arg + " " + t)
        elif kind == 'text':
            n_text += 1
            new.append(t)
        else:
            n_skip += 1
            skipped[t] = skipped.get(t, 0) + 1
            new.append(l)
    open(md, "w", encoding="utf-8").write("\n".join(new))
    print("=" * 60)
    print(os.path.basename(md))
    print("  层级:", {k: keep[k] for k in sorted(keep)})
    print(f"  去#普通: {n_text}  未匹配: {n_skip}")
    if skipped:
        from collections import Counter
        for t, n in sorted(skipped.items(), key=lambda x: -x[1])[:20]:
            print(f"    ×{n}: {t[:60]}")
