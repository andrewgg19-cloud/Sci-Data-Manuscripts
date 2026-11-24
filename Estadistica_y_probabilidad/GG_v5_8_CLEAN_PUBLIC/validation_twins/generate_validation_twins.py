#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate paired validation datasets for German Gamma v5.8.

This script creates controlled twins:
- null twin;
- filtered geometric twin;
- temporal drift twin;
- entropy twin;
- reversibility twin.

The datasets are synthetic controls for validation only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent


def write_pair(folder: str, a: pd.DataFrame, b: pd.DataFrame, expected: str) -> None:
    out = ROOT / folder
    out.mkdir(parents=True, exist_ok=True)
    a.to_csv(out / "base_A.csv", index=False)
    b.to_csv(out / "base_B.csv", index=False)
    (out / "expected_result.md").write_text(expected.strip() + "\n", encoding="utf-8")


def make_base(rng: np.random.Generator, n: int = 600) -> pd.DataFrame:
    x = rng.normal(0, 1, (n, 3))
    return pd.DataFrame({"t": np.arange(n), "x1": x[:, 0], "x2": x[:, 1], "x3": x[:, 2]})


def main() -> None:
    rng = np.random.default_rng(20260719)

    # 01 null twin: B is an independent sample with the same distribution.
    a = make_base(rng)
    b = make_base(rng)
    write_pair(
        "01_null_twin",
        a,
        b,
        """
# Expected Result

The model should not report a strong structural signal. Differences should be
compatible with ordinary sampling variation.
""",
    )

    # 02 filtered twin: B keeps points above a geometric boundary and resamples
    # to maintain row count for paired tools.
    a = make_base(rng)
    keep = (a["x1"] + a["x2"]) > 0.6
    selected = a.loc[keep].copy()
    b = selected.sample(n=len(a), replace=True, random_state=20260719).reset_index(drop=True)
    b["t"] = np.arange(len(b))
    write_pair(
        "02_filtered_twin",
        a,
        b,
        """
# Expected Result

The model should report geometric/energy-entropy differences. This is a
controlled deformation, not evidence of fraud.
""",
    )

    # 03 temporal twin: B receives gradual drift after midpoint.
    a = make_base(rng)
    b = a.copy()
    drift = np.linspace(0, 1.2, len(b))
    b["x1"] = b["x1"] + np.where(b["t"] >= len(b) // 2, drift, 0)
    write_pair(
        "03_temporal_twin",
        a,
        b,
        """
# Expected Result

Temporal sheet or reversibility tools should see stronger late-window structure
in B than in A.
""",
    )

    # 04 entropy twin: B has same center but lower variance after compression.
    a = make_base(rng)
    b = a.copy()
    for col in ["x1", "x2", "x3"]:
        b[col] = b[col].mean() + 0.35 * (b[col] - b[col].mean())
    write_pair(
        "04_entropy_twin",
        a,
        b,
        """
# Expected Result

B should show lower dispersion/entropy than A under comparable binning.
""",
    )

    # 05 reversibility twin: B has a directional spiral-like trajectory.
    n = 600
    t = np.arange(n)
    theta = np.linspace(0, 8 * np.pi, n)
    radius = np.linspace(0.2, 2.0, n)
    a = make_base(rng, n=n)
    b = pd.DataFrame(
        {
            "t": t,
            "x1": radius * np.cos(theta) + rng.normal(0, 0.04, n),
            "x2": radius * np.sin(theta) + rng.normal(0, 0.04, n),
            "x3": np.linspace(-1, 1, n) + rng.normal(0, 0.04, n),
        }
    )
    write_pair(
        "05_reversibility_twin",
        a,
        b,
        """
# Expected Result

B should show stronger trajectory/reversibility asymmetry than A because it has
a directional expanding path.
""",
    )

    print(f"Validation twins written to: {ROOT}")


if __name__ == "__main__":
    main()
