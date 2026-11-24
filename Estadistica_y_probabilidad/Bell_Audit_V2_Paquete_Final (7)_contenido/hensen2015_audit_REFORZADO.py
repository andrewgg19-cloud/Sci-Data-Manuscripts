#!/usr/bin/env python3
"""
Hensen 2015 Bell-test audit REFORZADO v2.0
Combina auditoria original + mejoras propuestas.

Novedades v2:
- No-signaling test (P(x|a,b)=P(x|a), P(y|a,b)=P(y|b))
- RNG randomness: uniformidad, runs test, autocorrelación
- Aceptación diaria vs S diario (Spearman) - bandera roja post-selección
- Look-elsewhere / corrección por búsqueda en grilla (Bonferroni, FDR, % robustez)
- Todo lo anterior: baseline, Taylor, bootstrap, offset MC, Kalman, cyclic, Kolmogorov, superficies 3D

Mantiene postura metodológica: sensibilidad es propiedad matemática del pipeline, no prueba fraude.
"""

from __future__ import annotations
import argparse, json, math, sys, urllib.request, zipfile, zlib
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np

DATASET_DOI = "10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31"
DATASET_URL = "https://data.4tu.nl/ndownloader/items/e8cf2991-3153-48ad-b67d-dfd7d7d97fd3/versions/1"
PAPER_DOI = "10.1038/nature15759"

INTERPRETATION_LIMITS = {
    "reproduced_facts": [
        "El valor CHSH base es reproducible desde el dataset abierto oficial.",
        "S y p-value varían materialmente a través de la grilla escaneada de timing.",
        "La violación es reproducible pero no invariante en esa familia de parámetros.",
        "Los tests de no-signaling y uniformidad de settings son verificables en el open data."
    ],
    "hypotheses_not_established_as_facts": [
        "Sensibilidad a timing puede indicar dependencia observacional del pipeline.",
        "Sensibilidad sola no prueba artefacto de post-selección, fraude, ni invalidez global.",
        "Correlación aceptación vs S diaria sugeriría dependencia pero no prueba causalidad."
    ],
    "hard_limits_of_the_open_data": [
        "Auditoría cubre pipeline open-data, no flujo crudo completo de intentos físicos.",
        "No puede decidir si sensibilidad es esperada o problema metodológico sin más datos primarios.",
        "No puede adjudicar entre violación Bell genuina vs selección sin datos adicionales.",
        "Comparativa con Giustina/Shalm 2015 requiere sus datasets para calibración cruzada."
    ],
    "mathematical_minimum_statement": [
        "S(theta) con theta=(offset event-ready, longitud ventana readout). Derivada parcial no cero en región explorada.",
        "No-signaling y uniformidad son propiedades estadísticas comprobables del pipeline filtrado."
    ],
    "unknowns": [
        "Si patrón de sensibilidad desaparece en flujo raw completo.",
        "Si es metodológicamente serio para cambiar interpretación física."
    ],
    "relevant_primary_sources": [
        f"Hensen et al. 2015 DOI {PAPER_DOI}",
        f"Dataset DOI {DATASET_DOI}",
        "Giustina et al. 2015, Shalm et al. 2015 para comparación"
    ]
}

@dataclass
class BaselineResult:
    candidate_rows: int; bell_trials: int; k: int; p_value: float; S: float; S_error: float; settings_counts: list[int]

@dataclass
class TaylorResult:
    parameter: str; nominal_value_ps: int; delta_ps: int; S_minus: float; S_0: float; S_plus: float
    first_derivative_per_ps: float; second_derivative_per_ps2: float

@dataclass
class MonteCarloBootstrapResult:
    replicates: int; mean_S: float; sd_S: float; q05: float; q50: float; q95: float; prob_S_gt_2: float

@dataclass
class MonteCarloOffsetResult:
    replicates: int; offset_min_ps: int; offset_max_ps: int; mean_S: float; sd_S: float
    min_S: float; max_S: float; prob_S_gt_2: float; min_bell_trials: int; max_bell_trials: int

@dataclass
class KalmanResult:
    q_mle: float; obs_rate_min: float; obs_rate_max: float; smooth_rate_min: float; smooth_rate_max: float
    smooth_first3: list[float]; smooth_last3: list[float]; corr_acceptance_vs_win_fraction: float; day_table: list[dict]

@dataclass
class KolmogorovProxyResult:
    n: int; rate: float; observed_compression_ratio: float; shuffle_mean: float; shuffle_sd: float
    shuffle_q05: float; shuffle_q95: float; bernoulli_mean: float; bernoulli_sd: float; bernoulli_q05: float
    bernoulli_q95: float; p_shuffle_le_observed: float; p_bernoulli_le_observed: float

@dataclass
class CyclicVectorResult:
    vector: list[float]; mean: float; cyclic_break_index: float; fourier_modes_abs: list[float]; mode1_to_mode0: float; mode2_to_mode0: float

@dataclass
class CyclicInvarianceResult:
    settings_counts: CyclicVectorResult; win_rates: CyclicVectorResult; e_values: CyclicVectorResult
    counts_chi2_uniform: float; counts_uniform_mc_p: float

# NUEVOS dataclasses v2
@dataclass
class NoSignalingResult:
    chi2_A: float; p_A: float; chi2_B: float; p_B: float
    chi2_joint: float; p_joint: float
    table_A: list[list[int]]  # P(x|a,b)
    table_B: list[list[int]]  # P(y|a,b)
    detail: list[dict]

