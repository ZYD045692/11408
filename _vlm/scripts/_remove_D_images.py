# -*- coding: utf-8 -*-
"""把任务4最终判定为 D（非正文）的图片引用从 origin 正文移除。
- 默认 dry-run，--apply 才写盘。
- 每个移除记录到 _vlm/repair/removed_D_images.jsonl（书/图/行号/前后文），可回溯。
- 图片文件本身不动。空出来的行保留为空行，不打乱段落结构。"""
import os, re, json, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, HERE)
from _vlm_task1_images import IMG_BOOKS   # 书 -> imgs 目录

CAT = json.load(open("_vlm/repair/task4_final_cat.json", encoding="utf-8"))
LOG = "_vlm/repair/removed_D_images.jsonl"
IMG_TAG = re.compile(r'<img\s[^>]*src="imgs/(img_\d+\.jpg)"[^>]*>')
APPLY = "--apply" in sys.argv

if APPLY and os.path.exists(LOG):
    os.remove(LOG)
total = 0
for book, d in CAT.items():
    dset = {i for i, c in d.items() if c == "D"}
    if not dset:
        continue
    imgs_dir = IMG_BOOKS[book]
    book_dir = os.path.dirname(imgs_dir)
    md = os.path.join(book_dir, os.path.basename(book_dir) + ".md")
    lines = open(md, encoding="utf-8").read().split("\n")
    found = collections.Counter()
    out_lines = []
    for ln, line in enumerate(lines, 1):
        def repl(m, ln=ln, line=line):
            img = m.group(1)
            if img not in dset:
                return m.group(0)
            found[img] += 1
            rec = {"book": book, "img": img, "line": ln, "tag": m.group(0),
                   "context": line.strip()[:150]}
            if APPLY:
                with open(LOG, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            return ""
        out_lines.append(IMG_TAG.sub(repl, line))
    missing = dset - set(found)
    n_lines_changed = sum(1 for a, b in zip(lines, out_lines) if a != b)
    print(f"{book}: D图={len(dset)} 移除引用={sum(found.values())} 涉及行={n_lines_changed} 未找到引用={sorted(missing) if missing else '无'}")
    total += sum(found.values())
    if APPLY and sum(found.values()):
        open(md, "w", encoding="utf-8", newline="\n").write("\n".join(out_lines))
print("总计移除引用", total, "| 模式:", "APPLY" if APPLY else "dry-run")
