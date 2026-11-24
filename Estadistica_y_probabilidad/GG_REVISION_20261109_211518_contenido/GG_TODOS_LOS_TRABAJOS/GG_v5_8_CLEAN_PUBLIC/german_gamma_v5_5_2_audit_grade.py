#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German Gamma v5.5.2 - Filter-Induced Structure Diagnostic.

Audit-grade cleanup:
- No EPS is used to force finite primary 2x2 results.
- Zero cells are reported as support conditions, not hidden as numbers.
- 2x2 output includes classical statistical checks when scipy is available.
- Horizon-mirror output includes an empirical permutation calibration.

This tool is exploratory. It does not prove fraud, intent, causality, or
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

try:
    from scipy.stats import chi2_contingency, fisher_exact
except Exception:  # pragma: no cover - optional dependency guard
    chi2_contingency = None
    fisher_exact = None


MODEL_NAME = "German Gamma v5.5.2 audit-grade"


@dataclass(frozen=True)
class Cell2x2:
    name: str
    accepted: int
    total: int
    rejected: int
    rate: float


@dataclass(frozen=True)
class ShadowResult:
    model: str
    metric_scope: str
    cells: list[Cell2x2]
    support_state: str
    min_total_cell: int
    min_accepted_cell: int
    finite_metric_evaluable: bool
    rate_interaction: float | None
    shadow_log_score: float | None
    classical_odds_ratio: float | None
    fisher_p_value: float | None
    chi_square_p_value: float | None
    bootstrap_p_value: float | None
    bootstrap_interval_95: tuple[float, float] | None
    reading: str
    limits: str


@dataclass(frozen=True)
class TemporalPoint:
    window: str
    support_state: str
    shadow_log_score: float | None
    entropy_normalized: float
    delta_shadow: float | None
    delta_entropy: float | None
    exploratory_flag: bool
    persistence_run: int
    temporal_status: str


@dataclass(frozen=True)
class HorizonResult:
    model: str
    input: str
    columns: list[str]
    horizon: str
    mirror: str
    n_total: int
    n_horizon: int
    horizon_rate: float
    bins_per_column: int
    c_h_js: float
    l1_histograms: float
    permutation_p_value: float | None
    permutation_interval_95: tuple[float, float] | None
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


def safe_rate(accepted: int, total: int) -> float:
    if total <= 0:
        raise ValueError("Each total N must be greater than zero.")
    if accepted < 0 or accepted > total:
        raise ValueError("Each accepted count n must satisfy 0 <= n <= N.")
    return accepted / total


def support_state(cells: list[Cell2x2]) -> tuple[str, int, int, bool]:
    min_total = min(c.total for c in cells)
    min_accepted = min(c.accepted for c in cells)
    if min_total <= 0:
        return "not_evaluable_total_support", min_total, min_accepted, False
    if min_accepted <= 0:
        return "expressed_support_loss", min_total, min_accepted, False
    return "complete_support", min_total, min_accepted, True


def entropy_normalized(values: list[int | float]) -> float:
    arr = np.asarray(values, dtype=float)
    total = float(arr.sum())
    if total <= 0 or len(arr) <= 1:
        return 0.0
    p = arr / total
    p = p[p > 0]
    h = -float(np.sum(p * np.log(p)))
    return h / math.log(len(arr))


def make_cells(n00: int, N00: int, n01: int, N01: int, n10: int, N10: int, n11: int, N11: int) -> list[Cell2x2]:
    raw = [("00", n00, N00), ("01", n01, N01), ("10", n10, N10), ("11", n11, N11)]
    return [Cell2x2(name, n, N, N - n, safe_rate(n, N)) for name, n, N in raw]


def rate_interaction_score(cells: list[Cell2x2]) -> tuple[float, float]:
    p = {c.name: c.rate for c in cells}
    # This is a log-linear multiplicative contrast of acceptance rates.
    interaction = (p["00"] * p["11"]) / (p["01"] * p["10"])
    return interaction, abs(math.log(interaction))


