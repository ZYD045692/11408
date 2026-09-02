
import sys, os, re, fitz
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M

# 1) 试题册 md 是否真缺测试卷
mdq = open(M.MATH["1000题-试题册"][0], encoding="utf-8").read()
print("试题册 md 含'测试卷'次数:", mdq.count("测试卷"), " 含'综合篇':", mdq.count("综合篇"))
for m in re.finditer(r"(?m)^(#{1,4})\s*(.*测试卷.*)$", mdq):
    print("  试题册md标题:", m.group(1), m.group(2)[:40])

# 2) 解析册 PDF 书签里测试卷/零基础页码
doc = fitz.open(M.MATH["1000题-解析册"][1])
toc = doc.get_toc()
n = doc.page_count
doc.close()
print("\n解析册总页数:", n)
for lvl, t, p in toc:
    if re.search(r"测试卷|零基础|综合篇|基础篇|强化篇", t):
        print(f"  书签 L{lvl} p{p} {t.strip()}")
