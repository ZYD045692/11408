# -*- coding: utf-8 -*-
"""把高数讲名统一移到 ## 第N讲 同一行（处理 \r\n 行尾）"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
raw = open(F, "rb").read().decode("utf-8")
raw = raw.replace("\r\n", "\n")
lines = raw.split("\n")

LECTURE_NAMES = {
    1:"函数极限与连续", 2:"数列极限", 3:"一元函数微分学的概念",
    4:"一元函数微分学的计算", 5:"一元函数微分学的应用（一）——几何应用",
    6:"一元函数微分学的应用（二）——中值定理、微分等式与微分不等式",
    7:"一元函数微分学的应用（三）——物理应用与经济应用",
    8:"一元函数积分学的概念与性质", 9:"一元函数积分学的计算",
    10:"一元函数积分学的应用（一） ——几何应用",
    11:"一元函数积分学的应用（二）——积分等式与积分不等式",
    12:"一元函数积分学的应用（三）——物理应用与经济应用",
    13:"多元函数微分学", 14:"二重积分", 15:"微分方程",
    16:"无穷级数（仅数学一、数学三）",
    17:"多元函数积分学的预备知识（仅数学一）",
    18:"多元函数积分学（仅数学一）",
}

out = []
fixed = 0
skip_count = 0

for i, line in enumerate(lines):
    if skip_count > 0:
        skip_count -= 1
        continue

    m = re.match(r"^## 第(\d+)讲\s*(.*)$", line)
    if m:
        no = int(m.group(1))
        name = m.group(2).strip()
        expected = LECTURE_NAMES.get(no)

        if not name and expected:
            # 往后跳过空行/div/table/| 找讲名
            j = i + 1
            name_parts = []
            while j < len(lines):
                s = lines[j].strip()
                if s == "":
                    j += 1
                    continue
                if s.startswith("<") or s.startswith("|") or s.startswith("###"):
                    break
                name_parts.append(s)
                j += 1
            full = "".join(name_parts)
            if full and full == expected:
                out.append(f"## 第{no}讲 {expected}")
                skip_count = j - i - 1
                fixed += 1
                continue

        if name and expected and name != expected and no != 4:
            out.append(f"## 第{no}讲 {expected}")
            fixed += 1
            continue

    out.append(line)

result = "\n".join(out)
open(F, "w", encoding="utf-8").write(result)
print(f"已将 {fixed} 讲讲名合并到 ## 同一行")