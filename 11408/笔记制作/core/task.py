# -*- coding: utf-8 -*-
"""任务与作业数据结构。Task=一篇笔记；Job=一次模型请求。"""
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Task:
    type: str                 # "408" | "math_lecture" | "math_section"
    note_path: str            # 目标笔记完整路径
    source_path: str          # 拆分稿原文完整路径
    tag: str                  # 日志 / raw 文件名标签（如 course:sec、book:name）
    title: str = ""           # 笔记标题（可能带 sec 前缀）
    meta: dict = field(default_factory=dict)

@dataclass
class Job:
    prompt: str
    stage: str = "main"            # 阶段名：main / one / c1..cn / synth
    max_tokens: Optional[int] = None   # 缺省 None → pipeline 用配置 max_tokens；organizer 可覆盖
    is_synth: bool = False         # 合成阶段：prompt 含 {CHUNKS} 占位，需先前阶段要点