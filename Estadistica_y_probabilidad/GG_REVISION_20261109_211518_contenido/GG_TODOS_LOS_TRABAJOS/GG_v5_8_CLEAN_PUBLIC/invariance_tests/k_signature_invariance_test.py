#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test whether a structural signature K(X) is preserved under transformations.

Validation utility only. It does not add a German Gamma core module.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

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
    if len(cols) < 2:
        raise ValueError("Use at least two numeric columns.")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return cols[:3]


def as_3d(x: np.ndarray) -> np.ndarray:
    if x.shape[1] == 2:
        return np.column_stack([x, np.zeros(len(x))])
    return x[:, :3]


def entropy(values: np.ndarray, bins: int) -> float:
    hist, _ = np.histogram(values, bins=bins, density=False)
    p = hist.astype(float)
    p = p[p > 0]
    p = p / p.sum()
    return float(-np.sum(p * np.log(p)))


def angular_metrics(x: np.ndarray) -> tuple[float, float]:
    center = np.median(x, axis=0)
    l_vectors = []
    for i in range(1, len(x)):
        r_t = x[i] - center
        v_t = x[i] - x[i - 1]
        l_vectors.append(np.cross(r_t, v_t))
    l_vectors = np.asarray(l_vectors)
    l_norm = np.linalg.norm(l_vectors, axis=1)
    mean_l = float(np.mean(l_norm))
    mean_vec = np.mean(l_vectors, axis=0)
    coherence = float(np.linalg.norm(mean_vec) / mean_l) if mean_l > 1e-15 else 0.0
    return mean_l, coherence


def k_signature(x: np.ndarray, bins: int) -> dict[str, float]:
    center = np.median(x, axis=0)
    radius = np.linalg.norm(x - center, axis=1)
    mean_l, coherence = angular_metrics(x)
    return {
        "radius_mean": float(np.mean(radius)),
        "radius_std": float(np.std(radius)),
        "radius_entropy": entropy(radius, bins),
        "mean_L_norm": mean_l,
        "rotation_coherence": coherence,
    }


def transform_identity(x: np.ndarray) -> np.ndarray:
    return x.copy()


def transform_mirror_x(x: np.ndarray) -> np.ndarray:
    y = x.copy()
    y[:, 0] *= -1.0
    return y


def transform_sign_c(x: np.ndarray) -> np.ndarray:
    return -x


def transform_time_reverse(x: np.ndarray) -> np.ndarray:
    return x[::-1].copy()


def transform_rotate_z_90(x: np.ndarray) -> np.ndarray:
    y = x.copy()
    y[:, 0] = -x[:, 1]
    y[:, 1] = x[:, 0]
    return y


TRANSFORMS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "I": transform_identity,
    "P_mirror_x": transform_mirror_x,
    "C_sign": transform_sign_c,
    "T_reverse": transform_time_reverse,
    "Rz_90": transform_rotate_z_90,
}


def signature_distance(a: dict[str, float], b: dict[str, float]) -> float:
    keys = list(a.keys())
    deltas = []
    for key in keys:
        denom = max(abs(a[key]), abs(b[key]), 1.0)
        deltas.append((a[key] - b[key]) / denom)
    return float(np.linalg.norm(deltas))


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    df = load_table(Path(args.input))
    if args.time_column and args.time_column in df.columns:
        df = df.sort_values(args.time_column).reset_index(drop=True)
    cols = parse_columns(df, args.columns)
    x = as_3d(df[cols].to_numpy(dtype=float))
    x = x[np.isfinite(x).all(axis=1)]
    if len(x) < 4:
        raise ValueError("At least four finite points are required.")

    base = k_signature(x, args.bins)
    rows = []
    for name, fn in TRANSFORMS.items():
        y = fn(x)
        sig = k_signature(y, args.bins)
        dist = signature_distance(base, sig)
        rows.append(
            {
                "transform": name,
                "distance": dist,
                "invariant_candidate": dist <= args.epsilon,
                **{f"base_{k}": v for k, v in base.items()},
                **{f"transformed_{k}": v for k, v in sig.items()},
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.to_csv(args.csv_out, index=False)

    conserved = out_df[out_df["invariant_candidate"]]["transform"].tolist()
    broken = out_df[~out_df["invariant_candidate"]]["transform"].tolist()
    result = {
        "name": "K signature invariance test",
        "scope": "validation/explanation only; not a German Gamma core module",
        "input": args.input,
        "columns": cols,
        "epsilon": float(args.epsilon),
        "base_signature": base,
        "conserved_transforms": conserved,
        "broken_transforms": broken,
        "n_conserved": len(conserved),
        "n_broken": len(broken),
        "reading": (
            "K(X) is a structural signature candidate if it remains within "
            "epsilon under declared transformations."
        ),
        "limits": "This tests declared transformations only; it does not prove universal invariance.",
    }
    Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="K(X) invariance test.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--columns", required=True)
    parser.add_argument("--time-column", default="t")
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--bins", type=int, default=16)
    parser.add_argument("--json-out", default="k_invariance_result.json")
    parser.add_argument("--csv-out", default="k_invariance_results.csv")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = analyze(args)
    print("=" * 88)
    print("K SIGNATURE INVARIANCE TEST")
    print("=" * 88)
    print(f"input                 : {result['input']}")
    print(f"epsilon               : {result['epsilon']}")
    print(f"conserved_transforms  : {', '.join(result['conserved_transforms'])}")
    print(f"broken_transforms     : {', '.join(result['broken_transforms'])}")
    print(f"JSON                  : {Path(args.json_out).resolve()}")
    print(f"CSV                   : {Path(args.csv_out).resolve()}")
    print("=" * 88)


if __name__ == "__main__":
    main()

