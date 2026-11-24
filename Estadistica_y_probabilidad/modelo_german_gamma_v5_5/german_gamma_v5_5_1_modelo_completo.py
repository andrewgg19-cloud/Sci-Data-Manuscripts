#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German-Gamma v5.5.1 - modelo operacional completo.

Incluye:
    1. Horizonte-espejo:
       C_H(X) = D_JS(Hist(M(Pi_H(X))), Hist(Pi_H(M(X))))

    2. Sombra geometrica 2x2:
       D_G = |ln((P00 P11)/(P01 P10))|

    3. Modo temporal:
       D_G(t), H*(t), perdida de soporte y apelacion temporal.

No incluye topologia persistente H0/H1; ese modulo requiere ripser/persim y
queda en german_gamma_v5_3_corregido.py.

Ejemplos:

    py -3 german_gamma_v5_5_1_modelo_completo.py horizon ^
      --input data.xlsx --columns x1,x2,x3 --horizon "x1 + x2 > 0.8"

    py -3 german_gamma_v5_5_1_modelo_completo.py shadow ^
      --n00 53 --N00 1143 --n01 79 --N01 1197 --n10 62 --N10 1202 --n11 51 --N11 1204

    py -3 german_gamma_v5_5_1_modelo_completo.py temporal ^
      --input ventanas.csv --critical-dg 0.25 --k 3
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


EPS = 1e-12


@dataclass(frozen=True)
class ResultadoHorizonteEspejo:
    modelo: str
    input: str
    columnas: list[str]
    horizonte: str
    espejo: str
    n_total: int
    n_horizonte: int
    tasa_horizonte: float
    c_h_js: float
    l1_histogramas: float
    bins_por_columna: int
    lectura: str
    advertencia: str


@dataclass(frozen=True)
class ResultadoSombra:
    modelo: str
    celdas: list[dict]
    invariante_sombra: float
    distancia_sombra_log: float
    tasa_minima: float
    tasa_maxima: float
    razon_max_min: float
    soporte_estado: str
    min_total_celda: int
    min_aceptados_celda: int
    lectura: str
    advertencia: str


@dataclass(frozen=True)
class PuntoTemporal:
    ventana: str
    invariante_sombra: float
    distancia_sombra_log: float
    entropia_expresada: float
    soporte_estado: str
    min_total_celda: int
    min_aceptados_celda: int
    dg_finito_evaluable: bool
    delta_sombra: float | None
    delta_entropia: float | None
    es_critico: bool
    racha_critica: int
    apelacion_temporal: str


