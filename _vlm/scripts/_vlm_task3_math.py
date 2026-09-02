# -*- coding: utf-8 -*-
"""任务3-数学：30讲(高数/线代) + 1000题(试题册/解析册) 的题目/答案完整性观察。
对齐方式：全页 OCR 全文索引（_vlm/pages/ocr_full/<book>.jsonl）定位 节/题 → PDF 页。
  30讲:  unit=讲, Q=####习题(##### N.M), A=####解答
  试题册: unit=篇/章, Q=### k.（书签定位章起始页，全文索引验证+定题页）
  解析册: unit=篇/科目/章, A=#### k.（全文索引定位章起始页与"【答案】"序列）
每题先定位到页，再按 ≤8 页窗口分组调用 VLM。结果写 task3q/task3a/<书>.jsonl（与408同格式，sec=unit名）。
用法: python _vlm_task3_math.py [Q|A|QA] [书名号...] [--dry-run] [--limit N]"""
import os, re, sys, io, json
if sys.stdout is not None and hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V

MATH = {
    "30讲-高数": ("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", "11408/pdf/27张宇基础30讲（高数）.pdf"),
    "30讲-线代": ("11408/origin/27张宇基础30讲线代/27张宇基础30讲线代.md", "11408/pdf/27张宇基础30讲线代.pdf"),
    "1000题-试题册": ("11408/origin/27张宇1000题数一【试题册】/27张宇1000题数一【试题册】.md", "11408/pdf/27张宇1000题数一【试题册】.pdf"),
    "1000题-解析册": ("11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md", "11408/pdf/27张宇1000题数一【解析册】.pdf"),
}
MATH = {k: (os.path.join(V.ROOT, a), os.path.join(V.ROOT, b)) for k, (a, b) in MATH.items()}
FULL_DIR = os.path.join(V.VLM, "pages", "ocr_full")
MAX_WIN = 8   # 每次调用最多带的核心页数

def _norm(s):
    """全角数字/字母转半角，便于正则匹配（OCR 常把 1 识别成 １）。"""
    return s.translate({0xFF10 + i: 0x30 + i for i in range(10)} |
                       {0xFF21 + i: 0x41 + i for i in range(26)} |
                       {0xFF41 + i: 0x61 + i for i in range(26)})

def load_full(book):
    path = os.path.join(FULL_DIR, f"{book}.jsonl")
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            out[r["page"]] = _norm(r.get("text", ""))
    return out

def pages_with(full, pat, lo=0, hi=None, flags=0):
    rx = re.compile(pat, flags)
    hi = hi if hi is not None else max(full) + 1
    return [p for p in sorted(full) if lo <= p < hi and rx.search(full[p])]

# ---------- md 解析 ----------
def parse_30jiang(md_path):
    """返回 [{lec, name, q:{num:text}, a:{num:text}}]"""
    text = open(md_path, encoding="utf-8").read()
    blocks = re.split(r"(?m)^## 第(\d+)讲\s*(.*)$", text)
    units = []
    for k in range(1, len(blocks), 3):
        lec, name, body = int(blocks[k]), blocks[k + 1].strip(), blocks[k + 2]
        m = re.search(r"(?m)^### 基础习题精练\s*$", body)
        if not m:
            continue
        seg = body[m.start():]
        # 截到下一个 ### 或 ## 之前
        m2 = re.search(r"(?m)^#{1,3} ", seg[10:])
        if m2:
            seg = seg[:10 + m2.start()]
        qm = re.search(r"(?m)^#### 习题\s*$", seg)
        am = re.search(r"(?m)^#### 解答\s*$", seg)
        qtxt = seg[qm.end():am.start() if am else len(seg)] if qm else ""
        atxt = seg[am.end():] if am else ""
        def probs(t):
            parts = re.split(r"(?m)^##### (\d+\.\d+)\s*$", t)
            return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}
        units.append({"lec": lec, "name": name, "q": probs(qtxt), "a": probs(atxt)})
    return units

