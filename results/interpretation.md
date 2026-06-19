# Interpretation Notes

This repo now includes a realistic team scenario: two KG export pipelines
produce mostly the same facts, but one pipeline adds formatting noise.

## Scenario

- `data/kg_pipeline_a.csv` represents the canonical export
- `data/kg_pipeline_b.csv` represents a partner or downstream export
- the team wants to know which differences are formatting-only noise and which
  represent real review items

## What the comparison runs show

### Strict mode

Command:

```bash
python3 src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv --out results/pipeline_strict
```

Observed conflicts:
- `TechCorp locatedIn Berlin` vs `TechCorp locatedIn " Berlin"`
- `Bob manages DataPlatform` vs `Bob manages "Data Platform"`

Interpretation:
- one conflict is formatting noise caused by leading whitespace
- one conflict is still a meaningful review item because the object value differs

### Whitespace normalization

Command:

```bash
python3 src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv --normalize-whitespace --out results/pipeline_whitespace_only
```

Interpretation:
- the whitespace-only conflict disappears
- the `DataPlatform` vs `Data Platform` mismatch remains for review

### Whitespace + case normalization

Command:

```bash
python3 src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv --normalize-whitespace --casefold --out results/pipeline_normalized
```

Interpretation:
- casing noise is removed
- the spacing difference inside `DataPlatform` vs `Data Platform` still remains
- this gives the team a smaller, more realistic review queue without hiding the
  remaining semantic mismatch

## Team decision reference

Team Brain decision:
`4c6fed1b-6b47-497a-b363-63d39ec7556c`

Decision summary:
- normalization should be available for noisy export comparisons
- normalization should remain opt-in so exact matching stays the default
