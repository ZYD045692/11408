# -*- coding: utf-8 -*-
"""把游离的【考纲内容】/【复习提示】块移到对应 # 第N章 之后。
适用：OS ch2/ch4, 数据结构 ch2/ch6/ch7, 计组 ch4, 网络 ch4
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

H1 = re.compile(r"^# 第(\d+)章\b")
KG = re.compile(r"^## 【考纲内容】")

JOBS = [
    ("11408/origin/2027操作系统/2027操作系统.md", [2, 4]),
    ("11408/origin/2027数据结构/2027数据结构.md", [2, 6, 7]),
    ("11408/origin/2027计算机组成原理/2027计算机组成原理.md", [4]),
    ("11408/origin/2027计算机网络/2027计算机网络.md", [4]),
]

for f, chs in JOBS:
    lines = open(f, encoding="utf-8").read().split("\n")
    changed = 0
    for n in chs:
        # 找到 # 第n章 标题
        h1 = None
        for i, l in enumerate(lines):
            if l.startswith(f"# 第{n}章") and (len(l) == len(f"# 第{n}章") or l[len(f"# 第{n}章")] in " \t"):
                h1 = i
                break
        if h1 is None:
            print(f"  !! {f} 没找到 # 第{n}章")
            continue
        # 从 h1 往前找最近的 ## 【考纲内容】
        kg = None
        for k in range(h1 - 1, -1, -1):
            s = lines[k].strip()
            if KG.match(s):
                kg = k
                break
            if s.startswith("## ") and s != "## 【复习提示】":
                break
        if kg is None:
            print(f"  !! {f} 第{n}章 没找到游离考纲块")
            continue
        block = lines[kg:h1]
        # 去掉块尾空白行
        while block and not block[-1].strip():
            block.pop()
        # 删除块
        del lines[kg:h1]
        # 现在 # 第n章 位于 kg 位置，把块插到它后面
        new_h1 = kg
        lines = lines[:new_h1 + 1] + [""] + block + lines[new_h1 + 1:]
        changed += 1
        print(f"  {f.split('/')[-2]}: 第{n}章 考纲块移动 ({len(block)} 行)")
    if changed:
        open(f, "w", encoding="utf-8").write("\n".join(lines))
print("done")
