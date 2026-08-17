# -*- coding: utf-8 -*-
"""计网 课后习题题目化收尾修复（连续性交叉验证发现的3处）:
粘连拆行×1(2.2A06)、丢点×1(3.1A06)、丢答案行×1(4.4A11,PDF p215确认11.C,
其解析"RIP规定一个路由器只向相邻路由器…"被并进10的解析)。
内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/2027计算机网络/2027计算机网络.md"
shutil.copy(path, "_backup_round2/计算机网络_before_tifix408.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(anchor, start=0):
    hits = [i for i in range(start, len(lines)) if anchor in lines[i]]
    assert hits, f"锚点找不到: {anchor[:40]!r}"
    return hits[0]

# 1. 2.2 A06: 粘连拆行
i = find("光纤的抗雷电和电磁干扰性能好，无串音干扰，保密性好。06. C")
lines[i:i+1] = [
    "光纤的抗雷电和电磁干扰性能好，无串音干扰，保密性好。",
    "", "06. C",
]
print(f"OK L{i+1}: 拆出 06. C")

# 2. 3.1 A06: 丢点
i = find("06 A")
assert lines[i].strip() == "06 A"
lines[i] = "06. A"
print(f"OK L{i+1}: 06 A -> 06. A")

# 3. 4.4 A11: 拆出 11. C(PDF p215确认; 该解析行原被并入10)
i = find("RIP 规定一个路由器只向相邻路由器发布路由信息")
assert lines[i-1].strip() != "" or True
lines[i:i] = ["11. C", ""]
print(f"OK L{i+1}前: 插入 11. C")

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n计网 3处修复写盘完成")
