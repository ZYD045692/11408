# -*- coding: utf-8 -*-
# 公式边界解析器：块模式($$)内 $ 不算边界；跳过 \$ 转义
# 输出：未配 $$、未配 $、块内 $ 计数
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
    in_block = None    # $$ 块开启位置
    in_inline = None   # $ 行内开启位置
    inblock_dollar = 0  # 块内出现的 $（单）计数
    unclosed_block = None
    unclosed_inline = None
    i = 0
    while i < n:
        if text.startswith("```", i):
            in_code = not in_code
            i += 3
            continue
        if in_code:
            i += 1
            continue
        c = text[i]
        if c == "\\" and i + 1 < n and text[i+1] == "$":
            i += 2  # \$ 转义
            continue
        if c == "$":
            if text.startswith("$$", i):
                if in_block is not None:
                    in_block = None
                else:
                    if in_inline is not None:
                        in_inline = None  # 行内被 $$ 关闭？记录
                    in_block = i
                i += 2
                continue
            else:
                if in_block is not None:
                    inblock_dollar += 1
                elif in_inline is not None:
                    in_inline = None
                else:
                    in_inline = i
                i += 1
                continue
        i += 1
    print(f"===== {os.path.basename(md.split('/')[-2])} =====")
    if in_block is not None:
        ln = line_of(text, in_block)
        print(f"  ⚠ 未配 $$ 在 L{ln}: {text[max(0,in_block-25):in_block+25]!r}")
    if in_inline is not None:
        ln = line_of(text, in_inline)
        print(f"  ⚠ 未配 $ 在 L{ln}: {text[max(0,in_inline-25):in_inline+25]!r}")
    if inblock_dollar:
        print(f"  ℹ 块内出现 $（单）共 {inblock_dollar} 处")
    if in_block is None and in_inline is None:
        print("  ✓ 边界完整")
