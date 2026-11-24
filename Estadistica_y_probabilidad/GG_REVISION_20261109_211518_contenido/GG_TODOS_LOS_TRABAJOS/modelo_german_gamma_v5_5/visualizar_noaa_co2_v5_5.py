#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualiza prueba NOAA CO2 con German-Gamma v5.5."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


DIR = Path("v5_5_noaa_co2")
OUT = DIR / "figuras"


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(DIR / "noaa_co2_mlo_gamma_input.csv")
    h = json.loads((DIR / "noaa_co2_horizonte_espejo.json").read_text(encoding="utf-8"))
    hc = json.loads((DIR / "noaa_co2_horizonte_control.json").read_text(encoding="utf-8"))
    topo = json.loads((DIR / "noaa_co2_topologia.json").read_text(encoding="utf-8"))

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(df["decimal_date"], df["co2_average"], color="#2563eb", linewidth=1.4, label="CO2 average")
    ax.plot(df["decimal_date"], df["co2_roll_mean_12"], color="#dc2626", linewidth=1.2, label="rolling mean 12")
    ax.fill_between(
        df["decimal_date"],
        df["co2_average"],
        df["co2_roll_mean_12"],
        where=df["co2_average"] > df["co2_roll_mean_12"],
        color="#f59e0b",
        alpha=0.25,
        label="horizonte: CO2 > media movil",
    )
    ax.set_title("NOAA GML Mauna Loa CO2: serie y horizonte")
    ax.set_xlabel("ano decimal")
    ax.set_ylabel("ppm CO2")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    save(fig, "01_noaa_co2_horizonte.png")

    fig, ax = plt.subplots(figsize=(7, 4.8))
    labels = ["identidad", "CO2 > roll_mean"]
    vals = [hc["c_h_js"], h["c_h_js"]]
    ax.bar(labels, vals, color=["#64748b", "#b45309"], width=0.55)
    ax.axhline(0.02, color="#64748b", linestyle="--", linewidth=1)
    ax.axhline(0.10, color="#f59e0b", linestyle="--", linewidth=1)
    ax.axhline(0.25, color="#dc2626", linestyle="--", linewidth=1)
    ax.set_ylabel("C_H Jensen-Shannon")
    ax.set_title("NOAA CO2: no conmutatividad horizonte-espejo")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "02_noaa_co2_CH.png")

    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.bar(["delta_H0", "delta_H1", "p_H1"], [topo["delta_h0_persistente"], topo["delta_h1_persistente"], topo["p_valor_bottleneck_H1"]], color=["#0f766e", "#2563eb", "#7c3aed"])
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_title("NOAA CO2: resumen topologico exploratorio")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "03_noaa_co2_topologia.png")

    lines = [
        "# NOAA CO2 - German-Gamma v5.5",
        "",
        "Fuente oficial: NOAA GML Mauna Loa CO2 mensual.",
        "",
        "## Horizonte-Espejo",
        "",
        f"- Control identidad C_H: {hc['c_h_js']:.6f}",
        f"- Horizonte `co2_average > co2_roll_mean_12` C_H: {h['c_h_js']:.6f}",
        f"- Lectura: {h['lectura']}",
        "",
        "## Topologia Exploratoria",
        "",
        "- Nota: el filtro usado no es un filtro original NOAA; se deriva como `co2_anomaly > 0` para prueba exploratoria.",
        f"- N total: {topo['N_total']}",
        f"- N post: {topo['N_post']}",
        f"- tasa supervivencia: {topo['tasa_supervivencia']:.6f}",
        f"- costo bits: {topo['costo_seleccion_bits']:.6f}",
        f"- delta H0: {topo['delta_h0_persistente']}",
        f"- delta H1: {topo['delta_h1_persistente']}",
        f"- p bottleneck H1: {topo['p_valor_bottleneck_H1']:.6f}",
        "",
        "## Lectura",
        "",
        "La serie NOAA CO2 muestra no-conmutatividad fuerte bajo el horizonte `CO2 > media movil`, lo cual es esperable porque el horizonte separa una region asimetrica respecto al espejo centrado.",
        "La topologia exploratoria no muestra ruptura H1 significativa.",
        "Este resultado debe leerse como prueba de funcionamiento sobre datos NOAA reales, no como conclusion climatologica.",
    ]
    (DIR / "RESUMEN_NOAA_CO2_V5_5.md").write_text("\n".join(lines), encoding="utf-8")

    print(DIR / "RESUMEN_NOAA_CO2_V5_5.md")
    for p in sorted(OUT.glob("*.png")):
        print(p.resolve())


if __name__ == "__main__":
    main()
