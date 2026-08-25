# nature-writing-studio v2.0.1

**简体中文（当前）** · [English](README_EN.md)

> Nature 风格学术写作 Skill：基于Nature级别正刊文章蒸馏知识库，把任意科学文本（中文或英文草稿）改写成顶刊风格的英文。

## 一键装机

在 Codex 里说

```powershell
请安装位于 https://github.com/mumdark/nature-writing-studio 的 Skill
```

总体积约 **15 MB**（13 个 TSV 知识库 + 10 个 模块）。

## 目录结构

```
nature-writing-studio/
├── README.md          <- 本文件（GitHub 主页）
├── README_EN.md
├── skill/             <- Codex skill 根目录
    ├── SKILL.md       <- Codex 入口；所有内部路径基于此目录
    ├── agents/openai.yaml
    ├── knowledge/     <- 13 个 TSV
    ├── prompts/       <- 10 个 prompt
    ├── scripts/       <- sanity 校验
    ├── docs/          <- roadmap
    ├── fixtures/      <- 中文测试 fixture
    ├── CHANGELOG.md
```


## Codex 调用示例

```md
$nature-writing-studio 把下面这段中文改写为 Nature 风格的英文：
我们用 CRISPRi 筛选了 287 个转录因子，找到 ZNF219 这个之前没报道过的转录因子，它抑制神经分化。

$nature-writing-studio 帮我把整篇草稿按 Nature 格式编排（abstract→introduction→results→discussion→methods）：
"input: <约 350 字中文草稿>
target: multi_section
domain: biology_genomics"
```

## 功能

skill 围绕三个核心设计展开。下文按 **核心设计 → 输出格式 → 调用方式** 三段展开。

### 三大核心设计

#### ① 真实 Nature 文章蒸馏

不做 LLM 自由发挥，而是从 Nature 正刊文章中按节抽取真实的写作模式，再按节级上下文挑出最匹配的句式。具体抓五类信号：

- **节首 3-gram**（`opener_distribution.tsv`，10488 行）—— 比如 abstract 节首最高频是 `here we`（279 篇论文中出现）。
- **节内转折模板**（`gap_transitions.tsv`，1668 行）—— 比如 introduction 中 `Although X, Y.` 出现 15 篇 / 15 篇。
- **动词按证据强度分档**（`hedge_verbs.tsv`，124 行）—— causal（强）→ `show` / `demonstrate` / `identify`；associative（中）→ `suggest` / `indicate` / `support`；speculative（弱）→ `may` / `could` / `possibly`。
- **跨节衔接模板**（`cross_section_linkers.tsv`，1766 行）—— 比如 intro → results 的 `Having established X, we next asked whether Y`（50 论文）。
- **results 段开头句**（`results_discussion_openers.tsv`，4864 行）—— 比如 `To characterize X, we performed Y`。

合计 19,378 行 pattern，spot-check 抽 18 行随机验证 89% 通过（LCS ≥ 0.5）。

#### ② 反 AI 用词对抗学习

LLM 在模仿 Nature 风格时总会带一些"AI 味"短语。我们从 LLM 冒充 Nature 风格的文章中抽出 136 条 AI-tell，skill 改写时**永远禁用**。分三级：

| 等级 | 数量 | 典型例子 |
|---|---|---|
| **严重 AI-tell**（必须替换） | 40 | `delve into` / `navigate the complexities of` / `shed light on` / `key role in` |
| **替换词 AI-tell**（优先换回基础词） | 127 | `leverage` / `utilize` / `robust` / `comprehensive` |
| **轻微 AI-tell**（润色掉即可） | 124 | `It's worth noting that` / `Importantly` / `It is important to note` |

