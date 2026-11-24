"""Publication figures from validated CSVs; no image synthesis."""
from pathlib import Path
from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"figures"; OUT.mkdir(exist_ok=True)
df=pd.read_csv(ROOT/"data"/"comparison_hrg.csv").sort_values("T_MeV")
den=pd.read_csv(ROOT/"data"/"entropy_densities.csv")
colors={"legacy":"#C4512B","14":"#8495A4","20":"#258A7E","25":"#154F84","meson":"#A8BFCE","light":"#ECE7DA"}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.3,"axes.labelsize":9,
 "axes.linewidth":.7,"xtick.labelsize":8,"ytick.labelsize":8,"legend.fontsize":7.7,
 "pdf.fonttype":42,"ps.fonttype":42,"savefig.dpi":450,"text.color":"#172D40",
 "axes.labelcolor":"#172D40","xtick.color":"#172D40","ytick.color":"#172D40"})
def clean(ax):
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(length=3,width=.65)
    ax.grid(axis="y",color="#DCE3E8",linewidth=.5,zorder=0)
def save(fig,name,lang):
    for fmt in ['pdf','png']:
        stream=BytesIO()
        fig.savefig(stream,format=fmt,bbox_inches="tight",pad_inches=.055)
        data=stream.getvalue()
        if fmt=='pdf':assert data.rstrip().endswith(b'%%EOF')
        target=OUT/f'{name}_{lang}.{fmt}'
        temp=OUT/f'{name}_{lang}.{fmt}.tmp'
        temp.write_bytes(data)
        temp.replace(target)
    plt.close(fig)
def sci(v):
    return f"{v:.4g}".replace("e-0","e-").replace("e+0","e+")
