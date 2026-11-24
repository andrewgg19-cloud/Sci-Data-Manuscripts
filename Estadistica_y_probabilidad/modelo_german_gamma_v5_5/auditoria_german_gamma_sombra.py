#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""German Gamma - auditoria de sombra geometrica 2x2.

Este modulo calcula si una regla de seleccion Gamma deja una huella
no uniforme entre cuatro celdas binarias. No prueba fraude, intencion ni
invalidez experimental; reporta deformacion compatible con filtrado diferencial.

Uso directo:
    python auditoria_german_gamma_sombra.py

Uso con datos propios:
    python auditoria_german_gamma_sombra.py --n00 53 --N00 1143 --n01 79 --N01 1197 --n10 62 --N10 1202 --n11 51 --N11 1204

Uso temporal:
    python auditoria_german_gamma_sombra.py --temporal-csv ventanas.csv

El CSV temporal debe contener:
    ventana,n00,N00,n01,N01,n10,N10,n11,N11
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


EPS = 1e-12


@dataclass(frozen=True)
class Celda:
    nombre: str
    aceptados: int
    total: int
    tasa: float


@dataclass(frozen=True)
class ResultadoSombra:
    modelo: str
    autor_proponente: str
    celdas: list[Celda]
    invariante_sombra: float
    distancia_sombra_log: float
    tasa_minima: float
    tasa_maxima: float
    razon_max_min: float
    bootstrap_p_bilateral: float | None
    bootstrap_intervalo_95: tuple[float, float] | None
    interpretacion: str
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


def tasa(aceptados: int, total: int) -> float:
    if total <= 0:
        raise ValueError("Cada total N debe ser mayor que cero.")
    if aceptados < 0 or aceptados > total:
        raise ValueError("Cada n debe estar entre 0 y N.")
    return aceptados / total


def entropia_normalizada(valores: list[int | float]) -> float:
    """Entropia Shannon normalizada en [0,1] para la composicion expresada."""

    arr = np.asarray(valores, dtype=float)
    total = float(arr.sum())
    if total <= 0 or len(arr) <= 1:
        return 0.0
    p = arr / total
    p = p[p > 0]
    h = -float(np.sum(p * np.log(p)))
    return h / math.log(len(arr))


def clasificar_soporte(values: dict[str, int]) -> tuple[str, int, int, bool]:
    """Clasifica soporte de una ventana temporal 2x2.

    - soporte_completo: todas las celdas tienen N_ab > 0 y n_ab > 0.
    - perdida_soporte_expresado: hay N_ab > 0 pero alguna n_ab = 0.
    - no_evaluable_soporte_total: alguna celda N_ab = 0.

    Solo `soporte_completo` debe alimentar apelacion temporal por sombra finita.
    """

    n_vals = [values["n00"], values["n01"], values["n10"], values["n11"]]
    n_total_vals = [values["N00"], values["N01"], values["N10"], values["N11"]]
    min_n = min(n_vals)
    min_n_total = min(n_total_vals)
    if min_n_total <= 0:
        return "no_evaluable_soporte_total", min_n_total, min_n, False
    if min_n <= 0:
        return "perdida_soporte_expresado", min_n_total, min_n, False
    return "soporte_completo", min_n_total, min_n, True


def interpretar(i_s: float, d_g: float, p_boot: float | None) -> str:
    """Dictamen conservador; no emite conclusiones juridicas."""

    if not math.isfinite(i_s) or not math.isfinite(d_g):
        return "no evaluable por division numerica inestable"
    if p_boot is not None and p_boot < 0.05 and d_g >= 0.25:
        return "sombra geometrica fuerte compatible con seleccion diferencial"
    if d_g >= 0.25:
        return "sombra geometrica moderada; requiere control estadistico y documental"
    if d_g >= 0.10:
        return "sombra geometrica leve"
    return "compatible con proporcionalidad local"


