#!/usr/bin/env python3
"""Demostracion falsable de capacidad explicativa multiescala con Pantheon+.

Compara tres modelos sobre la misma seleccion, covarianza y particion:
  1. Lambda-CDM plano.
  2. wCDM plano con w constante.
  3. Una extension multiescala con exponente local suave alpha_X(s).

El ajuste usa la matriz oficial STAT+SYS completa. El 20 % de las supernovas
se reserva por CID (objeto fisico), de forma estratificada en corrimiento al
rojo. La prediccion reservada usa la distribucion gaussiana condicional para
respetar las correlaciones entre entrenamiento y prueba.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import matplotlib
import numpy as np
import pandas as pd
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.integrate import cumulative_trapezoid
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import minimize, minimize_scalar


C_LIGHT = 299_792.458  # km s^-1
H0_FID = 70.0  # km s^-1 Mpc^-1; degenerado con M y fijado por conveniencia
Z_TRANSITION = 0.5
S_TRANSITION = math.log1p(Z_TRANSITION)
S_WIDTH = 0.12
SOURCE_REPOSITORY = "https://github.com/PantheonPlusSH0ES/DataRelease"
SOURCE_DATA = (
    "https://github.com/PantheonPlusSH0ES/DataRelease/blob/main/"
    "Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat"
)
SOURCE_COV = (
    "https://github.com/PantheonPlusSH0ES/DataRelease/blob/main/"
    "Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"
    "Pantheon%2BSH0ES_STAT%2BSYS.cov"
)
SOURCE_DATA_BLOB = "cce857db0c15e9ce7a0e0ce77452b6ff62af969a"
SOURCE_COV_BLOB = "d1a1498154e7ba826df14bdbef35ebcb7f5efba1"


@dataclass(frozen=True)
class DataSet:
    frame: pd.DataFrame
    covariance: np.ndarray
    original_count: int
    selected_indices: np.ndarray
    covariance_max_asymmetry_before_symmetrizing: float


@dataclass
class GaussianBlock:
    indices: np.ndarray
    covariance: np.ndarray
    factor: tuple[np.ndarray, bool]
    precision: np.ndarray
    cinv_one: np.ndarray
    one_cinv_one: float
    logdet: float


@dataclass(frozen=True)
class FitResult:
    name: str
    shape_parameters: dict[str, float]
    nuisance_M: float
    chi2: float
    n: int
    k: int
    aicc: float
    bic: float
    prediction: np.ndarray
    normalized_singular_values: list[float]
    spectral_condition: float
    parameter_sigma: dict[str, float]
    parameter_correlation: list[list[float]]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dataset(data_path: Path, covariance_path: Path) -> DataSet:
    frame_all = pd.read_csv(data_path, sep=r"\s+")
    if len(frame_all) != 1701:
        raise ValueError(f"Se esperaban 1701 filas; se obtuvieron {len(frame_all)}")

    with covariance_path.open("r", encoding="utf-8") as stream:
        dimension = int(stream.readline().strip())
    flat = np.loadtxt(covariance_path, skiprows=1, dtype=np.float64)
    if flat.size != dimension * dimension:
        raise ValueError(
            f"Covarianza incompleta: {flat.size} valores para {dimension}x{dimension}"
        )
    covariance_all = flat.reshape(dimension, dimension)
    max_asymmetry = float(np.max(np.abs(covariance_all - covariance_all.T)))
    median_variance = float(np.median(np.diag(covariance_all)))
    # El archivo publica ocho decimales; pares transpuestos difieren hasta 3e-8.
    if max_asymmetry > 1e-5 * median_variance:
        raise ValueError(
            "La asimetria de la covarianza excede el redondeo admisible: "
            f"{max_asymmetry:.3e}"
        )
    covariance_all = 0.5 * (covariance_all + covariance_all.T)

    mask = frame_all["zHD"].to_numpy() > 0.01
    indices = np.flatnonzero(mask)
    frame = frame_all.loc[mask].reset_index(drop=True)
    covariance = covariance_all[np.ix_(indices, indices)]
    return DataSet(frame, covariance, len(frame_all), indices, max_asymmetry)


def make_block(covariance: np.ndarray, indices: np.ndarray) -> GaussianBlock:
    subcov = covariance[np.ix_(indices, indices)]
    factor = cho_factor(subcov, lower=True, check_finite=False)
    precision = cho_solve(factor, np.eye(len(indices)), check_finite=False)
    precision = 0.5 * (precision + precision.T)
    ones = np.ones(len(indices))
    cinv_one = precision @ ones
    one_cinv_one = float(ones @ cinv_one)
    diagonal = np.diag(factor[0])
    logdet = float(2.0 * np.log(diagonal).sum())
    return GaussianBlock(
        indices, subcov, factor, precision, cinv_one, one_cinv_one, logdet
    )


def stratified_group_split(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Reserva cada quinto CID tras ordenar objetos por su mediana de z."""
    grouped = frame.groupby("CID", sort=False)["zHD"].median().sort_values()
    holdout_cids = set(grouped.index[::5].astype(str))
    is_holdout = frame["CID"].astype(str).isin(holdout_cids).to_numpy()
    return np.flatnonzero(~is_holdout), np.flatnonzero(is_holdout)


