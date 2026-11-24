"""Conditional retrospective inference from the measured net baryon yield.

Equilibrium spectra constrain the symmetric population; present cosmic inputs
constrain its difference. Exact ideal-gas quantum sums solve a scalar mu_B
constraint with mu_Q=mu_S=0. No kinetic trajectory is inferred or integrated.
"""
import json, math
import numpy as np
from scipy.special import kv, expit
from scipy.optimize import brentq
from scipy.integrate import quad
from reproduce_hrg import ROOT, TEMPERATURES, parse_list, evaluate, write_csv
from reconstruct_populations import GEV3_TO_CM3, Y_NET, ETA, S_PER_PHOTON

def kernels(rows,T,kmax=96):
    baryons=[r for r in rows if r['g']>0 and r['B']==1]
    k=np.arange(1,kmax+1,dtype=float)
    x=np.array([r['m']/T for r in baryons])[:,None]
    g=np.array([r['g'] for r in baryons])[:,None]
    assert all(r['stat']==1 for r in baryons)
    pref=g*x*x*T**3/(2*math.pi**2)
    signs=(-1.)**(k+1)
    n=pref*signs*kv(2,x*k)/k
    s=pref*signs*(4*kv(2,x*k)/(k*k)+x*kv(1,x*k)/k)
    fixed=evaluate(rows,T)['s_total_GeV3']-evaluate(rows,T)['s_B_GeV3']
    return baryons,k,n,s,fixed

def state(data,alpha):
    rows,k,n,s,fixed=data
    ch=np.cosh(k*alpha);sh=np.sinh(k*alpha)
    nsum=2*float(np.sum(n*ch))
    net=2*float(np.sum(n*sh))
    sB=2*float(np.sum(s*ch-alpha*n*sh))
    total=fixed+sB
    return dict(n_sum_GeV3=nsum,n_net_GeV3=net,n_B_GeV3=(nsum+net)/2,
                n_antiB_GeV3=(nsum-net)/2,s_total_GeV3=total,
                Y_net=net/total,Y_sum=nsum/total,muB_over_T=alpha)

def infer(rows,T,y_net=Y_NET,kmax=96):
    data=kernels(rows,T,kmax)
    alpha=brentq(lambda a:state(data,a)['Y_net']-y_net,0.,1.,xtol=1e-18,rtol=1e-13)
    return state(data,alpha),data

def nucleon_MB(rows,T):
    # Generalize the common-mass nucleon limit in Satarov et al. Eq. (19)
    # to the catalog's distinct proton and neutron masses, g_p=g_n=2.
    return sum(r['g']*r['m']**2*T/(2*math.pi**2)*kv(2,r['m']/T)
               for r in rows if r['pdg'] in [2212,2112])

def net_integral(mass,g,T,alpha):
    x=mass/T
    def f(q):
        E=math.hypot(q,x)
        if E>700:return 0.
        return q*q*math.sinh(alpha)/(math.cosh(E)+math.cosh(alpha))
    val,_=quad(f,0,np.inf,epsabs=1e-15,epsrel=5e-12,limit=200)
    return g*T**3/(2*math.pi**2)*val

