# -*- coding: utf-8 -*-
"""2026-08-17 第二轮：1000题试题册 标题/题号残留修复。"""
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

F = "11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md"
lines = open(F, encoding="utf-8").read().split("\n")
log, skip = [], []
# 收集 (index, op) 从大到小应用
ops = []  # (idx, kind, data)

# 1) H3 题型拆短：`### X、 YYY：rest` → `### X、 YYY` + body
H3 = [5685, 5772, 5788, 5835, 5907, 5921, 5970, 6042, 6055, 6098, 6168, 6182]
for ln in H3:
    ops.append((ln, "split_colon", None))

# 2) 挤行：在最后一个 `N. ` 处拆
CRAM = [385, 463, 465, 487, 611, 613, 617, 631]
for ln in CRAM:
    ops.append((ln, "split_num", None))

# 3) L461 Q3 题干挤在 Q2 选项行，在 `设函数` 前拆
ops.append((461, "split_stem", None))

# 4) 补题号（独立行前插）
ops.append((3833, "insert_num", "6. "))
ops.append((4402, "insert_num", "2. "))
ops.append((4709, "insert_num", "6. "))
# L2757 直接前缀
ops.append((2757, "prepend_num", "34. "))

# 5) 零 基础 → 零基础
ops.append((2, "replace", "## 零基础"))

# ---------- 从大到小应用 ----------
for ln, kind, data in sorted(ops, key=lambda x: -x[0]):
    cur = lines[ln - 1]
    if kind == "split_colon":
        m = re.search(r"^###\s+[一二三]、\s*\S+?[：:]", cur)
        if not m:
            skip.append((ln, cur[:50], "题型格式不匹配"))
            continue
        head = cur[:m.end() - 1]  # 去掉冒号
        body = cur[m.end():].strip()
        lines[ln - 1] = head
        lines[ln:ln] = [body]
        log.append((ln, cur[:35] + "…", head + " + 正文"))
    elif kind == "split_num":
        m = re.search(r"(?<!\d)\d{1,2}\.\s", cur)
        if not m:
            skip.append((ln, cur[:50], "未找到题号"))
            continue
        # 取最后一个匹配
        for mm in re.finditer(r"(?<!\d)(\d{1,2})\.\s", cur):
            m = mm
        lines[ln - 1] = cur[:m.start()]
        lines[ln:ln] = [cur[m.start():]]
        log.append((ln, cur[:35] + "…", "拆出 " + cur[m.start():m.start() + 8] + "…"))
    elif kind == "split_stem":
        idx = cur.find("设函数")
        if idx < 0:
            skip.append((ln, cur[:50], "未找到'设函数'"))
            continue
        lines[ln - 1] = cur[:idx].rstrip()
        lines[ln:ln] = ["3. " + cur[idx:]]
        log.append((ln, cur[:35] + "…", "补 3. 设函数…"))
    elif kind == "insert_num":
        lines[ln - 1:ln - 1] = [data]
        log.append((ln, cur[:30], "前插 " + data.strip()))
    elif kind == "prepend_num":
        lines[ln - 1] = data + cur
        log.append((ln, cur[:25], data.strip() + " …"))
    elif kind == "replace":
        if cur.strip() == "## 零 基础":
            lines[ln - 1] = data
            log.append((ln, cur, data))
        else:
            skip.append((ln, cur[:40], "期望 ## 零 基础"))

open(F, "w", encoding="utf-8").write("\n".join(lines))
print("=== 已修改 %d 处 ===" % len(log))
for ln, a, b in log:
    print("L%-6d |%s| -> |%s|" % (ln, a, b))
if skip:
    print("\n=== 跳过 %d ===" % len(skip))
    for ln, a, why in skip:
        print("L%-6d |%s|  (%s)" % (ln, a, why))