def classical_or(cells: list[Cell2x2]) -> float | None:
    c = {cell.name: cell for cell in cells}
    values = [c["00"].accepted, c["00"].rejected, c["01"].accepted, c["01"].rejected,
              c["10"].accepted, c["10"].rejected, c["11"].accepted, c["11"].rejected]
    if any(v <= 0 for v in values):
        return None
    odds = {
        key: c[key].accepted / c[key].rejected
        for key in ["00", "01", "10", "11"]
    }
    return (odds["00"] * odds["11"]) / (odds["01"] * odds["10"])


def fisher_layer(cells: list[Cell2x2]) -> float | None:
    if fisher_exact is None:
        return None
    # Conservative summary: diagonals vs off-diagonals, accepted/rejected.
    c = {cell.name: cell for cell in cells}
    table = np.array(
        [
            [c["00"].accepted + c["11"].accepted, c["00"].rejected + c["11"].rejected],
            [c["01"].accepted + c["10"].accepted, c["01"].rejected + c["10"].rejected],
        ],
        dtype=int,
    )
    try:
        return float(fisher_exact(table, alternative="two-sided").pvalue)
    except AttributeError:
        _, p = fisher_exact(table, alternative="two-sided")
        return float(p)


def chi_square_layer(cells: list[Cell2x2]) -> float | None:
    if chi2_contingency is None:
        return None
    table = np.array([[c.accepted, c.rejected] for c in cells], dtype=int)
    if np.any(table.sum(axis=1) <= 0):
        return None
    try:
        _, p, _, expected = chi2_contingency(table)
    except Exception:
        return None
    if np.any(expected < 5):
        return None
    return float(p)


def bootstrap_shadow(cells: list[Cell2x2], observed_score: float, *, n_boot: int, seed: int) -> tuple[float, tuple[float, float]]:
    rng = np.random.default_rng(seed)
    total_accepted = sum(c.accepted for c in cells)
    total_n = sum(c.total for c in cells)
    global_rate = total_accepted / total_n
    scores: list[float] = []

    for _ in range(n_boot):
        sim_cells = []
        usable = True
        for c in cells:
            n_sim = int(rng.binomial(c.total, global_rate))
            if n_sim <= 0:
                usable = False
                break
            sim_cells.append(Cell2x2(c.name, n_sim, c.total, c.total - n_sim, n_sim / c.total))
        if usable:
            _, score = rate_interaction_score(sim_cells)
            scores.append(score)

    if not scores:
        return float("nan"), (float("nan"), float("nan"))
    arr = np.asarray(scores, dtype=float)
    p_value = float(np.mean(arr >= observed_score))
    interval = (float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)))
    return p_value, interval


def read_shadow_result(
    n00: int,
    N00: int,
    n01: int,
    N01: int,
    n10: int,
    N10: int,
    n11: int,
    N11: int,
    *,
    bootstrap: int,
    seed: int,
) -> ShadowResult:
    cells = make_cells(n00, N00, n01, N01, n10, N10, n11, N11)
    state, min_total, min_accepted, finite = support_state(cells)

    interaction = None
    score = None
    boot_p = None
    boot_interval = None
    if finite:
        interaction, score = rate_interaction_score(cells)
        if bootstrap > 0:
            boot_p, boot_interval = bootstrap_shadow(cells, score, n_boot=bootstrap, seed=seed)

    or_value = classical_or(cells)
    fisher_p = fisher_layer(cells)
    chi_p = chi_square_layer(cells)

    if not finite:
        reading = "not_evaluable_as_finite_shadow"
    elif boot_p is not None and math.isfinite(boot_p) and boot_p < 0.05:
        reading = "empirically_calibrated_selection_signal"
    elif score is not None and score >= 0.25:
        reading = "exploratory_selection_signal_requires_calibration"
    else:
        reading = "compatible_with_local_proportionality"

    return ShadowResult(
        model=MODEL_NAME,
        metric_scope="2x2 acceptance-rate interaction; related to classical log-linear contrasts, not a new standalone statistic",
        cells=cells,
        support_state=state,
        min_total_cell=min_total,
        min_accepted_cell=min_accepted,
        finite_metric_evaluable=finite,
        rate_interaction=interaction,
        shadow_log_score=score,
        classical_odds_ratio=or_value,
        fisher_p_value=fisher_p,
        chi_square_p_value=chi_p,
        bootstrap_p_value=boot_p,
        bootstrap_interval_95=boot_interval,
        reading=reading,
        limits="Exploratory diagnostic only. It does not prove fraud, intent, causality, or invalidity.",
    )


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    raise ValueError("Unsupported file. Use CSV, TXT, XLSX, or XLS.")


