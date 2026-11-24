"""Generate manuscript tables from the validated calculation CSV."""
from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/"data"/"comparison_hrg.csv").open()))
captions={
"es":"Comparación a temperatura fija de la fracción de entropía barión-antibarión. Las cuatro columnas de $f$ son fracciones adimensionales; las dos últimas se expresan en porcentaje. La referencia reducida fue transcrita del manuscrito previo; las columnas PDG se calcularon en esta auditoría con el mismo plasma ligero. El cociente descriptivo se evaluó antes del redondeo del resultado PDG.",
"en":"Comparison at fixed temperature of the baryon-antibaryon entropy fraction. The four $f$ columns are dimensionless fractions; the last two are percentages. The reduced reference was transcribed from the prior manuscript; the PDG columns were calculated in this audit with the same light plasma. The descriptive ratio was evaluated before rounding the PDG result."}
def sf(v):
    v=float(v)
    if .001<=v<1e4:return f"{v:.4g}"
    m,e=f"{v:.3e}".split("e")
    return "$"+m+r"\times10^{"+str(int(e))+"}$"
for lang in ["es","en"]:
    prefix=r"\begin{table*}[t]\centering\footnotesize"+"\n"
    prefix+=r"\caption{"+captions[lang]+r"}\label{tab:comparison}"+"\n"
    prefix+=r"\setlength{\tabcolsep}{9pt}\renewcommand{\arraystretch}{1.14}"+"\n"
    prefix+=r"\begin{tabular}{rrrrrrr}\toprule"+"\n"
    prior="previo" if lang=="es" else "prior"
    prefix+=r"$T$ (MeV) & $f_{\mathrm{"+prior+r"}}$ & $f_{\mathrm{PDG2014}}$ & $f_{\mathrm{PDG2020}}$ & $f_{\mathrm{PDG2025}}$ & $100R$ & $100d$ \\ \midrule"+"\n"
    for row in rows:
        vals=[str(int(float(row["T_MeV"])))]+[sf(row[k]) for k in ["legacy_reduced_fraction","PDG2014_fraction","PDG2020_fraction","PDG2025_fraction"]]+[f"{float(row[k]):.2f}" for k in ["reconstruction_pct","relative_deficit_pct"]]
        prefix+=" & ".join(vals)+r" \\"+"\n"
    prefix+=r"\bottomrule\end{tabular}\end{table*}"+"\n"
    (ROOT/f"table_comparison_{lang}.tex").write_text(prefix,encoding="utf-8")
print("Generated both comparison tables.")

population=list(csv.DictReader((ROOT/"data"/"particle_densities.csv").open()))
population=[r for r in population if r['catalog']=='PDG2025']
for lang in ['es','en']:
    caption=("Densidades numéricas de equilibrio reconstruidas con PDG2025, a potenciales químicos nulos. La densidad de cada lado se muestra en la segunda columna; el total incluye ambos. $Y_\\Sigma=n_\\Sigma/s_{\\rm tot}$ separa la supresión térmica de la dilución. $\\mathcal Q=Y_\\Sigma/Y_{\\Delta B}^{\\rm ref}$ usa el exceso cosmológico como entrada externa. Son poblaciones instantáneas calculadas, sin contabilizar reacciones de regeneración o aniquilación."
        if lang=='es' else
        "Equilibrium number densities reconstructed with PDG2025 at zero chemical potentials. The second column gives the density of each side; the total includes both. $Y_\\Sigma=n_\\Sigma/s_{\\rm tot}$ separates thermal suppression from dilution. $\\mathcal Q=Y_\\Sigma/Y_{\\Delta B}^{\\rm ref}$ uses the cosmic excess as an external input. These are calculated instantaneous populations, without counting regeneration or annihilation events.")
    out=r'\begin{table*}[t]\centering\small'+ '\n'+r'\caption{'+caption+r'}\label{tab:populations}'+ '\n'
    out+=r'\setlength{\tabcolsep}{12pt}\renewcommand{\arraystretch}{1.14}'+ '\n'
    out+=r'\begin{tabular}{rrrrr}\toprule'+ '\n'
    out+=r'$T$ (MeV) & $n_B=n_{\bar B}$ (${\rm cm^{-3}}$) & $n_\Sigma$ (${\rm cm^{-3}}$) & $Y_\Sigma$ & $\mathcal Q$ \\ \midrule'+ '\n'
    for row in population:
        out+=' & '.join([str(int(float(row['T_MeV'])))]+[sf(row[k]) for k in ['n_B_cm3','n_sum_cm3','Y_sum_equilibrium','equilibrium_sum_to_external_net_ratio']])+r' \\'+ '\n'
    out+=r'\bottomrule\end{tabular}\end{table*}'+ '\n'
    (ROOT/f'table_populations_{lang}.tex').write_text(out)

