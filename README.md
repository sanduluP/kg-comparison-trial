# KG Comparison Trial

Small baseline project for comparing two CSV-formatted knowledge graphs.

Each input CSV must contain:

```csv
subject,predicate,object
```

## Practical team scenario

This repo now supports a realistic review workflow for teams comparing exports
from different KG pipelines.

Example:
- pipeline A exports canonical values
- pipeline B exports the same facts with extra whitespace or casing changes
- the team wants to reduce false-positive diffs without hiding real differences

To support that workflow, whitespace normalization is the default, while
strict mode remains available for exact-identifier comparisons.

## Usage

Default comparison (whitespace-normalized):

```bash
python src/compare.py data/kg1.csv data/kg2.csv --out tmp/results_default
```

Exact comparison:

```bash
python src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv \
  --strict \
  --out tmp/results_strict
```

Whitespace + object-case normalization:

```bash
python src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv \
  --casefold \
  --out tmp/results_casefold
```

## Output files

- `summary.json`: overlap and conflict counts
- `triple_overlap.csv`: identical triples in both KGs
- `kg1_only.csv`: triples only in the first KG
- `kg2_only.csv`: triples only in the second KG
- `conflicts.csv`: same `(subject, predicate)` but different object values

## Why this default

The practical team tradeoff is:
- whitespace-normalized mode is the best default for noisy exports
- strict mode is safest for exact identifier comparisons
- object-only casefolding is useful for noisy literal values, but should not be
  applied to subject or predicate identifiers

## Checked-in example results

The files under `results/pipeline_*` are checked-in example fixtures for this
scenario. Use a different output directory for local runs so you do not
overwrite tracked example outputs.

This change is tracked in Team Brain decision
`01d55eee-12c8-4590-92b0-f8ad284e5bbd`, which supersedes
`4c6fed1b-6b47-497a-b363-63d39ec7556c`.