def split_1000_q(md_path):
    """全文按标题流切。普通章: # 篇 > ## 章 > ### k.；测试卷: # 综合篇 > ## 测试卷X > ### 题型 > #### k."""
    text = open(md_path, encoding="utf-8").read()
    units, pian, juan, cur, cur_num = [], "", "", None, None
    for l in text.split("\n"):
        m = re.match(r"^(#{1,4})\s+(.*)$", l)
        if m:
            lvl, title = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                pian, juan, cur, cur_num = title, "", None, None
            elif lvl == 2:
                cur_num = None
                if "测试卷" in title:
                    juan, cur = title, None          # 等 lvl3 题型标题建单元
                else:
                    juan = ""
                    cur = {"unit": f"{pian}/{title}", "probs": {}}
                    units.append(cur)
            elif lvl == 3:
                cur_num = None
                if juan:
                    cur = {"unit": f"{pian}/{juan}/{title}", "probs": {}}
                    units.append(cur)
                elif cur is not None:
                    mm = re.match(r"^(\d+)\s*\\?\s*[.、．]", title)
                    if mm:
                        cur_num = mm.group(1)
                        cur["probs"][cur_num] = []
            elif lvl == 4 and juan and cur is not None:
                mm = re.match(r"^(\d+)\s*\\?\s*[.、．]", title)
                if mm:
                    cur_num = mm.group(1)
                    cur["probs"][cur_num] = []
            continue
        if cur is not None and cur_num is not None:
            cur["probs"][cur_num].append(l)
    for u in units:
        u["probs"] = {k: "\n".join(v).strip() for k, v in u["probs"].items()}
    return [u for u in units if u["probs"]]

def split_1000_a(md_path):
    """解析册: # 篇 > ## 科目 > ### 章 > #### k. → [{unit, probs}]"""
    text = open(md_path, encoding="utf-8").read()
    lines = text.split("\n")
    units, pian, subj, cur, cur_num = [], "", "", None, None
    for l in lines:
        m = re.match(r"^(#{1,4})\s+(.*)$", l)
        if m:
            lvl, title = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                pian = title
            elif lvl == 2:
                subj = title
            elif lvl == 3:
                cur = {"unit": f"{pian}/{subj}/{title}", "probs": {}}
                units.append(cur)
                cur_num = None
            elif lvl == 4 and cur is not None:
                mm = re.match(r"^(\d+)\s*\\?\s*[.、．]", title)
                if mm:
                    cur_num = mm.group(1)
                    cur["probs"][cur_num] = []
                    continue
            if lvl <= 3:
                cur_num = None
            continue
        if cur is not None and cur_num is not None:
            cur["probs"][cur_num].append(l)
    for u in units:
        u["probs"] = {k: "\n".join(v).strip() for k, v in u["probs"].items()}
    return [u for u in units if u["probs"]]

