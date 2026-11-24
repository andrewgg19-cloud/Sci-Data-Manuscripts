from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent/'resultados'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
r=json.loads((P/'verificacion_multicruce.json').read_text())
d=np.loadtxt(P/'M85000000_f1_final.csv',delimiter=',',skiprows=1)
fig,ax=plt.subplots(1,2,figsize=(8.2,3.2),layout='constrained')
t=d[:,0]*1e3;tau=(8.5e7)**3/(3*5.34e25*15.35)*1e3
ax[0].plot(t,d[:,1],color='#263c52');ax[1].semilogy(t,d[:,-1],color='#ae375b')
for j,e in enumerate(r['events'],1):
 tt=e['time_s']*1e3
 ax[0].scatter(tt,e['T_MeV'],color='#ae375b',zorder=3)
 ax[1].scatter(tt,1,color='#263c52',zorder=3)
 ax[1].annotate(str(j),(tt,1),xytext=(0,10),textcoords='offset points',ha='center')
ax[0].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='$T$ (MeV)',xlim=(.15,.34),ylim=(37,41),title='(a) Enfriamiento y recalentamiento')
ax[1].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='$R=n_{\\bar B}/\\Delta$',xlim=(.15,.34),ylim=(.4,float(d[(t>=.15)&(t<=.34),-1].max()*1.2)),title='(b) Tres cruces de $R=1$')
ax[1].axhline(1,color='gray',ls=':',lw=1)
for a in ax:
 a.axvline(tau,color='#37969b',ls='--',lw=1,label='Fin de evaporación');a.legend(fontsize=8);a.grid(alpha=.15)
fig.savefig(P/'multicruce.pdf');fig.savefig(P/'multicruce.png',dpi=180)
