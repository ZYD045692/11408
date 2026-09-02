
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
full = M.load_full("1000题-试题册")
units = M.split_1000_q(M.MATH["1000题-试题册"][0])
u = [x for x in units if x["unit"].startswith("基础篇/第1章 随机事件")][0]
print("md 题7 正文前80字:", u["probs"]["7"][:80].replace("\n", " "))
print("md 题14 正文前80字:", u["probs"]["14"][:80].replace("\n", " "))
t = full[68]
print("\n=== OCR p69 全文(%d字) ===" % len(t))
print(t)
