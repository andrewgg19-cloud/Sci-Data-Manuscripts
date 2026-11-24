"""Exploratory homogeneous kinetic benchmark, not a quantum bounce simulation.
Run: python simular.py. Requires numpy scipy matplotlib.
"""
from pathlib import Path
import json,csv
import numpy as np
from scipy.special import kv
from scipy.interpolate import CubicSpline,PchipInterpolator
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
hc=1.973269804e-11 # MeV cm
c=2.99792458e10; G=6.67430e-8; mev_erg=1.602176634e-6
M0=1e8; alpha=5.34e25*15.35; life=M0**3/(3*alpha)
nscale=1e30; delta0=8.8765e27; D=delta0/nscale
# Reduced ideal bath: photons, massless e+-, 3 neutrino flavours; massive muons and pions.
Ts=np.geomspace(10,100,1800)
rhos=[]; ps=[]
for T in Ts:
 rho=np.pi**2/30*10.75*T**4; p=rho/3
 for m,g,fermion in [(105.6583755,4,True),(134.9768,1,False),(139.57039,2,False)]:
  k=np.arange(1,65,dtype=float); sign=(-1.)**(k+1) if fermion else np.ones_like(k)
  x=m/T
  p+=g*m*m*T*T/(2*np.pi**2)*np.sum(sign*kv(2,k*x)/k**2)
  rho+=g*m*m*T*T/(2*np.pi**2)*np.sum(sign*(3*kv(2,k*x)/k**2+x*kv(1,k*x)/k))
 rhos.append(rho/hc**3);ps.append(p/hc**3)
rhoS=CubicSpline(Ts,rhos); pS=CubicSpline(Ts,ps)
def entropy(T):return (rhoS(T)+pS(T))/T
# Product nB_eq*nanti_eq reconstructed from rounded audit table; Boltzmann |B|=1 closure.
ta=np.array([37,38.203739,40,45,50.])
nb=np.array([4.4167e27,7.3454e27,1.9166e28,2.8323e29,2.7261e30])
na=np.array([1.1116e27,3.6727e27,1.4894e28,2.7694e29,2.7172e30])
lnb=PchipInterpolator(ta,np.log(np.sqrt(nb*na)))
def nuc(T):return T*kv(2,938.92/T)
def bzero(T):
 if T<37:return np.exp(lnb(37))*nuc(T)/nuc(37)
 if T>50:return np.exp(lnb(50))*nuc(T)/nuc(50)
 return np.exp(lnb(T))
