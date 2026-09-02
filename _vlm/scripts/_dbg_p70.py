
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
hits = M.pages_with(full, r"P\(A\|B\)\s*=\s*P\(B\|A\)|满足.*P.*A\|B|事件.*满足")
print("题7特征串候选页:", [p+1 for p in hits])
# 直接找 7. 8. 9. 行首 在 p70 (0-based 69)
for p in [69, 70]:
    t = full.get(p, "")
    heads = re.findall(r"(?m)^\s*\d{1,2}\s*[.、．]", t)
    print(f"p{p+1} 行首题号: {heads[:15]}  首100字: {t[:100]}")
