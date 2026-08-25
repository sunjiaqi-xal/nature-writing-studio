# Changelog

## v2.0.1+v3.1-active (2026-08-25)

The active development line. Working copy: 
ature-writing-studio_v2.0.1/.
Install path: C:\Users\30768\.codex\skills\nature-writing-studio\.
Frozen release snapshot: elease/nature-writing-studio_v2.0.1-active_2026-08-25/.

### Added since v2.0.0

#### v3 layer (knowledge base, deterministic TSVs distilled by MiniMax-M3 from 412 Nature papers)

- knowledge/gap_transitions.tsv (1668 rows) - within-section pivot-word templates indexed by (section, pivot_word).
- knowledge/opener_distribution.tsv (10488 rows) - section-scoped 3-gram openers. Top finding: here we opens 279/412 abstracts.
- knowledge/cross_section_linkers.tsv (1670 rows) - first-sentence cross-section bridge patterns. Top: Having established X, we next asked whether Y (intro->results, 50 papers).
- knowledge/hedge_verbs.tsv (124 rows) - causal / associative / speculative verb-tier priors. suggest 1645/409, show 1379/401.
- knowledge/results_discussion_openers.tsv (4864 rows) - results/discussion first-sentence templates.

Validation: 18/18 spot-check pass (LCS ratio >= 0.5).

#### v3.1 proto seed (added 2026-08-25)

- knowledge/inter_section_argue_chains.tsv (21 rows, v3.1 proto) - 3-step argumentative chain (claim_verb, evidence_verb, hedge_verb, tier) derived from existing v3 TSVs (not a fresh 412-paper LLM observation pass). Some claim_verb=y rows are honest placeholders. See docs/ROADMAP_v3.md for the full-distillation plan.

#### Tooling

- scripts/run_e2e_sanity.py (6KB) - CLI with three subcommands:
  - alidate: checks openai.yaml routing + TSV row counts against knowledge_summary.
  - inspect <fixture.txt>: lists per-section TSV candidates the section prompt would load.
  - probe: top-5 rows of every v3 TSV.
- ixtures/zh_splicing.txt - a real Chinese abstract fixture for end-to-end demo.
- distillation/v3/ - infrastructure for a full Direction A distillation:
  - data/selected_20.txt - 20 highest-aw_chars papers with all four sections present.
  - scripts/slice_sections.py / slice_bridges.py - mechanical section slicing (not AI extraction).
  - data/slices/*.slice.txt - 20 sliced papers (head/tail per section).
  - data/bridges.tsv - 40 bridge records.

#### Documentation

- docs/ROADMAP_v3.md (7KB) - three proposed v3 directions + status table.

### Fixed (caught by sanity tool, 2026-08-25)

- skill/agents/openai.yaml:
  - equired_files was missing the skill/ prefix on SKILL.md -> now skill/SKILL.md.
  - knowledge_summary.anti_ai_patterns.rows was 135, actual file has 136 data rows -> corrected to 136.
  - knowledge_summary.v3_deterministic block added.
  - distillation_provenance.v3_layer block added.
  - inter_section_argue_chains.tsv added to equired_files as v3.1 proto.

### Verification

- python scripts/run_e2e_sanity.py validate -> PASS - v2.0.1 routing intact, all TSV counts match knowledge_summary.
- All 5 v3 TSVs + openai.yaml SHA256 match between working copy and ~/.codex/skills/nature-writing-studio/.

## v2.0.0 (2026-07-27)

Release snapshot at elease/nature-writing-studio_v2.0.0-release_2026-07-27_21-03/.

- Refactored gents/openai.yaml as single source of truth.
- Same 5 hand-curated TSVs (writing_rules / phrase_bank / anti_ai_patterns / domain_register / paper_story_patterns).
- Added multi_section.txt orchestrator.

## v1.x (legacy, 2026-07-06 - 2026-08-13)

Superseded. Frozen at elease/nature-writing_v1.x-legacy_2026-08-25/.
ARCHIVED.md in that directory explains why and points to the v2 line.