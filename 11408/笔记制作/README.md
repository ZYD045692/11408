# 笔记制作

本目录存放**从拆分稿批量生成学习笔记**的脚本与规范。它独立于「处理流程」（后者负责 OCR → origin → 拆分稿这条内容生产线），专注于「笔记层」的生成与维护。

## 职责边界

| 目录 | 职责 |
|---|---|
| `11408/处理流程/` | 把扫描书变成拆分稿：清洗 origin、拆分、校验 |
| `11408/笔记制作/` | 把拆分稿变成复习笔记：扫描任务、调用模型填充、渲染落盘、注入关联图谱 |
| `11408/笔记/` | 最终产物：人工可读、可复习的考点总结与闪卡 |

## 架构（2026-08 重构）

```
408/数学拆分稿 ──▶ core/organizers（整理：扫描任务、聚合原文、构造 JSON 提示词）
                        │
                        ▼
                 core/agent（只发请求：限速滑动窗口 TPM/RPM、重试、json 降级）
                        │ 原始输出留档 _notes_runtime/raw/
                        ▼
                 core/parsers（解析：容错 JSON、$ 配平、模板渲染）
                        │
                        ▼
                 11408/笔记/ 对应位置（保留 frontmatter，写 gen:）
```

- **入口**：
  - `make_notes.py` — 批量入口（薄封装，调 `core.pipeline.main`）
  - `make_one.py` — 单粒度入口：看一节做一节，适合边学边生成（详见下文）
- **配置**：`notes_config.json`（模型/限速/线程）；api key 读顶层 `_vlm/.env` 的 `SILICONFLOW_API_KEY`（与 VLM 审计共享同一密钥，不入库，不要复制）
- **运行时产物**：模型 raw 留档 / 失败清单 / 运行日志统放顶层 `_notes_runtime/`（与 `_vlm/` 分离）
- **模块文档**：见 `core/README.md`（含新增笔记类型的扩展步骤）

> ⚠️ **旧脚本保留情况**：`scripts/_build_kg_skeleton.py`（骨架）与 `scripts/_apply_math_graph*.py`（图谱互链）仍沿用旧 `BASE_NOTE` 路径结构，与当前结构不符，**运行前需先核对并适配其内部路径常量**；不改路径时它们多数是无操作，不会破坏现有笔记。

## 快速开始

### 单粒度生成（推荐：看一节做一节）

```bash
python 11408/笔记制作/make_one.py 高数 1.1            # 高数 1.1 小节
python 11408/笔记制作/make_one.py 高数 第1讲           # 高数第1讲：讲级 + 全部小节
python 11408/笔记制作/make_one.py 线代 第2讲           # 线代第2讲讲级笔记
python 11408/笔记制作/make_one.py 操作系统 1           # 操作系统 01 章全部考点
python 11408/笔记制作/make_one.py 数据结构 2.2         # 数据结构 2.2 考点
python 11408/笔记制作/make_one.py --all               # 全量（等价于 make_notes.py）
```

第一个参数是课程/书/科（`高数`、`线代`、`30讲-高数`、`操作系统`、`数据结构`…），第二个参数是小节号/讲名/章号；已有 `gen:` 的会跳过，加 `--force` 强制重跑。

### 批量入口

```bash
python 11408/笔记制作/make_notes.py --list           # 只列任务（不调 API），并幂等建空 stub
python 11408/笔记制作/make_notes.py --pilot          # 试点（408×2 + 数学讲×1 + 小节×1）
python 11408/笔记制作/make_notes.py                  # 全量
python 11408/笔记制作/make_notes.py --type 408       # 只跑某类型：408 | math_lecture | math_section
python 11408/笔记制作/make_notes.py 数据结构          # 按课程/书过滤
python 11408/笔记制作/make_notes.py --force 操作系统  # 忽略 gen: 断点强制重跑
```

## 目录结构

```
11408/笔记制作/
├── README.md              # 本文件
├── TODO.md                # 已知遗留问题（暂缓项）
├── notes_config.json      # 模型/限速/线程等配置
├── make_notes.py          # 批量 CLI 入口
├── make_one.py            # 单粒度 CLI 入口（看一节做一节）
├── core/                  # 架构核心（详见 core/README.md）
│   ├── config.py          # 配置加载（notes_config.json + 顶层 _vlm/.env 共享 api key）
│   ├── agent.py           # Agent + RateLimiter：只发请求
│   ├── task.py            # Task（一篇笔记）/ Job（一次模型请求）
│   ├── pipeline.py        # 入口编排：收集→过滤→线程池→重试→落盘→汇总
│   ├── organizers/        # 整理：scan()→[Task]，jobs()→提示词
│   │   ├── k408.py        #   408 考点（聚合真题年份/前后节/习题链接）
│   │   ├── math_lecture.py#   数学讲级（长讲 chunk→synth 多阶段）
│   │   └── math_section.py#   数学小节（仅高数；拆分稿 #### N 切小节，幂等建 stub）
│   └── parsers/           # 解析：JSON→校验→渲染笔记模板
│       ├── base.py        #   容错 JSON 提取、LaTeX 保护、$ 配平、闪卡聚合
│       ├── k408.py
│       ├── math_lecture.py
│       └── math_section.py
└── scripts/               # 保留的旧脚本（骨架 / 图谱，使用时需适配路径）
```