for lang in ["es","en"]:
    es=lang=="es"
    reference="Reducido previo" if es else "Prior reduced"
    computed="PDG2025 (cálculo)" if es else "PDG2025 (calculated)"
    T=df["T_MeV"].to_numpy()
    fig=plt.figure(figsize=(7.15,3.36))
    gs=fig.add_gridspec(1,2,width_ratios=[1.88,1.05],wspace=.21,left=.095,right=.994,top=.91,bottom=.17)
    ax=fig.add_subplot(gs[0,0]);clean(ax)
    ax.plot(T,df.PDG2014_fraction,color=colors["14"],marker="v",lw=1.15,ms=3.7,ls=":",label="PDG2014",zorder=2)
    ax.plot(T,df.PDG2020_fraction,color=colors["20"],marker="s",lw=1.1,ms=3.3,ls="--",label="PDG2020",zorder=3)
    ax.plot(T,df.PDG2025_fraction,color=colors["25"],marker="o",lw=1.5,ms=3.1,label=computed,zorder=4)
    ax.plot(T,df.legacy_reduced_fraction,color=colors["legacy"],marker="D",lw=1.35,ms=3.3,ls="--",label=reference,zorder=5)
    ax.set_yscale("log");ax.set_ylim(7e-9,.24);ax.set_xlim(155,35);ax.set_xticks([150,120,100,80,60,40])
    ax.set_xlabel("Temperatura, T (MeV)" if es else "Temperature, T (MeV)")
    ax.set_ylabel(r"$f^{(s)}_{B\bar B}=s_{B+\bar B}/s_{\rm tot}$")
    ax.yaxis.set_major_locator(LogLocator(base=10,numticks=9));ax.yaxis.set_minor_formatter(NullFormatter())
    ax.legend(loc="lower left",frameon=False,handlelength=2.5,borderaxespad=.2,labelspacing=.55)
    ax.text(0,1.03,"a  Curvas de equilibrio" if es else "a  Equilibrium curves",transform=ax.transAxes,fontweight="bold",fontsize=9)
    ax.text(.52,-.18,"Enfriamiento →" if es else "Cooling →",transform=ax.transAxes,fontsize=7.8,ha="center")
    at=fig.add_subplot(gs[0,1]);at.set_axis_off()
    at.text(0,1.03,"b  Valores adimensionales" if es else "b  Dimensionless values",fontweight="bold",fontsize=9)
    rows=[[str(int(r.T_MeV)),sci(r.legacy_reduced_fraction),sci(r.PDG2025_fraction)] for r in df.iloc[::-1].itertuples()]
    tbl=at.table(cellText=rows,colLabels=["T","Previo" if es else "Prior","PDG2025"],colWidths=[.21,.38,.43],cellLoc="right",bbox=[0,.10,1,.88])
    tbl.auto_set_font_size(False);tbl.set_fontsize(7.7)
    for (row,col),cell in tbl.get_celld().items():
        cell.set_linewidth(0);cell.set_height(.1);cell.PAD=.08
        if row==0: cell.set_facecolor("#E9EEF2");cell.set_text_props(fontweight="bold",color="#172D40")
        else:
            if row%2==0:cell.set_facecolor("#F4F6F8")
            if col==1:cell.get_text().set_color(colors["legacy"])
            if col==2:cell.get_text().set_color(colors["25"])
    at.text(0,.025,"PDG: valores derivados en este trabajo." if es else "PDG: values derived in this study.",fontsize=7.0)
    save(fig,"fig01_comparison",lang)

    fig,ax=plt.subplots(figsize=(7.15,2.85))
    fig.subplots_adjust(left=.105,right=.983,top=.90,bottom=.23)
    clean(ax)
    ax.plot(T,df.reconstruction_pct,color=colors["25"],marker="o",ms=4,lw=1.5,label=r"$100\,f_{\rm previo}/f_{\rm PDG2025}$" if es else r"$100\,f_{\rm prior}/f_{\rm PDG2025}$")
    ax.plot(T,df.relative_deficit_pct,color=colors["legacy"],marker="D",ms=3.8,lw=1.4,ls="--",label=r"$100(1-f_{\rm previo}/f_{\rm PDG2025})$" if es else r"$100(1-f_{\rm prior}/f_{\rm PDG2025})$")
    for x,a,b in zip(T,df.reconstruction_pct,df.relative_deficit_pct):
        ax.annotate(f"{a:.2f}",(x,a),textcoords="offset points",xytext=(0,8),ha="center",fontsize=7.4,color=colors["25"])
        ax.annotate(f"{b:.2f}",(x,b),textcoords="offset points",xytext=(0,-11 if b>4 else 8),ha="center",fontsize=7.4,color=colors["legacy"])
    ax.set_xlim(158,32);ax.set_ylim(-5,110);ax.set_xticks(T);ax.set_yticks([0,25,50,75,100])
    ax.set_xlabel("Temperatura, T (MeV)" if es else "Temperature, T (MeV)")
    ax.set_ylabel("Comparación relativa (%)" if es else "Relative comparison (%)")
    ax.legend(loc="center",bbox_to_anchor=(.54,.50),ncol=1,frameon=False,fontsize=8.6)
    ax.text(.01,1.03,"Convergencia de las fracciones" if es else "Convergence of the fractions",transform=ax.transAxes,fontweight="bold",fontsize=9)
    save(fig,"fig02_convergence",lang)

    fig,(a,b)=plt.subplots(1,2,figsize=(7.15,2.95),gridspec_kw={"width_ratios":[1.02,1]})
    fig.subplots_adjust(left=.08,right=.97,top=.90,bottom=.23,wspace=.36)
    r=den[den.catalog=="PDG2025"].sort_values("T_MeV")
    temp=r.T_MeV.to_numpy()
    B=100*r.s_B_GeV3/r.s_total_GeV3
    M=100*r.s_meson_GeV3/r.s_total_GeV3
    L=100*r.s_light_GeV3/r.s_total_GeV3
    a.stackplot(temp,B,M,L,colors=[colors["25"],colors["meson"],colors["light"]],
                labels=[r"$B+\bar B$","Mesones" if es else "Mesons",r"$\gamma,e^\pm,\mu^\pm,\nu,\bar\nu$"],alpha=.98)
    clean(a);a.set_ylim(0,100);a.set_xlim(150,40);a.set_xticks([150,120,80,40])
    a.set_xlabel("Temperatura, T (MeV)" if es else "Temperature, T (MeV)")
    a.set_ylabel("Participación en la entropía (%)" if es else "Share of entropy (%)")
    a.legend(loc="center",bbox_to_anchor=(.55,.68),frameon=False,labelspacing=.45,fontsize=7.9)
    a.text(0,1.03,"a  Composición del denominador" if es else "a  Denominator composition",transform=a.transAxes,fontweight="bold",fontsize=8.5)
    vals=[8.45453323656,32.7957412877,58.7497254758]
    a.text(146,4.1,"8.45",color="white",fontsize=7.3,va="center")
    b.bar([0,1],[100*r.iloc[-1].f,100*r.iloc[-1].f_had],width=.56,color=[colors["25"],colors["20"]],zorder=3)
    clean(b);b.set_ylim(0,24);b.set_xticks([0,1],["Plasma total" if es else "Total plasma","Sólo hadrones" if es else "Hadrons only"])
    b.set_ylabel(r"$100\,s_{B+\bar B}/s_{\rm denominador}$" if es else r"$100\,s_{B+\bar B}/s_{\rm denominator}$")
    b.set_title("T = 150 MeV",loc="left",fontsize=8.5,pad=8)
    b.text(0,8.45453323656+.7,"8.45%",ha="center",fontweight="bold",color=colors["25"])
    b.text(1,20.4957013572+.7,"20.50%",ha="center",fontweight="bold",color=colors["20"])
    b.text(0,1.15,"b  Efecto de la normalización" if es else "b  Normalization effect",transform=b.transAxes,fontweight="bold",fontsize=8.5)
    save(fig,"fig03_denominator",lang)
