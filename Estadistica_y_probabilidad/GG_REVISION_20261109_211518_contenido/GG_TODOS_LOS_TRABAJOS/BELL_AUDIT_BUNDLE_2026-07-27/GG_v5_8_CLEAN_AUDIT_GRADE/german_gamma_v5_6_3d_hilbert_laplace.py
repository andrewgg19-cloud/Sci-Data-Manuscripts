#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German Gamma v5.6 - 3D / Hilbert / Laplace diagnostic layer.

This version adds four audit-grade commands:

1. cubic_shadow
   2x2x2 acceptance-rate interaction contrast.

2. cubic_mirror
   Horizon-mirror diagnostic over a 3D point cloud.

3. energy_entropy
   Residual energy and entropy coupling in a feature/Hilbert representation.

4. laplace_temporal
   Discrete Laplace response of a temporal diagnostic series.

The tool is exploratory. It does not prove fraud, intent, causality, or
experimental invalidity.
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


MODEL_NAME = "German Gamma v5.6 3D/Hilbert/Laplace"
CUBE_KEYS = ["000", "001", "010", "011", "100", "101", "110", "111"]


@dataclass(frozen=True)
class CubeCell:
    key: str
    accepted: int
    total: int
    rejected: int
    rate: float


@dataclass(frozen=True)
class CubicShadowResult:
    model: str
    metric_scope: str
    cells: list[CubeCell]
    support_state: str
    min_total_cell: int
    min_accepted_cell: int
    raw_evaluable: bool
    cubic_interaction_raw: float | None
    cubic_shadow_score_raw: float | None
    laplace_alpha: float
    cubic_interaction_laplace: float
    cubic_shadow_score_laplace: float
    permutation_p_value: float | None
    permutation_interval_95: tuple[float, float] | None
    reading: str
    limits: str


@dataclass(frozen=True)
class CubicMirrorResult:
    model: str
    input: str
    columns: list[str]
    horizon: str
    mirror: str
    n_total: int
    n_horizon: int
    horizon_rate: float
    bins_per_axis: int
    c3_js: float
    l1_histograms: float
    permutation_p_value: float | None
    permutation_interval_95: tuple[float, float] | None
    reading: str
    limits: str


@dataclass(frozen=True)
class EnergyEntropyResult:
    model: str
    input: str
    columns: list[str]
    filter_expression: str
    feature_map: str
    n_total: int
    n_filtered: int
    survival_rate: float
    residual_energy: float
    entropy_base: float
    entropy_filtered: float
    delta_entropy: float
    residual_energy_entropy_coupling: float
    reading: str
    limits: str


@dataclass(frozen=True)
class LaplaceTemporalResult:
    model: str
    input: str
    value_column: str
    n_points: int
    s_values: list[float]
    laplace_response: list[float]
    normalized_response: list[float]
    area_trapezoid: float
    persistence_mass: float
    reading: str
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


def numeric_columns(df: pd.DataFrame, explicit: str, *, required: int | None = None) -> list[str]:
    if explicit:
        cols = [c.strip() for c in explicit.split(",") if c.strip()]
    else:
        cols = list(df.select_dtypes(include=[np.number]).columns)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if required is not None and len(cols) != required:
        raise ValueError(f"Expected exactly {required} numeric columns.")
    if not cols:
        raise ValueError("No numeric columns available.")
    return cols


def safe_rate(accepted: int, total: int) -> float:
    if total <= 0:
        raise ValueError("Each total N must be greater than zero.")
    if accepted < 0 or accepted > total:
        raise ValueError("Each accepted count n must satisfy 0 <= n <= N.")
    return accepted / total


def cube_cells_from_args(args: argparse.Namespace) -> list[CubeCell]:
    cells = []
    for key in CUBE_KEYS:
        n = int(getattr(args, f"n{key}"))
        total = int(getattr(args, f"N{key}"))
        cells.append(CubeCell(key, n, total, total - n, safe_rate(n, total)))
    return cells


def cube_support(cells: list[CubeCell]) -> tuple[str, int, int, bool]:
    min_total = min(c.total for c in cells)
    min_accepted = min(c.accepted for c in cells)
    if min_total <= 0:
        return "not_evaluable_total_support", min_total, min_accepted, False
    if min_accepted <= 0:
        return "expressed_support_loss", min_total, min_accepted, False
    return "complete_support", min_total, min_accepted, True