def sv(T):return (3.5+8.6*np.sqrt(T/939))*1e-26*c
r0=float(rhoS(50));s0=float(entropy(50))
def hub(T,N,f,m):return np.sqrt(8*np.pi*G/3*(rhoS(T)+f*r0*m*np.exp(-3*N))*mev_erg/c**2)
def run(f,rtol=2e-7):
 # state N=ln(a), T, comoving n_antibaryon/nscale, independently integrated S/S0
 anti0=2*bzero(50)**2/(np.sqrt(delta0**2+4*bzero(50)**2)+delta0)/nscale
 y0=[0,50,anti0,1]
 def kin(T,N,y,dt):
  return sv(T)*dt*(np.exp(3*N)*bzero(T)**2/nscale-nscale*np.exp(-3*N)*y*(y+D))
 def rhs(u,y):
  N,T,z,S=y;m=1-u;dt=3*life*m*m; H=hub(T,N,f,m)
  inj=f*r0*np.exp(-3*N)
  return [H*dt,(-3*H*(rhoS(T)+pS(T))*dt+inj)/rhoS(T,1),kin(T,N,z,dt),f*r0/(T*s0)]
 sol=solve_ivp(rhs,[0,1],y0,method='BDF',rtol=rtol,atol=[1e-10,1e-8,1e-14,1e-10],max_step=.008,dense_output=True)
 if not sol.success:raise RuntimeError(sol.message)
 u=np.linspace(0,1,601);ys=sol.sol(u);times=life*(1-(1-u)**3)
 def rhs2(N,y):
  T,z,S,t=y;H=hub(T,N,0,0)
  return [-3*(rhoS(T)+pS(T))/rhoS(T,1),kin(T,N,z,1/H),0,1/H]
 def stop(N,y):return y[0]-30
 stop.terminal=True;stop.direction=-1
 N0,T0,z0,S0=sol.y[:,-1]
 post=solve_ivp(rhs2,[N0,N0+2],[T0,z0,S0,life],method='BDF',rtol=rtol,atol=[1e-8,1e-14,1e-10,1e-12],events=stop,max_step=.008,dense_output=True)
 if not post.success or not len(post.t_events[0]):raise RuntimeError('post failure')
 ns=np.linspace(N0,post.t[-1],601)[1:]; yp=post.sol(ns)
 Ns=np.r_[ys[0],ns];Temps=np.r_[ys[1],yp[0]];zs=np.r_[ys[2],yp[1]];Sint=np.r_[ys[3],yp[2]];times=np.r_[times,yp[3]]
 a3=np.exp(3*Ns); ds=delta0/a3; anti=zs*nscale/a3; ss=entropy(Temps); Sent=ss*a3/s0;Rs=anti/ds
 eqanti=np.array([2*bzero(T)**2/(np.sqrt(d*d+4*bzero(T)**2)+d) for T,d in zip(Temps,ds)])
 cross=[]
 for i in range(len(Rs)-1):
  if (Rs[i]-1)*(Rs[i+1]-1)<0:
   w=(1-Rs[i])/(Rs[i+1]-Rs[i]);cross.append(float(Temps[i]+w*(Temps[i+1]-Temps[i])))
 data=np.c_[times,Temps,np.exp(Ns),anti+ds,anti,ds,ss,ds/ss,Sent,Sint,Rs]
 summary={'rhoBH_over_rhoplasma_initial':f,'M_initial_g':M0,'lifetime_s':life,'T_after_evap_MeV':float(ys[1,-1]),'Sfinal_over_Sinitial':float(Sent[-1]),'Ynet_final':float(ds[-1]/ss[-1]),'Ynet_initial':delta0/s0,'crossings_MeV':cross,'max_entropy_balance_relative_error':float(np.max(abs(Sent-Sint)/Sint)),'max_relative_chemical_departure':float(np.max(abs(anti-eqanti)/eqanti)),'minimum_antibaryon_density':float(min(anti)),'min_H_per_s':float(min(hub(T,N,f,max(0,1-t/life)**(1/3)) for T,N,t in zip(Temps,Ns,times))),'max_T_MeV':float(max(Temps))}
 return summary,data
if __name__=='__main__':
 results=[];all_data=[]
 for f in [0,.01,.1,1]:
  r,d=run(f); results.append(r);all_data.append(d)
  np.savetxt(OUT/f'trayectoria_f{f:g}.csv',d,delimiter=',',header='time_since_50MeV_s,T_MeV,a,nB_cm-3,nanti_cm-3,delta_cm-3,s_over_kB_cm-3,Ynet,S_over_Sinitial,S_integrated_over_Sinitial,R_antibaryon_over_net',comments='')
  print(json.dumps(r),flush=True)
 check,dc=run(1,rtol=2e-8)
 checks={'tight_tolerance_case_f1':check,'relative_change_entropy_f1':abs(check['Sfinal_over_Sinitial']/results[-1]['Sfinal_over_Sinitial']-1),'relative_change_final_Y_f1':abs(check['Ynet_final']/results[-1]['Ynet_final']-1),'crossing_change_MeV':abs(check['crossings_MeV'][-1]-results[-1]['crossings_MeV'][-1]),'bath_s50':s0,'audit_s50':1.0210875816993465e38,'bath_relative_difference_audit':s0/1.0210875816993465e38-1}
 (OUT/'resultados.json').write_text(json.dumps({'runs':results,'checks':checks},indent=2))
 fig,axes=plt.subplots(1,3,figsize=(13,4.2))
 for r,d in zip(results,all_data):
  lab=f"f = {r['rhoBH_over_rhoplasma_initial']:g}"
  axes[0].plot(d[:,0]*1e3,d[:,1],label=lab)
  axes[1].plot(d[:,0]*1e3,d[:,8],label=lab)
  axes[2].semilogy(d[:,1],d[:,-1],label=lab)
 axes[0].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='Temperatura (MeV)')
 axes[1].set(xlabel='Tiempo desde 50 MeV (ms)',ylabel='Entropía comóvil / inicial')
 axes[2].set(xlabel='Temperatura (MeV)',ylabel='Antibariones / exceso neto',ylim=(1e-4,1e3));axes[2].invert_xaxis();axes[2].axhline(1,color='gray',ls=':')
 for ax in axes:ax.grid(alpha=.2);ax.legend()
 fig.suptitle('Prueba exploratoria: evaporación simétrica y plasma homogéneo; sin dinámica de rebote')
 fig.tight_layout();fig.savefig(OUT/'comparacion.png',dpi=170)
 print(json.dumps(checks),flush=True)