# ---------- 页定位 ----------
def locate_30jiang(book, units, full):
    """给每个讲的 习题/解答 定页范围 + 每题页码。返回 units 填充 pages_q/pages_a/pp_q/pp_a。"""
    # 0) 第1讲起始页（过滤目录页的"基础习题精练"误命中）
    first = units[0]
    lec1 = pages_with(full, rf"第\s*{first['lec']}\s*讲[\s\S]{{0,30}}{re.escape(first['name'][:4])}")
    floor = lec1[0] if lec1 else 0
    # 1) 习题精练标题页（全书顺序，一讲一个）
    starts = [p for p in pages_with(full, r"基础习题精练") if p >= floor]
    n_expect = len(units)
    if len(starts) != n_expect:
        V.log(f"[t3math:{book}] ⚠ 习题精练标题页 {len(starts)} != md讲数 {n_expect}，顺序对齐可能错位")
    starts = starts + [max(full) + 1]
    for i, u in enumerate(units):
        if i >= len(starts) - 1:
            u["pages_q"] = u["pages_a"] = None
            continue
        q0 = starts[i]
        # 下一讲起始页（界桩）：下一讲标题"第N+1讲 <名>"首次出现的页
        if i + 1 < len(units):
            nu = units[i + 1]
            nlec = pages_with(full, rf"第\s*{nu['lec']}\s*讲[\s\S]{{0,30}}{re.escape(nu['name'][:4])}", q0)
            hard_end = nlec[0] if nlec else starts[i + 1]
        else:
            hard_end = max(full) + 1
        q1 = min(starts[i + 1], hard_end)
        # 2) 解答起始页：本讲范围内找独立"解答"标题行；找不到则找 N.1 的第二次出现
        am = pages_with(full, r"(?m)^\s*解\s*答\s*$", q0, q1)
        if am:
            a0 = am[0]
        else:
            occ = pages_with(full, rf"(?<![\d.]){re.escape(str(u['lec']) + '.1')}(?![\d.])", q0, q1)
            a0 = occ[1] if len(occ) >= 2 else None
        u["pages_q"] = (q0, a0 + 1 if a0 is not None else q1)   # 含解答标题页（上半页可能还有题）
        u["pages_a"] = (a0, q1) if a0 is not None else None
        # 3) 每题页码（限定在各自范围内，避免题号在答案区重复混淆）
        # OCR 题号变体容忍："3.9" / "3. 9" / "3．9"；严格模式（尾部不带数字）优先，宽松兜底
        def find_num(num, rng):
            a, _, b = num.partition(".")
            base = rf"(?<![\d.]){a}\s*[.．、]\s*{b}"
            occ = pages_with(full, base + r"(?![\d.])", rng[0], rng[1])
            if not occ:
                occ = pages_with(full, base, rng[0], rng[1])
            return occ[0] if occ else None
        for scope, rng in (("q", u["pages_q"]), ("a", u["pages_a"])):
            u[f"pp_{scope}"] = {}
            if not rng:
                continue
            for num in u[scope]:
                u[f"pp_{scope}"][num] = find_num(num, rng)
    return units

def locate_1000q(book, units, full):
    """试题册章起点定位。
    普通章：书签 ±1 页内用 is_title（行首"题1"+本章章号）精修。
    测试卷：书签定卷首页，卷内按 一、选择/二、填空/三、解答 标题切题型范围。
    每题页码按题号单调推进（防跨章/跨页串号）。"""
    import fitz
    doc = fitz.open(MATH[book][1])
    toc = doc.get_toc()
    doc.close()
    bm_ch = [p - 1 for lvl, t, p in toc if re.search(r"第\d+章|零基础", t)]
    bm_juan = [p - 1 for lvl, t, p in toc if "测试卷" in t]
    hi_all = max(full) + 1
    chap_units = [u for u in units if "测试卷" not in u["unit"]]
    juan_units = [u for u in units if "测试卷" in u["unit"]]
    if len(bm_ch) != len(chap_units):
        V.log(f"[t3math:{book}] ⚠ 章书签数 {len(bm_ch)} != 章单元数 {len(chap_units)}（顺序配对前{min(len(bm_ch),len(chap_units))}个）")

    # --- 普通章/零基础 ---
    refined = []
    for i, u in enumerate(chap_units):
        if i >= len(bm_ch):
            refined.append(None)
            continue
        bm = bm_ch[i]
        chap = u["unit"].split("/")[-1]          # 第N章 xxx 或 零基础
        mnum = re.match(r"第(\d+)章\s*(.*)", chap)
        def is_title(p, mnum=mnum):
            """章标题页 = 行首"1."(题1) + 本章章号"第N章"；章号 OCR 烂掉时才用章名前4字兜底，
            且页面上不能出现任何"第M章"（防隔壁章页眉/标题误判）。"""
            t = full.get(p, "")
            if not t or not re.search(r"(?m)^\s*1\s*[.、．]", t):
                return False
            if mnum:
                if re.search(rf"第\s*{mnum.group(1)}\s*章", t):
                    return True
                if mnum.group(2) and mnum.group(2)[:4] in t:
                    return not re.search(r"第\s*\d+\s*章", t)
                return False
            return "零基础" in t
        cands = [bm + d for d in (0, -1, 1) if 0 <= bm + d < hi_all and is_title(bm + d)]
        refined.append(cands[0] if cands else bm)
    for i, u in enumerate(chap_units):
        if refined[i] is None:
            u["pages_q"] = None
            u["pp_q"] = {}
            continue
        nxt = min([r for r in refined[i + 1:] if r is not None] or [hi_all])
        u["pages_q"] = (refined[i], max(nxt, refined[i] + 1))
        u["pp_q"] = {}
        prev_pg = u["pages_q"][0]                # 题号页码单调推进
        for num in sorted(u["probs"], key=int):
            occ = pages_with(full, rf"(?m)^\s*{num}\s*[.、．]", prev_pg, u["pages_q"][1])
            if occ:
                u["pp_q"][num] = occ[0]
                prev_pg = occ[0]
            else:
                u["pp_q"][num] = None

    # --- 测试卷（每卷：选择/填空/解答 三个题型单元；书内题号全卷连排 1..22，需加偏移） ---
    juan_order = []
    for u in juan_units:
        nm = u["unit"].split("/")[-2]
        if nm not in juan_order:
            juan_order.append(nm)
    for ji, nm in enumerate(juan_order):
        us = [x for x in juan_units if x["unit"].split("/")[-2] == nm]
        if ji >= len(bm_juan):
            for u in us:
                u["pages_q"] = None
                u["pp_q"] = {}
            continue
        lo = bm_juan[ji]
        hi = bm_juan[ji + 1] if ji + 1 < len(bm_juan) else hi_all
        # 卷首页精修：±1 页内同时含卷名和行首"1."
        cands = [lo + d for d in (0, -1, 1) if 0 <= lo + d < hi_all
                 and nm in full.get(lo + d, "") and re.search(r"(?m)^\s*1\s*[.、．]", full.get(lo + d, ""))]
        lo = cands[0] if cands else lo
        cursor = lo
        for u in us:
            u["pages_q"] = (lo, hi)
            u["pp_q"] = {}
            for num in sorted(u["probs"], key=int):
                # md 题号即书内连排题号（填空=11-16、解答=17-22），单游标单调推进
                occ = pages_with(full, rf"(?m)^\s*{num}\s*[.、．]", cursor, hi)
                if occ:
                    u["pp_q"][num] = occ[0]
                    cursor = occ[0]
                else:
                    u["pp_q"][num] = None
    return units