def cubic_interaction_from_rates(rates: dict[str, float]) -> float:
    numerator = rates["000"] * rates["011"] * rates["101"] * rates["110"]
    denominator = rates["001"] * rates["010"] * rates["100"] * rates["111"]
    return numerator / denominator


def cubic_raw_score(cells: list[CubeCell]) -> tuple[float, float]:
    rates = {c.key: c.rate for c in cells}
    interaction = cubic_interaction_from_rates(rates)
    return interaction, abs(math.log(interaction))


def cubic_laplace_score(cells: list[CubeCell], alpha: float) -> tuple[float, float]:
    rates = {c.key: (c.accepted + alpha) / (c.total + 2.0 * alpha) for c in cells}
    interaction = cubic_interaction_from_rates(rates)
    return interaction, abs(math.log(interaction))


def cubic_permutation(cells: list[CubeCell], observed_score: float, *, permutations: int, seed: int) -> tuple[float, tuple[float, float]] | tuple[None, None]:
    if permutations <= 0:
        return None, None
    rng = np.random.default_rng(seed)
    total_accepted = sum(c.accepted for c in cells)
    total_n = sum(c.total for c in cells)
    global_rate = total_accepted / total_n
    scores = []
    for _ in range(permutations):
        sim = []
        usable = True
        for c in cells:
            n_sim = int(rng.binomial(c.total, global_rate))
            if n_sim <= 0:
                usable = False
                break
            sim.append(CubeCell(c.key, n_sim, c.total, c.total - n_sim, n_sim / c.total))
        if usable:
            _, score = cubic_raw_score(sim)
            scores.append(score)
    if not scores:
        return float("nan"), (float("nan"), float("nan"))
    arr = np.asarray(scores, dtype=float)
    return float(np.mean(arr >= observed_score)), (float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)))


def cubic_shadow(args: argparse.Namespace) -> CubicShadowResult:
    cells = cube_cells_from_args(args)
    state, min_total, min_accepted, raw_evaluable = cube_support(cells)
    raw_interaction = None
    raw_score = None
    p_value = None
    interval = None
    if raw_evaluable:
        raw_interaction, raw_score = cubic_raw_score(cells)
        p_value, interval = cubic_permutation(cells, raw_score, permutations=args.permutations, seed=args.seed)

    laplace_interaction, laplace_score = cubic_laplace_score(cells, args.alpha)

    if not raw_evaluable:
        reading = "raw_not_evaluable_support_loss_laplace_auxiliary_only"
    elif p_value is not None and math.isfinite(p_value) and p_value < 0.05:
        reading = "empirically_calibrated_cubic_selection_signal"
    elif raw_score is not None and raw_score >= args.critical_score:
        reading = "exploratory_cubic_selection_signal_requires_calibration"
    else:
        reading = "compatible_with_cubic_proportionality"

    return CubicShadowResult(
        model=MODEL_NAME,
        metric_scope="2x2x2 acceptance-rate interaction contrast; raw score is primary, Laplace score is auxiliary",
        cells=cells,
        support_state=state,
        min_total_cell=min_total,
        min_accepted_cell=min_accepted,
        raw_evaluable=raw_evaluable,
        cubic_interaction_raw=raw_interaction,
        cubic_shadow_score_raw=raw_score,
        laplace_alpha=float(args.alpha),
        cubic_interaction_laplace=laplace_interaction,
        cubic_shadow_score_laplace=laplace_score,
        permutation_p_value=p_value,
        permutation_interval_95=interval,
        reading=reading,
        limits="Exploratory diagnostic only. Laplace regularization is not the primary result.",
    )


def identity_horizon(cols: list[str]) -> str:
    return f"{cols[0]} == {cols[0]}"


def horizon_mask(df: pd.DataFrame, expression: str) -> np.ndarray:
    out = df.eval(expression, engine="python")
    mask = np.asarray(out, dtype=bool)
    if mask.shape[0] != len(df):
        raise ValueError("Horizon/filter expression did not return a valid row mask.")
    return mask


def clean_matrix(df: pd.DataFrame, cols: list[str], mask: np.ndarray | None = None) -> np.ndarray:
    data = df.loc[mask, cols] if mask is not None else df.loc[:, cols]
    x = data.to_numpy(dtype=float)
    finite = np.isfinite(x).all(axis=1)
    return x[finite]


