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
python3 src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv --strict --out results/pipeline_strict
```

Observed conflicts:
- `TechCorp locatedIn Berlin` vs `TechCorp locatedIn  Berlin`
- `Bob manages DataPlatform` vs `Bob manages Data Platform`

Interpretation:
- one conflict is formatting noise caused by leading whitespace
- one conflict is still a meaningful review item because the object value differs

### Default whitespace normalization

Command:

```bash
python3 src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv --out results/pipeline_whitespace_only
```

Interpretation:
- the whitespace-only conflict disappears
- the `DataPlatform` vs `Data Platform` mismatch remains for review

### Whitespace + case normalization

Command:

```bash
python3 src/compare.py data/kg_pipeline_a.csv data/kg_pipeline_b.csv --casefold --out results/pipeline_normalized
```

Interpretation:
- casing noise is removed
- subject and predicate values are not casefolded, because they may be
  identifier-like fields where case remains significant
- the spacing difference inside `DataPlatform` vs `Data Platform` still remains
- this gives the team a smaller, more realistic review queue without hiding the
  remaining semantic mismatch

## Team decision reference

Team Brain decision:
`01d55eee-12c8-4590-92b0-f8ad284e5bbd`

Decision summary:
- whitespace normalization should be the default for noisy export comparisons
- strict mode remains available when exact matching matters
- object-only casefolding avoids collapsing identifier-like subject and
  predicate values

## Fixture note

The checked-in `results/pipeline_*` files are frozen example fixtures for the
review scenario. Local exploratory runs should use a separate output directory.
