#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualiza la prueba temporal real BIG Bell para German-Gamma v5.5."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DIR = Path("v5_5_big_bell_temporal")
IN_COUNTS = DIR / "big_bell_sombra_temporal.csv"
IN_RESULT = DIR / "big_bell_sombra_temporal_resultado.csv"
OUT = DIR / "figuras"


def save(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    counts = pd.read_csv(IN_COUNTS)
    res = pd.read_csv(IN_RESULT)
    df = counts.merge(res, on="ventana", how="inner")

    df["idx"] = np.arange(len(df))
    dg = pd.to_numeric(df["distancia_sombra_log"], errors="coerce")
    h = pd.to_numeric(df["entropia_expresada"], errors="coerce")
    df["D_G_clip"] = dg.clip(upper=2.0)
    df["D_G_raw"] = dg
    df["H"] = h
    df["total_aceptados"] = df[["n00", "n01", "n10", "n11"]].sum(axis=1)
    df["min_aceptados_celda"] = df[["n00", "n01", "n10", "n11"]].min(axis=1)
    if "soporte_estado" in df.columns:
        df["soporte_perdido"] = df["soporte_estado"] != "soporte_completo"
    else:
        df["soporte_perdido"] = df["min_aceptados_celda"] == 0
    df["critica"] = df["D_G_raw"] > 0.25
    df["confirmada"] = df["apelacion_temporal"] == "confirmada_por_persistencia"

    fig, ax = plt.subplots(figsize=(12, 4.8))
    colors = np.where(df["confirmada"], "#dc2626", np.where(df["critica"], "#f59e0b", "#2563eb"))
    ax.bar(df["idx"], df["D_G_clip"], color=colors, width=0.85)
    ax.axhline(0.25, color="#111827", linestyle="--", linewidth=1, label="D_G critico 0.25")
    ax.set_title("BIG Bell temporal v5.5: sombra geometrica por ventana (D_G recortado a 2)")
    ax.set_xlabel("ventana temporal")
    ax.set_ylabel("D_G")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "01_big_bell_DG_temporal.png")

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(df["idx"], df["H"], color="#0f766e", linewidth=1.8)
    ax.scatter(df.loc[df["soporte_perdido"], "idx"], df.loc[df["soporte_perdido"], "H"], color="#dc2626", s=18, label="perdida de soporte")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("BIG Bell temporal v5.5: entropia expresada")
    ax.set_xlabel("ventana temporal")
    ax.set_ylabel("H*")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "02_big_bell_entropia_temporal.png")

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(df["idx"], df["total_aceptados"], color="#7c3aed", linewidth=1.6)
    ax.scatter(df.loc[df["soporte_perdido"], "idx"], df.loc[df["soporte_perdido"], "total_aceptados"], color="#dc2626", s=18, label="celda con n_ab=0")
    ax.set_title("BIG Bell temporal v5.5: aceptados por ventana")
    ax.set_xlabel("ventana temporal")
    ax.set_ylabel("total aceptados Gamma=1")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    save(fig, "03_big_bell_aceptados_temporal.png")

    summary = {
        "ventanas": int(len(df)),
        "ventanas_criticas_DG_gt_0_25": int(df["critica"].sum()),
        "ventanas_confirmadas_por_persistencia": int(df["confirmada"].sum()),
        "ventanas_con_perdida_soporte_n_ab_0": int(df["soporte_perdido"].sum()),
        "D_G_mediana": float(df["D_G_raw"].median()),
        "D_G_max": float(df["D_G_raw"].max()),
        "H_mediana": float(df["H"].median()),
        "aceptados_mediana": float(df["total_aceptados"].median()),
    }
    lines = ["# BIG Bell Temporal v5.5 - Resumen", ""]
    for k, v in summary.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Lectura")
    lines.append("")
    lines.append("La serie temporal muestra episodios de sombra finita alta, pero varias ventanas tienen perdida de soporte por celdas aceptadas en cero.")
    lines.append("La regla v5.5.1 separa esas ventanas como perdida_de_soporte_expresado y no las cuenta como confirmacion temporal.")
    lines.append("Resultado: no hay confirmacion por persistencia tras excluir ventanas degeneradas del conteo de racha.")
    (DIR / "RESUMEN_BIG_BELL_TEMPORAL_V5_5.md").write_text("\n".join(lines), encoding="utf-8")

    print(DIR / "RESUMEN_BIG_BELL_TEMPORAL_V5_5.md")
    for p in sorted(OUT.glob("*.png")):
        print(p.resolve())


if __name__ == "__main__":
    main()
