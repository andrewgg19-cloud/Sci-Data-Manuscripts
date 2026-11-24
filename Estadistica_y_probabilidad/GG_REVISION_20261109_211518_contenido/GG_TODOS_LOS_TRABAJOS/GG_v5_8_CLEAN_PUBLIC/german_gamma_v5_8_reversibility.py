#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German Gamma v5.8 - Reversibility Layer.

This closing layer evaluates whether a temporal trajectory preserves structure
when read forward and backward.

It computes:
- entropy path per window;
- centroid displacement path per window;
- forward vs reverse distribution divergence;
- entropy arrow score;
- transition asymmetry score.

Exploratory only. It does not prove fraud, intent, causality, or invalidity.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


MODEL_NAME = "German Gamma v5.8 Reversibility"


@dataclass(frozen=True)
class WindowState:
    window_id: int
    start_index: int
    end_index: int
    n_points: int
    entropy: float
    centroid: list[float]
    radius_mean: float
    radius_std: float


@dataclass(frozen=True)
class ReversibilityReport:
    model: str
    input: str
    columns: list[str]
    window_size: int
    step: int
    bins: int
    n_windows: int
    entropy_arrow_score: float
    centroid_path_length_forward: float
    centroid_path_length_reverse: float
    centroid_reversibility_gap: float
    js_forward_reverse_entropy_steps: float
    transition_asymmetry_score: float
    reading: str
    windows: list[WindowState]
    limits: str


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    raise ValueError("Unsupported file. Use CSV, TXT, XLSX, or XLS.")


def parse_columns(df: pd.DataFrame, columns: str) -> list[str]:
    cols = [c.strip() for c in columns.split(",") if c.strip()]
    if len(cols) < 1:
        raise ValueError("At least one numeric column is required.")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return cols


def entropy_nd(x: np.ndarray, bins: int) -> float:
    if len(x) == 0:
        return 0.0
    edges = []
    for j in range(x.shape[1]):
        col = x[:, j]
        lo = float(np.nanmin(col))
        hi = float(np.nanmax(col))
        if abs(hi - lo) <= 1e-15:
            lo -= 0.5
            hi += 0.5
        edges.append(np.linspace(lo, hi, bins + 1))
    hist, _ = np.histogramdd(x, bins=edges)
    p = hist.astype(float).ravel()
    p = p[p > 0]
    if len(p) == 0:
        return 0.0
    p = p / p.sum()
    h = -float(np.sum(p * np.log(p)))
    return h / math.log(len(hist.ravel())) if len(hist.ravel()) > 1 else 0.0


def js_divergence_from_samples(a: np.ndarray, b: np.ndarray, bins: int) -> float:
    if len(a) == 0 or len(b) == 0:
        return 0.0
    combined = np.concatenate([a, b])
    lo = float(np.nanmin(combined))
    hi = float(np.nanmax(combined))
    if abs(hi - lo) <= 1e-15:
        return 0.0
    edges = np.linspace(lo, hi, bins + 1)
    pa, _ = np.histogram(a, bins=edges)
    pb, _ = np.histogram(b, bins=edges)
    pa = pa.astype(float)
    pb = pb.astype(float)
    if pa.sum() <= 0 or pb.sum() <= 0:
        return 0.0
    pa = pa / pa.sum()
    pb = pb / pb.sum()
    m = 0.5 * (pa + pb)
    ma = pa > 0
    mb = pb > 0
    return float(0.5 * np.sum(pa[ma] * np.log2(pa[ma] / m[ma])) + 0.5 * np.sum(pb[mb] * np.log2(pb[mb] / m[mb])))


def build_windows(df: pd.DataFrame, cols: list[str], *, window_size: int, step: int, bins: int) -> list[WindowState]:
    states: list[WindowState] = []
    for start in range(0, max(0, len(df) - window_size + 1), step):
        end = start + window_size
        x = df.iloc[start:end][cols].to_numpy(dtype=float)
        finite = np.isfinite(x).all(axis=1)
        x = x[finite]
        if len(x) == 0:
            continue
        centroid = np.mean(x, axis=0)
        radius = np.linalg.norm(x - centroid, axis=1)
        states.append(
            WindowState(
                window_id=len(states),
                start_index=start,
                end_index=end - 1,
                n_points=int(len(x)),
                entropy=entropy_nd(x, bins),
                centroid=[float(v) for v in centroid],
                radius_mean=float(np.mean(radius)),
                radius_std=float(np.std(radius)),
            )
        )
    return states


