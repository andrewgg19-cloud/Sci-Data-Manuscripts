#!/usr/bin/env python3
"""Prueba positiva/negativa de estructura multiescala en masa-radio planetaria.

Fuente: instantanea 2023-05-13 de la tabla compuesta del NASA Exoplanet
Archive, conservada por leoybkim/exoplanet. Se usan solamente planetas
transitantes con masa (no M sin i), radio, incertidumbres y sin banderas de
limite. El ajuste incorpora errores en ambos ejes e dispersion intrinseca.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.optimize import minimize

matplotlib.use("Agg")
import matplotlib.pyplot as plt


MIRROR_REPOSITORY = "https://github.com/leoybkim/exoplanet"
MIRROR_COMMIT = "360dc412571742ce0e7cc82b1c8fabc824702c95"
MIRROR_BLOB = "bb2d6c917f0cf5b3c571d8b447c6fc3177613a7d"
NASA_ARCHIVE = "https://exoplanetarchive.ipac.caltech.edu/"
NASA_TAP_DOCS = "https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html"
SNAPSHOT_DATE = "2023-05-13"
HINGE_WIDTH = 0.16
X_REFERENCE = math.log(10.0)
RNG_SEED = 20260814


@dataclass(frozen=True)
class PlanetData:
    frame: pd.DataFrame
    x: np.ndarray
    y: np.ndarray
    sigma_x: np.ndarray
    sigma_y: np.ndarray
    original_rows: int


@dataclass(frozen=True)
class ModelFit:
    model: str
    parameters: np.ndarray
    parameter_names: tuple[str, ...]
    nll: float
    n: int
    k: int
    aicc: float
    bic: float
    rmse_log_radius: float
    median_absolute_fractional_error: float
    singular_values_normalized: tuple[float, ...]
    spectral_condition: float


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_planets(path: Path) -> PlanetData:
    raw = pd.read_csv(path, low_memory=False)
    required = [
        "pl_name",
        "hostname",
        "disc_year",
        "tran_flag",
        "pl_rade",
        "pl_radeerr1",
        "pl_radeerr2",
        "pl_radelim",
        "pl_bmasse",
        "pl_bmasseerr1",
        "pl_bmasseerr2",
        "pl_bmasselim",
        "pl_bmassprov",
        "pl_bmasse_reflink",
        "pl_rade_reflink",
    ]
    missing = sorted(set(required) - set(raw.columns))
    if missing:
        raise ValueError(f"Faltan columnas: {missing}")

    finite_columns = [
        "pl_rade",
        "pl_radeerr1",
        "pl_radeerr2",
        "pl_bmasse",
        "pl_bmasseerr1",
        "pl_bmasseerr2",
    ]
    frame = raw.dropna(subset=finite_columns).copy()
    frame = frame[
        (frame["tran_flag"] == 1)
        & (frame["pl_bmassprov"] == "Mass")
        & (frame["pl_radelim"].fillna(1) == 0)
        & (frame["pl_bmasselim"].fillna(1) == 0)
        & (frame["pl_rade"] > 0)
        & (frame["pl_bmasse"] > 0)
    ].copy()

    radius_error_max = np.maximum(
        frame["pl_radeerr1"].abs(), frame["pl_radeerr2"].abs()
    )
    mass_error_max = np.maximum(
        frame["pl_bmasseerr1"].abs(), frame["pl_bmasseerr2"].abs()
    )
    frame = frame[
        (radius_error_max / frame["pl_rade"] <= 0.20)
        & (mass_error_max / frame["pl_bmasse"] <= 0.50)
    ].copy()
    frame = frame.sort_values("pl_bmasse").reset_index(drop=True)

    radius_error = 0.5 * (
        frame["pl_radeerr1"].abs().to_numpy()
        + frame["pl_radeerr2"].abs().to_numpy()
    )
    mass_error = 0.5 * (
        frame["pl_bmasseerr1"].abs().to_numpy()
        + frame["pl_bmasseerr2"].abs().to_numpy()
    )
    radius = frame["pl_rade"].to_numpy(dtype=float)
    mass = frame["pl_bmasse"].to_numpy(dtype=float)
    return PlanetData(
        frame=frame,
        x=np.log(mass),
        y=np.log(radius),
        sigma_x=mass_error / mass,
        sigma_y=radius_error / radius,
        original_rows=len(raw),
    )


def smooth_hinge(value: np.ndarray) -> np.ndarray:
    return HINGE_WIDTH * np.logaddexp(0.0, value / HINGE_WIDTH)


def sigmoid(value: np.ndarray) -> np.ndarray:
    clipped = np.clip(value, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def parameterization(model: str) -> tuple[tuple[str, ...], list[tuple[float, float]]]:
    if model == "single":
        return ("a", "b", "log_sigma_int"), [(-2.0, 4.0), (-1.0, 1.5), (-6.0, 1.0)]
    if model == "quadratic":
        return (
            "a",
            "b",
            "c",
            "log_sigma_int",
        ), [(-2.0, 4.0), (-1.0, 1.5), (-0.5, 0.5), (-6.0, 1.0)]
    if model == "multiscale":
        return (
            "a",
            "b1",
            "b2",
            "b3",
            "ln_M_break1",
            "ln_M_break2",
            "log_sigma_int",
        ), [
            (-2.0, 4.0),
            (-1.0, 1.5),
            (-1.0, 1.5),
            (-1.0, 1.5),
            (math.log(0.3), math.log(80.0)),
            (math.log(8.0), math.log(3000.0)),
            (-6.0, 1.0),
        ]
    raise ValueError(model)


def mean_and_slope(
    model: str, parameters: np.ndarray, x: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    if model == "single":
        a, b, _ = parameters
        return a + b * (x - X_REFERENCE), np.full_like(x, b)
    if model == "quadratic":
        a, b, c, _ = parameters
        centered = x - X_REFERENCE
        return a + b * centered + c * centered**2, b + 2.0 * c * centered
    if model == "multiscale":
        a, b1, b2, b3, break1, break2, _ = parameters
        if break2 <= break1 + 0.35:
            return np.full_like(x, np.nan), np.full_like(x, np.nan)
        h1 = smooth_hinge(x - break1) - smooth_hinge(
            np.asarray(X_REFERENCE - break1)
        )
        h2 = smooth_hinge(x - break2) - smooth_hinge(
            np.asarray(X_REFERENCE - break2)
        )
        mean = a + b1 * (x - X_REFERENCE) + (b2 - b1) * h1 + (b3 - b2) * h2
        slope = (
            b1
            + (b2 - b1) * sigmoid((x - break1) / HINGE_WIDTH)
            + (b3 - b2) * sigmoid((x - break2) / HINGE_WIDTH)
        )
        return mean, slope
    raise ValueError(model)


def negative_log_likelihood(
    model: str,
    parameters: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    sigma_x: np.ndarray,
    sigma_y: np.ndarray,
) -> float:
    mean, slope = mean_and_slope(model, parameters, x)
    if not np.all(np.isfinite(mean)):
        return 1e100
    intrinsic = math.exp(float(parameters[-1]))
    variance = sigma_y**2 + slope**2 * sigma_x**2 + intrinsic**2
    if np.any(variance <= 0.0) or not np.all(np.isfinite(variance)):
        return 1e100
    residual = y - mean
    return float(0.5 * np.sum(residual**2 / variance + np.log(2.0 * np.pi * variance)))


def initial_points(model: str, x: np.ndarray, y: np.ndarray) -> list[np.ndarray]:
    linear = np.polyfit(x - X_REFERENCE, y, 1)
    a = float(linear[1])
    b = float(linear[0])
    scatter = float(np.log(max(np.std(y - (a + b * (x - X_REFERENCE))), 0.02)))
    if model == "single":
        return [np.array([a, b, scatter])]
    if model == "quadratic":
        polynomial = np.polyfit(x - X_REFERENCE, y, 2)
        base = np.array([polynomial[2], polynomial[1], polynomial[0], scatter])
        return [base, np.array([a, b, 0.0, scatter])]

    starts = []
    configurations = [
        (2.0, 100.0, 0.28, 0.55, 0.02),
        (5.0, 100.0, 0.30, 0.45, 0.00),
        (10.0, 300.0, 0.35, 0.30, -0.02),
        (20.0, 500.0, 0.40, 0.15, 0.02),
        (2.0, 300.0, 0.20, 0.55, -0.02),
        (30.0, 1000.0, 0.45, 0.05, 0.00),
    ]
    for mass1, mass2, b1, b2, b3 in configurations:
        starts.append(
            np.array([a, b1, b2, b3, math.log(mass1), math.log(mass2), scatter])
        )
    return starts


def fit_parameters(
    model: str,
    data: PlanetData,
    indices: np.ndarray,
) -> np.ndarray:
    names, bounds = parameterization(model)
    x = data.x[indices]
    y = data.y[indices]
    sx = data.sigma_x[indices]
    sy = data.sigma_y[indices]

    def objective(parameters: np.ndarray) -> float:
        return negative_log_likelihood(model, parameters, x, y, sx, sy)

    candidates = []
    for start in initial_points(model, x, y):
        clipped = np.array(
            [np.clip(value, low, high) for value, (low, high) in zip(start, bounds)]
        )
        candidates.append(
            minimize(
                objective,
                clipped,
                method="L-BFGS-B",
                bounds=bounds,
                options={
                    "maxiter": 2000,
                    "ftol": 1e-12,
                    "gtol": 1e-7,
                    "maxls": 60,
                    "eps": 1e-6,
                },
            )
        )
    finite = [candidate for candidate in candidates if np.isfinite(candidate.fun)]
    if not finite:
        raise RuntimeError(f"No hubo solucion finita para {model}")
    return np.asarray(min(finite, key=lambda item: item.fun).x)


def spectral_diagnostics(
    model: str,
    parameters: np.ndarray,
    data: PlanetData,
    indices: np.ndarray,
) -> tuple[tuple[float, ...], float]:
    mean, slope = mean_and_slope(model, parameters, data.x[indices])
    intrinsic = math.exp(float(parameters[-1]))
    variance = (
        data.sigma_y[indices] ** 2
        + slope**2 * data.sigma_x[indices] ** 2
        + intrinsic**2
    )
    mean_parameter_count = len(parameters) - 1
    columns = []
    for column in range(mean_parameter_count):
        step = 1e-4 * max(1.0, abs(float(parameters[column])))
        plus = parameters.copy()
        minus = parameters.copy()
        plus[column] += step
        minus[column] -= step
        y_plus, _ = mean_and_slope(model, plus, data.x[indices])
        y_minus, _ = mean_and_slope(model, minus, data.x[indices])
        columns.append((y_plus - y_minus) / (2.0 * step) / np.sqrt(variance))
    operator = np.column_stack(columns)
    norms = np.linalg.norm(operator, axis=0)
    normalized = operator / norms
    singular = np.linalg.svd(normalized, compute_uv=False)
    positive = singular[singular > 1e-12]
    return tuple(float(value) for value in singular), float(positive[0] / positive[-1])


def score_fit(
    model: str,
    parameters: np.ndarray,
    data: PlanetData,
    indices: np.ndarray,
) -> ModelFit:
    names, _ = parameterization(model)
    x = data.x[indices]
    y = data.y[indices]
    nll = negative_log_likelihood(
        model, parameters, x, y, data.sigma_x[indices], data.sigma_y[indices]
    )
    mean, _ = mean_and_slope(model, parameters, x)
    residual = y - mean
    k = len(parameters)
    n = len(indices)
    aic = 2.0 * nll + 2.0 * k
    aicc = aic + 2.0 * k * (k + 1.0) / (n - k - 1.0)
    bic = 2.0 * nll + k * math.log(n)
    singular, condition = spectral_diagnostics(model, parameters, data, indices)
    return ModelFit(
        model=model,
        parameters=parameters,
        parameter_names=names,
        nll=float(nll),
        n=n,
        k=k,
        aicc=float(aicc),
        bic=float(bic),
        rmse_log_radius=float(np.sqrt(np.mean(residual**2))),
        median_absolute_fractional_error=float(np.median(np.abs(np.exp(residual) - 1.0))),
        singular_values_normalized=singular,
        spectral_condition=condition,
    )


def split_indices(n: int) -> tuple[np.ndarray, np.ndarray]:
    all_indices = np.arange(n)
    holdout = all_indices[::5]
    train = np.setdiff1d(all_indices, holdout, assume_unique=True)
    return train, holdout


def serialize_fit(fit: ModelFit) -> dict:
    values = {
        name: float(value)
        for name, value in zip(fit.parameter_names, fit.parameters)
    }
    if fit.model == "multiscale":
        values["M_break1_Earth"] = float(math.exp(values["ln_M_break1"]))
        values["M_break2_Earth"] = float(math.exp(values["ln_M_break2"]))
    return {
        "model": fit.model,
        "parameters": values,
        "NLL": fit.nll,
        "n": fit.n,
        "k": fit.k,
        "AICc": fit.aicc,
        "BIC": fit.bic,
        "RMSE_lnR": fit.rmse_log_radius,
        "median_absolute_fractional_error": fit.median_absolute_fractional_error,
        "normalized_operator_singular_values": fit.singular_values_normalized,
        "spectral_condition_number": fit.spectral_condition,
    }


def five_fold_cross_validation(
    models: tuple[str, ...], data: PlanetData
) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    n = len(data.frame)
    all_indices = np.arange(n)
    fold_details: dict[str, list[dict]] = {model: [] for model in models}
    residuals: dict[str, list[np.ndarray]] = {model: [] for model in models}
    total_nll = {model: 0.0 for model in models}
    total_count = {model: 0 for model in models}

    for fold in range(5):
        test = all_indices[fold::5]
        train = np.setdiff1d(all_indices, test, assume_unique=True)
        for model in models:
            parameters = fit_parameters(model, data, train)
            score = score_fit(model, parameters, data, test)
            mean, _ = mean_and_slope(model, parameters, data.x[test])
            residual = data.y[test] - mean
            residuals[model].append(residual)
            total_nll[model] += score.nll
            total_count[model] += len(test)
            values = {
                name: float(value)
                for name, value in zip(score.parameter_names, parameters)
            }
            if model == "multiscale":
                values["M_break1_Earth"] = float(math.exp(values["ln_M_break1"]))
                values["M_break2_Earth"] = float(math.exp(values["ln_M_break2"]))
            fold_details[model].append(
                {
                    "fold": fold,
                    "train_n": int(len(train)),
                    "test_n": int(len(test)),
                    "test_NLL": float(score.nll),
                    "test_RMSE_lnR": float(score.rmse_log_radius),
                    "test_median_fractional_error": float(
                        score.median_absolute_fractional_error
                    ),
                    "train_parameters": values,
                }
            )

    summary = {}
    for model in models:
        combined = np.concatenate(residuals[model])
        entry = {
            "folds": 5,
            "predicted_planets_once_each": int(total_count[model]),
            "total_test_NLL": float(total_nll[model]),
            "test_NLL_per_planet": float(total_nll[model] / total_count[model]),
            "pooled_RMSE_lnR": float(np.sqrt(np.mean(combined**2))),
            "pooled_median_fractional_error": float(
                np.median(np.abs(np.exp(combined) - 1.0))
            ),
            "fold_test_NLL": [float(item["test_NLL"]) for item in fold_details[model]],
        }
        if model == "multiscale":
            break1 = np.array(
                [item["train_parameters"]["M_break1_Earth"] for item in fold_details[model]]
            )
            break2 = np.array(
                [item["train_parameters"]["M_break2_Earth"] for item in fold_details[model]]
            )
            entry.update(
                {
                    "M_break1_mean_Earth": float(break1.mean()),
                    "M_break1_sd_across_folds_Earth": float(break1.std(ddof=1)),
                    "M_break2_mean_Earth": float(break2.mean()),
                    "M_break2_sd_across_folds_Earth": float(break2.std(ddof=1)),
                }
            )
        summary[model] = entry
    return summary, fold_details


def make_figure(
    path: Path,
    data: PlanetData,
    train: np.ndarray,
    holdout: np.ndarray,
    full_fits: dict[str, ModelFit],
    cross_validation: dict[str, dict],
) -> None:
    colors = {"single": "#374151", "quadratic": "#0072B2", "multiscale": "#C23B22"}
    labels = {"single": "Potencia única", "quadratic": "Cuadrático suave", "multiscale": "Multiescala"}
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.8))
    ax_a, ax_b, ax_c, ax_d = axes.ravel()
    mass = np.exp(data.x)
    radius = np.exp(data.y)
    ax_a.scatter(mass[train], radius[train], s=15, alpha=0.28, color="#64748b", label="Entrenamiento")
    ax_a.scatter(
        mass[holdout],
        radius[holdout],
        s=31,
        facecolors="none",
        edgecolors="#111827",
        linewidths=0.8,
        alpha=0.7,
        label="Prueba reservada",
    )
    mass_grid = np.geomspace(mass.min() * 0.9, mass.max() * 1.1, 800)
    x_grid = np.log(mass_grid)
    for model in ("single", "quadratic", "multiscale"):
        mean, _ = mean_and_slope(model, full_fits[model].parameters, x_grid)
        ax_a.plot(mass_grid, np.exp(mean), color=colors[model], lw=2.2, label=labels[model])
    multiscale_parameters = dict(
        zip(full_fits["multiscale"].parameter_names, full_fits["multiscale"].parameters)
    )
    for key in ("ln_M_break1", "ln_M_break2"):
        ax_a.axvline(math.exp(multiscale_parameters[key]), color=colors["multiscale"], ls=":", lw=1.2)
    ax_a.set_xscale("log")
    ax_a.set_yscale("log")
    ax_a.set_xlabel(r"Masa [$M_\oplus$]")
    ax_a.set_ylabel(r"Radio [$R_\oplus$]")
    ax_a.set_title("A. Relación masa-radio observada")
    ax_a.legend(frameon=False, fontsize=8.8, ncol=2)
    ax_a.grid(alpha=0.16, which="both")

    for model in ("single", "quadratic", "multiscale"):
        _, local_slope = mean_and_slope(model, full_fits[model].parameters, x_grid)
        ax_b.plot(mass_grid, local_slope, color=colors[model], lw=2.25, label=labels[model])
    ax_b.axhline(0.0, color="#64748b", ls="--", lw=1.0)
    ax_b.set_xscale("log")
    ax_b.set_xlabel(r"Masa [$M_\oplus$]")
    ax_b.set_ylabel(r"Exponente local $d\ln R/d\ln M$")
    ax_b.set_title("B. Exponente inferido por escala")
    ax_b.legend(frameon=False, fontsize=9)
    ax_b.grid(alpha=0.16, which="both")

    order = ["single", "quadratic", "multiscale"]
    xbars = np.arange(3)
    nll_per_object = [cross_validation[name]["test_NLL_per_planet"] for name in order]
    ax_c.bar(xbars, nll_per_object, color=[colors[name] for name in order], width=0.62)
    ax_c.set_xticks(xbars, [labels[name] for name in order])
    ax_c.set_ylabel("NLL cruzada por planeta")
    ax_c.set_title("C. Predicción fuera de muestra (5 pliegues)")
    ax_c.grid(axis="y", alpha=0.18)

    baseline = full_fits["single"]
    delta_aicc = [full_fits[name].aicc - baseline.aicc for name in order]
    delta_bic = [full_fits[name].bic - baseline.bic for name in order]
    width = 0.34
    ax_d.bar(xbars - width / 2, delta_aicc, width, color="#4C78A8", label=r"$\Delta$AICc")
    ax_d.bar(xbars + width / 2, delta_bic, width, color="#F2A541", label=r"$\Delta$BIC")
    ax_d.axhline(0.0, color="#111827", lw=1.0)
    ax_d.set_xticks(xbars, [labels[name] for name in order])
    ax_d.set_ylabel("Diferencia frente a potencia única")
    ax_d.set_title("D. Explicación penalizada por complejidad")
    ax_d.legend(frameon=False, fontsize=9)
    ax_d.grid(axis="y", alpha=0.18)

    fig.suptitle(
        "Demostración empírica de capacidad explicativa multiescala",
        fontsize=16,
        fontweight="bold",
        y=0.985,
    )
    caption = (
        f"Figura 2. Relación masa-radio para {len(data.frame)} exoplanetas transitantes de una instantánea "
        f"del NASA Exoplanet Archive ({SNAPSHOT_DATE}); se exigieron masa física, radio, sin límites y errores "
        "relativos <=50 % en masa y <=20 % en radio. Cada planeta fue predicho una vez mediante validación "
        "cruzada de cinco pliegues estratificados por masa. "
        "El ajuste usa verosimilitud con errores en ambos ejes y dispersión intrínseca. Las fronteras verticales "
        "son inferidas, no impuestas. Esto demuestra capacidad descriptiva/predictiva del operador por regímenes "
        "en este problema; no demuestra que el marco sea una ley fundamental ni que las fronteras sean universales."
    )
    fig.text(0.052, 0.018, caption, ha="left", va="bottom", fontsize=9.1, wrap=True)
    fig.tight_layout(rect=(0.04, 0.108, 0.98, 0.955), h_pad=2.2, w_pad=2.0)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def run(snapshot: Path, output_dir: Path) -> dict:
    data = load_planets(snapshot)
    train, holdout = split_indices(len(data.frame))
    full = np.arange(len(data.frame))
    models = ("single", "quadratic", "multiscale")

    full_fits = {}
    for model in models:
        parameters_full = fit_parameters(model, data, full)
        full_fits[model] = score_fit(model, parameters_full, data, full)
    cross_validation, fold_details = five_fold_cross_validation(models, data)

    selected_path = output_dir / "exoplanetas_masa_radio_seleccion.csv"
    export = data.frame.copy()
    export["split"] = "train"
    export.loc[holdout, "split"] = "holdout"
    export.to_csv(selected_path, index=False)

    table_rows = []
    for model in models:
        full_fit = full_fits[model]
        cv = cross_validation[model]
        row = {
            "model": model,
            "n_full": full_fit.n,
            "k": full_fit.k,
            "NLL_full": full_fit.nll,
            "AICc_full": full_fit.aicc,
            "BIC_full": full_fit.bic,
            "NLL_cross_validated": cv["total_test_NLL"],
            "NLL_cross_validated_per_planet": cv["test_NLL_per_planet"],
            "RMSE_lnR_cross_validated": cv["pooled_RMSE_lnR"],
            "median_fractional_error_cross_validated": cv[
                "pooled_median_fractional_error"
            ],
            "spectral_condition_full": full_fit.spectral_condition,
        }
        row.update(
            {
                name: float(value)
                for name, value in zip(full_fit.parameter_names, full_fit.parameters)
            }
        )
        table_rows.append(row)
    table_path = output_dir / "demostracion_exoplanetas_ajustes.csv"
    pd.DataFrame(table_rows).to_csv(table_path, index=False)

    figure_path = output_dir / "figura_demostracion_exoplanetas_multiescala.png"
    make_figure(figure_path, data, train, holdout, full_fits, cross_validation)

    ms = full_fits["multiscale"]
    baseline = full_fits["single"]
    smooth = full_fits["quadratic"]
    holdout_best = min(
        models, key=lambda name: cross_validation[name]["total_test_NLL"]
    )
    pass_criterion = bool(
        ms.bic < min(baseline.bic, smooth.bic) - 10.0
        and holdout_best == "multiscale"
    )
    if pass_criterion:
        statement = (
            "La ley multiescala supera a la potencia unica y al polinomio suave con "
            "evidencia BIC fuerte y la mejor verosimilitud fuera de muestra."
        )
    else:
        statement = (
            "La ley multiescala no supera simultaneamente BIC y prediccion reservada; "
            "esta muestra no demuestra capacidad explicativa adicional."
        )

    result = {
        "status": "completed",
        "scope": (
            "Capacidad explicativa de una ley por regimenes para la relacion masa-radio. "
            "No es una validacion de unificacion fisica fundamental."
        ),
        "source": {
            "NASA_archive": NASA_ARCHIVE,
            "NASA_TAP_documentation": NASA_TAP_DOCS,
            "mirror_repository": MIRROR_REPOSITORY,
            "mirror_commit": MIRROR_COMMIT,
            "mirror_blob": MIRROR_BLOB,
            "snapshot_date": SNAPSHOT_DATE,
            "local_sha256": sha256(snapshot),
            "rows_in_snapshot": data.original_rows,
        },
        "selection": {
            "transiting": True,
            "mass_provenance": "Mass",
            "limit_flags": 0,
            "max_relative_mass_error": 0.50,
            "max_relative_radius_error": 0.20,
            "selected_planets": len(data.frame),
            "train_planets": len(train),
            "holdout_planets": len(holdout),
            "split_rule": (
                "Cinco pliegues: indices 0::5, 1::5, ..., tras ordenar por masa; "
                "cada planeta es prueba exactamente una vez"
            ),
        },
        "models": {
            "single": "ln R = a + b(ln M - ln 10)",
            "quadratic": "ln R = a + b x_c + c x_c^2",
            "multiscale": (
                "Ley continua de tres exponentes locales con dos bisagras suaves "
                "inferidas; ancho fijo Delta ln M = 0.16"
            ),
        },
        "criterion": (
            "BIC multiescala al menos 10 unidades menor que ambos competidores y "
            "menor NLL acumulada en validacion cruzada de cinco pliegues"
        ),
        "full_fit": {model: serialize_fit(full_fits[model]) for model in models},
        "five_fold_cross_validation": cross_validation,
        "cross_validation_fold_details": fold_details,
        "verdict": {
            "criterion_passed": pass_criterion,
            "holdout_best_model": holdout_best,
            "cross_validation_best_model": holdout_best,
            "delta_BIC_multiscale_minus_single": float(ms.bic - baseline.bic),
            "delta_BIC_multiscale_minus_quadratic": float(ms.bic - smooth.bic),
            "statement": statement,
        },
        "outputs": {
            "figure": str(figure_path.resolve()),
            "selected_data": str(selected_path.resolve()),
            "fit_table": str(table_path.resolve()),
        },
    }
    result_path = output_dir / "demostracion_exoplanetas_resultados.json"
    result["outputs"]["json"] = str(result_path.resolve())
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prueba multiescala de la relacion masa-radio exoplanetaria."
    )
    base = Path(__file__).resolve().parent
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=base / "data" / "nasa_exoplanet_archive_snapshot_2023-05-13.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=base)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = run(args.snapshot, args.output_dir)
    print(json.dumps(result["verdict"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