def locate_1000a(book, units, full):
    """解析册：章标题页=范围内同时含'第N章'与章名片段的首页；题页=【答案】序列。
    零基础：标题+行首"1."定起点。测试卷：先定卷首页，卷内【答案】序列按 md 各题型题数顺序切片。"""
    prev = 0
    juan_units = []
    for u in units:
        chap = u["unit"].split("/")[-1]          # 第N章 xxx / 零基础 / 一、选择题…
        if "测试卷" in u["unit"]:
            u["pages_a"] = None                  # 占位，后面统一按卷处理
            u["pp_a"] = {}
            juan_units.append(u)
            continue
        mnum = re.match(r"第(\d+)章\s*(.*)", chap)
        if not mnum:
            if "零基础" in chap:
                occ = [p for p in pages_with(full, "零基础", prev)
                       if re.search(r"(?m)^\s*1\s*[.、．]", full[p])]
                if not occ:
                    occ = pages_with(full, "零基础", prev)
                if occ:
                    u["pages_a"] = (occ[0], None)
                    prev = occ[0] + 1
                else:
                    u["pages_a"] = None
                    u["pp_a"] = {}
                    V.log(f"[t3math:{book}] ⚠ 未定位 {u['unit']}")
            else:
                u["pages_a"] = None
                u["pp_a"] = {}
            continue
        num, name = mnum.group(1), mnum.group(2)
        pat = f"第\\s*{num}\\s*章"
        if name:
            pat += rf"[\s\S]{{0,40}}{re.escape(name[:4])}"
        occ = pages_with(full, pat, prev)
        if not occ:
            occ = pages_with(full, f"第\\s*{num}\\s*章", prev)
        if not occ:
            u["pages_a"] = None
            u["pp_a"] = {}
            V.log(f"[t3math:{book}] ⚠ 未定位 {u['unit']}")
            continue
        a0 = occ[0]
        u["pages_a"] = (a0, None)   # 终点=下一单元起点，事后补
        prev = a0 + 1
    # --- 测试卷：先定各卷首页（顺序链；卷首页=卷名命中页前后含行首"1."的页），也当普通章边界 ---
    juan_start = {}
    jprev = prev
    for u in juan_units:
        nm = u["unit"].split("/")[-2]            # 测试卷一…
        if nm in juan_start:
            continue
        occ = [p for p in pages_with(full, re.escape(nm), jprev)
               if re.search(r"【答案】", full[p])]
        if not occ:
            occ = pages_with(full, re.escape(nm), jprev)
        if occ:
            p0 = occ[0]
            one = pages_with(full, r"(?m)^\s*1\s*[.、．]", max(jprev, p0 - 1), p0 + 2)
            juan_start[nm] = one[0] if one else p0
            jprev = juan_start[nm] + 1
        else:
            juan_start[nm] = None
            V.log(f"[t3math:{book}] ⚠ 未定位 {nm}")
    # --- 补终点（普通章/零基础），然后按【答案】序列定每题页 ---
    bounds = [u["pages_a"][0] for u in units if u.get("pages_a")] + \
             [s for s in juan_start.values() if s is not None]
    hi_all = max(full) + 1
    for u in units:
        if not u.get("pages_a"):
            continue
        nxt = [b for b in bounds if b > u["pages_a"][0]]
        u["pages_a"] = (u["pages_a"][0], min(nxt) if nxt else hi_all)
        u["pp_a"] = assign_ans_pages(full, u["pages_a"], u["probs"])
    # --- 测试卷题型：书内题号全卷连排（选择1-10/填空11-16/解答17-22），加偏移+单游标单调推进 ---
    for nm, js in juan_start.items():
        us = [u for u in juan_units if u["unit"].split("/")[-2] == nm]
        if js is None:
            for u in us:
                u["pages_a"] = None
                u["pp_a"] = {}
            continue
        nxt_js = min([s for s in juan_start.values() if s is not None and s > js] or [hi_all])
        n_ans = sum(len(re.findall(r"【答案】", full[p])) for p in pages_with(full, r"【答案】", js, nxt_js))
        need = sum(len(u["probs"]) for u in us)
        if n_ans != need:
            V.log(f"[t3math:{book}] ℹ {nm} 【答案】标记数 {n_ans} vs md题数 {need}（OCR 标记有缺，以题号游标为准）")
        cursor = js
        first_pg, last_pg = None, None
        for u in us:
            u["pp_a"] = {}
            for num in sorted(u["probs"], key=int):
                # md 题号即书内连排题号（填空=11-16、解答=17-22），单游标单调推进
                occ = pages_with(full, rf"(?m)^\s*{num}\s*[.、．]", cursor, nxt_js)
                if occ:
                    u["pp_a"][num] = occ[0]
                    cursor = occ[0]
                    first_pg = occ[0] if first_pg is None else first_pg
                    last_pg = occ[0]
                else:
                    u["pp_a"][num] = None
            u["pages_a"] = (js, nxt_js)   # 卷范围仅供记录；分组按 pp_a 实际页
        V.log(f"[t3math:{book}] {nm}: 答案页 p{(first_pg or js)+1}~p{(last_pg or js)+1}")
    return units

