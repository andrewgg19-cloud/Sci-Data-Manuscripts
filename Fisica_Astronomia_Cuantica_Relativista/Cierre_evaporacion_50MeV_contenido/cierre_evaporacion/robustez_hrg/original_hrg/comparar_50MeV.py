"""Compute HRG populations at 50 MeV and the published abundance crossover.

Defines R(T)=n_antibaryon/(n_baryon-n_antibaryon). Finds R=1 in 37-40 MeV.
This is equilibrium inference with external net yield, not kinetic evolution.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reproduce_hrg import (
    parse_list, evaluate, entropy_over_T3, write_csv, MUON_MASS,
)
from reconstruct_populations import (
    number_over_T3, GEV3_TO_CM3, KB_GEV_K, ETA, ETA_SIGMA, S_PER_PHOTON, Y_NET,
)
from infer_early_populations import kernels, state

ROOT=Path(__file__).resolve().parent
CATALOGS=['PDG2014','PDG2020','PDG2025']
POINTS_MEV=[50.,45.,40.,38.2,37.]
REFERENCE_MEV=38.2


def relative(a,b):
    return abs(a/b-1)


def solve(rows,T_MeV,y_net=Y_NET,kmax=96):
    T=T_MeV/1000
    d=evaluate(rows,T,kmax=kmax)
    massless=2*math.pi**2/45*(2+4*7/8+6*7/8)
    light=(massless+entropy_over_T3(MUON_MASS,4,1,T,kmax))*T**3
    baryons,k,n,s,_=kernels(rows,T,kmax=kmax)
    data=(baryons,k,n,s,d['s_meson_GeV3']+light)
    # This safe bracket is deliberately restricted to the requested T range.
    assert 37 <= T_MeV <= 50
    alpha=brentq(lambda a:state(data,a)['Y_net']-y_net,
                  0.,1.,xtol=1e-18,rtol=1e-13)
    st=state(data,alpha)
    st['R_antibaryon_to_net']=st['n_antiB_GeV3']/st['n_net_GeV3']
    st['antiB_to_B']=st['n_antiB_GeV3']/st['n_B_GeV3']
    st['net_fraction_of_sum']=st['n_net_GeV3']/st['n_sum_GeV3']
    st['T_MeV']=T_MeV
    st['T_K']=T/KB_GEV_K
    for kfield in ['B','antiB','sum','net']:
        st[f'n_{kfield}_cm3']=st[f'n_{kfield}_GeV3']*GEV3_TO_CM3
    st['Y_B']=st['n_B_GeV3']/st['s_total_GeV3']
    st['Y_antiB']=st['n_antiB_GeV3']/st['s_total_GeV3']
    st['muB_MeV']=alpha*T_MeV
    st['s_light_GeV3']=float(light)
    st['s_meson_GeV3']=d['s_meson_GeV3']
    st['s_B_GeV3']=2*float(np.sum(s*np.cosh(data[1]*alpha)
                                -alpha*n*np.sinh(data[1]*alpha)))
    st['baryon_entropy_fraction']=st['s_B_GeV3']/st['s_total_GeV3']
    st['Y_net_input']=y_net
    return st,data


def crossover(rows,y_net=Y_NET,kmax=96):
    return brentq(lambda tm:solve(rows,tm,y_net,kmax)[0]['R_antibaryon_to_net']-1,
                  37.,40.,xtol=1e-10,rtol=1e-13)


def independent_integrals(mass,g,T,alpha):
    x=mass/T
    def number(beta):
        val,_=quad(lambda q:q*q*expit(beta-math.hypot(q,x)),0,np.inf,
                   epsabs=1e-25,epsrel=5e-12,limit=200)
        return g*T**3/(2*math.pi**2)*val
    def entropy(beta):
        def integrand(q):
            E=math.hypot(q,x)
            return q*q*(E+q*q/(3*E)-beta)*expit(beta-E)
        val,_=quad(integrand,0,np.inf,epsabs=1e-25,epsrel=5e-12,limit=200)
        return g*T**3/(2*math.pi**2)*val
    def net(q):
        E=math.hypot(q,x)
        if E>700:return 0.
        return q*q*math.sinh(alpha)/(math.cosh(E)+math.cosh(alpha))
    val,_=quad(net,0,np.inf,epsabs=1e-25,epsrel=5e-12,limit=200)
    return number(alpha),number(-alpha),g*T**3/(2*math.pi**2)*val,entropy(alpha)+entropy(-alpha)


def species(rows,st,data):
    out=[]
    baryons,k,n,_,_=data
    index={r['pdg']:i for i,r in enumerate(baryons)}
    T=st['T_MeV']/1000
    alpha=st['muB_over_T']
    for r in rows:
        if r['g']<=0:continue
        if r['B']==1:
            j=index[r['pdg']]
            nsum=2*float(np.sum(n[j]*np.cosh(k*alpha)))
            net=2*float(np.sum(n[j]*np.sinh(k*alpha)))
            values=[(nsum+net)/2,(nsum-net)/2]
        else:
            ni=number_over_T3(r['m'],r['g'],r['stat'],T)*T**3
            values=[ni]*r['multiplicity']
        for conjugate,ni in enumerate(values):
            sign=1 if conjugate==0 else -1
            out.append(dict(T_MeV=st['T_MeV'],pdg_id=sign*r['pdg'],
                name=r['name'] if sign==1 else 'anti('+r['name']+')',
                B=sign*r['B'],Q=sign*r['Q'],S=sign*r['S'],
                mass_GeV=r['m'],spin_degeneracy=r['g'],n_GeV3=ni,
                n_cm3=ni*GEV3_TO_CM3,Y_i=ni/st['s_total_GeV3']))
    for baryon_charge,field in [(1,'n_B_GeV3'),(-1,'n_antiB_GeV3')]:
        assert relative(sum(r['n_GeV3'] for r in out if r['B']==baryon_charge),st[field])<1e-12
    return out


def main():
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'figures').mkdir(exist_ok=True)
    prior=json.loads((ROOT/'provenance.json').read_text())
    results=[];crosses=[];inventories=[];controls=[]
    catalog_rows={}
    for key in CATALOGS:
        path=ROOT/'catalogs'/f'{key}_list.dat'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==prior['catalogs'][key]['sha256']
        rows=parse_list(path);catalog_rows[key]=rows
        tx=crossover(rows)
        tx192=crossover(rows,kmax=192)
        delta=tx-REFERENCE_MEV
        st_cross,data_cross=solve(rows,tx)
        assert abs(st_cross['R_antibaryon_to_net']-1)<1e-9
        assert abs(tx-tx192)<1e-8
        crosses.append(dict(catalog=key,T_cross_MeV=tx,T_cross_K=tx/1000/KB_GEV_K,
            published_reference_MeV=REFERENCE_MEV,difference_MeV=delta,
            numerical_difference_pct=100*delta/REFERENCE_MEV,
            R_at_cross=st_cross['R_antibaryon_to_net'],
            antiB_to_B_at_cross=st_cross['antiB_to_B'],
            net_yield_input=Y_NET,T_cross_k192_MeV=tx192,
            meaning='Equilibrium abundance crossover. Published reference has one decimal; percentage difference is not statistical agreement precision.'))
        for tm in POINTS_MEV+[tx]:
            st,data=solve(rows,tm)
            more,_=solve(rows,tm,kmax=192)
            largest=max(relative(st[f],more[f]) for f in
                ['n_B_GeV3','n_antiB_GeV3','n_net_GeV3','n_sum_GeV3',
                 's_total_GeV3','muB_over_T','R_antibaryon_to_net'])
            closure=relative(st['Y_net'],Y_NET)
            assert max(largest,closure)<1e-9
            controls.append(dict(catalog=key,T_MeV=tm,
                maximum_relative_k96_to192_difference=largest,
                net_yield_constraint_relative_error=closure))
            results.append(dict(catalog=key,point='crossover' if tm==tx else 'fixed_T',**st))
            if key!='PDG2025' or tm not in [50.,38.2,tx]:continue
            inv=species(rows,st,data)
            assert len(inv)==443
            inventories.extend(inv)
            for j,r in enumerate(data[0]):
                if r['pdg'] not in [2212,2112]:continue
                sumn=2*float(np.sum(data[2][j]*np.cosh(data[1]*st['muB_over_T'])))
                net=2*float(np.sum(data[2][j]*np.sinh(data[1]*st['muB_over_T'])))
                entropy=2*float(np.sum(data[3][j]*np.cosh(data[1]*st['muB_over_T'])
                    -st['muB_over_T']*data[2][j]*np.sinh(data[1]*st['muB_over_T'])))
                a,b,c,d=independent_integrals(r['m'],r['g'],tm/1000,st['muB_over_T'])
                errs=dict(particle_number=relative((sumn+net)/2,a),
                          antiparticle_number=relative((sumn-net)/2,b),
                          stable_net_number=relative(net,c),pair_entropy=relative(entropy,d))
                assert max(errs.values())<1e-8
                controls.append(dict(catalog=key,T_MeV=tm,pdg=r['pdg'],
                                      independent_integrals_relative_errors=errs))
    rows=catalog_rows['PDG2025']
    sensitivity=[]
    for label,eta in [('eta_minus_sigma',ETA-ETA_SIGMA),('central',ETA),('eta_plus_sigma',ETA+ETA_SIGMA)]:
        tx=crossover(rows,y_net=eta/S_PER_PHOTON)
        st,_=solve(rows,50,y_net=eta/S_PER_PHOTON)
        sensitivity.append(dict(input_case=label,eta=eta,Y_net=eta/S_PER_PHOTON,
            T_cross_MeV=tx,R_at_50MeV=st['R_antibaryon_to_net']))
    tx=next(r['T_cross_MeV'] for r in crosses if r['catalog']=='PDG2025')
    tlo=min(r['T_cross_MeV'] for r in sensitivity)
    thi=max(r['T_cross_MeV'] for r in sensitivity)
    curve=[]
    for tm in np.linspace(37,50,66):
        st,_=solve(rows,float(tm))
        curve.append(dict(T_MeV=float(tm),R_antibaryon_to_net=st['R_antibaryon_to_net'],
                          antiB_to_B=st['antiB_to_B'],muB_over_T=st['muB_over_T']))
    p50=next(r for r in results if r['catalog']=='PDG2025' and r['T_MeV']==50.)
    p38=next(r for r in results if r['catalog']=='PDG2025' and r['T_MeV']==38.2)
    pcross=next(r for r in results if r['catalog']=='PDG2025' and r['point']=='crossover')
    nus={}
    for tm in [50.,tx]:
        records=[r for r in inventories if r['T_MeV']==tm and r['B']!=0]
        nus[str(tm)]=sum(r['n_GeV3'] for r in records if abs(r['pdg_id']) in [2212,2112])/sum(r['n_GeV3'] for r in records)
    summary=dict(point_50MeV_PDG2025=p50,point_38p2MeV_PDG2025=p38,
        crossover_PDG2025=pcross,crossover_all_catalogs=crosses,
        eta_only_sensitivity=sensitivity,
        T_cross_eta_only_range_MeV=[tlo,thi],nucleon_share_of_B_plus_antiB=nus,
        distance_50_to_published_cross_MeV=50-REFERENCE_MEV,
        distance_50_to_computed_cross_MeV=50-tx,
        numerical_difference_to_38p2_MeV=tx-REFERENCE_MEV,
        crossing_interpretation='n_antiB=n_net; equivalently n_B=2*n_antiB. Antibaryons have not vanished at this crossover.',
        external_input='Y_net=eta/7.04 imposed from the same present cosmological reference; not independently predicted.',
        uncertainty='Range changes eta alone within its quoted input sigma. No total model uncertainty, reference temperature error or statistical significance inferred.',
        conclusion='The calculated crossover rounds to the published 38.2 MeV benchmark. This is equilibrium-model consistency with shared external inputs, not new observational evidence or a kinetic onset/end determination.')
    write_csv(ROOT/'data/resultados_50MeV_y_entorno.csv',results)
    write_csv(ROOT/'data/cruces_por_catalogo.csv',crosses)
    write_csv(ROOT/'data/sensibilidad_eta.csv',sensitivity)
    write_csv(ROOT/'data/especies_PDG2025.csv',inventories)
    write_csv(ROOT/'data/curva_R_PDG2025.csv',curve)
    (ROOT/'data/resumen.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    (ROOT/'data/validacion.json').write_text(json.dumps(dict(controls=controls,
        all_assertions_passed=True,particle_species_records=len(inventories)),indent=2)+'\n')
    provenance=dict(analysis_date='2026-10-09',python=platform.python_version(),
        numpy=np.__version__,scipy=scipy.__version__,
        catalog_commit=prior['commit'],catalog_sha256={key:prior['catalogs'][key]['sha256'] for key in CATALOGS},
        requested_point_MeV=50,curve_range_MeV=[37,50],crossover_bracket_MeV=[37,40],
        quantum_series_terms=[96,192],mu_Q=0,mu_S=0,
        cosmological_inputs=dict(eta=ETA,eta_sigma=ETA_SIGMA,s_per_present_photon=S_PER_PHOTON,Y_net=Y_NET),
        numerical_methods='Nested Brent roots for muB/T and R(T)=1; stable pair sinh/cosh sums; 96/192 term convergence and independent momentum quadrature.',
        primary_reference=dict(authors='Cheng Tao Yang and Johann Rafelski',year=2022,
            title='Cosmological strangeness abundance',journal='Physics Letters B 827, 136944',
            doi='10.1016/j.physletb.2022.136944',url='https://arxiv.org/pdf/2108.01752',
            published_pdf='https://scoap3-prod-backend.s3.cern.ch/media/files/67970/10.1016/j.physletb.2022.136944.pdf',
            reference_temperature_MeV=38.2,reference_precision='One decimal; temperature uncertainty not quoted for this point.',
            reference_criterion='n_antibaryon/(n_baryon-n_antibaryon)=1',
            differences='Their calculation includes charge and strangeness neutrality and a reduced hadronic inventory; ours uses full catalogs with muQ=muS=0. Their central net yield is 0.865e-10 versus ours 0.86931818e-10.'),
        fifty_context=dict(citation='Satarov, Mishustin and Greiner (2013), Phys. Rev. C 88, 024908',
            doi='10.1103/PhysRevC.88.024908',url='https://arxiv.org/pdf/1305.4046',
            meaning='Below about 50 MeV their calculated relative antibaryon abundance decreases rapidly; this is not the R=1 criterion.'),
        scope=summary['conclusion'])
    (ROOT/'provenance_50MeV.json').write_text(json.dumps(provenance,indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.8})
    fig,(ax,zoom)=plt.subplots(1,2,figsize=(9.8,4.4),gridspec_kw={'width_ratios':[1.45,1]})
    xx=np.array([r['T_MeV'] for r in curve]);yy=np.array([r['R_antibaryon_to_net'] for r in curve])
    ax.plot(xx,yy,color='#205493',lw=2,label='HRG PDG2025')
    ax.axhline(1,color='#333333',ls='--',lw=1,label='Criterio de cruce: R = 1')
    ax.scatter([50],[p50['R_antibaryon_to_net']],color='#d46b27',s=36,zorder=4)
    ax.annotate('50 MeV: R = 306.11',xy=(50,p50['R_antibaryon_to_net']),xytext=(44,125),fontsize=9)
    ax.scatter([tx],[1],color='#205493',s=30,zorder=4)
    ax.set(yscale='log',xlim=(36.8,50.6),ylim=(.3,500),xlabel='Temperatura T (MeV)',ylabel=r'$R=n_{\bar B}/(n_B-n_{\bar B})$')
    ax.grid(axis='y',alpha=.16);ax.legend(loc='upper left',frameon=False,fontsize=8.5)
    zcurve=[]
    for tm in np.linspace(38.1,38.3,61):
        st,_=solve(rows,float(tm));zcurve.append(st['R_antibaryon_to_net'])
    zx=np.linspace(38.1,38.3,61)
    zoom.plot(zx,zcurve,color='#205493',lw=2)
    zoom.axhline(1,color='#333333',ls='--',lw=1)
    zoom.axvspan(tlo,thi,color='#205493',alpha=.12,label=r'Variación de $\eta\pm\sigma_\eta$')
    zoom.axvline(REFERENCE_MEV,color='#d46b27',ls=':',lw=1.7,label='Referencia: 38.2 MeV')
    zoom.scatter([tx],[1],color='#205493',s=30,zorder=4,label='Cruce HRG: 38.204 MeV')
    zoom.set(xlim=(38.1,38.3),ylim=(.92,1.09),xlabel='Temperatura T (MeV)',ylabel='R cerca del cruce')
    zoom.ticklabel_format(useOffset=False,axis='x');zoom.grid(axis='y',alpha=.16)
    zoom.legend(loc='upper left',frameon=False,fontsize=8)
    fig.suptitle('Población de antibariones frente al exceso neto bariónico',fontsize=12,y=.97)
    fig.subplots_adjust(bottom=.2,top=.84,wspace=.3)
    fig.text(.08,.06,'Figura 1. Equilibrio HRG con rendimiento neto cosmológico impuesto. La banda varía sólo η;\nno representa la incertidumbre física total. El cruce R = 1 no implica ausencia de antibariones.',fontsize=8.5,ha='left')
    fig.savefig(ROOT/'figures/cruce_50MeV.png',dpi=220)
    fig.savefig(ROOT/'figures/cruce_50MeV.svg')
    plt.close(fig)
    print(json.dumps(dict(at50=p50,at38p2=p38,crossovers=crosses,
        eta_only_sensitivity=sensitivity,nucleon_shares=nus,
        validation_assertions='PASSED',species_records=len(inventories)),indent=2))


if __name__=='__main__':main()
