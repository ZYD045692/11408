# -*- coding: utf-8 -*-
"""修复高数 origin 讲标题：统一为 ## 第N讲 讲名"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = glob.glob("11408/origin/*高数*/*.md")[0]
print("文件:", F)

raw = open(F, "rb").read().decode("utf-8")
raw = raw.replace("\r\n", "\n")
lines = raw.split("\n")

NAMES = {
    1:"函数极限与连续", 2:"数列极限", 3:"一元函数微分学的概念",
    5:"一元函数微分学的应用（一）——几何应用",
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
# 第4讲已正确，跳过

out = []
fixed = 0
skip = 0

for i, line in enumerate(lines):
    if skip > 0:
        skip -= 1
        continue

    # 匹配两种格式：## 第N讲 或 第N讲（已丢失##）
    m = re.match(r"^(?:## )?第(\d+)讲\s*(.*)$", line)
    if m:
        no = int(m.group(1))
        has_name = m.group(2).strip()
        expected = NAMES.get(no)

        if no == 4:
            # 已验证正确
            out.append(line)
            continue

        if expected:
            # 需要加##
            if not line.startswith("## "):
                # 丢失了##，需恢复
                out.append(f"## 第{no}讲 {expected}")
                fixed += 1
                continue
            elif not has_name:
                # 有##但无讲名，去后续行提取
                j = i + 1
                parts = []
                while j < len(lines):
                    s = lines[j].strip()
                    if not s:
                        j += 1; continue
                    if s.startswith("<") or s.startswith("|") or s.startswith("###"):
                        break
                    parts.append(s)
                    j += 1
                got = "".join(parts)
                if got == expected:
                    out.append(f"## 第{no}讲 {expected}")
                    skip = j - i - 1
                    fixed += 1
                    continue

    out.append(line)

result = "\n".join(out)
open(F, "w", encoding="utf-8").write(result)
print(f"已修复 {fixed} 讲讲标题")