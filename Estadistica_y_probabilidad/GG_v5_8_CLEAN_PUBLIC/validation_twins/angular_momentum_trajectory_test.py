#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Angular-momentum trajectory test for German Gamma validation twins.

Validation utility only. It does not add a new German Gamma core module.

For each temporal point it computes:

    r_t = x_t - n_t
    v_t = x_t - x_{t-1}
    L_t = r_t x v_t
    tau_t = L_t - L_{t-1}

where n_t is a rolling neutral point.
"""

from __future__ import annotations

import argparse
import json
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
    if len(cols) < 2:
        raise ValueError("At least two numeric columns are required.")
    return cols[:3]


def rolling_center(x: np.ndarray, idx: int, radius: int) -> np.ndarray:
    start = max(0, idx - radius)
    end = min(len(x), idx + radius + 1)
    return np.median(x[start:end], axis=0)


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

    if x.shape[1] == 2:
        x = np.column_stack([x, np.zeros(len(x))])

    if len(x) < 4:
        raise ValueError("At least four points are required.")

    rows = []
    previous_l = None
    for i in range(1, len(x)):
        n_t = rolling_center(x, i, args.center_radius)
        r_t = x[i] - n_t
        v_t = x[i] - x[i - 1]
        l_t = np.cross(r_t, v_t)
        l_norm = float(np.linalg.norm(l_t))
        r_norm = float(np.linalg.norm(r_t))
        v_norm = float(np.linalg.norm(v_t))

        if previous_l is None:
            tau = np.array([np.nan, np.nan, np.nan], dtype=float)
            tau_norm = np.nan
        else:
            tau = l_t - previous_l
            tau_norm = float(np.linalg.norm(tau))
        previous_l = l_t

        rows.append(
            {
                "index": i,
                "r_norm": r_norm,
                "v_norm": v_norm,
                "Lx": float(l_t[0]),
                "Ly": float(l_t[1]),
                "Lz": float(l_t[2]),
                "L_norm": l_norm,
                "tau_x": float(tau[0]) if np.isfinite(tau[0]) else None,
                "tau_y": float(tau[1]) if np.isfinite(tau[1]) else None,
                "tau_z": float(tau[2]) if np.isfinite(tau[2]) else None,
                "tau_norm": tau_norm if np.isfinite(tau_norm) else None,
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.to_csv(args.csv_out, index=False)

    l_values = out_df["L_norm"].to_numpy(dtype=float)
    tau_values = out_df["tau_norm"].dropna().to_numpy(dtype=float)
    mean_l_vector = out_df[["Lx", "Ly", "Lz"]].mean().to_numpy(dtype=float)
    resultant_l = float(np.linalg.norm(mean_l_vector))
    mean_l = float(np.mean(l_values))
    coherence = resultant_l / mean_l if mean_l > 1e-15 else 0.0
    torque_ratio = float(np.mean(tau_values) / mean_l) if mean_l > 1e-15 and len(tau_values) else None

    if mean_l <= args.low_rotation and coherence < args.coherence_threshold:
        reading = "low_rotation_or_radial_motion"
    elif coherence >= args.coherence_threshold and (torque_ratio is not None and torque_ratio <= args.torque_threshold):
        reading = "stable_rotational_structure_candidate"
    elif coherence >= args.coherence_threshold and torque_ratio is not None and torque_ratio > args.torque_threshold:
        reading = "rotational_break_or_transition_candidate"
    elif coherence < args.coherence_threshold and torque_ratio is not None and torque_ratio > args.torque_threshold:
        reading = "diffuse_stochastic_rotation_no_stable_axis"
    else:
        reading = "diffuse_rotation_without_stable_axis"

    result = {
        "name": "Angular momentum trajectory test",
        "scope": "validation/explanation only; not a German Gamma core module",
        "input": args.input,
        "columns": cols,
        "n_points": int(len(x)),
        "center_radius": int(args.center_radius),
        "mean_L_norm": mean_l,
        "median_L_norm": float(np.median(l_values)),
        "max_L_norm": float(np.max(l_values)),
        "mean_tau_norm": float(np.mean(tau_values)) if len(tau_values) else None,
        "median_tau_norm": float(np.median(tau_values)) if len(tau_values) else None,
        "rotation_coherence": coherence,
        "torque_ratio": torque_ratio,
        "mean_L_vector": mean_l_vector,
        "reading": reading,
        "limits": "Detects rotational structure around a rolling neutral point; it does not prove causality or physical angular momentum.",
    }
    Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Angular momentum trajectory test.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--columns", required=True)
    parser.add_argument("--time-column", default="t")
    parser.add_argument("--center-radius", type=int, default=20)
    parser.add_argument("--json-out", default="angular_momentum_result.json")
    parser.add_argument("--csv-out", default="angular_momentum_points.csv")
    parser.add_argument("--low-rotation", type=float, default=0.05)
    parser.add_argument("--coherence-threshold", type=float, default=0.35)
    parser.add_argument("--torque-threshold", type=float, default=1.25)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = analyze(args)
    print("=" * 88)
    print("ANGULAR MOMENTUM TRAJECTORY TEST")
    print("=" * 88)
    print(f"input              : {result['input']}")
    print(f"n_points           : {result['n_points']}")
    print(f"mean_L_norm        : {result['mean_L_norm']:.6f}")
    print(f"median_L_norm      : {result['median_L_norm']:.6f}")
    print(f"max_L_norm         : {result['max_L_norm']:.6f}")
    print(f"mean_tau_norm      : {result['mean_tau_norm']}")
    print(f"rotation_coherence : {result['rotation_coherence']:.6f}")
    print(f"torque_ratio       : {result['torque_ratio']}")
    print(f"reading            : {result['reading']}")
    print(f"JSON               : {Path(args.json_out).resolve()}")
    print(f"CSV                : {Path(args.csv_out).resolve()}")
    print("=" * 88)


if __name__ == "__main__":
    main()
