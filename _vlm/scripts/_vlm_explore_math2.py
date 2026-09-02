# -*- coding: utf-8 -*-
"""探查2：数学 PDF 文本层 / 试题册书签 / 高数习题节样本 / md 页码标记。"""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import fitz

print("## PDF 文本层测试（第20页提取文字长度）")
for f in ["27张宇基础30讲（高数）.pdf", "27张宇基础30讲线代.pdf",
          "27张宇1000题数一【试题册】.pdf", "27张宇1000题数一【解析册】.pdf"]:
    doc = fitz.open(os.path.join("11408/pdf", f))
    t = doc[19].get_text().strip()
    print(f"  {f}: 文本层 {len(t)} 字符 | 样例: {t[:60]!r}")
    doc.close()

print("\n## 试题册全部书签")
doc = fitz.open("11408/pdf/27张宇1000题数一【试题册】.pdf")
for lvl, title, pg in doc.get_toc():
    print(f"  {'  '*(lvl-1)}{title} -> p{pg}")
doc.close()

print("\n## 高数 md 页码/锚点标记检查")
text = open("11408/origin/27张宇基础30讲（高数）/27张宇基础30讲（高数）.md", encoding="utf-8").read()
for pat in [r"<!--.*?-->", r"\[页\s*\d+\]", r"第\s*\d+\s*页", r"p\d{1,3}\b"]:
    m = re.findall(pat, text)
    print(f"  {pat}: {len(m)} {m[:5]}")

print("\n## 高数 第1讲 基础习题精练 节内容样本")
i = text.find("基础习题精练")
print(text[i:i+1500])
