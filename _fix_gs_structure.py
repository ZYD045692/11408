# -*- coding: utf-8 -*-
"""高数结构性修复：
1. 恢复被降级的节标题：四 幂级数求和函数 / 四 平面第二型曲线积分 → ####
2. 正文泄漏 → 去 #（核(自带光环)、2.61 解 因为、3.9 证明、4.7 证明、证 将大区间…）
3. 乱码标题修复：8 {x_} → 8
4. 第16讲「四 幂级数求和函数」下 4 项 → H5；第18讲「四 平面第二型曲线积分」下 4 项 → H5
5. 第3讲 补插「### 基础习题精练」
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
lines = open(f, encoding="utf-8").read().split("\n")

PROMOTE = {
    "四 幂级数求和函数（解答题/客观题）",
    "四 平面第二型曲线积分  $\\rightarrow$ 进入向量型被积函数求积分",
}

TO_PLAIN_PREFIX = (
    "核(自带光环)",
    "2.61 解 因为",
    "3.9 证明 使用泰勒公式，有",
    "4.7 证明 根据导数定义，有",
    "证 将大区间 [0,1] 分成两个小区间 [0,x] 和 [x,1]",
)

HEAD = re.compile(r"^(#{2,6})\s+(.*)$")

# 第一步：处理标题行
out = []
for l in lines:
    m = HEAD.match(l)
    if m:
        lv = len(m.group(1))
        t = m.group(2).strip()
        if lv == 4:
            if t.startswith(TO_PLAIN_PREFIX):
                out.append(t)
                continue
            if t == "8 {x_} 收敛于 a 的速度问题":
                out.append("#### 8 收敛于 a 的速度问题")
                continue
    out.append(l)

# 第二步：提升被降级的节标题（当前是正文）
out2 = []
for l in out:
    if not l.startswith("#") and l.strip() in PROMOTE:
        out2.append(f"#### {l.strip()}")
    else:
        out2.append(l)

# 第三步：第16讲 四 下的 4 项 → H5；第18讲 四 下的 4 项 → H5
SEC16 = "#### 四 幂级数求和函数（解答题/客观题）"
END16 = "#### 五 函数展开成幂级数"
SEC18 = "#### 四 平面第二型曲线积分  $\\rightarrow$ 进入向量型被积函数求积分"
END18 = "#### 五 第二型曲面积分"
H5_16 = {"概念", "2 运算法则", "3 恒等变形方式", "4 性质"}
H5_18 = {"变力沿曲线做功", "2 概念", "3 性质", "4 计算"}
out3 = []
mode = None
for l in out2:
    s = l.strip()
    if s == SEC16:
        mode = 16
    elif s == SEC18:
        mode = 18
    elif mode == 16 and s == END16:
        mode = None
    elif mode == 18 and s == END18:
        mode = None
    if mode == 16 and HEAD.match(l) and len(HEAD.match(l).group(1)) == 4 and HEAD.match(l).group(2).strip() in H5_16:
        l = "##### " + s
    elif mode == 18 and HEAD.match(l) and len(HEAD.match(l).group(1)) == 4 and HEAD.match(l).group(2).strip() in H5_18:
        l = "##### " + s
    out3.append(l)

# 第四步：第3讲 补插 基础习题精练（在 第3讲 内第一个 #### 习题 前）
final = []
inserted = False
j3 = next(i for i, l in enumerate(out3) if l.startswith("## 第3讲"))
for idx, l in enumerate(out3):
    if not inserted and idx > j3 and l == "#### 习题":
        final.append("### 基础习题精练")
        final.append("")
        inserted = True
    final.append(l)

open(f, "w", encoding="utf-8").write("\n".join(final))
print(f"提升节标题2处 | 去#正文 {len([1 for l in final if not l.startswith('#') and 0])} (见下) | 第16/18讲降H5 | 第3讲补插基础习题精练: {inserted}")
