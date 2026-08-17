# -*- coding: utf-8 -*-
# 假设每章每节都可能有习题：找出"拆分稿有考点文件但无习题文件"的节，
# 并回 origin 核实该节是否真的没有习题区。
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ORIGINS = {
    "数据结构": "11408/origin/2027数据结构/2027数据结构.md",
    "操作系统": "11408/origin/2027操作系统/2027操作系统.md",
    "计算机组成原理": "11408/origin/2027计算机组成原理/2027计算机组成原理.md",
    "计算机网络": "11408/origin/2027计算机网络/2027计算机网络.md",
}

for b, origin in ORIGINS.items():
    root = f"11408/拆分稿/{b}"
    print(f"\n===== {b} =====")
    # 收集拆分稿：每章 考点文件节号 → 习题文件节号集合
    issues = 0
    for ch in sorted(os.listdir(root)):
        chp = os.path.join(root, ch)
        if not os.path.isdir(chp):
            continue
        kao_dir = os.path.join(chp, "考点")
        ex_dir = os.path.join(chp, "习题")
        ex_set = set()
        if os.path.isdir(ex_dir):
            for f in os.listdir(ex_dir):
                m = re.match(r"(\d+)\.(\d+)-", f)
                if m:
                    ex_set.add((int(m.group(1)), int(m.group(2))))
        if not os.path.isdir(kao_dir):
            continue
        for f in sorted(os.listdir(kao_dir)):
            m = re.match(r"(\d+)\.(\d+)-", f)
            if not m:
                continue
            sec = (int(m.group(1)), int(m.group(2)))
            if sec not in ex_set:
                # 有考点无习题 → 去 origin 核实该节是否有习题区
                has_exam = False
                oline = open(origin, encoding="utf-8").read().split("\n")
                in_sec = False
                for l in oline:
                    s = l.strip()
                    if re.match(rf"^### {sec[0]}\.{sec[1]}\s", s):
                        in_sec = True
                        continue
                    if in_sec and re.match(r"^### (\d+)\.(\d+)\s", s):
                        break
                    if in_sec and re.search(r"本节(试题|习题)精选", s):
                        has_exam = True
                        break
                status = "⚠ origin有习题区但拆分缺!" if has_exam else "origin确认无习题区(正常)"
                if has_exam:
                    issues += 1
                print(f"  {ch} 节{sec[0]}.{sec[1]}: {f[:30]} → {status}")
    if issues == 0:
        print("  （所有无习题文件的节，origin 确认确实没有习题区）")
