# -*- coding: utf-8 -*-
# 用法: python _find_unmatched.py <md> 定位未配 $/$$
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
md = sys.argv[1]
text = open(md, encoding="utf-8").read()
n = len(text)
in_code = False
in_block = None
in_inline = None
i = 0
starts = []
while i < n:
    if text.startswith("```", i):
        in_code = not in_code
        i += 3
        continue
    if in_code:
        i += 1
        continue
    if text[i] == "\\" and i + 1 < n and text[i+1] == "$":
        i += 2
        continue
    if text[i] == "$":
        if text.startswith("$$", i):
            in_block = None if in_block is not None else i
            i += 2
            continue
        else:
            if in_block is not None:
                pass
            elif in_inline is not None:
                in_inline = None
            else:
                in_inline = i
                starts.append(i)
            i += 1
            continue
    i += 1
print(f"未配 $$ 开头: {in_block is not None}")
if in_block is not None:
    ln = text.count("\n", 0, in_block) + 1
    ctx = text[max(0,in_block-30):in_block+30].replace("\n", "⏎")
    print(f"  未配 $$ 位置 L{ln}: ...{ctx!r}")
print(f"未配 $ 数量: {len(starts)}")
for pos in starts[:10]:
    ln = text.count("\n", 0, pos) + 1
    ctx = text[max(0,pos-20):pos+20].replace("\n", "⏎")
    print(f"  L{ln}: ...{ctx!r}")