def cargar_tabla(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if path.suffix.lower() in {".csv", ".txt"}:
        return pd.read_csv(path)
    raise ValueError("Formato no soportado. Usa CSV o Excel.")


def columnas_numericas(df: pd.DataFrame, explicit: str) -> list[str]:
    if explicit:
        cols = [c.strip() for c in explicit.split(",") if c.strip()]
    else:
        cols = list(df.select_dtypes(include=[np.number]).columns)
    if not cols:
        raise ValueError("No hay columnas numericas para evaluar.")
    faltantes = [c for c in cols if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas no encontradas: {faltantes}")
    return cols


def horizonte_identidad(cols: list[str]) -> str:
    """Horizonte total formal: x_j == x_j.

    En computacion NaN != NaN, por lo que esta identidad conserva el dominio
    valido de la columna elegida.
    """

    return f"{cols[0]} == {cols[0]}"


def horizonte_mask(df: pd.DataFrame, expr: str) -> np.ndarray:
    out = df.eval(expr, engine="python")
    mask = np.asarray(out, dtype=bool)
    if mask.shape[0] != len(df):
        raise ValueError("La expresion de horizonte no produce una mascara valida.")
    return mask


def limpiar_matriz(df: pd.DataFrame, cols: list[str], mask: np.ndarray | None = None) -> np.ndarray:
    data = df.loc[mask, cols] if mask is not None else df.loc[:, cols]
    x = data.to_numpy(dtype=float)
    finite = np.isfinite(x).all(axis=1)
    return x[finite]


def aplicar_espejo(x: np.ndarray, tipo: str) -> np.ndarray:
    if tipo == "negate":
        return -x
    if tipo == "reverse_columns":
        return x[:, ::-1]
    if tipo == "center_reflect":
        return 2.0 * np.nanmean(x, axis=0, keepdims=True) - x
    if tipo == "z_reflect":
        mu = np.nanmean(x, axis=0, keepdims=True)
        sd = np.nanstd(x, axis=0, keepdims=True)
        sd = np.where(sd <= EPS, 1.0, sd)
        z = (x - mu) / sd
        return mu - z * sd
    raise ValueError("Espejo no soportado: negate, reverse_columns, center_reflect, z_reflect.")


def aplicar_horizonte_a_matriz(x: np.ndarray, cols: list[str], expr: str) -> np.ndarray:
    temp = pd.DataFrame(x, columns=cols)
    mask = horizonte_mask(temp, expr)
    return x[mask]


def bordes_histograma(a: np.ndarray, b: np.ndarray, bins: int) -> list[np.ndarray]:
    both = np.vstack([a, b])
    edges = []
    for j in range(both.shape[1]):
        col = both[:, j]
        lo = float(np.nanmin(col))
        hi = float(np.nanmax(col))
        if abs(hi - lo) <= EPS:
            lo -= 0.5
            hi += 0.5
        edges.append(np.linspace(lo, hi, bins + 1))
    return edges


def hist_prob(x: np.ndarray, edges: list[np.ndarray]) -> np.ndarray:
    if len(x) == 0:
        raise ValueError("Una ruta produjo cero filas; C_H no es evaluable.")
    hist, _ = np.histogramdd(x, bins=edges)
    p = hist.astype(float).ravel() + EPS
    return p / p.sum()


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log2(p / m)) + 0.5 * np.sum(q * np.log2(q / m)))


def interpretar_ch(c_h: float) -> str:
    if c_h < 0.02:
        return "horizonte_espejo_compatible"
    if c_h < 0.10:
        return "no_conmutatividad_leve"
    if c_h < 0.25:
        return "no_conmutatividad_moderada"
    return "no_conmutatividad_fuerte"


def calcular_horizonte_espejo(input_path: Path, cols_arg: str, horizonte: str, espejo: str, bins: int) -> ResultadoHorizonteEspejo:
    df = cargar_tabla(input_path)
    cols = columnas_numericas(df, cols_arg)
    horizonte_expr = horizonte or horizonte_identidad(cols)

    base_mask = np.isfinite(df[cols].to_numpy(dtype=float)).all(axis=1)
    h_mask = horizonte_mask(df, horizonte_expr) & base_mask
    x_base = limpiar_matriz(df, cols, base_mask)
    x_h = limpiar_matriz(df, cols, h_mask)

    ruta_1 = aplicar_espejo(x_h, espejo)  # M(Pi_H(X))
    x_m = aplicar_espejo(x_base, espejo)
    ruta_2 = aplicar_horizonte_a_matriz(x_m, cols, horizonte_expr)  # Pi_H(M(X))

    edges = bordes_histograma(ruta_1, ruta_2, bins)
    p = hist_prob(ruta_1, edges)
    q = hist_prob(ruta_2, edges)
    c_h = js_divergence(p, q)
    l1 = float(np.sum(np.abs(p - q)))

    return ResultadoHorizonteEspejo(
        modelo="German-Gamma v5.5.1 horizonte-espejo",
        input=str(input_path),
        columnas=cols,
        horizonte=horizonte_expr,
        espejo=espejo,
        n_total=int(len(x_base)),
        n_horizonte=int(len(x_h)),
        tasa_horizonte=float(len(x_h) / len(x_base)) if len(x_base) else float("nan"),
        c_h_js=c_h,
        l1_histogramas=l1,
        bins_por_columna=bins,
        lectura=interpretar_ch(c_h),
        advertencia="C_H mide no-conmutatividad definida; no prueba causalidad, fraude ni invalidez por si solo.",
    )


