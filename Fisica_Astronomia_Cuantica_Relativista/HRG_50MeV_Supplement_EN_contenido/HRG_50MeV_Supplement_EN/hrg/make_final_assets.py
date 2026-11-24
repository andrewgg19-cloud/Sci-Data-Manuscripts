"""Build final manuscript tables and figures from verified stored outputs.

This script does not repeat the thermal inference or alter its scientific inputs.
"""
from pathlib import Path
import csv
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "calculos_50MeV_cruce" / "data"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
summary = json.loads((DATA / "resumen.json").read_text())
sys.path.insert(0, str(ROOT / "calculos_50MeV_cruce"))
from reconstruct_populations import cosmic_reference
cosmo = cosmic_reference()
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data/cosmological_reference.json").write_text(json.dumps(cosmo, indent=2)+"\n")
states = list(csv.DictReader((DATA / "resultados_50MeV_y_entorno.csv").open()))
species = list(csv.DictReader((DATA / "especies_PDG2025.csv").open()))
curve = list(csv.DictReader((DATA / "curva_R_PDG2025.csv").open()))
crosses = summary["crossover_all_catalogs"]
sens = summary["eta_only_sensitivity"]

def sci(v):
    a, b = f"{float(v):.4e}".split("e")
    return f"${a}\\times10^{{{int(b)}}}$"

for lang in ("es", "en"):
    es = lang == "es"
    caption = ("Estados reconstruidos con PDG2025 y el valor central de $\\eta$. "
               "Las densidades corresponden al volumen físico a cada temperatura; "
               "$R=n_{\\bar B}/\\Delta n_B$." if es else
               "Reconstructed PDG2025 states at the central input $\\eta$. "
               "Densities refer to physical volume at each temperature; "
               "$R=n_{\\bar B}/\\Delta n_B$.")
    out = [r"\begin{table*}[t]\centering\small", "\\caption{" + caption + "}",
           r"\label{tab:states}", r"\setlength{\tabcolsep}{6pt}",
           r"\begin{tabular}{rrrrrr}\toprule",
           r"$T$ (MeV) & $n_B$ (cm$^{-3}$) & $n_{\bar B}$ (cm$^{-3}$) & $\Delta n_B$ (cm$^{-3}$) & $R$ & $\mu_B/T$\\\midrule"]
    selected = [r for r in states if r["catalog"] == "PDG2025" and
                (r["point"] == "crossover" or float(r["T_MeV"]) in (50.,45.,40.,37.))]
    selected.sort(key=lambda r: -float(r["T_MeV"]))
    for r in selected:
        t = float(r["T_MeV"])
        tstr = f"{t:.6f}" if r["point"] == "crossover" else f"{t:.1f}"
        out.append(" & ".join([tstr, sci(r["n_B_cm3"]), sci(r["n_antiB_cm3"]),
                               sci(r["n_net_cm3"]),f"{float(r['R_antibaryon_to_net']):.6f}",
                               f"{float(r['muB_over_T']):.6f}"]) + r"\\")
    out += [r"\bottomrule\end{tabular}", r"\end{table*}"]
    (ROOT / f"table_states_{lang}.tex").write_text("\n".join(out) + "\n")

    caption = ("Nucleones y sus antipartículas a 50 MeV, PDG2025. "
               "La densidad se expresa en unidades de $10^{30}$ cm$^{-3}$." if es else
               "Nucleons and their antiparticles at 50 MeV, PDG2025. "
               "Density is given in units of $10^{30}$ cm$^{-3}$.")
    out = [r"\begin{table}[t]\centering\small", "\\caption{"+caption+"}",
           r"\label{tab:nucleons50}", r"\begin{tabular}{lrr}\toprule",
           (r"Especie de partícula & Masa (MeV) & Densidad\\\midrule" if es else
            r"Particle species & Mass (MeV) & Density\\\midrule")]
    for pdg, label in [(2212,"$p$"),(-2212,"$\\bar p$"),(2112,"$n$"),(-2112,"$\\bar n$")]:
        r = next(r for r in species if float(r["T_MeV"]) == 50. and int(r["pdg_id"]) == pdg)
        out.append(f"{label} & {float(r['mass_GeV'])*1000:.3f} & {float(r['n_cm3'])/1e30:.6f}"+r"\\")
    out += [r"\bottomrule\end{tabular}",r"\end{table}"]
    (ROOT/f"table_nucleons50_{lang}.tex").write_text("\n".join(out)+"\n")

    caption = ("Sensibilidad al inventario con la misma entrada cosmológica. "
               "Los decimales adicionales documentan el cálculo, no su exactitud física." if es else
               "Inventory sensitivity at the same cosmological input. "
               "Extra decimal places document the calculation, not its physical accuracy.")
    out = [r"\begin{table}[t]\centering\small","\\caption{"+caption+"}",
           r"\label{tab:crosscatalogs}",r"\begin{tabular}{lrr}\toprule",
           (r"Lista & $T_\times$ (MeV) & $R(50\ {\rm MeV})$\\\midrule" if es else
            r"List & $T_\times$ (MeV) & $R(50\ {\rm MeV})$\\\midrule")]
    for r in crosses:
        r50 = next(s for s in states if s["catalog"] == r["catalog"] and float(s["T_MeV"]) == 50.)
        out.append(f"{r['catalog']} & {r['T_cross_MeV']:.6f} & {float(r50['R_antibaryon_to_net']):.6f}" + r"\\")
    out += [r"\bottomrule\end{tabular}",r"\end{table}"]
    (ROOT/f"table_crosscatalogs_{lang}.tex").write_text("\n".join(out)+"\n")

    plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False,
                         "pdf.fonttype":42,"font.family":"DejaVu Sans"})
    fig, ax = plt.subplots(1,2,figsize=(7.05,2.75),gridspec_kw={"width_ratios":[1.3,1]},layout="constrained")
    t = np.array([float(r["T_MeV"]) for r in curve])
    R = np.array([float(r["R_antibaryon_to_net"]) for r in curve])
    ax[0].semilogy(t,R,color="#173B56",lw=1.5)
    for r in selected:
        ax[0].plot(float(r["T_MeV"]),float(r["R_antibaryon_to_net"]),"o",color="#173B56",ms=3)
    ax[0].axhline(1,color="#a55222",lw=1,ls="--")
    ax[0].axvline(38.2,color="#777777",lw=.7,ls=":")
    ax[0].annotate("50 MeV: R = 306.115",xy=(50,306.1147),xytext=(41,125),
                   arrowprops={"arrowstyle":"-","color":"#777777","lw":.6},fontsize=7)
    ax[0].set(xlim=(37,50.4),ylim=(.25,450),xlabel=("Temperatura (MeV)" if es else "Temperature (MeV)"),
              ylabel=r"$R=n_{\bar B}/(n_B-n_{\bar B})$",
              title=("a. Estados de equilibrio" if es else "a. Equilibrium states"))
    xs=[r["eta"]*1e10 for r in sens]
    ys=[r["T_cross_MeV"] for r in sens]
    ax[1].plot(xs,ys,"o-",color="#173B56",ms=4,lw=1)
    ax[1].axhline(38.2,color="#a55222",ls="--",lw=1,
                  label=("Referencia publicada: 38.2 MeV" if es else "Published reference: 38.2 MeV"))
    ax[1].set(xlabel=r"$\eta\times10^{10}$",ylabel=r"$T_\times$ (MeV)",
              title=("b. Sensibilidad sólo a $\\eta$" if es else "b. Sensitivity to $\\eta$ alone"))
    ax[1].ticklabel_format(axis="y",useOffset=False)
    ax[1].set_xticks(xs)
    ax[1].legend(fontsize=6.6,loc="upper left",frameon=False)
    for a in ax: a.grid(axis="y",alpha=.15,lw=.5)
    fig.savefig(FIG/f"final_cross_{lang}.pdf")
    fig.savefig(FIG/f"final_cross_{lang}.png",dpi=450)
    plt.close(fig)

