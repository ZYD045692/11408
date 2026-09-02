
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M
mdq = open(M.MATH["1000题-试题册"][0], encoding="utf-8").read()
i = mdq.find("三、 解答题")
if i < 0: i = mdq.find("解答题")
print("=== md 测试卷一 解答题区域 ===")
print(mdq[i-200:i+500])
