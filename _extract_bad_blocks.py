# -*- coding: utf-8 -*-
# 提取解析册中所有"含 $ 的 $$ 块"（块吞正文/块内嵌行内$），带行号和上下文
# 用法: python _extract_bad_blocks.py [起始序号] [数量]
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MD = "11408/origin/27张宇1000题数一【解析册】/27张宇1000题数一【解析册】.md"
txt = open(MD, encoding="utf-8").read()
lines = txt.split("\n")

# 找所有 $$...$$ 块（跨行），记录起始行号
blocks = []
for m in re.finditer(r"\$\$([\s\S]*?)\$\$", txt):
    content = m.group(1)
    if "$" in content.replace(r"\$", ""):  # 含 $ 的块
        start_line = txt.count("\n", 0, m.start()) + 1
        blocks.append((start_line, content))

print(f"共 {len(blocks)} 个含$的块")
start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2]) if len(sys.argv) > 2 else 10

for idx in range(start, min(start + count, len(blocks))):
    ln, content = blocks[idx]
    # 取块前后 3 行上下文
    ctx_before = "\n".join(l for l in lines[max(0, ln-4):ln-1])
    ctx_after = "\n".join(l for l in lines[ln + content.count("\n") + 1: ln + content.count("\n") + 4])
    print(f"\n{'='*60}\n[{idx}] 起始L{ln} (块长{len(content)})")
    print(f"  · 前文: {ctx_before.strip()[:80]!r}")
    print(f"  · 块内容头60: {content[:60]!r}")
    print(f"  · 块内容尾60: {content[-60:]!r}")
    print(f"  · 后文: {ctx_after.strip()[:80]!r}")
