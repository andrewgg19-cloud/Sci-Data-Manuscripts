#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comparación probabilística reproducible, pero exploratoria, German Gamma vs Forecaster.

Requisitos: Python 3.12, numpy, scipy, astro-forecaster.
Entradas: predicciones aleatorizadas por sistema de German Gamma y mediciones NASA.
El código no reentrena GG; usa predicciones fuera de pliegue previamente obtenidas.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
from collections import defaultdict
from importlib import metadata

import numpy as np
from scipy.special import logsumexp
from scipy.stats import norm


def read_rows(path: Path):
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    needed = ('planet','hostname','fold','mass_earth','radius_earth',
              'mass_err_frac','radius_err_frac','gg_radius','gg_regime_sigma_lnR')
    if not rows or any(k not in rows[0] for k in needed):
        raise ValueError(f'Columnas requeridas: {needed}')
    for row in rows:
        for k in needed[3:]:
            v = float(row[k]);
            if not math.isfinite(v) or (v <= 0 if k in ('mass_earth','radius_earth','gg_radius','gg_regime_sigma_lnR') else v < 0):
                raise ValueError(f'Dato inválido en {row["planet"]}: {k}={v}')
    return rows


def crps_norm(mu, sigma, y):
    z = (y-mu)/sigma
    return float(sigma*(z*(2*norm.cdf(z)-1) + 2*norm.pdf(z) - 1/math.sqrt(math.pi)))


def crps_empirical(samples, y):
    """CRPS exactamente para la distribución empírica, O(n log n)."""
    s = np.sort(np.asarray(samples,dtype=float))
    n = s.size
    coeff = 2*np.arange(1,n+1,dtype=float)-n-1
    return float(np.mean(np.abs(s-y)) - np.dot(coeff,s)/(n*n))


def kde_nll(samples, y):
    """NLL exploratoria: densidad KDE, NO likelihood analítica del Forecaster original."""
    s=np.asarray(samples,dtype=float)
    sd=float(np.std(s,ddof=1))
    h=max(0.015,1.06*sd*(len(s)**(-0.2)))
    return float(-logsumexp(norm.logpdf(y,loc=s,scale=h))+math.log(len(s)))


