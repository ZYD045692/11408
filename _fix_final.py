# -*- coding: utf-8 -*-
"""终检修复：
1. 线代 4 处 kaoyan33311 广告残留（含1处嵌进 $$ 公式的）→ 删/移除
2. 线代 2 处 \\xrightarrow 乱码（化学/一成历九）→ 化为
3. 高数 有界函数公式乱码 → 按 img_485.jpg 内容重写
4. 高数 2 处跨行 $...$ 边界空格 → $$...$$
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def patch(md, pairs):
    txt = open(md, encoding="utf-8").read()
    for old, new in pairs:
        if old not in txt:
            print(f"  ⚠ 未找到: {old[:50]!r}")
            continue
        txt = txt.replace(old, new)
    open(md, "w", encoding="utf-8").write(txt)
    print(f"{md.split('/')[-2]}: 修复 {len(pairs)} 组")

# ---- 线代 ----
patch("11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md", [
    # 1. 嵌在 $$ 公式里的广告行 → 删除整行
    ("\n $$一  于 +V：kaoyan33311$$\n", "\n"),
    # 2. 句中广告 + 断行 → 移除广告并接合
    ("此元素所在的一手+V：kaoyan33311\n\n的行数", "此元素所在的行数"),
    # 3. 行内广告整行 → 删除（"化为"在下一句箭头处）
    ("\n一手+V：kaoyan33311化为\n", "\n"),
    # 4. 句中广告 + 断行 → 移除广告并接合
    ("对矩阵一手+V：kaoyan33311\n\n表达式", "对矩阵表达式"),
    # 5. \\xrightarrow 乱码
    ("\\xrightarrow{ 一成历九 }", "\\xrightarrow{ 化为 }"),
    ("\\xrightarrow{ 化学 }", "\\xrightarrow{ 化为 }"),
])

# ---- 高数 ----
patch("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", [
    # 6. 有界函数公式乱码 → 按 img_485.jpg 重写（一元 f(x) on [a,b] / 二元 f(x,y) on D）
    ("""设有界函数

 $ \\left\\{\\begin{array}{l}

f(x) 　 a \\quad\\

f(x, y) 　 O \\quad

\\end{array}\\right. $
""", """设有界函数

$$\\left\\{\\begin{array}{l}
f(x), & x \\in [a, b],\\\\
f(x, y), & (x, y) \\in D
\\end{array}\\right.$$
"""),
    # 7. 跨行公式边界空格 → $$ 块
    (" $ \\left\\{\\begin{array}{l}\n", "$$\\left\\{\\begin{array}{l}\n"),
    ("\\end{array}\\right. $ 按最高次写一般式", "\\end{array}\\right.$$ 按最高次写一般式"),
])