执行机制在 [验收层](#验收层verification-layer)——不是软规则，是 hard post-process。

#### ③ 分模块写作 + agent 自动识别

skill 不是一锅端改全文，而是按论文模块独立改写。`multi_section` 模式下 agent 会**自动**根据 input 的章节标题、长度、关键词判断要改写哪些模块，无需用户手动指定：

| 模块 | 用途 | 输入长度建议 |
|---|---|---|
| `abstract` | 摘要改写 | 100–250 字 |
| `introduction` | 引言改写 | 300–800 字 |
| `methods` | 方法改写 | 200–500 字 |
| `results` | 结果改写 | 300–800 字 |
| `discussion` | 讨论改写 | 300–600 字 |
| `figure_legend` | 图注改写 | 50–150 字 |
| `sentence` | 句级打磨（最短输入） | 任意 |

例如 multi_section 模式下输入一篇 800 字的中文草稿，agent 自动识别到这是"results + discussion"类型，套用 SP005 版式（results + discussion 串写），不会硬塞 abstract。

### 输出格式

每个调用都返回**三件套**：

| 字段 | 含义 | 何时用 |
|---|---|---|
| `text` | 正文（Nature 风格英文） | 直接用于投稿 / 润色稿 |
| `text_compact` | 紧凑版（60–70% 长度） | 投稿字数限制 / 快速预览 |
| `summary` | 改写元信息：用了哪些规则、避开了哪些 AI-tell、所属章节与领域 | 自查 / debug |

**示例**（把"我们用 CRISPRi 筛选了 287 个转录因子，找到 ZNF219 这个之前没报道过的转录因子，它抑制神经分化"按 `target=abstract` 改写）：

```json
{
  "text": "Here we used CRISPRi screening across 287 transcription factors and identified ZNF219 as a previously uncharacterized repressor of neural differentiation.",
  "text_compact": "We screened 287 TFs by CRISPRi and identified ZNF219 as a repressor of neural differentiation.",
  "summary": {
    "section": "abstract",
    "domain": "biology_genomics",
    "logic_line": "screen -> single hit -> mechanism",
    "rules_applied": ["R001 主动语态", "R023 数字格式"],
    "ai_tells_avoided": ["delve into", "navigate complexities", "shed light on", "leverage"]
  }
}
```

### 调用方式

两种调用模式，按需求选：

**单节改写（single_section）**：从 7 个 `target` 中选一个，传入对应章节的草稿，返回三件套。

**整稿编排（multi_section，v2.0.1 新增）**：传入整篇草稿，agent 自动识别章节结构，按节改写并跑跨节一致性审计（X001–X010），返回每节 JSON + `meta` 对象（`version_used` / `logic_line` / `entity_registry` / `cross_section`）。

7 个 single_section 接口共享同一 prompt 模板 `prompts/sections/<target>.txt`；multi_section 走独立的编排器 `prompts/sections/multi_section.txt`。

## 蒸馏产物详解

逐个 TSV 一句话讲清 + 例子。所有数据来自 Nature 正刊文章抽取（详见上方三大核心设计 ①）。

### 句式 / 衔接类（5 个 TSV）

| TSV | 一句话 | 例子 |
|---|---|---|
| `opener_distribution.tsv`（10488 行） | 节首 3-gram 用什么开头 | abstract：`here we`（387 hits / 279 论文） |
| `gap_transitions.tsv`（1668 行） | 节内转折用什么 pivot | introduction：`Although X, Y.`（15 hits / 15 论文） |
| `cross_section_linkers.tsv`（1766 行） | 跨节衔接模板 | intro → results：`Having established X, we next asked whether Y`（50 论文） |
| `hedge_verbs.tsv`（124 行） | 动词按证据强度分档 | associative 档：`suggest`（1645 hits / 409 论文） |
| `results_discussion_openers.tsv`（4864 行） | results / discussion 段开头句模板 | results：`To characterize X, we performed Y.`（21 hits / 12 论文） |

### 论文结构 / 规则类（3 个 TSV）

| TSV | 一句话 | 例子 |
|---|---|---|
| `paper_story_patterns.tsv`（12 行） | 整篇论文的章节版式 | SP001：abstract → introduction → results → discussion → methods（默认） |
| `cross_section_rules.tsv`（10 行） | 多节编排时的跨节一致性规则 | X001：hedge 不能由弱变强；abstract 用 causal，discussion 不能升级回 causal |
| `inter_section_argue_chains.tsv`（21 行，v3.1 proto） | 3 步论证链（claim → evidence → hedge） | 实验型 paragraph：claim_verb=`show` → evidence_verb=`identify` → hedge_verb=`suggest` |

### 写作规则 / 短语类（5 个 TSV）

| TSV | 一句话 | 例子 |
|---|---|---|
| `writing_rules.tsv`（85 行） | Nature 写作规则编号集 | R001：主动语态；R023：数字 ≥ 10 用阿拉伯、1–9 拼写 |
| `phrase_bank.tsv`（134 行） | 可复用短语模板 | "Taken together, these findings..." |
| `anti_ai_patterns.tsv`（136 行） | AI-tell 黑名单 | 见上方核心设计 ② |
| `domain_register.tsv`（46 行） | 22 个生物学子领域的 register | genomics 用被动少、CRISPR 类用主动 |
| `sentence_stats_by_domain.tsv`（24 行） | 每个领域的真实句长统计 | genomics 摘要平均 23 词 / 句 |

13 个 TSV 共 19,378 行 pattern。每行都至少有一个 Nature 论文 DOI 作为来源锚点；改写时按节级上下文挑最匹配的句式，不靠 LLM 自由发挥。

## 渲染输出契约

- **每个 target 必产三件套**：`text` + `text_compact` + `summary`
- **`multi_section` 多加一层 meta**：每节 JSON + `meta`（`version_used` / `logic_line` / `entity_registry` / `cross_section` 审计 / `degraded` flag）
- **em-dash 零容忍**：`text` 与 `text_compact` 都不允许出现 U+2014（—）；`strip_em_dash()` 在验收层之后强制跑一次
- **加粗策略**：只用于标题、表头、置信度行、引用锚点；正文不粗体
- **不输出**：内部块（如"前言与合规说明"、"主张→证据映射"、"覆盖范围说明"、"对抗性自检"）不进文件，只在 skill 内部跑

## 验收层（Verification Layer）

skill 改写后的最后一道闸，**5 条规则顺序固定**（在反 AI 自检之后、返回给用户之前跑）：

| 规则 | 作用 | 命中示例 |
|---|---|---|
| **1a 回溯性（HARD）** | output 里的 figure 编号、引用 token、数值、organism / tissue / cell-type 等生物实体必须能在 input 里找到同字面或同义词 | input 没提"Fig. 3"，output 出现 "(Fig. 3)" → 删 |
| **1b 通用知识白名单** | 通用科学常识允许不出现在 input | `alternative splicing` / `transcriptome` / `eukaryotes` 不需回溯 |
| **2 em-dash 零容忍** | output 不允许 U+2014 | "regulation—mediated by..." → 改写 |
| **2.5 em-dash 确定性清洗** | `text` / `text_compact` 各跑一次 `strip_em_dash()`；hard post-process | 同上，强制 |
| **4 引用要求** | introduction 的 background claim 必须带引用 | "Several studies have shown..." 没引用 → 补 [1] / [2] 占位 |

**修复方式**：先删幻觉 token；若整句依赖该 token 就改写该句，其它节段不动。

**白名单**（改写词库内、不需回溯）：
- **连接词**：and / then / here / through / by / using / with / of / from / to / in / on / as / that
- **通用动词**：show / identify / report / use / perform / measure / observe / suggest / demonstrate / establish / find
- **通用名词**：sample / cell / data / figure / method / condition / group / replicate / trial / experiment / analysis
- **领域通用实体**：CRISPR / CRISPRi / TF / RNA / DNA / mRNA / PCR

白名单之外 token 一律需回溯；不能回溯即伪造。

## 🤝 Contributions / 贡献

欢迎提出问题、建议和提交 Pull Request！

AI 相关应用或合作可以进一步沟通交流：
- 307686155@qq.com
