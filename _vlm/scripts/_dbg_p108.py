
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
for p in range(105, 112):
    t = full.get(p, "")
    a = bool(re.search(r"第\s*10\s*章", t))
    b = "一元" in t
    c = bool(re.search(r"(?m)^\s*1\s*[.、．]", t))
    heads = re.findall(r"(?m)^\s*\d{1,2}\s*[.、．]", t)
    print(f"p{p+1}: 第10章={a} 一元={b} 行首1.={c} 行首题号={heads[:14]} | 首60字: {t[:60]}".replace(chr(10), " | "))
