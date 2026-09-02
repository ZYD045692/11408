# -*- coding: utf-8 -*-
"""修复队列构建：从 task3q/task3a jsonl 提取去重后的 false 标记项，
附上 origin md 里该题的当前文本 + 书页范围，写 _vlm/repair/queue.json。
纯文本不调 API。用法: python _repair_queue.py"""
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M

OUT_DIR = os.path.join(V.VLM, "repair")
os.makedirs(OUT_DIR, exist_ok=True)
RES = os.path.join(V.VLM, "results")

QFLAGS = ["present", "stem_complete", "options_complete", "subq_complete", "figure_ok"]
AFLAGS = ["present", "letter_exists", "analysis_complete"]

def dedup_flagged(path, flags):
    dd = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("num") is not None:
            dd[(r.get("uc") or r.get("sec"), str(r["num"]))] = r
    return [r for r in dd.values() if any(r.get(f) is False for f in flags)]

queue = []

# ---- 408 四本 ----
for book, (md, pdf) in V.BOOKS.items():
    toc, _ = V.pdf_toc(pdf)
    for pass_type, flags in (("Q", QFLAGS), ("A", AFLAGS)):
        path = os.path.join(RES, "task3" + pass_type.lower(), f"{book}.jsonl")
        flagged = dedup_flagged(path, flags)
        if not flagged:
            continue
        secs = {s["sec"]: s for s in V.split_sections(md, "exercise") if s["kind"] == pass_type}
        for r in flagged:
            sec = secs.get(r["sec"])
            if not sec:
                continue
            probs, _pre = V.split_problems(sec["text"])
            pages = V.sec_pages(toc, r["sec"])
            queue.append({"book": book, "pass": pass_type, "sec": r["sec"], "uc": r["sec"],
                          "num": str(r["num"]),
                          "flags": [f for f in flags if r.get(f) is False],
                          "note": r.get("note", ""), "evidence": r.get("evidence", ""),
                          "md_text": probs.get(str(r["num"]).lstrip("0") or "0", probs.get(str(r["num"]), "")),
                          "pages": list(pages) if pages else None})

# ---- 数学 ----
def math_items(book, pass_type, flags):
    path = os.path.join(RES, "task3" + pass_type.lower(), f"{book}.jsonl")
    flagged = dedup_flagged(path, flags)
    if not flagged:
        return
    md, pdf = M.MATH[book]
    full = M.load_full(book)
    if book.startswith("30讲"):
        units = M.locate_30jiang(book, M.parse_30jiang(md), full)
        scope = "q" if pass_type == "Q" else "a"
        lut = {f"第{u['lec']}讲 {u['name']}": (u[scope], u[f"pp_{scope}"]) for u in units}
    elif book == "1000题-试题册":
        units = M.locate_1000q(book, M.split_1000_q(md), full)
        lut = {u["unit"]: (u["probs"], u["pp_q"]) for u in units}
    else:
        units = M.locate_1000a(book, M.split_1000_a(md), full)
        lut = {u["unit"]: (u["probs"], u["pp_a"]) for u in units}
    for r in flagged:
        uc = r.get("uc") or r.get("sec")
        base_uc = uc.split("#")[0]
        if base_uc not in lut:
            continue
        probs, pp = lut[base_uc]
        num = str(r["num"])
        pg = pp.get(num) or pp.get(num.lstrip("0"))
        if pg is None and pp:   # 该题未定位：借最近已定位邻居题的页码
            def nk(x):
                return tuple(int(p) if p.isdigit() else 0 for p in str(x).split("."))
            ks = sorted(pp, key=nk)
            tgt = nk(num)
            nxt = [k for k in ks if nk(k) >= tgt]
            pg = pp[nxt[0]] if nxt else pp[ks[-1]]
        if pg is None:          # 整章未定位：借 META 记录的分组页范围
            for line in open(path, encoding="utf-8"):
                try:
                    m = json.loads(line)
                except Exception:
                    continue
                if m.get("cat") in ("META", "META_FILL") and (m.get("uc") or m.get("sec")) == uc and m.get("pages"):
                    a1, b1 = m["pages"].split("-")
                    pg = int(a1) - 1    # META pages 是 1-based 渲染区间，取起点
                    break
        pages = [pg - 1, pg + 1] if pg is not None else None
        queue.append({"book": book, "pass": pass_type, "sec": base_uc, "uc": uc, "num": num,
                      "flags": [f for f in flags if r.get(f) is False],
                      "note": r.get("note", ""), "evidence": r.get("evidence", ""),
                      "md_text": probs.get(num, probs.get(num.lstrip("0"), "")),
                      "pages": pages})

math_items("30讲-高数", "Q", QFLAGS); math_items("30讲-高数", "A", AFLAGS)
math_items("30讲-线代", "Q", QFLAGS); math_items("30讲-线代", "A", AFLAGS)
math_items("1000题-试题册", "Q", QFLAGS); math_items("1000题-解析册", "A", AFLAGS)

# ---- task2 块级 ----
t2path = os.path.join(RES, "task2_sections", "数据结构.jsonl")
if os.path.exists(t2path):
    md, pdf = V.BOOKS["数据结构"]
    toc, _ = V.pdf_toc(pdf)
    dd = {}
    for line in open(t2path, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("i") is not None and r.get("in_md") in ("部分", "无"):
                dd[(r.get("sec"), r.get("i"))] = r
    for r in dd.values():
        pages = V.sec_pages(toc, r["sec"])
        queue.append({"book": "数据结构", "pass": "T2", "sec": r["sec"], "uc": r["sec"],
                      "num": f"块{r['i']}", "flags": [r["in_md"]],
                      "note": r.get("note", ""), "evidence": r.get("evidence", ""),
                      "md_text": "", "pages": list(pages) if pages else None,
                      "block_type": r.get("type", "")})

for i, it in enumerate(queue):
    it["rid"] = i + 1
json.dump(queue, open(os.path.join(OUT_DIR, "queue.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

import collections
c = collections.Counter((it["book"], it["pass"]) for it in queue)
for (b, p), n in sorted(c.items()):
    print(f"{b} {p}: {n}")
print("无md_text:", sum(1 for it in queue if not it["md_text"] and it["pass"] != "T2"))
print("无pages:", sum(1 for it in queue if not it["pages"]))
print("total:", len(queue))
