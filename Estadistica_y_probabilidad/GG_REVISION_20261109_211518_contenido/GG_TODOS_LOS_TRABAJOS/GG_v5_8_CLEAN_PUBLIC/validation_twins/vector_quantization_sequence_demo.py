#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vector quantization + sequence reading demo for German Gamma validation.

This is not a new German Gamma core module.

It demonstrates a validation idea:
- compress a point cloud into k centroids;
- replace each point by its nearest centroid;
- measure reconstruction error;
- read the temporal sequence of centroid labels;
- estimate transition matrix and label entropy.

Purpose:
    compress local chaos into a finite recognition alphabet.
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


def standardize(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = np.mean(x, axis=0)
    sd = np.std(x, axis=0)
    sd = np.where(sd <= 1e-15, 1.0, sd)
    return (x - mu) / sd, mu, sd


def kmeans_numpy(x: np.ndarray, k: int, *, seed: int, max_iter: int) -> tuple[np.ndarray, np.ndarray]:
    if k <= 0:
        raise ValueError("k must be positive.")
    if k > len(x):
        raise ValueError("k cannot exceed number of points.")

    rng = np.random.default_rng(seed)
    centroids = x[rng.choice(len(x), size=k, replace=False)].copy()
    labels = np.zeros(len(x), dtype=int)

    for _ in range(max_iter):
        dist2 = np.sum((x[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        new_labels = np.argmin(dist2, axis=1)
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        for j in range(k):
            mask = labels == j
            if np.any(mask):
                centroids[j] = np.mean(x[mask], axis=0)
            else:
                centroids[j] = x[rng.integers(0, len(x))]
    return centroids, labels


def entropy_from_labels(labels: np.ndarray, k: int) -> float:
    counts = np.bincount(labels, minlength=k).astype(float)
    p = counts[counts > 0] / counts.sum()
    h = -float(np.sum(p * np.log(p)))
    return h / math.log(k) if k > 1 else 0.0


def transition_matrix(labels: np.ndarray, k: int) -> np.ndarray:
    mat = np.zeros((k, k), dtype=float)
    if len(labels) <= 1:
        return mat
    for a, b in zip(labels[:-1], labels[1:]):
        mat[int(a), int(b)] += 1.0
    rowsum = mat.sum(axis=1, keepdims=True)
    return np.divide(mat, rowsum, out=np.zeros_like(mat), where=rowsum > 0)


def transition_entropy(mat: np.ndarray) -> float:
    vals = []
    for row in mat:
        p = row[row > 0]
        if len(p):
            vals.append(-float(np.sum(p * np.log(p))) / math.log(len(row)))
    return float(np.mean(vals)) if vals else 0.0


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
    xz, mu, sd = standardize(x)

    centroids_z, labels = kmeans_numpy(xz, args.k, seed=args.seed, max_iter=args.max_iter)
    reconstructed_z = centroids_z[labels]
    reconstructed = reconstructed_z * sd + mu
    error = np.linalg.norm(xz - reconstructed_z, axis=1)
    mat = transition_matrix(labels, args.k)

    out_df = df.copy()
    out_df["vq_label"] = labels
    out_df["vq_error"] = error
    for i, col in enumerate(cols):
        out_df[f"{col}_vq_center"] = reconstructed[:, i]
    out_df.to_csv(args.csv_out, index=False)

    result = {
        "name": "Vector quantization sequence demo",
        "scope": "validation/explanation only; not a German Gamma core module",
        "input": args.input,
        "columns": cols,
        "k": args.k,
        "n_points": int(len(x)),
        "mean_reconstruction_error_z": float(np.mean(error)),
        "median_reconstruction_error_z": float(np.median(error)),
        "max_reconstruction_error_z": float(np.max(error)),
        "label_entropy_normalized": entropy_from_labels(labels, args.k),
        "transition_entropy_normalized": transition_entropy(mat),
        "centroids_original_scale": (centroids_z * sd + mu).tolist(),
        "transition_matrix": mat.tolist(),
        "reading": (
            "lower reconstruction error means stronger compression by centroids; "
            "transition entropy summarizes how ordered or dispersed the centroid sequence is"
        ),
        "limits": "Quantization compresses structure; it does not prove causality, intent, or validity.",
    }
    Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vector quantization + sequence validation demo.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--columns", required=True)
    parser.add_argument("--time-column", default="")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260719)
    parser.add_argument("--max-iter", type=int, default=100)
    parser.add_argument("--json-out", default="vq_sequence_result.json")
    parser.add_argument("--csv-out", default="vq_sequence_points.csv")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = analyze(args)
    print("=" * 88)
    print("VECTOR QUANTIZATION SEQUENCE DEMO")
    print("=" * 88)
    print(f"input                         : {result['input']}")
    print(f"k                             : {result['k']}")
    print(f"n_points                      : {result['n_points']}")
    print(f"mean reconstruction error (z) : {result['mean_reconstruction_error_z']:.6f}")
    print(f"label entropy normalized      : {result['label_entropy_normalized']:.6f}")
    print(f"transition entropy normalized : {result['transition_entropy_normalized']:.6f}")
    print(f"JSON                          : {Path(args.json_out).resolve()}")
    print(f"CSV                           : {Path(args.csv_out).resolve()}")
    print("=" * 88)


if __name__ == "__main__":
    main()
