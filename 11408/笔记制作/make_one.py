# -*- coding: utf-8 -*-
"""单粒度笔记生成工具。

用法：
  python 11408/笔记制作/make_one.py 高数 1.1           # 高数 1.1 小节
  python 11408/笔记制作/make_one.py 高数 第1讲         # 高数第1讲全部小节
  python 11408/笔记制作/make_one.py 高数 1             # 同上（数字等价）
  python 11408/笔记制作/make_one.py 线代 第2讲-矩阵     # 线代第2讲整讲笔记
  python 11408/笔记制作/make_one.py 操作系统 01          # 操作系统 01 章全部考点
  python 11408/笔记制作/make_one.py 数据结构 2.2         # 数据结构 2.2 考点
  python 11408/笔记制作/make_one.py --all               # 全量（同 make_notes.py）

说明：
  - 第一个位置参数是 课程/书/科（如 高数、操作系统、数据结构）
  - 第二个位置参数是 小节号/讲名/章号（如 1.1、第1讲、01）
  - 不指定第二个参数时，生成该课程/书下全部任务
"""
import io, os, re, sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(ROOT_DIR, "core", "pipeline.py")):
    ROOT_DIR = os.getcwd()
if sys.stdout is not None and hasattr(sys.stdout, "buffer") and (sys.stdout.encoding or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ROOT_DIR)

from core.config import cfg
from core.agent import Agent
from core.organizers import ORGANIZERS, TYPES
from core.pipeline import process


def _parse_args(argv):
    all_flag = "--all" in argv
    force = "--force" in argv
    pos = [a for a in argv if not a.startswith("--")]
    return all_flag, force, pos


def _match(task, scope, target):
    """判断 task 是否命中 scope/target 过滤。"""
    t = task.type
    m = task.meta

    if t == "408":
        course = m.get("course", "")
        sec = m.get("sec", "")
        cno = str(m.get("chapter_no", ""))
        # scope 匹配课程
        if scope and scope != course:
            return False
        if not target:
            return True
        # target 可能是 2.2（节）或 01（章号）
        if "." in target:
            return sec == target
        # 无点号：当作章号前缀匹配（如 01 匹配 01-绪论下的所有 sec）
        return sec.startswith(target + ".")

    if t == "math_section":
        sub = m.get("sub", "")
        sec = m.get("sec", "")
        lec_name = m.get("lec_name", "")
        if scope and scope not in (sub, m.get("book", "")):
            return False
        if not target:
            return True
        # target 是 1.1 → 匹配 sec
        if re.match(r"^\d+\.\d+$", target):
            return sec == target
        # target 是 1 或 第1讲 → 匹配讲号
        if re.match(r"^\d+$", target):
            return sec.startswith(target + ".")
        if target.startswith("第"):
            return lec_name.startswith(target)
        return lec_name.startswith(target)

    if t == "math_lecture":
        sub = m.get("sub", "")
        name = m.get("name", "")
        if scope and scope not in (sub, m.get("book", "")):
            return False
        if not target:
            return True
        if re.match(r"^\d+$", target):
            return name.startswith(f"第{target}讲-")
        return name.startswith(target)

    return False


def _collect(scope, target):
    tasks = []
    for ty in sorted(TYPES):
        for t in ORGANIZERS[ty].scan():
            if _match(t, scope, target):
                tasks.append(t)
    return tasks


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    all_flag, force, pos = _parse_args(argv)

    if all_flag:
        from core.pipeline import main as pipeline_main
        return pipeline_main(["--all"] + (["--force"] if force else []))

    scope = pos[0] if len(pos) > 0 else None
    target = pos[1] if len(pos) > 1 else None

    tasks = _collect(scope, target)
    if not tasks:
        print(f"未找到匹配任务: scope={scope or '-'} target={target or '-'}")
        return 1

    # 已生成且非 force 则跳过
    from core.parsers.base import already_gen
    todo = []
    skip = 0
    for t in tasks:
        if already_gen(t.note_path) and not force:
            skip += 1
            continue
        todo.append(t)

    print(f"匹配 {len(tasks)} 个任务，跳过 {skip} 个已生成，待生成 {len(todo)} 个")
    if not todo:
        print("全部已生成，加 --force 可重跑")
        return 0

    c = cfg()
    agent = Agent(c)
    ok_count = fail = 0
    for t in todo:
        try:
            _, ok, ncards, manual = process(agent, t)
            print(f"{'✓' if ok else '△'} {t.tag} 闪卡{ncards}张")
            if ok:
                ok_count += 1
            else:
                fail += 1
        except Exception as e:
            print(f"✗ {t.tag} 异常: {e}")
            fail += 1
    print(f"完成 成功{ok_count} 失败{fail}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