def mirror_transform(x: np.ndarray, mode: str) -> np.ndarray:
    if mode == "negate":
        return -x
    if mode == "reverse_columns":
        return x[:, ::-1]
    if mode == "center_reflect":
        return 2.0 * np.nanmean(x, axis=0, keepdims=True) - x
    if mode == "z_reflect":
        mu = np.nanmean(x, axis=0, keepdims=True)
        sd = np.nanstd(x, axis=0, keepdims=True)
        sd = np.where(sd <= 0, 1.0, sd)
        z = (x - mu) / sd
        return mu - z * sd
    raise ValueError("Unsupported mirror mode.")


def apply_horizon_to_matrix(x: np.ndarray, cols: list[str], expression: str) -> np.ndarray:
    temp = pd.DataFrame(x, columns=cols)
    mask = horizon_mask(temp, expression)
    return x[mask]


def histogram_edges(a: np.ndarray, b: np.ndarray, bins: int) -> list[np.ndarray]:
    both = np.vstack([a, b])
    edges = []
    for j in range(both.shape[1]):
        col = both[:, j]
        lo = float(np.nanmin(col))
        hi = float(np.nanmax(col))
        if not np.isfinite(lo) or not np.isfinite(hi):
            raise ValueError("Non-finite data in histogram input.")
        if abs(hi - lo) <= 1e-15:
            lo -= 0.5
            hi += 0.5
        edges.append(np.linspace(lo, hi, bins + 1))
    return edges


def hist_prob(x: np.ndarray, edges: list[np.ndarray]) -> np.ndarray:
    if len(x) == 0:
        raise ValueError("One route produced zero rows; mirror score is not evaluable.")
    hist, _ = np.histogramdd(x, bins=edges)
    p = hist.astype(float).ravel()
    total = float(p.sum())
    if total <= 0:
        raise ValueError("Empty histogram.")
    return p / total


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    p_mask = p > 0
    q_mask = q > 0
    kl_pm = np.sum(p[p_mask] * np.log2(p[p_mask] / m[p_mask]))
    kl_qm = np.sum(q[q_mask] * np.log2(q[q_mask] / m[q_mask]))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


def mirror_score(x_h: np.ndarray, x_base: np.ndarray, cols: list[str], horizon: str, mirror: str, bins: int) -> tuple[float, float]:
    route_h_then_m = mirror_transform(x_h, mirror)
    x_m = mirror_transform(x_base, mirror)
    route_m_then_h = apply_horizon_to_matrix(x_m, cols, horizon)
    edges = histogram_edges(route_h_then_m, route_m_then_h, bins)
    p = hist_prob(route_h_then_m, edges)
    q = hist_prob(route_m_then_h, edges)
    return js_divergence(p, q), float(np.sum(np.abs(p - q)))


def cubic_mirror(args: argparse.Namespace) -> CubicMirrorResult:
    df = load_table(Path(args.input))
    cols = numeric_columns(df, args.columns, required=3)
    horizon = args.horizon or identity_horizon(cols)
    finite_base = np.isfinite(df[cols].to_numpy(dtype=float)).all(axis=1)
    h_mask = horizon_mask(df, horizon) & finite_base
    x_base = clean_matrix(df, cols, finite_base)
    x_h = clean_matrix(df, cols, h_mask)
    c3, l1 = mirror_score(x_h, x_base, cols, horizon, args.mirror, args.bins)

    p_value = None
    interval = None
    if args.permutations > 0:
        rng = np.random.default_rng(args.seed)
        base_df = pd.DataFrame(x_base, columns=cols)
        h_size = len(x_h)
        sims = []
        for _ in range(args.permutations):
            mask = np.zeros(len(base_df), dtype=bool)
            mask[rng.choice(len(base_df), size=h_size, replace=False)] = True
            sim_h = clean_matrix(base_df, cols, mask)
            try:
                sim_c3, _ = mirror_score(sim_h, x_base, cols, horizon, args.mirror, args.bins)
            except Exception:
                continue
            sims.append(sim_c3)
        if sims:
            arr = np.asarray(sims, dtype=float)
            p_value = float(np.mean(arr >= c3))
            interval = (float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)))

    if p_value is not None and math.isfinite(p_value):
        reading = "empirically_calibrated_3d_mirror_difference" if p_value < 0.05 else "not_significant_under_permutation_null"
    else:
        reading = "exploratory_3d_mirror_difference_requires_calibration"

    return CubicMirrorResult(
        model=MODEL_NAME,
        input=args.input,
        columns=cols,
        horizon=horizon,
        mirror=args.mirror,
        n_total=int(len(x_base)),
        n_horizon=int(len(x_h)),
        horizon_rate=float(len(x_h) / len(x_base)) if len(x_base) else float("nan"),
        bins_per_axis=int(args.bins),
        c3_js=c3,
        l1_histograms=l1,
        permutation_p_value=p_value,
        permutation_interval_95=interval,
        reading=reading,
        limits="3D mirror score is representation- and bin-sensitive; interpret only with calibration.",
    )


