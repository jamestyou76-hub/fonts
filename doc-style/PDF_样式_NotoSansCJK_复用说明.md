# PDF 样式复用说明 - NotoSansCJK / Pandoc / XeLaTeX

本文记录本次较好看的 PDF 导出风格，后续生成中文 / 日文技术 memo、TODO list、设计说明书时可直接复用。

---

## 1. 推荐用途

适合以下类型文档：

- 电路级 TODO list
- 工程 memo
- 设计 review 简报
- 中日文混排技术说明
- 表格较多、但不追求 Word 版复杂排版的 PDF

不建议用于：

- 图片特别多的正式报告
- 需要复杂页眉页脚 / 目录 / 自动编号的 Word 风格报告
- 超宽表格、复杂合并单元格表格

---

## 2. 核心风格

| 项目 | 推荐设置 |
|---|---|
| PDF 生成方式 | Markdown -> Pandoc -> XeLaTeX -> PDF |
| 页面 | A4 portrait |
| 主字体 | NotoSansCJKjp Regular |
| 粗体 | NotoSansCJKjp Bold |
| 中文 / 日文字体 | NotoSansCJKjp |
| 正文字号 | 9.2-9.5 pt 推荐 |
| 行距 | 1.12-1.18 推荐 |
| 页边距 | 约 16-18 mm |
| 表格 | 尽量短列名、短句；避免超宽表格 |
| 符号 | 尽量使用 ASCII 半角符号，避免特殊长横线造成渲染问题 |

本次最终 PDF 使用的感觉是：**NotoSansCJKjp Regular / Bold + XeLaTeX + 紧凑页边距 + 简洁 Markdown 表格**。

---

## 3. 字体组合

优先使用：

```text
NotoSansCJKjp-Regular.otf
NotoSansCJKjp-Bold.otf
```

或系统中可用的字体名：

```text
Noto Sans CJK JP
Noto Sans CJK JP Bold
```

说明：

- 即使是中文文档，也可以使用 `Noto Sans CJK JP`，中日文显示都比较稳定。
- 不建议混用 SimSun、MS Gothic、Arial Unicode MS 等，因为不同环境下渲染差异较大。
- PDF 中应嵌入字体，避免用户电脑缺字体导致显示变化。

---

## 4. Pandoc 推荐命令

基础命令：

```bash
pandoc input.md \
  -o output.pdf \
  --pdf-engine=xelatex \
  -V papersize=a4 \
  -V geometry:margin=17mm \
  -V fontsize=9.5pt \
  -V linestretch=1.15 \
  -V mainfont="Noto Sans CJK JP" \
  -V sansfont="Noto Sans CJK JP" \
  -V CJKmainfont="Noto Sans CJK JP" \
  -V colorlinks=false
```

如果正文仍然偏大，可改为：

```bash
-V fontsize=9pt
```

如果页面太松，可改为：

```bash
-V geometry:margin=16mm
-V linestretch=1.12
```

如果表格很多，建议不要只缩小字体，而是先精简表格文字。

---

## 5. 推荐 Markdown 写法

### 5.1 标题

```markdown
# 文档标题

版：Rev.x / 日期：YYYY-MM-DD  
范围：仅记录硬件 / 电路级 TODO，不含固件实现。

## 1. 输入电源与充电功率
```

标题层级建议最多到三级：

```markdown
# 一级标题
## 二级标题
### 三级标题
```

不要使用过深层级，PDF 会显得杂乱。

### 5.2 表格

推荐：

```markdown
| No. | TODO | 现状 / 判断 | 优先度 |
|---|---|---|---|
| 1.1 | VIN 输入能力最终确定 | R18=374Ω，ILIM 约 3A；若 VIN=5V/2A，则 1.5A 充电需降额。 | 高 |
```

表格注意点：

- 一行内容不要太长。
- 列数建议 3-4 列以内。
- 长解释放在表格下方的补充说明，不要全部塞进表格。
- 避免合并单元格。

### 5.3 TODO 列表

推荐：

```markdown
## 8. 次版 SCH 中需要明确的 TBD

1. VIN 输入规格：5V/2A 还是 5V/3A。
2. 5V/2A 输入时是否允许最大充电电流降额。
3. 4.2V / 4.35V 硬件 jumper 是否必须。
```

---

## 6. 内容风格建议

### 6.1 技术 TODO 文档

推荐写法：

```text
TODO + 现状 / 判断 + 优先度
```

例如：