def numeric_columns(df: pd.DataFrame, explicit: str) -> list[str]:
    if explicit:
        cols = [c.strip() for c in explicit.split(",") if c.strip()]
    else:
        cols = list(df.select_dtypes(include=[np.number]).columns)
    if not cols:
        raise ValueError("No numeric columns available.")
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return cols


def identity_horizon(cols: list[str]) -> str:
    return f"{cols[0]} == {cols[0]}"


def horizon_mask(df: pd.DataFrame, expression: str) -> np.ndarray:
    out = df.eval(expression, engine="python")
    mask = np.asarray(out, dtype=bool)
    if mask.shape[0] != len(df):
        raise ValueError("Horizon expression did not return a valid row mask.")
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
        raise ValueError("One route produced zero rows; horizon score is not evaluable.")
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


def compute_ch_from_arrays(x_h: np.ndarray, x_base: np.ndarray, cols: list[str], horizon: str, mirror: str, bins: int) -> tuple[float, float]:
    route_h_then_m = mirror_transform(x_h, mirror)
    x_m = mirror_transform(x_base, mirror)
    route_m_then_h = apply_horizon_to_matrix(x_m, cols, horizon)
    edges = histogram_edges(route_h_then_m, route_m_then_h, bins)
    p = hist_prob(route_h_then_m, edges)
    q = hist_prob(route_m_then_h, edges)
    return js_divergence(p, q), float(np.sum(np.abs(p - q)))


def horizon_reading(c_h: float, p_value: float | None) -> str:
    if p_value is not None and math.isfinite(p_value):
        if p_value < 0.05:
            return "empirically_calibrated_horizon_mirror_difference"
        return "not_significant_under_permutation_null"
    if c_h < 0.02:
        return "low_horizon_mirror_difference_exploratory"
    return "exploratory_horizon_mirror_difference_requires_calibration"


def horizon_result(
    input_path: Path,
    *,
    cols_arg: str,
    horizon: str,
    mirror: str,
    bins: int,
    permutations: int,
    seed: int,
) -> HorizonResult:
    df = load_table(input_path)
    cols = numeric_columns(df, cols_arg)
    horizon_expr = horizon or identity_horizon(cols)
    finite_base = np.isfinite(df[cols].to_numpy(dtype=float)).all(axis=1)
    h_mask = horizon_mask(df, horizon_expr) & finite_base
    x_base = clean_matrix(df, cols, finite_base)
    x_h = clean_matrix(df, cols, h_mask)
    c_h, l1 = compute_ch_from_arrays(x_h, x_base, cols, horizon_expr, mirror, bins)

    p_value = None
    interval = None
    if permutations > 0:
        rng = np.random.default_rng(seed)
        base_df = pd.DataFrame(x_base, columns=cols)
        h_size = len(x_h)
        sims = []
        for _ in range(permutations):
            mask = np.zeros(len(base_df), dtype=bool)
            mask[rng.choice(len(base_df), size=h_size, replace=False)] = True
            sim_h = clean_matrix(base_df, cols, mask)
            try:
                sim_ch, _ = compute_ch_from_arrays(sim_h, x_base, cols, horizon_expr, mirror, bins)
            except Exception:
                continue
            sims.append(sim_ch)
        if sims:
            arr = np.asarray(sims, dtype=float)
            p_value = float(np.mean(arr >= c_h))
            interval = (float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)))

    return HorizonResult(
        model=MODEL_NAME,
        input=str(input_path),
        columns=cols,
        horizon=horizon_expr,
        mirror=mirror,
        n_total=int(len(x_base)),
        n_horizon=int(len(x_h)),
        horizon_rate=float(len(x_h) / len(x_base)) if len(x_base) else float("nan"),
        bins_per_column=bins,
        c_h_js=c_h,
        l1_histograms=l1,
        permutation_p_value=p_value,
        permutation_interval_95=interval,
        reading=horizon_reading(c_h, p_value),
        limits="C_H is representation- and bin-sensitive. Interpret only with calibration and domain context.",
    )


