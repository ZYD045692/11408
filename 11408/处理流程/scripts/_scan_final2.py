# -*- coding: utf-8 -*-
"""终检3（补盲区）：table/tr/td 收支 / img标签完整性 / 页眉页脚残留 / 公式内裸中文 / 奇怪字符"""
import io, sys, re, glob
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for f in sorted(glob.glob("11408/origin/*/*.md")):
    txt = open(f, encoding="utf-8").read()
    lines = txt.split("\n")
    name = f.split("/")[-2]
    # 1) table/tr/td 收支
    bal = {}
    for t in ("table", "tr", "td", "sup", "span", "b", "p"):
        bal[t] = len(re.findall(r"<%s\b" % t, txt, re.I)) - len(re.findall(r"</%s>" % t, txt, re.I))
    imgbad = []
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"<img\b[^>]*>", l):
            tag = m.group(0)
            if 'src="' not in tag or '">' not in tag and not tag.rstrip().endswith("/>"):
                imgbad.append((i, tag[:50]))
            # 引号闭合检查
            if tag.count('"') % 2 == 1:
                imgbad.append((i, "引号奇数 " + tag[:50]))
    # 2) 页眉/广告残留特征（不覆盖正常词）
    header = []
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if re.search(r"(202[5-7]年|考研全程|微信公众号|扫码关注|加微信|免费资料|关注公众号)", s):
            header.append((i, s[:60]))
    # 3) 公式内裸中文（$...$ 里出现中文且不在 \text{}/\mbox{}内）
    cn_in_math = []
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"\$([^$]+)\$", l):
            body = m.group(1)
            # 去掉 \text{...} / \mbox{...} 内的中文
            cleaned = re.sub(r"\\(text|mbox|textnormal)\{[^}]*\}", "", body)
            if re.search(r"[\u4e00-\u9fff]", cleaned):
                cn_in_math.append((i, cleaned[:60]))
    probs = []
    tagbal = {k: v for k, v in bal.items() if v}
    if tagbal: probs.append("标签失衡 " + str(tagbal))
    if imgbad: probs.append(f"img异常 {len(imgbad)}")
    if header: probs.append(f"页眉/广告特征 {len(header)}")
    if cn_in_math: probs.append(f"公式内裸中文 {len(cn_in_math)}")
    if probs:
        print(f"== {name}")
        for p in probs:
            print(f"  {p}")
        for i, t in (imgbad + header + cn_in_math)[:8]:
            print(f"    L{i}: {t}")
