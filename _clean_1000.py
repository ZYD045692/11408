# -*- coding: utf-8 -*-
"""清洗 1000题 新版 origin（直接改 origin，保持可读性）：
1. 截取正文（删封面/CIP/前言/目录）
2. 删页眉广告行 + 行内广告
3. 删假重复标题 / 修错字标题
4. 按书目录补缺章标题（内容已核实存在）
5. 篇/章标题级别统一
用法: python _clean_1000.py [--apply]  # 不带 --apply 输出到 _tmp_clean/
"""
import io, sys, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HEADER_AD = re.compile(r"考研数学题源探析经典1000题（数学一）|考研数学题源探析经典1000题（分数学一、数学二、数学三）")
INLINE_AD = ["首发公众号：新资料网", "首发公众号：新资料", "联系微信", "一手+V"]

def clean(path, start_line, inserts, deletes, fixes, regex_fixes):
    lines = open(path, encoding="utf-8").read().split("\n")
    out = []
    for i in range(start_line - 1, len(lines)):
        ln = i + 1
        raw = lines[i]
        s = raw.strip()
        # 1) 页眉广告整行删除
        if HEADER_AD.search(s):
            continue
        # 2) 假重复标题删除
        if ln in deletes:
            continue
        # 3) 插入补章标题
        if ln in inserts:
            out.append(inserts[ln])
        # 4) 行内广告清除
        for a in INLINE_AD:
            raw = raw.replace(a, "")
        # 5) 错字/乱码修正（字符串 + 正则）
        for old, new in fixes:
            raw = raw.replace(old, new)
        for pat, new in regex_fixes:
            raw = re.sub(pat, new, raw)
        # 6) 标题级别统一
        raw = re.sub(r"^## (第\d+章 .+)$", r"# \1", raw)
        raw = re.sub(r"^## (测试卷.+)", r"# \1", raw)
        raw = re.sub(r"^## (零\s*基础.*)$", r"# \1", raw)
        raw = re.sub(r"^## (基础篇|强化篇|综合篇)$", r"# \1", raw)
        out.append(raw)
    # 尾部连续空行清理
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"

JOBS = [
    # ============ 试题册 ============
    dict(book="27张宇1000题数一【试题册】", start=184,
         inserts={
             1529: "# 第17章 多元函数积分学的预备知识",
             2663: "# 第5章 大数定律与中心极限定理",
             3160: "# 第4章 一元函数微分学的计算",
             3516: "# 第8章 一元函数积分学的概念与性质",
             3611: "# 第9章 一元函数积分学的计算",
             4503: "# 第18章 多元函数积分学",
             5474: "# 第5章 多维随机变量函数的分布",
         },
         deletes={5896},  # 题目中间插的假标题
         fixes=[("应��", "应用"), ("伴随��阵", "伴随矩阵")],
         regex_fixes=[]),
    # ============ 解析册 ============
    dict(book="27张宇1000题数一【解析册】", start=167,
         inserts={
             167: "# 基础篇",          # 正文起点插篇标题
             4101: "# 第17章 多元函数积分学的预备知识",
             7155: "# 强化篇",          # 基础篇概率结束→强化篇
             8856: "# 第8章 一元函数积分学的概念与性质",
             10598: "# 第14章 二重积分",
             16961: "# 综合篇",          # 测试卷一前
         },
         deletes={1385, 6658, 10352, 12498, 15450, 15570},  # 假重复标题
         fixes=[("多元函数和分学的预备知识", "多元函数积分学的预备知识")],
         regex_fixes=[
             (r"切线�+\s*y", "切线在 y"),
             (r"矩阵�+故", "矩阵，故"),
             (r"似然�+计", "似然估计"),
             (r"�+边取", "两边取"),
             (r"^�+\s*", ""),   # 行首乱码
             (r"�+", ""),       # 兜底：其余孤立乱码
         ]),
]

DRY = "--apply" not in sys.argv
for j in JOBS:
    d = os.path.join("11408/origin", j["book"])
    md = glob.glob(os.path.join(d, "*.md"))[0]
    out = clean(md, j["start"], j["inserts"], j["deletes"], j["fixes"], j.get("regex_fixes", []))
    if DRY:
        tmp = os.path.join(d, "_clean_tmp.md")
        open(tmp, "w", encoding="utf-8").write(out)
        print(f"{j['book']}: 已输出 {tmp} ({len(out.splitlines())} 行)")
    else:
        open(md, "w", encoding="utf-8").write(out)
        print(f"{j['book']}: 已覆盖 origin ({len(out.splitlines())} 行)")
