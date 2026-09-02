# -*- coding: utf-8 -*-
"""应用补丁到 origin/*.md（内容锚定+断言+幂等+完整度门槛）。
安全级：
  L1 直接应用：insert_options（块尾补选项）/ insert_problem（新块插入）/ set_letter（补答案字母）
  L2 完整度门槛后应用：replace_analysis/fix_analysis/fix_stem——内容须"收尾干净"且比原文长
  其余 → manual_review.md
应用记录写 applied.jsonl（重跑跳过）；失败/存疑写 manual_review.md。
用法: python _repair_apply.py [--dry-run]"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M

OUT_DIR = os.path.join(V.VLM, "repair")
PATCHES = os.path.join(OUT_DIR, "patches.jsonl")
APPLIED = os.path.join(OUT_DIR, "applied.jsonl")
MANUAL = os.path.join(OUT_DIR, "manual_review.md")
DRY = "--dry-run" in sys.argv

# ---------- 读取补丁 ----------
recs = {}
for line in open(PATCHES, encoding="utf-8"):
    line = line.strip()
    if line:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("rid"):
            recs[r["rid"]] = r          # 同一 rid 后写覆盖（重试轮）
patches = [r for r in recs.values() if r.get("verdict") == "real" and r.get("fix") and r["fix"].get("content")]
done = set()
if os.path.exists(APPLIED):
    for line in open(APPLIED, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                done.add(json.loads(line)["rid"])
            except Exception:
                pass
patches = [p for p in patches if p["rid"] not in done]
print(f"待应用 {len(patches)} 个 real 补丁")

# ---------- 完整度门槛 ----------
CLEAN_END = re.compile(r"(。|．|\.|\$|）|\)|】|」|故选.?|正确|错误|___)$")

def looks_complete(content):
    c = content.rstrip()
    if len(c) >= 780 and not CLEAN_END.search(c[-30:]):
        return False
    if re.search(r"\\[a-zA-Z]{0,3}$", c):   # 以半个 LaTeX 命令结尾 = 截断
        return False
    return True

# ---------- 内容归一 ----------
def norm_A_content(num, content):
    """A区提取内容 → (letter|None, body)。剥 'NN.' 前缀、识别字母行/前缀。"""
    c = content.strip()
    c = re.sub(rf"^\s*{re.escape(num)}\s*[.、．]\s*", "", c)
    letter = None
    m = re.match(r"^【答案】\s*\(?\s*([A-E])\s*\)?\s*\n?", c)
    if m:
        letter = m.group(1); c = c[m.end():].strip()
    else:
        m = re.match(r"^\(?\s*([A-E])\s*\)?\s*(?=\n|$)", c)
        if m:
            letter = m.group(1); c = c[m.end():].strip()
        else:
            m = re.match(r"^\(\s*([A-E])\s*\)\s*", c)
            if m:
                letter = m.group(1); c = c[m.end():].strip()
    c = re.sub(r"^【解析】\s*", "", c)
    c = re.sub(r"^解\s+", "解 ", c)
    return letter, c

# ---------- 块定位器（返回 (head_i, end_i) 行号区间，end 不含） ----------
def find_block_408(lines, sec, num):
    """408: ### sec 范围内找 ##### NN。"""
    si = None
    for i, l in enumerate(lines):
        if re.match(rf"^###\s+{re.escape(sec)}(\s|$)", l):
            si = i
            break
    if si is None:
        return None
    se = len(lines)
    for j in range(si + 1, len(lines)):
        if re.match(r"^###\s+\d+\.\d+\.\d+", lines[j]):
            se = j
            break
    tgt = int(num)
    for i in range(si + 1, se):
        m = re.match(r"^#####\s+(\d{1,3})\s*$", lines[i].strip())
        if m and int(m.group(1)) == tgt:
            e = se
            for j in range(i + 1, se):
                if re.match(r"^#{1,5}\s", lines[j]):
                    e = j
                    break
            return i, e
    return ("INSERT", si, se)     # 块不存在 → 需新建

def find_block_30jiang(lines, lec, num, pass_type):
    """30讲: ## 第N讲 → #### 习题/解答 范围内 ##### N.M。"""
    si = None
    for i, l in enumerate(lines):
        if re.match(rf"^##\s+第{lec}讲(\s|$)", l):
            si = i
            break
    if si is None:
        return None
    se = len(lines)
    for j in range(si + 1, len(lines)):
        if re.match(r"^##\s+第\d+讲", lines[j]):
            se = j
            break
    area = None
    for i in range(si + 1, se):
        if re.match(r"^####\s+(习题|解答)", lines[i]):
            area = i
            if ("习题" in lines[i]) == (pass_type == "Q"):
                break
    if area is None:
        return None
    ae = se
    for j in range(area + 1, se):
        if re.match(r"^#{2,4}\s", lines[j]):
            ae = j
            break
    for i in range(area + 1, ae):
        m = re.match(r"^#####\s+(\d+\.\d+)\s*$", lines[i].strip())
        if m and m.group(1) == num:
            e = ae
            for j in range(i + 1, ae):
                if re.match(r"^#{1,5}\s", lines[j]):
                    e = j
                    break
            return i, e
    return ("INSERT", area, ae)

