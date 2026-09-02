# -*- coding: utf-8 -*-
"""对比 task4 报告中 打不开/正常 文件的内容特征差异"""
import glob, os
BS = chr(92)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "task4_images_context"))
bad = {"30讲-高数.md", "操作系统.md", "1000题-解析册.md"}
feats = ["<div", "<img", "<br", "![[", "$", BS + "(", BS + "[", "<!--", "data:", "http", "[图片", "```", "|" + BS]
for fn in sorted(glob.glob("*.md")):
    t = open(fn, encoding="utf-8").read()
    tag = "打不开" if fn in bad else "正常  "
    c = {f: t.count(f) for f in feats}
    c = {k: v for k, v in c.items() if v}
    # 缩略图引用的文件是否存在
    import re
    embeds = re.findall(r"!\[\[([^\]|]+)", t)
    missing = [e for e in embeds if not os.path.exists(os.path.join("..", "..", "..", e))]
    print(tag, fn, c, "嵌入图缺失:", len(missing), missing[:3])
