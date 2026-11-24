"""Synthetic biomedical dropout example for selection symmetry.

This is not a clinical claim. It is a controlled simulation showing how
response-dependent follow-up can make the observed treatment contrast differ
from the full-cohort contrast.
"""

from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from plotting_utils import save_simple_bar_plot


SEED = 20260428
N_SUBJECTS = 80_000
OUT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = OUT_DIR / "results"
FIGURES_DIR = OUT_DIR / "paper" / "figures"


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


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


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    treated: list[int] = []
    response: list[int] = []
    followed: list[int] = []

    for _ in range(N_SUBJECTS):
        severity = rng.gauss(0.0, 1.0)
        treatment = 1 if rng.random() < 0.5 else 0
        response_prob = sigmoid(-0.25 + 0.18 * treatment - 0.72 * severity)
        outcome = 1 if rng.random() < response_prob else 0

        # Dropout is higher for non-responders and severe subjects, with an
        # interaction that makes treated non-responders especially likely to
        # miss follow-up. This creates a visible selection artifact.
        treated_nonresponse = treatment * (1 - outcome)
        followup_prob = sigmoid(1.15 + 1.00 * outcome - 0.45 * severity + 0.10 * treatment - 1.10 * treated_nonresponse)
        observed = 1 if rng.random() < followup_prob else 0

        treated.append(treatment)
        response.append(outcome)
        followed.append(observed)

    full_treated = [r for r, t in zip(response, treated) if t == 1]
    full_control = [r for r, t in zip(response, treated) if t == 0]
    obs_treated = [r for r, t, f in zip(response, treated, followed) if t == 1 and f == 1]
    obs_control = [r for r, t, f in zip(response, treated, followed) if t == 0 and f == 1]

    full_effect = mean(full_treated) - mean(full_control)
    observed_effect = mean(obs_treated) - mean(obs_control)
    selection_bias = observed_effect - full_effect
    p_followup = mean([float(f) for f in followed])
    i_response_followup = mutual_information_binary(response, followed)

    b_req = abs(observed_effect)
    b_max = abs(selection_bias)
    rho_sel = b_req / b_max if b_max > 0 else math.inf
    robust = rho_sel > 1.0

    rows = [
        {
            "scenario": "full cohort",
            "n": N_SUBJECTS,
            "p_followup": p_followup,
            "treated_response_rate": mean(full_treated),
            "control_response_rate": mean(full_control),
            "effect": full_effect,
            "I_R_F_nats": i_response_followup,
            "selection_bias": 0.0,
            "b_req": abs(full_effect),
            "b_max": 0.0,
            "rho_sel": "",
            "robust": "",
        },
        {
            "scenario": "observed follow-up",
            "n": sum(followed),
            "p_followup": p_followup,
            "treated_response_rate": mean(obs_treated),
            "control_response_rate": mean(obs_control),
            "effect": observed_effect,
            "I_R_F_nats": i_response_followup,
            "selection_bias": selection_bias,
            "b_req": b_req,
            "b_max": b_max,
            "rho_sel": rho_sel,
            "robust": robust,
        },
    ]

    with (RESULTS_DIR / "biomedical_dropout_selection.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    save_simple_bar_plot(
        FIGURES_DIR / "biomedical_dropout_selection.png",
        ["FULL", "OBS", "BIAS"],
        [full_effect, observed_effect, selection_bias],
        title="Biomedical dropout selection",
        ylabel="Treatment contrast",
        colors=[(91, 142, 125), (196, 109, 94), (179, 63, 98)],
    )
    print(rows[-1])


if __name__ == "__main__":
    main()
