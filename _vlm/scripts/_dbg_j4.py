
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-解析册")
for p in range(558, 563):
    t = full.get(p, "")
    hs = re.findall(r"(?m)^\s*\d{1,2}\s*[.、．]", t)
    ans = len(re.findall(r"【答案】", t))
    print(f"=== p{p+1} 行首题号={hs[:12]} 【答案】x{ans}")
    print(t[:350].replace(chr(10), " | "))
    print()
