
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
units = M.locate_1000q("1000题-试题册", units, full)
for u in units:
    if "测试卷一" in u["unit"]:
        nums = sorted(u["probs"], key=int)
        print(u["unit"], "pages_q:", u["pages_q"], "md题数:", len(nums))
        print("  pp_q:", {n: (p+1 if p is not None else None) for n in nums for p in [u["pp_q"].get(n)]})
