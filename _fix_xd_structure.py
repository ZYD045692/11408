# -*- coding: utf-8 -*-
"""线代结构性修复：
1. 被降级的节标题 恢复为 #### （三 行列式的逆序数法定义、五 矩阵的相似对角化）
2. 节内编号子项/例题 #### → #####（部分 ③ 项）
3. 正文泄漏（方法二/示例/解/证/记住/看到…）→ 去 # 变正文
4. 第3讲/第5讲 补插「### 基础内容精讲」
5. 第5讲 游离的「### 特征值与特征向量」→ 正文
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

f = "11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md"
lines = open(f, encoding="utf-8").read().split("\n")

PROMOTE = {
    "三 行列式的逆序数法定义（第二种定义）",
    "五 矩阵的相似对角化",
}

TO_H5 = {
    "排列和逆序",
    "2 n 阶行列式的定义",
    "$n(n \\geqslant 2)$ 阶行列式",
    "例1.5 计算行列式",
    "2 递推法",
    "例1.7",
    "3 行列式表示的函数和方程",
    "例1.9 设关于 $\\lambda$的方程",
    "1  n 维向量空间中的一个基可表达所有信息",
    "2 矩阵信息表达中的关系",
    "2 逆矩阵的性质与重要公式",
    "3 用定义法求可逆矩阵的逆矩阵",
    "初等变换",
    "2 初等矩阵的定义",
    "3 初等矩阵的性质与重要公式",
    "5 行阶梯形矩阵与行最简阶梯形矩阵",
    "6 简单分块矩阵的逆",
    "③ 有关秩的几个重要式子",
    "向量的概念和运算",
    "2 向量的内积与正交",
    "3 正交矩阵 行（列）向量长度为1的单位向量，且相互正交",
    "4 向量组的线性表示与线性相关的概念",
    "5 判别线性相关性的七大定理 ★（不需要掌握证明）",
    "3 极大线性无关组、等价向量组、向量组的秩",
    "示例1",
    "例 3.7 设向量组",
    "有解的条件",
    "2 解的性质",
    "3 基础解系和解的结构",
    "4 求解方法与步骤",
    "1 有解的条件",
    "3 求解方法与步骤",
    "示例",
    "可相似对角化的充分条件",
    "1 实对称矩阵的性质",
    "2 实对称矩阵相似对角化的基本步骤",
    "线性变换的定义",
    "2 矩阵合同的定义与性质",
    "惯性定理",
    "定义",
    "2 二次型正定的充要条件",
    "3 二次型正定的必要条件",
    "例 6.10 判别二次型",
}

TO_H6 = {
    "1 极大线性无关组",
    "3 向量组的秩",
    "4 有关秩的重要定理和公式",
}

TO_PLAIN_PREFIX = (
    "方法二 对该矩阵作初等变换",
    "2.15 设4阶矩阵",
    "2.12 2 解 矩阵",
    "示例 有这样的一个矩阵",
    "4 个4维列向量",
    "② 等价向量组",
    "→4维空间中的2维子空间",
    "记住结论",
    "4.8 解 对增广矩阵",
    "③ 求可逆矩阵 P",
    "看到正交变换一定要想到",
    "6.9 设二次型",
    "方法二 二次型",
    "6.9 解 (1) 二次型",
)

HEAD = re.compile(r"^(#{2,6})\s+(.*)$")
n_prom, n_h5, n_h6, n_plain, n_stray = 0, 0, 0, 0, 0
out = []
i = 0
while i < len(lines):
    l = lines[i]
    m = HEAD.match(l)
    if m:
        lv = len(m.group(1))
        t = m.group(2).strip()
        if lv == 3 and t == "特征值与特征向量":
            # 第5讲游离讲标题
            out.append(t)
            n_stray += 1
            i += 1
            continue
        if lv == 4:
            if t in PROMOTE:  # 不会发生（这些是正文），但保险
                l = f"#### {t}"; n_prom += 1
            elif t in TO_H5:
                l = f"##### {t}"; n_h5 += 1
            elif t in TO_H6:
                l = f"###### {t}"; n_h6 += 1
            elif t.startswith(TO_PLAIN_PREFIX):
                l = t; n_plain += 1
    out.append(l)
    i += 1

# 处理正文行的提升（PROMOTE 目标当前是正文）
lines2 = out
out2 = []
for l in lines2:
    if not l.startswith("#") and l.strip() in PROMOTE:
        out2.append(f"#### {l.strip()}")
        n_prom += 1
    else:
        out2.append(l)

# 补插 基础内容精讲（第3讲 / 第5讲）
final = []
inserted = 0
anchor3 = "#### 线性代数中的一号人物——向量"
anchor5 = "#### 特征值与特征向量的定义"
for l in out2:
    if l.strip() == anchor3 and inserted < 1:
        final.append("### 基础内容精讲")
        final.append("")
        inserted += 1
    elif l.strip() == anchor5 and inserted < 2:
        final.append("### 基础内容精讲")
        final.append("")
        inserted += 1
    final.append(l)

open(f, "w", encoding="utf-8").write("\n".join(final))
print(f"提升节标题 {n_prom} | 降H5 {n_h5} | 降H6 {n_h6} | 去#正文 {n_plain} | 去#游离讲标题 {n_stray} | 补插基础内容精讲 {inserted}")
