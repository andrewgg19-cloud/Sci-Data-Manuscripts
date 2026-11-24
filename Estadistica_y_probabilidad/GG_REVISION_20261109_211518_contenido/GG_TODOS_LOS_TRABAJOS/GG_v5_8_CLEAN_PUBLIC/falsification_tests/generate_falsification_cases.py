#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate falsification cases for the angular trajectory test."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def save(out: Path, name: str, df: pd.DataFrame) -> None:
    path = out / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"created={path} rows={len(df)}")


def main() -> None:
    out = Path(__file__).resolve().parent
    rng = np.random.default_rng(20260719)
    n = 300
    t = np.arange(n)

    # Positive control: coherent circular trajectory.
    angle = 2.0 * np.pi * t / 60.0
    radius = 1.0 + 0.01 * np.sin(2.0 * np.pi * t / 97.0)
    save(
        out,
        "01_positive_orbit",
        pd.DataFrame(
            {
                "t": t,
                "x1": radius * np.cos(angle),
                "x2": radius * np.sin(angle),
                "x3": 0.01 * np.sin(2.0 * np.pi * t / 41.0),
            }
        ),
    )

    # Negative control: radial line through the neutral point.
    u = np.linspace(-1.0, 1.0, n)
    save(
        out,
        "02_negative_radial",
        pd.DataFrame(
            {
                "t": t,
                "x1": u,
                "x2": np.zeros(n),
                "x3": np.zeros(n),
            }
        ),
    )

    # Noise control: random walk without a declared stable axis.
    steps = rng.normal(0.0, 0.08, size=(n, 3))
    walk = np.cumsum(steps, axis=0)
    save(
        out,
        "03_noise_random_walk",
        pd.DataFrame({"t": t, "x1": walk[:, 0], "x2": walk[:, 1], "x3": walk[:, 2]}),
    )


if __name__ == "__main__":
    main()

