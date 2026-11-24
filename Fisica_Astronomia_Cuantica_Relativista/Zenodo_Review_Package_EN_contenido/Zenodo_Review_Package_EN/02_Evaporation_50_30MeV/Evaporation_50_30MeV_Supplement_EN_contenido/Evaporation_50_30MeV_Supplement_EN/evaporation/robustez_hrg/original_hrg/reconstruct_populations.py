"""Reconstruct equilibrium particle number densities and a conditional cosmic ledger.

This is a static ideal-HRG calculation, not a kinetic regeneration simulation.
Cosmic means use measured eta, T_CMB and primordial helium as external inputs.
"""
from pathlib import Path
import json, math
import numpy as np
from scipy.special import kv, zeta, expit
from scipy.integrate import quad
from reproduce_hrg import ROOT, TEMPERATURES, KMAX, parse_list, evaluate, write_csv

HBARC_GEV_CM = 1.973269804e-14
GEV3_TO_CM3 = HBARC_GEV_CM**-3
KB_GEV_K = 8.617333262e-14
TCMB_K, TCMB_SIGMA_K = 2.7255, 0.0006
ETA, ETA_SIGMA = 6.12e-10, 0.04e-10
S_PER_PHOTON = 7.04
HELIUM_BARYON_FRACTION, HELIUM_SIGMA = 0.245, 0.003
D_OVER_H, D_OVER_H_SIGMA = 2.508e-5, 0.029e-5
Y_NET = ETA/S_PER_PHOTON

def number_over_T3(mass, g, stat, T, kmax=KMAX):
    """One particle species; its antiparticle is handled explicitly by the caller."""
    x=mass/T
    if x==0:
        return g*float(zeta(3,1))/math.pi**2*(0.75 if stat==1 else 1.)
    k=np.arange(1,kmax+1,dtype=float)
    signs=(-1.)**(k+1) if stat==1 else np.ones_like(k)
    return g*x*x/(2*math.pi**2)*float(np.sum(signs*kv(2,k*x)/k))

def integral_number_over_T3(mass,g,stat,T):
    x=mass/T
    def integrand(q):
        E=math.hypot(q,x)
        if E==0:return 0.
        occ=expit(-E) if stat==1 else (0. if E>700 else 1/math.expm1(E))
        return q*q*occ
    val,_=quad(integrand,0,np.inf,epsabs=1e-15,epsrel=5e-12,limit=200)
    return g/(2*math.pi**2)*val

def cosmic_reference():
    ng=number_over_T3(0.,2.,-1,TCMB_K*KB_GEV_K)*(TCMB_K*KB_GEV_K)**3*GEV3_TO_CM3
    sg=S_PER_PHOTON*ng
    nb=ETA*ng
    rel_ng=3*TCMB_SIGMA_K/TCMB_K
    sigma_nb=nb*math.hypot(ETA_SIGMA/ETA,rel_ng)
    nh=(1-HELIUM_BARYON_FRACTION)*nb
    nhe=HELIUM_BARYON_FRACTION*nb/4
    sig_nh=nh*math.hypot(sigma_nb/nb,HELIUM_SIGMA/(1-HELIUM_BARYON_FRACTION))
    sig_nhe=nhe*math.hypot(sigma_nb/nb,HELIUM_SIGMA/HELIUM_BARYON_FRACTION)
    nd=D_OVER_H*nh
    sig_nd=nd*math.hypot(sig_nh/nh,D_OVER_H_SIGMA/D_OVER_H)
    return dict(T_CMB_K=TCMB_K,T_CMB_sigma_K=TCMB_SIGMA_K,eta=ETA,eta_sigma=ETA_SIGMA,
        helium_baryon_fraction=HELIUM_BARYON_FRACTION,helium_sigma=HELIUM_SIGMA,
        D_over_H=D_OVER_H,D_over_H_sigma=D_OVER_H_SIGMA,
        n_gamma0_cm3=ng,n_gamma0_sigma_cm3=ng*rel_ng,s0_cm3=sg,
        Y_net_external=Y_NET,Y_net_external_sigma=ETA_SIGMA/S_PER_PHOTON,
        n_baryon0_cm3=nb,n_baryon0_sigma_cm3=sigma_nb,
        n_H_nuclei_primordial_composition_equivalent_cm3=nh,n_H_sigma_cm3=sig_nh,
        n_He4_nuclei_primordial_composition_equivalent_cm3=nhe,n_He4_sigma_cm3=sig_nhe,
        n_D_nuclei_primordial_composition_equivalent_cm3=nd,n_D_sigma_cm3=sig_nd,
        approximation="Mean primordial-composition equivalent scaled to today's volume; no stellar processing, neutral fraction or nuclear-network prediction. H/He formula neglects trace nuclides and binding-energy corrections.",
        uncertainty_method="First-order independent-input propagation of eta, T_CMB, helium and D/H; output errors share inputs and are correlated, no likelihood or HRG physical uncertainty inferred.")