def calcular_invariante_sombra(
    n_00: int,
    N_00: int,
    n_01: int,
    N_01: int,
    n_10: int,
    N_10: int,
    n_11: int,
    N_11: int,
    *,
    bootstrap: int = 0,
    seed: int = 20260517,
) -> ResultadoSombra:
    """Calcula el invariante de sombra local.

    I_S = (P00 * P11) / (P01 * P10)
    D_G = |log(I_S)|

    I_S cercano a 1 sugiere proporcionalidad local entre celdas.
    I_S alejado de 1 sugiere seleccion diferencial entre celdas.
    """

    celdas = [
        Celda("00", n_00, N_00, tasa(n_00, N_00)),
        Celda("01", n_01, N_01, tasa(n_01, N_01)),
        Celda("10", n_10, N_10, tasa(n_10, N_10)),
        Celda("11", n_11, N_11, tasa(n_11, N_11)),
    ]
    p = {c.nombre: c.tasa for c in celdas}

    invariante = ((p["00"] + EPS) * (p["11"] + EPS)) / ((p["01"] + EPS) * (p["10"] + EPS))
    distancia = abs(math.log(invariante))
    tasas = [c.tasa for c in celdas]
    razon_max_min = max(tasas) / max(min(tasas), EPS)

    p_boot = None
    intervalo = None
    if bootstrap > 0:
        p_boot, intervalo = bootstrap_sombra(celdas, distancia, bootstrap=bootstrap, seed=seed)

    return ResultadoSombra(
        modelo="German-Gamma sombra geometrica 2x2",
        autor_proponente="Andres German Garcia",
        celdas=celdas,
        invariante_sombra=float(invariante),
        distancia_sombra_log=float(distancia),
        tasa_minima=float(min(tasas)),
        tasa_maxima=float(max(tasas)),
        razon_max_min=float(razon_max_min),
        bootstrap_p_bilateral=p_boot,
        bootstrap_intervalo_95=intervalo,
        interpretacion=interpretar(invariante, distancia, p_boot),
        advertencia=(
            "Este resultado detecta sombra geometrica compatible con seleccion diferencial; "
            "no prueba fraude, intencion ni invalidez experimental por si solo."
        ),
    )


def bootstrap_sombra(
    celdas: list[Celda],
    distancia_observada: float,
    *,
    bootstrap: int,
    seed: int,
) -> tuple[float, tuple[float, float]]:
    """Control nulo: misma tasa global, mismos N por celda."""

    rng = np.random.default_rng(seed)
    total_aceptados = sum(c.aceptados for c in celdas)
    total_n = sum(c.total for c in celdas)
    tasa_global = total_aceptados / total_n
    simuladas = []

    for _ in range(bootstrap):
        tasas_sim = {}
        for c in celdas:
            n_sim = rng.binomial(c.total, tasa_global)
            tasas_sim[c.nombre] = n_sim / c.total
        i_sim = ((tasas_sim["00"] + EPS) * (tasas_sim["11"] + EPS)) / (
            (tasas_sim["01"] + EPS) * (tasas_sim["10"] + EPS)
        )
        simuladas.append(abs(math.log(i_sim)))

    arr = np.asarray(simuladas, dtype=float)
    p_valor = float(np.mean(arr >= distancia_observada))
    intervalo = (float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)))
    return p_valor, intervalo


