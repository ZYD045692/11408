# -*- coding: utf-8 -*-
"""李良概统 origin → 拆分稿（一章一个 md）。

拆分稿数学目录：
  拆分稿/数学/概统-基础/第N章-章名.md     （源 27李良概统基础）
  拆分稿/数学/概统-强化/第N章-章名.md     （源 27李良概统强化）
frontmatter：type=章, course=数学, book=概统-基础/强化
图片引用改指 origin（3 级相对路径）。
"""
import glob, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ORIGIN = os.path.join(ROOT, "11408", "origin")
SPLIT = os.path.join(ROOT, "11408", "拆分稿", "数学")

BOOKS = {
    "概统-基础": "27李良概统基础",
    "概统-强化": "27李良概统强化",
}

CHAPTER_NO = {
    "第一章": 1, "第二章": 2, "第三章": 3, "第四章": 4,
    "第五章": 5, "第六章": 6, "第七章": 7,
}

def main():
    for book, odir in BOOKS.items():
        src_dir = os.path.join(ORIGIN, odir)
        out_dir = os.path.join(SPLIT, book)
        os.makedirs(out_dir, exist_ok=True)
        for md in sorted(glob.glob(os.path.join(src_dir, "*.md"))):
            fname = os.path.basename(md)            # 第一章-随机事件和概率.md
            ch_name = fname.split("-", 1)[0]         # 第一章
            ch_title = os.path.splitext(fname)[0]    # 第一章-随机事件和概率
            body = open(md, encoding="utf-8").read().strip()
            # 图片引用：imgs/xxx → ../../../origin/<odir>/imgs/xxx
            def repl(m):
                return m.group(0).replace("imgs/", "../../../origin/%s/imgs/" % odir)
            body = re.sub(r'src="[^"]*imgs/[^"]+"', repl, body)
            fm = ("---\n"
                  "type: 章\n"
                  "course: 数学\n"
                  "book: %s\n"
                  "chapter_no: %d\n"
                  "tags:\n"
                  "  - 考研数学\n"
                  "  - 概率论与数理统计\n"
                  "chapter_title: %s\n"
                  "---\n\n"
                  % (book, CHAPTER_NO[ch_name], ch_title))
            out = os.path.join(out_dir, fname)
            with open(out, "w", encoding="utf-8", newline="\n") as f:
                f.write(fm + body + "\n")
            print("✓ %s" % out.replace(ROOT, ""))

if __name__ == "__main__":
    main()