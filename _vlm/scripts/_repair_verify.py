# -*- coding: utf-8 -*-
"""修复核实+提取（第二批 VLM 调用）：对 queue.json 每一项，带书页图二次核实，
排除系统性误报；核实为真则提取可用于补齐的精确内容。
输出 _vlm/repair/patches.jsonl（按 rid 断点续跑）。用法: python _repair_verify.py [--limit N]"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V
import _vlm_task3_math as M

OUT_DIR = os.path.join(V.VLM, "repair")
PATCHES = os.path.join(OUT_DIR, "patches.jsonl")

BAD_ESC = re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')

def parse_salvage(text):
    """清洗非法转义 + 截断抢救 → list"""
    t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
    i = t.find("[")
    if i < 0:
        return []
    t = BAD_ESC.sub(lambda m: m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:], t[i:])
    try:
        j = json.loads(t)
        return j if isinstance(j, list) else []
    except Exception:
        pass
    cut = t.rfind("},")
    if cut < 0:
        return []
    try:
        j = json.loads(t[:cut + 1] + "]")
        return j if isinstance(j, list) else []
    except Exception:
        return []

FLAG_CN = {"present": "题/答案整体缺失", "stem_complete": "题干不完整/被截断",
           "options_complete": "选项缺失", "subq_complete": "子问缺失",
           "figure_ok": "题说'如图'但稿里无图", "letter_exists": "答案字母/答案内容缺失",
           "analysis_complete": "解析不完整（被截断或并入他题）",
           "无": "整个内容块缺失", "部分": "内容块部分缺失"}

PROMPT_HEAD = """这是考研书《{book}》{sec} 的书页扫描图（红字标注 PDF 页码）和对应 OCR markdown 的**复核任务**。
前一位观察者用模型初筛，标记了下列题目/块的可疑缺陷。你的任务：**逐项核实真伪**，真的才提取修正内容。初筛可能有系统性误报，请严格按下面的判定要点复核：

【判定要点】
- **比较方向**：缺陷 = 书页上有而 markdown 里没有/不全。书页上"有"本身不构成缺陷，必须 markdown 里缺才算 real
- 我给的"当前 markdown 全文"若已含完整题干+选项/完整答案解析，直接 false_alarm
- 数学解答题/计算题/证明题**本来就没有"答案字母"**，只要解析/答案内容在就是正常 → false_alarm
- 30讲数学解答的格式是 "(C) 解 ……故选(C)."：开头有 (X) 即字母存在
- 408 答案区格式是 "##### NN" 标题下一行是单独字母（如 "C"）：有字母行即 letter 存在
- OCR 措辞/标点/全半角差异不算问题；书上本来就没有的内容（如无选项的填空题）标 false_alarm
- 只有**书页上确实有而 markdown 里确实没有/确实不全**的，才标 real

【输出格式】严格只输出 JSON 数组，每项一个对象：
- num: 题号（字符串，与我给的一致）
- verdict: "real" 或 "false_alarm"
- reason: 一句话依据（引用书页原文作证）
- fix: verdict 为 real 时给出，否则 null。fix 为对象：
  - type: insert_options（补选项）/ set_letter（补答案字母）/ replace_analysis（补完整解析）/ fix_stem（补完整题干）/ insert_problem（补整题含选项）/ figure（缺图）/ other
  - content: 可直接粘贴进 markdown 的修正内容。数学公式用 $...$ LaTeX；选项每个一行形如 "(A) 内容"；解析给完整全文；缺图时 content 写图的标题/内容描述
  - position_hint: 内容应放的位置说明（如"题干后""##### NN 标题下第一行"）
【硬性要求】content 和 reason 里**禁止连续 4 个以上下划线**（填空横线用 ___ 三个表示）；单条 content 不超过 800 字。

