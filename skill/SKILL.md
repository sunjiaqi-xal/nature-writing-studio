---
name: nature-writing-studio
description: >-
  Rewrite scientific text into Nature Portfolio English using a knowledge base
  distilled from 657 Nature family papers via per-paper LLM observation (87.6% coverage), now extended with
  5 deterministic AI-observation TSVs (gap_transitions / opener_distribution / cross_section_linkers / hedge_verbs
  / results_discussion_openers) from 412 v3 Nature papers via MiniMax-M3 per-paper observation.
  Trigger for Nature-style polish, Chinese-to-English Nature translation,
  anti-AI cleanup (remove delve-into / navigate-complexities / shed-light-on /
  key role), single-section drafting (abstract / introduction / methods / results /
  discussion / figure_legend / sentence), and full-paper multi-section orchestration
  (target=multi_section: 7 section-prompt invocations driven by a logic-line +
  story-arc + entity-registry pre-step, a 10-rule cross-section audit, and a
  shared-context fence prepended to each section). Returns inline Markdown with text + text_compact + summary per section (no file write by default; switch to JSON or DOCX only on explicit user request). For multi_section, returns per-section blocks plus a top-level meta line with version_used, logic_line, entity_registry, cross_section, and degraded. Knowledge base: 95 writing rules (52 prior + 24 distilled + 9 pre-existing data-quality rows + 10 v2.0.1
  cross-section), 134 phrase templates (122 prior + 12 distilled), 136 AI-tell blacklists (133 prior + 3 from
  30-paper adversarial), 46 domain registers (22 prior + 24 distilled), 12 Nature story-pattern templates,
  24 per-domain sentence-stats rows, plus 5 deterministic v3 TSVs: gap_transitions (1668 templates from
  412 papers), opener_distribution (10488 3-grams), cross_section_linkers (1766 patterns, 96 new paragraph-level bridges from 414 Nature v3 papers via agent extraction),
  hedge_verbs (124 verb-tier clusters), results_discussion_openers (4864 templates).
version: 2.0.1
inputs:
  - input_text (string)
  - target (abstract | introduction | methods | results | discussion | figure_legend | sentence | multi_section)
  - domain (one of 22 domain_register.tsv values, or general_nature; optional)
outputs:
  - text (Nature-level prose)
  - text_compact (60-70% length)
  - summary (logic_line + rules_applied + patterns_used + ai_tells_avoided + section + domain)
references:
  - prompts/system_writer.txt
  - prompts/style_guide.txt
  - prompts/sections/<target>.txt
  - knowledge/writing_rules.tsv
  - knowledge/phrase_bank.tsv
  - knowledge/anti_ai_patterns.tsv
  - knowledge/domain_register.tsv
  - knowledge/paper_story_patterns.tsv
  - prompts/sections/multi_section.txt
  - knowledge/cross_section_rules.tsv
  - knowledge/gap_transitions.tsv
  - knowledge/opener_distribution.tsv
  - knowledge/cross_section_linkers.tsv
  - knowledge/hedge_verbs.tsv
  - knowledge/results_discussion_openers.tsv
  - scripts/run_e2e_sanity.py
  - docs/ROADMAP_v3.md
  - knowledge/inter_section_argue_chains.tsv  # v3.1 proto seed (21 rows), not in live routing
---
# nature-writing

> Codex / Claude Code skill that rewrites scientific text into Nature Portfolio English.
> Distilled from 750 Nature family papers + editorial style guidelines.
> Knowledge base: 60 writing rules, 122 phrases, 132 AI-tell blacklist, 22 domain registers, 12 section skeletons.

## What this skill does

Given any user-supplied scientific text - claim list, methods paragraph, draft abstract, full intro - produce:

1. **`text`** - Nature-level English rewrite.
2. **`text_compact`** - tighter 60-70% length version for comparison.
3. **`summary`** - metadata including:
   - `logic_line`: the reasoning behind the rewrite
   - `rules_applied`: rule IDs (R001-) from `knowledge/writing_rules.tsv`
   - `patterns_used`: phrase IDs (P001-) from `knowledge/phrase_bank.tsv`
   - `ai_tells_avoided`: AI-tell patterns removed
   - `section`: target section type
   - `domain`: inferred or provided domain

When `target=multi_section`, the orchestrator instead produces per-section blocks plus a top-level `meta` line containing `version_used`, `logic_line`, `entity_registry`, `cross_section` audit, and an optional `degraded` flag. The agent (or human-facing layer) is responsible for stitching the per-section `text` and `text_compact` strings into two final full-paper versions.

