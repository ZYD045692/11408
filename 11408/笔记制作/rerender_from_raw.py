# -*- coding: utf-8 -*-
"""离线重渲染：从 _notes_runtime/raw/ 读取模型原始输出，用当前 parser 重新生成笔记。
不调用 API，只用于 prompt/渲染层修复后刷新已有笔记。"""
import os, sys, glob, re
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT_DIR, "11408", "笔记制作"))

from core.config import cfg, model_tag, ROOT
from core.organizers import ORGANIZERS, TYPES
from core.parsers import PARSERS
from core.parsers.base import already_gen

RAW_DIR = os.path.join(ROOT, "_notes_runtime", "raw")


def raw_files_for_task(task):
    """返回 [(stage, path)]，按文件名/修改时间排序（单阶段在前，chunk/synth 在后）。"""
    sub = task.meta.get("raw_sub", "misc")
    d = os.path.join(RAW_DIR, sub)
    if not os.path.isdir(d):
        return []
    base = task.tag.replace(":", "_").replace("/", "-")
    # 先找完全匹配主阶段文件名
    main_file = os.path.join(d, base + ".md")
    out = []
    if os.path.exists(main_file):
        out.append(("main", main_file))
    # 再找带 stage 后缀的文件（.one, .chunk1, .synth ...）
    stage_files = []
    for f in os.listdir(d):
        if not f.startswith(base + "."):
            continue
        suffix = f[len(base + "."):]
        if suffix.endswith(".md"):
            stage = suffix[:-3]
        else:
            continue
        stage_files.append((stage, os.path.join(d, f)))
    # 按修改时间排序
    stage_files.sort(key=lambda x: os.path.getmtime(x[1]))
    out.extend(stage_files)
    return out


def needs_fix(note_path):
    """判断笔记是否包含字面 \\n 或表格被包在列表项里。"""
    text = open(note_path, encoding="utf-8", errors="replace").read()
    if "\\\\n" in text:
        return True
    # 表格粘在列表项后：- **xxx**：| ... |
    if re.search(r"^-\s+\*\*[^*]+\*\*：\s*\|", text, re.M):
        return True
    return False


def rerender_task(task):
    psr = PARSERS[task.type]
    org = ORGANIZERS[task.type]
    stage_results = []
    files = raw_files_for_task(task)
    if not files:
        return False, "无 raw 文件"
    for stage, path in files:
        raw = open(path, encoding="utf-8", errors="replace").read()
        data = psr.parse(raw)
        stage_results.append((stage, data))
    # 保持原 gen 行不变（避免更新日期），仅修正渲染
    old = open(task.note_path, encoding="utf-8").read()
    m = re.search(r"(?m)^gen:\s*(.+)$", old)
    gen_line = m.group(1).strip() if m else f"{model_tag()}-think"
    content, ncards = psr.render(task, stage_results, gen_line)
    open(task.note_path, "w", encoding="utf-8", newline="\n").write(content)
    return True, f"闪卡{ncards}张"


def main():
    cfg()
    all_mode = "--all" in sys.argv
    todo = []
    for t in sorted(TYPES):
        for task in ORGANIZERS[t].scan():
            if not os.path.exists(task.note_path):
                continue
            if all_mode:
                if already_gen(task.note_path):
                    todo.append(task)
            elif needs_fix(task.note_path):
                todo.append(task)
    print(f"需重渲染笔记：{len(todo)}")
    ok = fail = 0
    for task in todo:
        try:
            success, info = rerender_task(task)
            if success:
                print(f"  ✓ {task.note_path} ({info})")
                ok += 1
            else:
                print(f"  △ {task.note_path}: {info}")
                fail += 1
        except Exception as e:
            print(f"  ✗ {task.note_path}: {e}")
            fail += 1
    print(f"完成：成功 {ok}，失败 {fail}")


if __name__ == "__main__":
    main()
