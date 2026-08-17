# -*- coding: utf-8 -*-
"""打印 Markdown 文件的大纲（标题层级缩进树）。
用法: python _show_outline.py <文件路径> [行号范围]

示例:
  python _show_outline.py 11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md
  python _show_outline.py 11408/origin/2027数据结构/2027数据结构.md \"100-200\"
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

if len(sys.argv) < 2:
    print("用法: python _show_outline.py <md路径> [行号范围]")
    sys.exit(1)

path = sys.argv[1]
try:
    lines = open(path, encoding="utf-8").read().split("\n")
except FileNotFoundError:
    # 尝试自动在 11408/origin/ 下查找
    import glob
    fs = glob.glob(f"11408/origin/**/{path}", recursive=True) or glob.glob(f"11408/origin/*{path}*/*.md")
    if not fs:
        print(f"文件未找到: {path}")
        sys.exit(1)
    lines = open(fs[0], encoding="utf-8").read().split("\n")

start, end = 0, len(lines)
if len(sys.argv) >= 3:
    m = re.match(r"(\d+)(?:-(\d+))?", sys.argv[2])
    if m:
        start = max(0, int(m.group(1)) - 1)
        end = int(m.group(2)) if m.group(2) else len(lines)

prev = 0
for i in range(start, min(end, len(lines))):
    l = lines[i].rstrip()
    m = re.match(r"^(#{1,6})\s+(.*)$", l)
    if not m:
        continue
    lv = len(m.group(1))
    title = m.group(2).strip()
    indent = "  " * (lv - 1)
    # 标记跳级
    jump = ""
    if lv > prev + 1 and prev > 0:
        jump = "  ⚠ 跳级"
    prev = lv
    print(f"{indent}{title}{jump}")