@dataclass
class RNGResult:
    uniform_chi2_A: float; uniform_p_A: float; uniform_chi2_B: float; uniform_p_B: float
    joint_chi2: float; joint_p: float
    runs_A: dict; runs_B: dict
    autocorr_A_lag1: float; autocorr_B_lag1: float
    counts_A: list[int]; counts_B: list[int]; counts_joint: list[int]

@dataclass
class AcceptanceVsSResult:
    spearman_r: float; pearson_r: float
    n_days: int
    slope: float
    interpretation: str
    per_day: list[dict]

@dataclass
class LookElsewhereResult:
    S_min: float; S_max: float; S_span: float
    p_min: float; p_max: float
    pct_S_gt_2: float; pct_S_gt_2_2: float; pct_S_gt_2_4: float
    pct_p_lt_0_05: float; pct_p_lt_0_01: float
    bonferroni_p_min_corrected: float
    fdr_significant_cells: int
    total_valid_cells: int
    interpretation: str

def binom_sf(k_minus_1: int, n: int, p: float) -> float:
    total = 0.0
    for k in range(k_minus_1 + 1, n + 1):
        total += math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))
    return total

def download_and_extract_dataset(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    outer_zip = out_dir / "hensen2015_dataset_outer.zip"
    inner_zip = out_dir / "data.zip"
    extract_dir = out_dir / "hensen2015_dataset"
    if not extract_dir.exists():
        urllib.request.urlretrieve(DATASET_URL, outer_zip)
        with zipfile.ZipFile(outer_zip) as zf:
            zf.extract("data.zip", path=out_dir)
        with zipfile.ZipFile(inner_zip) as zf:
            zf.extractall(path=extract_dir)
    data_file = extract_dir / "bell_open_data.txt"
    if not data_file.exists():
        raise FileNotFoundError(f"No encontrado: {data_file}")
    return data_file

def load_open_data(data_file: Path):
    timestamps = np.loadtxt(data_file, delimiter=",", usecols=[0], dtype="datetime64[us]")
    data = np.loadtxt(data_file, delimiter=",", usecols=np.arange(1, 17), dtype=np.int64)
    return timestamps, data

def compute_pipeline(data: np.ndarray, offset_ps: int = 0, readout_window_length: int = 3700) -> dict:
    (day_number, run_number, event_ready_click1_time, event_ready_click1_channel,
     event_ready_click2_time, event_ready_click2_channel, random_number_A, random_number_B,
     random_number_A_time, random_number_B_time, readout_click_A_time, readout_click_B_time,
     click_after_excite_A_time, click_after_excite_B_time, last_invalid_marker_A, last_invalid_marker_B) = data.T

    start0 = 5426350 + offset_ps
    start1 = 5425700 + offset_ps
    event_ready_window_length = 55000 - 2550
    event_ready_window_separation = 250000
    readout_window_start = 10620
    invalid_marker_lookback = 250

    w1c0 = (start0 <= event_ready_click1_time) & (event_ready_click1_time < (start0 + event_ready_window_length)) & (event_ready_click1_channel == 0)
    w1c1 = (start1 <= event_ready_click1_time) & (event_ready_click1_time < (start1 + event_ready_window_length)) & (event_ready_click1_channel == 1)
    w2c0 = (start0 + event_ready_window_separation <= event_ready_click2_time) & (event_ready_click2_time < (start0 + event_ready_window_separation + event_ready_window_length)) & (event_ready_click2_channel == 0)
    w2c1 = (start1 + event_ready_window_separation <= event_ready_click2_time) & (event_ready_click2_time < (start1 + event_ready_window_separation + event_ready_window_length)) & (event_ready_click2_channel == 1)

    event_ready_window_filter = (w1c0 | w1c1) & (w2c0 | w2c1) & (event_ready_click1_channel != event_ready_click2_channel)
    no_invalid_marker = ((last_invalid_marker_A == 0) | (last_invalid_marker_A > invalid_marker_lookback)) & ((last_invalid_marker_B == 0) | (last_invalid_marker_B > invalid_marker_lookback))
    no_excitation_click = (click_after_excite_A_time == 0) & (click_after_excite_B_time == 0)
    bell_trial_filter = event_ready_window_filter & no_invalid_marker & no_excitation_click

    detection_A = (readout_click_A_time > readout_window_start) & (readout_click_A_time <= readout_window_start + readout_window_length)
    detection_B = (readout_click_B_time > readout_window_start) & (readout_click_B_time <= readout_window_start + readout_window_length)

    a_i = random_number_A; b_i = random_number_B
    x_i = detection_A.astype(np.int64) * 2 - 1
    y_i = detection_B.astype(np.int64) * 2 - 1
    t_i = bell_trial_filter.astype(np.int64)

    n = int(t_i.sum())
    c_i = t_i * (((-1) ** (a_i * b_i) * (x_i * y_i) + 1) / 2)
    k = int(c_i.sum())
    tau = 5.4e-6 * 2; ksi = 3.0/4.0 + 3.0*(tau + tau**2)
    p_value = binom_sf(k-1, n, ksi)

    inputs_ab = [(0,0),(0,1),(1,0),(1,1)]
    outputs_xy = [(+1,+1),(+1,-1),(-1,+1),(-1,-1)]
    correlation_matrix = np.zeros((4,4), dtype=np.int64)
    xy_corr = np.full(4, np.nan, dtype=float); xy_err = np.full(4, np.nan, dtype=float)

    for i,(a,b) in enumerate(inputs_ab):
        for j,(x,y) in enumerate(outputs_xy):
            correlation_matrix[i,j] = int(np.sum(bell_trial_filter & (a_i==a) & (b_i==b) & (x_i==x) & (y_i==y)))
        denom = int(np.sum(correlation_matrix[i,:]))
        if denom==0: continue
        numerator = correlation_matrix[i,0] - correlation_matrix[i,1] - correlation_matrix[i,2] + correlation_matrix[i,3]
        xy_corr[i] = numerator / float(denom)
        xy_err[i] = math.sqrt(max(0.0, 1.0 - xy_corr[i]**2) / float(denom))

    settings_counts = [int(np.sum(correlation_matrix[i,:])) for i in range(4)]
    valid_chsh = bool(np.all(np.isfinite(xy_corr)))
    S = float(xy_corr[0]+xy_corr[1]+xy_corr[2]-xy_corr[3]) if valid_chsh else float("nan")
    S_error = float(math.sqrt(np.sum(xy_err**2))) if valid_chsh else float("nan")

    return {"day_number":day_number,"a_i":a_i,"b_i":b_i,"x_i":x_i,"y_i":y_i,"t_i":t_i,"bell_filter":bell_trial_filter,
            "correlation_matrix":correlation_matrix,"xy_corr":xy_corr,"xy_err":xy_err,"settings_counts":settings_counts,
            "n":n,"k":k,"p_value":p_value,"S":S,"S_error":S_error,"valid_chsh":valid_chsh}

def taylor_sensitivity(data, nominal_ps, delta_ps):
    minus = compute_pipeline(data, offset_ps=nominal_ps-delta_ps)
    center = compute_pipeline(data, offset_ps=nominal_ps)
    plus = compute_pipeline(data, offset_ps=nominal_ps+delta_ps)
    vals = np.array([minus["S"], center["S"], plus["S"]], dtype=float)
    if not np.all(np.isfinite(vals)): raise ValueError("Config sin 4 settings")
    first = (vals[2]-vals[0])/(2.0*delta_ps); second = (vals[2]-2*vals[1]+vals[0])/float(delta_ps**2)
    return TaylorResult("event_ready_offset_ps", nominal_ps, delta_ps, float(vals[0]), float(vals[1]), float(vals[2]), float(first), float(second))

def monte_carlo_bootstrap(rng, pipeline, replicates):
    valid = np.where(pipeline["bell_filter"])[0]
    obs = np.column_stack([pipeline["a_i"][valid], pipeline["b_i"][valid], pipeline["x_i"][valid], pipeline["y_i"][valid]])
    strata=[]
    for a,b in [(0,0),(0,1),(1,0),(1,1)]:
        s=obs[(obs[:,0]==a)&(obs[:,1]==b)]
        if len(s)==0: raise ValueError(f"Sin trials para ({a},{b})")
        strata.append(s)
    S_values=np.empty(replicates)
    for i in range(replicates):
        E=np.empty(4)
        for j,stratum in enumerate(strata):
            samp=stratum[rng.integers(0,len(stratum),size=len(stratum))]
            E[j]=float(np.mean(samp[:,2]*samp[:,3]))
        S_values[i]=E[0]+E[1]+E[2]-E[3]
    return MonteCarloBootstrapResult(replicates,float(np.mean(S_values)),float(np.std(S_values,ddof=1)),
                                     float(np.quantile(S_values,0.05)),float(np.quantile(S_values,0.5)),float(np.quantile(S_values,0.95)),
                                     float(np.mean(S_values>2.0)))

def monte_carlo_offset(rng, data, replicates, offset_min_ps, offset_max_ps):
    S_values=[]; n_values=[]
    for _ in range(replicates):
        offset=int(rng.integers(offset_min_ps, offset_max_ps+1))
        res=compute_pipeline(data, offset_ps=offset)
        if not res["valid_chsh"]: continue
        S_values.append(float(res["S"])); n_values.append(int(res["n"]))
    if len(S_values)<2: raise ValueError("Menos de 2 configs válidas")
    S_arr=np.asarray(S_values); n_arr=np.asarray(n_values)
    return MonteCarloOffsetResult(len(S_values),offset_min_ps,offset_max_ps,float(np.mean(S_arr)),float(np.std(S_arr,ddof=1)),
                                  float(np.min(S_arr)),float(np.max(S_arr)),float(np.mean(S_arr>2.0)),int(np.min(n_arr)),int(np.max(n_arr)))

def kalman_daily_acceptance(pipeline):
    day_number=pipeline["day_number"]; bell=pipeline["bell_filter"]; a_i=pipeline["a_i"]; b_i=pipeline["b_i"]; x_i=pipeline["x_i"]; y_i=pipeline["y_i"]
    unique_days=sorted(np.unique(day_number))
    rows_per_day=np.array([(day_number==d).sum() for d in unique_days],float)
    acc_per_day=np.array([np.sum(bell&(day_number==d)) for d in unique_days],float)
    y_obs=acc_per_day/rows_per_day; r_obs=np.maximum(y_obs*(1-y_obs)/rows_per_day,1e-8)
    q_grid=np.logspace(-8,-3,200)
    def loglike(q):
        x=y_obs[0]; P=r_obs[0]+q; total=0.0
        for t in range(len(y_obs)):
            if t>0: P=P+q
            e=y_obs[t]-x; S=P+r_obs[t]; total+=-0.5*(math.log(2*math.pi*S)+(e*e)/S); K=P/S; x=x+K*e; P=(1-K)*P
        return total
    lls=np.array([loglike(q) for q in q_grid]); q_mle=float(q_grid[np.argmax(lls)])
    x_f=np.zeros(len(y_obs)); P_f=np.zeros(len(y_obs)); x_pred=np.zeros(len(y_obs)); P_pred=np.zeros(len(y_obs))
    x=y_obs[0]; P=r_obs[0]+q_mle
    for t in range(len(y_obs)):
        xp=x; Pp=P+q_mle if t>0 else P; x_pred[t]=xp; P_pred[t]=Pp; e=y_obs[t]-xp; S=Pp+r_obs[t]; K=Pp/S; x=xp+K*e; P=(1-K)*Pp; x_f[t]=x; P_f[t]=P
    x_s=x_f.copy(); P_s=P_f.copy()
    for t in range(len(y_obs)-2,-1,-1):
        C=P_f[t]/P_pred[t+1]; x_s[t]=x_f[t]+C*(x_s[t+1]-x_pred[t+1]); P_s[t]=P_f[t]+C*C*(P_s[t+1]-P_pred[t+1])
    win_fraction=[]
    for d in unique_days:
        mask=bell&(day_number==d)
        if np.sum(mask)==0: win_fraction.append(np.nan); continue
        vals=(((-1)**(a_i[mask]*b_i[mask])*(x_i[mask]*y_i[mask])+1)/2); win_fraction.append(float(np.mean(vals)))
    win_fraction=np.array(win_fraction,float); valid=np.isfinite(win_fraction)
    corr=float(np.corrcoef(y_obs[valid],win_fraction[valid])[0,1]) if np.sum(valid)>=2 else float("nan")
    day_table=[]
    for d,rows,acc,y_raw,y_smooth,w in zip(unique_days,rows_per_day,acc_per_day,y_obs,x_s,win_fraction):
        day_table.append({"day":int(d),"candidate_rows":int(rows),"accepted_trials":int(acc),"acceptance_rate_observed":float(y_raw),"acceptance_rate_smoothed":float(y_smooth),"win_fraction":None if not np.isfinite(w) else float(w)})
    return KalmanResult(q_mle,float(np.min(y_obs)),float(np.max(y_obs)),float(np.min(x_s)),float(np.max(x_s)),[float(v) for v in x_s[:3]],[float(v) for v in x_s[-3:]],corr,day_table)

def cyclic_vector_metrics(vector):
    arr=np.asarray(vector,float); F=np.fft.fft(arr)
    break_energy=float(np.sum(np.abs(F[1:])**2)); total_energy=float(np.sum(np.abs(F)**2))
    break_index=math.sqrt(break_energy/total_energy) if total_energy>0 else float("nan"); f0=abs(F[0])
    return CyclicVectorResult([float(v) for v in arr],float(np.mean(arr)),float(break_index),[float(abs(z)) for z in F],float(abs(F[1])/f0) if f0 else float("nan"),float(abs(F[2])/f0) if f0 else float("nan"))

def cyclic_invariance_audit(rng, pipeline, mc_replicates=200000):
    correlation_matrix=pipeline["correlation_matrix"]; settings_counts=np.sum(correlation_matrix,axis=1).astype(float)
    if np.any(settings_counts==0): raise ValueError("Cyclic requiere 4 settings")
    N=int(np.sum(settings_counts)); expected=N/4.0; chi2=float(np.sum((settings_counts-expected)**2/expected))
    sims=rng.multinomial(N,[0.25]*4,size=mc_replicates); chi2_sims=np.sum((sims-expected)**2/expected,axis=1); p_mc=float(np.mean(chi2_sims>=chi2))
    win_counts=np.array([correlation_matrix[0,0]+correlation_matrix[0,3],correlation_matrix[1,0]+correlation_matrix[1,3],correlation_matrix[2,0]+correlation_matrix[2,3],correlation_matrix[3,1]+correlation_matrix[3,2]],float)
    win_rates=win_counts/settings_counts
    e_values=np.array([(row[0]-row[1]-row[2]+row[3])/float(np.sum(row)) for row in correlation_matrix],float)
    return CyclicInvarianceResult(cyclic_vector_metrics(settings_counts),cyclic_vector_metrics(win_rates),cyclic_vector_metrics(e_values),chi2,p_mc)

def compression_ratio(bits):
    payload="".join("1" if v else "0" for v in bits.astype(np.int8)).encode("ascii")
    return len(zlib.compress(payload,9))/len(payload)

def kolmogorov_proxy(rng, bits, replicates):
    bits=bits.astype(np.int8); n=len(bits); rate=float(np.mean(bits)); ones=int(np.sum(bits)); observed=compression_ratio(bits)
    shuffle=np.empty(replicates,float); bernoulli=np.empty(replicates,float); base=np.zeros(n,dtype=np.int8); base[:ones]=1
    for i in range(replicates):
        shuffled=base.copy(); rng.shuffle(shuffled); shuffle[i]=compression_ratio(shuffled); bern=(rng.random(n)<rate).astype(np.int8); bernoulli[i]=compression_ratio(bern)
    return KolmogorovProxyResult(n,rate,float(observed),float(np.mean(shuffle)),float(np.std(shuffle,ddof=1)),float(np.quantile(shuffle,0.05)),float(np.quantile(shuffle,0.95)),float(np.mean(bernoulli)),float(np.std(bernoulli,ddof=1)),float(np.quantile(bernoulli,0.05)),float(np.quantile(bernoulli,0.95)),float(np.mean(shuffle<=observed)),float(np.mean(bernoulli<=observed)))

def build_surface_scan(data, offset_values, readout_values):
    offset_values=np.asarray(offset_values,int); readout_values=np.asarray(readout_values,int)
    grid_offset,grid_readout=np.meshgrid(offset_values,readout_values,indexing="xy")
    S_grid=np.empty_like(grid_offset,float); p_grid=np.empty_like(grid_offset,float); n_grid=np.empty_like(grid_offset,float)
    for i,readout in enumerate(readout_values):
        for j,offset in enumerate(offset_values):
            res=compute_pipeline(data,offset_ps=int(offset),readout_window_length=int(readout)); S_grid[i,j]=res["S"]; p_grid[i,j]=res["p_value"]; n_grid[i,j]=res["n"]
    return {"offset_values_ps":offset_values,"readout_values":readout_values,"offset_grid_ps":grid_offset,"readout_grid":grid_readout,"S_grid":S_grid,"p_value_grid":p_grid,"bell_trials_grid":n_grid}

# ============ NUEVAS FUNCIONES v2 REFORZADO ============

def no_signaling_test(pipeline) -> NoSignalingResult:
    """Test no-signaling: P_A(x|a,b) = P_A(x|a) y P_B(y|a,b)=P_B(y|b)"""
    cm = pipeline["correlation_matrix"]  # 4x4: rows ab, cols xy
    # Reconstruir conteos marginales
    # ab index: 0=00,1=01,2=10,3=11 ; xy: 0=++,1=+-,2=-+,3=--
    # Para Alice: x=+1 es col 0,1 ; x=-1 es 2,3
    # Contingencia: para cada a, comparar distribución de x entre b=0 vs b=1
    from math import isnan
    # Tabla A: rows: (a,b) ; cols: x=+1, x=-1
    table_A = []
    for i,(a,b) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
        x_plus = cm[i,0]+cm[i,1]; x_minus = cm[i,2]+cm[i,3]; table_A.append([int(x_plus), int(x_minus)])
    # Tabla B: y=+1 es col 0,2 ; y=-1 es 1,3
    table_B = []
    for i in range(4):
        y_plus = cm[i,0]+cm[i,2]; y_minus = cm[i,1]+cm[i,3]; table_B.append([int(y_plus), int(y_minus)])
    
    def chi2_2x2(n11,n12,n21,n22):
        n = n11+n12+n21+n22
        if n==0: return 0.0, 1.0
        r1=n11+n12; r2=n21+n22; c1=n11+n21; c2=n12+n22
        if r1==0 or r2==0 or c1==0 or c2==0: return 0.0, 1.0
        e11=r1*c1/n; e12=r1*c2/n; e21=r2*c1/n; e22=r2*c2/n
        chi2 = (n11-e11)**2/e11 + (n12-e12)**2/e12 + (n21-e21)**2/e21 + (n22-e22)**2/e22
        # p-value chi2 1dof
        # aproximación usando erf: p = exp(-chi2/2) *... simplificamos usando survival
        # usamos aproximación: p = 1 - CDF, con erfc
        # para 1 dof, p = erfc(sqrt(chi2/2))
        import mpmath as _mp
        try:
            p = float(math.erfc(math.sqrt(chi2/2.0)))
        except:
            # fallback sin mpmath
            p = math.exp(-chi2/2.0) if chi2>0 else 1.0
        return chi2, p

    # Alice: compara b=0 vs b=1 para cada a
    chi2_A_total=0; detail=[]
    # a=0: rows 0 vs 1
    c,p = chi2_2x2(table_A[0][0],table_A[0][1],table_A[1][0],table_A[1][1])
    chi2_A_total+=c; detail.append({"test":"Alice a=0: b=0 vs b=1","chi2":c,"p":p,"counts":[table_A[0],table_A[1]]})
    c,p = chi2_2x2(table_A[2][0],table_A[2][1],table_A[3][0],table_A[3][1])
    chi2_A_total+=c; detail.append({"test":"Alice a=1: b=0 vs b=1","chi2":c,"p":p,"counts":[table_A[2],table_A[3]]})
    # Bob: a=0 vs a=1 para cada b
    chi2_B_total=0
    c,p = chi2_2x2(table_B[0][0],table_B[0][1],table_B[2][0],table_B[2][1])
    chi2_B_total+=c; detail.append({"test":"Bob b=0: a=0 vs a=1","chi2":c,"p":p,"counts":[table_B[0],table_B[2]]})
    c,p = chi2_2x2(table_B[1][0],table_B[1][1],table_B[3][0],table_B[3][1])
    chi2_B_total+=c; detail.append({"test":"Bob b=1: a=0 vs a=1","chi2":c,"p":p,"counts":[table_B[1],table_B[3]]})

    # p-values aproximados para 2 dof: p = exp(-chi2/2)*(1+chi2/2)
    def p_chi2_2dof(chi2):
        return math.exp(-chi2/2.0)*(1+chi2/2.0) if chi2>=0 else 1.0
    def p_chi2_4dof(chi2):
        return math.exp(-chi2/2.0)*(1+chi2/2.0+chi2*chi2/8.0) if chi2>=0 else 1.0

    p_A = p_chi2_2dof(chi2_A_total); p_B = p_chi2_2dof(chi2_B_total)
    chi2_joint = chi2_A_total+chi2_B_total; p_joint = p_chi2_4dof(chi2_joint)

    return NoSignalingResult(chi2_A_total,p_A,chi2_B_total,p_B,chi2_joint,p_joint,table_A,table_B,detail)

def rng_randomness_test(pipeline) -> RNGResult:
    a_i=pipeline["a_i"][pipeline["bell_filter"]]; b_i=pipeline["b_i"][pipeline["bell_filter"]]
    # Uniformidad
    cnt_A0=int(np.sum(a_i==0)); cnt_A1=int(np.sum(a_i==1))
    cnt_B0=int(np.sum(b_i==0)); cnt_B1=int(np.sum(b_i==1))
    n=len(a_i)
    exp=n/2.0
    chi2_A = (cnt_A0-exp)**2/exp + (cnt_A1-exp)**2/exp if exp>0 else 0
    chi2_B = (cnt_B0-exp)**2/exp + (cnt_B1-exp)**2/exp if exp>0 else 0
    # joint 4 combos
    cnt_00=int(np.sum((a_i==0)&(b_i==0))); cnt_01=int(np.sum((a_i==0)&(b_i==1))); cnt_10=int(np.sum((a_i==1)&(b_i==0))); cnt_11=int(np.sum((a_i==1)&(b_i==1)))
    exp_joint=n/4.0
    chi2_joint = sum((c-exp_joint)**2/exp_joint for c in [cnt_00,cnt_01,cnt_10,cnt_11]) if exp_joint>0 else 0
    # p-values chi2 1dof y 3dof aprox
    def p_1dof(chi2): return math.erfc(math.sqrt(chi2/2.0)) if chi2>=0 else 1.0
    def p_3dof(chi2): return math.exp(-chi2/2.0)*(1+chi2/2.0+0) if chi2>=0 else 1.0 # simplificada, usamos aprox 3dof
    # runs test
    def runs_test(bits):
        n=len(bits)
        if n<2: return {"runs":0,"expected":0,"z":0,"p":1}
        runs=1
        for i in range(1,n):
            if bits[i]!=bits[i-1]: runs+=1
        p0=np.mean(bits); exp_runs=2*n*p0*(1-p0)+1
        var = (2*n*p0*(1-p0)*(2*n*p0*(1-p0)-n))/((n-1)) if n>1 else 1
        var = max(var,1e-8)
        z=(runs-exp_runs)/math.sqrt(var)
        p=math.erfc(abs(z)/math.sqrt(2))
        return {"runs":int(runs),"expected":float(exp_runs),"z":float(z),"p":float(p)}
    runs_A=runs_test(a_i); runs_B=runs_test(b_i)
    # autocorr lag1
    def autocorr_lag1(bits):
        if len(bits)<3: return 0.0
        m=np.mean(bits); denom=np.sum((bits-m)**2)
        if denom==0: return 0.0
        num=np.sum((bits[:-1]-m)*(bits[1:]-m)); return float(num/denom)
    ac_A=autocorr_lag1(a_i.astype(float)); ac_B=autocorr_lag1(b_i.astype(float))
    return RNGResult(chi2_A,p_1dof(chi2_A),chi2_B,p_1dof(chi2_B),chi2_joint,p_3dof(chi2_joint),runs_A,runs_B,ac_A,ac_B,[cnt_A0,cnt_A1],[cnt_B0,cnt_B1],[cnt_00,cnt_01,cnt_10,cnt_11])

def acceptance_vs_S_daily(pipeline) -> AcceptanceVsSResult:
    day_number=pipeline["day_number"]; bell=pipeline["bell_filter"]; a_i=pipeline["a_i"]; b_i=pipeline["b_i"]; x_i=pipeline["x_i"]; y_i=pipeline["y_i"]
    unique_days=sorted(np.unique(day_number))
    per_day=[]
    for d in unique_days:
        mask_all=(day_number==d)
        mask_bell=bell & mask_all
        rows=int(np.sum(mask_all)); acc=int(np.sum(mask_bell))
        acc_rate=acc/rows if rows>0 else 0
        if acc<4: continue
        # S diario si hay 4 settings
        cm=np.zeros((4,4),int)
        for idx,(a,b) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
            for j,(x,y) in enumerate([(1,1),(1,-1),(-1,1),(-1,-1)]):
                cm[idx,j]=int(np.sum(mask_bell & (a_i==a)&(b_i==b)&(x_i==x)&(y_i==y)))
        settings_counts=[int(np.sum(cm[i,:])) for i in range(4)]
        if any(c==0 for c in settings_counts): continue
        E=[(row[0]-row[1]-row[2]+row[3])/float(np.sum(row)) for row in cm]
        S=E[0]+E[1]+E[2]-E[3]
        per_day.append({"day":int(d),"acceptance_rate":float(acc_rate),"S":float(S),"trials":int(acc)})
    if len(per_day)>=3:
        acc_rates=np.array([x["acceptance_rate"] for x in per_day]); S_vals=np.array([x["S"] for x in per_day])
        # Pearson
        pearson=np.corrcoef(acc_rates,S_vals)[0,1] if len(per_day)>=2 else float("nan")
        # Spearman (rank)
        def spearman(x,y):
            rx=np.argsort(np.argsort(x)); ry=np.argsort(np.argsort(y))
            return np.corrcoef(rx,ry)[0,1]
        spear=spearman(acc_rates,S_vals)
        slope=np.polyfit(acc_rates,S_vals,1)[0] if len(per_day)>=2 else float("nan")
        if abs(spear)>0.6:
            interp="Correlación fuerte aceptación vs S diaria - posible bandera roja, revisar dependencia pipeline"
        elif abs(spear)>0.3:
            interp="Correlación moderada - monitorear"
        else:
            interp="Sin correlación relevante - no hay indicio de post-selección por día"
    else:
        pearson=float("nan"); spear=float("nan"); slope=float("nan"); interp="Insuficientes días con S definido"
    return AcceptanceVsSResult(float(spear) if 'spear' in locals() else float("nan"), float(pearson) if 'pearson' in locals() else float("nan"), len(per_day), float(slope) if 'slope' in locals() else float("nan"), interp, per_day)

def look_elsewhere_correction(surface_scan: dict) -> LookElsewhereResult:
    S_grid=surface_scan["S_grid"]; p_grid=surface_scan["p_value_grid"]
    valid=np.isfinite(S_grid)
    total=int(np.sum(valid))
    if total==0:
        return LookElsewhereResult(float("nan"),float("nan"),float("nan"),float("nan"),float("nan"),0,0,0,0,0,float("nan"),0,0,"Sin celdas válidas")
    S_valid=S_grid[valid]; p_valid=p_grid[valid]
    S_min=float(np.min(S_valid)); S_max=float(np.max(S_valid)); p_min=float(np.min(p_valid)); p_max=float(np.max(p_valid))
    pct_S_gt_2=float(np.mean(S_valid>2.0))*100; pct_S_gt_2_2=float(np.mean(S_valid>2.2))*100; pct_S_gt_2_4=float(np.mean(S_valid>2.4))*100
    pct_p_lt_05=float(np.mean(p_valid<0.05))*100; pct_p_lt_01=float(np.mean(p_valid<0.01))*100
    bonf_p = min(1.0, p_min*total)
    # FDR Benjamini-Hochberg q=0.05
    sorted_p=np.sort(p_valid); n=len(sorted_p); fdr_count=0
    for i,pp in enumerate(sorted_p):
        if pp <= (i+1)/n * 0.05: fdr_count=i+1
    if pct_S_gt_2>80:
        interp=f"Robusto: {pct_S_gt_2:.1f}% de celdas violan CHSH (>2). Sensibilidad existe pero violación persiste."
    elif pct_S_gt_2>50:
        interp=f"Moderadamente robusto: {pct_S_gt_2:.1f}% viola. S varía pero mayoría sigue >2."
    else:
        interp=f"Frágil: solo {pct_S_gt_2:.1f}% viola. Interpretación depende fuertemente de elección de timing."
    return LookElsewhereResult(S_min,S_max,S_max-S_min,p_min,p_max,pct_S_gt_2,pct_S_gt_2_2,pct_S_gt_2_4,pct_p_lt_05,pct_p_lt_01,bonf_p,fdr_count,total,interp)

def generate_surface_artifacts(data, plot_dir, offset_values, readout_values):
    plot_dir.mkdir(parents=True, exist_ok=True)
    scan=build_surface_scan(data, offset_values, readout_values)
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        def save_plot(path,x_grid,y_grid,z_grid,z_label,title):
            fig=plt.figure(figsize=(9,6)); ax=fig.add_subplot(111,projection="3d")
            surf=ax.plot_surface(x_grid,y_grid,z_grid,cmap="viridis",linewidth=0.2,edgecolor=(0.1,0.1,0.1,0.3),antialiased=True)
            ax.set_xlabel("offset_ps"); ax.set_ylabel("readout"); ax.set_zlabel(z_label); ax.set_title(title)
            fig.colorbar(surf,ax=ax,shrink=0.6); fig.tight_layout(); fig.savefig(path,dpi=200); plt.close(fig)
        save_plot(plot_dir/"surface_S.png",scan["offset_grid_ps"],scan["readout_grid"],scan["S_grid"],"S","CHSH S")
        save_plot(plot_dir/"surface_p.png",scan["offset_grid_ps"],scan["readout_grid"],scan["p_value_grid"],"p-value","p-value")
        save_plot(plot_dir/"surface_n.png",scan["offset_grid_ps"],scan["readout_grid"],scan["bell_trials_grid"],"Bell trials","Bell trials")
        artifacts={"surface_S":str(plot_dir/"surface_S.png")}
    except Exception as e:
        artifacts={"error":str(e)}
    return {
        "offset_range_ps":[int(np.min(offset_values)),int(np.max(offset_values))],
        "readout_range":[int(np.min(readout_values)),int(np.max(readout_values))],
        "grid_shape":[int(scan["S_grid"].shape[0]),int(scan["S_grid"].shape[1])],
        "S_min":float(np.nanmin(scan["S_grid"])),"S_max":float(np.nanmax(scan["S_grid"])),
        "artifacts":artifacts,
        "_scan":scan  # interno para look-elsewhere
    }

def main():
    parser=argparse.ArgumentParser(description="Audit Hensen 2015 REFORZADO v2")
    parser.add_argument("--data-file",default="",help="bell_open_data.txt")
    parser.add_argument("--download-dir",default="hensen2015_dataset_cache")
    parser.add_argument("--seed",type=int,default=20260727)
    parser.add_argument("--taylor-delta-ps",type=int,default=100)
    parser.add_argument("--mc-bootstrap",type=int,default=20000)
    parser.add_argument("--mc-offset",type=int,default=4000)
    parser.add_argument("--mc-offset-min-ps",type=int,default=-3000)
    parser.add_argument("--mc-offset-max-ps",type=int,default=4000)
    parser.add_argument("--kolmogorov-sims",type=int,default=2000)
    parser.add_argument("--cyclic-mc",type=int,default=200000)
    parser.add_argument("--generate-plots",action="store_true")
    parser.add_argument("--plot-dir",default="hensen2015_surface_plots_v2")
    parser.add_argument("--plot-offset-min-ps",type=int,default=-3000)
    parser.add_argument("--plot-offset-max-ps",type=int,default=4000)
    parser.add_argument("--plot-offset-steps",type=int,default=23)
    parser.add_argument("--plot-readout-min",type=int,default=3000)
    parser.add_argument("--plot-readout-max",type=int,default=4500)
    parser.add_argument("--plot-readout-steps",type=int,default=16)
    parser.add_argument("--json-out",default="")
    args=parser.parse_args()
    rng=np.random.default_rng(args.seed)
    data_file=Path(args.data_file) if args.data_file else download_and_extract_dataset(Path(args.download_dir))
    _, data = load_open_data(data_file)
    baseline_dict=compute_pipeline(data, offset_ps=0, readout_window_length=3700)
    baseline=BaselineResult(len(data),baseline_dict["n"],baseline_dict["k"],float(baseline_dict["p_value"]),float(baseline_dict["S"]),float(baseline_dict["S_error"]),baseline_dict["settings_counts"])
    taylor=taylor_sensitivity(data,0,args.taylor_delta_ps)
    mc_boot=monte_carlo_bootstrap(rng,baseline_dict,args.mc_bootstrap)
    mc_offset=monte_carlo_offset(rng,data,args.mc_offset,args.mc_offset_min_ps,args.mc_offset_max_ps)
    kalman=kalman_daily_acceptance(baseline_dict)
    cyclic=cyclic_invariance_audit(rng,baseline_dict,args.cyclic_mc)
    acceptance_bits=baseline_dict["bell_filter"].astype(np.int8)
    valid_win_bits= (((-1)**(baseline_dict["a_i"]*baseline_dict["b_i"])*(baseline_dict["x_i"]*baseline_dict["y_i"])+1)/2)[baseline_dict["bell_filter"]].astype(np.int8)
    kol_acc=kolmogorov_proxy(rng,acceptance_bits,args.kolmogorov_sims)
    kol_win=kolmogorov_proxy(rng,valid_win_bits,args.kolmogorov_sims)

    # NUEVOS TESTS v2
    nosig=no_signaling_test(baseline_dict)
    rng_test=rng_randomness_test(baseline_dict)
    acc_vs_S=acceptance_vs_S_daily(baseline_dict)

    report={
        "what_was_audited":{"paper_doi":PAPER_DOI,"dataset_doi":DATASET_DOI,"pipeline":"candidate two-photon rows at C -> valid Bell trials -> CHSH","limitation":"Open dataset no es flujo raw completo"},
        "interpretation_limits":INTERPRETATION_LIMITS,
        "baseline":asdict(baseline),
        "taylor":asdict(taylor),
        "monte_carlo_bootstrap":asdict(mc_boot),
        "monte_carlo_offset":asdict(mc_offset),
        "kalman_daily_acceptance":asdict(kalman),
        "cyclic_invariance":asdict(cyclic),
        "kolmogorov_acceptance":asdict(kol_acc),
        "kolmogorov_win":asdict(kol_win),
        "no_signaling":asdict(nosig),
        "rng_randomness":asdict(rng_test),
        "acceptance_vs_S_daily":asdict(acc_vs_S),
    }

    if args.generate_plots:
        offset_values=np.unique(np.rint(np.linspace(args.plot_offset_min_ps,args.plot_offset_max_ps,args.plot_offset_steps)).astype(int))
        readout_values=np.unique(np.rint(np.linspace(args.plot_readout_min,args.plot_readout_max,args.plot_readout_steps)).astype(int))
        surf=generate_surface_artifacts(data,Path(args.plot_dir),offset_values,readout_values)
        scan=surf.pop("_scan",None)
        report["surface_scans"]=surf
        if scan is not None:
            look=look_elsewhere_correction(scan)
            report["look_elsewhere"]=asdict(look)

    print(json.dumps(report,indent=2,allow_nan=True))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report,indent=2,allow_nan=True),encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
