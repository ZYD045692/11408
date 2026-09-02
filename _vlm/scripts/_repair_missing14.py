# -*- coding: utf-8 -*-
"""1000题 14 道缺题补齐：题↔答核查发现试题册 md 丢失、书上存在的题。
从试题册 PDF 对应页提取完整题目（题干+选项），按 `#### k.` 格式生成补丁。
输出 _vlm/repair/missing14.jsonl。用法: python _repair_missing14.py"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concurrent.futures import ThreadPoolExecutor
import _vlm_lib as V
import _vlm_task3_math as M

OUT = os.path.join(V.VLM, "repair", "missing14.jsonl")
BAD_ESC = re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')

MISSING = {
    "基础篇/第5章 一元函数微分学的应用（一） ——几何应用": ["14", "17", "20"],
    "基础篇/第6章 一元函数微分学的应用（二）——中值定理、微分等式与微分不等式": ["10", "18"],
    "基础篇/第8章 一元函数积分学的概念与性质": ["2", "8", "11", "14", "16", "19", "20"],
    "基础篇/第9章 一元函数积分学的计算": ["32"],
    "强化篇/第9章 参数估计与假设检验": ["17"],
}

PROMPT = """这是考研数学书《1000题-试题册》{unit} 的书页扫描图（红字标注 PDF 页码）。
这份书的 OCR markdown 里**丢失了题号 {nums} 的题目**（书上存在，前后题都在稿里，唯独这些题丢了）。
请从书页上找到这些题，逐题完整提取为 markdown，格式严格如下（参考本书其它题的排版）：

#### 题号.

题干文字（数学公式用 $...$ LaTeX 行内格式）

(A) 选项内容(B) 选项内容(C) 选项内容(D) 选项内容

要求：
- 选择题 4 个选项齐全，连成一行、选项间不空行（与本书格式一致）；填空/解答题无选项则不写选项行
- 题干完整（含"如图"等提示语）；公式从书页精确转写
- **禁止连续 4 个以上下划线**（填空横线用 ___ 表示）
- 严格只输出 JSON 数组：[{{"num": "题号", "content": "#### 题号.\\n\\n题干\\n\\n选项行", "page": 题所在PDF页码, "confident": true/false}}]
- 某一题在给出的书页上找不到时，该题 confident 填 false，content 填空串"""

def main():
    book = "1000题-试题册"
    md, pdf = M.MATH[book]
    full = M.load_full(book)
    units = M.locate_1000q(book, M.split_1000_q(md), full)
    lut = {u["unit"]: u for u in units}
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    if r.get("content"):
                        done.add((r["unit"], str(r["num"])))
                except Exception:
                    pass
    jobs = []
    for unit, nums in MISSING.items():
        u = lut.get(unit)
        if not u:
            V.log(f"[missing14] 单元未找到: {unit}")
            continue
        pp = u["pp_q"]
        have = sorted((int(k), v) for k, v in pp.items() if str(k).isdigit() and v is not None)
        for num in nums:
            if (unit, num) in done:
                continue
            n = int(num)
            prev = max(((k, v) for k, v in have if k < n), default=None)
            nxt = min(((k, v) for k, v in have if k > n), default=None)
            lo = (prev[1] if prev else (have[0][1] if have else 0)) - 1
            hi = (nxt[1] if nxt else (have[-1][1] if have else 0)) + 1
            jobs.append({"unit": unit, "num": num, "lo": max(0, lo), "hi": hi})
    V.log(f"[missing14] 待提取 {len(jobs)} 题")

    def work(j):
        page_nos = list(range(j["lo"], j["hi"] + 1))
        imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", "1000题-试题册"), tag="试题")
        prompt = PROMPT.replace("{unit}", j["unit"]).replace("{nums}", j["num"])
        try:
            text, usage = V.chat(prompt, images=imgs, max_tokens=4000,
                                 tag=f"m14:{j['unit']}:{j['num']}")
            t = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
            i = t.find("[")
            arr = []
            if i >= 0:
                tt = BAD_ESC.sub(lambda m: m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:], t[i:])
                try:
                    arr = json.loads(tt)
                except Exception:
                    cut = tt.rfind("},")
                    if cut > 0:
                        try:
                            arr = json.loads(tt[:cut + 1] + "]")
                        except Exception:
                            pass
            got = [r for r in arr if isinstance(r, dict) and str(r.get("num")) == j["num"]]
            rec = got[0] if got else {"num": j["num"], "content": "", "confident": False}
            rec.update({"unit": j["unit"], "pages": f"{j['lo']+1}-{j['hi']+1}", "raw": text})
            V.append_jsonl(OUT, rec)
        except Exception as e:
            V.append_jsonl(OUT, {"unit": j["unit"], "num": j["num"], "content": "",
                                 "confident": False, "error": str(e)[:200]})

    with ThreadPoolExecutor(V.cfg()["threads"]) as ex:
        list(ex.map(work, jobs))
    V.log("[missing14] 完成")

if __name__ == "__main__":
    main()
