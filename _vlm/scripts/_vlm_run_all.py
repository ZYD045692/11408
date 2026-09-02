# -*- coding: utf-8 -*-
"""流水线串行驱动（供 pythonw 无窗口运行）：任务1 → 任务3Q → 任务3A → 任务2。
stdout/stderr 重定向到 _vlm/logs/pipeline.log；断点续跑由各任务脚本自带。"""
import sys, os, time

SCRIPTS = os.path.dirname(os.path.abspath(__file__))            # _vlm/scripts
LOG = open(os.path.join(os.path.dirname(SCRIPTS), "logs", "pipeline.log"), "a", encoding="utf-8", buffering=1)
sys.stdout = LOG
sys.stderr = LOG

def mark(msg):
    print(f"\n=== {msg} {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)

mark("PIPELINE START")
try:
    import _vlm_task1_images as t1
    import _vlm_task3_math as t3m
    import _vlm_task3_qa as t3
    import _vlm_task2_sections as t2

    print("--- STAGE task1 (插图鉴定, 8本) ---", flush=True)
    t1.run()
    print("--- STAGE task3-math Q (30讲x2 + 试题册) ---", flush=True)
    t3m.run("Q", list(t3m.MATH))
    print("--- STAGE task3-math A (30讲x2 + 解析册) ---", flush=True)
    t3m.run("A", list(t3m.MATH))
    print("--- STAGE task3Q (408四本) ---", flush=True)
    t3.run("Q")
    print("--- STAGE task3A (408四本) ---", flush=True)
    t3.run("A")
    print("--- STAGE task2 ds (内容节试点) ---", flush=True)
    t2.run()
except Exception:
    import traceback
    traceback.print_exc()
    mark("PIPELINE CRASHED")
    raise
mark("ALL STAGES DONE")
