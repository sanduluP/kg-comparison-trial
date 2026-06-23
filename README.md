# KG Comparison Trial

> Last updated: 2026-06-23

This repo compares two CSV knowledge graphs and produces decision-ready outputs:

- overlapping triples
- triples only present in KG1
- triples only present in KG2
- subject-predicate conflicts
- dataset quality issues for each KG
- a machine-readable summary

Input files must use this schema:

```csv
subject,predicate,object
Alice,knows,Bob
Bob,worksAt,TechCorp
```

## End-to-End Workflow

### 1. Kickoff

The kickoff is where the comparison is framed before any graph metrics are trusted.

Clarify:

- Decision: what choice this comparison should support.
- Scope: which KGs, source systems, dates, versions, and domains are included.
- Ground truth: which source wins when the graphs disagree, or who resolves conflicts.
- Quality bar: which data quality failures block the comparison.
- Outputs: what the team needs at the end: CSVs, summary, meeting notes, or a decision log.

Example kickoff:

```text
Goal:
Compare the CRM KG and research KG for organization/person facts before merging them.

KG1:
data/kg1.csv, exported from Team Brain snapshot 2026-06-15.

KG2:
data/kg2.csv, generated from latest activity inference run.

Decision:
Decide which triples can be accepted automatically and which need review.

Conflict rule:
Exact triple overlap is accepted.
Same subject + predicate with different object goes to review.
Age, status, and role facts require source/date metadata before merge.

Quality gate:
Rows with missing subject, predicate, or object are rejected.
Duplicate triples are allowed but reported.
Self-loops are reviewed unless the predicate explicitly allows them.
```

### 2. Prepare Inputs

Place the two source files in `data/` or pass paths directly:

```bash
python src/compare.py data/kg1.csv data/kg2.csv --out results
```

The script loads raw rows for quality reporting, then creates a cleaned graph for comparison by:

- requiring `subject`, `predicate`, `object`
- trimming leading and trailing whitespace
- dropping rows with missing required values
- dropping exact duplicate triples

You can declare predicates that should have only one object per subject:

```bash
python src/compare.py data/kg1.csv data/kg2.csv --out results \
  --single-valued-predicate age \
  --single-valued-predicate bornIn \
  --single-valued-predicate locatedIn
```

Defaults are `age`, `bornIn`, and `locatedIn`.

### 3. Run Dataset Quality Checks

Quality checks run before comparison and are included in `results/summary.json` plus `results/data_quality_issues.csv`.

Current checks:

- raw row count vs cleaned row count
- missing required values
- duplicate triples
- leading or trailing whitespace
- self-loops such as `Alice,knows,Alice`
- multiple objects for declared single-valued predicates, such as `Alice,age,30` and `Alice,age,31`

Example quality issue:

```csv
kg,row_number,subject,predicate,object,issues
kg2,,Alice,age,31,multiple_objects_for_single_valued_predicate
```

### 4. Compare KGs

The comparison produces:

- `results/triple_overlap.csv`: facts both KGs agree on exactly.
- `results/kg1_only.csv`: facts only KG1 contains.
- `results/kg2_only.csv`: facts only KG2 contains.
- `results/conflicts.csv`: same subject and predicate, different object.
- `results/summary.json`: counts for overlaps, differences, conflicts, and quality.

Using the sample data, these triples overlap:

```csv
Alice,knows,Bob
Alice,knows,Carol
Bob,worksAt,TechCorp
TechCorp,locatedIn,CityA
```

These are conflicts:

```csv
subject,predicate,object_kg1,object_kg2
Alice,age,30,31
Carol,worksAt,UniX,BioLab
```

### 5. Review and Decide

Use the outputs this way:

- Accept `triple_overlap.csv` when quality gates pass.
- Review `conflicts.csv` first because these block automatic merge.
- Review `kg1_only.csv` and `kg2_only.csv` as candidate additions or removals.
- Use `data_quality_issues.csv` to decide whether a source needs cleanup before KG decisions are made.

Example decision log:

```text
Accepted:
4 overlapping triples.

Needs review:
Alice age differs: KG1 says 30, KG2 says 31.
Carol worksAt differs: KG1 says UniX, KG2 says BioLab.

Candidate addition:
Dave knows Alice appears only in KG2.

Rejected until cleanup:
Any rows with missing subject, predicate, or object.
```

## Team Brain Context

If Team Brain has access to activity history, chats, and later decision traces, use that context as evidence, not as the final authority.

Recommended pattern:

1. Activity/chat history proposes candidate triples.
2. Source metadata records why the triple exists.
3. KG comparison checks whether another KG agrees, disagrees, or lacks the fact.
4. Data quality checks block malformed or suspicious facts.
5. Human or rule-based review resolves conflicts.
6. The decision is written back as accepted, rejected, or needs-review.

Example:

```text
Activity signal:
Several chats mention "Carol moved from UniX to BioLab".

Candidate triple:
Carol,worksAt,BioLab

Comparison:
KG1 says Carol,worksAt,UniX.
KG2 says Carol,worksAt,BioLab.

Decision:
Conflict. Review source timestamp and confidence before replacing UniX.
```

## Output Contract

After a run, downstream tools can consume:

```text
results/summary.json
results/triple_overlap.csv
results/kg1_only.csv
results/kg2_only.csv
results/conflicts.csv
results/data_quality_issues.csv
```
