#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local oscillation anchor with noise discrimination.

Validation utility, not a German Gamma core module.

For each temporal point x_t it evaluates the local triad:

    x_{t-1}, x_t, x_{t+1}

and computes:

    local mean
    oscillation from local mean
    discrete curvature
    local noise scale
    oscillation/noise ratio
    curvature/noise ratio

Noise is not erased; it is used as a denominator of discernment.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("Use CSV, TXT, XLSX, or XLS.")


def parse_columns(df: pd.DataFrame, columns: str) -> list[str]:
    cols = [c.strip() for c in columns.split(",") if c.strip()]
    if not cols:
        raise ValueError("Provide numeric columns.")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return cols


def triad_metrics(x: np.ndarray, idx: int) -> tuple[float, float]:
    prev_x = x[idx - 1]
    cur_x = x[idx]
    next_x = x[idx + 1]
    triad = np.vstack([prev_x, cur_x, next_x])
    local_mean = np.mean(triad, axis=0)
    oscillation = float(np.linalg.norm(cur_x - local_mean))
    curvature = float(np.linalg.norm(next_x - 2.0 * cur_x + prev_x))
    return oscillation, curvature


def robust_scale(values: np.ndarray) -> tuple[float, float]:
    """Return local median and robust MAD scale."""

    values = np.asarray(values, dtype=float)
    med = float(np.median(values))
    mad = float(np.median(np.abs(values - med)))
    scale = 1.4826 * mad
    if scale <= 1e-15:
        scale = float(np.std(values))
    if scale <= 1e-15:
        return med, float("nan")
    return med, scale


def local_reference_metrics(x: np.ndarray, idx: int, radius: int) -> tuple[float, float, float, float]:
    """Estimate local noise from neighboring triad metrics."""

    start = max(1, idx - radius)
    end = min(len(x) - 1, idx + radius + 1)
    osc_vals = []
    curv_vals = []
    for j in range(start, end):
        o, c = triad_metrics(x, j)
        osc_vals.append(o)
        curv_vals.append(c)
    osc_center, osc_scale = robust_scale(np.asarray(osc_vals, dtype=float))
    curv_center, curv_scale = robust_scale(np.asarray(curv_vals, dtype=float))
    return osc_center, osc_scale, curv_center, curv_scale


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    df = load_table(Path(args.input))
    if args.time_column:
        if args.time_column not in df.columns:
            raise ValueError(f"Missing time column: {args.time_column}")
        df = df.sort_values(args.time_column).reset_index(drop=True)
    cols = parse_columns(df, args.columns)
    x = df[cols].to_numpy(dtype=float)
    finite = np.isfinite(x).all(axis=1)
    df = df.loc[finite].reset_index(drop=True)
    x = x[finite]
    if len(x) < 3:
        raise ValueError("At least three points are required.")

    rows = []
    for i in range(1, len(x) - 1):
        prev_x = x[i - 1]
        cur_x = x[i]
        next_x = x[i + 1]
        triad = np.vstack([prev_x, cur_x, next_x])
        local_mean = np.mean(triad, axis=0)
        oscillation, curvature = triad_metrics(x, i)
        osc_center, osc_scale, curv_center, curv_scale = local_reference_metrics(x, i, args.noise_radius)

        if not np.isfinite(osc_scale) or not np.isfinite(curv_scale):
            osc_ratio = None
            curv_ratio = None
            state = "not_evaluable_noise_scale"
        else:
            osc_ratio = max(0.0, (oscillation - osc_center) / osc_scale)
            curv_ratio = max(0.0, (curvature - curv_center) / curv_scale)
            if osc_ratio >= args.critical_ratio or curv_ratio >= args.critical_ratio:
                state = "local_oscillation_above_noise"
            else:
                state = "compatible_with_local_noise"

        row = {
            "index": i,
            "oscillation": oscillation,
            "curvature": curvature,
            "oscillation_local_center": osc_center,
            "oscillation_noise_scale": osc_scale,
            "curvature_local_center": curv_center,
            "curvature_noise_scale": curv_scale,
            "oscillation_noise_ratio": osc_ratio,
            "curvature_noise_ratio": curv_ratio,
            "state": state,
        }
        for j, col in enumerate(cols):
            row[f"{col}_local_mean"] = float(local_mean[j])
        rows.append(row)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(args.csv_out, index=False)

    valid = out_df[out_df["state"] != "not_evaluable_noise_scale"]
    flagged = out_df[out_df["state"] == "local_oscillation_above_noise"]

    result = {
        "name": "Local oscillation noise discriminator",
        "scope": "validation/explanation only; not a German Gamma core module",
        "input": args.input,
        "columns": cols,
        "n_points": int(len(x)),
        "n_evaluated": int(len(out_df)),
        "n_valid_noise_scale": int(len(valid)),
        "n_flagged": int(len(flagged)),
        "flag_rate": float(len(flagged) / max(1, len(valid))),
        "critical_ratio": float(args.critical_ratio),
        "mean_oscillation": float(out_df["oscillation"].mean()),
        "mean_curvature": float(out_df["curvature"].mean()),
        "mean_oscillation_noise_scale": float(valid["oscillation_noise_scale"].mean()) if len(valid) else None,
        "mean_curvature_noise_scale": float(valid["curvature_noise_scale"].mean()) if len(valid) else None,
        "reading": (
            "Noise is retained as the scale of discernment. A point is flagged "
            "only when local oscillation or curvature is unusually high relative "
            "to neighboring triad behavior."
        ),
        "limits": "This detects local structure above noise; it does not prove causality, intent, or validity.",
    }

    Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local oscillation with noise discrimination.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--columns", required=True)
    parser.add_argument("--time-column", default="")
    parser.add_argument("--noise-radius", type=int, default=5)
    parser.add_argument("--critical-ratio", type=float, default=2.0)
    parser.add_argument("--json-out", default="local_oscillation_noise_result.json")
    parser.add_argument("--csv-out", default="local_oscillation_noise_points.csv")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = analyze(args)
    print("=" * 88)
    print("LOCAL OSCILLATION NOISE DISCRIMINATOR")
    print("=" * 88)
    print(f"input             : {result['input']}")
    print(f"n_points          : {result['n_points']}")
    print(f"n_evaluated       : {result['n_evaluated']}")
    print(f"n_flagged         : {result['n_flagged']}")
    print(f"flag_rate         : {result['flag_rate']:.6f}")
    print(f"mean_oscillation  : {result['mean_oscillation']:.6f}")
    print(f"mean_curvature    : {result['mean_curvature']:.6f}")
    print(f"mean_osc_noise    : {result['mean_oscillation_noise_scale']}")
    print(f"mean_curv_noise   : {result['mean_curvature_noise_scale']}")
    print(f"JSON              : {Path(args.json_out).resolve()}")
    print(f"CSV               : {Path(args.csv_out).resolve()}")
    print("=" * 88)


if __name__ == "__main__":
    main()
