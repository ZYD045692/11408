# -*- coding: utf-8 -*-
"""笔记生成统一入口（替换旧 _fill_notes.py / _math_sections.py）。

用法：
  python 11408/笔记制作/make_notes.py --list         # 只列任务（不调 API）
  python 11408/笔记制作/make_notes.py --pilot        # 试点（408×2 + 数学讲×1 + 小节×1）
  python 11408/笔记制作/make_notes.py --all          # 全量（默认）
  python 11408/笔记制作/make_notes.py --type 408     # 只跑某类型
  python 11408/笔记制作/make_notes.py 数据结构        # 按课程/书/讲名过滤
  python 11408/笔记制作/make_notes.py --force 数据结构  # 忽略 gen 强制重跑

说明：模型/限速/线程等见同目录 notes_config.json；api key 从 _vlm/.env 读。
"""
import io, os, sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(ROOT_DIR, "core", "pipeline.py")):
    # Windows 中文路径下 __file__ 乱码时回退 cwd
    ROOT_DIR = os.getcwd()
if sys.stdout is not None and hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ROOT_DIR)

from core.pipeline import main

if __name__ == "__main__":
    sys.exit(main())