def analizar_trayectoria_temporal(
    ruta_csv: Path,
    *,
    critical_dg: float,
    k: int,
) -> list[PuntoTemporal]:
    """Analiza movimiento: sombra, entropia y persistencia por ventanas.

    La entropia se calcula sobre la composicion de eventos aceptados
    [n00, n01, n10, n11]. Mide cuan concentrada o distribuida esta la
    expresion observable entre celdas en cada ventana.
    """

    required = ["n00", "N00", "n01", "N01", "n10", "N10", "n11", "N11"]
    puntos: list[PuntoTemporal] = []
    racha = 0
    prev_dg = None
    prev_h = None

    with ruta_csv.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("El CSV temporal no contiene encabezados.")
        faltantes = [col for col in required if col not in reader.fieldnames]
        if faltantes:
            raise ValueError(f"Faltan columnas requeridas: {faltantes}")

        for idx, row in enumerate(reader, start=1):
            ventana = str(row.get("ventana") or row.get("window") or idx)
            values = {col: int(float(row[col])) for col in required}
            resultado = calcular_invariante_sombra(
                values["n00"],
                values["N00"],
                values["n01"],
                values["N01"],
                values["n10"],
                values["N10"],
                values["n11"],
                values["N11"],
                bootstrap=0,
            )
            h = entropia_normalizada([values["n00"], values["n01"], values["n10"], values["n11"]])
            dg = resultado.distancia_sombra_log
            soporte_estado, min_total_celda, min_aceptados_celda, dg_finito_evaluable = clasificar_soporte(values)
            es_critico = dg_finito_evaluable and dg >= critical_dg
            racha = racha + 1 if es_critico else 0
            if not dg_finito_evaluable:
                apelacion = soporte_estado
            elif racha >= k:
                apelacion = "confirmada_por_persistencia"
            elif es_critico:
                apelacion = "senal_en_apelacion"
            else:
                apelacion = "sin_persistencia_critica"

            puntos.append(
                PuntoTemporal(
                    ventana=ventana,
                    invariante_sombra=resultado.invariante_sombra,
                    distancia_sombra_log=dg,
                    entropia_expresada=h,
                    soporte_estado=soporte_estado,
                    min_total_celda=min_total_celda,
                    min_aceptados_celda=min_aceptados_celda,
                    dg_finito_evaluable=dg_finito_evaluable,
                    delta_sombra=None if (prev_dg is None or not dg_finito_evaluable) else dg - prev_dg,
                    delta_entropia=None if prev_h is None else h - prev_h,
                    es_critico=es_critico,
                    racha_critica=racha,
                    apelacion_temporal=apelacion,
                )
            )
            if dg_finito_evaluable:
                prev_dg = dg
            prev_h = h

    return puntos


def imprimir_trayectoria(puntos: list[PuntoTemporal], *, critical_dg: float, k: int) -> None:
    print("-" * 96)
    print("GERMAN-GAMMA: TRAYECTORIA TEMPORAL DE SOMBRA Y ENTROPIA")
    print("-" * 96)
    print(f"Umbral D_G critico: {critical_dg:.6f} | Persistencia requerida k={k}")
    print("-" * 96)
    print("ventana,D_G,H_expresada,soporte,delta_D_G,delta_H,racha,apelacion")
    for p in puntos:
        ddg = "" if p.delta_sombra is None else f"{p.delta_sombra:.6f}"
        dh = "" if p.delta_entropia is None else f"{p.delta_entropia:.6f}"
        print(
            f"{p.ventana},{p.distancia_sombra_log:.6f},{p.entropia_expresada:.6f},"
            f"{p.soporte_estado},{ddg},{dh},{p.racha_critica},{p.apelacion_temporal}"
        )
    print("-" * 96)


def guardar_trayectoria_json(puntos: list[PuntoTemporal], ruta: Path) -> None:
    ruta.write_text(
        json.dumps([asdict(p) for p in puntos], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def guardar_trayectoria_csv(puntos: list[PuntoTemporal], ruta: Path) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "ventana",
                "invariante_sombra",
                "distancia_sombra_log",
                "entropia_expresada",
                "soporte_estado",
                "min_total_celda",
                "min_aceptados_celda",
                "dg_finito_evaluable",
                "delta_sombra",
                "delta_entropia",
                "es_critico",
                "racha_critica",
                "apelacion_temporal",
            ]
        )
        for p in puntos:
            writer.writerow(
                [
                    p.ventana,
                    p.invariante_sombra,
                    p.distancia_sombra_log,
                    p.entropia_expresada,
                    p.soporte_estado,
                    p.min_total_celda,
                    p.min_aceptados_celda,
                    p.dg_finito_evaluable,
                    "" if p.delta_sombra is None else p.delta_sombra,
                    "" if p.delta_entropia is None else p.delta_entropia,
                    p.es_critico,
                    p.racha_critica,
                    p.apelacion_temporal,
                ]
            )


