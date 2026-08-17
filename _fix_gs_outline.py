# -*- coding: utf-8 -*-
"""高数 origin 大纲结构修复：例题去#、补/改节标题、拆标题混行、OCR错字符（一次性，可删）"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
path = "11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md"
lines = open(path, encoding="utf-8").read().split("\n")

def find_in(lec, pattern):
    """在第N讲范围内找唯一精确匹配行(0-based)"""
    start = next(i for i, l in enumerate(lines) if l.strip().startswith(f"## 第{lec}讲"))
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^## 第\d+讲", lines[i])), len(lines))
    hits = [i for i in range(start, end) if lines[i].strip() == pattern]
    assert len(hits) == 1, f"第{lec}讲 '{pattern}' 匹配 {len(hits)} 处: {[h+1 for h in hits]}"
    return hits[0]

n = 0
def sub(lec, old, new):
    global n
    i = find_in(lec, old)
    assert old in lines[i]
    lines[i] = lines[i].replace(old, new, 1)
    n += 1
    print(f"OK L{i+1} [{old[:40]}] -> [{new[:40]}]")

# 1. 例题去 #（变正文）
sub(2,  r"#### 例2.3 证明数列  $\left\{n^{(-1)^n}\right\}$ 极限不存在",
        r"例2.3 证明数列  $\left\{n^{(-1)^n}\right\}$ 极限不存在")
sub(4,  r"#### 例4.6 设函数  $y = |xe^{-x}|$，求  $y''$。",
        r"例4.6 设函数  $y = |xe^{-x}|$，求  $y''$。")
sub(12, "#### 例 12.1 用铁锤将一铁钉击入木板，设木板对铁钉的阻力与铁钉",
        "例 12.1 用铁锤将一铁钉击入木板，设木板对铁钉的阻力与铁钉")

# 2. 第5讲 重建节结构（按原书结构图）
sub(5, "##### 1 极值的定义", "#### 一 极值的定义")
sub(5, "##### 2 单调性与极值的判别", "#### 二 单调性与极值的判别")
sub(5, "#### 单调性的判别", "##### 1 单调性的判别")
sub(5, "#### 二 凹凸性与拐点", "#### 三 凹凸性与拐点的概念")
sub(5, "##### 3 判别凹凸性", "##### 1 判别凹凸性")
# 节四：正文行拆成 标题 + 注释段
i = find_in(5, "四凹凸性与拐点的判别——→与极值点的判别结合记忆")
lines[i] = "#### 四 凹凸性与拐点的判别\n\n——→与极值点的判别结合记忆"
n += 1
print(f"OK L{i+1} 拆行: #### 四 凹凸性与拐点的判别 + 注释段")
# 节六：渐近线引导语前插入节标题
i = find_in(5, "——→当曲线上的点远离原点时，曲线与某直线充分靠近，则称该直线为曲线的渐近线。")
lines[i] = "#### 六 渐近线\n\n" + lines[i].strip()
n += 1
print(f"OK L{i+1} 插入: #### 六 渐近线")

# 3. 第13讲 补「一 基本概念」
i = find_in(13, "##### 1 邻域")
lines[i] = "#### 一 基本概念\n\n" + lines[i].strip()
n += 1
print(f"OK L{i+1} 插入: #### 一 基本概念")

# 4. 第14讲 补「1 概念」
i = find_in(14, "#### 一 概念、性质与对称性")
lines[i] = lines[i].strip() + "\n\n##### 1 概念"
n += 1
print(f"OK L{i+1} 插入: ##### 1 概念")

# 5. 第16讲
# 2 求法：标题混行拆分
i = find_in(16, "2 求法 → 缺点：计算量大，比较麻烦，一般不用这种方法。优点：让我们直观感受具体展开式怎么来的。")
lines[i] = "##### 2 求法\n\n→ 缺点：计算量大，比较麻烦，一般不用这种方法。优点：让我们直观感受具体展开式怎么来的。"
n += 1
print(f"OK L{i+1} 拆行: ##### 2 求法 + 注释段")
# 六 傅里叶级数：正文行→节标题
sub(16, "六傅里叶级数（仅数学一）", "#### 六 傅里叶级数（仅数学一）")
# 周期为2l：正文行→子项标题，修 OCR 2/→2l
sub(16, "周期为2/的傅里叶级数", "##### 1 周期为 $2l$ 的傅里叶级数")
# [0,7]→[0,l]
sub(16, "##### 4 只在  $[0,7]$ 上有定义的函数的正弦级数和余弦级数展开",
        "##### 4 只在  $[0,l]$ 上有定义的函数的正弦级数和余弦级数展开")

open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print(f"\n共 {n} 处修复")
