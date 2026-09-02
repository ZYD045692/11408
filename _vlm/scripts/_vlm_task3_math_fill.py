# -*- coding: utf-8 -*-
"""任务3补漏（数学四本）：主跑中模型可能漏返回部分题（META.n_rows < n_probs）。
本脚本重算 单元→分组→题号，对照 jsonl 已观察题号，仅对**缺失题号**重新调用并追加。
幂等：补过的题再跑会自动跳过。用法: python _vlm_task3_math_fill.py [Q|A|QA] [书名...]"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V
import _vlm_task3_math as M

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
            if "num" in r and "uc" in r:
                out.setdefault(r["uc"], set()).add(str(r["num"]))
    return out

def run_fill(pass_type, books):
    outdir = os.path.join(V.VLM, "results", "task3" + pass_type.lower())
    for book in books:
        md, pdf = M.MATH[book]
        full = M.load_full(book)
        if book.startswith("30讲"):
            units = M.locate_30jiang(book, M.parse_30jiang(md), full)
            scope = "q" if pass_type == "Q" else "a"
            items = [(u, u[scope], u[f"pp_{scope}"], u[f"pages_{scope}"]) for u in units]
        elif book == "1000题-试题册":
            if pass_type != "Q":
                continue
            units = M.locate_1000q(book, M.split_1000_q(md), full)
            items = [(u, u["probs"], u["pp_q"], u["pages_q"]) for u in units]
        else:
            if pass_type != "A":
                continue
            units = M.locate_1000a(book, M.split_1000_a(md), full)
            items = [(u, u["probs"], u["pp_a"], u["pages_a"]) for u in units]
        out_path = os.path.join(outdir, f"{book}.jsonl")
        obs = observed(out_path)
        jobs = []
        for u, probs, pp, rng in items:
            uname = f"第{u['lec']}讲 {u['name']}" if "lec" in u else u["unit"]
            if not probs or rng is None:
                continue
            for ci, (nums, p0, p1) in enumerate(M.make_chunks(probs, pp, fallback_rng=rng)):
                uc = f"{uname}#{ci}" if ci else uname
                missing = [n for n in nums if str(n) not in obs.get(uc, set())]
                if missing:
                    jobs.append({"uc": uc, "unit": uname, "probs": probs, "nums": missing, "p0": p0, "p1": p1})
        V.log(f"[t3fill{pass_type}] {book}: 待补 {len(jobs)} 组（{sum(len(j['nums']) for j in jobs)} 题）")
        if not jobs:
            continue

        def work(j):
            page_nos = list(range(max(0, j["p0"] - 1), j["p1"] + 2))
            imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=book[:2])
            prompt = M.build_prompt(book, j["unit"], j["probs"], j["nums"], j["p0"], j["p1"], pass_type)
            max_tok = min(16000, max(6000, len(j["nums"]) * 300))
            try:
                text, usage = V.chat(prompt, images=imgs, max_tokens=max_tok,
                                     tag=f"t3fill{pass_type}:{book}:{j['uc']}")
                jj = V.parse_json(text)
                if not isinstance(jj, list):
                    jj = salvage_list(text)
                for row in jj:
                    if isinstance(row, dict):
                        row.update({"book": book, "sec": j["unit"], "uc": j["uc"], "kind": pass_type, "fill": True})
                        V.append_jsonl(out_path, row)
                V.append_jsonl(out_path, {"book": book, "sec": j["unit"], "uc": j["uc"], "kind": pass_type,
                                          "cat": "META_FILL", "n_probs": len(j["nums"]), "n_rows": len(jj),
                                          "pages": f"{page_nos[0]+1}-{page_nos[-1]+1}", "usage": usage,
                                          "raw": text})
            except Exception as e:
                V.append_jsonl(out_path, {"book": book, "sec": j["unit"], "uc": j["uc"], "kind": pass_type,
                                          "cat": "CALL_FAIL", "error": str(e)[:200]})

        with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
            list(ex.map(work, jobs))
        V.log(f"[t3fill{pass_type}] {book}: 补漏完成")

if __name__ == "__main__":
    args = sys.argv[1:]
    passes = "QA"
    if args and args[0] in ("Q", "A", "QA"):
        passes = args[0]
        args = args[1:]
    books = args or list(M.MATH)
    for p in passes:
        run_fill(p, books)
