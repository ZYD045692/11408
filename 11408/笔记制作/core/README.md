# core/ — 笔记生成核心

职责分离的四组件 + 入口编排。**每个组件只做自己那一件事**，业务规则不在 agent/parser 里，新增笔记类型不用改它们。

## 模块结构

```
core/
├── config.py          # 配置：notes_config.json + 顶层 _vlm/.env 的 SILICONFLOW_API_KEY（共享密钥）
│                      #   常量：ROOT(vault根) / BASE_SPLIT(拆分稿) / BASE_NOTE(笔记) / RUNTIME(_notes_runtime)
│                      #   helpers: cfg() 惰性单例 / model_tag() / log()（stdout + _notes_runtime/logs/run.log）
├── agent.py           # Agent：只发请求。RateLimiter 滑动窗口 TPM/RPM + settle 真实修正
├── task.py            # Task（一篇笔记）/ Job（一次模型请求）dataclass
├── pipeline.py        # main()：收集→过滤(gen 断点)→线程池→重试→渲染→落盘→汇总/人工清单
├── organizers/        # 整理：scan() 扫拆分稿产 [Task]（缺 stub 幂等建）；jobs() 返回 [Job]
│   ├── __init__.py    #   ORGANIZERS 注册表 {"408", "math_lecture", "math_section"}
│   ├── base.py        #   基类 + ensure_stub / denoise / chunk_source / truncated / read_fm
│   ├── k408.py        #   408 考点：真题年份(zhenti_years) / 前后节(section_siblings) / 习题链接
│   ├── math_lecture.py#   数学讲级：长讲 chunk→synth 两阶段（synth 阶段 prompt 含 {CHUNKS}）
│   └── math_section.py#   数学小节：拆分稿 ### 精讲 @ #### N 切小节，编号 x.y
└── parsers/           # 解析：parse() 容错 JSON → validate() 结构/$配平 → render() 渲染落盘
    ├── __init__.py    #   PARSERS 注册表（与 ORGANIZERS 同 key）
    ├── base.py        #   基类 + extract_json / math_balanced / fmt_cards / fmt_points / fmt_confusions
    │                  #         + preserve_fm / already_gen
    ├── k408.py        #   JSON → 408 模板（一句话/核心要点/易混/真题/关联/闪卡）
    ├── math_lecture.py#   多阶段结果归并：synth 优先，失败退回拼各块要点
    └── math_section.py#   JSON → 小节模板
```

## 一次生成是怎么走的（时序）

```
make_notes.py → core.pipeline.main(argv)
  1. 读 notes_config.json（config.load_config + api key）
  2. collect(): 遍历 ORGANIZERS，调 org.scan(only)，按 --pilot/--type/位置参数过滤
  3. 过滤断点：already_gen(note_path)（frontmatter 有 gen:）且非 --force → 跳过
  4. ThreadPoolExecutor(cfg.threads) 并行 process(task)：
       for job in org.jobs(task):            # 不同 stage 顺序执行
           agent.chat(prompt, json_mode=True) # 限速 acquire → POST → settle → 指数退避重试
           save_raw()                          # 原始输出 → _notes_runtime/raw/{raw_sub}/{tag}.md
           psr.parse → validate → raw_ok($配平)；失败重试一次（带纠错提示）
       psr.render(task, stages, gen_line)     # 保留 frontmatter，写 gen: <model>-think
       写盘 task.note_path
  5. 失败任务 → append_manual() 追加 _notes_runtime/repair/notes_manual.md；汇总 生成/跳过/失败
```

## JSON Schema 约定

- **408 与 math_section** 单请求：`{"one_liner", "points":[name/conclusion/content/exam_tip], "confusions":[title/body], "cards":[q/a]}`
- **math_lecture** 短讲单请求同上；长讲分块（`{"points","cards"}`）→ synth（`{"one_liner","points","confusions"}`，prompt 里 `{CHUNKS}` 由 `org.synth_source(stage_results)` 填充）

## 约定与护栏

- **stub 幂等**：`ensure_stub()` 文件已存在绝不覆盖（用户笔记优先）。
- **断点续跑**：`gen:` 存在即跳过；`--force` 强制重跑。
- **frontmatter 保留**：`preserve_fm()` 只剥旧 `gen:` 换新，其余字段（status/mastery/source…）不动。
- **失败不静默**：保 stub → 记 `_notes_runtime/repair/notes_manual.md`；raw 留档 `_notes_runtime/raw/`；日志 `_notes_runtime/logs/run.log`。
- **限速**：单模型 + 多线程，RPM/TPM 在 `notes_config.json` 的 `models` 注册表（值以用户实测为准）。

## 如何新增一种笔记类型（三步）

> 适用场景：比如以后要出 `习题解析笔记`、`错题本`、`专题笔记`。不需要碰 pipeline / agent / parser 基类。

**第 1 步：写 organizer**，放 `core/organizers/xxx.py`

```python
from .base import Organizer, ensure_stub, denoise, truncated
from ..config import BASE_SPLIT, BASE_NOTE, cfg
from ..task import Task, Job

class XxxOrganizer(Organizer):
    type = "xxx"                             # 与注册表 key、--type 参数一致

    def scan(self, only=None):               # 返回 [Task]；目标笔记缺失时 ensure_stub
        ...
        return [Task(type="xxx", note_path=note, source_path=src, tag="...", meta={...})]

    def jobs(self, task):                    # 返回 [Job]；多阶段按序执行
        return [Job(prompt.format(...), stage="main")]
```

**第 2 步：写 parser**，放 `core/parsers/xxx.py`

```python
class XxxParser(Parser):
    type = "xxx"

    def render(self, task, stages, gen_line):   # 返回 (完整笔记文本, 闪卡张数)
        data = stages[0][1] or {}
        fm = preserve_fm(open(task.note_path, encoding="utf-8").read(), gen_line)
        return "\n".join([...]), ncards
```

复用基类工具：`fmt_points` / `fmt_confusions` / `fmt_cards` / `math_balanced`（基类已接好 validate）。

**第 3 步：注册**，`core/organizers/__init__.py` 与 `core/parsers/__init__.py` 各加一行 import + 实例。

完成。`pipeline` / `agent` / `config` 不需要任何改动；`--type xxx`、位置过滤、断点、留档自动生效。提示词模板放 organizer 文件顶部常量即可（`response_format=json_object` + 「严格只输出 JSON」措辞与现有保持一致）。

## 常见坑

- **中文路径**：`make_notes.py` 已做 `__file__` 乱码回退；新脚本里路径一律用 `os.path.join(BASE_NOTE, ...)`，不要拼 `\\`。
- **synth 阶段**：`job.is_synth=True` 时 pipeline 会用 `org.synth_source(stage_results)` 填充 `{CHUNKS}`；`synth_source` 返回空串会让该任务标记失败。
- **`$` 配平**：提示词里 JSON 示例中的 `\\n` 是写给模型的；你在模板常量里写 `\n` 时注意别用 `raw string` 吞掉。
- **批改文件先备份 + 幂等**：任何会动 `笔记/` 的写入逻辑都经 `ensure_stub` / `preserve_fm`，不要裸覆盖。