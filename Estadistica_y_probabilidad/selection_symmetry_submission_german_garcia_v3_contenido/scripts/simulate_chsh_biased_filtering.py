"""Simulate apparent CHSH violations from asymmetric post-selection."""

from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from plotting_utils import save_line_plot


SEED = 20260428
N_TRIALS = 250_000
OUT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = OUT_DIR / "results"
FIGURES_DIR = OUT_DIR / "paper" / "figures"


def mutual_information_binary(xs: list[int], ys: list[int]) -> float:
    n = len(xs)
    info = 0.0
    for xv in (0, 1):
        px = sum(x == xv for x in xs) / n
        for yv in (0, 1):
            py = sum(y == yv for y in ys) / n
            pxy = sum((x == xv and y == yv) for x, y in zip(xs, ys)) / n
            if pxy > 0.0 and px > 0.0 and py > 0.0:
                info += pxy * math.log(pxy / (px * py))
    return info


def simulate_for_bias(rng: random.Random, bias: float) -> dict[str, float | int]:
    sums = [0, 0, 0, 0]
    counts = [0, 0, 0, 0]
    r_bits: list[int] = []
    f_bits: list[int] = []
    kept = 0
    target = [1, 1, 1, -1]

    for _ in range(N_TRIALS):
        a0 = rng.choice((-1, 1))
        a1 = rng.choice((-1, 1))
        b0 = rng.choice((-1, 1))
        b1 = rng.choice((-1, 1))
        products = [a0 * b0, a0 * b1, a1 * b0, a1 * b1]
        setting = rng.randrange(4)
        r = products[setting]
        favored = r == target[setting]
        keep_prob = max(0.0, min(1.0, 0.55 + (bias if favored else -bias)))
        selected = rng.random() < keep_prob
        r_bits.append(1 if r == 1 else 0)
        f_bits.append(1 if selected else 0)
        if selected:
            kept += 1
            sums[setting] += r
            counts[setting] += 1

    correlations = [sums[i] / counts[i] for i in range(4)]
    s_observed = correlations[0] + correlations[1] + correlations[2] - correlations[3]
    p_keep = kept / N_TRIALS
    i_rf = mutual_information_binary(r_bits, f_bits)
    i_min_bound = p_keep * max(s_observed - 2.0, 0.0) ** 2 / 32.0
    return {
        "bias": bias,
        "n_trials": N_TRIALS,
        "p_keep": p_keep,
        "E00": correlations[0],
        "E01": correlations[1],
        "E10": correlations[2],
        "E11": correlations[3],
        "S_observed": s_observed,
        "I_R_F_nats": i_rf,
        "I_min_bound_nats": i_min_bound,
        "selected_00": counts[0],
        "selected_01": counts[1],
        "selected_10": counts[2],
        "selected_11": counts[3],
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    biases = [i * 0.02 for i in range(23)]
    rows = [simulate_for_bias(rng, bias) for bias in biases]

    out_csv = RESULTS_DIR / "chsh_biased_filtering.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    save_line_plot(
        FIGURES_DIR / "chsh_biased_filtering.png",
        [
            ([float(row["bias"]) for row in rows], [float(row["S_observed"]) for row in rows], (31, 111, 139)),
            ([float(row["bias"]) for row in rows], [40.0 * float(row["I_R_F_nats"]) for row in rows], (179, 63, 98)),
        ],
        x_min=0.0,
        x_max=max(biases),
        y_min=0.0,
        y_max=4.1,
        reference_y=2.0,
        title="Biased CHSH post-selection",
        xlabel="Selection bias strength",
        ylabel="S and 40 x I(R;F)",
        labels=["Observed CHSH S", "Scaled selection information"],
    )
    print(rows[-1])


if __name__ == "__main__":
    main()
