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




```markdown
提示词：
$Nature Writing Studio 把下面这句话改写为英文：我们用 CRISPRi 筛选了 287 个转录因子，找到 ZNF219 这个之前没报道过的转录因子，它抑制神经分化。
```



输出为标准的**三件套**：

| 字段 | 含义 | 何时用 |
|---|---|---|
| `text` | 正文（Nature 风格英文） | 直接用于投稿 / 润色稿 |
| `text_compact` | 紧凑版（60–70% 长度） | 投稿字数限制 / 快速预览 |
| `summary` | 改写元信息：用了哪些规则、避开了哪些 AI-tell、所属章节与领域 | 自查 / debug |

示例如下：

<img width="582" height="577" alt="image" src="https://github.com/user-attachments/assets/113e5887-4f3c-4abe-8b8f-79ea7d7c182d" />



## 核心设计与功能

skill 具有四大核心设计，具体如下：


#### ① 真实 Nature 文章蒸馏

不做 LLM 自由发挥，而是从 Nature 正刊文章中按节抽取真实的写作模式，再按节级上下文挑出最匹配的句式。具体抓五类信号：

- **节首 3-gram**（10488 种）—— 比如 abstract 节首最高频是 `here we`（279 篇论文中出现）。
- **节内转折模板**（1668 种）—— 比如 introduction 中 `Although X, Y.` 出现 15 篇 / 15 篇。
- **动词按证据强度分档**（124 种）—— 比如 causal（强）→ `show` / `demonstrate` / `identify`；associative（中）→ `suggest` / `indicate` / `support`；speculative（弱）→ `may` / `could` / `possibly`。
- **跨节衔接模板**（1766 种）—— 比如 intro → results 的 `Having established X, we next asked whether Y`（50 论文）。
- **results 段开头句**（4864 种）—— 比如 `To characterize X, we performed Y`。

合计 19,378 种写作模式。

#### ② 逻辑线提炼

基于 input 的可识别结构（方法 + 发现 + 意义）映射出来的写作逻辑（logic_line），并且显式输出到summary中。

比如上面的输入例子：我们用 CRISPRi 筛选了 287 个转录因子，找到 ZNF219 这个之前没报道过的转录因子，它抑制神经分化。

输出 text 是："Here we applied CRISPRi screening to a panel of 287 transcription factors (TFs) and identified ZNF219, a previously uncharacterized TF, as a repressor of neural differentiation."

对应的 logic_line输出是："screen → single hit → mechanism"


#### ③ 分模块写作 + agent 自动识别

skill 不是一锅端改全文，而是按论文模块独立改写（自动识别）。另外提供 `multi_section` 模式，agent 会**自动**根据 input 的内容改写完整多端文章：

| 模块 | 用途 | 输入长度建议 |
|---|---|---|
| `abstract` | 摘要改写 | 100–250 字 |
| `introduction` | 引言改写 | 300–800 字 |
| `methods` | 方法改写 | 200–500 字 |
| `results` | 结果改写 | 300–800 字 |
| `discussion` | 讨论改写 | 300–600 字 |
| `figure_legend` | 图注改写 | 50–150 字 |
| `sentence` | 句级打磨（最短输入） | 任意 |
| `multi_section` | 多个段落内容 | 任意 |

multi_section 模式下输入一篇 800 字的中文草稿，agent 自动识别到这是"results + discussion"类型，套用 SP005 版式（results + discussion 串写），不会硬塞 abstract。


#### ④ 基于对抗学习避免 AI 用词

LLM 在模仿 Nature 风格时总会带一些"AI 味"短语。我们基于 30 篇真实文章的内容逻辑，让 LLM 进行重新写作。根据真实文章的内容作为阴性对照，从 LLM 写作的文章中抽出了 136 条 AI-tell（AI常用用词），skill 改写时**永远禁用**。分三级：