def main():
    populations=[]; comparisons=[]; controls={}; pairs_examples=[]
    for key in ['PDG2014','PDG2020','PDG2025']:
        rows=parse_list(ROOT/'catalogs'/f'{key}_list.dat')
        max_closure=0.;max_k=0.;max_zero=0.
        for tm in TEMPERATURES:
            T=tm/1000
            inferred,data=infer(rows,T)
            check,_=infer(rows,T,kmax=192)
            zero=state(data,0.)
            baseline=evaluate(rows,T)
            max_closure=max(max_closure,abs(inferred['Y_net']/Y_NET-1))
            max_k=max(max_k,abs(inferred['muB_over_T']/check['muB_over_T']-1),abs(inferred['Y_sum']/check['Y_sum']-1))
            max_zero=max(max_zero,abs(zero['s_total_GeV3']/baseline['s_total_GeV3']-1))
            ratio=inferred['n_antiB_GeV3']/inferred['n_B_GeV3']
            populations.append(dict(T_MeV=tm,catalog=key,
                **{k:v for k,v in inferred.items()},
                n_B_cm3=inferred['n_B_GeV3']*GEV3_TO_CM3,
                n_antiB_cm3=inferred['n_antiB_GeV3']*GEV3_TO_CM3,
                n_net_cm3=inferred['n_net_GeV3']*GEV3_TO_CM3,
                n_sum_cm3=inferred['n_sum_GeV3']*GEV3_TO_CM3,
                antiB_to_B=ratio,net_yield_closure_relative=inferred['Y_net']/Y_NET-1,
                Y_net_input=Y_NET,
                symmetric_to_inferred_sum_change_pct=100*(inferred['n_sum_GeV3']/zero['n_sum_GeV3']-1),
                symmetric_to_inferred_total_entropy_change_pct=100*(inferred['s_total_GeV3']/zero['s_total_GeV3']-1)))
            if key=='PDG2025':
                nq=sum(float(np.sum(data[2][j])) for j,r in enumerate(data[0]) if r['pdg'] in [2212,2112])
                mb=float(nucleon_MB(rows,T))
                comparisons.append(dict(T_MeV=tm,n_B_full_zero_mu_cm3=zero['n_B_GeV3']*GEV3_TO_CM3,
                    n_p_plus_n_quantum_cm3=nq*GEV3_TO_CM3,n_p_plus_n_MB_cm3=mb*GEV3_TO_CM3,
                    nucleon_share_pct=100*nq/zero['n_B_GeV3'],heavy_baryon_share_pct=100*(1-nq/zero['n_B_GeV3']),
                    MB_to_quantum_relative_difference_pct=100*(mb/nq-1),
                    comparison='Our evaluation of the ideal-nucleon limit underlying Satarov et al. (2013), Eq. (19); not published tabulated measurements.'))
        controls[key]=dict(maximum_net_yield_constraint_relative_error=max_closure,
            maximum_relative_reconstruction_change_k96_to192=max_k,
            maximum_zero_mu_total_entropy_difference=max_zero)
    test=[]
    rows=parse_list(ROOT/'catalogs'/'PDG2025_list.dat')
    for tm in [150.,40.]:
        d,data=infer(rows,tm/1000)
        for j,r in enumerate(data[0]):
            if r['pdg'] not in [2212,2112]:continue
            series=2*float(np.sum(data[2][j]*np.sinh(data[1]*d['muB_over_T'])))
            integral=net_integral(r['m'],r['g'],tm/1000,d['muB_over_T'])
            test.append(dict(T_MeV=tm,pdg=r['pdg'],relative_net_density_difference=abs(series/integral-1)))
    # A rank-one observation of a two-component initial population has a null direction.
    ys=next(x for x in populations if x['catalog']=='PDG2025' and x['T_MeV']==150.)['Y_sum']
    for factor in [.1,1.,10.,100.]:
        total=ys*factor
        yanti=(total-Y_NET)/2
        yB=yanti+Y_NET
        pairs_examples.append(dict(pair_sum_factor=factor,Y_sum_candidate=total,Y_B_candidate=yB,
            Y_antiB_candidate=yanti,Y_net_constraint=Y_NET,eta_after_pairs_removed=S_PER_PHOTON*Y_NET,
            interpretation='Algebraic degeneracy under net-baryon conservation only; not a demonstrated kinetic history.'))
    observation_map=np.array([[1.,-1.]])
    assert np.linalg.norm(observation_map @ np.array([1.,1.]))==0.
    identifiability=dict(observation_map=observation_map.tolist(),rank=int(np.linalg.matrix_rank(observation_map)),unknown_initial_components=observation_map.shape[1],
        null_direction=[1.,1.],examples=pairs_examples,
        conclusion='Present net yield alone cannot uniquely recover the initial symmetric pair population; the equilibrium condition at specified T is additional information.')
    controls['independent_finite_mu_net_integrals']=test
    controls['maximum_finite_mu_net_integral_relative_difference']=max(x['relative_net_density_difference'] for x in test)
    assert controls['maximum_finite_mu_net_integral_relative_difference']<1e-8
    for key in ['PDG2014','PDG2020','PDG2025']:
        assert controls[key]['maximum_net_yield_constraint_relative_error']<1e-10
        assert controls[key]['maximum_relative_reconstruction_change_k96_to192']<1e-10
    assert all(x['n_B_GeV3']>x['n_antiB_GeV3']>0. for x in populations)
    write_csv(ROOT/'data'/'retrospective_inference.csv',populations)
    write_csv(ROOT/'data'/'nucleon_literature_comparison.csv',comparisons)
    (ROOT/'data'/'inverse_identifiability.json').write_text(json.dumps(identifiability,indent=2)+'\n')
    (ROOT/'data'/'inverse_validation.json').write_text(json.dumps(controls,indent=2)+'\n')
    (ROOT/'inverse_provenance.json').write_text(json.dumps(dict(
        objective='Test conditional retrospective reconstruction from particle properties and current cosmological inputs.',
        signatures_used='Catalog rest masses, spin degeneracy, quantum statistics and charges; no original spectral measurements were analyzed.',
        cosmological_inputs='Measured eta and present CMB temperature; primordial composition used only for a mean-density reference.',
        inference_constraint='n_net(T,mu_B)/s_total(T,mu_B)=eta/7.04',
        assumptions='Specified T, ideal equilibrium, zero widths, mu_Q=mu_S=0, common light sector, entropy and net baryon conservation.',
        solver='scipy.optimize.brentq; quantum sums with stable sinh/cosh pair representation; 96/192 term and independent momentum-integral checks.',
        literature_comparison='Generalized ideal-nucleon limit of Satarov et al. (2013), Eq. (19), evaluated here using distinct p/n catalog masses and the same normalization; not a reproduction of their interacting kinetic calculation.',
        identifiability='Rank-one difference map with common-pair null direction; four algebraic candidates, without kinetic feasibility claims.',
        kinetic_annihilation_onset='Not identified by the inverse equilibrium constraint.'),indent=2)+'\n')
    selected=[x for x in populations if x['catalog']=='PDG2025' and x['T_MeV'] in [150.,100.,40.]]
    print(json.dumps(dict(inferred=selected,nucleon_comparison=comparisons,validation=controls,identifiability=identifiability),indent=2))

if __name__=='__main__':main()