## notes_config.json 配置

```jsonc
{
  "base_url": "https://api.siliconflow.cn/v1",
  "model": "Qwen/Qwen3.5-397B-A17B",         // 当前用哪个模型，改这里即可
  "models": {                                // 模型注册表：RPM/TPM 限速（数值以实测/平台档位为准）
    "Qwen/Qwen3.5-397B-A17B": { "rpm": 500,  "tpm": 2000000 },
    "Qwen/Qwen3.6-35B-A3B":   { "rpm": 1000, "tpm": 40000 },
    "Qwen/Qwen3.5-4B":        { "rpm": 1000, "tpm": 50000 },
    "THUDM/GLM-Z1-9B-0414":   { "rpm": 1000, "tpm": 50000 }
  },
  "enable_thinking": false,                  // 思考模式开关（397B 关闭即可，开了慢）
  "threads": 4,
  "timeout": 300,
  "max_retries": 5,
  "max_src": 1000000,                        // 原文截断上限；务必大于最长小节，宁可不截断
  "max_tokens": 128000,
  "max_cards": 50,                           // 每篇笔记闪卡封顶张数
  "raw_dir": "_notes_runtime/raw",
  "manual_list": "_notes_runtime/repair/notes_manual.md"
}
```

**模型选择经验**（2026-08 实测）：
- **397B** 对「问题抽象通用、不针对具体例题或数值」这类一句式正面约束就能稳定执行，定义事实错误基本消失，是当前的默认选择。
- **4B/35B** 对抽象约束执行不稳：会生成具体例题数值卡、元信息卡（"什么时候讲"），偶发事实错误（如把 $x\in D$ 写成 $x\notin D$）；负面示例在小模型上会产生反效果（越禁越学），不要往 prompt 里堆"不要这样"的示例。
- GLM-Z1-9B 出过事实性错误，不用于笔记生成。

**限速机制**：`agent.RateLimiter` 用滑动窗口记账（每分钟 TPM + RPM 双限），每次请求前预扣估计 token，响应后按 usage 真实值 `settle` 修正；多线程共享同一限速器，天然线程安全。

## 笔记目标路径

| 类型 | 目标 |
|---|---|
| 408 考点 | `笔记/408/{课程}/{NN-章名}/{x.y-节名}.md` |
| 数学讲级（高数，有小节） | `笔记/数学/30讲-高数/{第N讲-讲名}/{第N讲-讲名}.md` |
| 数学讲级（线代，只有讲级） | `笔记/数学/30讲-线代/{第N讲-讲名}.md` |
| 数学小节（仅高数） | `笔记/数学/30讲-高数/{第N讲-讲名}/{x.y-标题}.md` |

- 线代**不切小节**（只出讲级笔记）；讲级落盘路径按"是否有小节"自适应（`math_lecture.lecture_note_path`）。
- 扫描时目标文件缺失会**幂等建 stub**（已有文件绝不覆盖，保留用户笔记）。
- 生成后写 `gen: <model>-think` frontmatter；`gen:` 存在即视为「已生成」，后续运行跳过（断点续跑）。

## 闪卡与 SR 复习队列

生成物默认使用 `#card` 标签，**不进入 Obsidian Spaced Repetition 的复习队列**。原因：

- 批量生成的闪卡需要先做质量检查（问题是否自包含、答案是否准确、是否重复）。
- 若直接用 `#flashcards`，所有新卡片会立即涌入 SR，导致复习负担不可控，也难以批量修正。

确认某篇/某批笔记可以复习后，再切换标签：

```bash
# 启用复习（#card → #flashcards）
python 11408/笔记制作/toggle_card_tag.py --on 408/操作系统/01-计算机系统概述/1.1-操作系统的基本概念.md

# 禁用复习（#flashcards → #card）
python 11408/笔记制作/toggle_card_tag.py --off 408/操作系统/01-计算机系统概述/1.1-操作系统的基本概念.md

# 批量启用/禁用（glob 模式）
python 11408/笔记制作/toggle_card_tag.py --on "408/操作系统/**/*.md"
python 11408/笔记制作/toggle_card_tag.py --off "数学/30讲-高数/第1讲-函数极限与连续/**/*.md"

# 只检查，不写盘
python 11408/笔记制作/toggle_card_tag.py --dry --on "408/**/*.md"
```