def transition_weight(s: np.ndarray) -> np.ndarray:
    """Peso activo a baja escala cosmologica y apagado suavemente a alta z."""
    return 0.5 * (1.0 - np.tanh((s - S_TRANSITION) / S_WIDTH))


def integrated_transition(s: np.ndarray) -> np.ndarray:
    """Integral de transition_weight desde 0 hasta s."""
    x = (s - S_TRANSITION) / S_WIDTH
    x0 = -S_TRANSITION / S_WIDTH
    return 0.5 * (s - S_WIDTH * (np.log(np.cosh(x)) - math.log(math.cosh(x0))))


def expansion_rate(z: np.ndarray, model: str, parameters: np.ndarray) -> np.ndarray:
    omega_m = float(parameters[0])
    s = np.log1p(z)
    matter = omega_m * np.exp(3.0 * s)
    if model == "lcdm":
        rho_x = np.ones_like(z)
    elif model == "wcdm":
        w = float(parameters[1])
        rho_x = np.exp(3.0 * (1.0 + w) * s)
    elif model == "multiscale":
        amplitude = float(parameters[1])
        rho_x = np.exp(amplitude * integrated_transition(s))
    else:
        raise ValueError(f"Modelo desconocido: {model}")
    e2 = matter + (1.0 - omega_m) * rho_x
    if np.any(e2 <= 0.0) or not np.all(np.isfinite(e2)):
        return np.full_like(z, np.nan)
    return np.sqrt(e2)


def distance_modulus_without_M(
    z_hd: np.ndarray,
    z_hel: np.ndarray,
    model: str,
    parameters: np.ndarray,
) -> np.ndarray:
    z_max = float(np.max(z_hd)) * 1.002
    grid = np.linspace(0.0, z_max, 7000)
    e_grid = expansion_rate(grid, model, parameters)
    if not np.all(np.isfinite(e_grid)):
        return np.full_like(z_hd, np.nan)
    dc_grid = (C_LIGHT / H0_FID) * cumulative_trapezoid(
        1.0 / e_grid, grid, initial=0.0
    )
    d_m = np.interp(z_hd, grid, dc_grid)
    luminosity_distance = (1.0 + z_hel) * d_m
    return 5.0 * np.log10(luminosity_distance) + 25.0


