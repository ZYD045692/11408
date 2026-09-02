
import sys, os, re, fitz
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
doc = fitz.open(M.MATH["1000题-试题册"][1])
toc = doc.get_toc()
doc.close()
hits = [(lvl, t, p) for lvl, t, p in toc if re.search(r"第\d+章|零基础|测试卷", t)]
print("匹配书签数:", len(hits))
for lvl, t, p in hits:
    print(f"  L{lvl} p{p} {t}")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
print("\nmd单元数:", len(units))
for u in units[:8]:
    print("  md:", u["unit"])
