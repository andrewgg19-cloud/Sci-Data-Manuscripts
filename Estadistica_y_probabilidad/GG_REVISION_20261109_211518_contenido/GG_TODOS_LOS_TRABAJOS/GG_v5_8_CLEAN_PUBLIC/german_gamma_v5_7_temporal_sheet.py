#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German Gamma v5.7 - Temporal Sheet Layer.

Each temporal window is treated as a frozen local sheet. For every sheet the
script estimates:

- C_T: temporal sheet mirror asymmetry.
- E_res: residual energy between base and filtered feature centroids.
- Delta_S: entropy change.
- P_i: empirical null probability of observing C_T or larger.
- A_T: Temporal Sheet Energy.

    A_T = C_T * log(1 + E_res) * |Delta_S| * [-log(P_i)]

This is an exploratory diagnostic. It does not prove fraud, intent, causality,
or experimental invalidity.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


MODEL_NAME = "German Gamma v5.7 Temporal Sheet"


@dataclass(frozen=True)
class TemporalSheetPoint:
    window_id: int
    start_index: int
    end_index: int
    n_window: int
    n_filtered: int
    survival_rate: float
    c_t_mirror: float | None
    residual_energy: float | None
    entropy_base: float | None
    entropy_filtered: float | None
    delta_entropy: float | None
    p_empirical: float | None
    temporal_sheet_energy: float | None
    support_state: str
    reading: str


@dataclass(frozen=True)
class TemporalSheetReport:
    model: str
    input: str
    columns: list[str]
    filter_expression: str
    window_size: int
    step: int
    bins: int
    permutations: int
    n_windows: int
    points: list[TemporalSheetPoint]
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


def numeric_columns(df: pd.DataFrame, explicit: str) -> list[str]:
    cols = [c.strip() for c in explicit.split(",") if c.strip()]
    if len(cols) != 3:
        raise ValueError("Temporal sheet requires exactly three numeric columns.")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return cols


def identity_filter(cols: list[str]) -> str:
    return f"{cols[0]} == {cols[0]}"


def mask_from_expr(df: pd.DataFrame, expr: str) -> np.ndarray:
    out = df.eval(expr, engine="python")
    mask = np.asarray(out, dtype=bool)
    if len(mask) != len(df):
        raise ValueError("Expression did not return a valid row mask.")
    return mask


