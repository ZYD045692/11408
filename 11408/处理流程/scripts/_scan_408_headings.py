# -*- coding: utf-8 -*-
# 408 书：按编号深度判断期望层级，输出所有层级不符的标题
import io, sys, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
]

HEAD = re.compile(r'^(#{1,6})\s+(.*)$')
# 章: 第N章 / 第N部分 / 纯编号
CH_NUM = re.compile(r'^第\s*\d+\s*[章讲部分]')
NUM = re.compile(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?\s')
SPECIAL = ["【考纲内容】", "【复习提示】", "【小结】", "考点追踪", "本节习题精选", "本节试题精选", "本节小结", "答案与解析", "思维拓展", "易混淆知识点"]

for md in BOOKS:
    print("=" * 70)
    print(os.path.basename(md))
    lines = open(md, encoding="utf-8").read().split("\n")
    wrong = []
    for i, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if not m:
            continue
        lv = len(m.group(1))
        text = m.group(2).strip()
        # 跳过 TOC 快速跳转
        if text.startswith("📑"):
            continue
        if CH_NUM.match(text):
            exp = 1
        else:
            nm = NUM.match(text)
            if nm:
                parts = [p for p in nm.groups() if p]
                exp = len(parts) + 1  # 1.x -> H2, 1.1.x -> H3, 1.1.1.x -> H4
            else:
                exp = None
        if exp and lv != exp:
            wrong.append((i, lv, exp, text))
    print(f"层级不符 {len(wrong)} 处:")
    cur = None
    for i, lv, exp, t in wrong:
        if lv == 2 and exp == 3:
            tag = "节被降为H3(应H2)"
        elif lv == 3 and exp == 2:
            tag = "节被升为H3(应H2)"
        elif lv == 3 and exp == 4:
            tag = "小节被升为H3(应H4)"
        elif lv == 4 and exp == 3:
            tag = "小节被降为H4(应H3)"
        elif lv == 1 and exp == 2:
            tag = "节被升为H1(应H2)"
        elif lv == 2 and exp == 1:
            tag = "章被降为H2(应H1)"
        elif lv == 4 and exp == 5:
            tag = "子节被降为H4(应H5)"
        elif lv == 5 and exp == 4:
            tag = "子节被升为H5(应H4)"
        else:
            tag = f"H{lv}->H{exp}"
        print(f"  L{i}: {tag}  {t[:55]}")
