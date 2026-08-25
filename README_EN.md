# nature-writing-studio v2.0.1

[简体中文](README.md) · **English (current)**

> Nature-style academic writing Skill: rewrite any scientific text (Chinese or English draft) into Nature main-journal-style English.
> Distilled from **Nature main-journal articles (2025–2026)**; v2.0.1 adds a `multi_section` orchestration interface on top of v2.0.0 (2026-08-25: +96 paragraph-level bridges via v3 distillation).

## One-line install

In Codex, say:

```powershell
Please install the Skill located at C:\Users\30768\.codex\skills\nature-writing-studio
```

Total volume about **15 MB** (13 TSV knowledge bases + 10 prompts).

## Layout

This repo root is for GitHub readers; the Codex skill entry lives under `skill/`.

```
nature-writing-studio/
├── README.md          <- this file (GitHub landing)
├── README_EN.md
├── skill/             <- Codex skill root
    ├── SKILL.md       <- Codex entry; all internal paths are relative to this directory
    ├── agents/openai.yaml
    ├── knowledge/     <- 13 TSVs
    ├── prompts/       <- 9 prompts
    ├── scripts/       <- sanity validator
    ├── docs/          <- roadmap
    ├── fixtures/      <- Chinese test fixture
    ├── CHANGELOG.md
```

**Install into Codex**: copy the whole repo (or just the `skill/` subdir) to `~/.codex/skills/nature-writing-studio/`, keep the `skill/` subdirectory intact so Codex can locate the entry at `r0/nature-writing-studio/skill/SKILL.md`.

## Codex invocation examples

```md
$nature-writing-studio Rewrite the following Chinese to Nature-style English:
"We used CRISPRi to screen 287 transcription factors and identified ZNF219, a previously uncharacterized TF that represses neural differentiation."

$nature-writing-studio Help me orchestrate a full draft into Nature format (abstract→introduction→results→discussion→methods):
"input: <about 350 Chinese characters>
target: multi_section
domain: biology_genomics"
```

## Interfaces (target enum)

| Interface | Trigger | Output |
|---|---|---|
| `abstract` | Single-section rewrite: abstract | `text + text_compact + summary` |
| `introduction` | Single-section rewrite: introduction | same |
| `methods` | Single-section rewrite: methods | same |
| `results` | Single-section rewrite: results | same |
| `discussion` | Single-section rewrite: discussion | same |
| `figure_legend` | Single-section rewrite: figure legend | same |
| `sentence` | Sentence-level polish (shortest input) | same |
| `multi_section` (new in v2.0.1) | Full-draft orchestration | Per-section JSON + `meta` object (`version_used` / `logic_line` / `entity_registry` / cross-section audit) |

The 7 `single_section` interfaces share the same prompt template at `prompts/sections/<target>.txt`; `multi_section` runs `prompts/sections/multi_section.txt` as orchestrator and **does not pre-stitch prose** — the caller concatenates by SP format.

## Distillation output map

| Distilled artefact | Location | Purpose |
|---|---|---|
| 5 Nature phrasing / transition TSVs | `knowledge/*.tsv` (see below) | Decide "which phrasing / transition to use" |
| 3 hedge tiers (causal / associative / speculative) | `knowledge/hedge_verbs.tsv` | Decide "how strong a verb" |
| 10 cross-section rules (X001–X010) | `knowledge/cross_section_rules.tsv` | Decide "how to stay consistent across sections" |
| 4–12 SP formats (SP001–SP012) | `knowledge/paper_story_patterns.tsv` | Decide "section order in multi-section orchestration" |
| 1 anti-AI-tell blacklist | `knowledge/anti_ai_patterns.tsv` | Decide "phrasing that must never appear" |

### 1. Five Nature phrasing / transition TSVs (18,910 3-grams / patterns total)

**What it is**: Sentence-form and word-frequency statistics extracted directly from Nature full papers. The skill picks the best-matching phrasing by section position + context — no free-form LLM invention.

**Why five TSVs**: Each one answers one distinct "which phrasing" decision:

| TSV | Decision it answers | Rows |
|---|---|---|
| `gap_transitions.tsv` | Which pivot for in-section contrast | 1668 |
| `opener_distribution.tsv` | Which 3-gram at section opener (here we / by contrast / we show / ...) | 10488 |
| `cross_section_linkers.tsv` | Cross-section linking templates ("Having established X, we next asked Y" etc.) | **1766** (v2.0.1=1670, v3 paragraph-level bridge +96) |
| `hedge_verbs.tsv` | Verbs bucketed by evidence strength (causal → show / demonstrate; associative → suggest / indicate; speculative → may / could) | 124 |
| `results_discussion_openers.tsv` | Results-section opener templates ("To characterize X, we performed Y" etc.) | 4864 |