net = cosmo["n_baryon0_cm3"]*1e6
R50 = summary["point_50MeV_PDG2025"]["R_antibaryon_to_net"]
derived = {"normalization_present_volume_m3":1.,"N_net":net,
           "N_B_50":net*(R50+1),"N_antiB_50":net*R50,"N_sum_50":net*(2*R50+1),
           "N_B_cross":2*net,"N_antiB_cross":net,
           "chemical_condition":"muQ=muS=0; charge and strangeness neutrality are not imposed",
           "source":"Stored verified finite-muB species and state outputs; no new thermal inference"}
for key, temp in [("50",50.),("cross",summary["crossover_PDG2025"]["T_MeV"])]:
    rows = [r for r in species if float(r["T_MeV"]) == temp]
    derived[f"net_charge_to_net_B_{key}"]=sum(float(r["Q"])*float(r["Y_i"]) for r in rows)/summary["point_50MeV_PDG2025"]["Y_net"]
    derived[f"net_strangeness_to_net_B_{key}"]=sum(float(r["S"])*float(r["Y_i"]) for r in rows)/summary["point_50MeV_PDG2025"]["Y_net"]
(ROOT/"data/final_derived_quantities.json").write_text(json.dumps(derived,indent=2)+"\n")
print("Generated final ES/EN tables, figures and derived-quantity provenance.")