```markdown
| No. | TODO | 现状 / 判断 | 优先度 |
|---|---|---|---|
| 2.1 | L1 电流和温升复核 | L1=1uH，Current Rating 12A，DCR 7.4mΩ。需在 5V 输入、8.4V/1.5A 输出条件下确认饱和电流、RMS 电流和温升。 | 高 |
```

### 6.2 不确定项

未确定内容直接写 TBD，不要写成确定结论：

```markdown
| 4.2 | 2.54mm 接口形式确认 | 构想资料要求 2.54mm，当前 PCB 形式是否满足仍为 TBD。 | 高 |
```

### 6.3 结论语气

推荐使用：

- `可接受，但建议预留追加位`
- `偏紧，需实测确认`
- `TBD`
- `建议下一版 SCH 明确`
- `不直接判 NG，但需保留验证项`

避免使用过度绝对的表达：

- `一定不够`
- `必须全部修改`
- `肯定没问题`

---

## 7. PDF 生成后的检查流程

每次生成 PDF 后都需要渲染检查页面图像：

```bash
python /home/oai/skills/pdfs/scripts/render_pdf.py output.pdf --out_dir render_check --dpi 160
```

检查重点：

- 字体是否正常显示
- 中文 / 日文是否缺字
- 表格是否溢出页面
- 是否有空白页
- 标题是否断页过丑
- 表格行是否被压得过密

如果表格溢出，优先处理：

1. 缩短列标题和表格文字。
2. 将长说明移到表格外。
3. 降低正文字号到 9pt。
4. 页边距改为 15-16mm。
5. 必要时拆分表格。

---

## 8. 推荐文件命名

中文：

```text
电池充电基板_当前SCH电路TODO_精简版_ZH.pdf
电池充电基板_当前SCH电路TODO_精简版_ZH.md
```

日文：

```text
バッテリー充電基板_現行SCH回路TODO_簡易版_JP.pdf
バッテリー充電基板_現行SCH回路TODO_簡易版_JP.md
```

若有专题版本，可追加后缀：

```text
_MLCC_EVM修正版
_MLCC_DC_Bias確認版
_Rev6対応版
```

---

## 9. 推荐复用模板

```markdown
# 电池充电基板 - 当前 SCH 电路级 TODO List（精简版）

版：Rev.x 对应检查版  
范围：仅记录客户要求对应的电路 / 硬件 TODO，不含固件实现、通信协议和上位机处理。  
前提：当前 SCH、客户要求书、构想资料中的充电模块要求、相关 datasheet / EVM 资料。

## 1. 输入电源与充电功率

| No. | TODO | 现状 / 判断 | 优先度 |
|---|---|---|---|
| 1.1 | VIN 输入能力最终确定：5V/2A 或 5V/3A | TBD。若支持 1.5A 充电，通常需要 5V/3A 级输入。 | 高 |

## 2. BQ25887 主功率回路

| No. | TODO | 现状 / 判断 | 优先度 |
|---|---|---|---|
| 2.1 | L1 电流和温升复核 | 按最大充电条件计算 RMS 电流、峰值电流和温升。 | 高 |

## 3. MLCC DC Bias 与 EVM 对照

| 节点 | 当前配置 | 判断 | TODO |
|---|---|---|---|
| SNS | 22uF x2 | 与 EVM nominal 配置接近，不直接判 NG。 | 保留实测项，必要时预留追加电容位。 |
| PMID | 10uF | 与 EVM 接近，但 after derating 余量 TBD。 | 预留追加 10uF-22uF 位。 |

## 4. 客户接口和保护

| 项目 | 当前状态 | TODO |
|---|---|---|
| ICHG_SET1/2 | TBD | 明确 GPIO、默认电平、ESD/串阻。 |
| ACOK/STAT | LED 兼用可能 | 建议外部 OD 与 LED 支路分离。 |

## 5. 下一版 SCH 最小修正顺序

1. 先确定 VIN 输入规格。
2. 根据 VIN 决定 ILIM 和充电电流表。
3. 明确客户接口 pin table。
4. 复核 MLCC DC Bias，并保留必要的追加电容位。
5. 复核 TVS、NTC、CBSET 温升。
```

---

## 10. 一句话总结

后续想复现这次好看的 PDF 风格，优先使用：

```text
Markdown + Pandoc + XeLaTeX + NotoSansCJKjp Regular/Bold + A4 + 16-18mm margin + 9-9.5pt + 简洁表格
```
