# -*- coding: utf-8 -*-
"""批量启用/禁用笔记中的闪卡（修改 #card ↔ #flashcards）。

默认 SR 插件识别 #flashcards；生成笔记时使用 #card，避免自动涌入复习队列。
想复习某篇/某批笔记时，用本工具把 #card 改成 #flashcards；想暂时移出复习，改回 #card。
"""
import glob
import os
import re
import sys
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTE_DIR = os.path.join(ROOT, "11408", "笔记")


def toggle_in_file(path, to_flash=False, dry=False):
    """把文件中的 #card 或 #flashcards 标签互换。

    只替换独立行上的标签（前面可选空格），不影响行内其他内容。
    to_flash=True: #card -> #flashcards
    to_flash=False: #flashcards -> #card
    """
    text = open(path, encoding="utf-8").read()
    old = "#flashcards" if to_flash else "#card"
    new = "#card" if to_flash else "#flashcards"
    # 要求标签独占一行（或前面只有空白），避免误改行内文字
    pat = re.compile(rf"^(\s*){re.escape(old)}(\s*)$", re.M)
    new_text, n = pat.subn(rf"\1{new}\2", text)
    if n == 0:
        return 0
    if not dry:
        open(path, "w", encoding="utf-8", newline="\n").write(new_text)
    return n


def collect_paths(patterns):
    out = set()
    for p in patterns:
        if os.path.isfile(p):
            out.add(os.path.abspath(p))
            continue
        # 相对路径以笔记根为基准
        if not os.path.isabs(p):
            p = os.path.join(NOTE_DIR, p)
        for f in glob.glob(p, recursive=True):
            if f.endswith(".md"):
                out.add(os.path.abspath(f))
    return sorted(out)


def main():
    parser = argparse.ArgumentParser(
        description="批量切换笔记闪卡标签：#card ↔ #flashcards"
    )
    parser.add_argument(
        "patterns", nargs="+",
        help="文件路径或 glob 模式（相对 11408/笔记/ 或直接绝对路径）"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--on", action="store_true", help="启用复习：#card -> #flashcards")
    group.add_argument("--off", action="store_true", help="禁用复习：#flashcards -> #card")
    parser.add_argument("--dry", action="store_true", help="只报告，不写盘")
    args = parser.parse_args()

    paths = collect_paths(args.patterns)
    if not paths:
        print("未匹配到文件")
        sys.exit(1)

    to_flash = args.on
    changed = total = 0
    for p in paths:
        total += 1
        n = toggle_in_file(p, to_flash=to_flash, dry=args.dry)
        if n:
            tag = "#flashcards" if to_flash else "#card"
            print(f"{'[dry] ' if args.dry else ''}{p}: -> {tag}")
            changed += 1

    action = "启用" if to_flash else "禁用"
    print(f"\n{action}复习：扫描 {total} 个文件，{changed} 个包含标签（dry={args.dry}）")


if __name__ == "__main__":
    main()
