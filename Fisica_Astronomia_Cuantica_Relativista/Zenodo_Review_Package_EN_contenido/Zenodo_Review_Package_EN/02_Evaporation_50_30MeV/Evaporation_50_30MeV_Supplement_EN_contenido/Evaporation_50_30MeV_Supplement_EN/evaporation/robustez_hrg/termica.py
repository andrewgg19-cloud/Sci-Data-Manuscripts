"""Ideal zero-width HRG, frozen catalogs; MeV, cm^-3, MeV cm^-3.
Neutrality solver is an EQUILIBRIUM control with Le=Lmu=Ltau=0.
The kinetic background uses zero chemical potentials, independently of pairs.
"""
from pathlib import Path
import sys
import numpy as np
from scipy.special import kve
from scipy.optimize import root,brentq
from scipy.interpolate import CubicSpline
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'original_hrg'))
from reproduce_hrg import parse_list
HC=1.973269804e-11
TARGET=6.12e-10/7.04

class HRG:
 def __init__(self,catalog='PDG2025'):
  self.rows=[r for r in parse_list(P/'original_hrg/catalogs'/f'{catalog}_list.dat') if r['g']>0]
  self.mass=np.array([r['m']*1000 for r in self.rows]+[105.6583755])
  self.g=np.array([r['g'] for r in self.rows]+[2.])
  self.stat=np.array([r['stat'] for r in self.rows]+[1])
  self.multi=np.array([r['multiplicity'] for r in self.rows]+[2])
  self.charges=np.array([[r['B'],r['Q'],r['S'],0,0] for r in self.rows]+[[0,-1,0,0,1]],float)
  self.pair=self.multi==2
  self.bmask=self.charges[:,0]==1
  self.catalog=catalog
 def kernels(self,T,kmax=64):
  k=np.arange(1,kmax+1,dtype=float)[None,:]
  x=self.mass[:,None]/T
  signs=np.where(self.stat[:,None]==1,(-1.)**(k+1),1.)
  pref=self.g[:,None]*x*x/(2*np.pi**2)*signs
  # Exponentially scaled Bessel kernels; combine chemical and mass exponent
  # before exponentiating to avoid 0*inf at low T and high series order.
  b2=kve(2,k*x);b1=kve(1,k*x)
  n=pref*b2/k
  p=pref*b2/k**2
  rho=pref*(3*b2/k**2+x*b1/k)
  return k,n,p,rho
 def state(self,T,alphas=None,kmax=64,kernels=None):
  a=np.zeros(5) if alphas is None else np.asarray(alphas)
  k,n,p,rho=self.kernels(T,kmax) if kernels is None else kernels
  mu=self.charges@a
  argument=mu[:,None]*k
  mass_exponent=-self.mass[:,None]/T*k
  plus=np.exp(mass_exponent+argument);minus=np.exp(mass_exponent-argument)
  fac=np.where(self.pair[:,None],plus+minus,np.exp(mass_exponent))
  difference=np.sign(argument)*np.exp(mass_exponent+abs(argument))*(-np.expm1(-2*abs(argument)))
  net=np.where(self.pair,np.sum(n*difference,axis=1),0.)
  rh=float(np.sum(rho*fac));pr=float(np.sum(p*fac))
  density=net@self.charges
  entropy=rh+pr-float(mu@net)
  # electron particle: Q=-1, Le=+1; neutrino Le=+1, etc.; tau flavor zero.
  for g,charges in [(2,np.array([0,-1,0,1,0.])),(1,np.array([0,0,0,1,0.])),(1,np.array([0,0,0,0,1.])),(1,np.zeros(5))]:
   v=float(charges@a)
   dn=g/6*(v+v**3/np.pi**2)
   pp=g*(7*np.pi**2/360+v*v/12+v**4/(24*np.pi**2))
   rh+=3*pp;pr+=pp;entropy+=4*pp-v*dn;density+=charges*dn
  # photons
  pp=2*np.pi**2/90;rh+=3*pp;pr+=pp;entropy+=4*pp
  bp=float(np.sum(n[self.bmask]*plus[self.bmask]))
  bm=float(np.sum(n[self.bmask]*minus[self.bmask]))
  conv=T**3/HC**3
  return dict(T_MeV=T,nB=bp*conv,nanti=bm*conv,delta=density[0]*conv,
   s=entropy*conv,rho=rh*T*conv,p=pr*T*conv,
   charges=density*conv,alpha=a,Y=density[0]/entropy,
   R=(bm/density[0] if density[0]!=0 else None))
 def equilibrium(self,T,Y=TARGET,neutral=False,kmax=64):
  kernels=self.kernels(T,kmax)
  zero=self.state(T,kernels=kernels)
  guess=np.arcsinh(Y*zero['s']/(2*zero['nB']))
  if not neutral:
   beta=brentq(lambda b:self.state(T,[b,0,0,0,0],kernels=kernels)['Y']-Y,0,max(2,guess+2),xtol=1e-13)
   return self.state(T,[beta,0,0,0,0],kernels=kernels)
  scale=np.array([1.,1e-9,1e-5,1e-9,1e-9])
  def residual(x):
   st=self.state(T,x*scale,kernels=kernels)
   v=st['charges'].copy();v[0]-=Y*st['s']
   return v/(Y*st['s'])
  sol=root(residual,np.array([guess,0,0,0,0]),tol=1e-10)
  err=float(np.max(abs(residual(sol.x))))
  if not np.isfinite(err) or err>1e-7:raise RuntimeError((T,sol.message,err,sol.x))
  st=self.state(T,sol.x*scale,kernels=kernels);st['neutrality_residual_over_delta']=err
  return st
 def background(self,n_grid=801):
  grid=np.linspace(20,80,n_grid);rho=[];p=[];b=[]
  for T in grid:
   st=self.state(float(T));rho.append(st['rho']);p.append(st['p']);b.append(st['nB'])
  # Smooth log b avoids the five-point abundance interpolation and endpoint tails.
  return grid,CubicSpline(grid,rho),CubicSpline(grid,p),CubicSpline(grid,np.log(b))