pop=pd.read_csv(ROOT/'data'/'particle_densities.csv')
pop=pop[pop.catalog=='PDG2025'].sort_values('T_MeV')
nuc=pd.read_csv(ROOT/'data'/'nucleon_densities_PDG2025.csv')
nuc=nuc.groupby('T_MeV').n_particle_cm3.sum().reindex(pop.T_MeV).to_numpy()
for lang in ['es','en']:
    es=lang=='es'
    fig,(a,b)=plt.subplots(1,2,figsize=(7.15,3.05))
    fig.subplots_adjust(left=.09,right=.988,top=.86,bottom=.21,wspace=.40)
    for ax in [a,b]:
        clean(ax);ax.set_yscale('log');ax.set_xlim(155,35);ax.set_xticks([150,120,80,40])
        ax.set_xlabel('Temperatura, T (MeV)' if es else 'Temperature, T (MeV)')
    a.plot(pop.T_MeV,pop.Y_sum_equilibrium,'o-',color=colors['25'],lw=1.5,ms=3.5,label=r'$Y_\Sigma^{\rm eq}=(n_B+n_{\bar B})/s_{\rm tot}$')
    a.axhline(pop.Y_net_external.iloc[0],color=colors['legacy'],ls='--',lw=1.3,
              label=r'$Y_{\Delta B}^{\rm ref}=\eta/7.04$')
    a.set_ylim(2.5e-11,.05)
    a.set_ylabel('Número por unidad de entropía' if es else 'Number per entropy unit')
    a.text(0,1.08,'a  Población térmica y exceso neto' if es else 'a  Thermal population and net excess',transform=a.transAxes,fontweight='bold',fontsize=8.3)
    a.legend(frameon=False,loc='lower left',bbox_to_anchor=(.01,.26),fontsize=7.3)
    a.annotate(r'$7.465\times10^{-3}$',(150,pop.Y_sum_equilibrium.iloc[-1]),xytext=(8,8),textcoords='offset points',fontsize=7.4,color=colors['25'])
    a.annotate(r'$6.876\times10^{-10}$',(40,pop.Y_sum_equilibrium.iloc[0]),xytext=(-8,10),ha='right',textcoords='offset points',fontsize=7.4,color=colors['25'])
    a.text(.10,.08,'Exceso: entrada externa' if es else 'Net excess: external input',transform=a.transAxes,color=colors['legacy'],fontsize=7.4)
    b.plot(pop.T_MeV,pop.n_B_cm3,'o-',color=colors['25'],lw=1.5,ms=3.5,label=r'$n_B^{\rm eq}=n_{\bar B}^{\rm eq}$')
    b.plot(pop.T_MeV,nuc,'s--',color=colors['20'],lw=1.2,ms=3.1,label=r'$n_p^{\rm eq}+n_n^{\rm eq}$')
    b.set_ylim(3e27,6e37)
    b.set_ylabel(r'Densidad de número (${\rm cm^{-3}}$)' if es else r'Number density (${\rm cm^{-3}}$)')
    b.text(0,1.08,'b  Densidad por lado y nucleones' if es else 'b  Density per side and nucleons',transform=b.transAxes,fontweight='bold',fontsize=8.3)
    b.legend(frameon=False,loc='lower left',fontsize=7.5)
    b.annotate(r'$1.722\times10^{37}$',(150,pop.n_B_cm3.iloc[-1]),xytext=(8,8),textcoords='offset points',fontsize=7.4,color=colors['25'])
    b.annotate(r'$1.690\times10^{28}$',(40,pop.n_B_cm3.iloc[0]),xytext=(-8,9),textcoords='offset points',ha='right',fontsize=7.4,color=colors['25'])
    save(fig,'fig04_populations',lang)
