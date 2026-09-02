
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
for p in range(180, 185):
    t = full.get(p, "")
    hs = re.findall(r"(?m)^\s*\d{1,2}\s*[.、．]", t)
    print(f"=== p{p+1} 行首题号={hs[:16]} | 首100字: {t[:100]}".replace(chr(10), " | "))
