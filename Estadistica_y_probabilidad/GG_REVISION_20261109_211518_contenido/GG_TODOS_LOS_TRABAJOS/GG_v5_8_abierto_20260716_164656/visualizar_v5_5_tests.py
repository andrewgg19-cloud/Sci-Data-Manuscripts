#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualizador German-Gamma v5.5.

Genera figuras de la bateria de pruebas:

    py -3 visualizar_v5_5_tests.py

Entradas:
    v5_5_test_run/resumen_v5_5_tests.csv

Salidas:
    v5_5_test_run/figuras/*.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RUN = Path("v5_5_test_run")
OUT = RUN / "figuras"


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def short_label(text: str) -> str:
    return (
        text.replace("_horizonte_espejo", "")
        .replace("_topologia", "")
        .replace("big_bell", "BIG Bell")
        .replace("geometric", "Geom")
        .replace("control", "Control")
        .replace("ring_broken", "Ring Broken")
    )


def save(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_horizonte(df: pd.DataFrame) -> None:
    d = df[df["tipo"] == "horizonte_espejo"].copy()
    d["C_H_JS"] = numeric(d["C_H_JS"])
    d["L1"] = numeric(d["L1"])
    labels = [short_label(x) for x in d["prueba"]]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    x = np.arange(len(d))
    ax.bar(x, d["C_H_JS"], color=["#6b7280", "#b45309", "#2563eb"], width=0.62)
    ax.axhline(0.02, color="#64748b", linestyle="--", linewidth=1, label="leve")
    ax.axhline(0.10, color="#f59e0b", linestyle="--", linewidth=1, label="moderada")
    ax.axhline(0.25, color="#dc2626", linestyle="--", linewidth=1, label="fuerte")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0)
    ax.set_ylabel("C_H Jensen-Shannon")
    ax.set_title("German-Gamma v5.5: no conmutatividad horizonte-espejo")
    ax.legend(frameon=False, ncols=3, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "01_horizonte_espejo_CH.png")


def plot_topologia(df: pd.DataFrame) -> None:
    d = df[df["tipo"] == "topologia"].copy()
    d["p_bottleneck_H1"] = numeric(d["p_bottleneck_H1"])
    d["delta_H0"] = numeric(d["delta_H0"])
    labels = [short_label(x) for x in d["prueba"]]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    x = np.arange(len(d))
    axes[0].bar(x, d["p_bottleneck_H1"], color="#2563eb", width=0.62)
    axes[0].axhline(0.05, color="#dc2626", linestyle="--", linewidth=1, label="0.05")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=20, ha="right")
    axes[0].set_ylabel("p bottleneck H1")
    axes[0].set_title("Ruptura topologica H1")
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=0.25)

    colors = ["#6b7280" if v >= -50 else "#b45309" for v in d["delta_H0"]]
    axes[1].bar(x, d["delta_H0"], color=colors, width=0.62)
    axes[1].axhline(-50, color="#dc2626", linestyle="--", linewidth=1, label="alerta H0")
    axes[1].axhline(0, color="#111827", linewidth=0.8)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=20, ha="right")
    axes[1].set_ylabel("Delta H0")
    axes[1].set_title("Deformacion geometrica H0")
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y", alpha=0.25)

    save(fig, "02_topologia_H0_H1.png")


def plot_supervivencia(df: pd.DataFrame) -> None:
    d = df.copy()
    d["tasa"] = numeric(d["tasa"])
    labels = [short_label(x) for x in d["prueba"]]
    colors = ["#64748b" if t == "horizonte_espejo" else "#0f766e" for t in d["tipo"]]

    fig, ax = plt.subplots(figsize=(11, 4.8))
    x = np.arange(len(d))
    ax.bar(x, d["tasa"], color=colors, width=0.65)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Tasa")
    ax.set_title("Tasa de horizonte / supervivencia por prueba")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "03_tasa_supervivencia.png")


def plot_lamina(df: pd.DataFrame) -> None:
    """Lamina compacta: filas=pruebas, columnas=metricas normalizadas."""

    d = df.copy()
    d["C_H_JS"] = numeric(d["C_H_JS"]).fillna(0)
    d["p_bottleneck_H1"] = numeric(d["p_bottleneck_H1"])
    d["delta_H0"] = numeric(d["delta_H0"])
    d["costo_bits"] = numeric(d["costo_bits"]).fillna(0)

    # Convertimos a "intensidad de alerta" comparable.
    d["alerta_CH"] = np.clip(d["C_H_JS"] / 0.25, 0, 1)
    d["alerta_H1"] = np.where(d["p_bottleneck_H1"].notna(), np.clip((0.05 - d["p_bottleneck_H1"]) / 0.05, 0, 1), 0)
    d["alerta_H0"] = np.where(d["delta_H0"].notna(), np.clip(np.abs(d["delta_H0"]) / 100, 0, 1), 0)
    d["alerta_costo"] = np.clip(d["costo_bits"] / 2.0, 0, 1)

    mat = d[["alerta_CH", "alerta_H0", "alerta_H1", "alerta_costo"]].to_numpy()
    labels = [short_label(x) for x in d["prueba"]]
    cols = ["C_H", "H0", "H1", "costo"]

    fig, ax = plt.subplots(figsize=(8.8, 6.2))
    im = ax.imshow(mat, aspect="auto", cmap="magma", vmin=0, vmax=1)
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols)
    ax.set_title("Lamina v5.5: intensidad comparativa de senales")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", color="white" if mat[i, j] > 0.45 else "black")
    fig.colorbar(im, ax=ax, label="intensidad normalizada")
    save(fig, "04_lamina_intensidad.png")


def main() -> None:
    csv_path = RUN / "resumen_v5_5_tests.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe {csv_path}. Corre primero summarize_v5_5_tests.py")
    df = pd.read_csv(csv_path)

    plot_horizonte(df)
    plot_topologia(df)
    plot_supervivencia(df)
    plot_lamina(df)

    print(f"Figuras generadas en: {OUT.resolve()}")
    for path in sorted(OUT.glob("*.png")):
        print(path.resolve())


if __name__ == "__main__":
    main()