def find_block_1000(lines, sec, num):
    """1000题: 非黏滞状态机定位 unit 内题块。
    sec='篇/章'(试题册普通章, 题在 ### k.) 或 '篇/科目/章'| '综合篇/测试卷X/题型'(题在 #### k.)。"""
    parts = sec.split("/")
    pian, rest = parts[0], parts[-1]
    subj = parts[1] if len(parts) == 3 else None
    plevel = 3 if subj is None else 4
    cur = {1: "", 2: "", 3: ""}
    tgt = int(num)
    was_in, exit_i = False, None
    for i, l in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.*)$", l)
        lv, t = (len(m.group(1)), m.group(2).strip()) if m else (0, "")
        if m and lv <= 3:
            cur[lv] = t
            for k in range(lv + 1, 4):
                cur[k] = ""
        if subj:
            in_unit = bool(pian in cur[1] and subj in cur[2] and M._norm(rest[:6]) in M._norm(cur[3]))
        else:
            in_unit = bool(pian in cur[1] and M._norm(rest[:6]) in M._norm(cur[2]))
        if not in_unit:
            if was_in and exit_i is None:
                exit_i = i
            was_in = False
            continue
        was_in = True
        if m and lv == plevel:
            m2 = re.match(r"^(\d+)\s*\\?\s*[.、．]", t)
            if m2:
                n2 = int(m2.group(1))
                if n2 == tgt:
                    e = len(lines)
                    for j in range(i + 1, len(lines)):
                        if re.match(r"^#{1,4}\s", lines[j]):
                            e = j
                            break
                    return i, e
                if n2 > tgt:
                    return ("INSERT", i, i)
    if exit_i is not None:
        return ("INSERT", exit_i, exit_i)
    return None

