# -*- coding: utf-8 -*-
"""操作系统 课后习题题目化收尾修复（连续性交叉验证发现的9处）:
粘连拆行×3、全角点×2、OCR错字×2(31R→31.B经PDF p37、II.→11.)、
丢答案行×2(2.1答03、2.4答45,经PDF p70/p184补)、4.2答案13-16区错位重建。
内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/2027操作系统/2027操作系统.md"
shutil.copy(path, "_backup_round2/操作系统_before_tifix408.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(anchor, start=0):
    hits = [i for i in range(start, len(lines)) if anchor in lines[i]]
    assert hits, f"锚点找不到: {anchor[:40]!r}"
    return hits[0]

# 1. 1.3 A31: OCR R->B (PDF p37 确认 31. B)
i = find("发生系统调用时，CPU 通过执行软中断指令将 CPU 的运行状态从用户态切换到内核态")
j = next(k for k in range(i, i-4, -1) if lines[k].strip() == "31 R")
lines[j] = "31. B"
print(f"OK L{j+1}: 31 R -> 31. B")

# 2. 2.1 A缺3: 补 03. A (PDF p70 确认)
i = find("动态性是进程最重要的特性，以此来区分文件形式的静态程序")
lines[i:i] = ["03. A", ""]
print(f"OK L{i+1}前: 插入 03. A")

# 3. 2.4 Q31: 全角点
i = find("31．下列各种方法中，可用于解除已发生死锁的是")
lines[i] = lines[i].replace("31．", "31. ", 1)
print(f"OK L{i+1}: 31．-> 31.")

# 4. 2.4 A缺45: OCR R->B (PDF p184 确认 45. B, 解析完好)
i = find("45 R")
assert lines[i].strip() == "45 R"
lines[i] = "45. B"
print(f"OK L{i+1}: 45 R -> 45. B")

# 5. 3.1 Q11: OCR II.->11.
i = find("II. 动态重定位的过程依赖于（）。")
assert lines[i].strip() == "II. 动态重定位的过程依赖于（）。"
lines[i] = "11. 动态重定位的过程依赖于（）。"
print(f"OK L{i+1}: II. -> 11.")

# 6. 4.2 答案13-16区重建 (PDF p294 确认 13C/14A/15A/16B 及各自解析)
i13 = find("### 4.2.12 答案与解析")
i13 = find("##### 13", i13)
i17 = find("##### 17", i13)
region = lines[i13:i17]
def grab(prefix):
    hit = [l for l in region if l.strip().startswith(prefix)]
    assert len(hit) == 1, f"区域行不唯一: {prefix} -> {hit}"
    return hit[0].strip()
t_duo  = grab("在文件系统中采用多级目录结构后")
t_dan  = grab("在单级目录文件中，每当新建一个文件时")
t_ci   = grab("磁带是一种顺序存")
t_lian = grab("采用连续分配和索引分配的文件都支持随机存取")
lines[i13:i17] = [
    "##### 13", "", "C", "", t_duo, "",
    "##### 14", "", "A", "", t_dan, "",
    "##### 15", "", "A", "", t_ci, "",
    "##### 16", "", "B", "", t_lian, "",
]
print(f"OK L{i13+1}~L{i17+1}: 4.2答案13-16区重建")

# 7. 5.2 A缺2: 粘连拆行
i = find("即使用户程序和实际使用的物理设备无关。02\\. C")
lines[i:i+1] = ["设备的独立性主要是指用户使用设备的透明性，即使用户程序和实际使用的物理设备无关。", "", "02. C"]
print(f"OK L{i+1}: 拆出 02. C")

# 8. 5.2 Q缺10/11: 粘连拆行
i = find("$70\\mu s$10. 某操作系统采用双缓冲区")
s = lines[i]
pre, post = s.split("$10. ", 1)
lines[i:i+1] = [pre + "$", "", "10. " + post]
print(f"OK L{i+1}: 拆出 10.")
i = find("T_{2}+T_{3})$11. 若 I/O 所花费的时间比 CPU 的处理时间短得多")
s = lines[i]
pre, post = s.split("$11. ", 1)
lines[i:i+1] = [pre + "$", "", "11. " + post]
print(f"OK L{i+1}: 拆出 11.")

# 9. 5.2 Q31: 全角点
i = find("31．下列设备管理工作中，适合由设备独立性软件来完成的有")
lines[i] = lines[i].replace("31．", "31. ", 1)
print(f"OK L{i+1}: 31．-> 31.")

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n操作系统 9处修复写盘完成")