def model_parameterization(name: str) -> tuple[np.ndarray, list[tuple[float, float]], list[str]]:
    if name == "lcdm":
        return np.array([0.30]), [(0.05, 0.60)], ["Omega_m"]
    if name == "wcdm":
        return np.array([0.30, -1.0]), [(0.05, 0.60), (-2.0, -0.2)], ["Omega_m", "w"]
    if name == "multiscale":
        return np.array([0.30, 0.0]), [(0.05, 0.60), (-3.0, 3.0)], ["Omega_m", "A"]
    raise ValueError(name)


def predict_profiled(
    frame: pd.DataFrame,
    observed: np.ndarray,
    block: GaussianBlock,
    model: str,
    parameters: np.ndarray,
) -> tuple[float, float, np.ndarray]:
    mu0 = distance_modulus_without_M(
        frame["zHD"].to_numpy(), frame["zHEL"].to_numpy(), model, parameters
    )
    if not np.all(np.isfinite(mu0)):
        return 1e100, np.nan, mu0
    residual0 = observed[block.indices] - mu0[block.indices]
    nuisance_M = float(block.cinv_one @ residual0 / block.one_cinv_one)
    residual = residual0 - nuisance_M
    solved = block.precision @ residual
    chi2 = float(residual @ solved)
    return chi2, nuisance_M, mu0 + nuisance_M


def optimize_shape(
    frame: pd.DataFrame,
    observed: np.ndarray,
    block: GaussianBlock,
    model: str,
) -> tuple[np.ndarray, float, float, np.ndarray]:
    initial, bounds, _ = model_parameterization(model)

    def objective(parameters: np.ndarray) -> float:
        if any(
            value < low or value > high
            for value, (low, high) in zip(parameters, bounds)
        ):
            return 1e100
        return predict_profiled(frame, observed, block, model, parameters)[0]

    if model == "lcdm":
        result_1d = minimize_scalar(
            lambda value: objective(np.array([value])),
            bounds=bounds[0],
            method="bounded",
            options={"xatol": 1e-9},
        )
        parameters = np.array([result_1d.x])
        success = result_1d.success
        message = result_1d.message
    else:
        starts = [
            initial,
            np.array([0.20, initial[1]]),
            np.array([0.40, initial[1]]),
            np.array([0.30, -0.7 if model == "wcdm" else 0.7]),
            np.array([0.30, -1.3 if model == "wcdm" else -0.7]),
        ]
        candidates = [
            minimize(
                objective,
                start,
                method="L-BFGS-B",
                bounds=bounds,
                options={
                    "maxiter": 300,
                    "ftol": 1e-10,
                    "gtol": 1e-5,
                    "eps": 1e-4,
                    "maxls": 50,
                },
            )
            for start in starts
        ]
        finite_candidates = [item for item in candidates if np.isfinite(item.fun)]
        if not finite_candidates:
            raise RuntimeError(f"Ningun ajuste finito para {model}")
        best = min(finite_candidates, key=lambda item: item.fun)
        parameters = np.asarray(best.x)
        success = np.isfinite(best.fun)
        message = best.message
    if not success:
        raise RuntimeError(f"Fallo el ajuste de {model}: {message}")
    chi2, nuisance_M, prediction = predict_profiled(
        frame, observed, block, model, parameters
    )
    return parameters, nuisance_M, chi2, prediction