inv=pd.read_csv(ROOT/'data'/'retrospective_inference.csv')
inv=inv[inv.catalog=='PDG2025'].sort_values('T_MeV')
limit=pd.read_csv(ROOT/'data'/'nucleon_literature_comparison.csv').sort_values('T_MeV')
for lang in ['es','en']:
    es=lang=='es'
    fig,(a,b)=plt.subplots(1,2,figsize=(7.15,3.06))
    fig.subplots_adjust(left=.095,right=.985,top=.85,bottom=.21,wspace=.37)
    for ax in [a,b]:
        clean(ax);ax.set_xlim(155,35);ax.set_xticks([150,120,100,80,60,40])
        ax.set_xlabel('Temperatura, T (MeV)' if es else 'Temperature, T (MeV)')
    a.set_yscale('log')
    a.plot(inv.T_MeV,inv.n_B_GeV3/inv.s_total_GeV3,'o-',color=colors['25'],lw=1.5,ms=3.4,label=r'$Y_B$')
    a.plot(inv.T_MeV,inv.n_antiB_GeV3/inv.s_total_GeV3,'s--',color=colors['legacy'],lw=1.2,ms=3.6,mfc='white',label=r'$Y_{\bar B}$')
    a.axhline(inv.Y_net.iloc[0],color='#6B7B87',ls=':',lw=1.35,label=r'$Y_{\Delta B}^{\rm ref}$')
    a.set_ylim(2.5e-11,.015)
    a.set_ylabel('Número por unidad de entropía' if es else 'Number per entropy unit')
    a.text(0,1.10,'a  Inferencia con exceso finito' if es else 'a  Inference with finite excess',transform=a.transAxes,fontweight='bold',fontsize=8.4)
    a.legend(frameon=False,loc='lower left',bbox_to_anchor=(.02,.29),fontsize=8)
    a.text(.10,.18,r'$n_{\bar B}/n_B=0.7771$'+'\n'+('a 40 MeV' if es else 'at 40 MeV'),transform=a.transAxes,fontsize=8.1,color=colors['legacy'])
    b.plot(limit.T_MeV,limit.nucleon_share_pct,'o-',color=colors['20'],lw=1.5,ms=3.5,label='Protones + neutrones' if es else 'Protons + neutrons')
    b.plot(limit.T_MeV,limit.heavy_baryon_share_pct,'D--',color=colors['25'],lw=1.3,ms=3.4,label='Otros bariones' if es else 'Other baryons')
    b.set_ylim(-4,109);b.set_yticks([0,25,50,75,100])
    b.set_ylabel('Participación en el número bariónico (%)' if es else 'Share of baryon number (%)')
    b.text(0,1.10,'b  Control del límite nucleónico' if es else 'b  Nucleon-limit check',transform=b.transAxes,fontweight='bold',fontsize=8.4)
    b.legend(frameon=False,loc='center',bbox_to_anchor=(.47,.86),fontsize=7.2)
    b.annotate('74.42%',(150,limit.heavy_baryon_share_pct.iloc[-1]),xytext=(8,-14),textcoords='offset points',fontsize=7.5,color=colors['25'])
    b.annotate('1.525%',(40,limit.heavy_baryon_share_pct.iloc[0]),xytext=(-8,8),ha='right',textcoords='offset points',fontsize=7.5,color=colors['25'])
    save(fig,'fig05_inverse',lang)
print('Created five figures in Spanish and English, each in vector PDF and 450-dpi PNG.')

