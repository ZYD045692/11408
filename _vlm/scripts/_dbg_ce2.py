
import sys, os, re, fitz
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_task3_math as M

mdq = open(M.MATH["1000题-试题册"][0], encoding="utf-8").read()
i = mdq.find("## 测试卷一")
print("=== 试题册 md 测试卷一片段 ===")
print(mdq[i:i+600])

doc = fitz.open(M.MATH["1000题-解析册"][1])
toc = doc.get_toc()
doc.close()
print("\n解析册书签总数:", len(toc))
for lvl, t, p in toc[:15]:
    print(f"  L{lvl} p{p} {t.strip()[:30]}")

full = M.load_full("1000题-解析册")
print("\n解析册全文索引 测试卷/零基础 命中页(1-based):")
for pat in ["测试卷一", "测试卷二", "测试卷三", "测试卷四", "零基础"]:
    print(" ", pat, "->", [p+1 for p in M.pages_with(full, pat)][:8])
