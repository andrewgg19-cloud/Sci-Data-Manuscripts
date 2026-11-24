"""Minimal reproducibility checks for generated CSV and figure artifacts."""

from __future__ import annotations

import csv
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class ReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run_all.py")], cwd=ROOT, check=True)

    def test_run_all_generates_expected_artifacts(self) -> None:
        expected_csvs = [
            ROOT / "results" / "chsh_biased_filtering.csv",
            ROOT / "results" / "information_bounds_bell.csv",
            ROOT / "results" / "archetypal_selection_structures.csv",
            ROOT / "results" / "biomedical_dropout_selection.csv",
        ]
        expected_figures = [
            ROOT / "paper" / "figures" / "chsh_biased_filtering.png",
            ROOT / "paper" / "figures" / "information_bounds_bell.png",
            ROOT / "paper" / "figures" / "archetypal_selection_structures.png",
            ROOT / "paper" / "figures" / "biomedical_dropout_selection.png",
        ]

        for path in expected_csvs + expected_figures:
            self.assertTrue(path.exists(), path)
            self.assertGreater(path.stat().st_size, 0, path)

    def test_chsh_selection_information_tracks_bias(self) -> None:
        rows = read_rows(ROOT / "results" / "chsh_biased_filtering.csv")
        first = rows[0]
        last = rows[-1]
        self.assertLess(float(first["I_R_F_nats"]), 1.0e-4)
        self.assertGreater(float(last["S_observed"]), 2.0)
        self.assertGreater(float(last["I_R_F_nats"]), float(first["I_R_F_nats"]))

    def test_information_bound_is_exact_formula(self) -> None:
        rows = read_rows(ROOT / "results" / "information_bounds_bell.csv")
        for row in rows[::37]:
            p_keep = float(row["p_keep"])
            s_value = float(row["S_observed"])
            expected = p_keep * (s_value - 2.0) ** 2 / 32.0
            self.assertLess(abs(float(row["I_min_bound_nats"]) - expected), 1.0e-15)

    def test_robust_criterion_columns(self) -> None:
        rows = read_rows(ROOT / "results" / "archetypal_selection_structures.csv")
        case_types = {row["case_type"] for row in rows}
        self.assertIn("symmetric_control", case_types)
        self.assertIn("biased_spurious", case_types)
        self.assertIn("borderline", case_types)
        self.assertIn("robust", case_types)
        self.assertIn("non_robust", case_types)

        robust_rows = [row for row in rows if row["robust"] == "True"]
        non_robust_rows = [row for row in rows if row["robust"] == "False" and row["borderline"] == "False"]
        borderline_rows = [row for row in rows if row["borderline"] == "True"]
        self.assertGreaterEqual(len(robust_rows), 1)
        self.assertGreaterEqual(len(non_robust_rows), 1)
        self.assertGreaterEqual(len(borderline_rows), 1)

        control = next(row for row in rows if row["case_type"] == "symmetric_control")
        self.assertLess(float(control["selection_information_proxy"]), 1.0e-6)

        robust = next(row for row in rows if row["case_type"] == "robust")
        self.assertGreater(float(robust["rho_sel"]), 1.0)

    def test_biomedical_dropout_selection_bias(self) -> None:
        rows = read_rows(ROOT / "results" / "biomedical_dropout_selection.csv")
        self.assertEqual({row["scenario"] for row in rows}, {"full cohort", "observed follow-up"})
        observed = next(row for row in rows if row["scenario"] == "observed follow-up")
        self.assertGreater(float(observed["I_R_F_nats"]), 0.0)
        self.assertGreater(abs(float(observed["selection_bias"])), 0.0)


if __name__ == "__main__":
    unittest.main()
