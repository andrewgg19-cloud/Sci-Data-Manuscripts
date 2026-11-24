from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axs=plt.subplots(2,2,figsize=(8,5.3),layout='constrained')
for f,col in zip([0,.01,.1,1],['#263c52','#37969b','#d88c30','#ae375b']):
 d=np.loadtxt(P/f'trayectoria_f{f:g}.csv',delimiter=',',skiprows=1)
 lab=f'$f={f:g}$'
 axs[0,0].plot(d[:,0]*1e3,d[:,1],color=col,label=lab)
 axs[0,1].plot(d[:,0]*1e3,d[:,8],color=col,label=lab)
 axs[1,0].semilogy(d[:,1],d[:,-1],color=col,label=lab)
 axs[1,1].plot(d[:,0]*1e3,d[:,7]/d[0,7],color=col,label=lab)
axs[0,0].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='$T$ (MeV)',title='(a) Evolución térmica')
axs[0,1].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='$S_{pl}/S_{pl,i}$',title='(b) Entropía del plasma')
axs[1,0].set(xlabel='$T$ (MeV)',ylabel='$R=n_{\\bar B}/\\Delta$',title='(c) Cruce de abundancias')
axs[1,0].invert_xaxis();axs[1,0].axhline(1,color='gray',ls=':',lw=1)
axs[1,1].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='$Y_\\Delta/Y_{\\Delta,i}$',title='(d) Dilución del exceso')
for ax in axs.ravel():ax.grid(alpha=.15);ax.legend(fontsize=8)
fig.savefig(P/'figura_resultados.pdf');fig.savefig(P/'figura_resultados.png',dpi=200)
