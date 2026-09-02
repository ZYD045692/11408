# -*- coding: utf-8 -*-
"""task1 新提示词校准：对截图中暴露的问题图逐一验证期望分类。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _vlm_lib as V
from _vlm_task1_images import PROMPT, SUBJECT, IMG_BOOKS

CASES = [   # (书, 图, 期望cat, 说明)
    ("操作系统", "img_11.jpg",  "D", "感叹号三角警示标志"),
    ("操作系统", "img_14.jpg",  "A", "OS 层次结构示意图"),
    ("操作系统", "img_15.jpg",  "A", "操作系统发展史流程图"),
    ("30讲-高数", "img_128.jpg", "B", "0/1 数字表格(矩阵?)"),
    ("30讲-高数", "img_217.jpg", "A", "椭圆与x轴相切坐标图"),
    ("30讲-高数", "img_219.jpg", "D", "蓝色笔和纸张图标"),
    ("30讲-高数", "img_220.jpg", "D", "小人搬薯条二维码插画"),
    ("30讲-高数", "img_221.jpg", "D", "蓝色书本装饰插图"),
    ("30讲-高数", "img_222.jpg", "A", "中值定理思维导图"),
]

ok = 0
for book, img, expect, note in CASES:
    p = os.path.join(IMG_BOOKS[book], img)
    if not os.path.exists(p):
        print(f"[缺图] {book}/{img}"); continue
    text, _ = V.chat(PROMPT.format(book=book, subject=SUBJECT[book]),
                     images=[p], max_tokens=300, tag=f"cal:{book}:{img}")
    j = V.parse_json(text) or {}
    got = j.get("cat", "PARSE_FAIL")
    mark = "OK " if got == expect else "XX "
    ok += got == expect
    print(f"{mark}{book}/{img} 期望{expect} 实得{got}/{j.get('sub')} | {note} | {j.get('desc','')[:50]}")
print(f"== {ok}/{len(CASES)} 符合期望 ==")
