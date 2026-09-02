
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
units = M.locate_1000q("1000题-试题册", units, full)
for u in units:
    if "随机事件" in u["unit"] and u["unit"].startswith("基础篇"):
        nums = sorted(u["probs"], key=int)
        print("unit:", u["unit"], "题数:", len(nums), "题号:", nums)
        print("pages_q:", u["pages_q"])
        for n in nums:
            print("  题", n, "->", u["pp_q"].get(n))
        p0, p1 = u["pages_q"]
        for p in range(p0, min(p1, p0+3)):
            t = full.get(p, "")
            hits = re.findall(r"(?m)^\s*\d+\s*[.、．]", t)
            print(f"--- p{p+1} 行首题号: {hits[:20]}")
