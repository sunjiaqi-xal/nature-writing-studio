# Provenance (auto-generated)

generated: 2026-07-21

- n_observation_rows: 657
- n_adversarial_rows: 30

- writing_rules.tsv: {'rows': 85, 'distilled_added': 25, 'prior_retained': 60}
- phrase_bank.tsv: {'rows': 134, 'distilled_added': 12, 'prior_retained': 122}
- anti_ai_patterns.tsv: {'rows': 135, 'distilled_added': 3, 'prior_retained': 132}
- domain_register.tsv: {'rows': 46, 'distilled_added': 24, 'prior_retained': 22}
- sentence_stats_by_domain.tsv: {'rows': 24}

### Deterministic AI distillation (v3, 412 unique papers)
- Source: MiniMax-M3 per-paper observation of .evidence_packet.md files (415 JSONL records, 412 unique DOIs)
- Driver: distillation/v2/scripts/deterministic_distill.py (LCS-based quote validation, ratio >= 0.5)
- Aggregator: distillation/v2/scripts/aggregate_deterministic.py
- Output: 5 TSVs (gap_transitions 1668 rows, opener_distribution 10488, cross_section_linkers 1670, hedge_verbs 124, results_discussion_openers 4864)
- Spot-check: distillation/v2/scripts/spot_check_quotes.py - 18/18 (100%) verified against original .evidence_packet.md
