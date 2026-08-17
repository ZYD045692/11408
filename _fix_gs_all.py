# -*- coding: utf-8 -*-
"""高数 origin 全面修复：
1. 删除重复的 ## 第1讲（第二处）
2. 结构化讲中：#### N 子项 → #####（当父节为 #### 一/二/三时）
3. 结构化讲中：#### 例N.N/定理 N → #####
4. 第5讲 补 一/二 节标题、修复凹凸性子项层级
5. 第10讲 补 1 平面图形的面积
6. 第15讲 齐次/非齐次层级统一
"""
import io, sys, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = glob.glob("11408/origin/*高数*/*.md")[0]
print("文件:", F)

raw = open(F, "rb").read().decode("utf-8")
raw = raw.replace("\r\n", "\n")
lines = raw.split("\n")

# ========= 1. 删除重复的 ## 第1讲（第二处 L3115） =========
# 第一次出现 L0 已正确
dup1_idx = None
cnt = 0
for i, l in enumerate(lines):
    if l.startswith("## 第1讲"):
        cnt += 1
        if cnt == 2:
            dup1_idx = i
            break
if dup1_idx:
    # 删除这一行
    lines[dup1_idx] = None
    print(f"1. 删除重复第1讲 L{dup1_idx+1}")

# ========= 2. 结构化讲中：#### N / #### 例N / #### 定理 N → ##### =========
# 识别结构化讲：讲内包含 #### 一/二/三（至少2个）
STRUCTURED = {}
current_lecture = None
for i, l in enumerate(lines):
    if l is None: continue
    m = re.match(r"^## 第(\d+)讲", l)
    if m:
        current_lecture = int(m.group(1))
    if current_lecture and re.match(r"^#### [一二三四五六七八九十]", l):
        STRUCTURED.setdefault(current_lecture, set()).add(l[:6])

# 需要子项降级的讲（含 #### 一/二 及以上）
demote_lectures = {k for k, v in STRUCTURED.items() if len(v) >= 2}
print(f"2. 结构化讲（需子项降级）: {sorted(demote_lectures)}")

# 处理需要降级的讲
for i, l in enumerate(lines):
    if l is None: continue
    m = re.match(r"(^####\s+)(\d+)(\s.*)$", l)
    if not m:
        m = re.match(r"(^####\s+)(例[\d.]+)(.*)$", l)
    if not m:
        m = re.match(r"(^####\s+)(定理\s*\d+)(.*)$", l)
    if m:
        # 判断当前讲是否属于降级范围
        # 需要知道前面的 ## 第N讲
        lecture_no = None
        for j in range(i, -1, -1):
            if lines[j] is None: continue
            lm = re.match(r"^## 第(\d+)讲", lines[j] if lines[j] else "")
            if lm:
                lecture_no = int(lm.group(1))
                break
        if lecture_no in demote_lectures:
            lines[i] = f"#####{m.group(2)}{m.group(3)}"
print("   子项降级完成")

# ========= 3. 第5讲 补 一 极值与单调性、二 凹凸性与拐点 =========
# 插入 #### 一 极值与单调性 在 #### 1 极值的定义 之前
for i, l in enumerate(lines):
    if l is None: continue
    if l == "#### 1 极值的定义":
        # 检查前面是否有 #### 一，没有则插入
        has_yi = False
        for j in range(i-1, max(0, i-50), -1):
            if lines[j] and lines[j].startswith("#### 一"):
                has_yi = True
                break
            if lines[j] and lines[j].startswith("## 第"):
                break
        if not has_yi:
            lines[i] = None  # 标记删除位置
            # 在 i 位置插入新行
            lines[i] = "#### 一 极值与单调性"
            # 原 1 极值的定义 放到下一行
            insert_after = i
    break

# 找 #### 凹凸性与拐点的概念 → 改为 #### 二 凹凸性与拐点
for i, l in enumerate(lines):
    if l is None: continue
    if l == "#### 凹凸性与拐点的概念":
        lines[i] = "#### 二 凹凸性与拐点"
        print(f"3. 第5讲: 凹凸性与拐点 → #### 二")
        break

# #### 凹凸性定义(1/2/3) 和 ### 拐点判别(1/2/3/4/5) 在 二 下应降为 #####
# 这些在 demote_lectures 中已处理（第5讲在demote_lectures中）

# ========= 4. 第10讲 补 1 平面图形的面积 =========
# 在 #### 2 用定积分表达和计算旋转体的体积 前插入 1
for i, l in enumerate(lines):
    if l is None: continue
    if l == "#### 2 用定积分表达和计算旋转体的体积":
        has_one = False
        for j in range(i-1, max(0, i-50), -1):
            if lines[j] and lines[j].startswith("#### 1"):
                has_one = True
                break
            if lines[j] and (lines[j].startswith("## 第") or lines[j].startswith("### 基础")):
                break
        if not has_one:
            lines.insert(i, "#### 1 平面图形的面积")
            print(f"4. 第10讲: 补 #### 1 平面图形的面积")
        break

# ========= 5. 第15讲 齐次/非齐次层级统一 =========
# 当前: #### 1 二阶常系数齐次线性微分方程 → 改为 #####
#        ##### 2 二阶常系数非齐次线性微分方程 → 保持
# 但齐次现在可能已经降级（第15讲在demote_lectures中）
# 需要确保 #1. 二阶常系数齐次 也是 #####
for i, l in enumerate(lines):
    if l is None: continue
    m = re.match(r"^####\s+(\d)\s+二阶常系数", l)
    if m:
        lines[i] = f"##### {m.group(1)} 二阶常系数" + l.split("二阶常系数")[1] if "二阶常系数" in l else l
        print(f"5. 第15讲: 齐次/非齐次降为 #####")
        break

# ========= 清理 None 行（删除标记） =========
lines = [l for l in lines if l is not None]

# 写回
result = "\n".join(lines)
open(F, "w", encoding="utf-8").write(result)
print("完成")