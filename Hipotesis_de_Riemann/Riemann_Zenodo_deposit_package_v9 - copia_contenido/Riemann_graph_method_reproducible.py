#!/usr/bin/env python3
"""Reproducible graph audit for the Riemann-zero topology manuscript.

This script is a numerical illustration only. It does not prove RH.
It computes positive critical-line zeros with mpmath, applies the smooth
Riemann-von Mangoldt unfolding, builds null / neutral / Riemann Rips graphs,
and reports Laplacian beta_0 across a fixed epsilon grid.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import mpmath as mp
import numpy as np


def nbar(t: np.ndarray) -> np.ndarray:
    return t/(2*np.pi)*np.log(t/(2*np.pi)) - t/(2*np.pi) + 7/8


def rips_adjacency(points: np.ndarray, eps: float) -> np.ndarray:
    dist = np.abs(points[:, None] - points[None, :])
    return ((dist <= eps) & (dist > 0)).astype(float)


def laplacian_report(points: np.ndarray, eps: float, tol: float = 1e-10) -> dict:
    A = rips_adjacency(points, eps)
    D = np.diag(A.sum(axis=1))
    L = D - A
    vals = np.linalg.eigvalsh(L)
    return {
        "epsilon": eps,
        "edges": int(A.sum()/2),
        "mean_degree": float(A.sum(axis=1).mean()),
        "beta0": int(np.sum(np.abs(vals) < tol)),
        "lambda2": float(vals[1]) if len(vals) > 1 else None,
        "lambda_max": float(vals[-1]) if len(vals) else None,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--dps", type=int, default=40)
    p.add_argument("--out", default="riemann_graph_audit_results.json")
    args = p.parse_args()

    mp.mp.dps = args.dps
    gamma = np.array([float(mp.im(mp.zetazero(k))) for k in range(1, args.n+1)])
    x = nbar(gamma)
    gaps = np.diff(x)
    neutral = np.arange(args.n, dtype=float)
    eps_grid = [0.25,0.50,0.75,1.00,1.25,1.50,1.75,2.00]

    out = {
        "n": args.n,
        "unfolding": "Nbar(T)=T/(2pi) log(T/(2pi))-T/(2pi)+7/8",
        "gap_summary": {
            "mean": float(gaps.mean()),
            "median": float(np.median(gaps)),
            "min": float(gaps.min()),
            "max": float(gaps.max()),
        },
        "epsilon_grid": eps_grid,
        "null_beta0": [args.n for _ in eps_grid],
        "neutral": [laplacian_report(neutral, e) for e in eps_grid],
        "riemann": [laplacian_report(x, e) for e in eps_grid],
    }
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
