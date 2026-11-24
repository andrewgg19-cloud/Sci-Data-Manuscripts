#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualiza NOAA CO2 temporal v5.5.1."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DIR = Path("v5_5_noaa_co2_temporal")
COUNTS = DIR / "noaa_co2_sombra_temporal_5y.csv"
RESULT = DIR / "noaa_co2_sombra_temporal_5y_resultado.csv"
OUT = DIR / "figuras"


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    counts = pd.read_csv(COUNTS)
    res = pd.read_csv(RESULT)
    df = counts.merge(res, on="ventana", how="inner")
    df["idx"] = np.arange(len(df))
    df["D_G_raw"] = pd.to_numeric(df["distancia_sombra_log"], errors="coerce")
    df["D_G_clip"] = df["D_G_raw"].clip(upper=2.0)
    df["H"] = pd.to_numeric(df["entropia_expresada"], errors="coerce")
    df["soporte_ok"] = df["soporte_estado"] == "soporte_completo"
    df["critica"] = (df["D_G_raw"] > 0.25) & df["soporte_ok"]

    colors = np.where(~df["soporte_ok"], "#dc2626", np.where(df["critica"], "#f59e0b", "#2563eb"))
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(df["idx"], df["D_G_clip"], color=colors, width=0.72)
    ax.axhline(0.25, color="#111827", linestyle="--", linewidth=1, label="D_G critico")
    ax.set_xticks(df["idx"])
    ax.set_xticklabels(df["ventana"], rotation=45, ha="right")
    ax.set_ylabel("D_G recortado a 2")
    ax.set_title("NOAA CO2 temporal 5y: sombra y soporte")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "01_noaa_temporal_DG_5y.png")

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(df["idx"], df["H"], color="#0f766e", linewidth=1.8)
    ax.scatter(df.loc[~df["soporte_ok"], "idx"], df.loc[~df["soporte_ok"], "H"], color="#dc2626", s=28, label="soporte no completo")
    ax.set_xticks(df["idx"])
    ax.set_xticklabels(df["ventana"], rotation=45, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("H*")
    ax.set_title("NOAA CO2 temporal 5y: entropia expresada")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    save(fig, "02_noaa_temporal_entropia_5y.png")

    soporte_counts = df["soporte_estado"].value_counts().to_dict()
    lines = ["# NOAA CO2 Temporal v5.5.1 - Resumen", ""]
    lines.append("Definicion exploratoria corregida:")
    lines.append("")
    lines.append("```text")
    lines.append("a = mes Apr-Sep")
    lines.append("b = co2_delta > 0")
    lines.append("Gamma = co2_average > co2_deseasonalized")
    lines.append("ventana = bloque de 5 anos")
    lines.append("```")
    lines.append("")
    lines.append(f"- ventanas: {len(df)}")
    lines.append(f"- soporte_completo: {int(soporte_counts.get('soporte_completo', 0))}")
    lines.append(f"- perdida_soporte_expresado: {int(soporte_counts.get('perdida_soporte_expresado', 0))}")
    lines.append(f"- no_evaluable_soporte_total: {int(soporte_counts.get('no_evaluable_soporte_total', 0))}")
    lines.append(f"- ventanas criticas evaluables: {int(df['critica'].sum())}")
    lines.append(f"- confirmadas por persistencia: {int((df['apelacion_temporal'] == 'confirmada_por_persistencia').sum())}")
    lines.append(f"- H mediana: {float(df['H'].median()):.6f}")
    finite = df.loc[df["soporte_ok"], "D_G_raw"].dropna()
    lines.append(f"- D_G mediana evaluable: {float(finite.median()) if len(finite) else float('nan'):.6f}")
    lines.append("")
    lines.append("## Lectura")
    lines.append("")
    lines.append("La prueba temporal NOAA no produce una sombra finita persistente limpia.")
    lines.append("La senal dominante es perdida de soporte expresado en muchas ventanas de 5 anos, causada por la estructura estacional de la regla Gamma exploratoria.")
    lines.append("Esto prueba que German-Gamma separa soporte perdido de sombra finita y evita confirmar una deformacion persistente cuando la base local es degenerada.")
    lines.append("")
    lines.append("No es una conclusion climatologica; es una prueba metodologica sobre datos NOAA reales.")
    (DIR / "RESUMEN_NOAA_TEMPORAL_V5_5_1.md").write_text("\n".join(lines), encoding="utf-8")

    print(DIR / "RESUMEN_NOAA_TEMPORAL_V5_5_1.md")
    for p in sorted(OUT.glob("*.png")):
        print(p.resolve())


if __name__ == "__main__":
    main()
