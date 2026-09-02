
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
units = M.locate_1000q("1000题-试题册", units, full)
for u in units:
    if u["unit"] == "基础篇/第4章 一元函数微分学的计算":
        nums = sorted(u["probs"], key=int)
        print("范围:", u["pages_q"], "题数:", len(nums))
        print("定位:", {n: (p+1 if p is not None else None) for n in nums for p in [u["pp_q"].get(n)]})
for p in range(13, 18):
    t = full.get(p, "")
    hs = re.findall(r"(?m)^\s*\d{1,2}\s*[.、．]", t)
    a = bool(re.search(r"第\s*4\s*章", t)); b = "一元" in t; c = bool(re.search(r"(?m)^\s*1\s*[.、．]", t))
    print(f"p{p+1}: 第4章={a} 一元={b} 行首1.={c} 行首题号={hs[:14]} | 首50字: {t[:50]}".replace(chr(10), " | "))
