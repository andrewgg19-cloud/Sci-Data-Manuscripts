"""Compare evaporation scenarios at the same final baryon/entropy yield.
The thermal bath has no baryon feedback, so its entropy factor does not depend
on delta_initial. The final yield is a boundary condition, not a prediction.
Run after simular.py. All paths are relative to this script's directory.
"""
from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import simular as model
P=Path(__file__).resolve().parent
DEST=P/'exceso_final_comun'
DEST.mkdir(exist_ok=True)
TARGET=6.12e-10/7.04  # external input retained from the prior thermal audit
HEADER='time_since_50MeV_s,T_MeV,a,nB_cm-3,nanti_cm-3,delta_cm-3,s_over_kB_cm-3,Ynet,S_over_Sinitial,S_integrated_over_Sinitial,R_antibaryon_over_net'

def main():
 baseline=json.loads((P/'resultados.json').read_text())
 rows=[];results=[];trajectories=[]
 for prev in baseline['runs']:
  f=prev['rhoBH_over_rhoplasma_initial']
  entropy_factor=prev['Sfinal_over_Sinitial']
  initial_delta=TARGET*model.s0*entropy_factor
  summary,data=model.run(f,delta_initial=initial_delta)
  final_error=summary['Ynet_final']/TARGET-1
  checks=dict(final_yield_target_relative_error=float(final_error),
   net_comoving_identity_max_relative=float(np.max(abs(data[:,5]*data[:,2]**3/initial_delta-1))),
   yield_entropy_identity_max_relative=float(np.max(abs(data[:,7]*data[:,8]/summary['Ynet_initial']-1))),
   initial_equilibrium_product_relative_error=float(data[0,3]*data[0,4]/model.bzero(50)**2-1),
   positive_densities=bool(np.all(data[:,3:6]>0)),
   temperature_final_MeV=float(data[-1,1]),
   entropy_factor_relative_change=float(summary['Sfinal_over_Sinitial']/entropy_factor-1))
  assert abs(final_error)<1e-6
  assert checks['positive_densities']
  assert checks['net_comoving_identity_max_relative']<1e-12
  assert checks['yield_entropy_identity_max_relative']<1e-12
  assert abs(checks['temperature_final_MeV']-30)<1e-7
  assert len(summary['crossings_MeV'])==1
  np.savetxt(DEST/f'trayectoria_f{f:g}.csv',data,delimiter=',',header=HEADER,comments='')
  item=dict(summary=summary,delta_initial_cm3=initial_delta,target_final_yield=TARGET,checks=checks)
  results.append(item);trajectories.append(data)
  rows.append(dict(f=f,S_final_over_initial=summary['Sfinal_over_Sinitial'],Y_initial=summary['Ynet_initial'],delta_initial_cm3=initial_delta,Y_final=summary['Ynet_final'],T_cross_MeV=summary['crossings_MeV'][0],T_cross_fixed_initial_MeV=prev['crossings_MeV'][0],target_relative_error=final_error))
  print(json.dumps(item),flush=True)
 # Verify numerical stability at the strongest evaporation, holding its initial
 # density fixed. Do not re-fit the target when decreasing solver tolerance.
 tight,_=model.run(1,rtol=2e-8,delta_initial=results[-1]['delta_initial_cm3'])
 convergence=dict(summary=tight,
  relative_change_Y_final=abs(tight['Ynet_final']/results[-1]['summary']['Ynet_final']-1),
  relative_change_entropy=abs(tight['Sfinal_over_Sinitial']/results[-1]['summary']['Sfinal_over_Sinitial']-1),
  crossing_change_MeV=abs(tight['crossings_MeV'][0]-rows[-1]['T_cross_MeV']))
 assert convergence['relative_change_Y_final']<1e-6
 output=dict(target_final_yield=TARGET,target_definition='eta/7.04; eta=6.12e-10, retained external input from the prior thermal audit',normalization='delta_initial = target * s_initial * baseline_entropy_factor; no independent final-abundance prediction',runs=results,convergence_f1=convergence)
 (DEST/'resultados.json').write_text(json.dumps(output,indent=2))
 with (DEST/'comparacion.csv').open('w',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
 fig,axs=plt.subplots(1,2,figsize=(8.2,3.25),layout='constrained')
 for item,data,col in zip(results,trajectories,['#263c52','#37969b','#d88c30','#ae375b']):
  f=item['summary']['rhoBH_over_rhoplasma_initial'];label=f'$f={f:g}$'
  axs[0].plot(data[:,0]*1e3,data[:,7]/TARGET,color=col,label=label)
  axs[1].semilogy(data[:,1],data[:,-1],color=col,label=label)
 axs[0].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='$Y_\\Delta/Y_{\\mathrm{obj}}$',title='(a) Mismo exceso final impuesto')
 axs[0].axhline(1,color='gray',ls=':',lw=1)
 axs[1].set(xlabel='$T$ (MeV)',ylabel='$R=n_{\\bar B}/\\Delta$',xlim=(40,37),ylim=(.3,4),title='(b) Cruces recalculados')
 axs[1].axhline(1,color='gray',ls=':',lw=1)
 for ax in axs:ax.grid(alpha=.15);ax.legend(fontsize=8)
 fig.savefig(DEST/'comparacion.pdf');fig.savefig(DEST/'comparacion.png',dpi=180)
 print(json.dumps(convergence),flush=True)

if __name__=='__main__':main()