def feature_map(x: np.ndarray, mode: str) -> np.ndarray:
    if mode == "linear":
        return x
    if mode == "quadratic":
        if x.shape[1] != 3:
            raise ValueError("Quadratic feature map expects exactly 3 columns.")
        x1, x2, x3 = x[:, 0], x[:, 1], x[:, 2]
        return np.column_stack([x1, x2, x3, x1 * x2, x1 * x3, x2 * x3, x1**2, x2**2, x3**2])
    raise ValueError("Unsupported feature map.")


def discretized_entropy(x: np.ndarray, bins: int) -> float:
    if len(x) == 0:
        return 0.0
    edges = []
    for j in range(x.shape[1]):
        col = x[:, j]
        lo, hi = float(np.nanmin(col)), float(np.nanmax(col))
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


def energy_entropy(args: argparse.Namespace) -> EnergyEntropyResult:
    df = load_table(Path(args.input))
    cols = numeric_columns(df, args.columns, required=3)
    filt = args.filter or identity_horizon(cols)
    finite_base = np.isfinite(df[cols].to_numpy(dtype=float)).all(axis=1)
    filter_mask = horizon_mask(df, filt) & finite_base
    x_base = clean_matrix(df, cols, finite_base)
    x_f = clean_matrix(df, cols, filter_mask)
    if len(x_f) == 0:
        raise ValueError("Filter selected zero rows; energy-entropy is not evaluable.")

    phi_base = feature_map(x_base, args.feature_map)
    phi_f = feature_map(x_f, args.feature_map)
    mu_base = np.mean(phi_base, axis=0)
    mu_f = np.mean(phi_f, axis=0)
    residual_energy = float(np.sum((mu_base - mu_f) ** 2))

    h_base = discretized_entropy(phi_base, args.bins)
    h_f = discretized_entropy(phi_f, args.bins)
    delta_h = h_base - h_f
    coupling = math.log1p(residual_energy) * abs(delta_h)

    if coupling >= args.critical_coupling:
        reading = "high_residual_energy_entropy_coupling_exploratory"
    elif coupling >= args.critical_coupling / 3:
        reading = "moderate_residual_energy_entropy_coupling_exploratory"
    else:
        reading = "low_residual_energy_entropy_coupling"

    return EnergyEntropyResult(
        model=MODEL_NAME,
        input=args.input,
        columns=cols,
        filter_expression=filt,
        feature_map=args.feature_map,
        n_total=int(len(x_base)),
        n_filtered=int(len(x_f)),
        survival_rate=float(len(x_f) / len(x_base)) if len(x_base) else float("nan"),
        residual_energy=residual_energy,
        entropy_base=h_base,
        entropy_filtered=h_f,
        delta_entropy=delta_h,
        residual_energy_entropy_coupling=coupling,
        reading=reading,
        limits="Exploratory geometric-informational score. It must be calibrated for operational decisions.",
    )


def laplace_temporal(args: argparse.Namespace) -> LaplaceTemporalResult:
    df = load_table(Path(args.input))
    if args.value_column not in df.columns:
        raise ValueError(f"Column not found: {args.value_column}")
    y = pd.to_numeric(df[args.value_column], errors="coerce").to_numpy(dtype=float)
    y = y[np.isfinite(y)]
    if len(y) == 0:
        raise ValueError("No finite temporal values.")
    y = np.abs(y) if args.absolute else y
    t = np.arange(len(y), dtype=float)
    s_values = [float(s.strip()) for s in args.s_values.split(",") if s.strip()]
    responses = []
    for s in s_values:
        responses.append(float(np.sum(np.exp(-s * t) * y)))
    base = responses[0] if responses and abs(responses[0]) > 1e-15 else 1.0
    normalized = [float(r / base) for r in responses]
    area = float(np.trapezoid(y, t)) if len(y) > 1 else float(y[0])
    persistence_mass = float(np.sum(y >= args.threshold) / len(y))
    if persistence_mass >= 0.5:
        reading = "high_temporal_persistence_mass"
    elif persistence_mass > 0:
        reading = "localized_temporal_persistence_mass"
    else:
        reading = "no_threshold_persistence_mass"
    return LaplaceTemporalResult(
        model=MODEL_NAME,
        input=args.input,
        value_column=args.value_column,
        n_points=int(len(y)),
        s_values=s_values,
        laplace_response=responses,
        normalized_response=normalized,
        area_trapezoid=area,
        persistence_mass=persistence_mass,
        reading=reading,
        limits="Discrete Laplace response summarizes temporal persistence; it is not causal proof.",
    )