def assign_ans_pages(full, rng, probs):
    """范围内【答案】出现顺序 ≈ 题号顺序，同页多答案展开后逐题对齐。"""
    ans_pages = pages_with(full, r"【答案】", *rng)
    pp = {}
    nums = sorted(probs, key=int)
    if ans_pages:
        seq = []
        for p in ans_pages:
            seq += [p] * len(re.findall(r"【答案】", full[p]))
        for k, num in enumerate(nums):
            pp[num] = seq[k] if k < len(seq) else seq[-1]
    else:
        for num in nums:
            pp[num] = None
    return pp

# ---------- 分组 ----------
def make_chunks(probs, pp, max_pages=MAX_WIN, fallback_rng=None):
    """按题页码分组：窗口 ≤max_pages 页。返回 [(nums, p0, p1)]。
    未定位题：中间的挂上一窗口；开头的挂第一窗口；全部未定位时用 fallback_rng 兜底成一组。"""
    nums = sorted(probs, key=lambda x: int(x.split(".")[-1]))
    chunks, cur_nums, pages, pending = [], [], set(), []
    for n in nums:
        p = pp.get(n)
        if p is None:
            if chunks:
                chunks[-1][0].append(n)
            else:
                pending.append(n)
            continue
        if pages and (max(pages | {p}) - min(pages | {p}) + 1) > max_pages:
            chunks.append((cur_nums, min(pages), max(pages)))
            cur_nums, pages = [], set()
        if not chunks and not cur_nums and pending:
            cur_nums, pending = list(pending), []
        cur_nums.append(n)
        pages.add(p)
    if cur_nums:
        chunks.append((cur_nums, min(pages), max(pages)))
    elif pending and fallback_rng:
        p0 = fallback_rng[0]
        chunks.append((list(pending), p0, min(fallback_rng[1] - 1, p0 + max_pages - 1)))
    return chunks