## When to use this skill

Trigger when the user asks for any of:
- Nature-style writing, polish, rewrite, translate (Chinese -> Nature English), restructure
- Academic writing upgrade ("make it sound like Nature")
- Section drafts: abstract, introduction, methods, results, discussion, figure legend
- Sentence-level polish: turn a single Chinese sentence into Nature-grade English
- Multi-section writing: when the user supplies a full draft (Chinese or English) and wants a Nature-style full paper; produces per-section Markdown blocks + a `summary` line that an external agent stitches into two full-paper versions
- Anti-AI cleanup: remove `delve into`, `navigate complexities`, etc.
- Domain-specific drafting (physics / biology / medicine / materials / etc.)

## Calling convention

The skill expects input shaped like:

```
input: <the text to rewrite>
target: <abstract | introduction | methods | results | discussion | figure_legend | sentence>
domain: <physics_condensed | biology_neuro | medicine_oncology | ... | general_nature>  (optional)
```

For sentence-level polish, `target = sentence` and `input` can be a single sentence or short phrase.

For full-paper orchestration:

```
target: multi_section
input: <full draft, Chinese or English, no section markers required>
domain: <optional>
```

The `multi_section` target invokes `prompts/sections/multi_section.txt` as an orchestrator. It auto-selects a section sequence (SP001 default), forces a `logic_line` + `story_arc` + `entity_registry` pre-step, invokes the per-section prompts with a shared context, and emits per-section Markdown blocks plus a `summary` line. The external agent (or human-facing layer) stitches the per-section `text` and `text_compact` into two final full-paper versions.

## Operating procedure (for the agent)

1. **Load** `prompts/system_writer.txt` and `prompts/style_guide.txt`.
2. **Load** the section-specific prompt from `prompts/sections/<target>.txt`.
3. **Read** `knowledge/writing_rules.tsv` (60 rules), `phrase_bank.tsv` (122 phrases), `anti_ai_patterns.tsv` (132 blacklist), `domain_register.tsv` (if domain specified).
4. **Rewrite** the input following the section architecture and hedge tiers.
5. **Anti-AI scan**: substitute or delete any phrase matching `anti_ai_patterns.tsv`.
6. **Render** the result with the full output contract (text, text_compact, summary).
7. **Self-check** against the criteria in `style_guide.txt` "Quick Sanity Check Before Returning".
8. **Multi-section orchestration** (only when `target=multi_section`). Read `prompts/sections/multi_section.txt` and `knowledge/cross_section_rules.tsv`. Then:
   - Select the section sequence via the orchestrator's auto-version-selection (SP001 default).
   - Produce `logic_line` + `story_arc` + `entity_registry` as a hard prereq before any section writing.
   - Build a `shared_context` object and prepend it (fenced) to each section's input slice.
   - Invoke the matching per-section prompt for each section in version order.
   - Run the existing Verification Layer per section; re-run once on failure with corrected context.
   - After all sections, run the cross-section audit (entity diff, hedge ladder, citation gaps, abbreviation drift, transition breaks, numeric format, reference density) and emit `meta.cross_section`.
   - Return inline Markdown blocks in the same shape as the single-section example, with per-section `## text` / `## text_compact` / `## summary` followed by a `## meta` block listing `version_used`, `logic_line`, `entity_registry`, `cross_section`, `degraded`. Do **not** stitch prose; the agent does that.
9. **Verify (Verification Layer, anti-fabrication)**: run the Verification Layer defined in `prompts/system_writer.txt` (Rule 1a / 1b / 2 / 2.5 / 3). Two tiers of traceability:
   - **Rule 1a (HARD, must trace to input)**: any data claim about the user's study — data, statistics, sample sizes, time points, figure / citation tokens, user-specific identifiers (gene variants, cell line IDs, dataset accessions), user-stated conditions. A non-traceable data token IS fabrication; drop it.
   - **Rule 1b (SOFT, allow freely)**: established scientific knowledge (mechanisms like `alternative splicing` or `gene regulation`, well-known pathways like `Wnt` or `MAPK`, model organisms as background, generic tissue / cell-type categories, generic phenotype / process terms). These set up the user's specific finding and are NEVER fabrication.
   - **Decision rule**: if the token would still be a true statement if you replaced the user's specific gene / number / cell with someone else's — it is Rule 1b (allow). If removing the user's input would make the sentence false — it is Rule 1a (must trace).
   - Treat em-dash (U+2014) as fabrication (Rule 2). The audit field is `summary.untraceable_tokens` — empty array `[]` = pass; non-empty = fabrication was found, the rewrite must be redone. In multi_section mode, the offending section is set to `text=null` and listed in `meta.degraded`. See the worked examples for delete-only, delete-plus-rewrite, and general-knowledge-allowed cases.

