# VLM 鉴定流水线（Qwen3.5-4B 多模态，硅基流动）

> 目的：用小模型对 8 本书的 origin 做全量**观察**（不做判决），结果全部落盘 JSONL，后续另行裁定。
> 状态：**全量完成（2026-08-18）**。任务1 提示词 v2 全量 2288/2288；task3 数学+408 十六个 jsonl 缺题对账全部归零（三轮补漏 + raw 抢救）；task2 试点（数据结构 92 节）完成；**缺陷修复收尾完成**：初筛713→核实real218→修复/确认216、待人工2，8本校验全过；**任务4完成**：364张非A图片带上下文重判（92翻正为A）。汇总见 `_vlm/results/SUMMARY.md`。
> **看结果先读 `_vlm/results/README.md`（结果说明书，面向未接触过本项目的人）。**

## 核心原则（用户定调）

1. 小模型只做观察、不做判决——markdown 清洗过，与原书必有差异，"像不像"不能直接采信
2. 结果写 JSONL 文件，**不要读进上下文**（文件大，看统计用脚本聚合）
3. 断点续跑：每条结果追加写盘，重跑自动跳过已完成项（靠 `load_done`）
4. 限速 70k TPM / 900 RPM（额度 L0：80k TPM / 1000 RPM，留余量）；429/5xx 指数退避，最多 5 次后记 CALL_FAIL 继续
5. 无证据引用（evidence）的观察行不进后续终审队列

## 三个任务

| 任务 | 单元 | 内容 | 输出 |
|---|---|---|---|
| 1 插图鉴定 | 每张图（~2200 张，8 本） | 先一句描述（强制兜覆盖），再分大类 A 真实插图 / B 内容型图片（本该是文字）/ C 无法判断，B 再细分（文字段落/公式/表格/目录页/整页书页/图文混合/二维码广告/空白损坏/其他） | `results/task1_images/<书>.jsonl` |
| 3Q 题目完整性 | 408 每个 习题/试题精选节 | 逐题观察：present / stem_complete / options_complete / subq_complete / figure_ok + evidence + note | `results/task3q/<书>.jsonl` |
| 3A 答案完整性 | 408 每个 答案与解析节 | 逐题观察：present / letter / analysis_complete（重点：解析被并入上题、解析截断）+ evidence + note | `results/task3a/<书>.jsonl` |
| 2 小节对照 | 内容型小节（### X.Y.Z，习题/答案节除外） | 按书上顺序列内容块：type + in_md(有/部分/无) + evidence + note；白名单（广告/二维码/页眉=故意删）不算缺失 | `results/task2_sections/<书>.jsonl` |

**执行顺序**：校准 → 任务1 → 任务3Q/3A（408 四本）→ 任务2（先试点数据结构一本，看质量再铺开）。
**不做**：不改 origin/拆分稿任何文件；不判"是否缺陷/答案对错"；不做编号连续性（脚本已确定性覆盖）；数学全量题目对照暂缓。

## 技术要点

- **页对齐**：408 用 PDF 书签 `fitz.get_toc()`（书签页=PDF 页）；每单元页范围前后各带 1 页灰标上下文，prompt 里声明"只判定核心范围"。数学 PDF 无书签，若铺开用"讲起始页 + 图片感知哈希锚点"推算（未实现）
- **超长小节**：>8 页在 H5 子项边界切分（未实现，目前 `text[:7000]` 截断）
- **模型是 thinking 型**：响应有 `reasoning_content`，最终答案在 `content`；`max_tokens` 要给足（任务1=300 够，任务2/3=4000）
- **渲染**：dpi 110，左上角叠加红色 `PDF pN` 标注，缓存在 `_vlm/pages/`
- **幂等**：任务脚本重跑自动跳过 JSONL 里已有的 key（任务1=img，任务2/3=sec）

## 文件清单

```
_vlm/
├── PLAN.md            ← 本文件
├── .env               ← API key（已 gitignore）
├── config.json        ← base_url/model/限速/重试/dpi
├── scripts/           ← 全部流水线脚本（pythonw 无窗口运行）
│   ├── _vlm_lib.py            ← 客户端/限速器(锁外睡眠)/JSONL 续跑/PDF 渲染(线程安全)/书签对齐/小节切分
│   ├── _vlm_run_all.py        ← ★串行驱动：任务1→3Q→3A→任务2（生产环境入口）
│   ├── _vlm_task1_images.py   ← 任务1（8 本，4 线程，每行带 raw 原始返回）
│   ├── _vlm_task3_qa.py       ← 任务3 Q|A（4 线程/节级并行，raw 存 META 行）
│   ├── _vlm_task2_sections.py ← 任务2（4 线程，raw 存 META 行）
│   ├── _vlm_report.py         ← JSONL → 每任务每书 Markdown 观察表（带缩略图/raw 列）
│   ├── _vlm_aggregate.py      ← 聚合对账 → results/SUMMARY.md
│   └── _vlm_calibrate.py / _vlm_smoke.py / _vlm_explore_math*.py（校准/冒烟/探查，已用完）
├── pages/             ← PDF 渲染缓存（gitignore）
├── logs/              ← run.log（逐事件）+ pipeline.log（驱动 stdout）
└── results/
    ├── README.md      ← ★结果说明书（先看这个）
    ├── SUMMARY.md     ← 跑完后的对账汇总（_vlm_aggregate.py 生成）
    ├── task1_images/  task2_sections/  task3q/  task3a/   ← 各含 书名.jsonl(账) + 书名.md(观察表)
    └── calibration/   ← GO/NO-GO 校准记录
```

## 待办（按序）

1. ~~冒烟测试~~ / ~~校准~~（任务1 6/6；3Q、3A 合成缺陷 3/3 识别，A-pass prompt 已加固）
2. ~~任务1 全量~~ 跑批中（任务1→3Q→3A→任务2 串行，pythonw 无窗口 + 5 分钟守护）
3. 任务3 扩展到数学四本（PDF 无书签：插图模板匹配建锚点+单调插值；30讲 unit=讲的习题/解答，1000题 unit=章）
4. 跑任务2 其余 7 本前评估数据结构试点质量
5. 聚合统计 → 交付裁定

## 历史障碍（已解决）

- 2026-08-18 01:35 API 报 402 余额不足（账户 balance=0，连免费模型也不通）；同日稍后自愈/恢复，冒烟通过。