# ---------- Prompt ----------
def build_prompt(book, unit_name, probs, nums, p0, p1, pass_type):
    plist = "、".join(nums)
    text = "\n\n".join(f"##### {n}\n\n{probs[n]}" for n in nums)
    head = f"""这是考研数学书《{book}》{unit_name} 的{'题目' if pass_type=='Q' else '答案与解析'}的 OCR 文本和对应书页扫描图。
书页按 OCR 全文索引定位（红字标注 PDF 页码），可能有个别页收多或收少，属正常。OCR 文本经过清洗，措辞/标点差异不算问题。你只负责**观察事实**，不要推断原因、不要下结论。

== 本组题的 OCR markdown（<img> 是图片占位符）==
{text[:6000]}
== 结束 ==

本组只有这些题号：{plist}。书页上出现的其他题号的内容**不要报告**。"""
    if pass_type == "Q":
        head += """
对每一个题号逐项观察（true/false，不适用填 null）：
- present: 该题在书页上是否存在（找不到填 false，evidence 留空，note 写"页内未找到"）
- stem_complete: OCR 题干与书页相比是否完整（有头有尾未截断）
- options_complete: 书上有 (A)(B)(C)(D) 选项而 OCR 缺任何一个即 false；非选择题填 null
- figure_ok: 题干提到"如图"时 OCR 是否有 <img> 占位；无图题填 null
- evidence: 引用书页上该题开头一句原文（找不到写空串）
- note: OCR 与书页的具体差异（没有写空串）

严格只输出 JSON 数组（每题一个对象，键名如上，外加 "num"），不要输出其他文字。"""
    else:
        head += """
对每一个题号逐项观察 OCR 中的答案与解析（true/false）：
- present: 该题答案在书页上是否存在（找不到填 false，evidence 留空，note 写"页内未找到"）
- letter_exists: OCR 中能否看到该题的答案字母/答案内容（如【答案】(B)；书上没有字母只有解答过程的填 null）
- analysis_complete: OCR 的解析与书页相比是否完整（被并进上一题/中间断掉=false）
- evidence: 引用书页上该题答案开头一句原文（找不到写空串）
- note: OCR 与书页的具体差异（没有写空串）

严格只输出 JSON 数组（每题一个对象，键名如上，外加 "num"），不要输出其他文字。"""
    return head

