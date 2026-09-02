# -*- coding: utf-8 -*-
# 列出 408 各书 "其他" 类标题（未被任何规则匹配的），按文本去重统计
import io, sys, re, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
CH = re.compile(r'^第\s*\d+\s*[章部分]')
SEC = re.compile(r'^(\d+)\.(\d+)\s')
SUB = re.compile(r'^(\d+)\.(\d+)\.(\d+)\s')
KG = re.compile(r'^【考纲内容】|^【复习提示】')
ZKD = re.compile(r'^考点追踪')
JX = re.compile(r'^本节(习题|试题)精选|^本节小结|^答案与解析')
TX = re.compile(r'^[单项多选综合填空应用算法设计].{0,6}题$')
ANSWER = re.compile(r'^\d{1,3}\s*[\\]?\.\s*[A-D](?:、[A-D])?$')
NUMITEM = re.compile(r'^\d{1,3}\s*[\\]?\.\s+\S')
PAREN = re.compile(r'^（\s*\d+\s*）\s*\S')

for md in BOOKS:
    print("=" * 70)
    print(os.path.basename(md))
    cnt = Counter()
    lines = open(md, encoding="utf-8").read().split("\n")
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if not m:
            continue
        lv = len(m.group(1))
        t = m.group(2).strip()
        if t.startswith("📑") or CH.match(t) or SEC.match(t) or SUB.match(t) or KG.match(t) \
           or ZKD.match(t) or JX.match(t) or TX.match(t) or ANSWER.match(t) or NUMITEM.match(t) or PAREN.match(t):
            continue
        cnt[(lv, t[:60])] += 1
    for (lv, t), n in sorted(cnt.items()):
        print(f"  H{lv} ×{n}: {t}")
