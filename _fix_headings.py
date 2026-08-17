# -*- coding: utf-8 -*-
# 统一标题层级：
#   数学书：讲标题统一 ## 第N讲；讲名(H1)去 # 变普通文本
#   408：删除重复章名 H1（章节预告）；公式误当 H1 去 #
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def apply(md, delete=None, replace=None):
    lines = open(md, encoding="utf-8").read().split("\n")
    del_count = rep_count = 0
    if delete:
        del_set = set(delete)
        new_lines = []
        for l in lines:
            if l.strip() in del_set:
                del_count += 1
                continue
            new_lines.append(l)
        lines = new_lines
    if replace:
        for i, l in enumerate(lines):
            s = l.strip()
            for old, new in replace:
                if s == old:
                    lines[i] = new
                    rep_count += 1
                    break
    open(md, "w", encoding="utf-8").write("\n".join(lines))
    print(f"{md.split('/')[-2]}: 删 {del_count} 行, 改 {rep_count} 处")

# 高数：讲标题 H1→H2 + 讲名去 #
apply("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md",
    replace=[
        ("# 第3讲", "## 第3讲"),
        ("# 第4讲 一元函数微分学的计算", "## 第4讲 一元函数微分学的计算"),
        ("# 第9讲", "## 第9讲"),
        ("# 一元函数微分学的应用（一）——几何应用", "一元函数微分学的应用（一）——几何应用"),
        ("# 一元函数微分学的应用（二）——中值定理、微分等式与微分不等式", "一元函数微分学的应用（二）——中值定理、微分等式与微分不等式"),
        ("# 一元函数微分学的应用（三）——物理应用与经济应用", "一元函数微分学的应用（三）——物理应用与经济应用"),
        ("# 一元函数积分学的概念与性质", "一元函数积分学的概念与性质"),
        ("# 一元函数积分学的应用（一） ——几何应用", "一元函数积分学的应用（一） ——几何应用"),
        ("# 一元函数积分学的应用（二）——积分等式与积分不等式", "一元函数积分学的应用（二）——积分等式与积分不等式"),
        ("# 一元函数积分学的应用（三）——物理应用与经济应用", "一元函数积分学的应用（三）——物理应用与经济应用"),
        ("# 多元函数积分学的预备知识（仅数学一）", "多元函数积分学的预备知识（仅数学一）"),
    ])

# 线代：第0讲讲名去 #
apply("11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md",
    replace=[("# 零基础课 ——线性代数入门", "零基础课 ——线性代数入门")])

# 操作系统：删重复章名
apply("11408/origin/2027操作系统/2027操作系统.md",
    delete=["# 计算机系统概述", "# 进程与线程", "# 内存管理", "# 文件管理", "# 输入/输出管理"])

# 计组：删重复章名 + 公式注释去 #
apply("11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    delete=["# 计算机系统概述", "# 指令系统"],
    replace=[("# (R1) +1 → R1", "(R1) +1 → R1")])