# ---------- 主流程 ----------
def run(pass_type, books, dry_run=False, limit=None):
    outdir = os.path.join(V.VLM, "results", "task3" + pass_type.lower())
    os.makedirs(outdir, exist_ok=True)
    for book in books:
        md, pdf = MATH[book]
        full = load_full(book)
        if book.startswith("30讲"):
            units = parse_30jiang(md)
            units = locate_30jiang(book, units, full)
            scope = "q" if pass_type == "Q" else "a"
            items = [(u, u[scope], u[f"pp_{scope}"], u[f"pages_{scope}"]) for u in units]
        elif book == "1000题-试题册":
            if pass_type != "Q":
                continue
            units = split_1000_q(md)
            units = locate_1000q(book, units, full)
            items = [(u, u["probs"], u["pp_q"], u["pages_q"]) for u in units]
        else:
            if pass_type != "A":
                continue
            units = split_1000_a(md)
            units = locate_1000a(book, units, full)
            items = [(u, u["probs"], u["pp_a"], u["pages_a"]) for u in units]
        out_path = os.path.join(outdir, f"{book}.jsonl")
        done = V.load_done(out_path, "uc")
        V.log(f"[t3math{pass_type}] {book}: {len(items)} 单元, 已完成{len(done)}")
        # 展开成 (unit, chunk) 任务
        jobs = []
        for u, probs, pp, rng in items:
            uname = f"第{u['lec']}讲 {u['name']}" if "lec" in u else u["unit"]
            if not probs:
                if not dry_run:
                    V.append_jsonl(out_path, {"book": book, "uc": uname, "sec": uname, "kind": pass_type,
                                              "cat": "SKIP", "note": "无题号"})
                else:
                    print(f"  {book} {uname}: SKIP 无题号")
                continue
            if rng is None:
                if not dry_run:
                    V.append_jsonl(out_path, {"book": book, "uc": uname, "sec": uname, "kind": pass_type,
                                              "cat": "NO_ANCHOR", "n_probs": len(probs)})
                else:
                    print(f"  {book} {uname}: NO_ANCHOR 题{len(probs)}")
                continue
            for ci, (nums, p0, p1) in enumerate(make_chunks(probs, pp, fallback_rng=rng)):
                uc = f"{uname}#{ci}" if ci else uname
                if uc in done:
                    continue
                jobs.append({"uc": uc, "unit": uname, "probs": probs, "nums": nums, "p0": p0, "p1": p1,
                             "n_unlocated": sum(1 for n in probs if pp.get(n) is None)})
        if limit:
            jobs = jobs[:limit]
        if dry_run:
            for j in jobs:
                print(f"  {book} {j['uc']}: 题{len(j['nums'])} 页p{j['p0']+1}~p{j['p1']+1} 未定位题{j['n_unlocated']}")
            V.log(f"[t3math{pass_type}] {book}: dry-run {len(jobs)} 组")
            continue

        def work(j):
            p0, p1 = j["p0"], j["p1"]
            page_nos = list(range(max(0, p0 - 1), p1 + 2))
            imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=book[:2])
            prompt = build_prompt(book, j["unit"], j["probs"], j["nums"], p0, p1, pass_type)
            max_tok = min(12000, max(4000, len(j["nums"]) * 120))
            try:
                text, usage = V.chat(prompt, images=imgs, max_tokens=max_tok,
                                     tag=f"t3m{pass_type}:{book}:{j['uc']}")
                jj = V.parse_json(text)
                if not isinstance(jj, list):
                    jj = []
                for row in jj:
                    if isinstance(row, dict):
                        row.update({"book": book, "sec": j["unit"], "uc": j["uc"], "kind": pass_type})
                        V.append_jsonl(out_path, row)
                V.append_jsonl(out_path, {"book": book, "sec": j["unit"], "uc": j["uc"], "kind": pass_type,
                                          "cat": "META", "n_probs": len(j["nums"]), "n_rows": len(jj),
                                          "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}", "usage": usage,
                                          "raw": text})
            except Exception as e:
                V.append_jsonl(out_path, {"book": book, "sec": j["unit"], "uc": j["uc"], "kind": pass_type,
                                          "cat": "CALL_FAIL", "error": str(e)[:200]})

        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            list(ex.map(work, jobs))
        V.log(f"[t3math{pass_type}] {book}: 本轮跑 {len(jobs)} 组")

if __name__ == "__main__":
    argv = sys.argv[1:]
    limit = None
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    dry = "--dry-run" in argv
    args = [a for a in argv if not a.startswith("--")]
    passes = "QA"
    if args and args[0] in ("Q", "A", "QA"):
        passes = args[0]
        args = args[1:]
    books = args or list(MATH)
    for p in passes:
        run(p, books, dry_run=dry, limit=limit)