# ---------- 应用器 ----------
def apply_patches(book, items, dry):
    md = (V.BOOKS.get(book) or M.MATH[book])[0]
    lines = open(md, encoding="utf-8").read().split("\n")
    log = []
    manual = []
    # 从后往前应用，防行号位移（先按定位行排序——定位在应用时动态做，改为逐个定位逐个改但每改一个重定位下一个）
    for p in items:
        num, ps, sec = p["num"], p["pass"], p["sec"]
        ftype = p["fix"]["type"]
        content = str(p["fix"]["content"]).strip()
        rid = p["rid"]
        # 定位
        if book in V.BOOKS:
            loc = find_block_408(lines, sec, num)
        elif book.startswith("30讲"):
            lec = int(sec.split(" ")[0].replace("第", "").replace("讲", ""))
            loc = find_block_30jiang(lines, lec, num, ps)
        else:
            loc = find_block_1000(lines, sec, num)
        if loc is None:
            manual.append((p, "块定位失败"))
            continue
        action = None
        new_lines = None
        if loc[0] == "INSERT":
            # 新建块
            _si, area_s, area_e = loc[0], loc[1], loc[2]
            # 1000题试题册普通章题号是 ### k.（三级），其余（解析册/测试卷）是 #### k.
            h4 = not (book == "1000题-试题册" and len(sec.split("/")) == 2)
            hprefix = "####" if h4 else "###"
            if ps == "A":
                letter, body = norm_A_content(num, content)
                if book in V.BOOKS:
                    head = f"##### {int(num):02d}"
                    blk = [head, "", (letter or ""), "", body] if letter else [head, "", body]
                elif book.startswith("30讲"):
                    blk = [f"##### {num}", "", ((f"({letter}) " if letter else "") + body)]
                else:
                    blk = [f"{hprefix} {num}.", "", (f"【答案】({letter})" if letter else ""), "", ("【解析】" + body if body else "")]
                    blk = [x for x in blk if x != ""]
            else:
                head = f"##### {int(num):02d}" if book in V.BOOKS else (f"##### {num}" if book.startswith("30讲") else f"{hprefix} {num}.")
                blk = [head, "", content]
            # 插入点
            if book in V.BOOKS or book.startswith("30讲"):
                # 408/30讲：locator 给的是区域，需在区域内找编号大于 num 的首个块标题
                ins_at = area_e
                tgt = float(num) if "." in num else int(num)
                for j in range(area_s, area_e):
                    m = re.match(r"^#{4,5}\s+(\d+(?:\.\d+)?)\s*\\?[.、．]?\s*$", lines[j].strip())
                    if m:
                        v = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
                        if v > tgt:
                            ins_at = j
                            break
            else:
                ins_at = area_s   # 1000题 locator 已给精确插入行
            new_lines = lines[:ins_at] + [""] + blk + [""] + lines[ins_at:]
            action = "insert_block"
        else:
            bi, ei = loc
            body = "\n".join(lines[bi + 1:ei]).strip()
            if ftype in ("replace_analysis", "fix_analysis", "fix_stem"):
                if not looks_complete(content):
                    manual.append((p, "内容疑似截断（需补提取）"))
                    continue
                if len(content) < len(body) * 0.8:
                    manual.append((p, f"新内容({len(content)}字)明显短于原文({len(body)}字)，不敢替换"))
                    continue
                if ps == "A":
                    letter, abody = norm_A_content(num, content)
                    if book in V.BOOKS:
                        blk = ([letter] if letter else []) + [abody]
                    elif book.startswith("30讲"):
                        blk = [((f"({letter}) " if letter else "") + abody)]
                    else:
                        blk = ([f"【答案】({letter})"] if letter else []) + ["【解析】" + abody]
                else:
                    blk = [content]
                new_lines = lines[:bi + 1] + [""] + blk + [""] + lines[ei:]
                action = "replace_body"
            elif ftype in ("insert_options", "set_letter"):
                if ps == "A" or ftype == "set_letter":
                    letter, _b = norm_A_content(num, content)
                    letter = letter or content.strip().split("\n")[0].strip("()【答案】 ")
                    if not re.match(r"^[A-E]$", letter):
                        manual.append((p, "字母识别失败: " + content[:40]))
                        continue
                    if re.search(rf"(^|\n)\s*\(?{letter}\)?\s*(\n|$)", body):
                        log.append((rid, "already_present"))
                        continue
                    if book in V.BOOKS:
                        new_lines = lines[:bi + 1] + ["", letter] + lines[bi + 1:]
                    elif book.startswith("30讲"):
                        # 在块首行加 (X) 前缀
                        nb = lines[:]
                        for j in range(bi + 1, ei):
                            if lines[j].strip():
                                nb[j] = f"({letter}) " + lines[j]
                                break
                        new_lines = nb
                    else:
                        new_lines = lines[:bi + 1] + ["", f"【答案】({letter})"] + lines[bi + 1:]
                    action = "set_letter"
                else:
                    # Q区补选项：块尾追加
                    if content[:20] in body:
                        log.append((rid, "already_present"))
                        continue
                    new_lines = lines[:ei] + ["", content] + lines[ei:]
                    action = "append_options"
            elif ftype == "insert_problem":
                # 块已存在但模型说缺（多为缺题干/缺字母）→ 前插而非覆盖，保住块内已有解析
                if not looks_complete(content):
                    manual.append((p, "insert_problem 落到已存在块且内容疑似截断"))
                    continue
                cnorm = re.sub(r"^\s*\d+\s*[.、．]\s*", "", content).strip()
                if cnorm[:25] and cnorm[:25] in body:
                    log.append((rid, "already_present"))
                    continue
                new_lines = lines[:bi + 1] + ["", content, ""] + lines[bi + 1:]
                action = "prepend_block"
            else:
                manual.append((p, f"未知 fix.type={ftype}"))
                continue
        if action:
            if not dry:
                lines = new_lines
            log.append((rid, action))
    if not dry:
        open(md, "w", encoding="utf-8").write("\n".join(lines))
    return log, manual

# ---------- 主流程 ----------
def main():
    by_book = {}
    for p in patches:
        if p["pass"] == "T2":
            continue          # T2 块级另处理
        by_book.setdefault(p["book"], []).append(p)
    all_log, all_manual = [], []
    for book, items in by_book.items():
        log, manual = apply_patches(book, items, DRY)
        all_log += [(book, rid, a) for rid, a in log]
        all_manual += [(book, p, why) for p, why in manual]
        print(f"{book}: 应用 {sum(1 for _, a in log if a != 'already_present')} 处（跳过已存在 {sum(1 for _, a in log if a == 'already_present')}），存疑 {len(manual)}")
    if not DRY:
        for book, rid, a in all_log:
            V.append_jsonl(APPLIED, {"rid": rid, "book": book, "action": a})
    if all_manual:
        with open(MANUAL, "w", encoding="utf-8") as f:
            f.write("# 待人工/补提取清单\n\n")
            f.write("（由 _repair_apply.py 生成，每次运行全量重写；dry-run 与实跑内容相同）\n\n")
            for book, p, why in all_manual:
                f.write(f"- [ ] **{book}** {p['pass']} `{p['sec']}` 题{p['num']}（rid{p['rid']}）：{why}；初筛标记 {'+'.join(p['flags'])}；核实理由：{p.get('reason','')[:80]}\n")
    print(f"合计: 应用 {sum(1 for _, _, a in all_log if a != 'already_present')}，存疑 {len(all_manual)}")

if __name__ == "__main__":
    main()
