# nature-writing-studio v2.0.1

**English (current)** · [简体中文](README.md)

> Nature-style academic writing Skill: based on a knowledge base distilled from Nature-tier flagship papers, rewrites any scientific text (Chinese or English draft) into top-tier journal style English.

## One-line install

In Codex, say:

```powershell
Please install the Skill located at https://github.com/mumdark/nature-writing-studio
```

Total size about **15 MB** (13 TSV knowledge bases + 10 prompts).

## Layout

```
nature-writing-studio/
├── README.md          <- this file (GitHub landing)
├── README_EN.md
├── skill/             <- Codex skill root
    ├── SKILL.md       <- Codex entry; all internal paths are relative to this directory
    ├── agents/openai.yaml
    ├── knowledge/     <- 13 TSVs
    ├── prompts/       <- 10 prompts
    ├── scripts/       <- sanity validator
    ├── docs/          <- roadmap
    ├── fixtures/      <- Chinese test fixture
    ├── CHANGELOG.md
```

## Codex invocation examples

```markdown
Prompt:
$Nature Writing Studio Rewrite the following sentence to English: We used CRISPRi to screen 287 transcription factors and identified ZNF219, a previously uncharacterized transcription factor that represses neural differentiation.
```

Every call returns **three deliverables**:

| Field | Meaning | When to use |
|---|---|---|
| `text` | Main text (Nature-style English) | Directly for submission / polished draft |
| `text_compact` | Compact version (60-70% length) | Submission word limits / quick preview |
| `summary` | Rewrite metadata: which rules applied, which AI-tells avoided, section and domain | Self-check / debug |


## Core design and functionality

The skill has four core designs, as follows:

#### 1. Real Nature article distillation

Rather than letting LLM improvise, the skill extracts real writing patterns from Nature flagship papers section by section, then picks the best-matching sentence templates based on section-level context. Specifically, five types of signals are captured:

- **Section-opening 3-grams** (10,488 kinds) — for example, the highest-frequency opener in abstract sections is `here we` (appears in 279 papers).
- **Within-section transition templates** (1,668 kinds) — for example, `Although X, Y.` appears in 15 out of 15 papers in introduction sections.
- **Verb tiering by evidence strength** (124 kinds) — for example, causal (strong) -> `show` / `demonstrate` / `identify`; associative (medium) -> `suggest` / `indicate` / `support`; speculative (weak) -> `may` / `could` / `possibly`.
- **Cross-section linking templates** (1,766 kinds) — for example, intro -> results uses `Having established X, we next asked whether Y` (50 papers).
- **Results section opening sentences** (4,864 kinds) — for example, `To characterize X, we performed Y`.

Total: 19,378 writing patterns.

#### 2. Logic line extraction

Writing logic (logic_line) mapped from the input's recognizable structure (method + finding + significance), and explicitly output to the summary.

For example, with the input above: "We used CRISPRi to screen 287 transcription factors and identified ZNF219, a previously uncharacterized transcription factor that represses neural differentiation."

The output text is: "Here we applied CRISPRi screening to a panel of 287 transcription factors (TFs) and identified ZNF219, a previously uncharacterized TF, as a repressor of neural differentiation."

The corresponding logic_line output is: "screen -> single hit -> mechanism"

#### 3. Modular writing + agent auto-identification

The skill doesn't rewrite the entire text at once; instead it rewrites by paper module independently (auto-identification). It also provides a `multi_section` mode where the agent **automatically** identifies the content and rewrites a complete multi-section paper based on the input:

| Module | Purpose | Input length suggestion |
|---|---|---|
| `abstract` | Abstract rewrite | 100-250 characters |
| `introduction` | Introduction rewrite | 300-800 characters |
| `methods` | Methods rewrite | 200-500 characters |
| `results` | Results rewrite | 300-800 characters |
| `discussion` | Discussion rewrite | 300-600 characters |
| `figure_legend` | Figure legend rewrite | 50-150 characters |
| `sentence` | Sentence-level polish (shortest input) | Any |
| `multi_section` | Multi-paragraph content | Any |

In multi_section mode, inputting an 800-character Chinese draft, the agent automatically identifies it as "results + discussion" type, applies the SP005 pattern (results + discussion stitching), and won't force an abstract.

#### 4. Anti-AI vocabulary via adversarial learning

When LLMs imitate Nature style, they always carry some "AI flavor" phrases. We based on 30 real articles' content logic, let LLM perform rewriting. Using the real articles' content as negative control, we extracted 136 AI-tells (commonly used AI words) from the LLM-written articles, **always forbidden** during rewriting. Three tiers:

| Level | Count | Typical examples |
|---|---|---|
| **Severe AI-tells** (must replace) | 40 | `delve into` / `navigate the complexities of` / `shed light on` / `key role in` |
| **Replacement AI-tells** (prefer swapping back to base words) | 127 | `leverage` / `utilize` / `robust` / `comprehensive` |
| **Mild AI-tells** (just polish away) | 124 | `It's worth noting that` / `Importantly` / `It is important to note` |

