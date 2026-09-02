# -*- coding: utf-8 -*-
"""修复 \nRightarrow 乱码：
1. 线代: A \\neq B \\nRightarrow |A| \\neq$ |B| → A \\neq B \\not\\Rightarrow |A| \\neq |B|$（且 $ 边界归位）
2. 高数: \\nRightarrow → \\Rightarrow（可微充分条件）
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def patch(md, pairs):
    txt = open(md, encoding="utf-8").read()
    ok = 0
    for old, new in pairs:
        if old not in txt:
            print(f"  ⚠ 未找到: {old[:40]!r}")
            continue
        txt = txt.replace(old, new, 1)
        ok += 1
    open(md, "w", encoding="utf-8").write(txt)
    print(f"{md.split('/')[-2]}: 修复 {ok}/{len(pairs)}")

patch("11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md", [
    ("A \\neq B \\nRightarrow |A| \\neq$ |B|;",
     "A \\neq B \\not\\Rightarrow |A| \\neq |B|$;"),
])

patch("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", [
    ("\\nRightarrow\\", "\\Rightarrow\\"),
])
