#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye ventanas temporales NOAA CO2 para German-Gamma v5.5.

Entrada:
    v5_5_noaa_co2/noaa_co2_mlo_gamma_input.csv

Salida:
    v5_5_noaa_co2_temporal/noaa_co2_sombra_temporal.csv

Definicion 2x2 exploratoria:
    a = 1 si co2_average > co2_roll_mean_12
    b = 1 si co2_delta > 0
    Gamma = 1 si co2_anomaly > 0

Ventana:
    year

Nota:
    Gamma es derivado para prueba metodologica; no es un filtro original NOAA.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT = Path("v5_5_noaa_co2/noaa_co2_mlo_gamma_input.csv")
OUT_DIR = Path("v5_5_noaa_co2_temporal")
OUT_CSV = OUT_DIR / "noaa_co2_sombra_temporal.csv"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(INPUT)
    required = ["year", "co2_average", "co2_roll_mean_12", "co2_delta", "co2_anomaly"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    df = df.dropna(subset=required).copy()
    df["a"] = (df["co2_average"] > df["co2_roll_mean_12"]).astype(int)
    df["b"] = (df["co2_delta"] > 0).astype(int)
    df["gamma"] = (df["co2_anomaly"] > 0).astype(int)

    rows = []
    for year, g in df.groupby("year"):
        row = {"ventana": str(int(year)), "year": int(year)}
        for a in [0, 1]:
            for b in [0, 1]:
                cell = g[(g["a"] == a) & (g["b"] == b)]
                key = f"{a}{b}"
                row[f"N{key}"] = int(len(cell))
                row[f"n{key}"] = int(cell["gamma"].sum())
        rows.append(
            {
                "ventana": row["ventana"],
                "year": row["year"],
                "n00": row["n00"],
                "N00": row["N00"],
                "n01": row["n01"],
                "N01": row["N01"],
                "n10": row["n10"],
                "N10": row["N10"],
                "n11": row["n11"],
                "N11": row["N11"],
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False)
    print(f"Entrada: {INPUT.resolve()}")
    print(f"Temporal NOAA: {OUT_CSV.resolve()}")
    print(f"Ventanas anuales: {len(out)}")
    print(out.head().to_string(index=False))


if __name__ == "__main__":
    main()
