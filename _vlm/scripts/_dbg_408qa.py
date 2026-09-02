
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
import _vlm_lib as V
secs = V.split_sections(V.BOOKS["数据结构"][0], "exercise")
for s in secs[:4]:
    probs, pre = V.split_problems(s["text"])
    print(s["sec"], s["kind"], s["name"][:20], "题数:", len(probs), "题号样本:", list(probs)[:5])
    if len(probs) == 0:
        print("  正文前300字:", s["text"][:300].replace(chr(10), " | "))
