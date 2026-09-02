# -*- coding: utf-8 -*-
"""修复 VLM 补丁引入的 JSON 转义腐蚀（限定在 applied.jsonl 记录的补丁块内）。
腐蚀模式：
  A) \r / \n 被 JSON 解码成换行 → 行首残留 "ight..."(原 \rightX) 或 "eq..."(原 \neq) → 并回上一行
  B) \\ 衰减成 \ → 数学环境内 \数字 \- \= \<空格> 应是行分隔 \\ → 补回双反斜杠
  C) \\n 字面两字符 → 真实换行
用法: python _fix_escape_damage.py [--dry-run]"""
import os, sys, glob, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_apply import find_block_408, find_block_30jiang, find_block_1000

DRY = "--dry-run" in sys.argv
BS = chr(92)

# ---- 收集每本书被补丁过的 (sec, num, pass) ----
recs = {}
for line in open("_vlm/repair/patches.jsonl", encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("rid"):
            recs[r["rid"]] = r
targets = {}   # book -> [(sec, num, pass)]
for line in open("_vlm/repair/applied.jsonl", encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    if r.get("action") not in ("replace_body", "complete_replace", "prepend_block", "insert_block"):
        continue
    p = recs.get(r["rid"])
    if not p:
        continue
    targets.setdefault(p["book"], []).append((p["sec"], str(p["num"]), p["pass"]))

def math_fix(s):
    """数学环境内的衰减修复。逐段处理 $...$ / $$...$$。"""
    out, i, n = [], 0, len(s)
    while i < n:
        if s[i] == "$":
            if s.startswith("$$", i):
                j = s.find("$$", i + 2)
                if j == -1:
                    out.append(s[i:])
                    break
                seg, nxt = s[i:j + 2], j + 2
            else:
                j = s.find("$", i + 1)
                if j == -1:
                    out.append(s[i:])
                    break
                seg, nxt = s[i:j + 1], j + 1
            # 0) 先回滚上一版 bug 造成的三连反斜杠：\\\数字 → \\数字
            seg = re.sub(r"\\\\\\(?=[0-9\-=])", lambda m: BS + BS, seg)
            # B) 衰减的 \\ ：单反斜杠(前一个不是反斜杠)后跟 数字/-/= → 双反斜杠
            seg = re.sub(r"(?<!\\)\\(?=[0-9\-=])", lambda m: BS + BS, seg)
            # 数组环境内的 '\ '（衰减的行分隔）→ '\\ '
            if BS + "begin{" in seg:
                seg = re.sub(r"(?<!\\)\\ ", lambda m: BS + BS + " ", seg)
            out.append(seg)
            i = nxt
        else:
            out.append(s[i])
            i += 1
    return "".join(out)

def fix_block(blk_lines):
    """返回 (新行列表, 改动数)"""
    # A) 行首碎片并回
    merged = []
    chg = 0
    for l in blk_lines:
        if re.match(r"^ight", l) and merged:
            merged[-1] = merged[-1] + BS + "r" + l
            chg += 1
        elif re.match(r"^eq([$\s},.]|$)", l) and merged and merged[-1].count("$") % 2 == 1:
            merged[-1] = merged[-1] + BS + "n" + l
            chg += 1
        else:
            merged.append(l)
    # C) 字面 \n（不跟字母）→ 真换行
    out = []
    for l in merged:
        if BS + "n" in l:
            parts = re.split(r"\\n(?![a-zA-Z])", l)
            if len(parts) > 1:
                out.extend(parts)
                chg += 1
                continue
        out.append(l)
    # B) 数学段内衰减修复
    final = []
    for l in out:
        nl = math_fix(l)
        if nl != l:
            chg += 1
        final.append(nl)
    return final, chg

def main():
    total_chg = 0
    for book, items in targets.items():
        md = (V.BOOKS.get(book) or M.MATH[book])[0]
        lines = open(md, encoding="utf-8").read().split("\n")
        book_chg = 0
        for sec, num, ps in items:
            if book in V.BOOKS:
                loc = find_block_408(lines, sec, num)
            elif book.startswith("30讲"):
                lec = int(sec.split(" ")[0].replace("第", "").replace("讲", ""))
                loc = find_block_30jiang(lines, lec, num, ps)
            else:
                loc = find_block_1000(lines, sec, num)
            if not loc or loc[0] == "INSERT":
                continue
            bi, ei = loc
            new_blk, chg = fix_block(lines[bi:ei])
            if chg:
                book_chg += chg
                lines = lines[:bi] + new_blk + lines[ei:]
        print(f"{book}: 修复块内改动 {book_chg} 处（{len(items)} 个补丁块）")
        if book_chg and not DRY:
            open(md, "w", encoding="utf-8", newline="").write("\n".join(lines))
        total_chg += book_chg
    print("总改动", total_chg, "dry =", DRY)

if __name__ == "__main__":
    main()
