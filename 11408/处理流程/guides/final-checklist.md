# 内容终检清单

扫描版 OCR 书常见内容级残留，标题/公式校验都查不出，需专项扫描（`_final_scan.py`、`_scan_bounds.py`、`_scan_artifacts.py`、`_scan_div.py`、`_check_div_balance.py`、`_scan_unclosed_divs.py`）：

| 问题 | 特征 | 处理 | 脚本 |
|---|---|---|---|
| **句中广告残留** | `一手+V：kaoyan33311` 嵌在句子里（`_del_ads.py` 只删整行漏掉） | 移除广告词并接合断行；嵌进 `$$...$$` 的整行删 | `_fix_final.py` |
| **公式边界空格** | 跨行 `$ \left\{...\right. $` 开 `$` 后有空格/闭 `$` 前有空格 → Obsidian 不渲染 | 转 `$$...$$` 块；乱码内容按配图重写（`luma` 读图核对） | `_fix_final.py` |
| **未闭合 `<div>`** | `<div style="text-align: center;">` 缺 `</div>`，**嵌套成链**，导致其后全文居中泄漏（高数曾 42 个连到文件尾） | 首个非空内容为 `<img>` → 图后补 `</div>`；为文本/表格/其它div → 删孤儿 div 行；改后收支必须为 0 | `_fix_unclosed_div.py` |
| **成对 `==` 假高亮** | 一行内两个 `==`（如 `if(a==b)` 出现两次）→ Obsidian 把中间整段染黄 | C 表达式包反引号 | `_fix_eq_pairs.py` |
| `\xrightarrow{化学}` 乱码 | OCR 把"化为"读成"化学/一成历九" | 按上下文改回 | 人工/`_fix_final.py` |
| 行尾 `\` 残留 | `20 \. B\`（答案行） | 去 `\` | 顺手处理 |
