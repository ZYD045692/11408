# -*- coding: utf-8 -*-
"""30讲数学 题目编号连续性交叉验证（转换后必跑）。
每讲检查: 例/习题/解答 编号各自连续(1..max无缺无重无乱序) + 题号集=答号集。
用法: python _check_ti_continuity.py <origin_md>"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = sys.argv[1]
lines = open(path, encoding="utf-8").read().split("\n")
lec = None; sec = None
in_code = in_math = False
data = {}
for s in lines:
    t = s.strip()
    if t.startswith("```"): in_code = not in_code; continue
    if in_code: continue
    if s.count("$$") % 2 == 1: in_math = not in_math; continue
    if in_math: continue
    m = re.match(r"^## 第(\d+)讲", s)
    if m:
        lec = int(m.group(1)); data[lec] = {"例": [], "题": [], "答": []}; sec = None; continue
    if s.startswith("### 基础内容精讲"): sec = "精讲"; continue
    if s.startswith("#### 习题"): sec = "习题"; continue
    if s.startswith("#### 解答"): sec = "解答"; continue
    if s.startswith("## ") or s.startswith("### "): sec = None
    m = re.match(r"^#{4,6} [★☆]*\s*例(\d+)\.(\d+)$", s)
    if m and sec == "精讲" and lec:
        data[lec]["例"].append(int(m.group(2))); continue
    m = re.match(r"^#{4,6} (\d+)\.(\d+)$", s)
    if m and sec in ("习题", "解答") and lec:
        data[lec]["题" if sec == "习题" else "答"].append(int(m.group(2)))

bad = 0
for lec in sorted(data):
    d = data[lec]
    issues = []
    for key in ("例", "题", "答"):
        nums = d[key]
        if not nums: issues.append(f"{key}=空"); continue
        if nums != sorted(nums): issues.append(f"{key}乱序")
        if len(nums) != len(set(nums)): issues.append(f"{key}重复")
        if nums != list(range(1, max(nums) + 1)):
            issues.append(f"{key}缺{sorted(set(range(1, max(nums) + 1)) - set(nums))[:8]}")
    if d["题"] != d["答"]:
        issues.append(f"题答不对称: 题多{sorted(set(d['题'])-set(d['答']))} 答多{sorted(set(d['答'])-set(d['题']))}")
    if issues: bad += 1
    print(f"第{lec:2d}讲: 例{len(d['例']):3d} 题{len(d['题']):3d} 答{len(d['答']):3d}  {' | '.join(issues) if issues else '✓'}")
print(f"\n{'⚠ ' + str(bad) + ' 讲有问题' if bad else '✅ 全部讲: 编号连续、无缺、题答对称'}")
sys.exit(1 if bad else 0)
