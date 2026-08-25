# v3 Section-Bridging Roadmap (proposed)

## Why this document


ature-writing-studio v2.0.1 already ships **five intra-section TSVs**:

- gap_transitions.tsv (1668 rows) — within-section pivot-word templates
- opener_distribution.tsv (10488 rows) — section-scoped 3-gram openers
- cross_section_linkers.tsv (1670 rows) — first cross-section bridge layer
- hedge_verbs.tsv (124 rows) — causal / associative / speculative tier priors
- esults_discussion_openers.tsv (4864 rows) — section-scoped openers

These cover the **within-section** and **first bridge** levels. The next
gap is **inter-section argumentative logic**: how the body of one section
talks to the body of the next (not just the first sentence after a heading).
That is what this document proposes to distill.

## Scope decision (must be approved before we start)

Three candidate directions. Pick at most one for v3:

### Direction A — Section-bridging argumentative templates (recommended)

**Output**: 2 new TSVs.

- inter_section_bridges.tsv — sentence templates that *body-paragraph*
  bridges carry, indexed by (from_section, to_section, function) where
  unction in {setup_to_question, finding_to_interpretation,
  method_to_validation, limitation_to_future}.
- inter_section_argue_chains.tsv — 3-step chain templates
  (claim_verb → evidence_verb → hedge_verb) such as
  identify → demonstrate → suggest (causal) or
  observe → consistent_with → may (associative).

**Source**: re-observe the 412 papers in

ature-writing-build/work/papers_clean/ whose .evidence_packet.md
files were used for the v3 layer. Each paper yields one bundle of
"first paragraph after heading N -> last paragraph before heading N+1"
pairs.

**Cost**: estimated ~25k tokens for one full pass, plus 5k for aggregation
and 5k for spot-check. **Total ~35k tokens**.

**Value**: closes the inter-section gap so the skill can chain introduction
question -> methods answer -> results answer -> discussion implication
without the agent having to invent transitions.

### Direction B — Adversarial / low-quality exemplars

**Output**: 1 new TSV.

- nti_ai_v2.tsv — rows where the per-paper observer found an expression
  a Nature editor would strike. Each row carries (pattern, original_quote,
  editor_rationale, severity).

**Source**: same 412 papers, re-prompted to mark **red-pen** language.

**Cost**: ~30k tokens.

**Value**: makes nti_ai_patterns.tsv (currently a hand-curated blacklist)
backed by real corpus evidence. Stronger guarantee than v1.

### Direction C — End-to-end orchestration report (no new TSVs)

**Output**: 1 markdown report per full-paper run.

- 2e_runs/<fixture>.report.md — per-section TSV rows the skill would
  load, expected hedge tier, fabricated-numbers scan, intra/inter-section
  link presence.

**Source**: drive the existing v2.0.1 wiring over the user's "pig
alternative-splicing" fixture (already in ixtures/zh_splicing.txt)
through scripts/run_e2e_sanity.py and emit the report.

**Cost**: ~5k tokens (no LLM calls beyond the sanity script, which itself
does not invoke the model — only reads the knowledge base).

**Value**: zero new corpus work; turns the v2.0.1 wiring into a
reproducible audit. Already 80% done after scripts/run_e2e_sanity.py
inspect fixtures/zh_splicing.txt.

## Recommendation

Ship **A** in v3.0.0 (the gap is real), keep **B** in reserve for v3.1.0
(needs an editor-style rubric prompt — design overhead is bigger than the
TSV itself), and run **C** *now* as the v2.0.1 close-out so we have a
concrete "before" baseline to compare v3.0.0 against.

## Status (as of 2026-08-25)

- [x] C: scripts/run_e2e_sanity.py shipped + validate / inspect / probe
      subcommands wired.
- [ ] C: ixtures/zh_splicing.txt e2e report committed (Step 2d).
- [ ] A: design prompt v1 for inter-section bridge observation.
- [ ] A: driver script (reuse distillation/v2/scripts/deterministic_distill.py
      with new prompt).
- [ ] A: aggregate, spot-check, patch openai.yaml + sections prompts.
- [ ] B: design editor-red-pen prompt (v3.1).

## How to drive A when approved

1. Write distillation/v3/prompts/bridge_observation.md (per-paper prompt).
2. Reuse distillation/v2/scripts/deterministic_distill.py with new
   prompt + new output schema.
3. Reuse distillation/v2/scripts/aggregate_deterministic.py.
4. Reuse distillation/v2/scripts/spot_check_quotes.py (LCS ratio >= 0.5).
5. Patch 
ature-writing-studio_v2.0.1/skill/agents/openai.yaml:
   - equired_files append the 2 new TSVs.
   - knowledge_summary.inter_section_* blocks.
   - distillation_provenance.v3_layer.inter_section_bridges.
6. Patch prompts/sections/multi_section.txt and per-section prompts.
7. Run python scripts/run_e2e_sanity.py validate until PASS.
8. Commit + sync ~/.codex/skills/nature-writing-studio/.

## Update 2026-08-25 (proto seed)

- [x] **Direction A proto seed** shipped: `knowledge/inter_section_argue_chains.tsv` with 21 rows.
  - Derived mechanically from the existing v3 `cross_section_linkers.tsv` (1670 rows) + `hedge_verbs.tsv` (124 rows). No new per-paper LLM observation pass.
  - Schema: `from_section / to_section / tier / claim_verb / evidence_verb / hedge_verb / total_occurrences / exemplar_pattern / source`.
  - Wired into `openai.yaml` `required_files` as a v3.1 proto, **not** into the live routing.
- [x] `scripts/run_e2e_sanity.py` validate / inspect / probe live in install path.
- [x] `fixtures/zh_splicing.txt` demo committed.

What this proto seed tells you at a glance:

| from -> to          | tier        | hedge verb  | total occ |
|---------------------|-------------|-------------|-----------|
| intro -> results    | associative | suggest     | 70        |
| intro -> results    | associative | suggest     | 60        |
| results -> disc.    | associative | suggest     | 57        |
| results -> disc.    | associative | indicate    | 16        |
| results -> disc.    | causal      | demonstrate | 10        |
| results -> disc.    | causal      | show        |  5        |

Some `claim_verb` / `evidence_verb` rows are `y` placeholders where the
underlying pattern itself was a Nature placeholder (`Using this approach,
we Y`). They are honest data, not errors; mark them as `y` so a downstream
LLM can decide to ignore them or back-fill them.

What is **not** in the proto seed and would need a real v3 distillation:

- Paragraph-internal bridges (mid-paragraph `Given X, ...` / `To test X, ...`)
- Function labels (setup_to_question / finding_to_interpretation / ...)
- Per-paper frequency weighting (current proto only carries occurrence sums)
- Discussion -> introduction back-references (currently `results -> introduction` only has 2 rows in cross_section_linkers; should likely be expanded)

Estimated cost for the missing parts: ~80k tokens across 20 selected papers
in `distillation/v3/data/selected_20.txt`, plus ~10k for aggregator +
spot-check + skill patch. Realistic on a fresh session.
