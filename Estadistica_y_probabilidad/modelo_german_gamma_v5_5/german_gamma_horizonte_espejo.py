#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German-Gamma v5.5 - prueba horizonte-espejo.

Calcula la no conmutatividad:

    C_H(X) = D( M(Pi_H(X)), Pi_H(M(X)) )

No es una metafora: Pi_H es una seleccion de horizonte, M es una
transformacion explicita, y D es una divergencia Jensen-Shannon sobre
histogramas multivariables.
"""

from __future__ import annotations

import argparse
import json
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


def horizonte_mask(df: pd.DataFrame, expr: str) -> np.ndarray:
    out = df.eval(expr, engine="python")
    mask = np.asarray(out, dtype=bool)
    if mask.shape[0] != len(df):
        raise ValueError("La expresion de horizonte no produce una mascara valida.")
    return mask


def horizonte_identidad(cols: list[str]) -> str:
    """Horizonte total como condicion identidad explicita.

    En datos tabulares usamos x_j == x_j porque en computacion NaN != NaN.
    Asi el horizonte total conserva el dominio valido sin tratarse como
    ausencia de condicion.
    """

    return f"{cols[0]} == {cols[0]}"


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
    raise ValueError("Espejo no soportado. Opciones: negate, reverse_columns, center_reflect, z_reflect")


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
        if not np.isfinite(lo) or not np.isfinite(hi):
            raise ValueError("Datos no finitos en histogramas.")
        if abs(hi - lo) <= EPS:
            lo -= 0.5
            hi += 0.5
        edges.append(np.linspace(lo, hi, bins + 1))
    return edges


def hist_prob(x: np.ndarray, edges: list[np.ndarray]) -> np.ndarray:
    if len(x) == 0:
        raise ValueError("Una de las rutas produjo cero filas; C_H no es evaluable.")
    hist, _ = np.histogramdd(x, bins=edges)
    p = hist.astype(float).ravel()
    p = p + EPS
    return p / p.sum()


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log2(p / m))
    kl_qm = np.sum(q * np.log2(q / m))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


def interpretar(c_h: float) -> str:
    if c_h < 0.02:
        return "horizonte_espejo_compatible"
    if c_h < 0.10:
        return "no_conmutatividad_leve"
    if c_h < 0.25:
        return "no_conmutatividad_moderada"
    return "no_conmutatividad_fuerte"


def calcular(
    input_path: Path,
    *,
    cols_arg: str,
    horizonte: str,
    espejo: str,
    bins: int,
) -> ResultadoHorizonteEspejo:
    df = cargar_tabla(input_path)
    cols = columnas_numericas(df, cols_arg)
    horizonte_expr = horizonte or horizonte_identidad(cols)
    base_mask = np.isfinite(df[cols].to_numpy(dtype=float)).all(axis=1)
    h_mask = horizonte_mask(df, horizonte_expr) & base_mask

    x_base = limpiar_matriz(df, cols, base_mask)
    x_h = limpiar_matriz(df, cols, h_mask)

    # Ruta 1: M(Pi_H(X)).
    ruta_h_luego_m = aplicar_espejo(x_h, espejo)

    # Ruta 2: Pi_H(M(X)).
    x_m = aplicar_espejo(x_base, espejo)
    ruta_m_luego_h = aplicar_horizonte_a_matriz(x_m, cols, horizonte_expr)

    edges = bordes_histograma(ruta_h_luego_m, ruta_m_luego_h, bins)
    p = hist_prob(ruta_h_luego_m, edges)
    q = hist_prob(ruta_m_luego_h, edges)
    c_h = js_divergence(p, q)
    l1 = float(np.sum(np.abs(p - q)))

    return ResultadoHorizonteEspejo(
        modelo="German-Gamma v5.5 horizonte-espejo",
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
        lectura=interpretar(c_h),
        advertencia=(
            "C_H mide no conmutatividad entre horizonte y espejo para las transformaciones definidas. "
            "No prueba causalidad, fraude ni invalidez por si solo."
        ),
    )


def imprimir(r: ResultadoHorizonteEspejo) -> None:
    print("-" * 88)
    print("GERMAN-GAMMA v5.5: PRUEBA HORIZONTE-ESPEJO")
    print("-" * 88)
    print(f"Input              : {r.input}")
    print(f"Columnas           : {', '.join(r.columnas)}")
    print(f"Horizonte          : {r.horizonte}")
    print(f"Espejo             : {r.espejo}")
    print(f"N total            : {r.n_total}")
    print(f"N horizonte        : {r.n_horizonte}")
    print(f"Tasa horizonte     : {r.tasa_horizonte:.6f}")
    print(f"C_H JS             : {r.c_h_js:.6f}")
    print(f"L1 histogramas     : {r.l1_histogramas:.6f}")
    print(f"Lectura            : {r.lectura}")
    print(f"Nota               : {r.advertencia}")
    print("-" * 88)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="German-Gamma v5.5: no conmutatividad horizonte-espejo.")
    p.add_argument("--input", required=True, help="CSV o Excel de entrada.")
    p.add_argument("--columns", default="", help="Columnas numericas separadas por coma. Si se omite, usa todas.")
    p.add_argument("--horizon", default="", help='Expresion pandas. Ej: "x1 > 0"')
    p.add_argument(
        "--mirror",
        default="center_reflect",
        choices=["negate", "reverse_columns", "center_reflect", "z_reflect"],
    )
    p.add_argument("--bins", type=int, default=8, help="Bins por columna para JS multivariable.")
    p.add_argument("--json-out", default="horizonte_espejo_resultado.json")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    r = calcular(
        Path(args.input),
        cols_arg=args.columns,
        horizonte=args.horizon,
        espejo=args.mirror,
        bins=args.bins,
    )
    imprimir(r)
    Path(args.json_out).write_text(json.dumps(asdict(r), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON: {Path(args.json_out).resolve()}")


if __name__ == "__main__":
    main()
