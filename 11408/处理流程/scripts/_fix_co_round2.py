# -*- coding: utf-8 -*-
"""2026-08-17 第二轮：2027计算机组成原理 标题级残留修复。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/2027计算机组成原理/2027计算机组成原理.md"
lines = open(F, encoding="utf-8").read().split("\n")
log, skip = [], []

def set_line(ln, new, expect=None):
    cur = lines[ln - 1]
    if expect is not None and cur.strip() != expect.strip():
        skip.append((ln, cur[:60], "期望[%s]" % expect[:40]))
        return
    lines[ln - 1] = new
    log.append((ln, cur[:45], new[:45]))

def insert_before(ln, text):
    cur = lines[ln - 1]
    lines[ln - 1:ln - 1] = text
    log.append((ln, "插入前:" + cur[:25], text[0][:45]))

# ---------- 1. 考点追踪裸行 → H3（排除 L8542，它破坏指令寻址簇） ----------
EXCLUDE = {8542}
n_kz = 0
for i, l in enumerate(lines, 1):
    if i in EXCLUDE:
        continue
    if l.startswith("考点追踪") and not l.startswith("#"):
        new = "### " + re.sub(r"^考点追踪\s*", "考点追踪 ", l)
        set_line(i, new, l)
        n_kz += 1
print("考点追踪裸行提升 %d (排除 L8542)" % n_kz)

# ---------- 2. 考纲子项 → H3 ----------
KG = [913, 3939, 3941, 3943, 3949, 3953, 3957, 3963, 8077, 8079, 8081, 8083,
      8087, 8089, 10551, 10553, 10555, 10557, 10561, 10565, 10571, 15437, 15441]
for ln in KG:
    cur = lines[ln - 1]
    if cur.startswith("（"):
        set_line(ln, "### " + cur, cur)
    else:
        skip.append((ln, cur[:40], "考纲子项未匹配"))

# ---------- 3. (N) 数字子项恢复标题 ----------
PROMO = {
    484: "#### （2） 主频和 CPU 时钟周期",
    509: "#### （4） CPU 执行时间，运行一个程序所花费的时间",
    531: "#### （5） MIPS（Million Instructions Per Second）",
    539: "#### （6） FLOPS（Floating-point Operations Per Second）",
    968: "##### （1）二进制数转换为八进制数和十六进制数",
    986: "##### （2）任意进制数转换为十进制数",
    1068: "##### （1）原码表示法",
    1940: "#### （2）减法运算的工作原理",
    2064: "##### （2）无符号整数的乘法运算电路",
    2196: "##### （2）无符号整数的除法运算电路",
    8139: "#### 1. 零地址指令",
    8155: "#### 2. 一地址指令",
    8179: "#### 3. 二地址指令",
    5112: "#### （2） 同时启动方式",
    6015: "#### （2）磁记录原理",
    6021: "#### （3）磁盘的性能指标",
    6044: "#### （4）磁盘地址",
    6056: "#### 2. 磁盘阵列",
    9382: "#### （2）算术和逻辑运算指令",
    12350: "##### （1）微程序控制器的基本组成",
    12368: "##### （2）微程序控制器的工作过程",
    12496: "##### （1）硬布线控制器的特点",
    12995: "#### （1） 故障（Fault）",
    14486: "### 1. 流水线越多，并行度就越高。是否流水段越多，指令执行越快？",
    15039: "#### （1） 非突发传输与突发传输",
    15651: "#### （1） 独立编址（I/O 映射方式）",
}
for ln, new in PROMO.items():
    set_line(ln, new, lines[ln - 1])

# ---------- 4. 指令寻址簇：1.指令寻址→H4；(1)顺序→H5；(2)跳跃 H4→H5 ----------
cur = lines[8534 - 1]
if cur.strip() == "1. 指令寻址":
    set_line(8534, "#### 1. 指令寻址", cur)
cur = lines[8538 - 1]
if cur.strip() == "（1）顺序寻址":
    set_line(8538, "##### （1）顺序寻址", cur)
cur = lines[8548 - 1]
if cur.strip() == "#### （2） 跳跃寻址":
    set_line(8548, "##### （2） 跳跃寻址", cur)

# ---------- 5. 拆行合并 L7404+L7406 ----------
cur4, cur6 = lines[7404 - 1], lines[7406 - 1]
if cur4.strip() == "### 考点追踪 TLB 的硬件实现（2018），TLB 和 Cache" and cur6.strip() == "的比较（2020）":
    lines[7404 - 1] = "### 考点追踪 TLB 的硬件实现（2018），TLB 和 Cache 的比较（2020）"
    del lines[7406 - 1]
    log.append((7404, cur4[:45], "合并拆行"))
    log.append((7406, cur6[:45], "删除残行"))
else:
    skip.append((7404, cur4[:45], "拆行前提不满足"))

# ---------- 6. 例2.3 题干标题 → 正文 ----------
cur = lines[1873 - 1]
if cur.startswith("#### 【例 2.3】"):
    set_line(1873, cur.replace("#### ", "", 1), cur)
else:
    skip.append((1873, cur[:50], "期望 #### 【例 2.3】"))

# ---------- 7. L2023 $^{4}$ → 4. ----------
cur = lines[2023 - 1]
if cur.strip() == "#### $^{4}$ 原码的加减运算（了解）":
    set_line(2023, "#### 4. 原码的加减运算（了解）", cur)

# ---------- 8. 删 L9531 碎片 ----------
cur = lines[9531 - 1]
if cur.strip() == '“指令的功能（2019':
    del lines[9531 - 1]
    log.append((9531, cur[:30], "删除OCR碎片"))
else:
    skip.append((9531, cur[:40], "碎片不匹配"))

# ---------- 9. 补插 02.【解答】 ----------
cur = lines[9253 - 1]
if cur.strip().startswith("1）因为PC的增量"):
    lines[9253 - 1:9253 - 1] = ["#### 02. 【解答】", ""]
    log.append((9253, "插入 #### 02. 【解答】", cur[:25]))
else:
    skip.append((9253, cur[:40], "02插入点不匹配"))

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("=== 已修改 %d 处 ===" % len(log))
for ln, a, b in log:
    print("L%-6d |%s| -> |%s|" % (ln, a, b))
if skip:
    print("\n=== 跳过 %d ===" % len(skip))
    for ln, a, why in skip:
        print("L%-6d |%s|  (%s)" % (ln, a, why))
