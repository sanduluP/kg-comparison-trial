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

To support that workflow, normalization is opt-in rather than default.

## Usage

Exact comparison:

```bash
python src/compare.py data/kg1.csv data/kg2.csv --out results
```

Whitespace-only normalization:

```bash
python src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv \
  --normalize-whitespace \
  --out results/pipeline_whitespace_only
```

Whitespace + case normalization:

```bash
python src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv \
  --normalize-whitespace \
  --casefold \
  --out results/pipeline_normalized
```

## Output files

- `summary.json`: overlap and conflict counts
- `triple_overlap.csv`: identical triples in both KGs
- `kg1_only.csv`: triples only in the first KG
- `kg2_only.csv`: triples only in the second KG
- `conflicts.csv`: same `(subject, predicate)` but different object values

## Why opt-in normalization

The practical team tradeoff is:
- strict mode is safest for exact identifier comparisons
- normalized mode is useful when different tools export harmless formatting noise

This change is tracked in Team Brain decision
`4c6fed1b-6b47-497a-b363-63d39ec7556c`.
