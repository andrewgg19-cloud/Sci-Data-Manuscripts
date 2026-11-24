"""Compute the operational information lower bound for CHSH excess."""

from __future__ import annotations

import csv
from pathlib import Path

from plotting_utils import save_line_plot


OUT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = OUT_DIR / "results"
FIGURES_DIR = OUT_DIR / "paper" / "figures"

def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    s_values = [2.0 + i * (0.85 / 119) for i in range(120)]
    keep_fractions = [0.25, 0.50, 0.75, 1.00]
    rows: list[dict[str, float]] = []
    series = []
    colors = [(31, 111, 139), (91, 142, 125), (196, 109, 94), (179, 63, 98)]
    for p_keep, color in zip(keep_fractions, colors):
        ys = []
        for s in s_values:
            bound = p_keep * (s - 2.0) ** 2 / 32.0
            rows.append(
                {
                    "p_keep": p_keep,
                    "S_observed": s,
                    "I_min_bound_nats": bound,
                    "analytic_bound_nats": bound,
                }
            )
            ys.append(bound)
        series.append((s_values, ys, color))

    with (RESULTS_DIR / "information_bounds_bell.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    save_line_plot(
        FIGURES_DIR / "information_bounds_bell.png",
        series,
        x_min=2.0,
        x_max=2.85,
        y_min=0.0,
        y_max=0.024,
        title="CHSH information lower bound",
        xlabel="Observed CHSH S",
        ylabel="Minimum selection information [nats]",
        labels=[f"p={p:.2f}" for p in keep_fractions],
    )
    print({p: p * (2.85 - 2.0) ** 2 / 32.0 for p in keep_fractions})


if __name__ == "__main__":
    main()