10. **Em-dash scrub (deterministic)**: after the Verification Layer passes, run the `strip_em_dash()` function from `prompts/system_writer.txt` Rule 2.5 on `text` and `text_compact` independently. This is a hard post-process, not a soft rule, and runs AFTER every LLM pass. The returned `text` and `text_compact` MUST contain zero U+2014. If the substitution breaks a sentence (e.g., starting with `, `), re-split at the sentence boundary. Do not invent new content to fix artifacts.

## Output contract

```markdown
## text
<Nature-level prose>

## text_compact
<tighter 60-70% length version>

## summary
- section: abstract
- domain: biology_neuro
- logic_line: <1-2 sentences>
- rules_applied: [R001, R005]
- patterns_used: [P005, P008]
- ai_tells_avoided: [delve_into, in_this_paper]
```

Default is inline Markdown. Switch to JSON or write to file only on explicit user request (e.g., "output as JSON", "save to .docx").


When `target=multi_section`, the output shape changes:

```markdown
## text
<abstract text> ... <methods text>     (stitched by the orchestrator)

## text_compact
<abstract text_compact> ... <methods text_compact>

## summary
- mode: multi_section
- version_used: SP001
    "logic_line": "<single sentence>",
    "entity_registry": [...],
    "cross_section": {"entity_diff": [], "hedge_violations": [], "citation_gaps": [], "abbreviation_drift": [], "transition_breaks": [], "numeric_format_drift": [], "reference_density": [], "overall": "PASS"},
    "degraded": null
  }
}
```

The agent (or human-facing layer) iterates `sections` in order and concatenates each section's `text` (separated by blank lines) into one final `text`, then concatenates each section's `text_compact` into one final `text_compact`. Render both stitched versions for the user to read.

## Example

User input (Chinese):
> 我们用CRISPRi 筛选了 287 个转录因子，找到 ZNF219 这个之前没报道过的转录因子，它抑制神经分化。
Skill output (Nature):
> Here we applied CRISPRi screening to a panel of 287 transcription factors (TFs) and identified ZNF219, a previously uncharacterized TF, as a repressor of neural differentiation.

Summary: `Logic: open with Here + method + scale; lead finding identifies a previously uncharacterized TF. Rules applied: R005 (Here we), R008 (hedge), R017 (avoid novel overuse). Patterns: P010, P013. AI-tells avoided: none (input was clean). Section: sentence. Domain: biology_neuro.`
Verification: `0 em-dash; 0 fabricated tokens; pass.` All tokens trace to the input (287, CRISPRi, ZNF219, transcription factor, repressor, neural differentiation).

## Figure and Citation Placeholders

When the user input has no figure numbers or citations, insert explicit placeholders in the prose:
- Figures: `(Fig. X)`, `(Extended Data Fig. X)`, `(Fig. 1a, b)` (use literal `X` if not assigned).
- Citations: `[citation needed]`, `[1]`, `[2]`, or numeric superscript placeholders like `[1-]`.
- Statistics: `[n = TBD]`, `[P = TBD]`.

Never silently omit. Placeholders are honest; omission invites fabrication risk.

## text vs text_compact

- `text`: full prose with hedges, parenthetical asides, calibrated redundancy.
- `text_compact`: 60-70% length. Drops parenthetical caveats and one of paired redundant clauses. Keeps lead claim, mechanism, anchor citations, and all anti-AI fixes.

The two versions must differ measurably - at least 20% length difference or 2 substantive cuts.

For multi-section orchestration, the stitched `text` is the concatenation of every section's `text`, and the stitched `text_compact` is the concatenation of every section's `text_compact`; the overall length ratio is preserved.

## Anti-AI precision

The word `key` is allowed in some Nature contexts (`key result`, `key step`, `key parameter`). It is AI-tell ONLY when collocated with `key player`, `key regulator`, `key insight`, `key step toward`, `key role`. See `knowledge/anti_ai_patterns.tsv` for the precise regex.
