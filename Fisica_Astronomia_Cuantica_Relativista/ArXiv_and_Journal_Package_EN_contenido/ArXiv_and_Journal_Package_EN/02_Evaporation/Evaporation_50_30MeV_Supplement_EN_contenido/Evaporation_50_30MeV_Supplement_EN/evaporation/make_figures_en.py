"""Render English figures from the archived numerical outputs; no model rerun."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parent
OUT = P / 'figures_en'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10, 'axes.spines.top':False,
                     'axes.spines.right':False, 'pdf.fonttype':42})
COLORS = ['#263c52','#37969b','#d88c30','#ae375b']

def finish(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=240)
    plt.close(fig)

fig, axs = plt.subplots(2, 2, figsize=(8, 5.3), layout='constrained')
for f, col in zip([0,.01,.1,1], COLORS):
    d = np.loadtxt(P/f'trayectoria_f{f:g}.csv', delimiter=',', skiprows=1)
    label = f'$f={f:g}$'
    axs[0,0].plot(d[:,0]*1e3, d[:,1], color=col, label=label)
    axs[0,1].plot(d[:,0]*1e3, d[:,8], color=col, label=label)
    axs[1,0].semilogy(d[:,1], d[:,-1], color=col, label=label)
    axs[1,1].plot(d[:,0]*1e3, d[:,7]/d[0,7], color=col, label=label)
axs[0,0].set(xlabel='Time since 50 MeV (ms)', ylabel='$T$ (MeV)', title='(a) Thermal evolution')
axs[0,1].set(xlabel='Time since 50 MeV (ms)', ylabel='$S_{\\mathrm{pl}}/S_{\\mathrm{pl},i}$', title='(b) Plasma entropy')
axs[1,0].set(xlabel='$T$ (MeV)', ylabel='$R=n_{\\bar B}/\\Delta$', title='(c) Abundance crossing')
axs[1,0].invert_xaxis()
axs[1,0].axhline(1, color='gray', ls=':', lw=1)
axs[1,1].set(xlabel='Time since 50 MeV (ms)', ylabel='$Y_\\Delta/Y_{\\Delta,i}$', title='(d) Yield dilution')
for ax in axs.ravel():
    ax.grid(alpha=.15)
    ax.legend(fontsize=8)
finish(fig, 'initial_excess')

target = json.loads((P/'exceso_final_comun/resultados.json').read_text())['target_final_yield']
fig, axs = plt.subplots(1, 2, figsize=(8.2, 3.25), layout='constrained')
for f, col in zip([0,.01,.1,1], COLORS):
    d = np.loadtxt(P/f'exceso_final_comun/trayectoria_f{f:g}.csv', delimiter=',', skiprows=1)
    label = f'$f={f:g}$'
    axs[0].plot(d[:,0]*1e3, d[:,7]/target, color=col, label=label)
    axs[1].semilogy(d[:,1], d[:,-1], color=col, label=label)
axs[0].set(xlabel='Time since 50 MeV (ms)', ylabel='$Y_\\Delta/Y_{\\mathrm{target}}$', title='(a) Common final yield')
axs[1].set(xlabel='$T$ (MeV)', ylabel='$R=n_{\\bar B}/\\Delta$', xlim=(40,37), ylim=(.3,4), title='(b) Recomputed crossings')
for ax in axs:
    ax.axhline(1, color='gray', ls=':', lw=1)
    ax.grid(alpha=.15)
    ax.legend(fontsize=8)
finish(fig, 'final_yield')

res = P/'robustez_hrg/resultados'
events = json.loads((res/'verificacion_multicruce.json').read_text())['events']
d = np.loadtxt(res/'M85000000_f1_final.csv', delimiter=',', skiprows=1)
t = d[:,0]*1e3
tau = (8.5e7)**3/(3*5.34e25*15.35)*1e3
fig, axs = plt.subplots(1, 2, figsize=(8.2, 3.2), layout='constrained')
axs[0].plot(t, d[:,1], color=COLORS[0])
axs[1].semilogy(t, d[:,-1], color=COLORS[3])
for i, e in enumerate(events, 1):
    tt = e['time_s']*1e3
    axs[0].scatter(tt, e['T_MeV'], color=COLORS[3], zorder=3)
    axs[1].scatter(tt, 1, color=COLORS[0], zorder=3)
    axs[1].annotate(str(i), (tt,1), xytext=(0,10), textcoords='offset points', ha='center')
axs[0].set(xlabel='Time since 50 MeV (ms)', ylabel='$T$ (MeV)', xlim=(.15,.34), ylim=(37,41), title='(a) Cooling and reheating')
axs[1].set(xlabel='Time since 50 MeV (ms)', ylabel='$R=n_{\\bar B}/\\Delta$', xlim=(.15,.34), ylim=(.4,float(d[(t>=.15)&(t<=.34),-1].max()*1.2)), title='(b) Three crossings of $R=1$')
axs[1].axhline(1, color='gray', ls=':', lw=1)
for ax in axs:
    ax.axvline(tau, color=COLORS[1], ls='--', lw=1, label='End of evaporation')
    ax.legend(fontsize=8)
    ax.grid(alpha=.15)
finish(fig, 'multiple_crossings')
print('Three English figures generated from unchanged CSV and JSON outputs.')
