# -*- coding: utf-8 -*-
# 深度检查：OCR 乱码 / 截断 LaTeX 命令 / $ 错位 / 全角空格混入公式
import io, sys, os, re, glob
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

# 1) 截断/损坏的 LaTeX 命令（常见 OCR 截断）
BROKEN_CMDS = [
    (r"\\qua[\s　]", "\\quad 损坏"),           # \qua 后面空格/全角
    (r"\\cd\b", "\\cdot 截断"),                # \cd
    (r"\\te\b", "\\text 截断"),                # \te
    (r"\\p\b", "\\pi 截断"),                   # \p 单独
    (r"\\lef\b", "\\left 截断"),
    (r"\\righ\b", "\\right 截断"),
    (r"\\be\b", "\\begin 截断"),
    (r"\\en\b", "\\end 截断"),
    (r"\\fr\b", "\\frac 截断"),
    (r"\\sqr\b", "\\sqrt 截断"),
    (r"\\in\b", "\\int 截断"),
    (r"\\li\b", "\\lim 截断"),
    (r"\\nft", "\\infty 截断"),               # nfty 缺 \
    (r"\\righ", "\\right 截断"),
    (r"\\(?:begin|end|frac|text|left|right)\s*[　 ]*\\", "\\后面紧跟\\"),
]
# 2) 公式内全角空格（正常文本里的全角空格不算）
# 3) $ 错位模式
DOLLAR_MIS = [
    (r"\\left\{\$", "$ 在 \\left{ 后"),
    (r"\\end\{\w+\}\$", "$ 在 \\end 后"),
    (r"\\text\{\$", "$ 在 \\text{ 内"),
    (r"\\frac\{[^}]*\}\{\$", "$ 在 \\frac 分母"),
]

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    hits = {}
    for i, l in enumerate(lines, 1):
        for pat, name in BROKEN_CMDS:
            for m in re.finditer(pat, l):
                hits.setdefault(name, []).append((i, l[max(0, m.start()-15):m.end()+15]))
        for pat, name in DOLLAR_MIS:
            for m in re.finditer(pat, l):
                hits.setdefault(name, []).append((i, l[max(0, m.start()-15):m.end()+15]))
    print(f"\n===== {os.path.basename(md.split('/')[-2])} =====")
    if not hits:
        print("  ✓ 无乱码/错位")
        continue
    for name, lst in sorted(hits.items()):
        print(f"  [{name}] {len(lst)} 处")
        for ln, s in lst[:2]:
            print(f"    L{ln}: ...{s}...")