| 等级 | 数量 | 典型例子 |
|---|---|---|
| **严重 AI-tell**（必须替换） | 40 | `delve into` / `navigate the complexities of` / `shed light on` / `key role in` |
| **替换词 AI-tell**（优先换回基础词） | 127 | `leverage` / `utilize` / `robust` / `comprehensive` |
| **轻微 AI-tell**（润色掉即可） | 124 | `It's worth noting that` / `Importantly` / `It is important to note` |

执行机制在 [验收层](#验收层verification-layer)——不是软规则。


### 调用方式

两种调用模式，可以按需求选，也可以由agent自动识别模式：

**单节改写（single_section）**：从 7 个 `target` 中选一个，传入对应章节的草稿，返回三件套。

**整稿编排（multi_section）**：传入整篇草稿，agent 自动识别章节结构，按节改写并跑跨节一致性审计（X001–X010），返回每节 JSON + `meta` 对象（`version_used` / `logic_line` / `entity_registry` / `cross_section`）。

7 个 single_section 接口共享同一 prompt 模板 `prompts/sections/<target>.txt`；multi_section 走独立的编排器 `prompts/sections/multi_section.txt`。

## 蒸馏产物介绍



### 句式 / 衔接类

| TSV | 一句话 | 例子 |
|---|---|---|
| `opener_distribution.tsv`（10488 行） | 节首 3-gram 用什么开头 | abstract：`here we`（387 hits / 279 论文） |
| `gap_transitions.tsv`（1668 行） | 节内转折用什么 pivot | introduction：`Although X, Y.`（15 hits / 15 论文） |
| `cross_section_linkers.tsv`（1766 行） | 跨节衔接模板 | intro → results：`Having established X, we next asked whether Y`（50 论文） |
| `hedge_verbs.tsv`（124 行） | 动词按证据强度分档 | associative 档：`suggest`（1645 hits / 409 论文） |
| `results_discussion_openers.tsv`（4864 行） | results / discussion 段开头句模板 | results：`To characterize X, we performed Y.`（21 hits / 12 论文） |

### 论文结构 / 规则类

| TSV | 一句话 | 例子 |
|---|---|---|
| `paper_story_patterns.tsv`（12 行） | 整篇论文的章节版式 | SP001：abstract → introduction → results → discussion → methods（默认） |
| `cross_section_rules.tsv`（10 行） | 多节编排时的跨节一致性规则 | X001：hedge 不能由弱变强；abstract 用 causal，discussion 不能升级回 causal |
| `inter_section_argue_chains.tsv`（21 行，v3.1 proto） | 3 步论证链（claim → evidence → hedge） | 实验型 paragraph：claim_verb=`show` → evidence_verb=`identify` → hedge_verb=`suggest` |

### 写作规则 / 短语类

| TSV | 一句话 | 例子 |
|---|---|---|
| `writing_rules.tsv`（85 行） | Nature 写作规则编号集 | R001：主动语态；R023：数字 ≥ 10 用阿拉伯、1–9 拼写 |
| `phrase_bank.tsv`（134 行） | 可复用短语模板 | "Taken together, these findings..." |
| `anti_ai_patterns.tsv`（136 行） | AI-tell 黑名单 | 见上方核心设计 ② |
| `domain_register.tsv`（46 行） | 22 个生物学子领域的 register | genomics 用被动少、CRISPR 类用主动 |
| `sentence_stats_by_domain.tsv`（24 行） | 每个领域的真实句长统计 | genomics 摘要平均 23 词 / 句 |

13 个 TSV 共 19,378 行 pattern。每行都至少有一个 Nature 论文 DOI 作为来源锚点；改写时按节级上下文挑最匹配的句式，不靠 LLM 自由发挥。


## 验收层（Verification Layer）

skill 改写后，输出前会经过一个验收层，agent 对内容进行质检，避免出现捏造信息，**5 条规则顺序固定**：

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

## 🤝 Contributions

欢迎提出问题、建议和提交 Pull Request！

