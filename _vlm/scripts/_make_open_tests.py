# -*- coding: utf-8 -*-
"""生成打开失败的二分定位测试文件（最小样本：1000题-解析册.md，8行表格）"""
import os, re
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context")
src = open(os.path.join(BASE, "1000题-解析册.md"), encoding="utf-8").read()
BS = chr(92)

def w(name, text):
    open(os.path.join(BASE, name), "w", encoding="utf-8", newline="\n").write(text)
    print("写出", name)

# t1: 原样副本（排除文件名玄学）
w("_t1_原样副本.md", src)
# t2: 去掉整个表格（表头+说明保留，数据行转为纯文本列表）
lines = src.split("\n")
no_table = [l for l in lines if not l.startswith("|")]
rows = [l for l in lines if l.startswith("|")][2:]  # 跳表头/分隔线
no_table += ["", "## 行内容（纯文本）"] + ["- " + r.replace("|", " / ")[:200] for r in rows]
w("_t2_无表格.md", "\n".join(no_table))
# t3: 去掉嵌入图 ![[...]]
w("_t3_无嵌入图.md", re.sub(r"!\[\[[^\]]*\]\]", "[图]", src))
# t4: 去掉转义竖线 \|（全部换成 /）
w("_t4_无转义竖线.md", src.replace(BS + "|", "/"))
# t5: 仅保留表头+第1条数据行
keep = [l for l in lines if not l.startswith("|")]
tbl = [l for l in lines if l.startswith("|")]
w("_t5_仅1行表格.md", "\n".join(keep[:3] + tbl[:3]))
# t6: 去数学 $...$
w("_t6_去数学符号.md", src.replace("$", ""))
print("完成")
