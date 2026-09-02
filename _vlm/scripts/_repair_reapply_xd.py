# -*- coding: utf-8 -*-
"""线代修复重放：从归档 raw 用"保 LaTeX 解码"重建内容，替换被 JSON 转义腐蚀的块体。
背景：json.loads 把模型写的 \frac \begin \right \to \neq 中的 \f \b \r \t \n
解码成控制字符/换行。raw 原文还在（patches 的 batch_meta.raw / complete.raw），
用保命令解码重新提取后重放。
流程：恢复备份 → 逐 rid 定位 → 门控 → 替换。幂等：直接整重来（从备份恢复）。"""
import os, sys, io, json, re, shutil, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_apply import find_block_30jiang, looks_complete, norm_A_content
from _fix_escape_damage import fix_block

BOOK = "30讲-线代"
BS = chr(92)
DRY = "--dry-run" in sys.argv

# ---- 保 LaTeX 的 JSON 预处理：\f \b \r \t \n 后跟字母 → 双写反斜杠保留命令 ----
PRESERVE = re.compile(r'(\\\\)|\\([frtbn])(?=[a-zA-Z])|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')

def pres_sub(m):
    if m.group(1):
        return m.group(1)                       # \\ 原样（json.loads → \）
    if m.group(2):
        return BS + BS + m.group(2)             # \f+a → \\f+a（json.loads → \f 字面）
    g = m.group(0)
    return BS + BS + g[1:]                      # 其他非法转义 → 字面化

def decode_preserving(raw):
    """从 raw 模型输出解析 JSON（数组或对象），保 LaTeX 命令。"""
    t = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.M)
    i = min([x for x in (t.find("["), t.find("{")) if x >= 0], default=-1)
    if i < 0:
        return None
    t = PRESERVE.sub(pres_sub, t[i:])
    try:
        return json.loads(t)
    except Exception:
        # 截断挽救：数组 → 最后一个 "},"
        if t.startswith("["):
            cut = t.rfind("},")
            if cut > 0:
                try:
                    return json.loads(t[:cut] + "}]")
                except Exception:
                    pass
        cut = t.rfind('",')
        if cut > 0:
            try:
                return json.loads(t[:cut] + '"}')
            except Exception:
                pass
    return None

# ---- 需要重放的 rid ----
COMPLETE_RIDS = {210, 211, 217, 235}
PATCH_RIDS = {215, 218, 222, 223, 224, 226}   # 全文替换类
PREPEND_RIDS = {220, 221}                     # 缺题干：前插，保住备份解析
SKIP_RIDS = {237: "误报：备份块已有答案行（仅公式排版差异），不动"}

# 元数据
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

# complete.jsonl raw
comp_raw = {}
for line in open("_vlm/repair/complete.jsonl", encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("rid") in COMPLETE_RIDS and r.get("raw"):
            comp_raw[r["rid"]] = r["raw"]

# batch_meta raw（线代全部批次）
batch_raws = []
for line in open("_vlm/repair/patches.jsonl", encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("batch_meta") and r.get("book") == BOOK and r.get("raw"):
            batch_raws.append(r["raw"])

def content_from_batches(num):
    for raw in batch_raws:
        arr = decode_preserving(raw)
        if not isinstance(arr, list):
            continue
        for it in arr:
            if isinstance(it, dict) and str(it.get("num")) == num:
                fx = it.get("fix") or {}
                if fx.get("content"):
                    return str(fx["content"]), it.get("verdict")
    return None, None

# ---- 恢复备份 ----
md = M.MATH[BOOK][0]
bak = "_vlm/md_backup/30讲-线代.md"
if not DRY:
    shutil.copy(bak, md)
lines = open(bak, encoding="utf-8").read().split("\n")
print("已从备份恢复", BOOK, len(lines), "行")

results = []
for rid in sorted(COMPLETE_RIDS | PATCH_RIDS | PREPEND_RIDS):
    p = recs.get(rid)
    if not p:
        results.append((rid, "无patch记录")); continue
    sec, num, ps = p["sec"], str(p["num"]), p["pass"]
    if rid in COMPLETE_RIDS:
        raw = comp_raw.get(rid)
        j = decode_preserving(raw) if raw else None
        content = str(j.get("content")) if isinstance(j, dict) and j.get("content") else None
    else:
        content, verdict = content_from_batches(num)
    if not content:
        results.append((rid, "raw恢复失败")); continue
    content = content.strip()
    if not looks_complete(content):
        results.append((rid, f"门控拦截 len={len(content)} 尾={content[-30:]!r}")); continue
    lec = int(sec.split(" ")[0].replace("第", "").replace("讲", ""))
    loc = find_block_30jiang(lines, lec, num, ps)
    if not loc or loc[0] == "INSERT":
        results.append((rid, "定位失败")); continue
    bi, ei = loc
    if rid in PREPEND_RIDS:
        # 缺题干：剥题号前缀后前插，保住块内已有解析
        stem = re.sub(rf"^\s*{re.escape(num)}\s*[.、．]?\s*", "", content).strip()
        fixed, _ = fix_block(stem.split("\n"))
        stem = "\n".join(fixed)
        old_body = "\n".join(lines[bi + 1:ei]).strip()
        if stem[:25] in old_body:
            results.append((rid, "题干已存在，跳过")); continue
        blk = [stem, "", old_body]
        lines = lines[:bi + 1] + [""] + blk + [""] + lines[ei:]
        results.append((rid, f"OK prepend len={len(stem)}"))
        continue
    letter, body = norm_A_content(num, content)
    head = ((f"({letter}) ") if letter else "") + body
    fixed, chg = fix_block(head.split("\n"))
    blk = ["\n".join(fixed)]
    lines = lines[:bi + 1] + [""] + blk + [""] + lines[ei:]
    results.append((rid, f"OK len={len(content)} letter={letter} 转义修复{chg}处"))

for rid, why in SKIP_RIDS.items():
    results.append((rid, "跳过: " + why))

for rid, msg in results:
    print(f"  rid{rid}: {msg}")
nok = sum(1 for _, m in results if m.startswith("OK"))
if not DRY and nok:
    open(md, "w", encoding="utf-8", newline="").write("\n".join(lines))
print(f"重放 {nok}/{len(COMPLETE_RIDS | PATCH_RIDS | PREPEND_RIDS)}（另跳过 {len(SKIP_RIDS)}），dry={DRY}")