def tasa(n: int, total: int) -> float:
    if total <= 0:
        raise ValueError("Cada total N debe ser mayor que cero.")
    if n < 0 or n > total:
        raise ValueError("Cada n debe estar entre 0 y N.")
    return n / total


def clasificar_soporte(values: dict[str, int]) -> tuple[str, int, int, bool]:
    n_vals = [values["n00"], values["n01"], values["n10"], values["n11"]]
    total_vals = [values["N00"], values["N01"], values["N10"], values["N11"]]
    min_n = min(n_vals)
    min_total = min(total_vals)
    if min_total <= 0:
        return "no_evaluable_soporte_total", min_total, min_n, False
    if min_n <= 0:
        return "perdida_soporte_expresado", min_total, min_n, False
    return "soporte_completo", min_total, min_n, True


def entropia_normalizada(values: list[int | float]) -> float:
    arr = np.asarray(values, dtype=float)
    total = float(arr.sum())
    if total <= 0 or len(arr) <= 1:
        return 0.0
    p = arr / total
    p = p[p > 0]
    return -float(np.sum(p * np.log(p))) / math.log(len(arr))


def interpretar_sombra(d_g: float, soporte_estado: str) -> str:
    if soporte_estado != "soporte_completo":
        return soporte_estado
    if d_g >= 0.25:
        return "sombra_geometrica_fuerte_o_moderada"
    if d_g >= 0.10:
        return "sombra_geometrica_leve"
    return "compatible_con_proporcionalidad_local"


def calcular_sombra(values: dict[str, int]) -> ResultadoSombra:
    soporte_estado, min_total, min_n, evaluable = clasificar_soporte(values)
    celdas = []
    for key in ["00", "01", "10", "11"]:
        n = values[f"n{key}"]
        total = values[f"N{key}"]
        celdas.append({"celda": key, "aceptados": n, "total": total, "tasa": None if total <= 0 else n / total})

    if soporte_estado == "no_evaluable_soporte_total":
        i_s = float("nan")
        d_g = float("nan")
        tasas = [c["tasa"] for c in celdas if c["tasa"] is not None]
    else:
        p00 = tasa(values["n00"], values["N00"])
        p01 = tasa(values["n01"], values["N01"])
        p10 = tasa(values["n10"], values["N10"])
        p11 = tasa(values["n11"], values["N11"])
        i_s = ((p00 + EPS) * (p11 + EPS)) / ((p01 + EPS) * (p10 + EPS))
        d_g = abs(math.log(i_s))
        tasas = [p00, p01, p10, p11]

    tasa_min = float(min(tasas)) if tasas else float("nan")
    tasa_max = float(max(tasas)) if tasas else float("nan")
    razon = float(tasa_max / max(tasa_min, EPS)) if tasas else float("nan")

    return ResultadoSombra(
        modelo="German-Gamma v5.5.1 sombra geometrica",
        celdas=celdas,
        invariante_sombra=float(i_s),
        distancia_sombra_log=float(d_g),
        tasa_minima=tasa_min,
        tasa_maxima=tasa_max,
        razon_max_min=razon,
        soporte_estado=soporte_estado,
        min_total_celda=min_total,
        min_aceptados_celda=min_n,
        lectura=interpretar_sombra(float(d_g), soporte_estado),
        advertencia="D_G detecta sombra o soporte perdido; no prueba causalidad, fraude ni invalidez por si solo.",
    )