def main():
    cosmic=cosmic_reference()
    populations=[]; species=[]; validation={}; nucleons=[]
    for key in ['PDG2014','PDG2020','PDG2025']:
        rows=parse_list(ROOT/'catalogs'/f'{key}_list.dat')
        assert all(r['B'] in (0,1) for r in rows if r['g']>0)
        max_k=0.
        for tm in TEMPERATURES:
            T=tm/1000
            d=evaluate(rows,T)
            nb=0.;nanti=0.;nm=0.;nhad192=0.;nhad96=0.
            for r in rows:
                if r['g']<=0:continue
                ni=number_over_T3(r['m'],r['g'],r['stat'],T)*T**3
                ni192=number_over_T3(r['m'],r['g'],r['stat'],T,192)*T**3
                nhad96+=ni*r['multiplicity'];nhad192+=ni192*r['multiplicity']
                max_k=max(max_k,abs(ni/ni192-1))
                if r['B']==1:nb+=ni;nanti+=ni
                else:nm+=ni*r['multiplicity']
                if key=='PDG2025':
                    for conjugate in range(r['multiplicity']):
                        sign=1 if conjugate==0 else -1
                        species.append(dict(T_MeV=tm,pdg_id=sign*r['pdg'],name=r['name'] if conjugate==0 else 'anti('+r['name']+')',
                            B=sign*r['B'],Q=sign*r['Q'],S=sign*r['S'],spin_degeneracy=r['g'],
                            mass_GeV=r['m'],n_GeV3=ni,n_cm3=ni*GEV3_TO_CM3,
                            Y_i=ni/d['s_total_GeV3']))
                    if r['pdg'] in (2212,2112):
                        nucleons.append(dict(T_MeV=tm,pdg_id=r['pdg'],name=r['name'],
                            n_particle_cm3=ni*GEV3_TO_CM3,n_antiparticle_cm3=ni*GEV3_TO_CM3,
                            share_of_all_baryons=0.))
            ng=number_over_T3(0.,2.,-1,T)*T**3
            nsum=nb+nanti;ysum=nsum/d['s_total_GeV3']
            alpha=math.asinh(Y_NET*d['s_total_GeV3']/nsum)
            populations.append(dict(T_MeV=tm,catalog=key,
                n_B_GeV3=nb,n_antiB_GeV3=nanti,n_sum_GeV3=nsum,
                n_B_cm3=nb*GEV3_TO_CM3,n_antiB_cm3=nanti*GEV3_TO_CM3,
                n_pairs_bookkeeping_cm3=min(nb,nanti)*GEV3_TO_CM3,n_sum_cm3=nsum*GEV3_TO_CM3,
                n_meson_cm3=nm*GEV3_TO_CM3,n_hadron_cm3=(nsum+nm)*GEV3_TO_CM3,
                n_gamma_cm3=ng*GEV3_TO_CM3,s_total_cm3=d['s_total_GeV3']*GEV3_TO_CM3,
                Y_sum_equilibrium=ysum,Y_B_equilibrium=ysum/2,Y_antiB_equilibrium=ysum/2,
                Y_net_equilibrium=0.,Y_net_external=Y_NET,
                equilibrium_sum_to_external_net_ratio=ysum/Y_NET,
                equilibrium_pairs_to_external_net_ratio=ysum/(2*Y_NET),
                n_net_external_cm3=Y_NET*d['s_total_GeV3']*GEV3_TO_CM3,
                muB_over_T_MB_diagnostic=alpha,
                mean_N_B_per_today_cm3_adiabatic=ysum/2*cosmic['s0_cm3'],
                mean_N_antiB_per_today_cm3_adiabatic=ysum/2*cosmic['s0_cm3'],
                mean_N_net_per_today_cm3_external=cosmic['n_baryon0_cm3'],
                physical_volume_per_today_cm3_adiabatic=cosmic['s0_cm3']/(d['s_total_GeV3']*GEV3_TO_CM3)))
            assert math.isclose(nsum,2*nb,rel_tol=1e-14) and nb>0
            assert math.isclose(nhad96,nsum+nm,rel_tol=1e-14)
            assert math.isclose(ysum*cosmic['s0_cm3'],nsum*GEV3_TO_CM3*populations[-1]['physical_volume_per_today_cm3_adiabatic'],rel_tol=1e-13)
        validation[key]={'maximum_relative_number_change_k96_to192_per_species':max_k}
    # Finish nucleon fractions after all baryonic species have been summed.
    for r in nucleons:
        d=next(x for x in populations if x['catalog']=='PDG2025' and x['T_MeV']==r['T_MeV'])
        r['share_of_all_baryons']=r['n_particle_cm3']/d['n_B_cm3']
    rows=parse_list(ROOT/'catalogs/PDG2025_list.dat')
    validation['independent_number_integrals']=[]
    for tm in (150.,40.):
        for r in [x for x in rows if x['pdg'] in (111,211,2212,2112)]+[dict(pdg=13,m=.1056583755,g=4,stat=1)]:
            a=number_over_T3(r['m'],r['g'],r['stat'],tm/1000)
            b=integral_number_over_T3(r['m'],r['g'],r['stat'],tm/1000)
            validation['independent_number_integrals'].append(dict(T_MeV=tm,pdg=r['pdg'],relative_difference=abs(a/b-1)))
    validation['max_independent_number_relative_difference']=max(x['relative_difference'] for x in validation['independent_number_integrals'])
    validation['massless_photon_number_integral_relative_difference']=abs(number_over_T3(0.,2.,-1,.15)/integral_number_over_T3(0.,2.,-1,.15)-1)
    validation['baryon_antibaryon_symmetry']='Exact at mu=0 in the implementation; no nonzero net baryon yield generated.'
    assert validation['max_independent_number_relative_difference']<1e-8
    assert all(validation[k]['maximum_relative_number_change_k96_to192_per_species']<1e-10 for k in ['PDG2014','PDG2020','PDG2025'])
    series=[r for r in populations if r['catalog']=='PDG2025']
    assert all(a['Y_sum_equilibrium']>b['Y_sum_equilibrium'] for a,b in zip(series,series[1:]))
    assert len(species)==443*len(TEMPERATURES)
    validation['particle_species_records_PDG2025']=len(species)
    validation['yield_suppression_orders_PDG2025']=math.log10(series[0]['Y_sum_equilibrium']/series[-1]['Y_sum_equilibrium'])
    write_csv(ROOT/'data/particle_densities.csv',populations)
    write_csv(ROOT/'data/species_densities_PDG2025.csv',species)
    write_csv(ROOT/'data/nucleon_densities_PDG2025.csv',nucleons)
    (ROOT/'data/cosmological_reference.json').write_text(json.dumps(cosmic,indent=2)+'\n')
    (ROOT/'data/number_validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    prov=dict(density_units='GeV^3 and cm^-3',conversion_hbarc_GeV_cm=HBARC_GEV_CM,
        reconstruction='Equilibrium number densities, not a number of particles physically regenerated or annihilated.',
        thermal_initial_point_MeV=150,kinetic_annihilation_onset='Not determined by this static calculation.',
        sources=dict(eta='Fields, Molaro & Sarkar, PDG BBN review (2025), Eq. 24.8',
            T_CMB='Fixsen (2009), ApJ 707, 916-920, doi:10.1088/0004-637X/707/2/916',
            helium_and_deuterium='Fields, Molaro & Sarkar, PDG BBN review (2025), Eqs. 24.2 and 24.3',
            hbarc='Robinson & Zyla, PDG physical constants (2025), Table 1.1'),
        assumptions=dict(mu_B=0,mu_Q=0,mu_S=0,abs_B_equal_one=True,
            adiabatic_mapping='Conditional entropy-conserving comparison with an externally normalized net yield.',
            current_H='Primordial-composition equivalent at cosmic mean density, not a measurement or prediction of present neutral hydrogen.'),
        uncertainty='First-order input propagation for cosmic references only; physical model systematics not quantified.')
    (ROOT/'population_provenance.json').write_text(json.dumps(prov,indent=2)+'\n')
    print(json.dumps(dict(at150=series[0],at40=series[-1],cosmic=cosmic,validation=validation,
        nucleons_at150=[r for r in nucleons if r['T_MeV']==150]),indent=2))

if __name__=='__main__':main()
