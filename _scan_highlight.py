# -*- coding: utf-8 -*-
# 扫描正文（非代码块）里的 ==高亮== 模式（Obsidian 会把 ==x== 渲染成黄色）
# 常见来源：C 代码比较 a == b == c 的中间 ==b== 被误识别
import io, sys, re, glob
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

pat = re.compile(r"==[^=\n]{1,40}?==")

def strip_inline_code(line):
    """把反引号行内代码 + $公式$ 内的内容替换为占位，避免误报"""
    s = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)
    s = re.sub(r"\$[^$]*\$", lambda m: " " * len(m.group(0)), s)
    return s

for md in BOOKS:
    lines = open(md, encoding="utf-8").read().split("\n")
    in_code = False
    hits = []
    for i, l in enumerate(lines, 1):
        if l.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for m in pat.finditer(strip_inline_code(l)):
            hits.append((i, m.group(0)))
    print(f"===== {md.split('/')[-2]} =====")
    if not hits:
        print("  ✓ 无正文高亮模式")
    else:
        print(f"  ⚠ {len(hits)} 处")
        for ln, h in hits[:12]:
            print(f"    L{ln}: {h!r}")
