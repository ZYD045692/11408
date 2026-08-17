# -*- coding: utf-8 -*-
"""408四本书 课后习题编号连续性交叉验证（题目化转换后必跑）。
每个 试题精选/答案与解析 节、每个题型小节(一/二)检查: ##### NN 序列从01连续无缺无重。
并配对 试题节X.Y.Z 与 答案节X.Y.(Z+1) 检查题答对称。
用法: python _check_ti_continuity_408.py"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BOOKS = ["2027数据结构", "2027操作系统", "2027计算机组成原理", "2027计算机网络"]

for b in BOOKS:
    f = f"11408/origin/{b}/{b}.md"
    lines = open(f, encoding="utf-8").read().split("\n")
    sec = sub = None
    cur = ""
    data = {}  # (prefix, 'Q'/'A', sub) -> [nums]
    in_code = in_math = False
    for s in lines:
        t = s.strip()
        if t.startswith("```"): in_code = not in_code; continue
        if in_code: continue
        if s.count("$$") % 2 == 1: in_math = not in_math; continue
        if in_math: continue
        m = re.match(r"^### ([\d.]+) (本节试题精选|本节习题精选)", t)
        if m:
            sec, sub = "Q", None
            cur = m.group(1).rsplit(".", 1)[0]
            continue
        m = re.match(r"^### [\d.]+ 答案与解析", t)
        if m:
            sec, sub = "A", None
            continue
        if re.match(r"^#{1,3} ", t): sec = sub = None
        if not sec: continue
        m = re.match(r"^#### ([一二])、", t)
        if m: sub = m.group(1); continue
        m = re.match(r"^##### (\d{1,2})$", t)
        if m and sub:
            data.setdefault((cur, sec, sub), []).append(int(m.group(1)))

    bad = 0
    for (cur, sec, sub), nums in sorted(data.items()):
        exp = list(range(1, max(nums) + 1)) if nums else []
        miss = sorted(set(exp) - set(nums))
        dup = sorted({n for n in nums if nums.count(n) > 1})
        if miss or dup:
            bad += 1
            print(f"{b} {cur} {sec}{sub}: 缺{miss} 重{dup}")
    # 题答对称
    for (cur, sec, sub), nums in sorted(data.items()):
        if sec != "Q": continue
        ans = data.get((cur, "A", sub))
        if ans is None:
            bad += 1
            print(f"{b} {cur} Q{sub}: 无对应答案小节")
            continue
        if sorted(nums) != sorted(ans):
            bad += 1
            only_q = sorted(set(nums) - set(ans))
            only_a = sorted(set(ans) - set(nums))
            print(f"{b} {cur} {sub}: 题多{only_q} 答多{only_a}")
    print(f"=== {b}: {'⚠ ' + str(bad) + ' 处' if bad else '✅ 全连续、题答对称'} ===\n")
