"""Generate archetypal selection structures for the diagnostic criterion.

The rows are synthetic archetypes, not claims about named experiments. They
provide controls and edge cases for the criterion b_req > b_max when no shared
physical control group is available.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from plotting_utils import save_grouped_bar_plot


OUT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = OUT_DIR / "results"
FIGURES_DIR = OUT_DIR / "paper" / "figures"
SEED = 20260428


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    rows = [
        {
            "scenario": "Bell-like symmetric control",
            "plot_label": "BELL CTRL",
            "archetype_family": "Bell-like",
            "selection_structure": "coincidence/post-selection",
            "case_type": "symmetric_control",
            "signal_scale": 0.02,
            "b_max": 0.12,
            "b_req": 0.00,
            "selection_information_proxy": 0.000,
            "interpretation": "selection-independent null reference",
        },
        {
            "scenario": "Bell-like biased false positive",
            "plot_label": "BELL BIAS",
            "archetype_family": "Bell-like",
            "selection_structure": "coincidence/post-selection",
            "case_type": "biased_spurious",
            "signal_scale": 0.82,
            "b_max": 0.44,
            "b_req": 0.31,
            "selection_information_proxy": 0.101,
            "interpretation": "allowed selection bias can explain the signal",
        },
        {
            "scenario": "AI benchmark filtering robust case",
            "plot_label": "AI ROB",
            "archetype_family": "AI/ML dataset filtering",
            "selection_structure": "benchmark curation / dataset inclusion",
            "case_type": "robust",
            "signal_scale": 5.00,
            "b_max": 0.42,
            "b_req": 1.35,
            "selection_information_proxy": 0.006,
            "interpretation": "required bias exceeds allowed bias",
        },
        {
            "scenario": "Single-cell QC borderline",
            "plot_label": "SC QC",
            "archetype_family": "single-cell omics",
            "selection_structure": "cell quality filtering",
            "case_type": "borderline",
            "signal_scale": 1.20,
            "b_max": 0.62,
            "b_req": 0.64,
            "selection_information_proxy": 0.011,
            "interpretation": "diagnostic separation is weak",
        },
        {
            "scenario": "Biomedical dropout non-robust toy case",
            "plot_label": "DROP FAIL",
            "archetype_family": "biomedical follow-up",
            "selection_structure": "response-dependent dropout",
            "case_type": "non_robust",
            "signal_scale": 0.95,
            "b_max": 0.70,
            "b_req": 0.48,
            "selection_information_proxy": 0.024,
            "interpretation": "selection explanation remains viable",
        },
    ]
    for row in rows:
        row["margin"] = row["b_req"] - row["b_max"]
        row["rho_sel"] = row["b_req"] / row["b_max"] if row["b_max"] > 0 else ""
        row["robust"] = row["margin"] > 0.05
        row["borderline"] = abs(row["margin"]) <= 0.05
        row["toy_uncertainty"] = rng.uniform(0.02, 0.05)

    with (RESULTS_DIR / "archetypal_selection_structures.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    save_grouped_bar_plot(
        FIGURES_DIR / "archetypal_selection_structures.png",
        [str(row["plot_label"]) for row in rows],
        [float(row["b_max"]) for row in rows],
        [float(row["b_req"]) for row in rows],
        title="Archetypal selection structures",
        ylabel="Operational bias scale",
    )
    print([{row["scenario"]: row["case_type"]} for row in rows])


if __name__ == "__main__":
    main()
