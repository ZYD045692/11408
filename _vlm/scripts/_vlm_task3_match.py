# -*- coding: utf-8 -*-
"""任务3补充：题↔答 对应核查（纯文本，不调 API）。
对 8 本书逐一比对"题目集合"与"答案集合"：
  408 四本: 同一小节号 X.Y.Z 的 试题精选(Q) ↔ 答案与解析(A)
  30讲 两本: 同一讲内 ####习题(q) ↔ ####解答(a)，题号 N.M
  1000题:   试题册(篇/章) ↔ 解析册(篇/科目/章)，章名模糊配对 + 题号集合
输出: _vlm/results/task3_match/<书>.md（每单元一行：Q数/A数/缺答/缺题）+ 同名 .jsonl
用法: python _vlm_task3_match.py"""
import os, re, json, sys, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M

OUT = os.path.join(V.VLM, "results", "task3_match")
os.makedirs(OUT, exist_ok=True)

def nums_408(md_path):
    """→ {'X.Y': {'Q': set, 'A': set}}。Q=X.Y.k 试题精选 / A=X.Y.m 答案与解析，同属一节 X.Y。"""
    secs = V.split_sections(md_path, "exercise")
    out = {}
    for s in secs:
        probs, _pre = V.split_problems(s["text"])
        parent = s["sec"].rsplit(".", 1)[0]
        d = out.setdefault(parent, {"Q": set(), "A": set()})
        d[s["kind"]] |= set(probs.keys())
    return out

def nums_30jiang(md_path):
    """→ {'第N讲 名': {'Q': set, 'A': set}}"""
    out = {}
    for u in M.parse_30jiang(md_path):
        out[f"第{u['lec']}讲 {u['name']}"] = {"Q": set(u["q"]), "A": set(u["a"])}
    return out

def norm_name(s):
    return re.sub(r"[\s（）()、，。——\-—·：:]+", "", s)

def nums_1000():
    """试题册 Q ↔ 解析册 A。→ {'篇/章 (模糊配对)': {'Q': set, 'A': set, 'a_unit': 名}}"""
    qu = M.split_1000_q(M.MATH["1000题-试题册"][0])
    au = M.split_1000_a(M.MATH["1000题-解析册"][0])
    # 候选 A 单元按 篇 分组
    def pian_of(u):
        return u["unit"].split("/")[0]
    a_by_pian = {}
    for a in au:
        a_by_pian.setdefault(pian_of(a), []).append(a)
    out = {}
    for q in qu:
        pian = pian_of(q)
        qtail = norm_name(q["unit"].split("/", 1)[1])
        best, best_r = None, 0.0
        for a in a_by_pian.get(pian, []):
            atail = norm_name(a["unit"].split("/", 1)[1])
            r = difflib.SequenceMatcher(None, qtail, atail).ratio()
            if r > best_r:
                best, best_r = a, r
        key = q["unit"]
        out[key] = {"Q": set(q["probs"]), "A": set(best["probs"]) if best and best_r >= 0.6 else set(),
                    "a_unit": best["unit"] if best else None, "match": round(best_r, 2)}
    return out

def numkey(x):
    return tuple(int(p) if p.isdigit() else 0 for p in str(x).split("."))

def report(book, pairs):
    """pairs: {单元: {'Q': set, 'A': set}} → 写 md + jsonl，返回汇总行"""
    lines = [f"# 题↔答 对应核查 — {book}", "",
             "每行一个单元。缺答=Q有题号而A没有（疑似解析丢失/并进他题）；缺题=反之。空=完全对应", "",
             "| 单元 | Q题数 | A答案数 | 缺答 | 缺题 |", "|---|---|---|---|---|---|"]
    n_q = n_a = 0
    miss_a_all, miss_q_all = [], []
    jl = []
    for unit, d in pairs.items():
        qs, as_ = d["Q"], d["A"]
        miss_a = sorted(qs - as_, key=numkey)   # 有题无答
        miss_q = sorted(as_ - qs, key=numkey)   # 有答无题
        n_q += len(qs); n_a += len(as_)
        miss_a_all += miss_a; miss_q_all += miss_q
        mark = "" if not miss_a and not miss_q else " ⚠"
        extra = f"（A单元: {d['a_unit']} 相似度{d['match']}）" if d.get("a_unit") and d["a_unit"] != unit else ""
        lines.append(f"| {unit}{extra} | {len(qs)} | {len(as_)} | {','.join(miss_a)} | {','.join(miss_q)}{mark} |")
        jl.append({"book": book, "unit": unit, "n_q": len(qs), "n_a": len(as_),
                   "missing_answer": miss_a, "missing_problem": miss_q,
                   **({"a_unit": d["a_unit"], "match": d["match"]} if d.get("a_unit") else {})})
    lines += ["", f"**合计：Q {n_q} 题 / A {n_a} 条；缺答 {len(miss_a_all)} 个、缺题 {len(miss_q_all)} 个**"]
    open(os.path.join(OUT, f"{book}.md"), "w", encoding="utf-8").write("\n".join(lines))
    with open(os.path.join(OUT, f"{book}.jsonl"), "w", encoding="utf-8") as f:
        for r in jl:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return book, n_q, n_a, len(miss_a_all), len(miss_q_all)

def main():
    summary = []
    for book, (md, _pdf) in V.BOOKS.items():
        summary.append(report(book, nums_408(md)))
    for book in ("30讲-高数", "30讲-线代"):
        summary.append(report(book, nums_30jiang(M.MATH[book][0])))
    summary.append(report("1000题(试题册↔解析册)", nums_1000()))
    print(f"{'书':<24} {'Q题':>5} {'A答':>5} {'缺答':>4} {'缺题':>4}")
    for b, nq, na, ma, mq in summary:
        print(f"{b:<24} {nq:>5} {na:>5} {ma:>4} {mq:>4}")

if __name__ == "__main__":
    main()
