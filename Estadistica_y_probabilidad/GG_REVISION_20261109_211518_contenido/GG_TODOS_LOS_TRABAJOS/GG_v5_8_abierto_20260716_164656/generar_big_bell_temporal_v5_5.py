#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye ventanas temporales 2x2 para German-Gamma v5.5 usando BIG Bell.

Entrada:
    big_bell_gamma_input.xlsx

Salida:
    v5_5_big_bell_temporal/big_bell_sombra_temporal.csv

Definicion 2x2:
    a = 1 si bitrate_bits_per_2s > bitrate_roll_mean_10
    b = 1 si bitrate_delta > 0
    Gamma = 1 si filtro == True

Cada ventana reporta n_ab y N_ab:
    N_ab = total de filas en celda (a,b)
    n_ab = filas sobrevivientes Gamma=1 en celda (a,b)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


INPUT = Path("big_bell_gamma_input.xlsx")
OUT_DIR = Path("v5_5_big_bell_temporal")
OUT_CSV = OUT_DIR / "big_bell_sombra_temporal.csv"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_excel(INPUT)
    required = [
        "t_rel_s",
        "bitrate_bits_per_2s",
        "bitrate_delta",
        "bitrate_roll_mean_10",
        "filtro",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")

    df = df.dropna(subset=required).copy()
    df["a"] = (df["bitrate_bits_per_2s"] > df["bitrate_roll_mean_10"]).astype(int)
    df["b"] = (df["bitrate_delta"] > 0).astype(int)
    df["gamma"] = df["filtro"].astype(bool).astype(int)

    # 96 ventanas: suficiente resolucion temporal sin dejar celdas demasiado pequenas.
    n_windows = 96
    edges = np.linspace(df["t_rel_s"].min(), df["t_rel_s"].max(), n_windows + 1)
    df["ventana_id"] = pd.cut(df["t_rel_s"], bins=edges, labels=False, include_lowest=True)

    rows = []
    for window_id, g in df.groupby("ventana_id", observed=True):
        if pd.isna(window_id):
            continue
        row = {
            "ventana": f"w{int(window_id) + 1:03d}",
            "t_inicio_s": float(g["t_rel_s"].min()),
            "t_fin_s": float(g["t_rel_s"].max()),
        }
        for a in [0, 1]:
            for b in [0, 1]:
                cell = g[(g["a"] == a) & (g["b"] == b)]
                key = f"{a}{b}"
                row[f"N{key}"] = int(len(cell))
                row[f"n{key}"] = int(cell["gamma"].sum())
        # El auditor temporal exige columnas n00,N00,...
        rows.append(
            {
                "ventana": row["ventana"],
                "t_inicio_s": row["t_inicio_s"],
                "t_fin_s": row["t_fin_s"],
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
    # Evitamos ventanas degeneradas donde alguna celda no existe.
    cell_totals = ["N00", "N01", "N10", "N11"]
    before = len(out)
    out = out[(out[cell_totals] > 0).all(axis=1)].reset_index(drop=True)
    dropped = before - len(out)
    out.to_csv(OUT_CSV, index=False)

    print(f"Entrada: {INPUT.resolve()}")
    print(f"Ventanas guardadas: {OUT_CSV.resolve()}")
    print(f"Ventanas validas: {len(out)}")
    print(f"Ventanas eliminadas por celdas vacias: {dropped}")


if __name__ == "__main__":
    main()