def bootstrap_mean_diff(rows, key_a, key_b, n_boot, seed):
    group=defaultdict(list)
    for r in rows:
        group[r['hostname']].append(float(r[key_a])-float(r[key_b]))
    names=list(group)
    lens=np.asarray([len(group[k]) for k in names],dtype=int)
    sums=np.asarray([sum(group[k]) for k in names])
    rng=np.random.default_rng(seed)
    vals=np.empty(n_boot,dtype=float)
    for j in range(n_boot):
        sel=rng.integers(0,len(names),size=len(names))
        vals[j]=sums[sel].sum()/lens[sel].sum()
    return float(np.mean([float(r[key_a])-float(r[key_b]) for r in rows])), [float(x) for x in np.percentile(vals,[2.5,97.5])]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',default='datos_897_gg.csv')
    ap.add_argument('--samples',type=int,default=2048,help='Muestras por planeta (recomendado 2048)')
    ap.add_argument('--chunk',type=int,default=128,help='Planetas por lote')
    ap.add_argument('--bootstrap',type=int,default=2000)
    ap.add_argument('--seed',type=int,default=20261103)
    ap.add_argument('--out',default='resultados_forecaster_897.csv')
    args=ap.parse_args()
    if args.samples < 128 or args.chunk <= 0:
        ap.error('Use samples>=128 y chunk>0')
    if args.chunk*args.samples>900000:
        ap.error('Disminuya chunk o samples: cada lote debe tener <900000 muestras')
    inp=Path(args.input)
    rows=read_rows(inp)
    print(f'Archivo: {inp.name}; planetas: {len(rows)}; sistemas: {len(set(r["hostname"] for r in rows))}',flush=True)
    print(f'Forecaster completo: {args.samples} muestras por planeta, en lotes de {args.chunk}',flush=True)

    # La función oficial Mpost2R usa np.random (generador global legacy).
    np.random.seed(args.seed)
    rng=np.random.default_rng(args.seed+3)
    import forecaster
    results=[]
    n=len(rows)
    for begin in range(0,n,args.chunk):
        part=rows[begin:begin+args.chunk]
        m=np.asarray([float(z['mass_earth']) for z in part])[:,None]
        err=np.asarray([float(z['mass_err_frac']) for z in part])[:,None]
        # Aproximación lognormal de errores de masa; mantiene masa media aproximadamente igual al valor catalogado.
        sigma_m=np.sqrt(np.log1p(err*err))
        sampled_m=m*np.exp(rng.normal(size=(len(part),args.samples))*sigma_m - 0.5*sigma_m*sigma_m)
        if np.any(sampled_m<3e-4) or np.any(sampled_m>3e5):
            raise ValueError('La muestra de masa excede el dominio Forecaster; revisar el catálogo')
        radius_samples=np.asarray(forecaster.Mpost2R(sampled_m.ravel(),unit='Earth',classify=False)).reshape(len(part),args.samples)
        if not np.all(np.isfinite(radius_samples)) or np.any(radius_samples<=0):
            raise ValueError('Forecaster devolvió radios no válidos')
        for j,row in enumerate(part):
            observed=float(row['radius_earth'])
            log_obs=math.log(observed)
            # Mediana de radio latente; no se añade error de medición para MAPE.
            latent=radius_samples[j]
            fc_med=float(np.median(latent))
            # Para pronosticar la medición (en lugar del radio verdadero) se añade error instrumental.
            sigma_r=math.sqrt(math.log1p(float(row['radius_err_frac'])**2))
            log_s=np.log(latent)+rng.normal(size=args.samples)*sigma_r
            p16,p84=np.percentile(log_s,[16,84]);p025,p975=np.percentile(log_s,[2.5,97.5])
            gg_mu=math.log(float(row['gg_radius']))
            gg_sd=float(row['gg_regime_sigma_lnR'])
            gg_q16,gg_q84=gg_mu+gg_sd*norm.ppf([0.16,0.84])
            gg_q025,gg_q975=gg_mu+gg_sd*norm.ppf([0.025,0.975])
            out={
                'planet':row['planet'],'hostname':row['hostname'],'fold':row['fold'],
                'mass_earth':row['mass_earth'],'radius_earth':row['radius_earth'],
                'gg_radius':row['gg_radius'],'forecaster_median_radius':fc_med,
                'gg_ape':100*abs(math.exp(gg_mu)-observed)/observed,
                'forecaster_ape':100*abs(fc_med-observed)/observed,
                'gg_crps_lnR':crps_norm(gg_mu,gg_sd,log_obs),
                'forecaster_crps_lnR':crps_empirical(log_s,log_obs),
                'gg_nll_lnR':float(-norm.logpdf(log_obs,loc=gg_mu,scale=gg_sd)),
                'forecaster_nll_kde_lnR':kde_nll(log_s,log_obs),
                'gg_cover68':int(gg_q16 <= log_obs <= gg_q84),
                'forecaster_cover68':int(p16 <= log_obs <= p84),
                'gg_cover95':int(gg_q025 <= log_obs <= gg_q975),
                'forecaster_cover95':int(p025 <= log_obs <= p975),
                'forecaster_radius_p025':float(np.exp(p025)),
                'forecaster_radius_p16':float(np.exp(p16)),
                'forecaster_radius_p84':float(np.exp(p84)),
                'forecaster_radius_p975':float(np.exp(p975)),
            }
            results.append(out)
        print(f'Procesados {min(begin+args.chunk,n)}/{n}',flush=True)

    with Path(args.out).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]))
        writer.writeheader();writer.writerows(results)

    def avg(key):return float(np.mean([float(r[key]) for r in results]))
    def med(key):return float(np.median([float(r[key]) for r in results]))
    crps_diff,crps_ci=bootstrap_mean_diff(results,'gg_crps_lnR','forecaster_crps_lnR',args.bootstrap,args.seed+101)
    try:
        package_version=metadata.version('astro-forecaster')
    except metadata.PackageNotFoundError:
        package_version='no disponible (entorno de pruebas)'
    summary={
        'analysis':'Comparación exploratoria GG (predicciones OOF) vs Forecaster 2.0.2 posterior de Chen-Kipping',
        'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),
        'n_planets':n,'n_systems':len(set(r['hostname'] for r in results)),
        'mc_samples_per_planet':args.samples,'seed':args.seed,
        'forecaster_package_version':package_version,
        'gg_mdape_pct':med('gg_ape'),'forecaster_mdape_pct':med('forecaster_ape'),
        'gg_mean_crps_lnR':avg('gg_crps_lnR'),'forecaster_mean_crps_lnR':avg('forecaster_crps_lnR'),
        'mean_crps_delta_gg_minus_fc':crps_diff,'delta_crps_95ci_cluster_bootstrap':crps_ci,
        'gg_cover68_pct':100*avg('gg_cover68'),'forecaster_cover68_pct':100*avg('forecaster_cover68'),
        'gg_cover95_pct':100*avg('gg_cover95'),'forecaster_cover95_pct':100*avg('forecaster_cover95'),
        'gg_mean_nll_lnR_analytic':avg('gg_nll_lnR'),
        'forecaster_mean_nll_lnR_kde_approx':avg('forecaster_nll_kde_lnR'),
        'limitations':[
            'GG se evaluó con pronósticos fuera de pliegue ya guardados; Forecaster usa el posterior publicado, no reajustado.',
            'No se ha excluido posible solapamiento histórico entre los objetos de calibración del Forecaster y el catálogo NASA.',
            'Incertidumbre de masa se aproxima como lognormal a partir de un error relativo simetrizado; ignoramos asimetrías completas.',
            'Se incorpora error de medición del radio al Forecaster para puntuaciones; las sigmas de GG ya estaban guardadas.',
            'NLL Forecaster calculada con KDE sobre muestras, no densidad analítica exacta; interpretación exploratoria.',
            'Bootstrap por sistema es condicional a los ajustes previos y no vuelve a entrenar modelos.',
            'Se eligieron métricas tras explorar datos previamente; prueba exploratoria, no confirmatoria.'
        ],
    }
    Path('RESUMEN_FORECASTER_COMPLETO.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print('\n--- RESUMEN ---',flush=True)
    for k in ('n_planets','gg_mdape_pct','forecaster_mdape_pct','gg_mean_crps_lnR','forecaster_mean_crps_lnR',
              'mean_crps_delta_gg_minus_fc','delta_crps_95ci_cluster_bootstrap',
              'gg_cover68_pct','forecaster_cover68_pct','gg_cover95_pct','forecaster_cover95_pct'):
        print(k,':',summary[k],flush=True)
    print('Listo: '+args.out+' + RESUMEN_FORECASTER_COMPLETO.json',flush=True)

if __name__=='__main__':
    main()
