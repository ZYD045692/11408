# -*- coding: utf-8 -*-
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V

path = os.path.join(V.VLM, "results", "task3q", "1000题-试题册.jsonl")
rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
mf = [r for r in rows if r.get("cat") == "META_FILL" and "第13章" in str(r.get("uc"))][0]
raw = str(mf["raw"])
BAD_ESC = re.compile(r'(\\\\)|\\u(?![0-9a-fA-F]{4})|\\(?![\\"/bfnrtu])')
t = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.M)
i = t.find("[")
t2 = BAD_ESC.sub(lambda m: m.group(1) if m.group(1) else "\\\\" + m.group(0)[1:], t[i:])
try:
    j = json.loads(t2)
    print("解析成功:", len(j), "行, 首行num=", j[0].get("num"))
except Exception as e:
    print("解析失败:", e)
    # 定位出错位置附近文本
    m = re.search(r"\d+", str(e))
    if m and hasattr(e, "pos"):
        print("出错附近:", t2[max(0, e.pos - 80):e.pos + 80])
