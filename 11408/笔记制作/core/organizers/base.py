# -*- coding: utf-8 -*-
"""Organizer 基类 + 公共工具（stub 幂等写入、图片降噪、原文切块、frontmatter 读取）。"""
import os, re

def ensure_stub(path, content):
    """幂等写 stub：文件已存在绝不覆盖（用户笔记优先）。返回是否新建。"""
    if os.path.exists(path):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8", newline="\n").write(content)
    return True

def denoise(src):
    """OCR 图片标签降噪 + 把易引发模型幻觉的 LaTeX 命令换成更常见的同义命令。"""
    src = re.sub(r"<img[^>]*>", "[图]", src)
    # 397B 等模型对 \Leftrightarrow 识别不稳定，常生成 \boldsymbol{x}/\beta 等乱码，换成熟悉的 \iff
    src = src.replace(r"\Leftrightarrow", r"\iff")
    return src

def read_fm(path):
    """读 frontmatter dict（简单字段够用）"""
    t = open(path, encoding="utf-8").read()
    m = re.match(r"(?s)^---\s*\n(.*?)\n---", t)
    fm = {}
    if m:
        for line in m.group(1).split("\n"):
            kv = re.match(r"^(\w+):\s*(.*)$", line)
            if kv:
                fm[kv.group(1)] = kv.group(2).strip().strip('"')
    return fm

def chunk_source(src, max_src):
    """按标题切块，打包成 ≤max_src 的组（长原文分块喂模型）"""
    parts = re.split(r"(?m)^(#{2,5} .+)$", src)
    units = []
    if parts[0].strip():
        units.append(parts[0])
    for i in range(1, len(parts) - 1, 2):
        units.append(parts[i] + parts[i + 1])
    groups, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) > max_src:
            groups.append(cur); cur = u
        else:
            cur += u
    if cur.strip():
        groups.append(cur)
    return groups

def truncated(src, max_src):
    if len(src) > max_src:
        return src[:max_src] + "\n（后文略）"
    return src


class Organizer:
    """整理工具：扫描拆分稿产任务、决定该发什么提示词。不直接调模型。"""

    type = ""

    def scan(self, only=None):
        """返回 [Task]；目标笔记缺失时顺带幂等写 stub。
        only：课程（如 数据结构）/ 书（如 30讲-高数）/ 讲名（如 第2讲-矩阵）过滤。"""
        raise NotImplementedError

    def jobs(self, task):
        """返回按序执行的 [Job]。复杂笔记（长讲）会返回多个阶段。"""
        raise NotImplementedError
