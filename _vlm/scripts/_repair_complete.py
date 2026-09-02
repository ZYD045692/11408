# -*- coding: utf-8 -*-
"""完整解析补提取：对"新内容短于原文/疑似截断"的 real 项，单题重调 VLM 要完整全文。
输出 _vlm/repair/complete.jsonl（按 rid 续跑）。用法: python _repair_complete.py [--limit N]"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V
import _vlm_task3_math as M

OUT_DIR = os.path.join(V.VLM, "repair")
COMPLETE = os.path.join(OUT_DIR, "complete.jsonl")
BAD_ESC = re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')

def parse_one(text):
    t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
    i = t.find("{")
    if i < 0:
        return None
    t = BAD_ESC.sub(lambda m: m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:], t[i:])
    try:
        return json.loads(t)
    except Exception:
        cut = t.rfind('",')
        if cut > 0:
            try:
                return json.loads(t[:cut] + '"}')
            except Exception:
                pass
    # 截断挽救：content 是最后一个字段且被 token 上限切断 → 手工提取字符串
    m = re.search(r'"content"\s*:\s*"(.*)', t, flags=re.S)
    if m:
        body = m.group(1)
        body = re.sub(r"\s*```\s*$", "", body)
        body = body.rstrip()
        if body.endswith('"'):
            body = body[:-1]
        if len(body) >= 80:
            try:
                content = json.loads('"' + body.replace('"', '\\"') + '"') if False else \
                          body.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
            except Exception:
                return None
            mnum = re.search(r'"num"\s*:\s*"([^"]*)"', t)
            mlet = re.search(r'"letter"\s*:\s*(null|"[^"]*")', t)
            return {"num": mnum.group(1) if mnum else "",
                    "letter": (None if not mlet or mlet.group(1) == "null" else mlet.group(1).strip('"')),
                    "content": content, "truncated": True}
    return None

PROMPT = """这是考研书《{book}》{sec} 的书页扫描图（红字标注 PDF 页码）。
任务：提取**题号 {num}** 的{what}**完整全文**，从第一个字到最后一个字，不得省略中间任何步骤。

当前 markdown 里该题的文本（不完整，仅供参考定位）：
{cur}

要求：
- 数学公式用 $...$ LaTeX；保持书上的推导步骤完整
- **禁止连续 4 个以上下划线**（填空横线用 ___ 表示）
- 严格只输出 JSON 对象：{{"num": "{num}", "letter": "答案字母(选择题才有, 没有则null)", "content": "完整全文"}}"""

def main(limit=None):
    queue = {q["rid"]: q for q in json.load(open(os.path.join(OUT_DIR, "queue.json"), encoding="utf-8"))}
    recs = {}
    for line in open(os.path.join(OUT_DIR, "patches.jsonl"), encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("rid"):
                recs[r["rid"]] = r
    applied = set()
    ap = os.path.join(OUT_DIR, "applied.jsonl")
    if os.path.exists(ap):
        for line in open(ap, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    applied.add(json.loads(line)["rid"])
                except Exception:
                    pass
    done = set()
    if os.path.exists(COMPLETE):
        for line in open(COMPLETE, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    done.add(json.loads(line)["rid"])
                except Exception:
                    pass
    todo = []
    for rid, r in recs.items():
        if r.get("verdict") != "real" or not r.get("fix") or rid in applied or rid in done:
            continue
        ft = r["fix"].get("type")
        if ft not in ("replace_analysis", "fix_analysis", "fix_stem"):
            continue          # 字母识别失败等畸形项留人工
        q = queue.get(rid)
        if not q or not q.get("pages"):
            continue
        todo.append((r, q))
    todo.sort(key=lambda x: x[0]["rid"])
    V.log(f"[complete] 待补提取 {len(todo)} 项")
    if limit:
        todo = todo[:limit]

    def work(rq):
        r, q = rq
        book = r["book"]
        pdf = (V.BOOKS.get(book) or M.MATH[book])[1]
        lo, hi = q["pages"]
        page_nos = list(range(max(0, lo - 1), hi + 2))
        imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag=book[:2])
        what = "答案与解析" if r["pass"] == "A" else "题干（含选项）"
        prompt = PROMPT.replace("{book}", book).replace("{sec}", r["sec"]) \
                       .replace("{num}", r["num"]).replace("{what}", what) \
                       .replace("{cur}", (q["md_text"] or "（稿中缺失）")[:600])
        try:
            text, usage = V.chat(prompt, images=imgs, max_tokens=16000,
                                 tag=f"cmp:{book}:{r['sec']}:{r['num']}")
            j = parse_one(text)
            rec = {"rid": r["rid"], "book": book, "pass": r["pass"], "sec": r["sec"], "uc": r["uc"],
                   "num": r["num"], "usage": usage, "raw": text}
            if j and j.get("content"):
                rec.update({"letter": j.get("letter"), "content": str(j["content"])})
                if j.get("truncated"):
                    rec["truncated"] = True
            else:
                rec["content"] = ""
            V.append_jsonl(COMPLETE, rec)
        except Exception as e:
            V.append_jsonl(COMPLETE, {"rid": r["rid"], "book": book, "pass": r["pass"], "sec": r["sec"],
                                      "uc": r["uc"], "num": r["num"], "content": "", "error": str(e)[:200]})

    with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
        list(ex.map(work, todo))
    V.log("[complete] 完成")

if __name__ == "__main__":
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    main(limit)
