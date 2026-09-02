# -*- coding: utf-8 -*-
"""从 META_FILL 的 raw 档案里抢救数据行（模型写了非法 JSON 转义如 \\arctan 导致解析失败）。
不调用 API：清洗非法反斜杠转义后重新解析，把数据行补进 jsonl（标 fill+recovered）。
幂等：已齐的组自动跳过。用法: python _vlm_task3_recover.py"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M

RES = os.path.join(V.VLM, "results")
# 合法对 \\ 先整体保留；\u 后非4位hex、其它非法转义 → 反斜杠加倍
BAD_ESC = re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')

def _fix_esc(m):
    return m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:]

def sanitize_parse(text):
    t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
    i = t.find("[")
    if i < 0:
        return []
    t = BAD_ESC.sub(_fix_esc, t[i:])
    try:
        return json.loads(t)
    except Exception:
        cut = t.rfind("},")
        if cut < 0:
            return []
        try:
            return json.loads(t[:cut + 1] + "]")
        except Exception:
            return []

def expected_math(book, pass_type):
    """→ {uc: [nums]}（重算分组）"""
    md, pdf = M.MATH[book]
    full = M.load_full(book)
    out = {}
    if book.startswith("30讲"):
        units = M.locate_30jiang(book, M.parse_30jiang(md), full)
        scope = "q" if pass_type == "Q" else "a"
        items = [(u, u[scope], u[f"pp_{scope}"], u[f"pages_{scope}"]) for u in units]
    elif book == "1000题-试题册":
        units = M.locate_1000q(book, M.split_1000_q(md), full)
        items = [(u, u["probs"], u["pp_q"], u["pages_q"]) for u in units]
    else:
        units = M.locate_1000a(book, M.split_1000_a(md), full)
        items = [(u, u["probs"], u["pp_a"], u["pages_a"]) for u in units]
    for u, probs, pp, rng in items:
        uname = f"第{u['lec']}讲 {u['name']}" if "lec" in u else u["unit"]
        if not probs or rng is None:
            continue
        for ci, (nums, p0, p1) in enumerate(M.make_chunks(probs, pp, fallback_rng=rng)):
            uc = f"{uname}#{ci}" if ci else uname
            out[uc] = [str(n) for n in nums]
    return out

def recover(path, expected):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    obs = {}
    for r in rows:
        k = r.get("uc") or r.get("sec")
        if r.get("num") is not None and k:
            obs.setdefault(k, set()).add(str(r["num"]))
    added = 0
    for r in rows:
        if r.get("cat") != "META_FILL" or r.get("n_rows", 0) > 0:
            continue
        k = r.get("uc") or r.get("sec")
        want = [n for n in expected.get(k, []) if n not in obs.get(k, set())]
        if not want:
            continue
        got = salvage = sanitize_parse(str(r.get("raw", "")))
        n0 = 0
        for row in got:
            if isinstance(row, dict) and str(row.get("num")) in want:
                row.update({"book": r["book"], "sec": r.get("sec") or r.get("unit") or k,
                            "kind": r["kind"], "fill": True, "recovered": True})
                if "uc" in r:
                    row["uc"] = k
                V.append_jsonl(path, row)
                obs.setdefault(k, set()).add(str(row["num"]))
                n0 += 1
        added += n0
        print(f"  {r['book']} {k}: 抢救 {n0}/{len(want)}")
    return added

total = 0
for pass_type, book in (("q", "1000题-试题册"), ("a", "1000题-解析册"),
                        ("q", "30讲-高数"), ("a", "30讲-高数"),
                        ("q", "30讲-线代"), ("a", "30讲-线代")):
    path = os.path.join(RES, "task3" + pass_type, f"{book}.jsonl")
    exp = expected_math(book, pass_type.upper())
    total += recover(path, exp)
print(f"合计抢救 {total} 行")
