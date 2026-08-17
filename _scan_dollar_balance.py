# -*- coding: utf-8 -*-
# 精确 $ 配对检查：跳过代码块，找未闭合的 $$ 块和 $ 行内公式
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOOKS = [
    "11408/origin/2027数据结构/2027数据结构.md",
    "11408/origin/2027操作系统/2027操作系统.md",
    "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "11408/origin/2027计算机网络/2027计算机网络.md",
    "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md",
    "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md",
]

def line_of(text, pos):
    return text.count("\n", 0, pos) + 1

for md in BOOKS:
    text = open(md, encoding="utf-8").read()
    n = len(text)
    in_code = False
    i = 0
    # 记录打开的数学边界（未闭合）
    open_block = None
    open_inline = None
    unclosed = []   # (类型, 行号, 上下文)
    while i < n:
        if text.startswith("```", i):
            if in_code:
                in_code = False
            else:
                in_code = True
            i += 3
            continue
        if in_code:
            i += 1
            continue
        c = text[i]
        if c == "$":
            if text.startswith("$$", i):
                if open_block is None:
                    open_block = i
                else:
                    open_block = None
                i += 2
                continue
            else:
                if open_inline is None:
                    open_inline = i
                else:
                    open_inline = None
                i += 1
                continue
        i += 1
    if open_block is not None:
        ln = line_of(text, open_block)
        ctx = text[max(0, open_block-30):open_block+30].replace("\n", " ")
        unclosed.append(("$$块", ln, ctx))
    if open_inline is not None:
        ln = line_of(text, open_inline)
        ctx = text[max(0, open_inline-30):open_inline+30].replace("\n", " ")
        unclosed.append(("$行内", ln, ctx))
    print(f"===== {os.path.basename(md.split('/')[-2])} =====")
    if unclosed:
        for t, ln, ctx in unclosed:
            print(f"  ⚠ 未闭合[{t}] L{ln}: ...{ctx}...")
    else:
        print("  ✓ $ 全部配对")