The enforcement mechanism is in the [Verification Layer](#verification-layer) — not a soft rule.

### How to invoke

Two invocation modes, choose based on need or let the agent auto-detect:

**Single-section rewrite (single_section)**: Pick one of the 7 `target`s, pass in the corresponding section's draft, get back the three deliverables.

**Full-draft orchestration (multi_section)**: Pass in the entire draft, the agent automatically identifies the section structure, rewrites section by section, runs cross-section consistency audit (X001-X010), returns per-section JSON + `meta` object (`version_used` / `logic_line` / `entity_registry` / `cross_section`).

The 7 single_section interfaces share the same prompt template `prompts/sections/<target>.txt`; multi_section uses a dedicated orchestrator `prompts/sections/multi_section.txt`.

## Distillation output overview

### Phrasing / linking category

| TSV | One-line summary | Example |
|---|---|---|
| `opener_distribution.tsv` (10,488 rows) | Section-opening 3-grams | abstract: `here we` (387 hits / 279 papers) |
| `gap_transitions.tsv` (1,668 rows) | Within-section transition pivot words | introduction: `Although X, Y.` (15 hits / 15 papers) |
| `cross_section_linkers.tsv` (1,766 rows) | Cross-section linking templates | intro -> results: `Having established X, we next asked whether Y` (50 papers) |
| `hedge_verbs.tsv` (124 rows) | Verb tiering by evidence strength | associative tier: `suggest` (1,645 hits / 409 papers) |
| `results_discussion_openers.tsv` (4,864 rows) | Results / discussion section opening templates | results: `To characterize X, we performed Y.` (21 hits / 12 papers) |

### Paper structure / rules category

| TSV | One-line summary | Example |
|---|---|---|
| `paper_story_patterns.tsv` (12 rows) | Section patterns for the entire paper | SP001: abstract -> introduction -> results -> discussion -> methods (default) |
| `cross_section_rules.tsv` (10 rows) | Cross-section consistency rules for multi-section orchestration | X001: hedge cannot strengthen backward; abstract uses causal, discussion cannot upgrade back to causal |
| `inter_section_argue_chains.tsv` (21 rows, v3.1 proto) | 3-step argumentative chain (claim -> evidence -> hedge) | Experiment-style paragraph: claim_verb=`show` -> evidence_verb=`identify` -> hedge_verb=`suggest` |

### Writing rules / phrases category

| TSV | One-line summary | Example |
|---|---|---|
| `writing_rules.tsv` (85 rows) | Nature writing rule ID set | R001: active voice; R023: numerals >= 10 use Arabic, 1-9 spelled out |
| `phrase_bank.tsv` (134 rows) | Reusable phrase templates | "Taken together, these findings..." |
| `anti_ai_patterns.tsv` (136 rows) | AI-tell blacklist | See core design 2 above |
| `domain_register.tsv` (46 rows) | Register for 22 biology sub-domains | genomics uses less passive, CRISPR class uses active |
| `sentence_stats_by_domain.tsv` (24 rows) | Real sentence-length statistics per domain | genomics abstract averages 23 words / sentence |

13 TSVs total 19,378 pattern rows. Each row has at least one Nature paper DOI as source anchor; rewrites select the best-matching sentence templates based on section-level context, not LLM improvisation.

## Verification Layer

After rewriting, before output, the skill passes through a verification layer where the agent quality-checks the content to avoid fabricated information. **5 rules in fixed order**:

| Rule | Function | Hit example |
|---|---|---|
| **1a Traceability (HARD)** | Figure numbers, citation tokens, numerical values, organism / tissue / cell-type etc. biological entities in output must be traceable to same literal or synonym in input | Input doesn't mention "Fig. 3", output has "(Fig. 3)" -> delete |
| **1b General knowledge whitelist** | General scientific knowledge allowed to not appear in input | `alternative splicing` / `transcriptome` / `eukaryotes` don't need traceability |
| **2 em-dash zero tolerance** | Output must not contain U+2014 | "regulation—mediated by..." -> rewrite |
| **2.5 em-dash deterministic scrub** | Run `strip_em_dash()` once on each of `text` / `text_compact`; hard post-process | Same as above, mandatory |
| **4 Citation requirement** | Background claims in introduction must carry citations | "Several studies have shown..." without citations -> add [1] / [2] placeholders |

**Fix method**: First delete hallucinated tokens; if the sentence depends on the token, rewrite the sentence; other sections unchanged.

**Whitelist** (in rewrite lexicon, no traceability needed):
- **Connectives**: and / then / here / through / by / using / with / of / from / to / in / on / as / that
- **Common verbs**: show / identify / report / use / perform / measure / observe / suggest / demonstrate / establish / find
- **Common nouns**: sample / cell / data / figure / method / condition / group / replicate / trial / experiment / analysis
- **Domain-common entities**: CRISPR / CRISPRi / TF / RNA / DNA / mRNA / PCR

Tokens outside the whitelist must be traceable; untraceable = fabricated.

## 🤝 Contributions

Welcome to raise issues, suggestions, and submit Pull Requests!

For AI-related applications or collaborations, please reach out:
- 307686155@qq.com
