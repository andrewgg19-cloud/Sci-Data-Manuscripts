"""Conditional HRG sensitivity around the published QCD crossover reference."""
import json
from infer_early_populations import infer,parse_list,ROOT,GEV3_TO_CM3
from reproduce_hrg import write_csv

TEMPERATURES_INITIAL=[150.,155.,156.5,158.]
rows_out=[]
controls={}
for key in ['PDG2014','PDG2020','PDG2025']:
    catalog=parse_list(ROOT/'catalogs'/f'{key}_list.dat')
    largest=0.
    for tm in TEMPERATURES_INITIAL:
        st,_=infer(catalog,tm/1000)
        more,_=infer(catalog,tm/1000,kmax=192)
        err=max(abs(st['Y_sum']/more['Y_sum']-1),abs(st['muB_over_T']/more['muB_over_T']-1))
        largest=max(largest,err)
        rows_out.append(dict(catalog=key,T_MeV=tm,T_K=tm*1e6/8.617333262e-5,
            n_B_cm3=st['n_B_GeV3']*GEV3_TO_CM3,n_antiB_cm3=st['n_antiB_GeV3']*GEV3_TO_CM3,
            n_net_cm3=st['n_net_GeV3']*GEV3_TO_CM3,n_sum_cm3=st['n_sum_GeV3']*GEV3_TO_CM3,
            muB_over_T=st['muB_over_T'],Y_sum=st['Y_sum'],Y_net=st['Y_net'],
            total_to_net_yield_ratio=st['Y_sum']/st['Y_net'],
            role='150 MeV main-grid starting point; 155-158 MeV crossover-reference sensitivity only.'))
    assert largest<1e-10
    controls[key]=dict(maximum_relative_solution_change_k96_to192=largest)
write_csv(ROOT/'data'/'initial_temperature_sensitivity.csv',rows_out)
central=next(r for r in rows_out if r['catalog']=='PDG2025' and r['T_MeV']==156.5)
base=next(r for r in rows_out if r['catalog']=='PDG2025' and r['T_MeV']==150.)
refs=dict(reference_temperature_MeV=156.5,reference_uncertainty_MeV=1.5,
    source='Bazavov et al. (HotQCD Collaboration), Physics Letters B 795 (2019) 15-21',
    doi='10.1016/j.physletb.2019.05.013',url='https://arxiv.org/pdf/1812.08235',
    source_role='Lattice-QCD chiral crossover estimate at zero chemical potentials; theoretical reference for the emergence of hadrons, not a measured annihilation onset.',
    assumptions='Same ideal-HRG inverse constraint and central cosmological inputs; mu_Q=mu_S=0. Numerical evaluation near the crossover is a sensitivity check, not a validated replacement for the QCD equation of state.',
    main_grid_start_MeV=150.,kelvin_conversion='T_K=T_MeV*1e6/k_B, k_B=8.617333262e-5 eV/K',
    central_reference_result=central,
    central_reference_vs150_density_change_pct=100*(central['n_sum_cm3']/base['n_sum_cm3']-1),
    central_reference_vs150_yield_change_pct=100*(central['Y_sum']/base['Y_sum']-1),
    controls=controls)
(ROOT/'data'/'initial_temperature_reference.json').write_text(json.dumps(refs,indent=2)+'\n')
print(json.dumps(refs,indent=2))
print(json.dumps([r for r in rows_out if r['catalog']=='PDG2025'],indent=2))
