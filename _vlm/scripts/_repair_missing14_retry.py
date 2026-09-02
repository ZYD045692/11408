# -*- coding: utf-8 -*-
"""补提取 2 道缺题（基础篇第5章题20 / 第9章题32）：加宽页窗重试。"""
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
import _vlm_task3_math as M
from _repair_missing14 import PROMPT, BAD_ESC

book = "1000题-试题册"
md, pdf = M.MATH[book]
OUT = os.path.join(V.VLM, "repair", "missing14.jsonl")

JOBS = [
    {"unit": "基础篇/第5章 一元函数微分学的应用（一） ——几何应用", "num": "20", "lo": 17, "hi": 21},
    {"unit": "基础篇/第9章 一元函数积分学的计算", "num": "32", "lo": 27, "hi": 31},
]
for j in JOBS:
    page_nos = list(range(j["lo"], j["hi"] + 1))
    imgs = V.render_pages(pdf, page_nos, os.path.join(V.VLM, "pages", book), tag="试题")
    prompt = PROMPT.replace("{unit}", j["unit"]).replace("{nums}", j["num"])
    try:
        text, usage = V.chat(prompt, images=imgs, max_tokens=4000, tag=f"m14r:{j['num']}")
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
        rec.update({"unit": j["unit"], "pages": f"{j['lo']+1}-{j['hi']+1}", "raw": text, "retry": True})
        V.append_jsonl(OUT, rec)
        print(f"题{j['num']}: confident={rec.get('confident')} {len(str(rec.get('content','')))}字")
    except Exception as e:
        print(f"题{j['num']}: ERR {e}")
        V.append_jsonl(OUT, {"unit": j["unit"], "num": j["num"], "content": "", "confident": False,
                             "error": str(e)[:200], "retry": True})