def analizar_temporal(path: Path, critical_dg: float, k: int) -> list[PuntoTemporal]:
    required = ["n00", "N00", "n01", "N01", "n10", "N10", "n11", "N11"]
    puntos: list[PuntoTemporal] = []
    prev_dg = None
    prev_h = None
    racha = 0

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV temporal sin encabezados.")
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Faltan columnas: {missing}")

        for idx, row in enumerate(reader, start=1):
            ventana = str(row.get("ventana") or row.get("window") or idx)
            values = {c: int(float(row[c])) for c in required}
            sombra = calcular_sombra(values)
            h = entropia_normalizada([values["n00"], values["n01"], values["n10"], values["n11"]])
            evaluable = sombra.soporte_estado == "soporte_completo"
            es_critico = evaluable and sombra.distancia_sombra_log >= critical_dg
            racha = racha + 1 if es_critico else 0

            if not evaluable:
                apelacion = sombra.soporte_estado
            elif racha >= k:
                apelacion = "confirmada_por_persistencia"
            elif es_critico:
                apelacion = "senal_en_apelacion"
            else:
                apelacion = "sin_persistencia_critica"

            puntos.append(
                PuntoTemporal(
                    ventana=ventana,
                    invariante_sombra=sombra.invariante_sombra,
                    distancia_sombra_log=sombra.distancia_sombra_log,
                    entropia_expresada=h,
                    soporte_estado=sombra.soporte_estado,
                    min_total_celda=sombra.min_total_celda,
                    min_aceptados_celda=sombra.min_aceptados_celda,
                    dg_finito_evaluable=evaluable,
                    delta_sombra=None if (prev_dg is None or not evaluable) else sombra.distancia_sombra_log - prev_dg,
                    delta_entropia=None if prev_h is None else h - prev_h,
                    es_critico=es_critico,
                    racha_critica=racha,
                    apelacion_temporal=apelacion,
                )
            )
            if evaluable:
                prev_dg = sombra.distancia_sombra_log
            prev_h = h

    return puntos


def write_json(obj, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_horizon(args: argparse.Namespace) -> None:
    r = calcular_horizonte_espejo(Path(args.input), args.columns, args.horizon, args.mirror, args.bins)
    print(json.dumps(asdict(r), indent=2, ensure_ascii=False))
    write_json(asdict(r), Path(args.json_out))


def cmd_shadow(args: argparse.Namespace) -> None:
    values = {
        "n00": args.n00,
        "N00": args.N00,
        "n01": args.n01,
        "N01": args.N01,
        "n10": args.n10,
        "N10": args.N10,
        "n11": args.n11,
        "N11": args.N11,
    }
    r = calcular_sombra(values)
    print(json.dumps(asdict(r), indent=2, ensure_ascii=False))
    write_json(asdict(r), Path(args.json_out))


def cmd_temporal(args: argparse.Namespace) -> None:
    puntos = analizar_temporal(Path(args.input), args.critical_dg, args.k)
    rows = [asdict(p) for p in puntos]
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    write_json(rows, Path(args.json_out))
    if args.csv_out:
        pd.DataFrame(rows).to_csv(args.csv_out, index=False)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="German-Gamma v5.5.1 modelo operacional completo.")
    sub = p.add_subparsers(required=True)

    h = sub.add_parser("horizon", help="Calcula C_H horizonte-espejo.")
    h.add_argument("--input", required=True)
    h.add_argument("--columns", default="")
    h.add_argument("--horizon", default="")
    h.add_argument("--mirror", default="center_reflect", choices=["negate", "reverse_columns", "center_reflect", "z_reflect"])
    h.add_argument("--bins", type=int, default=8)
    h.add_argument("--json-out", default="german_gamma_horizon_result.json")
    h.set_defaults(func=cmd_horizon)

    s = sub.add_parser("shadow", help="Calcula sombra geometrica 2x2.")
    s.add_argument("--n00", type=int, required=True)
    s.add_argument("--N00", type=int, required=True)
    s.add_argument("--n01", type=int, required=True)
    s.add_argument("--N01", type=int, required=True)
    s.add_argument("--n10", type=int, required=True)
    s.add_argument("--N10", type=int, required=True)
    s.add_argument("--n11", type=int, required=True)
    s.add_argument("--N11", type=int, required=True)
    s.add_argument("--json-out", default="german_gamma_shadow_result.json")
    s.set_defaults(func=cmd_shadow)

    t = sub.add_parser("temporal", help="Calcula sombra temporal, entropia, soporte y apelacion.")
    t.add_argument("--input", required=True)
    t.add_argument("--critical-dg", type=float, default=0.25)
    t.add_argument("--k", type=int, default=3)
    t.add_argument("--json-out", default="german_gamma_temporal_result.json")
    t.add_argument("--csv-out", default="german_gamma_temporal_result.csv")
    t.set_defaults(func=cmd_temporal)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
