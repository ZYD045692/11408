# -*- coding: utf-8 -*-
"""解析册 origin：基础篇/强化篇内插入 ## 高数/线代/概率论 并行的科目标题，章节降为 ###。
综合篇（测试卷）不动。科目判定复用拆分脚本关键词表。
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
lines = open(F, encoding="utf-8").read().split("\n")

XIANDAI = ["行列式", "余子式", "矩阵", "向量组", "线性方程组", "特征值", "相似", "二次型"]
GAILV = ["随机事件", "随机变量", "数字特征", "大数定律", "数理统计", "统计量", "参数估计"]
SUBJ_NAME = {"高数": "高数", "线代": "线代", "概率": "概率论"}

def subject_of(title):
    if any(k in title for k in GAILV):
        return "概率"
    if any(k in title for k in XIANDAI):
        return "线代"
    return "高数"

out = []
cur_pian = None
cur_subj = None
inserted = 0
demoted = 0

for raw in lines:
    s = raw.strip()
    m = re.match(r"^# (基础篇|强化篇|综合篇)\s*$", s)
    if m:
        cur_pian = m.group(1)
        cur_subj = None
        out.append(raw)
        continue
    if cur_pian in ("基础篇", "强化篇"):
        mz = re.match(r"^## 第(\d+)章\s+(.+)$", s)
        ml = re.match(r"^## 零\s*基础.*$", s)
        if mz or ml:
            title = mz.group(2).strip() if mz else "零 基础"
            subj = subject_of(title)
            if subj != cur_subj:
                if out and out[-1].strip() != "":
                    out.append("")
                out.append("## " + SUBJ_NAME[subj])
                out.append("")
                cur_subj = subj
                inserted += 1
            out.append("### " + s.lstrip("#").strip())
            demoted += 1
            continue
    out.append(raw)

open(F, "w", encoding="utf-8").write("\n".join(out))
print("插入科目标题:", inserted)
print("降级章节:", demoted)
