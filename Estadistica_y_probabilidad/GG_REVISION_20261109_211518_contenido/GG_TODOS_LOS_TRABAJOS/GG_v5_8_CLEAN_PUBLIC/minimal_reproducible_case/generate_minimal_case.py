#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the German Gamma minimal reproducible orbit case."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    out = Path(__file__).resolve().parent
    n = 240
    t = np.arange(n)
    angle = 2.0 * np.pi * t / 48.0
    radius = 1.0 + 0.015 * np.sin(2.0 * np.pi * t / 90.0)

    df = pd.DataFrame(
        {
            "t": t,
            "x1": radius * np.cos(angle),
            "x2": radius * np.sin(angle),
            "x3": 0.02 * np.sin(2.0 * np.pi * t / 37.0),
        }
    )
    path = out / "minimal_orbit_input.csv"
    df.to_csv(path, index=False)
    print(f"created={path}")
    print(f"rows={len(df)}")


if __name__ == "__main__":
    main()

