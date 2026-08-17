# -*- coding: utf-8 -*-
# 分析解析册所有 $$：区分"行内嵌"(误插，需拆开) vs "独立块边界"(真块，保留)
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
md = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
text = open(md, encoding="utf-8").read()
n = len(text)

inline_bb = []   # 行内嵌 $$（前后有内容）
block_bb = []    # 独立块边界 $$（前后空行/行首行尾）
total = 0
i = 0
while i < n:
    if text.startswith("$$", i):
        total += 1
        before = text[max(0,i-1):i]
        after = text[i+2:i+3]
        # 行内嵌：前一个字符不是换行/开头，且后一个字符不是换行/结尾
        prev_is_nl = (i == 0) or before == "\n" or before.isspace() or before == ">"
        next_is_nl = after == "\n" or after == "" or after.isspace()
        if prev_is_nl and next_is_nl:
            block_bb.append(i)      # 独立行 $$（前后空）
        elif prev_is_nl and not next_is_nl:
            block_bb.append(i)      # 行首 $$（块开）
        elif not prev_is_nl and next_is_nl:
            block_bb.append(i)      # 行尾 $$（块闭）
        else:
            inline_bb.append(i)     # 嵌在行内
        i += 2
    else:
        i += 1

print(f"$$ 总数: {total}")
print(f"独立块边界 $$: {len(block_bb)}")
print(f"行内嵌 $$: {len(inline_bb)}")

print("\n--- 行内嵌 $$ 样本(前12个) ---")
for pos in inline_bb[:12]:
    ln = text.count("\n", 0, pos) + 1
    ctx = text[max(0,pos-22):pos+22].replace("\n","⏎")
    print(f"  L{ln}: ...{ctx!r}")
