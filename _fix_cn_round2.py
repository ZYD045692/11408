# -*- coding: utf-8 -*-
"""2026-08-17 第二轮：2027计算机网络 标题级残留修复。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/2027计算机网络/2027计算机网络.md"
lines = open(F, encoding="utf-8").read().split("\n")
log, skip = [], []

def set_line(ln, new, expect=None):
    cur = lines[ln - 1]
    if expect is not None and cur.strip() != expect.strip():
        skip.append((ln, cur[:60], "期望[%s]" % expect[:40]))
        return
    lines[ln - 1] = new
    log.append((ln, cur[:45], new[:45]))

# ---------- 1. 考点追踪裸行 → H3（含缺空格补空格） ----------
n_kz = 0
for i, l in enumerate(lines, 1):
    if l.startswith("考点追踪") and not l.startswith("#"):
        new = "### " + re.sub(r"^考点追踪\s*", "考点追踪 ", l)
        set_line(i, new, l)
        n_kz += 1
print("考点追踪裸行提升 %d" % n_kz)

# 已有标题但粘连缺空格
n_sp = 0
for i, l in enumerate(lines, 1):
    if l.startswith("### 考点追踪") and not l.startswith("### 考点追踪 "):
        set_line(i, l.replace("### 考点追踪", "### 考点追踪 ", 1), l)
        n_sp += 1
print("考点追踪补空格 %d" % n_sp)

# OCR 首都→首部
cur = lines[11161 - 1]
if "首都格式" in cur:
    set_line(11161, cur.replace("首都格式", "首部格式"), cur)
else:
    skip.append((11161, cur[:60], "未含'首都格式'"))

# ---------- 2. 考纲子项 → H3 ----------
KG = [1507, 1521, 2554, 2556, 2558, 2584, 2588, 12465, 12469, 12473, 12479, 12483]
for ln in KG:
    cur = lines[ln - 1]
    if cur.startswith("（"):
        set_line(ln, "### " + cur, cur)
    else:
        skip.append((ln, cur[:40], "考纲子项未匹配"))

# ---------- 3. 缺号 (N) → 提升到与兄弟同级（H4） ----------
PROMO = {
    886: "#### （4） 传输层（Transport Layer）",
    2993: "#### （4）检验位取值",
    12736: "#### （2）本地域名服务器向其他域名服务器可采用递归查询或迭代查询",
    6032: "#### 单项选择题",
}
for ln, new in PROMO.items():
    set_line(ln, new, lines[ln - 1])

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("=== 已修改 %d 处 ===" % len(log))
for ln, a, b in log:
    print("L%-6d |%s| -> |%s|" % (ln, a, b))
if skip:
    print("\n=== 跳过 %d ===" % len(skip))
    for ln, a, why in skip:
        print("L%-6d |%s|  (%s)" % (ln, a, why))