inverse=[r for r in csv.DictReader((ROOT/'data'/'retrospective_inference.csv').open()) if r['catalog']=='PDG2025']
nucleon=list(csv.DictReader((ROOT/'data'/'nucleon_literature_comparison.csv').open()))
initial=[r for r in csv.DictReader((ROOT/'data'/'initial_temperature_sensitivity.csv').open()) if r['catalog']=='PDG2025']
for lang in ['es','en']:
    es=lang=='es'
    caption=(r'Reconstrucción inversa propia con PDG2025 y $Y_{\Delta B}=\eta/7.04$ como condición externa. Las densidades son medias por volumen físico; coinciden al redondeo en temperaturas altas, pero conservan un exceso finito. $\alpha=\mu_B/T$ y $Y_\Sigma=n_\Sigma/s_{\rm tot}$. Se usaron entradas centrales, sin errores físicos asignados al HRG.' if es else
             r'Our inverse reconstruction using PDG2025 with $Y_{\Delta B}=\eta/7.04$ as an external constraint. Densities are means per physical volume; they coincide at displayed rounding at high temperature but retain finite excess. $\alpha=\mu_B/T$ and $Y_\Sigma=n_\Sigma/s_{\rm tot}$. Central inputs were used without assigning HRG physical uncertainties.')
    out=r'\begin{table*}[t]\centering\small'+'\n'+r'\caption{'+caption+r'}\label{tab:inversepop}'+'\n'
    out+=r'\setlength{\tabcolsep}{7pt}\renewcommand{\arraystretch}{1.14}'+'\n'
    out+=r'\begin{tabular}{rrrrrr}\toprule'+'\n'
    out+=r'$T$ (MeV) & $\alpha$ & $n_B$ (${\rm cm^{-3}}$) & $n_{\bar B}$ (${\rm cm^{-3}}$) & $Y_\Sigma$ & $n_{\bar B}/n_B$ \\ \midrule'+'\n'
    for row in inverse:
        vals=[str(int(float(row['T_MeV'])))]+[sf(row[k]) for k in ['muB_over_T','n_B_cm3','n_antiB_cm3','Y_sum']]+[f"{float(row['antiB_to_B']):.6f}"]
        out+=' & '.join(vals)+r' \\'+'\n'
    out+=r'\bottomrule\end{tabular}\end{table*}'+'\n'
    (ROOT/f'table_inverse_{lang}.tex').write_text(out)

    caption=(r'Contraste calculado con el límite nucleónico de Satarov et al. (2013), generalizado a masas distintas de $p$ y $n$. Todas las columnas numéricas son resultados propios a $\mu_B=0$. $\delta_{\rm MB}$ expresa $100(n_N^{\rm MB}/n_N^{\rm FD}-1)$; la participación de otros bariones usa el total HRG con Fermi-Dirac.' if es else
             r'Calculated comparison with the nucleon limit of Satarov et al. (2013), generalized to distinct $p$ and $n$ masses. All numerical columns are our results at $\mu_B=0$. $\delta_{\rm MB}$ is $100(n_N^{\rm MB}/n_N^{\rm FD}-1)$; other-baryon share uses the full Fermi-Dirac HRG total.')
    out=r'\begin{table*}[t]\centering\small'+'\n'+r'\caption{'+caption+r'}\label{tab:nucleoncontrast}'+'\n'
    out+=r'\setlength{\tabcolsep}{8pt}\renewcommand{\arraystretch}{1.14}'+'\n'
    out+=r'\begin{tabular}{rrrrr}\toprule'+'\n'
    out+=r'$T$ (MeV) & $n_N^{\rm MB}$ (${\rm cm^{-3}}$) & $n_B^{\rm HRG}$ (${\rm cm^{-3}}$) & '
    out+=('Otros bariones (\\%)' if es else 'Other baryons (\\%)')+r' & $\delta_{\rm MB}$ (\%) \\ \midrule'+'\n'
    for row in nucleon:
        vals=[str(int(float(row['T_MeV'])))]+[sf(row[k]) for k in ['n_p_plus_n_MB_cm3','n_B_full_zero_mu_cm3']]+[f"{float(row['heavy_baryon_share_pct']):.4f}",sf(row['MB_to_quantum_relative_difference_pct'])]
        out+=' & '.join(vals)+r' \\'+'\n'
    out+=r'\bottomrule\end{tabular}\end{table*}'+'\n'
    (ROOT/f'table_nucleon_{lang}.tex').write_text(out)

    caption=(r'Sensibilidad propia a la temperatura de partida, con PDG2025 y la misma condición neta. La referencia de transición es $156.5\pm1.5$ MeV (HotQCD, 2019); 150 MeV se conserva como inicio de la malla principal. El intervalo cercano a la transición no representa una incertidumbre completa del HRG ni un inicio de aniquilación medido.' if es else
             r'Our starting-temperature sensitivity using PDG2025 and the same net constraint. The transition reference is $156.5\pm1.5$ MeV (HotQCD, 2019); 150 MeV remains the main-grid start. The near-transition interval is neither a complete HRG uncertainty nor a measured annihilation onset.')
    out=r'\begin{table*}[t]\centering\small'+'\n'+r'\caption{'+caption+r'}\label{tab:initialT}'+'\n'
    out+=r'\setlength{\tabcolsep}{11pt}\renewcommand{\arraystretch}{1.14}'+'\n'
    out+=r'\begin{tabular}{rrrrr}\toprule'+'\n'
    out+=r'$T$ (MeV) & $n_B$ (${\rm cm^{-3}}$) & $n_{\bar B}$ (${\rm cm^{-3}}$) & $\Delta n_B$ (${\rm cm^{-3}}$) & $Y_\Sigma$ \\ \midrule'+'\n'
    for row in initial:
        vals=[f"{float(row['T_MeV']):g}"]+[sf(row[k]) for k in ['n_B_cm3','n_antiB_cm3','n_net_cm3','Y_sum']]
        out+=' & '.join(vals)+r' \\'+'\n'
    out+=r'\bottomrule\end{tabular}\end{table*}'+'\n'
    (ROOT/f'table_initial_{lang}.tex').write_text(out)
print('Generated inverse, nucleon-comparison, and initial-temperature tables in both languages.')