def numerical_jacobian(
    frame: pd.DataFrame,
    model: str,
    parameters: np.ndarray,
    nuisance_M: float,
    indices: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    _, _, names = model_parameterization(model)
    columns = []
    for column, value in enumerate(parameters):
        step = 1e-4 * max(1.0, abs(float(value)))
        plus = parameters.copy()
        minus = parameters.copy()
        plus[column] += step
        minus[column] -= step
        mu_plus = distance_modulus_without_M(
            frame["zHD"].to_numpy(), frame["zHEL"].to_numpy(), model, plus
        )
        mu_minus = distance_modulus_without_M(
            frame["zHD"].to_numpy(), frame["zHEL"].to_numpy(), model, minus
        )
        columns.append((mu_plus[indices] - mu_minus[indices]) / (2.0 * step))
    columns.append(np.ones(len(indices)))
    return np.column_stack(columns), names + ["M"]


def spectral_diagnostics(
    frame: pd.DataFrame,
    block: GaussianBlock,
    model: str,
    parameters: np.ndarray,
    nuisance_M: float,
) -> tuple[list[float], float, dict[str, float], list[list[float]]]:
    jacobian, names = numerical_jacobian(
        frame, model, parameters, nuisance_M, block.indices
    )
    cinv_j = block.precision @ jacobian
    fisher = jacobian.T @ cinv_j
    covariance_parameters = np.linalg.inv(fisher)
    sigma = np.sqrt(np.diag(covariance_parameters))
    correlation = covariance_parameters / np.outer(sigma, sigma)

    column_norm = np.sqrt(np.diag(fisher))
    normalized_fisher = fisher / np.outer(column_norm, column_norm)
    singular = np.sqrt(np.clip(np.linalg.eigvalsh(normalized_fisher), 0.0, None))[::-1]
    positive = singular[singular > 1e-12]
    condition = float(positive[0] / positive[-1])
    return (
        singular.tolist(),
        condition,
        {name: float(value) for name, value in zip(names, sigma)},
        correlation.tolist(),
    )


def information_criteria(chi2: float, n: int, k: int) -> tuple[float, float]:
    aic = chi2 + 2.0 * k
    aicc = aic + (2.0 * k * (k + 1.0)) / (n - k - 1.0)
    bic = chi2 + k * math.log(n)
    return float(aicc), float(bic)


def fit_model(
    frame: pd.DataFrame,
    observed: np.ndarray,
    block: GaussianBlock,
    model: str,
) -> FitResult:
    parameters, nuisance_M, chi2, prediction = optimize_shape(
        frame, observed, block, model
    )
    _, _, names = model_parameterization(model)
    k = len(parameters) + 1
    aicc, bic = information_criteria(chi2, len(block.indices), k)
    singular, condition, sigma, correlation = spectral_diagnostics(
        frame, block, model, parameters, nuisance_M
    )
    return FitResult(
        name=model,
        shape_parameters={name: float(value) for name, value in zip(names, parameters)},
        nuisance_M=float(nuisance_M),
        chi2=float(chi2),
        n=len(block.indices),
        k=k,
        aicc=aicc,
        bic=bic,
        prediction=prediction,
        normalized_singular_values=singular,
        spectral_condition=condition,
        parameter_sigma=sigma,
        parameter_correlation=correlation,
    )


def conditional_holdout_chi2(
    observed: np.ndarray,
    covariance: np.ndarray,
    train: np.ndarray,
    holdout: np.ndarray,
    train_block: GaussianBlock,
    prediction: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray]:
    residual_train = observed[train] - prediction[train]
    residual_holdout = observed[holdout] - prediction[holdout]
    c_ht = covariance[np.ix_(holdout, train)]
    c_hh = covariance[np.ix_(holdout, holdout)]
    cinv_residual_train = train_block.precision @ residual_train
    conditional_residual = residual_holdout - c_ht @ cinv_residual_train
    cinv_c_th = train_block.precision @ c_ht.T
    conditional_covariance = c_hh - c_ht @ cinv_c_th
    conditional_covariance = 0.5 * (
        conditional_covariance + conditional_covariance.T
    )
    factor = cho_factor(conditional_covariance, lower=True, check_finite=False)
    solved = cho_solve(factor, conditional_residual, check_finite=False)
    return (
        float(conditional_residual @ solved),
        conditional_residual,
        conditional_covariance,
    )


def gls_bin(
    z: np.ndarray,
    residual: np.ndarray,
    covariance: np.ndarray,
    edges: np.ndarray,
) -> pd.DataFrame:
    rows = []
    for low, high in zip(edges[:-1], edges[1:]):
        select = np.flatnonzero((z >= low) & (z < high))
        if len(select) < 2:
            continue
        cov_bin = covariance[np.ix_(select, select)]
        factor = cho_factor(cov_bin, lower=True, check_finite=False)
        ones = np.ones(len(select))
        cinv_one = cho_solve(factor, ones, check_finite=False)
        denominator = float(ones @ cinv_one)
        mean = float(cinv_one @ residual[select] / denominator)
        rows.append(
            {
                "z_low": float(low),
                "z_high": float(high),
                "z_center": float(np.exp(np.mean(np.log1p(z[select]))) - 1.0),
                "n": int(len(select)),
                "residual_mag": mean,
                "sigma_mag": float(1.0 / math.sqrt(denominator)),
            }
        )
    return pd.DataFrame(rows)


def serialize_fit(fit: FitResult) -> dict:
    return {
        "model": fit.name,
        "shape_parameters": fit.shape_parameters,
        "nuisance_M": fit.nuisance_M,
        "chi2": fit.chi2,
        "n": fit.n,
        "k": fit.k,
        "chi2_per_datum": fit.chi2 / fit.n,
        "AICc": fit.aicc,
        "BIC": fit.bic,
        "normalized_operator_singular_values": fit.normalized_singular_values,
        "spectral_condition_number": fit.spectral_condition,
        "parameter_sigma_linearized": fit.parameter_sigma,
        "parameter_correlation": fit.parameter_correlation,
    }


def make_figure(
    output_path: Path,
    frame: pd.DataFrame,
    covariance: np.ndarray,
    observed: np.ndarray,
    full_fits: dict[str, FitResult],
    train_fits: dict[str, FitResult],
    holdout_scores: dict[str, float],
    holdout: np.ndarray,
    binned: pd.DataFrame,
) -> None:
    colors = {"lcdm": "#1f2937", "wcdm": "#0072B2", "multiscale": "#C23B22"}
    labels = {"lcdm": r"$\Lambda$CDM", "wcdm": r"$w$CDM", "multiscale": "Multiescala"}
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.8))
    ax_a, ax_b, ax_c, ax_d = axes.ravel()

    lcdm = full_fits["lcdm"]
    ax_a.errorbar(
        binned["z_center"],
        binned["residual_mag"],
        yerr=binned["sigma_mag"],
        fmt="o",
        color="#111827",
        ecolor="#64748b",
        capsize=2.5,
        ms=5,
        label="Pantheon+ agrupado",
        zorder=4,
    )
    order = np.argsort(frame["zHD"].to_numpy())
    z_ordered = frame["zHD"].to_numpy()[order]
    for name in ("wcdm", "multiscale"):
        delta = full_fits[name].prediction[order] - lcdm.prediction[order]
        ax_a.plot(z_ordered, delta, color=colors[name], lw=2.2, label=labels[name])
    ax_a.axhline(0.0, color=colors["lcdm"], lw=1.3, ls="--", label=labels["lcdm"])
    ax_a.set_xscale("log")
    ax_a.set_xlabel("Corrimiento al rojo $z$")
    ax_a.set_ylabel(r"Residuo respecto a $\Lambda$CDM [mag]")
    ax_a.set_title("A. Cierre sobre el diagrama de Hubble")
    ax_a.legend(frameon=False, fontsize=9, ncol=2)
    ax_a.grid(alpha=0.18)

    model_order = ["lcdm", "wcdm", "multiscale"]
    x = np.arange(len(model_order))
    holdout_reduced = [holdout_scores[name] / len(holdout) for name in model_order]
    ax_b.bar(
        x,
        holdout_reduced,
        color=[colors[name] for name in model_order],
        width=0.62,
    )
    ax_b.axhline(1.0, color="#64748b", ls="--", lw=1.2, label=r"$\chi^2/N=1$")
    ax_b.set_xticks(x, [labels[name] for name in model_order])
    ax_b.set_ylabel(r"$\chi^2_{\rm prueba}/N_{\rm prueba}$")
    ax_b.set_title(f"B. Predicción fuera de muestra ({len(holdout)} filas)")
    ax_b.legend(frameon=False, fontsize=9)
    ax_b.grid(axis="y", alpha=0.18)

    delta_aicc = [full_fits[name].aicc - lcdm.aicc for name in model_order]
    delta_bic = [full_fits[name].bic - lcdm.bic for name in model_order]
    width = 0.34
    ax_c.bar(x - width / 2, delta_aicc, width, color="#4C78A8", label=r"$\Delta$AICc")
    ax_c.bar(x + width / 2, delta_bic, width, color="#F2A541", label=r"$\Delta$BIC")
    ax_c.axhline(0.0, color="#111827", lw=1.0)
    ax_c.set_xticks(x, [labels[name] for name in model_order])
    ax_c.set_ylabel(r"Diferencia respecto a $\Lambda$CDM")
    ax_c.set_title("C. Ganancia frente a complejidad")
    ax_c.legend(frameon=False, fontsize=9)
    ax_c.grid(axis="y", alpha=0.18)

    z_grid = np.geomspace(0.01001, 2.3, 500)
    s_grid = np.log1p(z_grid)
    w_best = full_fits["wcdm"].shape_parameters["w"]
    a_best = full_fits["multiscale"].shape_parameters["A"]
    ax_d.plot(
        z_grid,
        np.full_like(z_grid, 3.0 * (1.0 + w_best)),
        color=colors["wcdm"],
        lw=2.2,
        label=r"$\alpha_X=3(1+w)$",
    )
    ax_d.plot(
        z_grid,
        a_best * transition_weight(s_grid),
        color=colors["multiscale"],
        lw=2.4,
        label=r"$\alpha_X(s)=A\,g(s)$",
    )
    ax_d.axhline(0.0, color=colors["lcdm"], ls="--", lw=1.2)
    ax_d.axvline(Z_TRANSITION, color="#64748b", ls=":", lw=1.2, label=r"$z_t=0.5$")
    ax_d.set_xscale("log")
    ax_d.xaxis.set_major_formatter(ScalarFormatter())
    ax_d.set_xlabel("Corrimiento al rojo $z$")
    ax_d.set_ylabel(r"Exponente local $\alpha_X=d\ln\rho_X/ds$")
    ax_d.set_title("D. Flujo de escala inferido")
    ax_d.legend(frameon=False, fontsize=9)
    ax_d.grid(alpha=0.18)

    fig.suptitle(
        "Prueba empírica acotada de capacidad explicativa multiescala",
        fontsize=16,
        fontweight="bold",
        y=0.985,
    )
    caption = (
        "Figura 1. Pantheon+ (zHD > 0.01) ajustado con la covarianza oficial estadística+sistemática completa. "
        "El 20 % de los objetos, separado por CID y estratificado en z, no intervino en el ajuste de entrenamiento; "
        "su puntuación usa la covarianza condicional. A muestra residuos GLS agrupados; B mide predicción reservada; "
        "C penaliza parámetros adicionales; D muestra el exponente sectorial inferido. Las curvas son ajustes "
        "fenomenológicos reproducibles, no datos experimentales nuevos ni validación de una teoría fundamental."
    )
    fig.text(0.055, 0.018, caption, ha="left", va="bottom", fontsize=9.2, wrap=True)
    fig.tight_layout(rect=(0.04, 0.105, 0.98, 0.955), h_pad=2.3, w_pad=2.0)
    fig.savefig(output_path, dpi=220, facecolor="white")
    plt.close(fig)