**Top samples**:

| Type | Top sample | Paper count |
|---|---|---|
| abstract opener | `here we` | 387 hits / 279 papers |
| results opener | `We found that X` | 21 hits / 12 papers |
| gap transition | `Although X, Y.` (introduction) | 15 hits / 15 papers |
| hedge verb | `suggest` (associative) | 1645 hits / 409 papers |
| cross-section linker | `Having established X, we next asked whether Y` (intro→results) | 50 papers |

### 2. Three hedge tiers (evidence strength bucketing)

**What it is**: For "we found X", different evidence strengths demand different verbs. The skill buckets verbs into 3 tiers and picks by context.

| Tier | Meaning | High-frequency verbs | Use where |
|---|---|---|---|
| **causal** | Direct cause / strong evidence | `show / demonstrate / establish / identify` | Only abstract + results core claims |
| **associative** | Correlation / moderate evidence | `suggest / indicate / appear / consistent with / support / imply` | Discussion main claims |
| **speculative** | Speculation / weak evidence | `may / could / might / possibly / probably / likely / hypothesize` | Outlook / future work |

**Why 3 not 2**: Two tiers (causal / non-causal) collapses everything else into non-causal, losing the "moderate evidence" bucket which is the most common in Nature discussion. Three tiers matches Nature's actual rhythm.

**Cross-section rule X001 hedge_ladder**: causal strongest in abstract + results, softens to associative in discussion, softens to speculative in outlook; **never escalates backwards** (discussion cannot be stronger than results). This rule is hard-coded as row 1 of `knowledge/cross_section_rules.tsv`.

### 3. Ten cross-section rules (X001–X010)

**What it is**: Consistency constraints the orchestrator must satisfy when stitching 5 sections into a full paper. Distilled from "cross-section fighting" issues Nature authors actually encounter.

| ID | Rule | TSV row |
|---|---|---|
| X001 hedge_ladder | causal → associative → speculative decays across sections; never escalates backwards | row 1 |
| X002 entity_continuity | Every number / abbreviation / gene / species / accession in `entity_registry` must be byte-identical across all sections that mention it | row 2 |
| X003 citation_numbering | Citation superscripts assigned by first appearance order; never reused; continuous across sections | row 3 |
| X004 abbreviation_expansion | First mention in full paper = full name + parenthetical abbreviation; afterwards abbreviation only; consistent across sections | row 4 |
| X005 methods_last | SP001 / SP002 / SP005 formats: `methods` is always last | row 5 |
| X006 transition_hooks | Section N's opener must echo Section N-1's closer in claim or entity | row 6 |
| X007 hedge_consistency | Same underlying claim must keep the same hedge tier across abstract / intro / results / discussion | row 7 |
| X008 logic_line_anchor | Each section's opener must trace to `logic_line` or `story_arc` | row 8 |
| X009 numeric_format | 10 and above use Arabic numerals, 1–9 spelled out; consistent within and across sections | row 9 |
| X010 reference_density_decay | Reference density: intro 5–10/section, results 0–2 (own data), discussion 1/paragraph | row 10 |

### 4. 4–12 SP formats (SP001–SP012)

**What it is**: The orchestrator picks a "section order template" by input length + section markers instead of mechanically abstract→intro→results→discussion→methods.

| Input signature | SP picked | Section order |
|---|---|---|
| >= 800 words + contains abstract / intro / results / discussion / methods markers | **SP001** (default) | abstract → introduction → results → discussion → methods |
| <= 600 words, no standalone abstract | SP002 | introduction → results → discussion → methods (inline abstract) |
| 400–800 words, results + methods only | SP005 | abstract → introduction → results → methods |

SP006–SP012 cover narrower scenarios (review / perspective / letter / corrigendum etc.) and are activated when the user explicitly passes `version=SP00X`.

### 5. One anti-AI-tell blacklist (136 patterns)

**What it is**: Phrases extracted from LLM-generated articles pretending to be Nature style. The skill **never** uses them.

