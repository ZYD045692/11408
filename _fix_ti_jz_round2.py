# -*- coding: utf-8 -*-
"""计组 课后习题题目化收尾修复（连续性交叉验证发现的15处缺口，合并为12项修复）:
孤儿```c围栏×4(2.1Q05/06、2.2Q35、4.3Q09、5.6Q05)、全角点×1(2.2Q21)、
OCR错字×2(Q20 [x]≠44H→[x]补=44H、5.6Q11 II.→11.)、丢题干首行×1(2.3Q25,PDF p75补)、
丢答案行×2(3.3A12补12.D+解析,PDF p113;5.7A05拆出05.B,PDF p283)、
粘连拆行×1(5.2A03)、div包裹×1(5.3Q09)、错号×1(5.4Q16 OCR成10,PDF p248)、
书本印刷错位×1(4.3A二07→09,PDF p202确认题09答07为原书错印)。
内容锚定+断言。一次性,可删。"""
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = "11408/origin/2027计算机组成原理/2027计算机组成原理.md"
shutil.copy(path, "_backup_round2/计算机组成原理_before_tifix408.md")
lines = open(path, encoding="utf-8").read().split("\n")

def find(anchor, start=0):
    hits = [i for i in range(start, len(lines)) if anchor in lines[i]]
    assert hits, f"锚点找不到: {anchor[:40]!r}"
    return hits[0]

def rm_fence(anchor, above=1):
    """删除 anchor 行上方 above 行的 ```c 与其下方最近的 ``` 这一对孤儿围栏"""
    i = find(anchor)
    j = i - above
    while not lines[j].strip().startswith("```"):
        j -= 1
        assert i - j <= 6, f"围栏上沿太远: {anchor[:30]!r}"
    assert lines[j].strip() == "```c", f"上沿不是```c: L{j+1} {lines[j]!r}"
    k = i + 1
    while lines[k].strip() == "":
        k += 1
    assert lines[k].strip() == "```", f"下沿不是```: L{k+1} {lines[k]!r}"
    del lines[k]
    del lines[j]
    print(f"OK L{j+1}/L{k+1}: 拆孤儿```c围栏 | {anchor[:30]}")

# 1. 2.1 Q05/Q06: 两对孤儿```c围栏(包裹题干行,阻断转换)
rm_fence("05. 若 [X]_{\\text{补}} = 1.1101010")
rm_fence("06. 若 X 为负数，则由")

# 2. 2.2 Q21 全角点 + Q20 OCR错字([x]≠44H 应为 [x]补=44H,与Q21行对照)
i = find("21．某8位计算机中，x和y是两个有符号整数")
lines[i] = lines[i].replace("21．", "21. ", 1)
print(f"OK L{i+1}: 21．-> 21.")
i = find("[x]≠44H，[y]≠DCH")
lines[i] = lines[i].replace("[x]≠44H，[y]≠DCH", "[x]补=44H，[y]补=DCH", 1)
print(f"OK L{i+1}: [x]≠44H -> [x]补=44H")

# 3. 2.2 Q35: 孤儿```c围栏
rm_fence("35. 【2025 统考真题】假设在 8 位字长的计算机中")

# 4. 2.3 Q25: 丢题干首行(PDF p75/书p63: "25. 有以下 C 语言代码段：")
i = find("int m=13;")
assert lines[i].strip() == "int m=13;"
lines[i:i] = ["25. 有以下 C 语言代码段：", ""]
print(f"OK L{i+1}前: 插入 25. 题干首行")

# 5. 3.3 A12: 补 12. D + 解析(PDF p113/书p101)
i = find("### 3.3.4 答案与解析")
i = find("##### 13", i)
lines[i:i] = [
    "12. D", "",
    "主存按字节编址，地址空间大小为 64MB，MAR 的寻址范围为 $64M = 2^{26}$，因此是 26 位。实际的主存容量 32MB 不能代表 MAR 的位数，考虑到存储器扩展的需要，MAR 应保证能访问到整个主存地址空间，反过来，MAR 的位数决定了主存地址空间的大小。",
    "",
]
print(f"OK L{i+1}前: 插入 12. D + 解析")

# 6. 4.3 Q09: 孤儿```c围栏
rm_fence("09. 下列关于选择结构语句")

# 7. 4.3 A二: ##### 07 -> ##### 09(原书错印:题09答07,PDF p202确认)
i = find("### 4.3.6 答案与解析")
i = find("#### 二、 综合应用题", i)
i = find("##### 07", i)
assert lines[i].strip() == "##### 07"
lines[i] = "##### 09"
print(f"OK L{i+1}: A二 ##### 07 -> ##### 09(原书错印改号)")

# 8. 5.2 A03: 粘连拆行
i = find("间址周期不是必需的。03\\. B")
lines[i:i+1] = [
    "指令周期是指 CPU 从主存取出一条指令加上执行这条指令的时间，间址周期不是必需的。",
    "", "03. B",
]
print(f"OK L{i+1}: 拆出 03. B")

# 9. 5.3 Q09: 去div包裹
i = find('<div style="text-align: center;">09. 【2015 统考真题】上题中描述的计算机')
assert lines[i].strip().startswith("<div") and lines[i].strip().endswith("</div>")
s = lines[i].strip()
lines[i] = s[len('<div style="text-align: center;">'):-len("</div>")]
print(f"OK L{i+1}: 去div 09.")

# 10. 5.4 Q16: OCR错号 10->16(PDF p248确认题16="下列说法中，正确的是()")
i = find("10. 下列说法中，正确的是（）。")
assert lines[i].strip() == "10. 下列说法中，正确的是（）。"
lines[i] = "16. 下列说法中，正确的是（）。"
print(f"OK L{i+1}: 10. -> 16.")

# 11. 5.6 Q05: 孤儿```c围栏; Q11: OCR II.->11.
rm_fence("05. 设指令流水线把一条指令分为取指、分析、执行3部分")
i = find("II. 下列关于数据冒险和转发技术的叙述中，正确的是（）。")
assert lines[i].strip().startswith("II. ")
lines[i] = lines[i].replace("II. ", "11. ", 1)
print(f"OK L{i+1}: II. -> 11.")

# 12. 5.7 A05: 04解析第二段即05的解析,拆出 05. B(PDF p283); 04句首补"A、"(OCR丢字,书为"A、B 和 C")
i = find("B 和 C 通常可理解为同一种概念，是 SIMD 结构")
assert lines[i].strip().startswith("B 和 C")
lines[i] = lines[i].replace("B 和 C 通常可理解为", "A、B 和 C 通常可理解为", 1)
print(f"OK L{i+1}: 补字 A、B 和 C")
i = find("单指令流多数据流（SIMD）结构的计算机通常由一个指令控制部件")
assert lines[i-1].strip() == ""
lines[i-1:i] = ["##### 05", "", "B", ""]
print(f"OK L{i}处: 拆出 ##### 05 + B")

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("\n计组 12项修复写盘完成")
