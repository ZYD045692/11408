# -*- coding: utf-8 -*-
# 统计 408 四本书所有标题的类型分布，决定统一层级
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
CH = re.compile(r'^第\s*\d+\s*[章部分]')
SEC = re.compile(r'^(\d+)\.(\d+)\s')          # N.M
SUB = re.compile(r'^(\d+)\.(\d+)\.(\d+)\s')    # N.M.K
SUB4 = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)\s')  # N.M.K.L
ANSWER = re.compile(r'^\d{1,3}\s*[\\]?\.\s*[A-D](?:、[A-D])?$')  # 03. D / 10 \. C
NUMITEM = re.compile(r'^\d{1,3}\s*[\\]?\.\s+\S')   # 1. 中文标题 / 2. xxx
PAREN = re.compile(r'^（\s*\d+\s*）\s*\S')           # （1） xxx
ZKD = re.compile(r'^考点追踪')
KG = re.compile(r'^【考纲内容】|^【复习提示】')
JX = re.compile(r'^本节(习题|试题)精选|^本节小结|^答案与解析')
TX = re.compile(r'^[单项多选综合填空应用算法设计].{0,6}题$')

for md in BOOKS:
    print("=" * 70)
    print(os.path.basename(md))
    cats = {"章(H1)":0, "节N.M":{}, "小节N.M.K":{}, "四级N.M.K.L":{}, "考纲/复习":{},
            "考点追踪":{}, "习题/答案节":{}, "题型(单选等)":{}, "答案行(应去#)":{},
            "数字条目N.":{}, "括号条目(N)":{}, "其他":{}}
    lines = open(md, encoding="utf-8").read().split("\n")
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if not m:
            continue
        lv = len(m.group(1))
        t = m.group(2).strip()
        if t.startswith("📑"):
            continue
        if CH.match(t):
            cats["章(H1)"] += 1
        elif SUB4.match(t):
            cats["四级N.M.K.L"].setdefault(lv, 0); cats["四级N.M.K.L"][lv]+=1
        elif SUB.match(t):
            cats["小节N.M.K"].setdefault(lv, 0); cats["小节N.M.K"][lv]+=1
        elif SEC.match(t):
            cats["节N.M"].setdefault(lv, 0); cats["节N.M"][lv]+=1
        elif KG.match(t):
            cats["考纲/复习"].setdefault(lv, 0); cats["考纲/复习"][lv]+=1
        elif ZKD.match(t):
            cats["考点追踪"].setdefault(lv, 0); cats["考点追踪"][lv]+=1
        elif JX.match(t):
            cats["习题/答案节"].setdefault(lv, 0); cats["习题/答案节"][lv]+=1
        elif TX.match(t):
            cats["题型(单选等)"].setdefault(lv, 0); cats["题型(单选等)"][lv]+=1
        elif ANSWER.match(t):
            cats["答案行(应去#)"].setdefault(lv, 0); cats["答案行(应去#)"][lv]+=1
        elif NUMITEM.match(t):
            cats["数字条目N."].setdefault(lv, 0); cats["数字条目N."][lv]+=1
        elif PAREN.match(t):
            cats["括号条目(N)"].setdefault(lv, 0); cats["括号条目(N)"][lv]+=1
        else:
            cats["其他"].setdefault(lv, 0); cats["其他"][lv]+=1
    for k, v in cats.items():
        if isinstance(v, int):
            print(f"  {k}: {v}")
        elif v:
            print(f"  {k}: { {lvl: n for lvl, n in sorted(v.items())} }")
        else:
            print(f"  {k}: (0)")
