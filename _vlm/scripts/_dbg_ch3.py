
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
units = M.locate_1000q("1000题-试题册", units, full)
for u in units:
    if u["unit"] in ("强化篇/第3章 矩阵运算", "基础篇/第9章 一元函数积分学的计算"):
        nums = sorted(u["probs"], key=int)
        loc = {n: u["pp_q"].get(n) for n in nums}
        print("==", u["unit"], "范围", u["pages_q"], "题数", len(nums))
        print("  定位:", {n: (p+1 if p is not None else None) for n, p in loc.items()})
        p0, p1 = u["pages_q"]
        for p in range(p0, min(p1, p0+2)):
            t = full.get(p, "")
            print(f"  --- p{p+1} 前300字: {t[:300]}".replace(chr(10), " | "))
