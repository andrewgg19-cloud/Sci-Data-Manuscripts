#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara datos NOAA GML Mauna Loa CO2 para German-Gamma v5.5.

Fuente oficial:
https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv

Salida:
    v5_5_noaa_co2/noaa_co2_mlo_gamma_input.csv

Notas:
    - Este dataset no trae un filtro Gamma original equivalente a aceptado/rechazado.
    - Para pruebas exploratorias se define gamma como anomaly > 0.
    - La prueba horizonte-espejo no requiere Gamma.
"""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

import pandas as pd


URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
OUT = Path("v5_5_noaa_co2")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    raw_path = OUT / "co2_mm_mlo.csv"
    with urlopen(URL, timeout=30) as r:
        raw_path.write_bytes(r.read())

    df = pd.read_csv(raw_path, comment="#")
    df.columns = [c.strip() for c in df.columns]

    # Columnas esperadas NOAA: year, month, decimal date, average, deseasonalized, ndays, sdev, unc
    rename = {
        "decimal date": "decimal_date",
        "average": "co2_average",
        "deseasonalized": "co2_deseasonalized",
        "ndays": "ndays",
        "sdev": "sdev",
        "unc": "unc",
    }
    df = df.rename(columns=rename)
    df = df[df["co2_average"] > 0].copy()
    df["t_index"] = range(len(df))
    df["co2_delta"] = df["co2_average"].diff().fillna(0.0)
    df["co2_roll_mean_12"] = df["co2_average"].rolling(12, min_periods=1).mean()
    df["co2_roll_std_12"] = df["co2_average"].rolling(12, min_periods=2).std().fillna(0.0)
    df["co2_anomaly"] = df["co2_average"] - df["co2_roll_mean_12"]

    # Gamma exploratorio, no filtro NOAA original.
    df["filtro"] = df["co2_anomaly"] > 0

    out_cols = [
        "year",
        "month",
        "decimal_date",
        "t_index",
        "co2_average",
        "co2_deseasonalized",
        "co2_delta",
        "co2_roll_mean_12",
        "co2_roll_std_12",
        "co2_anomaly",
        "ndays",
        "sdev",
        "unc",
        "filtro",
    ]
    out_csv = OUT / "noaa_co2_mlo_gamma_input.csv"
    df[out_cols].to_csv(out_csv, index=False)

    print(f"Fuente: {URL}")
    print(f"Raw: {raw_path.resolve()}")
    print(f"Preparado: {out_csv.resolve()}")
    print(f"Filas: {len(df)}")
    print(df[out_cols].head().to_string(index=False))


if __name__ == "__main__":
    main()