【待核实清单】
"""

def build_prompt(book, sec, items):
    parts = [PROMPT_HEAD.replace("{book}", book).replace("{sec}", sec)]
    for it in items:
        fl = "、".join(FLAG_CN.get(f, f) for f in it["flags"])
        blk = f"--- 题号 {it['num']} | 初筛标记: {fl} | 初筛说明: {it['note'] or '无'}"
        if it["pass"] == "T2":
            blk += f"\n块类型: {it.get('block_type','')} | 初筛证据: {it['evidence'][:100]}"
        else:
            blk += f"\n当前 markdown 全文:\n{it['md_text'][:800] if it['md_text'] else '（markdown 里找不到该题/该编号块——这本身就是缺陷表现）'}"
        parts.append(blk)
    return "\n\n".join(parts)

def batches(queue):
    """按 (book,pass,sec) 分组，再按页跨度/条数切批。"""
    groups = {}
    for it in queue:
        groups.setdefault((it["book"], it["pass"], it["sec"]), []).append(it)
    out = []
    for (book, ps, sec), items in groups.items():
        items.sort(key=lambda x: (x["pages"][0] if x["pages"] else 0, x["num"]))
        cur, lo, hi = [], None, None
        for it in items:
            p0, p1 = it["pages"] if it["pages"] else (lo or 0, hi or 0)
            if cur and (len(cur) >= 8 or (hi is not None and p1 - lo > 10)):
                out.append((book, ps, sec, cur, (lo, hi)))
                cur, lo, hi = [], None, None
            cur.append(it)
            lo = p0 if lo is None else min(lo, p0)
            hi = p1 if hi is None else max(hi, p1)
        if cur:
            out.append((book, ps, sec, cur, (lo, hi)))
    return out

def main(limit=None):
    queue = json.load(open(os.path.join(OUT_DIR, "queue.json"), encoding="utf-8"))
    done = set()
    if os.path.exists(PATCHES):
        for line in open(PATCHES, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    done.add(json.loads(line)["rid"])
                except Exception:
                    pass
    todo = []
    for book, ps, sec, items, span in batches(queue):
        items = [it for it in items if it["rid"] not in done]
        if items:
            todo.append((book, ps, sec, items, span))
    V.log(f"[repair-verify] 待核实 {sum(len(t[3]) for t in todo)} 项 / {len(todo)} 批")
    if limit:
        todo = todo[:limit]

    def work(job):
        book, ps, sec, items, (lo, hi) = job
        pdf = (V.BOOKS.get(book) or M.MATH[book])[1]
        page_nos = list(range(max(0, lo - 1), hi + 2))
        imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=book[:2])
        prompt = build_prompt(book, sec, items)
        try:
            text, usage = V.chat(prompt, images=imgs, max_tokens=12000,
                                 tag=f"verify:{book}:{sec}:{items[0]['num']}")
            j = parse_salvage(text)
            by_num = {str(r.get("num")): r for r in j if isinstance(r, dict)}
            for it in items:
                r = by_num.get(str(it["num"]))
                rec = {"rid": it["rid"], "book": book, "pass": ps, "sec": sec, "uc": it["uc"],
                       "num": str(it["num"]), "flags": it["flags"], "pages": [lo, hi]}
                if r is None:
                    rec.update({"verdict": "UNRESOLVED", "reason": "模型未返回该项"})
                else:
                    rec.update({"verdict": r.get("verdict", "UNRESOLVED"),
                                "reason": str(r.get("reason", ""))[:200],
                                "fix": r.get("fix")})
                V.append_jsonl(PATCHES, rec)
            V.append_jsonl(PATCHES, {"batch_meta": True, "book": book, "sec": sec,
                                     "n_items": len(items), "n_ret": len(j), "usage": usage,
                                     "raw": text})
        except Exception as e:
            for it in items:
                V.append_jsonl(PATCHES, {"rid": it["rid"], "book": book, "pass": ps, "sec": sec,
                                         "uc": it["uc"], "num": str(it["num"]), "flags": it["flags"],
                                         "verdict": "CALL_FAIL", "reason": str(e)[:200]})

    with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
        list(ex.map(work, todo))
    V.log("[repair-verify] 完成")

if __name__ == "__main__":
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    main(limit)