def finite_matrix(df: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    x = df[cols].to_numpy(dtype=float)
    finite = np.isfinite(x).all(axis=1)
    return x[finite], finite


def mirror_center(x: np.ndarray) -> np.ndarray:
    return 2.0 * np.mean(x, axis=0, keepdims=True) - x


def histogram_edges(a: np.ndarray, b: np.ndarray, bins: int) -> list[np.ndarray]:
    both = np.vstack([a, b])
    edges = []
    for j in range(both.shape[1]):
        col = both[:, j]
        lo = float(np.nanmin(col))
        hi = float(np.nanmax(col))
        if abs(hi - lo) <= 1e-15:
            lo -= 0.5
            hi += 0.5
        edges.append(np.linspace(lo, hi, bins + 1))
    return edges


def hist_prob(x: np.ndarray, edges: list[np.ndarray]) -> np.ndarray:
    hist, _ = np.histogramdd(x, bins=edges)
    p = hist.astype(float).ravel()
    total = float(p.sum())
    if total <= 0:
        raise ValueError("Empty histogram.")
    return p / total


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    pm = p > 0
    qm = q > 0
    return float(
        0.5 * np.sum(p[pm] * np.log2(p[pm] / m[pm]))
        + 0.5 * np.sum(q[qm] * np.log2(q[qm] / m[qm]))
    )


def mirror_asymmetry(base: np.ndarray, filtered: np.ndarray, bins: int) -> float:
    if len(base) == 0 or len(filtered) == 0:
        raise ValueError("Mirror asymmetry requires non-empty base and filtered arrays.")
    route_1 = mirror_center(filtered)
    route_2 = mirror_center(base)
    # Route 2 is restricted to the same sample size scale by nearest center distance.
    center_f = np.mean(filtered, axis=0, keepdims=True)
    d = np.linalg.norm(route_2 - center_f, axis=1)
    keep = np.argsort(d)[: len(filtered)]
    route_2 = route_2[keep]
    edges = histogram_edges(route_1, route_2, bins)
    p = hist_prob(route_1, edges)
    q = hist_prob(route_2, edges)
    return js_divergence(p, q)


def feature_map(x: np.ndarray) -> np.ndarray:
    x1, x2, x3 = x[:, 0], x[:, 1], x[:, 2]
    return np.column_stack([x1, x2, x3, x1 * x2, x1 * x3, x2 * x3, x1**2, x2**2, x3**2])


def residual_energy(base: np.ndarray, filtered: np.ndarray) -> float:
    phi_b = feature_map(base)
    phi_f = feature_map(filtered)
    return float(np.sum((np.mean(phi_b, axis=0) - np.mean(phi_f, axis=0)) ** 2))


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
    p = p / p.sum()
    h = -float(np.sum(p * np.log(p)))
    return h / math.log(len(hist.ravel())) if len(hist.ravel()) > 1 else 0.0


def empirical_p_value(
    base: np.ndarray,
    n_filtered: int,
    observed_ct: float,
    *,
    bins: int,
    permutations: int,
    seed: int,
) -> float | None:
    if permutations <= 0:
        return None
    if n_filtered <= 0 or n_filtered >= len(base):
        return None
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(permutations):
        idx = rng.choice(len(base), size=n_filtered, replace=False)
        sim_f = base[idx]
        try:
            sims.append(mirror_asymmetry(base, sim_f, bins))
        except Exception:
            continue
    if not sims:
        return None
    arr = np.asarray(sims, dtype=float)
    # Add-one correction avoids p=0 and stabilizes -log(P_i).
    return float((np.sum(arr >= observed_ct) + 1) / (len(arr) + 1))


def temporal_sheet_energy(ct: float, e_res: float, delta_s: float, p_emp: float | None) -> float | None:
    if p_emp is None or p_emp <= 0:
        return None
    return float(ct * math.log1p(e_res) * abs(delta_s) * (-math.log(p_emp)))


def reading_from_values(at: float | None, p_emp: float | None, support_state: str, critical: float) -> str:
    if support_state != "complete_temporal_sheet":
        return support_state
    if at is None:
        return "not_calibrated_temporal_sheet"
    if p_emp is not None and p_emp < 0.05 and at >= critical:
        return "rare_structural_temporal_sheet"
    if at >= critical:
        return "exploratory_temporal_sheet_signal"
    return "compatible_temporal_sheet"


def analyze_temporal_sheets(args: argparse.Namespace) -> TemporalSheetReport:
    df = load_table(Path(args.input))
    cols = numeric_columns(df, args.columns)
    expr = args.filter or identity_filter(cols)
    if args.time_column:
        if args.time_column not in df.columns:
            raise ValueError(f"Missing time column: {args.time_column}")
        df = df.sort_values(args.time_column).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    points: list[TemporalSheetPoint] = []
    window_id = 0
    for start in range(0, max(0, len(df) - args.window_size + 1), args.step):
        end = start + args.window_size
        w = df.iloc[start:end].copy()
        x_base, finite = finite_matrix(w, cols)
        w = w.loc[finite].reset_index(drop=True)
        if len(w) < args.min_n:
            points.append(
                TemporalSheetPoint(
                    window_id=window_id,
                    start_index=start,
                    end_index=end - 1,
                    n_window=int(len(w)),
                    n_filtered=0,
                    survival_rate=0.0,
                    c_t_mirror=None,
                    residual_energy=None,
                    entropy_base=None,
                    entropy_filtered=None,
                    delta_entropy=None,
                    p_empirical=None,
                    temporal_sheet_energy=None,
                    support_state="insufficient_window_size",
                    reading="insufficient_window_size",
                )
            )
            window_id += 1
            continue

        fmask = mask_from_expr(w, expr)
        x_f = w.loc[fmask, cols].to_numpy(dtype=float)
        n_filtered = int(len(x_f))
        if n_filtered < args.min_filtered:
            support = "insufficient_filtered_support"
            ct = e = h_base = h_f = delta = p_emp = at = None
        elif n_filtered >= len(x_base):
            support = "complete_temporal_sheet"
            ct = 0.0
            e = 0.0
            h_base = entropy_nd(feature_map(x_base), args.bins)
            h_f = h_base
            delta = 0.0
            p_emp = None
            at = 0.0
        else:
            support = "complete_temporal_sheet"
            ct = mirror_asymmetry(x_base, x_f, args.bins)
            e = residual_energy(x_base, x_f)
            h_base = entropy_nd(feature_map(x_base), args.bins)
            h_f = entropy_nd(feature_map(x_f), args.bins)
            delta = h_base - h_f
            p_emp = empirical_p_value(
                x_base,
                n_filtered,
                ct,
                bins=args.bins,
                permutations=args.permutations,
                seed=args.seed + window_id,
            )
            at = temporal_sheet_energy(ct, e, delta, p_emp)

        points.append(
            TemporalSheetPoint(
                window_id=window_id,
                start_index=start,
                end_index=end - 1,
                n_window=int(len(w)),
                n_filtered=n_filtered,
                survival_rate=float(n_filtered / len(w)) if len(w) else 0.0,
                c_t_mirror=ct,
                residual_energy=e,
                entropy_base=h_base,
                entropy_filtered=h_f,
                delta_entropy=delta,
                p_empirical=p_emp,
                temporal_sheet_energy=at,
                support_state=support,
                reading=reading_from_values(at, p_emp, support, args.critical_energy),
            )
        )
        window_id += 1

    return TemporalSheetReport(
        model=MODEL_NAME,
        input=args.input,
        columns=cols,
        filter_expression=expr,
        window_size=int(args.window_size),
        step=int(args.step),
        bins=int(args.bins),
        permutations=int(args.permutations),
        n_windows=len(points),
        points=points,
        limits="Exploratory temporal sheet diagnostic. It does not prove fraud, intent, causality, or invalidity.",
    )


def write_csv(path: Path, report: TemporalSheetReport) -> None:
    fields = [
        "window_id",
        "start_index",
        "end_index",
        "n_window",
        "n_filtered",
        "survival_rate",
        "c_t_mirror",
        "residual_energy",
        "entropy_base",
        "entropy_filtered",
        "delta_entropy",
        "p_empirical",
        "temporal_sheet_energy",
        "support_state",
        "reading",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for point in report.points:
            writer.writerow(asdict(point))


def print_report(report: TemporalSheetReport) -> None:
    print("=" * 96)
    print("GERMAN GAMMA v5.7 - TEMPORAL SHEET")
    print("=" * 96)
    print(f"Input      : {report.input}")
    print(f"Columns    : {', '.join(report.columns)}")
    print(f"Filter     : {report.filter_expression}")
    print(f"Windows    : {report.n_windows}")
    print(f"Window/step: {report.window_size}/{report.step}")
    print("-" * 96)
    print("window,n,n_f,C_T,E_res,Delta_S,P_i,A_T,reading")
    for p in report.points:
        def fmt(v: float | None) -> str:
            return "" if v is None else f"{v:.6f}"
        print(
            f"{p.window_id},{p.n_window},{p.n_filtered},{fmt(p.c_t_mirror)},"
            f"{fmt(p.residual_energy)},{fmt(p.delta_entropy)},{fmt(p.p_empirical)},"
            f"{fmt(p.temporal_sheet_energy)},{p.reading}"
        )
    print("-" * 96)
    print(report.limits)
    print("=" * 96)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="German Gamma v5.7 temporal sheet diagnostic.")
    parser.add_argument("--input", required=True, help="CSV, TXT, XLSX, or XLS input.")
    parser.add_argument("--columns", required=True, help="Exactly three numeric columns: x1,x2,x3.")
    parser.add_argument("--time-column", default="", help="Optional time column for sorting.")
    parser.add_argument("--filter", default="", help='Filter expression. Example: "x1 > 0"')
    parser.add_argument("--window-size", type=int, default=120)
    parser.add_argument("--step", type=int, default=60)
    parser.add_argument("--bins", type=int, default=5)
    parser.add_argument("--permutations", type=int, default=200)
    parser.add_argument("--min-n", type=int, default=30)
    parser.add_argument("--min-filtered", type=int, default=8)
    parser.add_argument("--critical-energy", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=20260716)
    parser.add_argument("--json-out", default="german_gamma_v5_7_temporal_sheet.json")
    parser.add_argument("--csv-out", default="german_gamma_v5_7_temporal_sheet.csv")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    report = analyze_temporal_sheets(args)
    print_report(report)
    write_json(Path(args.json_out), asdict(report))
    write_csv(Path(args.csv_out), report)
    print(f"JSON: {Path(args.json_out).resolve()}")
    print(f"CSV : {Path(args.csv_out).resolve()}")


if __name__ == "__main__":
    main()
