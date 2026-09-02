# -*- coding: utf-8 -*-
"""2026-08-17 第二轮：2027操作系统 标题级残留修复。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/2027操作系统/2027操作系统.md"
lines = open(F, encoding="utf-8").read().split("\n")
log, skip = [], []

def set_line(ln, new, expect=None):
    cur = lines[ln - 1]
    if expect is not None and cur.strip() != expect.strip():
        skip.append((ln, cur[:60], "期望[%s]" % expect[:40]))
        return
    lines[ln - 1] = new
    log.append((ln, cur[:48], new[:48]))

# ---------- A1. 考点追踪裸行 → H3（pattern：非标题的"考点追踪"开头行） ----------
n_kz = 0
for i, l in enumerate(lines, 1):
    if l.startswith("考点追踪") and not l.startswith("#"):
        new = "### " + re.sub(r"^考点追踪\s*", "考点追踪 ", l)
        set_line(i, new, l)
        n_kz += 1
print("考点追踪裸行提升 %d" % n_kz)

# ---------- A2. $$考点追踪...$$ → H3 ----------
BB = {
    3550: ("$$考点追踪 \\quad\\rightarrow 作业执行的相关计算 (2012、2016、2018、2019、2023、2024)$$",
           "### 考点追踪 作业执行的相关计算（2012、2016、2018、2019、2023、2024）"),
    15322: ("$$考点追踪 \\quad\\rightarrow I/O 子系统各层次的功能及分析（2011、2012、2013）$$",
            "### 考点追踪 I/O 子系统各层次的功能及分析（2011、2012、2013）"),
    17071: ("$$\\text{考点追踪 }\\rhd\\rhd SSTF 算法的应用 (2019、2021)$$",
            "### 考点追踪 SSTF 算法的应用（2019、2021）"),
    17102: ("$$\\text{考点追踪}\\rightarrow C-SCAN\\  算法的应用（2024）$$",
            "### 考点追踪 C-SCAN 算法的应用（2024）"),
}
for ln, (old, new) in BB.items():
    set_line(ln, new, old)

# ---------- A3. 考点追踪 粘连补空格 + OCR 多→多类 ----------
SP = [833, 858, 2027, 7924, 9486, 9528, 10924]
for ln in SP:
    cur = lines[ln - 1]
    if cur.startswith("### 考点追踪") and not cur.startswith("### 考点追踪 "):
        set_line(ln, cur.replace("### 考点追踪", "### 考点追踪 ", 1), cur)
# L8110 含"多"→"多类"
cur = lines[8110 - 1]
if "多在资源竞争" in cur:
    set_line(8110, cur.replace("多在资源竞争", "多类资源竞争").replace("### 考点追踪", "### 考点追踪 ", 1), cur)
else:
    skip.append((8110, cur[:60], "未含'多在资源竞争'"))

# ---------- B. OCR DNA→DMA ----------
cur = lines[15299 - 1]
if "DNA 方式" in cur:
    set_line(15299, cur.replace("DNA 方式", "DMA 方式"), cur)
else:
    skip.append((15299, cur[:60], "未含'DNA 方式'"))

# ---------- C. 编号格式 $^{*}N$/$^{4}$ → 普通编号 ----------
NF = {
    12993: "#### 1. 单级目录结构",
    13010: "#### 2. 两级目录结构",
    13047: "#### 4. 无环图目录结构",
    15306: "#### 4. 通道控制方式",
}
for ln, new in NF.items():
    set_line(ln, new, lines[ln - 1])

# ---------- D. (N) 子项恢复标题（按已核实的兄弟层级） ----------
PROMO = {
    3428: "##### （1）高级调度（作业调度）",
    5094: "##### （4）算法四：Peterson算法",
    11090: "##### （1）简单的 CLOCK 算法",
    5146: "#### （3）硬件指令方法——Swap 指令",
    1428: "#### （3）微内核的特点",
    2396: "#### （4）线程库（thread library）的实现",
    12959: "#### （1）磁盘索引节点",
    15974: "#### （4）缓冲池",
}
for ln, new in PROMO.items():
    set_line(ln, new, lines[ln - 1])

# ---------- E. 外核 H4→H3 ----------
cur = lines[1446 - 1]
if cur == "#### 5. 外核":
    set_line(1446, "### 5. 外核", cur)
else:
    skip.append((1446, cur[:50], "期望 #### 5. 外核"))

# ---------- F. 磁盘调度簇协调 ----------
# L17053 考点追踪裸行→H3；L17055/L17084 (1)(3) 降为 H4；L17069 (2) 提升 H4
cur = lines[17053 - 1]
if cur.startswith("考点追踪"):
    set_line(17053, "### " + re.sub(r"^考点追踪\s*", "考点追踪 ", cur), cur)
for ln in [17055, 17084]:
    cur = lines[ln - 1]
    if cur.startswith("##### "):
        set_line(ln, cur.replace("##### ", "#### ", 1), cur)
cur = lines[17069 - 1]
if cur.startswith("（2）"):
    set_line(17069, "#### " + cur, cur)

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("=== 已修改 %d 处 ===" % len(log))
for ln, a, b in log:
    print("L%-6d |%s| -> |%s|" % (ln, a, b))
if skip:
    print("\n=== 跳过 %d ===" % len(skip))
    for ln, a, why in skip:
        print("L%-6d |%s|  (%s)" % (ln, a, why))
