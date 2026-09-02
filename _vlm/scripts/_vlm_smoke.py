# -*- coding: utf-8 -*-
"""冒烟测试：验证 API 连通 + 模型多模态 + JSON 解析。
用 2 张已知图（高数 img_847=附录文字页、img_120=结构图）跑任务1 prompt。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import _vlm_lib as V
from _vlm_task1_images import PROMPT

CASES = [
    ("高数 img_847（应为B/整页书页或文字段落）", "11408/origin/27张宇基础30讲（高数）/imgs/img_847.jpg"),
    ("高数 img_120（应为A 真实插图/结构图）", "11408/origin/27张宇基础30讲（高数）/imgs/img_120.jpg"),
]

for label, path in CASES:
    text, usage = V.chat(PROMPT, images=[path], max_tokens=300, tag=f"smoke:{path[-14:]}")
    j = V.parse_json(text)
    print(f"{label}\n  usage={usage} 解析={j}\n  raw={text[:150]!r}\n")
print("SMOKE OK")