def imprimir_resultado(resultado: ResultadoSombra) -> None:
    print("-" * 72)
    print("GERMAN-GAMMA: AUDITORIA DE SOMBRA GEOMETRICA 2x2")
    print("-" * 72)
    for celda in resultado.celdas:
        print(f"P(Gamma=1 | {celda.nombre}) = {celda.tasa:.8f} ({celda.aceptados}/{celda.total})")
    print("-" * 72)
    print(f"Invariante de sombra I_S       = {resultado.invariante_sombra:.6f}")
    print(f"Distancia de sombra D_G=|ln I| = {resultado.distancia_sombra_log:.6f}")
    print(f"Razon tasa max/min             = {resultado.razon_max_min:.6f}")
    if resultado.bootstrap_p_bilateral is not None:
        lo, hi = resultado.bootstrap_intervalo_95 or (float("nan"), float("nan"))
        print(f"Bootstrap p bilateral          = {resultado.bootstrap_p_bilateral:.6f}")
        print(f"Bootstrap intervalo 95% D_G    = [{lo:.6f}, {hi:.6f}]")
    print("-" * 72)
    print(f"Lectura: {resultado.interpretacion}")
    print(f"Nota: {resultado.advertencia}")
    print("-" * 72)


def guardar_json(resultado: ResultadoSombra, ruta: Path) -> None:
    data = asdict(resultado)
    data["celdas"] = [asdict(c) for c in resultado.celdas]
    ruta.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def guardar_csv(resultado: ResultadoSombra, ruta: Path) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["celda", "aceptados", "total", "tasa"])
        for c in resultado.celdas:
            writer.writerow([c.nombre, c.aceptados, c.total, f"{c.tasa:.12f}"])
        writer.writerow([])
        writer.writerow(["invariante_sombra", resultado.invariante_sombra])
        writer.writerow(["distancia_sombra_log", resultado.distancia_sombra_log])
        writer.writerow(["razon_max_min", resultado.razon_max_min])
        writer.writerow(["bootstrap_p_bilateral", resultado.bootstrap_p_bilateral])
        writer.writerow(["interpretacion", resultado.interpretacion])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="German-Gamma: auditoria de sombra geometrica 2x2.")
    parser.add_argument("--temporal-csv", default="", help="CSV con ventanas temporales y conteos 2x2.")
    parser.add_argument("--critical-dg", type=float, default=0.25, help="Umbral critico para D_G temporal.")
    parser.add_argument("--k", type=int, default=2, help="Ventanas consecutivas requeridas para confirmacion.")
    parser.add_argument("--n00", type=int, default=53)
    parser.add_argument("--N00", type=int, default=1143)
    parser.add_argument("--n01", type=int, default=79)
    parser.add_argument("--N01", type=int, default=1197)
    parser.add_argument("--n10", type=int, default=62)
    parser.add_argument("--N10", type=int, default=1202)
    parser.add_argument("--n11", type=int, default=51)
    parser.add_argument("--N11", type=int, default=1204)
    parser.add_argument("--bootstrap", type=int, default=10000, help="Numero de simulaciones nulas.")
    parser.add_argument("--seed", type=int, default=20260517)
    parser.add_argument("--json-out", default="auditoria_sombra_geometrica.json")
    parser.add_argument("--csv-out", default="auditoria_sombra_geometrica.csv")
    parser.add_argument("--temporal-json-out", default="auditoria_sombra_temporal.json")
    parser.add_argument("--temporal-csv-out", default="auditoria_sombra_temporal.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.temporal_csv:
        puntos = analizar_trayectoria_temporal(
            Path(args.temporal_csv),
            critical_dg=args.critical_dg,
            k=args.k,
        )
        imprimir_trayectoria(puntos, critical_dg=args.critical_dg, k=args.k)
        guardar_trayectoria_json(puntos, Path(args.temporal_json_out))
        guardar_trayectoria_csv(puntos, Path(args.temporal_csv_out))
        print(f"JSON temporal: {Path(args.temporal_json_out).resolve()}")
        print(f"CSV temporal : {Path(args.temporal_csv_out).resolve()}")
        return

    resultado = calcular_invariante_sombra(
        args.n00,
        args.N00,
        args.n01,
        args.N01,
        args.n10,
        args.N10,
        args.n11,
        args.N11,
        bootstrap=args.bootstrap,
        seed=args.seed,
    )
    imprimir_resultado(resultado)
    guardar_json(resultado, Path(args.json_out))
    guardar_csv(resultado, Path(args.csv_out))
    print(f"JSON: {Path(args.json_out).resolve()}")
    print(f"CSV : {Path(args.csv_out).resolve()}")


if __name__ == "__main__":
    main()