def path_length(centroids: np.ndarray) -> float:
    if len(centroids) <= 1:
        return 0.0
    diffs = np.diff(centroids, axis=0)
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def transition_asymmetry(centroids: np.ndarray) -> float:
    if len(centroids) <= 2:
        return 0.0
    forward_steps = np.diff(centroids, axis=0)
    reverse_steps = -forward_steps[::-1]
    n = min(len(forward_steps), len(reverse_steps))
    if n == 0:
        return 0.0
    return float(np.mean(np.linalg.norm(forward_steps[:n] - reverse_steps[:n], axis=1)))


def analyze(args: argparse.Namespace) -> ReversibilityReport:
    df = load_table(Path(args.input))
    cols = parse_columns(df, args.columns)
    if args.time_column:
        if args.time_column not in df.columns:
            raise ValueError(f"Missing time column: {args.time_column}")
        df = df.sort_values(args.time_column).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    states = build_windows(df, cols, window_size=args.window_size, step=args.step, bins=args.bins)
    if len(states) < 2:
        raise ValueError("At least two windows are required for reversibility analysis.")

    ent = np.asarray([s.entropy for s in states], dtype=float)
    centroids = np.asarray([s.centroid for s in states], dtype=float)
    forward_entropy_steps = np.diff(ent)
    reverse_entropy_steps = -forward_entropy_steps[::-1]

    entropy_arrow = float(np.mean(forward_entropy_steps)) if len(forward_entropy_steps) else 0.0
    js_steps = js_divergence_from_samples(forward_entropy_steps, reverse_entropy_steps, args.bins)
    forward_len = path_length(centroids)
    reverse_len = path_length(centroids[::-1])
    gap = abs(forward_len - reverse_len)
    asym = transition_asymmetry(centroids)

    combined = abs(entropy_arrow) + js_steps + gap + asym
    if combined >= args.critical_score:
        reading = "irreversible_trajectory_signal_exploratory"
    elif combined >= args.critical_score / 3:
        reading = "weak_reversibility_asymmetry"
    else:
        reading = "approximately_reversible_under_selected_features"

    return ReversibilityReport(
        model=MODEL_NAME,
        input=args.input,
        columns=cols,
        window_size=int(args.window_size),
        step=int(args.step),
        bins=int(args.bins),
        n_windows=len(states),
        entropy_arrow_score=entropy_arrow,
        centroid_path_length_forward=forward_len,
        centroid_path_length_reverse=reverse_len,
        centroid_reversibility_gap=gap,
        js_forward_reverse_entropy_steps=js_steps,
        transition_asymmetry_score=asym,
        reading=reading,
        windows=states,
        limits="Exploratory reversibility diagnostic. It does not prove fraud, intent, causality, or invalidity.",
    )


def print_report(report: ReversibilityReport) -> None:
    print("=" * 92)
    print("GERMAN GAMMA v5.8 - REVERSIBILITY")
    print("=" * 92)
    print(f"Input                         : {report.input}")
    print(f"Columns                       : {', '.join(report.columns)}")
    print(f"Windows                       : {report.n_windows}")
    print(f"Entropy arrow score           : {report.entropy_arrow_score:.8f}")
    print(f"Forward centroid path length  : {report.centroid_path_length_forward:.8f}")
    print(f"Reverse centroid path length  : {report.centroid_path_length_reverse:.8f}")
    print(f"Centroid reversibility gap    : {report.centroid_reversibility_gap:.8f}")
    print(f"JS forward/reverse entropy    : {report.js_forward_reverse_entropy_steps:.8f}")
    print(f"Transition asymmetry score    : {report.transition_asymmetry_score:.8f}")
    print(f"Reading                       : {report.reading}")
    print("-" * 92)
    print(report.limits)
    print("=" * 92)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="German Gamma v5.8 reversibility diagnostic.")
    parser.add_argument("--input", required=True, help="CSV, TXT, XLSX, or XLS input.")
    parser.add_argument("--columns", required=True, help="Numeric columns separated by comma.")
    parser.add_argument("--time-column", default="", help="Optional time column for sorting.")
    parser.add_argument("--window-size", type=int, default=120)
    parser.add_argument("--step", type=int, default=60)
    parser.add_argument("--bins", type=int, default=8)
    parser.add_argument("--critical-score", type=float, default=0.10)
    parser.add_argument("--json-out", default="german_gamma_v5_8_reversibility.json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = analyze(args)
    print_report(report)
    write_json(Path(args.json_out), asdict(report))
    print(f"JSON: {Path(args.json_out).resolve()}")


if __name__ == "__main__":
    main()