def verdict_from_results(
    full_fits: dict[str, FitResult], holdout_scores: dict[str, float]
) -> dict[str, str | bool | float]:
    baseline = full_fits["lcdm"]
    candidate = full_fits["multiscale"]
    delta_bic = candidate.bic - baseline.bic
    delta_aicc = candidate.aicc - baseline.aicc
    holdout_gain = holdout_scores["lcdm"] - holdout_scores["multiscale"]
    beats_equal_complexity = holdout_scores["multiscale"] < holdout_scores["wcdm"]
    supported = bool(delta_bic < -2.0 and holdout_gain > 2.0 and beats_equal_complexity)
    if supported:
        statement = (
            "La extension multiescala supera el criterio preregistrado en este conjunto: "
            "mejora BIC, prediccion reservada y al competidor wCDM de igual complejidad."
        )
    elif holdout_gain > 0.0:
        statement = (
            "La extension multiescala mejora parcialmente la prediccion reservada, pero no "
            "supera simultaneamente la penalizacion BIC y el competidor de igual complejidad."
        )
    else:
        statement = (
            "La extension multiescala no mejora la prediccion reservada frente a Lambda-CDM; "
            "Pantheon+ no demuestra capacidad explicativa adicional para esta transicion."
        )
    return {
        "criterion_passed": supported,
        "delta_BIC_multiscale_minus_LCDM": float(delta_bic),
        "delta_AICc_multiscale_minus_LCDM": float(delta_aicc),
        "holdout_chi2_gain_LCDM_minus_multiscale": float(holdout_gain),
        "multiscale_beats_wCDM_on_holdout": bool(beats_equal_complexity),
        "statement": statement,
    }


