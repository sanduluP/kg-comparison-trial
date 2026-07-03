import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.compare import compare, comparison_mode, load_kg


def write_rows(path: Path, rows: list[tuple[str, str, str]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["subject", "predicate", "object"])
        writer.writerows(rows)


class CompareNormalizationTest(unittest.TestCase):
    def test_strict_mode_preserves_noise_and_default_whitespace_normalization_reduces_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            kg1_path = tmp_path / "kg1.csv"
            kg2_path = tmp_path / "kg2.csv"

            write_rows(
                kg1_path,
                [
                    ("Alice", "worksAt", "TechCorp"),
                    ("TechCorp", "locatedIn", "Berlin"),
                    ("Bob", "manages", "DataPlatform"),
                ],
            )
            write_rows(
                kg2_path,
                [
                    (" Alice ", "worksAt", "TechCorp"),
                    ("TechCorp", "locatedIn", " Berlin"),
                    ("Bob", "manages", "Data Platform"),
                ],
            )

            strict_results = compare(
                load_kg(kg1_path, normalize_whitespace=False),
                load_kg(kg2_path, normalize_whitespace=False),
            )
            normalized_results = compare(load_kg(kg1_path), load_kg(kg2_path))

            self.assertEqual(strict_results["summary"]["conflicts"], 2)
            self.assertEqual(normalized_results["summary"]["conflicts"], 1)

    def test_casefold_only_changes_object_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            kg1_path = tmp_path / "kg1.csv"
            kg2_path = tmp_path / "kg2.csv"

            write_rows(kg1_path, [("Person:Alice", "hasRole", "Engineer")])
            write_rows(kg2_path, [("person:alice", "hasRole", "engineer")])

            casefolded_kg1 = load_kg(kg1_path, casefold_object=True)
            casefolded_kg2 = load_kg(kg2_path, casefold_object=True)

            self.assertEqual(casefolded_kg1.iloc[0]["object"], "engineer")
            self.assertEqual(casefolded_kg2.iloc[0]["object"], "engineer")
            self.assertEqual(casefolded_kg1.iloc[0]["subject"], "Person:Alice")
            self.assertEqual(casefolded_kg2.iloc[0]["subject"], "person:alice")

    def test_comparison_mode_labels_are_stable(self) -> None:
        self.assertEqual(comparison_mode(strict=True, casefold=False), "strict")
        self.assertEqual(comparison_mode(strict=False, casefold=True), "casefold")
        self.assertEqual(
            comparison_mode(strict=False, casefold=False),
            "whitespace_normalized",
        )

    def test_summary_json_includes_machine_readable_comparison_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            kg1_path = tmp_path / "kg1.csv"
            kg2_path = tmp_path / "kg2.csv"
            out_dir = tmp_path / "results"

            write_rows(kg1_path, [("Alice", "worksAt", "TechCorp")])
            write_rows(kg2_path, [("Alice", "worksAt", "techcorp")])

            subprocess.run(
                [
                    "python3",
                    "src/compare.py",
                    str(kg1_path),
                    str(kg2_path),
                    "--casefold",
                    "--out",
                    str(out_dir),
                ],
                check=True,
                cwd=Path(__file__).resolve().parent.parent,
            )

            summary = json.loads((out_dir / "summary.json").read_text())
            self.assertEqual(summary["comparison_mode"], "casefold")


if __name__ == "__main__":
    unittest.main()
