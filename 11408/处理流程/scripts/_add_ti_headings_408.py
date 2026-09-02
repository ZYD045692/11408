# -*- coding: utf-8 -*-
"""408四本书 课后习题进大纲（参考30讲数学题目化处理）:
- ### X.Y.Z 本节试题精选/本节习题精选、### X.Y.Z 答案与解析 为扫描区
- #### 一、 单项选择题 / #### 二、 综合应用题 下:
    Q区正文 `NN. 题干` -> `##### NN` + 正文题干
    A区一 正文 `NN. C` -> `##### NN` + 正文答案
    A区二 标题 `#### NN. 【解答】` -> `##### NN` + 正文【解答】
    A区二 正文 `NN. 【解答】` -> 同上(补漏)
- 变体 `#### 单项选择题`(无"一、") -> `#### 一、 单项选择题`
- A区内 `##### （1）...` 子步骤 -> 降为 `###### （1）...`(嵌到所属答案下)
- 顺序期望校验: 编号须从01连续递增, 不符只告警不转换(内容列表不受影响)
用法: python _add_ti_headings_408.py [--apply]"""
import io, sys, re, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

APPLY = "--apply" in sys.argv
BOOKS = ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络"]

for b in BOOKS:
    path = f"11408/origin/{b}/{b}.md"
    lines = open(path, encoding="utf-8").read().split("\n")
    out = []
    sec = sub = None
    seclab = ""
    expect = 1
    in_code = in_math = False
    in_ans = False  # A区已转答案标题之后
    n_q = n_a1 = n_a2 = n_var = n_dem = 0
    warns = []
    for idx, s in enumerate(lines):
        t = s.strip()
        if t.startswith("```"):
            in_code = not in_code
            out.append(s); continue
        if in_code:
            out.append(s); continue
        if s.count("$$") % 2 == 1:
            in_math = not in_math
            out.append(s); continue
        if in_math:
            out.append(s); continue

        m = re.match(r"^### ([\d.]+) (本节试题精选|本节习题精选)", t)
        if m:
            sec, sub, in_ans = "Q", None, False
            seclab = m.group(1) + "试题"
            out.append(s); continue
        m = re.match(r"^### ([\d.]+) 答案与解析", t)
        if m:
            sec, sub, in_ans = "A", None, False
            seclab = m.group(1) + "答案"
            out.append(s); continue
        if re.match(r"^#{1,3} ", t):
            sec = sub = None; in_ans = False
            out.append(s); continue
        if not sec:
            out.append(s); continue

        m = re.match(r"^#### ([一二])、", t)
        if m:
            sub = m.group(1); expect = 1; in_ans = False
            out.append(s); continue
        if re.match(r"^#### 单项选择题\s*$", t):
            sub = "一"; expect = 1; in_ans = False
            out.append(s.replace("#### 单项选择题", "#### 一、 单项选择题"))
            n_var += 1; continue
        m = re.match(r"^#### (\d{1,2})\.\s*(.*)$", t)
        if m and sec == "A":
            num, tail = m.group(1), m.group(2).strip()
            if int(num) != expect:
                warns.append(f"{seclab} L{idx+1}: 答案标题号{num}≠期望{expect}")
            expect = int(num) + 1
            out.append(f"##### {num}")
            if tail:
                out.append(""); out.append(tail)
            n_a2 += 1; in_ans = True; continue
        m = re.match(r"^##### （\d+）", t)
        if m and sec == "A" and in_ans:
            out.append("#" + s.strip())
            n_dem += 1; continue
        m = re.match(r"^##### (\d{1,2})$", t)
        if m and sub:
            expect = int(m.group(1)) + 1  # 已转换标题: 同步期望(幂等重跑)
            in_ans = (sec == "A")
            out.append(s); continue
        m = re.match(r"^(\d{1,2})\s*\\?\.\s*(\S.*)$", t)
        if m and sub:
            num, tail = m.group(1), m.group(2).strip()
            if sec == "A" and sub == "二" and not tail.startswith("【"):
                out.append(s); continue  # 答案二下内容列表,不动
            n = int(num)
            if n < expect:
                # 内容列表/重复号: 不转换, 仅Q区与答案一告警
                if not (sec == "A" and sub == "二"):
                    warns.append(f"{seclab}{sub} L{idx+1}: 编号{num}<期望{expect} 跳过 | {t[:40]}")
                out.append(s); continue
            if n > expect:
                warns.append(f"{seclab}{sub} L{idx+1}: 缺号{expect}~{n-1} | {t[:40]}")
            out.append(f"##### {num}")
            if tail:
                out.append(""); out.append(tail)
            expect = n + 1
            if sec == "Q": n_q += 1
            elif sub == "一": n_a1 += 1
            else: n_a2 += 1
            in_ans = (sec == "A")
            continue
        out.append(s)

    print(f"=== {b} ===  题转标题 {n_q} | 答一 {n_a1} | 答二 {n_a2} | 小节变体 {n_var} | 子步骤降级 {n_dem}")
    for w in warns[:15]:
        print(f"  ⚠ {w}")
    if len(warns) > 15:
        print(f"  ⚠ ...共{len(warns)}条")
    if APPLY:
        shutil.copy(path, f"_backup_round2/{b}_before_ti408.md")
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))
        print("  已写盘")
