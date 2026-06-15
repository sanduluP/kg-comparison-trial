"""
KG comparison baseline: compares two CSV-formatted knowledge graphs.
Input CSVs must have columns: subject, predicate, object
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def load_kg(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).dropna()
    df.columns = df.columns.str.strip()
    df = df[["subject", "predicate", "object"]].drop_duplicates()
    return df


def compare(kg1: pd.DataFrame, kg2: pd.DataFrame) -> dict:
    entities1 = set(kg1["subject"]) | set(kg1["object"])
    entities2 = set(kg2["subject"]) | set(kg2["object"])
    relations1 = set(kg1["predicate"])
    relations2 = set(kg2["predicate"])

    triples1 = set(map(tuple, kg1.itertuples(index=False)))
    triples2 = set(map(tuple, kg2.itertuples(index=False)))

    only1 = triples1 - triples2
    only2 = triples2 - triples1

    # conflicts: same (subject, predicate), different object
    sp1 = kg1.groupby(["subject", "predicate"])["object"].apply(set).reset_index()
    sp2 = kg2.groupby(["subject", "predicate"])["object"].apply(set).reset_index()
    merged = sp1.merge(sp2, on=["subject", "predicate"], suffixes=("_kg1", "_kg2"))
    conflicts_mask = merged["object_kg1"] != merged["object_kg2"]
    conflicts = merged[conflicts_mask].copy()
    conflicts["object_kg1"] = conflicts["object_kg1"].apply(sorted).apply("|".join)
    conflicts["object_kg2"] = conflicts["object_kg2"].apply(sorted).apply("|".join)

    return {
        "summary": {
            "entity_overlap": len(entities1 & entities2),
            "entity_kg1_only": len(entities1 - entities2),
            "entity_kg2_only": len(entities2 - entities1),
            "relation_overlap": len(relations1 & relations2),
            "relation_kg1_only": len(relations1 - relations2),
            "relation_kg2_only": len(relations2 - relations1),
            "triple_overlap": len(triples1 & triples2),
            "triple_kg1_only": len(only1),
            "triple_kg2_only": len(only2),
            "conflicts": len(conflicts),
        },
        "triple_overlap_df": pd.DataFrame(sorted(triples1 & triples2), columns=["subject", "predicate", "object"]),
        "kg1_only_df": pd.DataFrame(sorted(only1), columns=["subject", "predicate", "object"]),
        "kg2_only_df": pd.DataFrame(sorted(only2), columns=["subject", "predicate", "object"]),
        "conflicts_df": conflicts[["subject", "predicate", "object_kg1", "object_kg2"]].sort_values(["subject", "predicate"]),
    }


def save_results(results: dict, out_dir: Path, kg1_name: str, kg2_name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = results["summary"]
    summary["kg1"] = kg1_name
    summary["kg2"] = kg2_name
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    results["triple_overlap_df"].to_csv(out_dir / "triple_overlap.csv", index=False)
    results["kg1_only_df"].to_csv(out_dir / "kg1_only.csv", index=False)
    results["kg2_only_df"].to_csv(out_dir / "kg2_only.csv", index=False)
    results["conflicts_df"].to_csv(out_dir / "conflicts.csv", index=False)

    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Compare two knowledge graphs in CSV format.")
    parser.add_argument("kg1", help="Path to first KG CSV (subject,predicate,object)")
    parser.add_argument("kg2", help="Path to second KG CSV (subject,predicate,object)")
    parser.add_argument("--out", default="results", help="Output directory (default: results/)")
    args = parser.parse_args()

    kg1 = load_kg(args.kg1)
    kg2 = load_kg(args.kg2)

    results = compare(kg1, kg2)
    save_results(results, Path(args.out), Path(args.kg1).stem, Path(args.kg2).stem)


if __name__ == "__main__":
    main()