def run(data_path: Path, covariance_path: Path, output_dir: Path) -> dict:
    dataset = load_dataset(data_path, covariance_path)
    frame = dataset.frame
    covariance = dataset.covariance
    observed = frame["m_b_corr"].to_numpy(dtype=float)
    train, holdout = stratified_group_split(frame)
    full = np.arange(len(frame))
    full_block = make_block(covariance, full)
    train_block = make_block(covariance, train)

    full_fits = {
        name: fit_model(frame, observed, full_block, name)
        for name in ("lcdm", "wcdm", "multiscale")
    }
    train_fits = {
        name: fit_model(frame, observed, train_block, name)
        for name in ("lcdm", "wcdm", "multiscale")
    }

    holdout_scores: dict[str, float] = {}
    conditional_details: dict[str, dict] = {}
    for name, fit in train_fits.items():
        score, conditional_residual, conditional_covariance = conditional_holdout_chi2(
            observed,
            covariance,
            train,
            holdout,
            train_block,
            fit.prediction,
        )
        holdout_scores[name] = score
        conditional_details[name] = {
            "chi2": float(score),
            "n": int(len(holdout)),
            "chi2_per_datum": float(score / len(holdout)),
            "conditional_residual_rms_mag": float(
                np.sqrt(np.mean(conditional_residual**2))
            ),
            "mean_conditional_sigma_mag": float(
                np.mean(np.sqrt(np.diag(conditional_covariance)))
            ),
        }

    residual_full_lcdm = observed - full_fits["lcdm"].prediction
    edges = np.geomspace(0.01, 2.31, 15)
    binned = gls_bin(
        frame["zHD"].to_numpy(), residual_full_lcdm, covariance, edges
    )
    binned.to_csv(output_dir / "demostracion_multiescala_residuos_binned.csv", index=False)

    fit_rows = []
    for scope, fits in (("full", full_fits), ("train", train_fits)):
        for name, fit in fits.items():
            row = {
                "scope": scope,
                "model": name,
                "n": fit.n,
                "k": fit.k,
                "chi2": fit.chi2,
                "chi2_per_datum": fit.chi2 / fit.n,
                "AICc": fit.aicc,
                "BIC": fit.bic,
                "M": fit.nuisance_M,
                "spectral_condition": fit.spectral_condition,
                **fit.shape_parameters,
            }
            if scope == "train":
                row["holdout_chi2"] = holdout_scores[name]
                row["holdout_chi2_per_datum"] = holdout_scores[name] / len(holdout)
            fit_rows.append(row)
    pd.DataFrame(fit_rows).to_csv(
        output_dir / "demostracion_multiescala_ajustes.csv", index=False
    )

    figure_path = output_dir / "figura_demostracion_capacidad_multiescala.png"
    make_figure(
        figure_path,
        frame,
        covariance,
        observed,
        full_fits,
        train_fits,
        holdout_scores,
        holdout,
        binned,
    )

    result = {
        "status": "completed",
        "scope": (
            "Prueba cosmologica acotada: forma del diagrama de Hubble de Pantheon+. "
            "No prueba una teoria unificada ni cuantizacion de la gravedad."
        ),
        "data": {
            "repository": SOURCE_REPOSITORY,
            "data_url": SOURCE_DATA,
            "covariance_url": SOURCE_COV,
            "source_git_blob_data": SOURCE_DATA_BLOB,
            "source_git_blob_covariance": SOURCE_COV_BLOB,
            "local_data_sha256": sha256(data_path),
            "local_covariance_sha256": sha256(covariance_path),
            "rows_original": dataset.original_count,
            "rows_after_zHD_gt_0.01": int(len(frame)),
            "unique_CID_after_cut": int(frame["CID"].nunique()),
            "train_rows": int(len(train)),
            "holdout_rows": int(len(holdout)),
            "train_unique_CID": int(frame.iloc[train]["CID"].nunique()),
            "holdout_unique_CID": int(frame.iloc[holdout]["CID"].nunique()),
            "covariance": "STAT+SYS completa, incluida la correlacion entre particiones",
            "covariance_max_asymmetry_before_symmetrizing": (
                dataset.covariance_max_asymmetry_before_symmetrizing
            ),
            "covariance_symmetrization": "C <- (C + C^T)/2 por redondeo decimal",
        },
        "fixed_protocol": {
            "scale_coordinate": "s = ln(1+z)",
            "transition_redshift": Z_TRANSITION,
            "transition_width_in_s": S_WIDTH,
            "split": "Cada quinto CID tras ordenar por mediana de z se reserva",
            "success_criterion": (
                "Delta BIC < -2, mejora de chi2 reservado > 2 y mejor chi2 reservado "
                "que wCDM de igual numero de parametros"
            ),
        },
        "models": {
            "lcdm": "E^2 = Omega_m(1+z)^3 + 1-Omega_m",
            "wcdm": "rho_X/rho_X0 = exp[3(1+w)s]",
            "multiscale": (
                "d ln(rho_X)/ds = alpha_X(s) = A g(s), "
                "g(s)=[1-tanh((s-s_t)/Delta_s)]/2"
            ),
        },
        "full_fit": {name: serialize_fit(fit) for name, fit in full_fits.items()},
        "train_fit": {name: serialize_fit(fit) for name, fit in train_fits.items()},
        "holdout_conditional": conditional_details,
        "verdict": verdict_from_results(full_fits, holdout_scores),
        "outputs": {
            "figure": str(figure_path.resolve()),
            "binned_residuals": str(
                (output_dir / "demostracion_multiescala_residuos_binned.csv").resolve()
            ),
            "fit_table": str(
                (output_dir / "demostracion_multiescala_ajustes.csv").resolve()
            ),
        },
    }
    result_path = output_dir / "demostracion_multiescala_resultados.json"
    result["outputs"]["json"] = str(result_path.resolve())
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prueba reproducible de una transicion multiescala con Pantheon+."
    )
    base = Path(__file__).resolve().parent
    parser.add_argument(
        "--data",
        type=Path,
        default=base / "data" / "Pantheon+SH0ES.dat",
    )
    parser.add_argument(
        "--covariance",
        type=Path,
        default=base / "data" / "Pantheon+SH0ES_STAT+SYS.cov",
    )
    parser.add_argument("--output-dir", type=Path, default=base)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = run(args.data, args.covariance, args.output_dir)
    print(json.dumps(result["verdict"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
