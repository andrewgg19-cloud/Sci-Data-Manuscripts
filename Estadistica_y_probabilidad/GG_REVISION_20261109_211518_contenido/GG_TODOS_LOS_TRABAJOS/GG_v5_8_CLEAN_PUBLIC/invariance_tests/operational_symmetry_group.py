#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the operational symmetry set Sym(X) and horizon-restricted Sym_H(X).

Validation utility only. It implements:

    Sym(X)   = {G in G_set : d(K(X), K(G(X))) <= epsilon}
    Sym_H(X) = {G in G_set : d(K(Pi_H(X)), K(Pi_H(G(X)))) <= epsilon}

and reports lost, preserved, and induced symmetries.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from k_signature_invariance_test import TRANSFORMS, as_3d, k_signature, load_table, parse_columns, signature_distance


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, set):
        return sorted(value)
    return value


def apply_horizon(df: pd.DataFrame, expression: str) -> pd.DataFrame:
    if not expression:
        return df.copy()
    try:
        mask = df.eval(expression)
    except Exception as exc:
        raise ValueError(f"Invalid horizon expression: {expression!r}") from exc
    if mask.dtype != bool:
        raise ValueError("Horizon expression must evaluate to boolean values.")
    return df.loc[mask].reset_index(drop=True)


def sym_set(x: np.ndarray, epsilon: float, bins: int) -> tuple[set[str], list[dict[str, Any]]]:
    base = k_signature(x, bins)
    rows = []
    conserved: set[str] = set()
    for name, fn in TRANSFORMS.items():
        transformed = fn(x)
        sig = k_signature(transformed, bins)
        dist = signature_distance(base, sig)
        is_conserved = dist <= epsilon
        if is_conserved:
            conserved.add(name)
        rows.append(
            {
                "transform": name,
                "distance": dist,
                "conserved": is_conserved,
            }
        )
    return conserved, rows


def sym_horizon_set(
    df: pd.DataFrame,
    cols: list[str],
    expression: str,
    epsilon: float,
    bins: int,
) -> tuple[set[str], list[dict[str, Any]], int]:
    """Compute Sym_H(X) using d(K(Pi_H(X)), K(Pi_H(G(X))))."""

    horizon_df = apply_horizon(df, expression)
    hx = as_3d(horizon_df[cols].to_numpy(dtype=float))
    hx = hx[np.isfinite(hx).all(axis=1)]
    if len(hx) < 4:
        raise ValueError("Horizon leaves fewer than four finite points; Sym_H is not evaluable.")
    base_h = k_signature(hx, bins)

    conserved: set[str] = set()
    rows = []
    original = as_3d(df[cols].to_numpy(dtype=float))
    for name, fn in TRANSFORMS.items():
        transformed = fn(original)
        tdf = df.copy()
        for idx, col in enumerate(cols):
            tdf[col] = transformed[:, idx]
        th_df = apply_horizon(tdf, expression)
        th = as_3d(th_df[cols].to_numpy(dtype=float))
        th = th[np.isfinite(th).all(axis=1)]
        if len(th) < 4:
            dist = float("inf")
            is_conserved = False
            n_after = int(len(th))
        else:
            sig = k_signature(th, bins)
            dist = signature_distance(base_h, sig)
            is_conserved = dist <= epsilon
            n_after = int(len(th))
        if is_conserved:
            conserved.add(name)
        rows.append(
            {
                "transform": name,
                "distance": dist,
                "conserved": is_conserved,
                "n_after_horizon_transform": n_after,
            }
        )
    return conserved, rows, int(len(hx))


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    df = load_table(Path(args.input))
    if args.time_column and args.time_column in df.columns:
        df = df.sort_values(args.time_column).reset_index(drop=True)
    cols = parse_columns(df, args.columns)
    x = as_3d(df[cols].to_numpy(dtype=float))
    x = x[np.isfinite(x).all(axis=1)]
    if len(x) < 4:
        raise ValueError("At least four finite points are required.")

    sym_x, rows_x = sym_set(x, args.epsilon, args.bins)

    sym_h, rows_h, n_horizon = sym_horizon_set(df, cols, args.horizon, args.epsilon, args.bins)

    lost = sorted(sym_x - sym_h)
    preserved = sorted(sym_x & sym_h)
    induced = sorted(sym_h - sym_x)
    broken_both = sorted(set(TRANSFORMS) - (sym_x | sym_h))

    result = {
        "name": "Operational symmetry group test",
        "scope": "validation/explanation only; not a German Gamma core module",
        "input": args.input,
        "columns": cols,
        "horizon": args.horizon,
        "epsilon": float(args.epsilon),
        "n_total": int(len(x)),
        "n_horizon": int(n_horizon),
        "survival_rate": float(n_horizon / len(x)),
        "Sym_X": sorted(sym_x),
        "Sym_H": sorted(sym_h),
        "preserved_symmetries": preserved,
        "lost_by_horizon": lost,
        "induced_by_horizon": induced,
        "broken_in_both": broken_both,
        "distances_X": rows_x,
        "distances_H": rows_h,
        "reading": (
            "Sym(X) is the set of declared transformations conserving K(X). "
            "Sym_H(X) is the same test after the declared horizon. "
            "Lost symmetries are candidates for horizon-induced structural deformation."
        ),
        "limits": "Operational symmetry over declared K and declared transformations only; not a universal symmetry proof.",
    }
    Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")

    rows = []
    dx = {row["transform"]: row for row in rows_x}
    dh = {row["transform"]: row for row in rows_h}
    for name in TRANSFORMS:
        rows.append(
            {
                "transform": name,
                "distance_X": dx[name]["distance"],
                "conserved_X": dx[name]["conserved"],
                "distance_H": dh[name]["distance"],
                "conserved_H": dh[name]["conserved"],
                "status": (
                    "preserved"
                    if name in preserved
                    else "lost_by_horizon"
                    if name in lost
                    else "induced_by_horizon"
                    if name in induced
                    else "broken_in_both"
                ),
            }
        )
    pd.DataFrame(rows).to_csv(args.csv_out, index=False)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operational symmetry group test.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--columns", required=True)
    parser.add_argument("--time-column", default="t")
    parser.add_argument("--horizon", default="x1 > 0")
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--bins", type=int, default=16)
    parser.add_argument("--json-out", default="operational_symmetry_result.json")
    parser.add_argument("--csv-out", default="operational_symmetry_results.csv")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = analyze(args)
    print("=" * 88)
    print("OPERATIONAL SYMMETRY GROUP TEST")
    print("=" * 88)
    print(f"input              : {result['input']}")
    print(f"horizon            : {result['horizon']}")
    print(f"n_total            : {result['n_total']}")
    print(f"n_horizon          : {result['n_horizon']}")
    print(f"survival_rate      : {result['survival_rate']:.6f}")
    print(f"Sym(X)             : {', '.join(result['Sym_X'])}")
    print(f"Sym_H(X)           : {', '.join(result['Sym_H'])}")
    print(f"lost_by_horizon    : {', '.join(result['lost_by_horizon'])}")
    print(f"induced_by_horizon : {', '.join(result['induced_by_horizon'])}")
    print(f"JSON               : {Path(args.json_out).resolve()}")
    print(f"CSV                : {Path(args.csv_out).resolve()}")
    print("=" * 88)


if __name__ == "__main__":
    main()