SR 插件默认识别 `#flashcards`；切换后重新打开 Obsidian 或等待插件扫描即可入队。

闪卡挂在考点下面（`points[].cards`），保证每张卡归属于具体考点：

```json
{
  "one_liner": "一句话点透本质",
  "points": [{
    "name": "考点名",
    "conclusion": "核心结论一句话",
    "content": "公式/代码/步骤模板",
    "exam_tip": "考试怎么用/易错提醒",
    "cards": [{ "q": "问题", "a": "简短答案" }]
  }],
  "confusions": [{ "title": "易混点", "body": "对比说明(可含表格)" }]
}
```

- 408 / 数学小节：单次请求，直接出上述结构。
- 数学讲级：短讲单次；长讲先逐块出 `{"points":[...]}`，再 synth 合成上述结构（输入是各块要点汇总）。
- 渲染时 parser 用 `collect_cards()` 从所有 `points[].cards` 聚合闪卡，按问题去重、封顶 `max_cards` 张。

## 提示词约束（两套通用）

三类 prompt（408 考点 / 数学讲级 / 数学小节）共用同一套精简约束：

- **深度优先、结论忠于原文**：关键定义、定理、公式、代码必须保留；**典型代表、实例、优缺点也必须出自原文，原文没写的不要凭常识补充**（防编造）。
- **闪卡规范**：每考点 2~5 张；问题抽象通用（问定义、定理、公式、通用方法），不针对具体例题或数值，不问元信息；答案是可直接记忆的结论。
- 不输出"本节核心是…"式目录句。
- JSON 字符串值内不换行；LaTeX 命令必须完整（`\frac`、`\mid`、`\leq`、`\subseteq`、`\to`…），定界符配对。

**护栏**：
- `response_format={"type":"json_object"}`；模型不支持时降级普通请求。
- `parsers/base.py` 解析前做两层预处理：`_preprocess_escapes`（把模型写的字面 `\\n` 还原为 JSON `\n`）、`_protect_latex`（给 JSON 不认识的 LaTeX 命令补双反斜杠，但跳过 `\n \t \r \b \f` 与 `\uXXXX`/`\UXXXXXXXX` 合法转义）。
- 解析失败 / `$` 配平不通过自动重试一次（带纠错提示）；再失败保持 stub、记入 `_notes_runtime/repair/notes_manual.md`，原始输出留档 `_notes_runtime/raw/` 供排查（raw 留着就能离线重渲染，不用重新调 API）。

## 408 机械信息

`k408.py` 扫描时自动聚合：

- **真题年份**：习题文件的 `【20XX 统考真题】` + 考点正文的 `考点追踪（20XX、20XX）` 两处合并提取。
- **习题链接**：同章 `习题/{x.y}-*.md`。
- **前后节关联**：同章考点按节号排序取前驱/后继。

## MOC

各科 MOC（`408-MOC`、`数学-MOC`、`408/{课程}/{课程}-MOC`、`数学/30讲-*/{高数,线代}-MOC`）只放章节/讲级 wikilink 清单，从拆分稿目录结构机械重建，**不放闪卡与正文内容**。生成新笔记不影响 MOC。

## 运行前检查

1. `_vlm/.env` 有有效的 `SILICONFLOW_API_KEY`；拆分稿已生成且目录结构正确。
2. 确认 `notes_config.json` 的 `model` 与 `models` 限速值。
3. 第一次跑某范围前，先 `--list` 看任务收集是否符合预期，再单点（`make_one.py`）看单篇效果。
4. 模型生成消耗 token，全量前确认配额。

## 排错

- **`缺少 API key`**：`_vlm/.env` 没有 `SILICONFLOW_API_KEY=...` 行（或环境变量）。
- **任务为 0 / 路径不对**：先 `--list` 核对；确认拆分稿里有 `### 基础内容精讲` / `#### N` 标题（高数小节切分依赖它们）。
- **生成内容为空或格式崩**：去 `_notes_runtime/raw/` 看模型原始输出；拆稿原文 OCR 噪声大时可先清洗 origin。
- **LaTeX 显示成 `ε` 字面量 / `\b` 吞字**：模型把反斜杠写成了 `\` 或单反斜杠命令，属于解析层问题——检查 `parsers/base.py` 的 `_protect_latex` 是否覆盖了该模式。
- **频繁 429 / 限速**：`threads` 调低，或核对 `models` 注册表 rpm/tpm 是否过高于实际配额。
- **卡在某篇重试**：`_notes_runtime/logs/run.log` 有每篇的请求与失败记录；`_notes_runtime/repair/notes_manual.md` 是失败清单。
