# -*- coding: utf-8 -*-
"""线代补漏：
1. 第2讲补插 ### 基础习题精练（在 #### 习题 前）
2. 例4.11 / 例4.12 → H5
3. 第5讲「4 由特征值、特征向量反求 A」「5 求 $A^k$ 及 $f(A)$」→ H5
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")

TO_H5 = {
    "例4.11 已知线性方程组",
    "例4.12 已知线性方程组",
    "4 由特征值、特征向量反求 A",
    "5 求  $A^{k}$ 及  $f(A)$",
}

HEAD = re.compile(r"^#{2,6}\s+(.*)$")
out = []
inserted = False
for i, l in enumerate(lines):
    # 第2讲：在基础内容精讲 内、### 基础习题精练 缺失、遇到 #### 习题 时插入
    m = HEAD.match(l)
    if (not inserted) and m and len(m.group(1)) == 4 and m.group(1).strip() == "习题":
        # 判断这是第2讲的 习题（第2讲标题在 1949 附近、且其前无 基础习题精练）
        # 找最近的 ## 第N讲
        j = i
        while j >= 0 and not re.match(r"^## 第\d+讲", lines[j]):
            j -= 1
        if j >= 0 and lines[j].startswith("## 第2讲"):
            # 检查这一讲内是否已有 基础习题精练
            has_jx = any(lines[k].startswith("### 基础习题精练") for k in range(j, i))
            if not has_jx:
                out.append("### 基础习题精练")
                out.append("")
                inserted = True
    if m and len(m.group(1)) == 4 and m.group(1).strip() in TO_H5:
        out.append(f"##### {m.group(1).strip()}")
        continue
    out.append(l)

open(f, "w", encoding="utf-8").write("\n".join(out))
print(f"补插基础习题精练: {inserted} | 降H5: {sum(1 for l in out if l.startswith('##### '))}")