def print_result(title: str, result: Any) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)
    data = asdict(result)
    for key, value in data.items():
        if key == "cells":
            print("cells:")
            for cell in value:
                print(f"  {cell}")
        else:
            print(f"{key}: {value}")
    print("=" * 88)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="German Gamma v5.6 3D/Hilbert/Laplace diagnostic.")
    sub = parser.add_subparsers(dest="command", required=True)

    cube = sub.add_parser("cubic_shadow", help="2x2x2 acceptance-rate interaction.")
    for key in CUBE_KEYS:
        cube.add_argument(f"--n{key}", type=int, required=True)
        cube.add_argument(f"--N{key}", type=int, required=True)
    cube.add_argument("--alpha", type=float, default=0.5, help="Laplace auxiliary smoothing alpha.")
    cube.add_argument("--permutations", type=int, default=1000)
    cube.add_argument("--critical-score", type=float, default=0.25)
    cube.add_argument("--seed", type=int, default=20260716)
    cube.add_argument("--json-out", default="german_gamma_v5_6_cubic_shadow.json")

    mirror = sub.add_parser("cubic_mirror", help="3D horizon-mirror diagnostic.")
    mirror.add_argument("--input", required=True)
    mirror.add_argument("--columns", required=True, help="Exactly three numeric columns, comma separated.")
    mirror.add_argument("--horizon", default="")
    mirror.add_argument("--mirror", default="center_reflect", choices=["negate", "reverse_columns", "center_reflect", "z_reflect"])
    mirror.add_argument("--bins", type=int, default=8)
    mirror.add_argument("--permutations", type=int, default=500)
    mirror.add_argument("--seed", type=int, default=20260716)
    mirror.add_argument("--json-out", default="german_gamma_v5_6_cubic_mirror.json")

    ee = sub.add_parser("energy_entropy", help="Residual energy and entropy coupling.")
    ee.add_argument("--input", required=True)
    ee.add_argument("--columns", required=True, help="Exactly three numeric columns, comma separated.")
    ee.add_argument("--filter", default="")
    ee.add_argument("--feature-map", default="quadratic", choices=["linear", "quadratic"])
    ee.add_argument("--bins", type=int, default=8)
    ee.add_argument("--critical-coupling", type=float, default=0.10)
    ee.add_argument("--json-out", default="german_gamma_v5_6_energy_entropy.json")

    lap = sub.add_parser("laplace_temporal", help="Discrete Laplace response of temporal series.")
    lap.add_argument("--input", required=True)
    lap.add_argument("--value-column", required=True)
    lap.add_argument("--s-values", default="0.01,0.05,0.1,0.2,0.5")
    lap.add_argument("--threshold", type=float, default=0.25)
    lap.add_argument("--absolute", action="store_true")
    lap.add_argument("--json-out", default="german_gamma_v5_6_laplace_temporal.json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "cubic_shadow":
        result = cubic_shadow(args)
        print_result("GERMAN GAMMA v5.6 - CUBIC SHADOW", result)
        write_json(Path(args.json_out), asdict(result))
        print(f"JSON: {Path(args.json_out).resolve()}")
        return
    if args.command == "cubic_mirror":
        result = cubic_mirror(args)
        print_result("GERMAN GAMMA v5.6 - CUBIC MIRROR", result)
        write_json(Path(args.json_out), asdict(result))
        print(f"JSON: {Path(args.json_out).resolve()}")
        return
    if args.command == "energy_entropy":
        result = energy_entropy(args)
        print_result("GERMAN GAMMA v5.6 - RESIDUAL ENERGY/ENTROPY", result)
        write_json(Path(args.json_out), asdict(result))
        print(f"JSON: {Path(args.json_out).resolve()}")
        return
    if args.command == "laplace_temporal":
        result = laplace_temporal(args)
        print_result("GERMAN GAMMA v5.6 - LAPLACE TEMPORAL", result)
        write_json(Path(args.json_out), asdict(result))
        print(f"JSON: {Path(args.json_out).resolve()}")
        return


if __name__ == "__main__":
    main()