| Category | Count | Examples |
|---|---|---|
| Severe AI-tell | 40 | `delve into` / `navigate the complexities of` / `shed light on` / `key role in` |
| Substitute AI-tell | 127 | `leverage` / `utilize` / `robust` / `comprehensive` |
| Minor AI-tell | 124 | `It's worth noting that` / `Importantly` / `It is important to note` |

Total **136 patterns** (some rows span multiple categories), recorded in `knowledge/anti_ai_patterns.tsv`.

**How it is enforced**: The Verification Layer's final step scans `text` + `text_compact`; any hit triggers a rewrite. This is hard enforcement, not a soft rule.

## Output contract

- **Every target produces three artefacts**: `text` (Nature-style English) + `text_compact` (60–70% length compressed version) + `summary` (rules hit + phrasings + verification result)
- **`multi_section` adds one more layer (meta)**: per-section JSON + `meta` (`version_used` / `logic_line` / `entity_registry` / cross-section audit / `degraded` flag)
- **Em-dash zero tolerance**: Neither `text` nor `text_compact` may contain U+2014 (—). The `strip_em_dash()` post-processor runs once on each string after the Verification Layer (hard post-process, not a soft rule)
- **Bold policy**: only used for headings, table headers, confidence rows, citation anchors; body body never is bold
- **Not emitted**: "preamble and compliance",", "claim→evidence map",", "coverage statement",", "adversarial self-check" and other internal blocks — they run inside the skill only, never reach files

### Verification Layer (acceptance check, final step)

5 rules in fixed order (runs AFTER anti-AI self-check, BEFORE returning to user):

1. **Rule 1a Traceability (HARD)**: Figure numbers, citation tokens, numerics (n / P / fold), and named biology entities (organism / tissue / cell-type / technique / time point) in output must trace to input's same literal / synonym; untraced = fabrication, delete
2. **Rule 1b General-knowledge allowlist**: General scientific knowledge (Tier B, e.g. `alternative splicing` / `transcriptome` / `eukaryotes`) is allowed without appearing in input; treated as background knowledge, no tracing required
3. **Rule 2 Em-dash zero tolerance**: Output must contain zero U+2014 (—); treated as fabrication-grade violation
4. **Rule 2.5 Em-dash deterministic scrub**: `text` and `text_compact` must each be post-processed by `strip_em_dash()` once; this is a hard post-process, not a soft rule; after execution `assert "—" not in text`
5. **Rule 4 Citation requirement**: Introduction's background claims must carry citations; missing citation = citation miss (NOT Tier B general knowledge), must be filled with `[1]` / `[2]` placeholders in `entity_registry`

**Repair procedure**: First delete hallucination tokens; if the sentence becomes mutilated, rewrite that sentence; leave other sections untouched.

**Traceability whitelist** (rewriter's dictionary, no tracing needed):
- Connectives: and / then / here / through / by / using / with / of / from / to / in / on / as / that
- Generic verbs: show / identify / report / use / perform / measure / observe / suggest / demonstrate / establish / find
- Generic nouns: sample / cell / data / figure / method / condition / group / replicate / trial / experiment / analysis
- Domain-generic entities: CRISPR / CRISPRi / TF / RNA / DNA / mRNA / PCR

Any token outside the whitelist must trace; untraceable = fabrication.

## Knowledge base scale

- **Distillation source**: Nature main-journal articles (2025–2026)
- **v3 paragraph-level bridge distillation** (2026-08-25): agent-extracted **96 new bridges** appended to `cross_section_linkers.tsv` (1670 → 1766); spot-check 18 random rows verified 16/18 = **89%** (LCS ≥ 0.5)
- **TSV total**: 13 files, **19,378 data rows** (gap_transitions 1668 + opener_distribution 10488 + cross_section_linkers 1766 + hedge_verbs 124 + results_discussion_openers 4864 + anti_ai_patterns 136 + cross_section_rules 10 + domain_register 46 + inter_section_argue_chains 21 + paper_story_patterns 12 + phrase_bank 134 + sentence_stats_by_domain 24 + writing_rules 85)
- **Prompt total**: 10 prompts (`style_guide.txt` + `system_writer.txt` + 8 sections/*.txt)
- **Adversarial samples**: LLM-pretending-Nature articles, **311 differences extracted** (40 severe + 127 substitute + 124 minor)

## 🤝 Contributions

Issues, suggestions and Pull Requests welcome!

For AI applications or collaboration, reach out:
- 307686155@qq.com
