"""Read-only scientific audit using direct momentum quadrature and algebra.

Usage: python auditoria_independiente.py --hrg-root PATH --output FILE.json
PATH is the extracted calculos_50MeV_cruce directory. No project functions
are imported. Catalog data and the published alpha values are shared inputs;
the number and entropy integrals are evaluated independently of Bessel sums.
"""
from pathlib import Path
import argparse, json, math, hashlib, platform
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import expit

def run(hrg_root):
    h=Path(hrg_root)
    ref=json.loads((h/'data/resumen.json').read_text())
    raw=(h/'catalogs/PDG2025_list.dat').read_text()
    rows=[]
    for line in raw.splitlines():
        p=line.split('#')[0].split()
        if p and float(p[4])>0:
            rows.append(dict(m=float(p[3]),g=float(p[4]),stat=int(p[5]),
                             B=int(p[6]),Q=int(p[7]),S=int(p[8]),C=int(p[9])))
    def integrate(m,g,stat,T,a):
        x=m/T
        def f(E):
            return expit(a-E) if stat==1 else math.exp(a-E)/(-math.expm1(a-E))
        def fn(q):
            E=math.hypot(q,x)
            return q*q*f(E)
        def fs(q):
            E=math.hypot(q,x)
            return q*q*(E+q*q/(3*E)-a)*f(E)
        pref=g*T**3/(2*math.pi**2)
        return tuple(pref*quad(fun,0,np.inf,epsabs=1e-50,epsrel=3e-11,limit=250)[0] for fun in [fn,fs])
    out=[]
    for key in ['point_50MeV_PDG2025','crossover_PDG2025']:
        st=ref[key];T=st['T_MeV']/1000;alpha=st['muB_over_T']
        nB=na=net=charge=strange=sh=0.
        active=0
        for r in rows:
            a=r['B']*alpha
            n,s=integrate(r['m'],r['g'],r['stat'],T,a)
            active+=1;sh+=s
            if r['B']==1:nB+=n
            if any(r[k] for k in ['B','Q','S','C']):
                nn,ss=integrate(r['m'],r['g'],r['stat'],T,-a)
                active+=1;sh+=ss
                if r['B']==1:
                    na+=nn
                    x=r['m']/T
                    def net_integrand(q):
                        E=math.hypot(q,x)
                        d=2*math.exp(-E)*math.sinh(a)/((1+math.exp(a-E))*(1+math.exp(-a-E)))
                        return q*q*d
                    dn=r['g']*T**3/(2*math.pi**2)*quad(net_integrand,0,np.inf,epsabs=1e-50,epsrel=3e-11,limit=250)[0]
                    net+=dn;charge+=r['Q']*dn;strange+=r['S']*dn
        s=sh+(2*math.pi**2/45*10.75)*T**3+integrate(.1056583755,4,1,T,0)[1]
        vals={'n_B_GeV3':nB,'n_antiB_GeV3':na,'n_net_GeV3':net,'s_total_GeV3':s}
        err={k:abs(v/st[k]-1) for k,v in vals.items()}
        out.append({'point':key,'T_MeV':st['T_MeV'],'shared_alpha':alpha,'active_species':active,
                    'relative_errors_vs_bessel':err,'Y_net_quadrature':net/s,
                    'R_quadrature':na/net,'charge_over_net':charge/net,'strangeness_over_net':strange/net})
    eta=6.12e-10;omega_m=.315;omega_b=.049309;ng=1.465e89;nb=8.966e79
    dh=2.527e-5;dhsigma=.030e-5;etasigma=.04e-10
    sq=math.sqrt(eta);sqsigma=etasigma/(2*sq)
    algebra={'C_b':nb/(eta*ng),'omega_m_over_omega_b':omega_m/omega_b,
             'C_m':omega_m/omega_b*nb/(eta*ng),
             'identity':'C_m/C_b = Omega_m/Omega_b; this ratio is an input, not an independent prediction.',
             'N_pair_1_k1':nb/eta,'N_pair_2_k1':omega_m/omega_b*nb/eta,
             'sqrt_eta':sq,'Xi_D':dh/sq,
             'relative_difference_denominator_DH_pct':100*(dh-sq)/dh,
             'relative_difference_denominator_sqrt_eta_pct':100*(dh-sq)/sq,
             'sigma_sqrt_eta_input_only':sqsigma,
             'D_difference_sigma_independent_inputs':(dh-sq)/math.hypot(dhsigma,sqsigma),
             'caution':'The last standardized difference assumes independent Gaussian inputs and no model error; not evidence of a physical relation.'}
    return {'scope':'Independent momentum-integral cross-check at two states; same catalog and chemical potentials. Algebraic audit of supplied residual manuscript.',
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'catalog_sha256':hashlib.sha256((h/'catalogs/PDG2025_list.dat').read_bytes()).hexdigest(),
            'quadrature':out,'residual_algebra':algebra}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--hrg-root',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();result=run(a.hrg_root)
    Path(a.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
