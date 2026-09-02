# -*- coding: utf-8 -*-
"""应用补提取结果（complete.jsonl）到 origin md。
对象：patches.jsonl 中 real 且 fix.type ∈ replace_analysis/fix_analysis/fix_stem、尚未 applied 的项，
其完整全文由 _repair_complete.py 单题重提取得到。
安全门槛：looks_complete + 长度不得明显短于原文 + 定位锚定；不过门槛 → manual_review2.md。
幂等：写 applied.jsonl（action=complete_replace），重跑跳过。
用法: python _repair_apply2.py [--dry-run]"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_apply import (find_block_408, find_block_30jiang, find_block_1000,
                           looks_complete, norm_A_content)

OUT_DIR = os.path.join(V.VLM, "repair")
DRY = "--dry-run" in sys.argv

# ---- 收集补提取结果（按 rid 去重，后写覆盖）----
comp = {}
for line in open(os.path.join(OUT_DIR, "complete.jsonl"), encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("rid") and r.get("content") and len(r["content"]) > 50:
        comp[r["rid"]] = r

# ---- 对应 patch 元数据 ----
recs = {}
for line in open(os.path.join(OUT_DIR, "patches.jsonl"), encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("rid"):
            recs[r["rid"]] = r

done = set()
ap = os.path.join(OUT_DIR, "applied.jsonl")
if os.path.exists(ap):
    for line in open(ap, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                done.add(json.loads(line)["rid"])
            except Exception:
                pass

todo = []
for rid, r in comp.items():
    p = recs.get(rid)
    if not p or rid in done:
        continue
    todo.append((rid, p, r))
todo.sort(key=lambda x: x[0])
print(f"补提取可用 {len(comp)} 项，待应用 {len(todo)} 项（dry={DRY}）")

log, manual = [], []
for rid, p, r in todo:
    book, ps, sec, num = p["book"], p["pass"], p["sec"], p["num"]
    md = (V.BOOKS.get(book) or M.MATH[book])[0]
    lines = open(md, encoding="utf-8").read().split("\n")
    if book in V.BOOKS:
        loc = find_block_408(lines, sec, num)
    elif book.startswith("30讲"):
        lec = int(sec.split(" ")[0].replace("第", "").replace("讲", ""))
        loc = find_block_30jiang(lines, lec, num, ps)
    else:
        loc = find_block_1000(lines, sec, num)
    if loc is None or loc[0] == "INSERT":
        manual.append((p, "块定位失败/不存在"))
        continue
    bi, ei = loc
    body = "\n".join(lines[bi + 1:ei]).strip()
    content = str(r["content"]).strip()
    gate_fail = None
    if not looks_complete(content):
        gate_fail = f"补提取内容仍疑似截断(len={len(content)})"
    elif len(content) < len(body) * 0.8:
        gate_fail = f"补提取内容({len(content)}字)短于原文({len(body)}字)"
    if gate_fail:
        # 交叉验证：若当前原文本身收尾完整，说明初筛/核实是误报，保留原文
        if looks_complete(body):
            if not DRY:
                V.append_jsonl(ap, {"rid": rid, "book": book, "action": "keep_original",
                                    "note": gate_fail, "len_old": len(body), "len_new": len(content)})
            log.append((book, rid, len(body), len(content), "keep_original"))
            continue
        manual.append((p, gate_fail + "；且原文收尾也不完整"))
        continue
    letter = r.get("letter")
    if ps == "A":
        l2, abody = norm_A_content(num, content)
        letter = letter or l2
        if book in V.BOOKS:
            blk = ([letter] if letter else []) + [abody]
        elif book.startswith("30讲"):
            blk = [((f"({letter}) " if letter else "") + abody)]
        else:
            blk = ([f"【答案】({letter})"] if letter else []) + ["【解析】" + abody]
    else:
        # Q 区：题干（含选项）整段替换
        c2 = re.sub(rf"^\s*{re.escape(num)}\s*[.、．]\s*", "", content).strip()
        blk = [c2]
    new_lines = lines[:bi + 1] + [""] + blk + [""] + lines[ei:]
    if not DRY:
        open(md, "w", encoding="utf-8").write("\n".join(new_lines))
        V.append_jsonl(ap, {"rid": rid, "book": book, "action": "complete_replace",
                            "len_old": len(body), "len_new": len(content)})
    log.append((book, rid, len(body), len(content), "replace"))

for b, rid, lo, ln, act in log:
    print(f"  ✓ {b} rid{rid} {lo}→{ln}字 [{act}]")
if manual:
    mode = "w"
    with open(os.path.join(OUT_DIR, "manual_review2.md"), mode, encoding="utf-8") as f:
        f.write("# 补提取后仍存疑清单\n\n")
        for p, why in manual:
            f.write(f"- [ ] **{p['book']}** {p['pass']} `{p['sec']}` 题{p['num']}（rid{p['rid']}）：{why}\n")
print(f"应用 {len(log)}，存疑 {len(manual)}")
