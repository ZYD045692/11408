# -*- coding: utf-8 -*-
# 假设"每章都有习题"，检查 408 四本拆分稿每章的考点/习题文件数
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for b in ["数据结构", "操作系统", "计算机组成原理", "计算机网络"]:
    root = f"11408/拆分稿/{b}"
    print(f"\n===== {b} =====")
    for ch in sorted(os.listdir(root)):
        chp = os.path.join(root, ch)
        if not os.path.isdir(chp):
            continue
        n_ex = len([f for f in os.listdir(os.path.join(chp, "习题")) if f.endswith(".md")]) if os.path.isdir(os.path.join(chp, "习题")) else 0
        n_k = len([f for f in os.listdir(os.path.join(chp, "考点")) if f.endswith(".md")]) if os.path.isdir(os.path.join(chp, "考点")) else 0
        flag = "  ⚠ 无习题!" if n_ex == 0 else ""
        print(f"  {ch}: 考点{n_k} 习题{n_ex}{flag}")
