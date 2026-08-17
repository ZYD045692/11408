# -*- coding: utf-8 -*-
# 用法: python _show_inline_bb.py <md路径>  输出行内嵌 $$ 上下文
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
md = sys.argv[1]
text = open(md, encoding="utf-8").read()
n = len(text)
i = 0
hits = []
while i < n:
    if text.startswith("$$", i):
        before = text[max(0,i-1):i]
        after = text[i+2:i+3]
        prev_is_nl = (i == 0) or before == "\n" or before.isspace() or before == ">"
        next_is_nl = after == "\n" or after == "" or after.isspace()
        if not prev_is_nl and not next_is_nl:
            hits.append(i)
        i += 2
    else:
        i += 1
print(f"行内嵌 $$ 共 {len(hits)} 个\n")
for idx, pos in enumerate(hits):
    ln = text.count("\n", 0, pos) + 1
    before = text[max(0,pos-45):pos].replace("\n","⏎")
    after = text[pos+2:pos+45].replace("\n","⏎")
    print(f"[{idx}] L{ln}")
    print(f"  前: ...{before}")
    print(f"  $$ →  后: {after}...")
    print()
