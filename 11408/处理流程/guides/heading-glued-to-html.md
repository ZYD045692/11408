# 标题紧贴 HTML 块

> **现象**：Obsidian 文件大纲里某个标题消失（如高数第1讲「三 函数极限的概念与性质」），文件里标题明明存在。
> **原因**：标题行**直接跟在 HTML 行后面，中间没有空行**（`</div>`、单行 `<table …>…</table>` 等）。CommonMark 的 HTML 块（type 6）一直延伸到空行为止 → 标题被吞进 HTML 块，不进大纲。
> **判别**：标题前一行是**文本**无所谓（ATX 标题可以打断段落，正常显示）；前一行以 `<` 开头（HTML 标签）才是问题。
> **修复**：标题与 HTML 行之间插一个空行。
> **排查命令**（8 本 origin 全跑，已固化为 `_scan_glue_heading.py`）：
> ```python
> import re
> for i, s in enumerate(lines):
>     if s.strip().startswith("```"): in_code = not in_code; continue
>     if in_code: continue
>     if re.match(r"^#{1,6} ", s) and i > 0 and lines[i-1].strip().startswith("<"):
>         print(i+1, s)  # 标题紧贴 HTML 行,需插空行
> ```
> **已知案例**：高数 L1291「#### 三 函数极限的概念与性质」← `</div>`、L8245「##### 1 物理应用」← `</div>`；操作系统 L8037/L16009、计算机网络 L8408/L13817 ← 单行 `<table>`。共 6 处，全部插空行修复。
