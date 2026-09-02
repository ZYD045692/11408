
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
for p in [139, 140, 141]:
    t = full.get(p, "")
    has_t = bool(re.search(r"第\s*3\s*章", t))
    has_1 = bool(re.search(r"(?m)^\s*1\s*[.、．]", t))
    print(f"p{p+1}: 含'第3章'={has_t} 含行首'1.'={has_1} | 首80字: {t[:80]}".replace(chr(10), " | "))
