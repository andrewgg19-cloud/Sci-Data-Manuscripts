#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye prueba temporal NOAA CO2 v5.5.1 no tautologica.

Entrada:
    v5_5_noaa_co2/noaa_co2_mlo_gamma_input.csv

Salida:
    v5_5_noaa_co2_temporal/noaa_co2_sombra_temporal_5y.csv

Definicion 2x2 exploratoria corregida:
    a = 1 si el mes esta en la mitad alta estacional: Apr-Sep
    b = 1 si co2_delta > 0
    Gamma = 1 si co2_average > co2_deseasonalized

Ventana:
    bloques no solapados de 5 anos.

Nota:
    Esta es una prueba metodologica con datos NOAA reales. Gamma no es un
    filtro declarado por NOAA; representa una expresion estacional positiva
    respecto al valor desestacionalizado.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT = Path("v5_5_noaa_co2/noaa_co2_mlo_gamma_input.csv")
OUT_DIR = Path("v5_5_noaa_co2_temporal")
OUT_CSV = OUT_DIR / "noaa_co2_sombra_temporal_5y.csv"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(INPUT)
    required = ["year", "month", "co2_average", "co2_deseasonalized", "co2_delta"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    df = df.dropna(subset=required).copy()
    first_year = int(df["year"].min())
    df["block_start"] = first_year + ((df["year"] - first_year) // 5) * 5
    df["a"] = df["month"].between(4, 9).astype(int)
    df["b"] = (df["co2_delta"] > 0).astype(int)
    df["gamma"] = (df["co2_average"] > df["co2_deseasonalized"]).astype(int)

    rows = []
    for block_start, g in df.groupby("block_start"):
        block_end = int(block_start) + 4
        row = {"ventana": f"{int(block_start)}-{block_end}", "block_start": int(block_start), "block_end": block_end}
        for a in [0, 1]:
            for b in [0, 1]:
                cell = g[(g["a"] == a) & (g["b"] == b)]
                key = f"{a}{b}"
                row[f"N{key}"] = int(len(cell))
                row[f"n{key}"] = int(cell["gamma"].sum())
        rows.append(
            {
                "ventana": row["ventana"],
                "block_start": row["block_start"],
                "block_end": row["block_end"],
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
    print(f"Temporal NOAA 5y: {OUT_CSV.resolve()}")
    print(f"Ventanas 5y: {len(out)}")
    print(out.head().to_string(index=False))


if __name__ == "__main__":
    main()