def temporal_result(path: Path, *, critical_score: float, k: int) -> list[TemporalPoint]:
    required = ["n00", "N00", "n01", "N01", "n10", "N10", "n11", "N11"]
    points: list[TemporalPoint] = []
    prev_score = None
    prev_entropy = None
    run = 0

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Temporal CSV has no header.")
        missing = [col for col in required if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        for idx, row in enumerate(reader, start=1):
            window = str(row.get("ventana") or row.get("window") or idx)
            vals = {col: int(float(row[col])) for col in required}
            shadow = read_shadow_result(
                vals["n00"], vals["N00"], vals["n01"], vals["N01"], vals["n10"], vals["N10"], vals["n11"], vals["N11"],
                bootstrap=0,
                seed=0,
            )
            score = shadow.shadow_log_score
            h = entropy_normalized([vals["n00"], vals["n01"], vals["n10"], vals["n11"]])
            flag = score is not None and score >= critical_score
            run = run + 1 if flag else 0
            if not shadow.finite_metric_evaluable:
                status = shadow.support_state
            elif run >= k:
                status = "temporal_persistence_flag"
            elif flag:
                status = "exploratory_single_window_flag"
            else:
                status = "no_temporal_persistence"
            points.append(
                TemporalPoint(
                    window=window,
                    support_state=shadow.support_state,
                    shadow_log_score=score,
                    entropy_normalized=h,
                    delta_shadow=None if prev_score is None or score is None else score - prev_score,
                    delta_entropy=None if prev_entropy is None else h - prev_entropy,
                    exploratory_flag=flag,
                    persistence_run=run,
                    temporal_status=status,
                )
            )
            if score is not None:
                prev_score = score
            prev_entropy = h
    return points


def print_shadow(r: ShadowResult) -> None:
    print("=" * 78)
    print("GERMAN GAMMA v5.5.2 - 2x2 FILTER DIAGNOSTIC")
    print("=" * 78)
    for c in r.cells:
        print(f"{c.name}: accepted={c.accepted} total={c.total} rejected={c.rejected} rate={c.rate:.8f}")
    print("-" * 78)
    print(f"support_state              : {r.support_state}")
    print(f"finite_metric_evaluable    : {r.finite_metric_evaluable}")
    print(f"rate_interaction           : {r.rate_interaction}")
    print(f"shadow_log_score           : {r.shadow_log_score}")
    print(f"classical_odds_ratio       : {r.classical_odds_ratio}")
    print(f"fisher_p_value             : {r.fisher_p_value}")
    print(f"chi_square_p_value         : {r.chi_square_p_value}")
    print(f"bootstrap_p_value          : {r.bootstrap_p_value}")
    print(f"bootstrap_interval_95      : {r.bootstrap_interval_95}")
    print(f"reading                    : {r.reading}")
    print(f"limits                     : {r.limits}")
    print("=" * 78)


def print_horizon(r: HorizonResult) -> None:
    print("=" * 78)
    print("GERMAN GAMMA v5.5.2 - HORIZON-MIRROR DIAGNOSTIC")
    print("=" * 78)
    print(f"input                      : {r.input}")
    print(f"columns                    : {', '.join(r.columns)}")
    print(f"horizon                    : {r.horizon}")
    print(f"mirror                     : {r.mirror}")
    print(f"n_total                    : {r.n_total}")
    print(f"n_horizon                  : {r.n_horizon}")
    print(f"horizon_rate               : {r.horizon_rate:.6f}")
    print(f"c_h_js                     : {r.c_h_js:.6f}")
    print(f"l1_histograms              : {r.l1_histograms:.6f}")
    print(f"permutation_p_value        : {r.permutation_p_value}")
    print(f"permutation_interval_95    : {r.permutation_interval_95}")
    print(f"reading                    : {r.reading}")
    print(f"limits                     : {r.limits}")
    print("=" * 78)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="German Gamma v5.5.2 audit-grade diagnostic.")
    sub = parser.add_subparsers(dest="command", required=True)

    shadow = sub.add_parser("shadow", help="2x2 acceptance-rate diagnostic.")
    shadow.add_argument("--n00", type=int, required=True)
    shadow.add_argument("--N00", type=int, required=True)
    shadow.add_argument("--n01", type=int, required=True)
    shadow.add_argument("--N01", type=int, required=True)
    shadow.add_argument("--n10", type=int, required=True)
    shadow.add_argument("--N10", type=int, required=True)
    shadow.add_argument("--n11", type=int, required=True)
    shadow.add_argument("--N11", type=int, required=True)
    shadow.add_argument("--bootstrap", type=int, default=10000)
    shadow.add_argument("--seed", type=int, default=20260517)
    shadow.add_argument("--json-out", default="german_gamma_v5_5_2_shadow.json")

    temporal = sub.add_parser("temporal", help="Temporal sequence of 2x2 windows.")
    temporal.add_argument("--temporal-csv", required=True)
    temporal.add_argument("--critical-score", type=float, default=0.25)
    temporal.add_argument("--k", type=int, default=2)
    temporal.add_argument("--json-out", default="german_gamma_v5_5_2_temporal.json")

    horizon = sub.add_parser("horizon", help="Horizon-mirror diagnostic with permutation calibration.")
    horizon.add_argument("--input", required=True)
    horizon.add_argument("--columns", default="")
    horizon.add_argument("--horizon", default="")
    horizon.add_argument("--mirror", default="center_reflect", choices=["negate", "reverse_columns", "center_reflect", "z_reflect"])
    horizon.add_argument("--bins", type=int, default=8)
    horizon.add_argument("--permutations", type=int, default=500)
    horizon.add_argument("--seed", type=int, default=20260517)
    horizon.add_argument("--json-out", default="german_gamma_v5_5_2_horizon.json")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "shadow":
        result = read_shadow_result(
            args.n00, args.N00, args.n01, args.N01, args.n10, args.N10, args.n11, args.N11,
            bootstrap=args.bootstrap,
            seed=args.seed,
        )
        print_shadow(result)
        write_json(Path(args.json_out), asdict(result))
        print(f"JSON: {Path(args.json_out).resolve()}")
        return

    if args.command == "temporal":
        points = temporal_result(Path(args.temporal_csv), critical_score=args.critical_score, k=args.k)
        write_json(Path(args.json_out), [asdict(p) for p in points])
        print(f"Temporal windows analyzed: {len(points)}")
        print(f"JSON: {Path(args.json_out).resolve()}")
        return

    if args.command == "horizon":
        result = horizon_result(
            Path(args.input),
            cols_arg=args.columns,
            horizon=args.horizon,
            mirror=args.mirror,
            bins=args.bins,
            permutations=args.permutations,
            seed=args.seed,
        )
        print_horizon(result)
        write_json(Path(args.json_out), asdict(result))
        print(f"JSON: {Path(args.json_out).resolve()}")
        return


if __name__ == "__main__":
    main()
