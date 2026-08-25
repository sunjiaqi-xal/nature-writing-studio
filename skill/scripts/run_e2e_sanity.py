#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_e2e_sanity.py - nature-writing-studio v2.0.1 sanity tool."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

SKILL_ROOT = Path(__file__).resolve().parent.parent
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
KNOWLEDGE = SKILL_ROOT / "knowledge"

V3_TSVS = ["gap_transitions.tsv","opener_distribution.tsv","cross_section_linkers.tsv","hedge_verbs.tsv","results_discussion_openers.tsv"]

TSV_SNIPPET_COL = {
    "gap_transitions.tsv": "template",
    "opener_distribution.tsv": "opener_3gram",
    "cross_section_linkers.tsv": "pattern",
    "hedge_verbs.tsv": "verb",
    "results_discussion_openers.tsv": "opener_template",
}

SECTION_TSV_MAP = {
    "abstract": [
        ("gap_transitions.tsv","section","abstract"),
        ("opener_distribution.tsv","section","abstract"),
        ("hedge_verbs.tsv","tier",None),
    ],
    "introduction": [
        ("gap_transitions.tsv","section","introduction"),
        ("opener_distribution.tsv","section","introduction"),
        ("cross_section_linkers.tsv","from_section","introduction"),
    ],
    "methods": [("opener_distribution.tsv","section","methods")],
    "results": [
        ("opener_distribution.tsv","section","results"),
        ("results_discussion_openers.tsv","section","results"),
        ("hedge_verbs.tsv","tier",None),
    ],
    "discussion": [
        ("gap_transitions.tsv","section","discussion"),
        ("opener_distribution.tsv","section","discussion"),
        ("cross_section_linkers.tsv","from_section","discussion"),
        ("results_discussion_openers.tsv","section","discussion"),
    ],
    "figure_legend": [("opener_distribution.tsv","section","figure_legend")],
    "sentence": [],
}

def read_tsv(path):
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return [], []
    header = lines[0].split("\t")
    rows = []
    for ln in lines[1:]:
        cells = ln.split("\t")
        rows.append({h: (cells[i] if i < len(cells) else "") for i, h in enumerate(header)})
    return header, rows

def load_openai_yaml():
    return yaml.safe_load(OPENAI_YAML.read_text(encoding="utf-8"))

def cmd_validate(_):
    cfg = load_openai_yaml()
    fails = []
    for rel in cfg.get("required_files", []):
        rel_path = rel.replace("<target>","sentence")
        target = SKILL_ROOT / rel_path
        if not target.exists():
            fails.append(f"missing required_file: {rel}")
    summary = cfg.get("knowledge_summary", {})
    for key, val in summary.items():
        if not isinstance(val, dict) or "rows" not in val:
            continue
        tsv_path = KNOWLEDGE / f"{key}.tsv"
        if not tsv_path.exists():
            fails.append(f"knowledge_summary key '{key}' references missing TSV")
            continue
        actual = sum(1 for _ in tsv_path.read_text(encoding="utf-8").splitlines() if _.strip()) - 1
        if actual != val["rows"]:
            fails.append(f"row count mismatch: {key}.tsv summary={val['rows']} actual={actual}")
    if "v3_deterministic" not in summary:
        fails.append("knowledge_summary.v3_deterministic block missing")
    if "v3_layer" not in cfg.get("distillation_provenance", {}):
        fails.append("distillation_provenance.v3_layer block missing")
    for tsv in V3_TSVS:
        p = KNOWLEDGE / tsv
        if not p.exists():
            fails.append(f"v3 TSV missing: {tsv}")
            continue
        _, rows = read_tsv(p)
        if not rows:
            fails.append(f"v3 TSV empty: {tsv}")
    if fails:
        print("FAIL")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS - v2.0.1 routing intact, all TSV counts match knowledge_summary.")
    return 0

def cmd_inspect(args):
    fixture = Path(args.fixture)
    if not fixture.exists():
        print(f"fixture not found: {fixture}", file=sys.stderr)
        return 1
    text = fixture.read_text(encoding="utf-8")
    print(f"Fixture: {fixture}")
    print(f"Length:  {len(text)} chars, {len(text.split())} whitespace tokens")
    print(f"First 80 chars: {text[:80].strip()!r}")
    print()
    for section, tsv_specs in SECTION_TSV_MAP.items():
        if not tsv_specs:
            print(f"[{section}] (no v3 TSV prior)")
            continue
        print(f"[{section}]")
        for tsv_name, col, want in tsv_specs:
            _, rows = read_tsv(KNOWLEDGE / tsv_name)
            hits = rows if want is None else [r for r in rows if r.get(col) == want]
            snip = TSV_SNIPPET_COL.get(tsv_name, "")
            print(f"  {tsv_name:36s} filter={col}={want!s:14s} -> {len(hits):5d} candidate rows")
            for r in hits[:2]:
                snippet = (r.get(snip) or "").replace("\t"," ")[:90]
                print(f"      - {snippet}")
        print()
    return 0

def cmd_probe(_):
    for tsv in V3_TSVS:
        path = KNOWLEDGE / tsv
        header, rows = read_tsv(path)
        print(f"==== {tsv} ({len(rows)} rows) ====")
        print(f"  cols: {header}")
        for r in rows[:5]:
            show = {k: ((v[:80]+"...") if len(v)>80 else v) for k,v in r.items()}
            print(f"  {show}")
        print()
    return 0

def main():
    p = argparse.ArgumentParser(description="nature-writing-studio v2.0.1 sanity tool")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate", help="check openai.yaml routing + TSV row counts")
    pi = sub.add_parser("inspect", help="list per-section TSV priors for a fixture")
    pi.add_argument("fixture", help="path to a Chinese or English draft fixture")
    sub.add_parser("probe", help="top-5 rows of every v3 TSV")
    args = p.parse_args()
    return {"validate": cmd_validate, "inspect": cmd_inspect, "probe": cmd_probe}[args.cmd](args)

if __name__ == "__main__":
    sys.exit(main())