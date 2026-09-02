
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
units = M.locate_1000q("1000题-试题册", units, full)
for u in units:
    if u["unit"] in ("基础篇/第8章 一元函数积分学的概念与性质", "基础篇/第5章 一元函数微分学的应用（一） ——几何应用"):
        p0, p1 = u["pages_q"]
        found = []
        for p in range(p0, p1):
            for mnum in re.findall(r"(?m)^\s*(\d{1,2})\s*[.、．]", full.get(p, "")):
                found.append(int(mnum))
        print(u["unit"], "页", p0+1, "-", p1)
        print("  书上行首题号:", sorted(set(found)))
        print("  md题号:", sorted(u["probs"], key=int))
