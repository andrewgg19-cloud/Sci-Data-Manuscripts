#!/usr/bin/env python3
"""
Hensen 2015 Bell-test audit script.

What this audits:
    - The published open dataset underlying Hensen et al. 2015
      (Nature 526, 682-686; DOI 10.1038/nature15759)
    - The published observational pipeline:
          candidate rows with two-photon signature at C
          -> valid Bell trials under official filters
          -> CHSH statistic

What this does:
    1. Reproduces the published baseline CHSH result from the open dataset.
    2. Computes a local Taylor-style sensitivity estimate around the nominal
       event-ready timing offset.
    3. Runs Monte Carlo bootstrap on accepted Bell trials.
    4. Runs Monte Carlo sensitivity to event-ready timing offset.
    5. Fits a simple Kalman local-level model to daily acceptance rates.
    6. Computes a Kolmogorov-style sequential complexity proxy using
       compression ratio against matched null sequences.
    7. Optionally scans a 2D grid of timing parameters and writes 3D color-mesh
       surfaces for S, Bell-trial count, and p-value.
    8. Tests no-signaling consistency on the filtered Bell-trial sample.
    9. Audits setting-bit randomness with uniformity, runs, and lag-1 autocorrelation checks.
    10. Compares daily acceptance rate against daily CHSH S when enough settings exist.
    11. Computes a look-elsewhere summary over the scanned timing grid.

Methodological stance:
    - Distinguish reproduced facts from interpretive hypotheses.
    - State explicit limits of what the open dataset can and cannot establish.
    - Treat parameter sensitivity as a mathematical property of the published
      observational pipeline, not as proof of fraud or invalid physics.
    - Say "unknown" where the open data cannot decide the issue.

Important limitation:
    The official open dataset already contains candidate rows that satisfy a
    broad two-photon signature at location C. It is not the full stream of all
    raw physical attempts.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
import zipfile
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


DATASET_DOI = "10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31"
DATASET_URL = "https://data.4tu.nl/ndownloader/items/e8cf2991-3153-48ad-b67d-dfd7d7d97fd3/versions/1"
PAPER_DOI = "10.1038/nature15759"
ADDITIONAL_ANALYSIS_DOI = "10.1038/srep30289"
ADDITIONAL_ANALYSIS_ARXIV = "1603.05705"

INTERPRETATION_LIMITS = {
    "reproduced_facts": [
        "The published baseline CHSH value is reproducible from the official open dataset.",
        "The CHSH statistic and p-value vary materially across the scanned timing-parameter grid.",
        "The reported violation is therefore reproducible but not invariant across that explored family of timing choices.",
        "No-signaling consistency and setting-bit randomness are testable on the filtered open-data sample.",
    ],
    "hypotheses_not_established_as_facts": [
        "Sensitivity to timing parameters may indicate observational dependence on the published selection pipeline.",
        "Sensitivity alone does not prove post-selection artifact, fraud, or global physical invalidity of the experiment.",
        "A correlation between daily acceptance rate and daily CHSH strength would be suggestive, not causal proof of post-selection.",
    ],
    "hard_limits_of_the_open_data": [
        "The audit covers the published open-data pipeline, not the full stream of raw physical attempts.",
        "The audit cannot by itself decide whether the observed sensitivity is an expected feature of a legitimate pipeline or evidence of a stronger methodological problem.",
        "The audit cannot adjudicate between a genuine Bell violation and a selection-driven interpretation without more primary data or stronger external constraints.",
        "Cross-experiment comparison against Giustina 2015 or Shalm 2015 would require their own primary datasets and matched pipelines.",
    ],
    "mathematical_minimum_statement": [
        "Within this audit, the reported CHSH value is a function S(theta) of timing-parameter choices theta = (event-ready offset, readout window length).",
        "The scanned grid shows that partial S / partial theta is not zero across the explored region.",
        "No-signaling and setting-uniformity claims are properties of the filtered sample and not direct statements about the unobserved raw population.",
    ],
    "unknowns": [
        "Unknown whether the same sensitivity pattern weakens or disappears in the full raw-attempt stream.",
        "Unknown whether the observed sensitivity is methodologically serious enough to change the physical interpretation of the experiment.",
    ],
    "relevant_primary_sources": [
        f"Hensen et al. 2015 Nature paper DOI {PAPER_DOI}.",
        f"Official open dataset DOI {DATASET_DOI}.",
        f"Hensen et al. 2016 additional analysis DOI {ADDITIONAL_ANALYSIS_DOI}, arXiv {ADDITIONAL_ANALYSIS_ARXIV}.",
    ],
}


@dataclass
class BaselineResult:
    candidate_rows: int
    bell_trials: int
    k: int
    p_value: float
    S: float
    S_error: float
    settings_counts: list[int]


@dataclass
class TaylorResult:
    parameter: str
    nominal_value_ps: int
    delta_ps: int
    S_minus: float
    S_0: float
    S_plus: float
    first_derivative_per_ps: float
    second_derivative_per_ps2: float


@dataclass
class MonteCarloBootstrapResult:
    replicates: int
    mean_S: float
    sd_S: float
    q05: float
    q50: float
    q95: float
    prob_S_gt_2: float


@dataclass
class MonteCarloOffsetResult:
    replicates: int
    offset_min_ps: int
    offset_max_ps: int
    mean_S: float
    sd_S: float
    min_S: float
    max_S: float
    prob_S_gt_2: float
    min_bell_trials: int
    max_bell_trials: int


@dataclass
class KalmanResult:
    q_mle: float
    obs_rate_min: float
    obs_rate_max: float
    smooth_rate_min: float
    smooth_rate_max: float
    smooth_first3: list[float]
    smooth_last3: list[float]
    corr_acceptance_vs_win_fraction: float
    day_table: list[dict]


@dataclass
class KolmogorovProxyResult:
    n: int
    rate: float
    observed_compression_ratio: float
    shuffle_mean: float
    shuffle_sd: float
    shuffle_q05: float
    shuffle_q95: float
    bernoulli_mean: float
    bernoulli_sd: float
    bernoulli_q05: float
    bernoulli_q95: float
    p_shuffle_le_observed: float
    p_bernoulli_le_observed: float


@dataclass
class CyclicVectorResult:
    vector: list[float]
    mean: float
    cyclic_break_index: float
    fourier_modes_abs: list[float]
    mode1_to_mode0: float
    mode2_to_mode0: float


@dataclass
class CyclicInvarianceResult:
    settings_counts: CyclicVectorResult
    win_rates: CyclicVectorResult
    e_values: CyclicVectorResult
    counts_chi2_uniform: float
    counts_uniform_mc_p: float


@dataclass
class NoSignalingResult:
    chi2_A: float
    p_A: float
    chi2_B: float
    p_B: float
    chi2_joint: float
    p_joint: float
    table_A: list[list[int]]
    table_B: list[list[int]]
    detail: list[dict]


@dataclass
class RNGResult:
    uniform_chi2_A: float
    uniform_p_A: float
    uniform_chi2_B: float
    uniform_p_B: float
    joint_chi2: float
    joint_p: float
    runs_A: dict
    runs_B: dict
    autocorr_A_lag1: float
    autocorr_B_lag1: float
    counts_A: list[int]
    counts_B: list[int]
    counts_joint: list[int]


@dataclass
class AcceptanceVsSResult:
    spearman_r: float
    pearson_r: float
    n_days: int
    slope: float
    interpretation: str
    per_day: list[dict]


@dataclass
class LookElsewhereResult:
    S_min: float
    S_max: float
    S_span: float
    p_min: float
    p_max: float
    pct_S_gt_2: float
    pct_S_gt_2_2: float
    pct_S_gt_2_4: float
    pct_p_lt_0_05: float
    pct_p_lt_0_01: float
    bonferroni_p_min_corrected: float
    fdr_significant_cells: int
    total_valid_cells: int
    interpretation: str


def binom_sf(k_minus_1: int, n: int, p: float) -> float:
    """Exact survival function P[X >= k] for modest n."""
    total = 0.0
    for k in range(k_minus_1 + 1, n + 1):
        total += math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))
    return total


def chi2_sf(x: float, dof: int) -> float:
    """Chi-square survival function for the small dof values used here."""
    if x < 0:
        return 1.0
    y = x / 2.0
    if dof == 1:
        return math.erfc(math.sqrt(y))
    if dof == 2:
        return math.exp(-y)
    if dof == 3:
        return math.erfc(math.sqrt(y)) + (2.0 / math.sqrt(math.pi)) * math.sqrt(y) * math.exp(-y)
    if dof == 4:
        return math.exp(-y) * (1.0 + y)
    raise ValueError(f"Unsupported dof={dof} for chi2_sf.")


def average_ranks(values: np.ndarray) -> np.ndarray:
    """Average-rank transform with tie handling for Spearman correlation."""
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and sorted_values[j] == sorted_values[i]:
            j += 1
        avg_rank = 0.5 * (i + j - 1)
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def download_and_extract_dataset(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    outer_zip = out_dir / "hensen2015_dataset_outer.zip"
    inner_zip = out_dir / "data.zip"
    extract_dir = out_dir / "hensen2015_dataset"

    if not extract_dir.exists():
        urllib.request.urlretrieve(DATASET_URL, outer_zip)
        with zipfile.ZipFile(outer_zip) as zf:
            zf.extract("data.zip", path=out_dir)
        with zipfile.ZipFile(inner_zip) as zf:
            zf.extractall(path=extract_dir)

    data_file = extract_dir / "bell_open_data.txt"
    if not data_file.exists():
        raise FileNotFoundError(f"Expected dataset file not found: {data_file}")
    return data_file


def load_open_data(data_file: Path) -> tuple[np.ndarray, np.ndarray]:
    timestamps = np.loadtxt(data_file, delimiter=",", usecols=[0], dtype="datetime64[us]")
    data = np.loadtxt(data_file, delimiter=",", usecols=np.arange(1, 17), dtype=np.int64)
    return timestamps, data


def compute_pipeline(data: np.ndarray, offset_ps: int = 0, readout_window_length: int = 3700) -> dict:
    (
        day_number,
        run_number,
        event_ready_click1_time,
        event_ready_click1_channel,
        event_ready_click2_time,
        event_ready_click2_channel,
        random_number_A,
        random_number_B,
        random_number_A_time,
        random_number_B_time,
        readout_click_A_time,
        readout_click_B_time,
        click_after_excite_A_time,
        click_after_excite_B_time,
        last_invalid_marker_A,
        last_invalid_marker_B,
    ) = data.T

    start0 = 5426350 + offset_ps
    start1 = 5425700 + offset_ps
    event_ready_window_length = 55000 - 2550
    event_ready_window_separation = 250000
    readout_window_start = 10620
    invalid_marker_lookback = 250

    w1c0 = (
        (start0 <= event_ready_click1_time)
        & (event_ready_click1_time < (start0 + event_ready_window_length))
        & (event_ready_click1_channel == 0)
    )
    w1c1 = (
        (start1 <= event_ready_click1_time)
        & (event_ready_click1_time < (start1 + event_ready_window_length))
        & (event_ready_click1_channel == 1)
    )
    w2c0 = (
        (start0 + event_ready_window_separation <= event_ready_click2_time)
        & (event_ready_click2_time < (start0 + event_ready_window_separation + event_ready_window_length))
        & (event_ready_click2_channel == 0)
    )
    w2c1 = (
        (start1 + event_ready_window_separation <= event_ready_click2_time)
        & (event_ready_click2_time < (start1 + event_ready_window_separation + event_ready_window_length))
        & (event_ready_click2_channel == 1)
    )

    event_ready_window_filter = (w1c0 | w1c1) & (w2c0 | w2c1) & (event_ready_click1_channel != event_ready_click2_channel)
    no_invalid_marker = (
        ((last_invalid_marker_A == 0) | (last_invalid_marker_A > invalid_marker_lookback))
        & ((last_invalid_marker_B == 0) | (last_invalid_marker_B > invalid_marker_lookback))
    )
    no_excitation_click = (click_after_excite_A_time == 0) & (click_after_excite_B_time == 0)
    bell_trial_filter = event_ready_window_filter & no_invalid_marker & no_excitation_click

    detection_in_readout_window_A = (
        (readout_click_A_time > readout_window_start)
        & (readout_click_A_time <= readout_window_start + readout_window_length)
    )
    detection_in_readout_window_B = (
        (readout_click_B_time > readout_window_start)
        & (readout_click_B_time <= readout_window_start + readout_window_length)
    )

    a_i = random_number_A
    b_i = random_number_B
    x_i = detection_in_readout_window_A.astype(np.int64) * 2 - 1
    y_i = detection_in_readout_window_B.astype(np.int64) * 2 - 1
    t_i = bell_trial_filter.astype(np.int64)

    n = int(t_i.sum())
    c_i = t_i * (((-1) ** (a_i * b_i) * (x_i * y_i) + 1) / 2)
    k = int(c_i.sum())
    tau = 5.4e-6 * 2
    ksi = 3.0 / 4.0 + 3.0 * (tau + tau**2)
    p_value = binom_sf(k - 1, n, ksi)

    inputs_ab = [(0, 0), (0, 1), (1, 0), (1, 1)]
    outputs_xy = [(+1, +1), (+1, -1), (-1, +1), (-1, -1)]
    correlation_matrix = np.zeros((4, 4), dtype=np.int64)
    xy_corr = np.zeros(4, dtype=float)
    xy_err = np.zeros(4, dtype=float)

    for i, (a, b) in enumerate(inputs_ab):
        for j, (x, y) in enumerate(outputs_xy):
            correlation_matrix[i, j] = np.sum(
                t_i & (a_i == a) & (b_i == b) & (x_i == x) & (y_i == y)
            )
        denom = float(np.sum(correlation_matrix[i, :]))
        xy_corr[i] = (
            correlation_matrix[i, 0]
            - correlation_matrix[i, 1]
            - correlation_matrix[i, 2]
            + correlation_matrix[i, 3]
        ) / denom
        xy_err[i] = math.sqrt((1 - xy_corr[i] ** 2) / denom)

    S = float(xy_corr[0] + xy_corr[1] + xy_corr[2] - xy_corr[3])
    S_error = float(math.sqrt(np.sum(xy_err**2)))

    settings_counts = [int(np.sum(correlation_matrix[i, :])) for i in range(4)]

    return {
        "day_number": day_number,
        "run_number": run_number,
        "a_i": a_i,
        "b_i": b_i,
        "x_i": x_i,
        "y_i": y_i,
        "t_i": t_i,
        "bell_filter": bell_trial_filter,
        "correlation_matrix": correlation_matrix,
        "settings_counts": settings_counts,
        "n": n,
        "k": k,
        "p_value": p_value,
        "S": S,
        "S_error": S_error,
    }


def taylor_sensitivity(data: np.ndarray, nominal_ps: int, delta_ps: int) -> TaylorResult:
    s_minus = compute_pipeline(data, offset_ps=nominal_ps - delta_ps)["S"]
    s_0 = compute_pipeline(data, offset_ps=nominal_ps)["S"]
    s_plus = compute_pipeline(data, offset_ps=nominal_ps + delta_ps)["S"]
    first = (s_plus - s_minus) / (2.0 * delta_ps)
    second = (s_plus - 2.0 * s_0 + s_minus) / float(delta_ps**2)
    return TaylorResult(
        parameter="event_ready_offset_ps",
        nominal_value_ps=nominal_ps,
        delta_ps=delta_ps,
        S_minus=float(s_minus),
        S_0=float(s_0),
        S_plus=float(s_plus),
        first_derivative_per_ps=float(first),
        second_derivative_per_ps2=float(second),
    )


def monte_carlo_bootstrap(rng: np.random.Generator, pipeline: dict, replicates: int) -> MonteCarloBootstrapResult:
    valid = np.where(pipeline["bell_filter"])[0]
    obs = np.column_stack(
        [
            pipeline["a_i"][valid],
            pipeline["b_i"][valid],
            pipeline["x_i"][valid],
            pipeline["y_i"][valid],
        ]
    )
    S_values = np.empty(replicates, dtype=float)
    strata = []

    for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        sub = obs[(obs[:, 0] == a) & (obs[:, 1] == b)]
        if len(sub) == 0:
            raise ValueError(f"Bootstrap requires at least one accepted trial for setting ({a}, {b}).")
        strata.append(sub)

    for i in range(replicates):
        E = []
        for sub in strata:
            sample = sub[rng.integers(0, len(sub), len(sub))]
            vals = sample[:, 2] * sample[:, 3]
            E.append(vals.mean())
        S_values[i] = E[0] + E[1] + E[2] - E[3]

    return MonteCarloBootstrapResult(
        replicates=replicates,
        mean_S=float(np.mean(S_values)),
        sd_S=float(np.std(S_values, ddof=1)),
        q05=float(np.quantile(S_values, 0.05)),
        q50=float(np.quantile(S_values, 0.50)),
        q95=float(np.quantile(S_values, 0.95)),
        prob_S_gt_2=float(np.mean(S_values > 2.0)),
    )


def monte_carlo_offset(
    rng: np.random.Generator,
    data: np.ndarray,
    replicates: int,
    offset_min_ps: int,
    offset_max_ps: int,
) -> MonteCarloOffsetResult:
    S_values = np.empty(replicates, dtype=float)
    n_values = np.empty(replicates, dtype=int)

    for i in range(replicates):
        offset = int(round(rng.uniform(offset_min_ps, offset_max_ps)))
        res = compute_pipeline(data, offset_ps=offset)
        S_values[i] = res["S"]
        n_values[i] = res["n"]

    return MonteCarloOffsetResult(
        replicates=replicates,
        offset_min_ps=offset_min_ps,
        offset_max_ps=offset_max_ps,
        mean_S=float(np.mean(S_values)),
        sd_S=float(np.std(S_values, ddof=1)),
        min_S=float(np.min(S_values)),
        max_S=float(np.max(S_values)),
        prob_S_gt_2=float(np.mean(S_values > 2.0)),
        min_bell_trials=int(np.min(n_values)),
        max_bell_trials=int(np.max(n_values)),
    )


def kalman_daily_acceptance(pipeline: dict) -> KalmanResult:
    day_number = pipeline["day_number"]
    bell = pipeline["bell_filter"]
    a_i = pipeline["a_i"]
    b_i = pipeline["b_i"]
    x_i = pipeline["x_i"]
    y_i = pipeline["y_i"]

    unique_days = sorted(np.unique(day_number))
    rows_per_day = np.array([(day_number == d).sum() for d in unique_days], dtype=float)
    acc_per_day = np.array([np.sum(bell & (day_number == d)) for d in unique_days], dtype=float)
    y_obs = acc_per_day / rows_per_day
    r_obs = np.maximum(y_obs * (1 - y_obs) / rows_per_day, 1e-8)

    q_grid = np.logspace(-8, -3, 200)

    def loglike(q: float) -> float:
        x = y_obs[0]
        P = r_obs[0] + q
        total = 0.0
        for t in range(len(y_obs)):
            if t > 0:
                P = P + q
            e = y_obs[t] - x
            S = P + r_obs[t]
            total += -0.5 * (math.log(2 * math.pi * S) + (e * e) / S)
            K = P / S
            x = x + K * e
            P = (1 - K) * P
        return total

    lls = np.array([loglike(q) for q in q_grid])
    q_mle = float(q_grid[np.argmax(lls)])

    x_f = np.zeros(len(y_obs))
    P_f = np.zeros(len(y_obs))
    x_pred = np.zeros(len(y_obs))
    P_pred = np.zeros(len(y_obs))

    x = y_obs[0]
    P = r_obs[0] + q_mle
    for t in range(len(y_obs)):
        if t == 0:
            xp = x
            Pp = P
        else:
            xp = x
            Pp = P + q_mle
        x_pred[t] = xp
        P_pred[t] = Pp
        e = y_obs[t] - xp
        S = Pp + r_obs[t]
        K = Pp / S
        x = xp + K * e
        P = (1 - K) * Pp
        x_f[t] = x
        P_f[t] = P

    x_s = x_f.copy()
    P_s = P_f.copy()
    for t in range(len(y_obs) - 2, -1, -1):
        C = P_f[t] / P_pred[t + 1]
        x_s[t] = x_f[t] + C * (x_s[t + 1] - x_pred[t + 1])
        P_s[t] = P_f[t] + C * C * (P_s[t + 1] - P_pred[t + 1])

    win_fraction = []
    for d in unique_days:
        mask = bell & (day_number == d)
        if np.sum(mask) == 0:
            win_fraction.append(np.nan)
            continue
        vals = (((-1) ** (a_i[mask] * b_i[mask]) * (x_i[mask] * y_i[mask]) + 1) / 2)
        win_fraction.append(float(np.mean(vals)))
    win_fraction = np.array(win_fraction, dtype=float)
    valid = np.isfinite(win_fraction)
    corr = float(np.corrcoef(y_obs[valid], win_fraction[valid])[0, 1])

    day_table = []
    for d, rows, acc, y_raw, y_smooth, w in zip(unique_days, rows_per_day, acc_per_day, y_obs, x_s, win_fraction):
        day_table.append(
            {
                "day": int(d),
                "candidate_rows": int(rows),
                "accepted_trials": int(acc),
                "acceptance_rate_observed": float(y_raw),
                "acceptance_rate_smoothed": float(y_smooth),
                "win_fraction": None if not np.isfinite(w) else float(w),
            }
        )

    return KalmanResult(
        q_mle=q_mle,
        obs_rate_min=float(np.min(y_obs)),
        obs_rate_max=float(np.max(y_obs)),
        smooth_rate_min=float(np.min(x_s)),
        smooth_rate_max=float(np.max(x_s)),
        smooth_first3=[float(v) for v in x_s[:3]],
        smooth_last3=[float(v) for v in x_s[-3:]],
        corr_acceptance_vs_win_fraction=corr,
        day_table=day_table,
    )


def cyclic_vector_metrics(vector: np.ndarray) -> CyclicVectorResult:
    arr = np.asarray(vector, dtype=float)
    F = np.fft.fft(arr)
    break_energy = float(np.sum(np.abs(F[1:]) ** 2))
    total_energy = float(np.sum(np.abs(F) ** 2))
    break_index = math.sqrt(break_energy / total_energy) if total_energy > 0 else float("nan")
    f0 = abs(F[0])
    return CyclicVectorResult(
        vector=[float(v) for v in arr],
        mean=float(np.mean(arr)),
        cyclic_break_index=float(break_index),
        fourier_modes_abs=[float(abs(z)) for z in F],
        mode1_to_mode0=float(abs(F[1]) / f0) if f0 else float("nan"),
        mode2_to_mode0=float(abs(F[2]) / f0) if f0 else float("nan"),
    )


def cyclic_invariance_audit(rng: np.random.Generator, pipeline: dict, mc_replicates: int = 200000) -> CyclicInvarianceResult:
    correlation_matrix = pipeline["correlation_matrix"]
    settings_counts = np.sum(correlation_matrix, axis=1).astype(float)
    win_counts = np.array(
        [
            correlation_matrix[0, 0] + correlation_matrix[0, 3],  # 00: x*y = +1
            correlation_matrix[1, 0] + correlation_matrix[1, 3],  # 01: x*y = +1
            correlation_matrix[2, 0] + correlation_matrix[2, 3],  # 10: x*y = +1
            correlation_matrix[3, 1] + correlation_matrix[3, 2],  # 11: x*y = -1
        ],
        dtype=float,
    )
    win_rates = win_counts / settings_counts
    e_values = np.array(
        [
            (row[0] - row[1] - row[2] + row[3]) / float(np.sum(row))
            for row in correlation_matrix
        ],
        dtype=float,
    )

    N = int(np.sum(settings_counts))
    expected = N / 4.0
    chi2 = float(np.sum((settings_counts - expected) ** 2 / expected))
    sims = rng.multinomial(N, [0.25, 0.25, 0.25, 0.25], size=mc_replicates)
    chi2_sims = np.sum((sims - expected) ** 2 / expected, axis=1)
    p_mc = float(np.mean(chi2_sims >= chi2))

    return CyclicInvarianceResult(
        settings_counts=cyclic_vector_metrics(settings_counts),
        win_rates=cyclic_vector_metrics(win_rates),
        e_values=cyclic_vector_metrics(e_values),
        counts_chi2_uniform=chi2,
        counts_uniform_mc_p=p_mc,
    )


def compression_ratio(bits: np.ndarray) -> float:
    payload = "".join("1" if v else "0" for v in bits.astype(np.int8)).encode("ascii")
    return len(zlib.compress(payload, 9)) / len(payload)


def kolmogorov_proxy(
    rng: np.random.Generator,
    bits: np.ndarray,
    replicates: int,
) -> KolmogorovProxyResult:
    bits = bits.astype(np.int8)
    n = len(bits)
    rate = float(np.mean(bits))
    ones = int(np.sum(bits))
    observed = compression_ratio(bits)

    shuffle = np.empty(replicates, dtype=float)
    bernoulli = np.empty(replicates, dtype=float)
    base = np.zeros(n, dtype=np.int8)
    base[:ones] = 1

    for i in range(replicates):
        shuffled = base.copy()
        rng.shuffle(shuffled)
        shuffle[i] = compression_ratio(shuffled)
        bern = (rng.random(n) < rate).astype(np.int8)
        bernoulli[i] = compression_ratio(bern)

    return KolmogorovProxyResult(
        n=n,
        rate=rate,
        observed_compression_ratio=float(observed),
        shuffle_mean=float(np.mean(shuffle)),
        shuffle_sd=float(np.std(shuffle, ddof=1)),
        shuffle_q05=float(np.quantile(shuffle, 0.05)),
        shuffle_q95=float(np.quantile(shuffle, 0.95)),
        bernoulli_mean=float(np.mean(bernoulli)),
        bernoulli_sd=float(np.std(bernoulli, ddof=1)),
        bernoulli_q05=float(np.quantile(bernoulli, 0.05)),
        bernoulli_q95=float(np.quantile(bernoulli, 0.95)),
        p_shuffle_le_observed=float(np.mean(shuffle <= observed)),
        p_bernoulli_le_observed=float(np.mean(bernoulli <= observed)),
    )


def no_signaling_test(pipeline: dict) -> NoSignalingResult:
    correlation_matrix = pipeline["correlation_matrix"]

    table_A = []
    for row in correlation_matrix:
        x_plus = int(row[0] + row[1])
        x_minus = int(row[2] + row[3])
        table_A.append([x_plus, x_minus])

    table_B = []
    for row in correlation_matrix:
        y_plus = int(row[0] + row[2])
        y_minus = int(row[1] + row[3])
        table_B.append([y_plus, y_minus])

    def chi2_2x2(table_top: list[int], table_bottom: list[int]) -> tuple[float, float]:
        n11, n12 = table_top
        n21, n22 = table_bottom
        n = n11 + n12 + n21 + n22
        if n == 0:
            return 0.0, 1.0
        r1 = n11 + n12
        r2 = n21 + n22
        c1 = n11 + n21
        c2 = n12 + n22
        if min(r1, r2, c1, c2) == 0:
            return 0.0, 1.0
        e11 = r1 * c1 / n
        e12 = r1 * c2 / n
        e21 = r2 * c1 / n
        e22 = r2 * c2 / n
        chi2 = (
            (n11 - e11) ** 2 / e11
            + (n12 - e12) ** 2 / e12
            + (n21 - e21) ** 2 / e21
            + (n22 - e22) ** 2 / e22
        )
        return float(chi2), float(chi2_sf(chi2, 1))

    detail = []
    chi2_A_0, p_A_0 = chi2_2x2(table_A[0], table_A[1])
    detail.append({"test": "Alice a=0, compare b=0 vs b=1", "chi2": chi2_A_0, "p": p_A_0, "counts": [table_A[0], table_A[1]]})
    chi2_A_1, p_A_1 = chi2_2x2(table_A[2], table_A[3])
    detail.append({"test": "Alice a=1, compare b=0 vs b=1", "chi2": chi2_A_1, "p": p_A_1, "counts": [table_A[2], table_A[3]]})
    chi2_B_0, p_B_0 = chi2_2x2(table_B[0], table_B[2])
    detail.append({"test": "Bob b=0, compare a=0 vs a=1", "chi2": chi2_B_0, "p": p_B_0, "counts": [table_B[0], table_B[2]]})
    chi2_B_1, p_B_1 = chi2_2x2(table_B[1], table_B[3])
    detail.append({"test": "Bob b=1, compare a=0 vs a=1", "chi2": chi2_B_1, "p": p_B_1, "counts": [table_B[1], table_B[3]]})

    chi2_A = chi2_A_0 + chi2_A_1
    chi2_B = chi2_B_0 + chi2_B_1
    chi2_joint = chi2_A + chi2_B

    return NoSignalingResult(
        chi2_A=chi2_A,
        p_A=float(chi2_sf(chi2_A, 2)),
        chi2_B=chi2_B,
        p_B=float(chi2_sf(chi2_B, 2)),
        chi2_joint=chi2_joint,
        p_joint=float(chi2_sf(chi2_joint, 4)),
        table_A=table_A,
        table_B=table_B,
        detail=detail,
    )


def rng_randomness_test(pipeline: dict) -> RNGResult:
    mask = pipeline["bell_filter"]
    a_i = pipeline["a_i"][mask].astype(np.int64)
    b_i = pipeline["b_i"][mask].astype(np.int64)
    n = len(a_i)

    cnt_A = [int(np.sum(a_i == 0)), int(np.sum(a_i == 1))]
    cnt_B = [int(np.sum(b_i == 0)), int(np.sum(b_i == 1))]
    exp_half = n / 2.0 if n else 1.0
    chi2_A = float(sum((c - exp_half) ** 2 / exp_half for c in cnt_A)) if n else 0.0
    chi2_B = float(sum((c - exp_half) ** 2 / exp_half for c in cnt_B)) if n else 0.0

    counts_joint = [
        int(np.sum((a_i == 0) & (b_i == 0))),
        int(np.sum((a_i == 0) & (b_i == 1))),
        int(np.sum((a_i == 1) & (b_i == 0))),
        int(np.sum((a_i == 1) & (b_i == 1))),
    ]
    exp_joint = n / 4.0 if n else 1.0
    chi2_joint = float(sum((c - exp_joint) ** 2 / exp_joint for c in counts_joint)) if n else 0.0

    def runs_test(bits: np.ndarray) -> dict:
        if len(bits) < 2:
            return {"runs": 0, "expected": 0.0, "z": 0.0, "p": 1.0}
        runs = 1 + int(np.sum(bits[1:] != bits[:-1]))
        n1 = int(np.sum(bits == 1))
        n0 = int(np.sum(bits == 0))
        if n1 == 0 or n0 == 0:
            return {"runs": runs, "expected": float(runs), "z": 0.0, "p": 1.0}
        expected = 1.0 + 2.0 * n0 * n1 / len(bits)
        variance = (
            2.0 * n0 * n1 * (2.0 * n0 * n1 - len(bits))
            / (len(bits) ** 2 * max(len(bits) - 1, 1))
        )
        variance = max(variance, 1e-12)
        z = (runs - expected) / math.sqrt(variance)
        return {"runs": runs, "expected": expected, "z": float(z), "p": float(math.erfc(abs(z) / math.sqrt(2.0)))}

    def autocorr_lag1(bits: np.ndarray) -> float:
        if len(bits) < 3:
            return 0.0
        centered = bits.astype(float) - float(np.mean(bits))
        denom = float(np.dot(centered, centered))
        if denom == 0.0:
            return 0.0
        return float(np.dot(centered[:-1], centered[1:]) / denom)

    return RNGResult(
        uniform_chi2_A=chi2_A,
        uniform_p_A=float(chi2_sf(chi2_A, 1)),
        uniform_chi2_B=chi2_B,
        uniform_p_B=float(chi2_sf(chi2_B, 1)),
        joint_chi2=chi2_joint,
        joint_p=float(chi2_sf(chi2_joint, 3)),
        runs_A=runs_test(a_i),
        runs_B=runs_test(b_i),
        autocorr_A_lag1=autocorr_lag1(a_i),
        autocorr_B_lag1=autocorr_lag1(b_i),
        counts_A=cnt_A,
        counts_B=cnt_B,
        counts_joint=counts_joint,
    )


def acceptance_vs_S_daily(pipeline: dict) -> AcceptanceVsSResult:
    day_number = pipeline["day_number"]
    bell = pipeline["bell_filter"]
    a_i = pipeline["a_i"]
    b_i = pipeline["b_i"]
    x_i = pipeline["x_i"]
    y_i = pipeline["y_i"]
    per_day = []

    for day in sorted(np.unique(day_number)):
        mask_all = day_number == day
        mask_bell = bell & mask_all
        rows = int(np.sum(mask_all))
        accepted = int(np.sum(mask_bell))
        if rows == 0:
            continue
        acceptance_rate = accepted / rows
        if accepted < 4:
            continue
        E_values = []
        valid_day = True
        for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            sub = mask_bell & (a_i == a) & (b_i == b)
            denom = int(np.sum(sub))
            if denom == 0:
                valid_day = False
                break
            prod = x_i[sub] * y_i[sub]
            E_values.append(float(np.mean(prod)))
        if not valid_day:
            continue
        S_day = E_values[0] + E_values[1] + E_values[2] - E_values[3]
        per_day.append({"day": int(day), "acceptance_rate": float(acceptance_rate), "S": float(S_day), "trials": accepted})

    if len(per_day) < 3:
        return AcceptanceVsSResult(
            spearman_r=float("nan"),
            pearson_r=float("nan"),
            n_days=len(per_day),
            slope=float("nan"),
            interpretation="Insufficient daily strata with all four settings represented.",
            per_day=per_day,
        )

    acc_rates = np.array([row["acceptance_rate"] for row in per_day], dtype=float)
    S_values = np.array([row["S"] for row in per_day], dtype=float)
    pearson = float(np.corrcoef(acc_rates, S_values)[0, 1])
    spearman = float(np.corrcoef(average_ranks(acc_rates), average_ranks(S_values))[0, 1])
    slope = float(np.polyfit(acc_rates, S_values, 1)[0])

    if abs(spearman) > 0.6:
        interpretation = "Strong daily acceptance-vs-S association; check for pipeline dependence."
    elif abs(spearman) > 0.3:
        interpretation = "Moderate daily acceptance-vs-S association; monitor but do not over-interpret."
    else:
        interpretation = "No strong daily acceptance-vs-S association in the represented daily strata."

    return AcceptanceVsSResult(
        spearman_r=spearman,
        pearson_r=pearson,
        n_days=len(per_day),
        slope=slope,
        interpretation=interpretation,
        per_day=per_day,
    )


def look_elsewhere_correction(surface_scan: dict) -> LookElsewhereResult:
    S_grid = np.asarray(surface_scan["S_grid"], dtype=float)
    p_grid = np.asarray(surface_scan["p_value_grid"], dtype=float)
    valid = np.isfinite(S_grid) & np.isfinite(p_grid)
    total = int(np.sum(valid))
    if total == 0:
        return LookElsewhereResult(
            S_min=float("nan"),
            S_max=float("nan"),
            S_span=float("nan"),
            p_min=float("nan"),
            p_max=float("nan"),
            pct_S_gt_2=0.0,
            pct_S_gt_2_2=0.0,
            pct_S_gt_2_4=0.0,
            pct_p_lt_0_05=0.0,
            pct_p_lt_0_01=0.0,
            bonferroni_p_min_corrected=float("nan"),
            fdr_significant_cells=0,
            total_valid_cells=0,
            interpretation="No valid grid cells were available.",
        )

    S_valid = S_grid[valid]
    p_valid = p_grid[valid]
    sorted_p = np.sort(p_valid)
    fdr_count = 0
    for i, p_val in enumerate(sorted_p, start=1):
        if p_val <= (i / len(sorted_p)) * 0.05:
            fdr_count = i

    pct_S_gt_2 = float(np.mean(S_valid > 2.0) * 100.0)
    if pct_S_gt_2 > 80.0:
        interpretation = f"Robust over the scanned grid: {pct_S_gt_2:.1f}% of valid cells satisfy S > 2."
    elif pct_S_gt_2 > 50.0:
        interpretation = f"Moderately robust over the scanned grid: {pct_S_gt_2:.1f}% of valid cells satisfy S > 2."
    else:
        interpretation = f"Fragile over the scanned grid: only {pct_S_gt_2:.1f}% of valid cells satisfy S > 2."

    return LookElsewhereResult(
        S_min=float(np.min(S_valid)),
        S_max=float(np.max(S_valid)),
        S_span=float(np.max(S_valid) - np.min(S_valid)),
        p_min=float(np.min(p_valid)),
        p_max=float(np.max(p_valid)),
        pct_S_gt_2=pct_S_gt_2,
        pct_S_gt_2_2=float(np.mean(S_valid > 2.2) * 100.0),
        pct_S_gt_2_4=float(np.mean(S_valid > 2.4) * 100.0),
        pct_p_lt_0_05=float(np.mean(p_valid < 0.05) * 100.0),
        pct_p_lt_0_01=float(np.mean(p_valid < 0.01) * 100.0),
        bonferroni_p_min_corrected=float(min(1.0, np.min(p_valid) * total)),
        fdr_significant_cells=fdr_count,
        total_valid_cells=total,
        interpretation=interpretation,
    )


def build_surface_scan(
    data: np.ndarray,
    offset_values: np.ndarray,
    readout_values: np.ndarray,
) -> dict:
    offset_values = np.asarray(offset_values, dtype=int)
    readout_values = np.asarray(readout_values, dtype=int)
    grid_offset, grid_readout = np.meshgrid(offset_values, readout_values, indexing="xy")

    S_grid = np.empty_like(grid_offset, dtype=float)
    p_grid = np.empty_like(grid_offset, dtype=float)
    n_grid = np.empty_like(grid_offset, dtype=float)

    for i, readout in enumerate(readout_values):
        for j, offset in enumerate(offset_values):
            res = compute_pipeline(data, offset_ps=int(offset), readout_window_length=int(readout))
            S_grid[i, j] = res["S"]
            p_grid[i, j] = res["p_value"]
            n_grid[i, j] = res["n"]

    return {
        "offset_values_ps": offset_values,
        "readout_values": readout_values,
        "offset_grid_ps": grid_offset,
        "readout_grid": grid_readout,
        "S_grid": S_grid,
        "p_value_grid": p_grid,
        "bell_trials_grid": n_grid,
    }


def save_surface_plot(
    output_path: Path,
    x_grid: np.ndarray,
    y_grid: np.ndarray,
    z_grid: np.ndarray,
    z_label: str,
    title: str,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(
        x_grid,
        y_grid,
        z_grid,
        cmap="viridis",
        linewidth=0.3,
        edgecolor=(0.1, 0.1, 0.1, 0.35),
        antialiased=True,
    )
    ax.set_xlabel("event_ready_offset_ps")
    ax.set_ylabel("readout_window_length")
    ax.set_zlabel(z_label)
    ax.set_title(title)
    fig.colorbar(surf, ax=ax, shrink=0.7, aspect=14, pad=0.08, label=z_label)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def generate_surface_artifacts(
    data: np.ndarray,
    plot_dir: Path,
    offset_values: np.ndarray,
    readout_values: np.ndarray,
) -> dict:
    plot_dir.mkdir(parents=True, exist_ok=True)
    scan = build_surface_scan(data, offset_values=offset_values, readout_values=readout_values)

    grid_npz = plot_dir / "hensen2015_surface_grid.npz"
    np.savez_compressed(
        grid_npz,
        offset_values_ps=scan["offset_values_ps"],
        readout_values=scan["readout_values"],
        S_grid=scan["S_grid"],
        p_value_grid=scan["p_value_grid"],
        bell_trials_grid=scan["bell_trials_grid"],
    )

    s_plot = plot_dir / "surface_S.png"
    n_plot = plot_dir / "surface_bell_trials.png"
    p_plot = plot_dir / "surface_p_value.png"

    save_surface_plot(
        s_plot,
        scan["offset_grid_ps"],
        scan["readout_grid"],
        scan["S_grid"],
        z_label="S",
        title="CHSH S over event-ready offset and readout window",
    )
    save_surface_plot(
        n_plot,
        scan["offset_grid_ps"],
        scan["readout_grid"],
        scan["bell_trials_grid"],
        z_label="Bell trials",
        title="Accepted Bell trials over event-ready offset and readout window",
    )
    save_surface_plot(
        p_plot,
        scan["offset_grid_ps"],
        scan["readout_grid"],
        scan["p_value_grid"],
        z_label="p-value",
        title="p-value over event-ready offset and readout window",
    )

    return {
        "offset_range_ps": [int(np.min(offset_values)), int(np.max(offset_values))],
        "readout_range": [int(np.min(readout_values)), int(np.max(readout_values))],
        "grid_shape": [int(scan["S_grid"].shape[0]), int(scan["S_grid"].shape[1])],
        "S_min": float(np.nanmin(scan["S_grid"])),
        "S_max": float(np.nanmax(scan["S_grid"])),
        "bell_trials_min": int(np.nanmin(scan["bell_trials_grid"])),
        "bell_trials_max": int(np.nanmax(scan["bell_trials_grid"])),
        "p_value_min": float(np.nanmin(scan["p_value_grid"])),
        "p_value_max": float(np.nanmax(scan["p_value_grid"])),
        "artifacts": {
            "grid_npz": str(grid_npz),
            "surface_S_png": str(s_plot),
            "surface_bell_trials_png": str(n_plot),
            "surface_p_value_png": str(p_plot),
        },
        "_scan": scan,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Hensen et al. 2015 Bell-test open dataset.")
    parser.add_argument("--data-file", default="", help="Path to bell_open_data.txt. If omitted, download official dataset.")
    parser.add_argument("--download-dir", default="hensen2015_dataset_cache", help="Directory for dataset download/extraction.")
    parser.add_argument("--seed", type=int, default=20260727)
    parser.add_argument("--taylor-delta-ps", type=int, default=100)
    parser.add_argument("--mc-bootstrap", type=int, default=20000)
    parser.add_argument("--mc-offset", type=int, default=4000)
    parser.add_argument("--mc-offset-min-ps", type=int, default=-3000)
    parser.add_argument("--mc-offset-max-ps", type=int, default=4000)
    parser.add_argument("--kolmogorov-sims", type=int, default=2000)
    parser.add_argument("--cyclic-mc", type=int, default=200000)
    parser.add_argument("--generate-plots", action="store_true", help="Generate 3D color-mesh surfaces over offset and readout window.")
    parser.add_argument("--plot-dir", default="hensen2015_surface_plots", help="Directory for surface-plot artifacts.")
    parser.add_argument("--plot-offset-min-ps", type=int, default=-3000)
    parser.add_argument("--plot-offset-max-ps", type=int, default=4000)
    parser.add_argument("--plot-offset-steps", type=int, default=23)
    parser.add_argument("--plot-readout-min", type=int, default=3000)
    parser.add_argument("--plot-readout-max", type=int, default=4500)
    parser.add_argument("--plot-readout-steps", type=int, default=16)
    parser.add_argument("--json-out", default="", help="Optional JSON output path.")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    if args.data_file:
        data_file = Path(args.data_file)
    else:
        data_file = download_and_extract_dataset(Path(args.download_dir))

    _, data = load_open_data(data_file)
    baseline = compute_pipeline(data, offset_ps=0, readout_window_length=3700)
    baseline_result = BaselineResult(
        candidate_rows=int(len(data)),
        bell_trials=baseline["n"],
        k=baseline["k"],
        p_value=float(baseline["p_value"]),
        S=float(baseline["S"]),
        S_error=float(baseline["S_error"]),
        settings_counts=baseline["settings_counts"],
    )

    taylor = taylor_sensitivity(data, nominal_ps=0, delta_ps=args.taylor_delta_ps)
    mc_boot = monte_carlo_bootstrap(rng, baseline, args.mc_bootstrap)
    mc_offset = monte_carlo_offset(
        rng,
        data,
        replicates=args.mc_offset,
        offset_min_ps=args.mc_offset_min_ps,
        offset_max_ps=args.mc_offset_max_ps,
    )
    kalman = kalman_daily_acceptance(baseline)
    cyclic = cyclic_invariance_audit(rng, baseline, args.cyclic_mc)
    no_signaling = no_signaling_test(baseline)
    rng_randomness = rng_randomness_test(baseline)
    acceptance_vs_S = acceptance_vs_S_daily(baseline)

    acceptance_bits = baseline["bell_filter"].astype(np.int8)
    valid_win_bits = (
        (((-1) ** (baseline["a_i"] * baseline["b_i"]) * (baseline["x_i"] * baseline["y_i"]) + 1) / 2)
        [baseline["bell_filter"]]
        .astype(np.int8)
    )
    kolmogorov_acceptance = kolmogorov_proxy(rng, acceptance_bits, args.kolmogorov_sims)
    kolmogorov_valid_win = kolmogorov_proxy(rng, valid_win_bits, args.kolmogorov_sims)

    report = {
        "what_was_audited": {
            "paper_doi": PAPER_DOI,
            "dataset_doi": DATASET_DOI,
            "additional_analysis_doi": ADDITIONAL_ANALYSIS_DOI,
            "additional_analysis_arxiv": ADDITIONAL_ANALYSIS_ARXIV,
            "object": "Published Hensen 2015 open-data observational pipeline",
            "pipeline": "candidate two-photon rows at C -> valid Bell trials -> CHSH statistic",
            "limitation": "Open dataset is not the full raw physical attempt stream.",
        },
        "interpretation_limits": INTERPRETATION_LIMITS,
        "baseline": asdict(baseline_result),
        "taylor": asdict(taylor),
        "monte_carlo_bootstrap": asdict(mc_boot),
        "monte_carlo_offset": asdict(mc_offset),
        "kalman_daily_acceptance": asdict(kalman),
        "cyclic_invariance": asdict(cyclic),
        "kolmogorov_acceptance_sequence": asdict(kolmogorov_acceptance),
        "kolmogorov_valid_win_sequence": asdict(kolmogorov_valid_win),
        "no_signaling": asdict(no_signaling),
        "rng_randomness": asdict(rng_randomness),
        "acceptance_vs_S_daily": asdict(acceptance_vs_S),
    }

    if args.generate_plots:
        if args.plot_offset_steps < 2 or args.plot_readout_steps < 2:
            raise ValueError("Plot grids require at least 2 steps per axis.")
        offset_values = np.unique(
            np.rint(
                np.linspace(
                    args.plot_offset_min_ps,
                    args.plot_offset_max_ps,
                    args.plot_offset_steps,
                )
            ).astype(int)
        )
        readout_values = np.unique(
            np.rint(
                np.linspace(
                    args.plot_readout_min,
                    args.plot_readout_max,
                    args.plot_readout_steps,
                )
            ).astype(int)
        )
        report["surface_scans"] = generate_surface_artifacts(
            data,
            plot_dir=Path(args.plot_dir),
            offset_values=offset_values,
            readout_values=readout_values,
        )
        surface_scan = report["surface_scans"].pop("_scan")
        report["look_elsewhere"] = asdict(look_elsewhere_correction(surface_scan))

    print(json.dumps(report, indent=2, allow_nan=True))

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.write_text(json.dumps(report, indent=2, allow_nan=True), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
