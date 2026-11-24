#!/usr/bin/env python3
"""Reproducible graph audit for the Riemann-zero topology manuscript.

This script is a numerical illustration only. It does not prove RH.
It computes positive critical-line zeros with mpmath, applies the smooth
Riemann-von Mangoldt unfolding, builds null / neutral / Riemann Rips graphs,
reports Laplacian beta_0 across a fixed epsilon grid, and optionally reports
the finite off-critical-line exclusion predicate Z_off(T).
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
from pathlib import Path
try:
    import mpmath as mp
except ModuleNotFoundError:
    mp = None
import numpy as np


POSITIVE_ORDINATE_CONVENTION = "0 < gamma <= T"


def nbar(t: np.ndarray) -> np.ndarray:
    return t/(2*np.pi)*np.log(t/(2*np.pi)) - t/(2*np.pi) + 7/8


def primes_up_to(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = False
    sieve[1] = False
    for n in range(2, int(limit**0.5) + 1):
        if sieve[n]:
            start = n * n
            sieve[start:limit + 1:n] = [False] * (((limit - start) // n) + 1)
    return [n for n, is_prime in enumerate(sieve) if is_prime]


def von_mangoldt_prime_power_terms(limit: int) -> list[dict]:
    terms = []
    for p in primes_up_to(limit):
        power = p
        exponent = 1
        while power <= limit:
            terms.append(
                {
                    "n": int(power),
                    "p": int(p),
                    "m": int(exponent),
                    "Lambda_n": float(math.log(p)),
                }
            )
            if power > limit // p:
                break
            power *= p
            exponent += 1
    return sorted(terms, key=lambda row: (row["n"], row["p"], row["m"]))


def finite_prime_angular_field(
    gamma: np.ndarray,
    terms: list[dict],
) -> np.ndarray:
    values = []
    for t in gamma:
        total = 0.0
        for term in terms:
            n = float(term["n"])
            total += term["Lambda_n"] / math.sqrt(n) * math.cos(float(t) * math.log(n))
        values.append(total)
    return np.asarray(values, dtype=float)


def psi_error_diagnostic(terms: list[dict], limit: int) -> dict:
    """Finite integer-grid diagnostic for the RH-equivalent Chebyshev bound."""
    lambda_at_n: dict[int, float] = {}
    for term in terms:
        n = int(term["n"])
        lambda_at_n[n] = lambda_at_n.get(n, 0.0) + float(term["Lambda_n"])

    epsilons = (0.10, 0.25, 0.50)
    running_psi = 0.0
    maxima = {eps: (-1.0, None) for eps in epsilons}
    tail_start = max(2, math.ceil(limit / 2))
    tail_maxima = {eps: (-1.0, None) for eps in epsilons}
    endpoint_values = {}
    for x in range(2, limit + 1):
        running_psi += lambda_at_n.get(x, 0.0)
        error = abs(running_psi - x)
        for eps in epsilons:
            ratio = error / (x ** (0.5 + eps))
            if ratio > maxima[eps][0]:
                maxima[eps] = (ratio, x)
            if x >= tail_start and ratio > tail_maxima[eps][0]:
                tail_maxima[eps] = (ratio, x)
            if x == limit:
                endpoint_values[eps] = ratio

    return {
        "name": "finite_Chebyshev_error_diagnostic",
        "definition": (
            "B_epsilon(P)=max_{2<=x<=P, x integer} "
            "|psi(x)-x|/x^(1/2+epsilon)"
        ),
        "values": [
            {
                "epsilon": float(eps),
                "B_epsilon_P": float(maxima[eps][0]),
                "argmax_integer_x": int(maxima[eps][1]),
                "ratio_at_P": float(endpoint_values[eps]),
                "tail_interval": [int(tail_start), int(limit)],
                "tail_max_ratio": float(tail_maxima[eps][0]),
                "tail_argmax_integer_x": int(tail_maxima[eps][1]),
            }
            for eps in epsilons
        ],
        "interpretation": (
            "This finite maximum is a diagnostic only. RH requires, for every "
            "epsilon>0, a bound uniform as P tends to infinity."
        ),
    }


def prime_limit_detector_report(
    gamma: np.ndarray,
    prime_limit: int,
    term_preview: int,
) -> dict:
    if prime_limit < 2:
        raise ValueError("prime_limit must be at least 2.")

    primes = primes_up_to(prime_limit)
    terms = von_mangoldt_prime_power_terms(prime_limit)
    raw_prime_sum = int(sum(primes))
    bounded_prime_sum = (
        raw_prime_sum / (1.0 + raw_prime_sum)
        if raw_prime_sum > 0
        else 0.0
    )
    pnt_prime_sum_scale = (
        (prime_limit * prime_limit) / (2.0 * math.log(prime_limit))
        if prime_limit > 2
        else None
    )
    pnt_normalized_prime_sum = (
        raw_prime_sum / pnt_prime_sum_scale
        if pnt_prime_sum_scale
        else None
    )
    theta_value = sum(math.log(p) for p in primes)
    psi_value = sum(term["Lambda_n"] for term in terms)
    angular_values = finite_prime_angular_field(gamma, terms)
    centered = angular_values - float(np.mean(angular_values))
    preview_count = max(0, min(term_preview, len(terms)))

    return {
        "name": "finite_prime_limit_detector",
        "prime_limit_P": int(prime_limit),
        "prime_count_pi_P": int(len(primes)),
        "prime_power_term_count": int(len(terms)),
        "prime_sum_limit_Sigma_pi_P": raw_prime_sum,
        "bounded_prime_sum_limit": float(bounded_prime_sum),
        "bounded_prime_sum_definition": (
            "Sigma_hat_pi(P)=Sigma_pi(P)/(1+Sigma_pi(P)), "
            "Sigma_pi(P)=sum_{p<=P} p"
        ),
        "prime_sum_PNT_scale": (
            None if pnt_prime_sum_scale is None else float(pnt_prime_sum_scale)
        ),
        "prime_sum_normalized_by_PNT_scale": (
            None
            if pnt_normalized_prime_sum is None
            else float(pnt_normalized_prime_sum)
        ),
        "prime_sum_growth_note": (
            "The raw sum Sigma_pi(P)=sum_{p<=P} p grows without bound as "
            "P increases. The bounded value Sigma_hat_pi(P) is included to "
            "keep the finite detector from diverging numerically; it tends to "
            "1 and is not an independent proof channel."
        ),
        "Chebyshev_theta_P": float(theta_value),
        "Chebyshev_psi_P": float(psi_value),
        "canonical_prime_power_sum": (
            "psi(P)=sum_{p^m<=P} log(p)=sum_{n<=P} Lambda(n)"
        ),
        "finite_angular_prime_sum": (
            "A_P(t)=sum_{p^m<=P} log(p)/sqrt(p^m) * cos(t*m*log(p))"
        ),
        "angular_cutoff_note": (
            "A_P uses a sharp unsmoothed cutoff. A proof-level explicit-formula "
            "argument requires an admissible test function or smoothing and all "
            "corresponding archimedean and trivial-zero terms."
        ),
        "angular_field_on_listed_zeros": {
            "mean": float(np.mean(angular_values)),
            "std": float(np.std(angular_values, ddof=1)) if len(angular_values) > 1 else 0.0,
            "min": float(np.min(angular_values)),
            "max": float(np.max(angular_values)),
            "centered_l2_norm": float(np.linalg.norm(centered)),
        },
        "prime_power_terms_preview": terms[:preview_count],
        "Chebyshev_error_diagnostic": psi_error_diagnostic(terms, prime_limit),
        "limit_interpretation": (
            "This is a finite prime cutoff. A RH-level statement would require "
            "a uniform limiting/error theorem as P and x tend to infinity, not "
            "only a detected finite prime sum."
        ),
        "RH_connection": (
            "The standard arithmetic route is through Chebyshev/von Mangoldt "
            "sums and the explicit formula linking primes and nontrivial zeros."
        ),
        "global_RH_proved": False,
    }


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


def beta0_1d_rips(points: np.ndarray, eps: float) -> int:
    sorted_points = np.sort(np.asarray(points, dtype=float))
    if len(sorted_points) == 0:
        return 0
    return int(1 + np.sum(np.diff(sorted_points) > eps))


def summarize_beta0_null(
    values: list[int],
    observed_beta0: int,
    eps: float,
) -> dict:
    arr = np.asarray(values, dtype=float)
    samples = len(arr)
    p_le = (int(np.sum(arr <= observed_beta0)) + 1) / (samples + 1)
    p_ge = (int(np.sum(arr >= observed_beta0)) + 1) / (samples + 1)
    return {
        "epsilon": float(eps),
        "observed_beta0": int(observed_beta0),
        "null_mean_beta0": float(arr.mean()),
        "null_std_beta0": float(arr.std(ddof=1)) if samples > 1 else 0.0,
        "null_q05_beta0": float(np.quantile(arr, 0.05)),
        "null_q50_beta0": float(np.quantile(arr, 0.50)),
        "null_q95_beta0": float(np.quantile(arr, 0.95)),
        "p_null_beta0_le_observed": float(p_le),
        "p_null_beta0_ge_observed": float(p_ge),
    }


def monte_carlo_selector_report(
    unfolded: np.ndarray,
    eps_grid: list[float],
    samples: int,
    seed: int,
) -> dict:
    x = np.sort(np.asarray(unfolded, dtype=float))
    if len(x) < 2:
        raise ValueError("Need at least two unfolded points for Monte Carlo.")

    rng = np.random.default_rng(seed)
    span = float(x[-1] - x[0])
    empirical_gaps = np.diff(x)
    observed_beta0 = [beta0_1d_rips(x, eps) for eps in eps_grid]
    null_values = {
        "uniform_unfolded_range": [[] for _ in eps_grid],
        "bootstrap_rescaled_empirical_gaps": [[] for _ in eps_grid],
    }

    for _ in range(samples):
        uniform_points = np.sort(rng.uniform(x[0], x[-1], size=len(x)))

        sampled_gaps = rng.choice(
            empirical_gaps,
            size=len(empirical_gaps),
            replace=True,
        )
        sampled_total = float(np.sum(sampled_gaps))
        if sampled_total > 0:
            sampled_gaps = sampled_gaps * (span / sampled_total)
        bootstrap_points = x[0] + np.concatenate(
            ([0.0], np.cumsum(sampled_gaps))
        )

        for idx, eps in enumerate(eps_grid):
            null_values["uniform_unfolded_range"][idx].append(
                beta0_1d_rips(uniform_points, eps)
            )
            null_values["bootstrap_rescaled_empirical_gaps"][idx].append(
                beta0_1d_rips(bootstrap_points, eps)
            )

    null_reports = {}
    null_definitions = {
        "uniform_unfolded_range": (
            "Draw n points uniformly over the same unfolded interval and sort them."
        ),
        "bootstrap_rescaled_empirical_gaps": (
            "Resample observed unfolded gaps with replacement and rescale them to "
            "the same total unfolded range. This is data-adaptive and exploratory."
        ),
    }
    for name, by_eps in null_values.items():
        summaries = [
            summarize_beta0_null(values, observed_beta0[idx], eps)
            for idx, (values, eps) in enumerate(zip(by_eps, eps_grid))
        ]
        selected = min(
            summaries,
            key=lambda row: (
                row["p_null_beta0_le_observed"],
                row["epsilon"],
            ),
        )
        null_reports[name] = {
            "definition": null_definitions[name],
            "epsilon_summaries": summaries,
            "selected_epsilon_by_min_left_tail_probability": selected["epsilon"],
            "selected_p_null_beta0_le_observed": (
                selected["p_null_beta0_le_observed"]
            ),
            "selected_p_bonferroni_over_epsilon_grid": float(
                min(1.0, len(eps_grid) * selected["p_null_beta0_le_observed"])
            ),
            "multiple_selection_note": (
                "The selected raw tail probability is the minimum over the "
                "epsilon grid. The Bonferroni value is the conservative "
                "family-wise correction for that selection."
            ),
        }

    return {
        "name": "finite_Monte_Carlo_selector",
        "samples": int(samples),
        "seed": int(seed),
        "observable": (
            "beta0 of the one-dimensional Rips graph over unfolded ordinates"
        ),
        "selection_rule": (
            "For each predeclared null, choose the epsilon with the smallest "
            "Monte Carlo left-tail probability P(beta0_null <= beta0_observed). "
            "All epsilon summaries are reported to avoid hidden selection."
        ),
        "observed_beta0_by_epsilon": [
            {"epsilon": float(eps), "beta0": int(beta0)}
            for eps, beta0 in zip(eps_grid, observed_beta0)
        ],
        "null_models": null_reports,
        "interpretation": (
            "Monte Carlo estimates finite null probabilities under specified "
            "sampling assumptions. It does not enumerate all possible zeros, "
            "does not certify Z_off(T)=empty, and does not prove RH."
        ),
    }


def read_zero_data(path: Path) -> list[float]:
    """Read zero ordinates from a small JSON or CSV audit file."""
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if "zeros_used" in data:
            return sorted(float(x) for x in data["zeros_used"])
        if "zeros" in data:
            return sorted(float(x) for x in data["zeros"])
        raise ValueError("JSON zero data must contain 'zeros_used' or 'zeros'.")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        return []

    preferred = ["gamma_n", "gamma", "ordinate", "t"]
    field = next((name for name in preferred if name in rows[0]), None)
    if field is None:
        raise ValueError(
            "CSV zero data must contain one of: gamma_n, gamma, ordinate, t."
        )
    return sorted(float(row[field]) for row in rows)


def validate_zero_ordinates(gamma: np.ndarray) -> np.ndarray:
    values = np.sort(np.asarray(gamma, dtype=float))
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("Zero ordinates must be a nonempty one-dimensional list.")
    if not np.all(np.isfinite(values)):
        raise ValueError("Zero ordinates must all be finite.")
    if np.any(values <= 0):
        raise ValueError(
            "This script uses positive ordinates only; every gamma must be > 0."
        )
    if len(values) > 1 and np.any(np.diff(values) <= 1e-12):
        raise ValueError(
            "Zero ordinates must be strictly increasing and nonduplicated."
        )
    return values


def load_or_compute_zeros(n: int, dps: int, zeros_data: str | None) -> tuple[np.ndarray, str]:
    if zeros_data:
        zeros = read_zero_data(Path(zeros_data))
        if n > 0:
            zeros = zeros[:n]
        return np.array(zeros, dtype=float), f"local data file: {zeros_data}"

    if mp is None:
        raise SystemExit(
            "mpmath is not installed. Install mpmath or pass --zeros-data "
            "with a JSON/CSV file of critical-line ordinates."
        )

    mp.mp.dps = dps
    zeros = [float(mp.im(mp.zetazero(k))) for k in range(1, n+1)]
    return np.array(zeros, dtype=float), f"mpmath.zetazero, dps={dps}"


def mirror_adjoint(beta: float, gamma: float) -> dict:
    reflected_beta = 1.0 - beta
    reflected_gamma = gamma
    linear_defect = abs(2.0 * beta - 1.0)
    quadratic_defect = linear_defect * linear_defect
    return {
        "rho": {"beta": float(beta), "gamma": float(gamma)},
        "R_adjoint_rho": {
            "beta": float(reflected_beta),
            "gamma": float(reflected_gamma),
        },
        "fixed_by_mirror": linear_defect == 0.0,
        "linear_defect_abs_2beta_minus_1": float(linear_defect),
        "quadratic_mirror_defect": float(quadratic_defect),
    }


def mirror_adjunction_report(
    gamma: np.ndarray,
    sample_beta: float | None,
    sample_gamma: float | None,
) -> dict:
    listed_count = int(len(gamma))
    line_residuals = [mirror_adjoint(0.5, float(g)) for g in gamma]
    max_linear = max(
        (row["linear_defect_abs_2beta_minus_1"] for row in line_residuals),
        default=0.0,
    )
    mirror_energy = sum(
        row["quadratic_mirror_defect"] for row in line_residuals
    )
    report = {
        "operator_name": "R_adjoint",
        "definition": (
            "R_adjoint(beta+i*gamma)=1-conjugate(beta+i*gamma)="
            "(1-beta)+i*gamma"
        ),
        "fixed_locus": "Re(rho)=1/2",
        "fixed_condition": "rho=R_adjoint(rho) iff Re(rho)=1/2",
        "listed_critical_line_zeros_tested": listed_count,
        "max_listed_zero_linear_defect_abs_2beta_minus_1": float(max_linear),
        "listed_zero_mirror_energy_sum": float(mirror_energy),
        "interpretation": (
            "All listed critical-line zeros are fixed by R_adjoint. This checks "
            "the listed data only; it does not exclude unlisted off-line zeros."
        ),
        "off_line_pair_rule": (
            "A hypothetical off-line zero beta+i*gamma with beta!=1/2 is mirrored "
            "to (1-beta)+i*gamma and has positive mirror defect."
        ),
    }
    if sample_beta is not None:
        if sample_gamma is None:
            sample_gamma = float(gamma[0]) if len(gamma) else 0.0
        report["sample_candidate"] = mirror_adjoint(sample_beta, sample_gamma)
    return report


def mobius_start_marker_report(
    below: list[float],
    above: list[float],
    T: float,
    supplied_total_count: int | None,
    german_value: int | None,
) -> dict:
    certified_closed = (
        supplied_total_count is not None
        and german_value == 0
    )
    return {
        "name": "M_German(T)",
        "coordinate_model": (
            "Finite Mobius-marker model: write v=beta-1/2 and identify "
            "the two ends of a finite band by (0,v)~(1,-v)."
        ),
        "start_mark": {
            "height_interval": POSITIVE_ORDINATE_CONVENTION,
            "first_listed_critical_line_zero": below[0] if below else None,
        },
        "finite_end_mark": {
            "T": float(T),
            "last_listed_critical_line_zero_up_to_T": below[-1] if below else None,
            "next_listed_critical_line_zero_above_T": above[0] if above else None,
        },
        "center_line_marker_rule": (
            "On v=0, the Mobius endpoint is identified with the initial point; "
            "an oriented transverse marker returns to the same orientation only "
            "after two turns."
        ),
        "off_line_marker_rule": (
            "A point with v!=0 is sent to the opposite side under the fold. "
            "The fold pairs off-line candidates; it does not remove them."
        ),
        "listed_center_line_marker_defect_sum": 0.0,
        "arithmetic_closure_certified_for_T": certified_closed,
        "closure_certification_rule": (
            "The finite path is arithmetically closed only when the independent "
            "whole-strip count equals the listed critical-line count, so "
            "G_German(T)=0."
        ),
        "interpretation": (
            "Finding the marked endpoint again is a finite closure marker. "
            "For RH, this marker must close with no off-line remainder for "
            "every finite T; a single finite closure is not a global proof."
        ),
    }


def german_bridge_lemma_report(
    T: float,
    german_value: int | None,
    certified: bool,
    prime_detector: dict | None,
) -> dict:
    if prime_detector is None:
        return {
            "name": "German_prime_zero_bridge_lemma",
            "display_name": "Lema puente de la función Germán",
            "status": "not_evaluated_no_prime_cutoff",
            "required_input": "Run with --prime-limit P to attach the prime channel.",
            "global_RH_proved": False,
        }

    return {
        "name": "German_prime_zero_bridge_lemma",
        "display_name": "Lema puente de la función Germán",
        "status": "NV_unproved_methodological_lemma",
        "finite_statement": (
            "For a finite height T and prime cutoff P, compare the zero-count "
            "remainder G_German(T) with the prime channel "
            "(Sigma_pi(P), Sigma_hat_pi(P), psi(P), A_P)."
        ),
        "proposed_bridge": (
            "If one proves a uniform error theorem showing that the bounded "
            "prime channel forces the whole-strip count to equal the "
            "critical-line count for every finite T, then G_German(T)=0 for "
            "all T would follow."
        ),
        "current_finite_inputs": {
            "T": float(T),
            "G_German_T": german_value,
            "Z_off_T_empty_certified_from_independent_count": bool(certified),
            "prime_cutoff_P": prime_detector["prime_limit_P"],
            "Sigma_pi_P": prime_detector["prime_sum_limit_Sigma_pi_P"],
            "Sigma_hat_pi_P": prime_detector["bounded_prime_sum_limit"],
            "psi_P": prime_detector["Chebyshev_psi_P"],
        },
        "verified_in_this_run": (
            "Only the finite arithmetic values and the optional external "
            "finite count comparison are evaluated."
        ),
        "not_verified": [
            "No theorem is proved here that Sigma_pi(P) or Sigma_hat_pi(P) determines all zeta zeros.",
            "No uniform P,T error bound is proved.",
            "No off-line mirror pair is excluded by the prime channel alone.",
            "No global quantifier over every finite T is discharged.",
        ],
        "proof_obligation": (
            "Prove a non-circular implication from the prime-limit data to "
            "N_strip(T)=N_critical_line(T), uniformly over T. This is the "
            "missing bridge between the finite detector and RH."
        ),
        "global_RH_proved": False,
    }


def zoff_report(
    gamma: np.ndarray,
    T: float,
    supplied_total_count: int | None,
    certification_source: str | None,
    prime_detector: dict | None = None,
) -> dict:
    below = [float(x) for x in gamma if 0 < float(x) <= T]
    above = [float(x) for x in gamma if float(x) > T]
    on_line_count = len(below)
    if supplied_total_count is not None and supplied_total_count < on_line_count:
        raise ValueError(
            "The supplied whole-strip count cannot be smaller than the number "
            "of listed critical-line zeros up to T."
        )
    german_value = (
        None
        if supplied_total_count is None
        else int(supplied_total_count - on_line_count)
    )
    certified = (
        supplied_total_count is not None
        and german_value == 0
    )
    report = {
        "predicate": (
            "Z_off_plus(T)={rho=beta+i*gamma: zeta(rho)=0, 0<beta<1, "
            "beta!=1/2, 0<gamma<=T}"
        ),
        "ordinate_convention": POSITIVE_ORDINATE_CONVENTION,
        "T": float(T),
        "critical_line_zeros_in_local_data_up_to_T": on_line_count,
        "last_local_zero_up_to_T": below[-1] if below else None,
        "next_local_zero_above_T": above[0] if above else None,
        "supplied_total_strip_count_N_plus_T": supplied_total_count,
        "certification_source": certification_source,
        "Z_off_T_empty_conditional_on_supplied_count": certified,
        "Z_off_T_empty_certified": certified,
        "certification_scope": (
            "The program checks equality against a user-supplied total count; "
            "it does not authenticate the external source."
        ),
        "certification_rule": (
            "Conditional on a valid externally supplied total count N_plus(T), "
            "Z_off_plus(T) is empty when that count equals the number of verified "
            "critical-line zeros with 0<gamma<=T."
        ),
        "German_function": {
            "name": "G_German(T)",
            "display_name": "Función Germán",
            "definition": (
                "G_German_plus(T)=N_strip_plus(T)-N_critical_line_plus(T)="
                "#Z_off_plus(T), using 0<gamma<=T"
            ),
            "multiplicity_convention": (
                "N_strip(T) and N_critical_line(T) must be counted with the same "
                "multiplicity and positive-ordinate convention. A local data file "
                "contains listed ordinates, not an authenticated total strip count."
            ),
            "value": german_value,
            "interpretation": (
                "Conditional on a valid external N_strip_plus(T), G_German_plus(T)=0 "
                "implies Z_off_plus(T)=empty for that finite T. Without that external "
                "count, the value is not computable from critical-line zeros alone."
            ),
            "RH_equivalence": (
                "RH is equivalent to G_German_plus(T)=0 for every finite T, using "
                "the same positive-ordinate and multiplicity conventions."
            ),
        },
        "German_mirror_adjoint_function": {
            "name": "G_German_star(T)",
            "display_name": "Función Germán espejo-adjunta",
            "mirror_operator": "R_adjoint(rho)=1-conjugate(rho)",
            "definition": (
                "G_German_star(T)=sum_{rho in Z_strip(T)} |rho-R_adjoint(rho)|^2"
                "=sum_{rho in Z_strip(T)} |2*Re(rho)-1|^2"
            ),
            "value": 0 if certified else None,
            "interpretation": (
                "G_German_star(T)=0 iff every zero in the finite strip segment "
                "is fixed by the adjoint mirror, hence lies on Re(s)=1/2. "
                "It cannot be computed from listed critical-line zeros alone unless "
                "a valid external total strip enumeration/count is supplied."
            ),
        },
        "Mobius_start_marker": mobius_start_marker_report(
            below,
            above,
            T,
            supplied_total_count,
            german_value,
        ),
        "German_bridge_lemma": german_bridge_lemma_report(
            T,
            german_value,
            certified,
            prime_detector,
        ),
        "local_data_alone_certifies_Z_off_T_empty": False,
        "global_RH_proved": False,
    }
    if prime_detector is not None:
        report["German_function"]["prime_limit_extension"] = {
            "name": "G_German(T;P)",
            "display_name": "Función Germán primo-limitada",
            "definition": (
                "G_German(T;P)=(N_strip(T)-N_critical_line(T), "
                "Sigma_pi(P), Sigma_hat_pi(P), psi(P), "
                "A_P restricted to the listed zeros)"
            ),
            "prime_cutoff_P": prime_detector["prime_limit_P"],
            "prime_count_pi_P": prime_detector["prime_count_pi_P"],
            "prime_sum_limit_Sigma_pi_P": (
                prime_detector["prime_sum_limit_Sigma_pi_P"]
            ),
            "bounded_prime_sum_limit": (
                prime_detector["bounded_prime_sum_limit"]
            ),
            "bounded_prime_sum_definition": (
                prime_detector["bounded_prime_sum_definition"]
            ),
            "prime_sum_normalized_by_PNT_scale": (
                prime_detector["prime_sum_normalized_by_PNT_scale"]
            ),
            "prime_power_term_count": prime_detector["prime_power_term_count"],
            "Chebyshev_psi_P": prime_detector["Chebyshev_psi_P"],
            "finite_angular_prime_sum": (
                prime_detector["finite_angular_prime_sum"]
            ),
            "angular_centered_l2_norm": (
                prime_detector["angular_field_on_listed_zeros"][
                    "centered_l2_norm"
                ]
            ),
            "role": (
                "The prime cutoff P acts as the detected finite arithmetic "
                "limit/channel. Sigma_pi(P) records the user's prime-sum "
                "limit, while Sigma_hat_pi(P) keeps that channel bounded. "
                "The zero-count component remains the only finite certificate "
                "for Z_off(T)=empty."
            ),
            "limit_requirement": (
                "A global RH argument would require a theorem controlling this "
                "prime channel uniformly as P and T increase, together with the "
                "whole-strip zero count. The finite value is not enough."
            ),
        }
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--dps", type=int, default=40)
    p.add_argument(
        "--zeros-data",
        default=None,
        help="Optional JSON/CSV file with critical-line zero ordinates.",
    )
    p.add_argument(
        "--zoff-T",
        type=float,
        default=None,
        help="If supplied, report the finite off-critical-line predicate Z_off(T).",
    )
    p.add_argument(
        "--supplied-total-count",
        "--certified-total-count",
        dest="supplied_total_count",
        type=int,
        default=None,
        help=(
            "User-supplied total count N_plus(T) in the critical strip for "
            "positive ordinates. The legacy --certified-total-count name is "
            "accepted for backward compatibility."
        ),
    )
    p.add_argument(
        "--certification-source",
        default=None,
        help=(
            "Citation or note for the externally supplied positive-ordinate "
            "total count. The script records but does not authenticate it."
        ),
    )
    p.add_argument(
        "--mirror-beta",
        type=float,
        default=None,
        help="Optional beta value for a sample adjoint-mirror candidate.",
    )
    p.add_argument(
        "--mirror-gamma",
        type=float,
        default=None,
        help="Optional gamma value for a sample adjoint-mirror candidate.",
    )
    p.add_argument(
        "--mc-samples",
        "--monte-carlo-samples",
        dest="mc_samples",
        type=int,
        default=0,
        help=(
            "Optional Monte Carlo samples for finite null-probability selection."
        ),
    )
    p.add_argument(
        "--mc-seed",
        "--monte-carlo-seed",
        dest="mc_seed",
        type=int,
        default=2510,
        help="Random seed for the optional Monte Carlo selector.",
    )
    p.add_argument(
        "--prime-limit",
        type=int,
        default=0,
        help=(
            "Optional finite prime cutoff P for Chebyshev/von Mangoldt prime "
            "sums and the detected prime angular field."
        ),
    )
    p.add_argument(
        "--prime-term-preview",
        type=int,
        default=12,
        help="Number of prime-power terms to preview in the JSON report.",
    )
    p.add_argument("--out", default="riemann_graph_audit_results.json")
    args = p.parse_args()

    gamma, zero_source = load_or_compute_zeros(args.n, args.dps, args.zeros_data)
    gamma = validate_zero_ordinates(gamma)
    if len(gamma) < 2:
        raise SystemExit("Need at least two zero ordinates for the graph audit.")

    x = nbar(gamma)
    gaps = np.diff(x)
    neutral = np.arange(len(gamma), dtype=float)
    eps_grid = [0.25,0.50,0.75,1.00,1.25,1.50,1.75,2.00]

    prime_detector = None
    if args.prime_limit > 0:
        prime_detector = prime_limit_detector_report(
            gamma,
            args.prime_limit,
            args.prime_term_preview,
        )

    out = {
        "n_requested": args.n,
        "n_used": int(len(gamma)),
        "zero_source": zero_source,
        "ordinate_convention": POSITIVE_ORDINATE_CONVENTION,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "mpmath": None if mp is None else getattr(mp, "__version__", "unknown"),
        },
        "unfolding": "Nbar(T)=T/(2pi) log(T/(2pi))-T/(2pi)+7/8",
        "gap_summary": {
            "mean": float(gaps.mean()),
            "median": float(np.median(gaps)),
            "min": float(gaps.min()),
            "max": float(gaps.max()),
        },
        "epsilon_grid": eps_grid,
        "null_beta0": [int(len(gamma)) for _ in eps_grid],
        "neutral": [laplacian_report(neutral, e) for e in eps_grid],
        "riemann": [laplacian_report(x, e) for e in eps_grid],
        "mirror_adjunction": mirror_adjunction_report(
            gamma,
            args.mirror_beta,
            args.mirror_gamma,
        ),
        "status": "finite_numerical_audit_not_RH_proof",
    }
    if args.mc_samples > 0:
        out["monte_carlo_selector"] = monte_carlo_selector_report(
            x,
            eps_grid,
            args.mc_samples,
            args.mc_seed,
        )
    if prime_detector is not None:
        out["prime_limit_detector"] = prime_detector
    if args.zoff_T is not None:
        out["Z_off_finite_audit"] = zoff_report(
            gamma,
            args.zoff_T,
            args.supplied_total_count,
            args.certification_source,
            prime_detector,
        )
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
