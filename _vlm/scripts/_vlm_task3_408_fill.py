# -*- coding: utf-8 -*-
"""任务3补漏（408 四本）：对照 META.n_probs 与已返回题号，仅对缺失题号重新调用并追加。
幂等。用法: python _vlm_task3_408_fill.py [Q|A|QA] [书名...]"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V
import _vlm_task3_qa as T

def salvage_list(text):
    """parse_json 失败（多为输出截断）时，抢救数组里已完整的对象。"""
    import re as _re
    t = _re.sub(r"^```(json)?|```$", "", text.strip(), flags=_re.M)
    i = t.find("[")
    if i < 0:
        return []
    body = t[i + 1:]
    cut = body.rfind("},")
    if cut < 0:
        cut = body.rfind("}")
    if cut < 0:
        return []
    try:
        return json.loads("[" + body[:cut + 1] + "]")
    except Exception:
        return []

def observed(path):
    out = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if "num" in r and "sec" in r:
                out.setdefault(r["sec"], set()).add(str(r["num"]))
    return out

def run_fill(pass_type, books):
    outdir = os.path.join(V.VLM, "results", "task3" + pass_type.lower())
    for book in books:
        md, pdf = V.BOOKS[book]
        toc, _ = V.pdf_toc(pdf)
        sections = [s for s in V.split_sections(md, "exercise") if s["kind"] == pass_type]
        out_path = os.path.join(outdir, f"{book}.jsonl")
        obs = observed(out_path)
        jobs = []
        for sec in sections:
            probs, pre = V.split_problems(sec["text"])
            pages = V.sec_pages(toc, sec["sec"])
            if not probs or pages is None:
                continue
            missing = {n: t for n, t in probs.items() if str(n) not in obs.get(sec["sec"], set())}
            if missing:
                jobs.append((sec, missing, pre, pages))
        V.log(f"[t3fill408{pass_type}] {book}: 待补 {len(jobs)} 节（{sum(len(j[1]) for j in jobs)} 题）")
        if not jobs:
            continue

        def work(item):
            sec, probs, pre, pages = item
            start, end = pages
            end = end if end is not None else start
            page_nos = list(range(max(0, start - 1), end + 2))
            core = f"p{start+1}~p{end+1}"
            imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=f"{book[:2]}")
            prompt = T.build_prompt(sec, probs, pre, core, pass_type)
            max_tok = min(16000, max(6000, len(probs) * 300))
            try:
                text, usage = V.chat(prompt, images=imgs, max_tokens=max_tok,
                                     tag=f"t3fill{pass_type}:{book}:{sec['sec']}")
                j = V.parse_json(text)
                if not isinstance(j, list):
                    j = salvage_list(text)
                for row in j:
                    if isinstance(row, dict):
                        row.update({"book": book, "sec": sec["sec"], "kind": pass_type, "fill": True})
                        V.append_jsonl(out_path, row)
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "kind": pass_type,
                                          "cat": "META_FILL", "n_probs": len(probs), "n_rows": len(j),
                                          "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}", "usage": usage,
                                          "raw": text})
            except Exception as e:
                V.append_jsonl(out_path, {"book": book, "sec": sec["sec"], "kind": pass_type,
                                          "cat": "CALL_FAIL", "error": str(e)[:200]})

        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            list(ex.map(work, jobs))
        V.log(f"[t3fill408{pass_type}] {book}: 补漏完成")

if __name__ == "__main__":
    args = sys.argv[1:]
    passes = "QA"
    if args and args[0] in ("Q", "A", "QA"):
        passes = args[0]
        args = args[1:]
    books = args or list(V.BOOKS)
    for p in passes:
        run_fill(p, books)
