from pathlib import Path
import sys,json,hashlib,csv
import numpy as np
from scipy.optimize import brentq
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent))
import simular as model
from termica import HRG,TARGET
OUT=P/'resultados';OUT.mkdir(exist_ok=True)
HEADER='time_since_50MeV_s,T_MeV,a,nB_cm-3,nanti_cm-3,delta_cm-3,s_over_kB_cm-3,Ynet,S_over_Sinitial,S_integrated_over_Sinitial,R_antibaryon_over_net'

def writecsv(path,rows):
 with path.open('w',newline='') as stream:
  w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def configure(eos,mass):
 grid,rs,ps,bs=eos
 model.rhoS=rs;model.pS=ps
 def bzero(T):
  if not grid[0]<=T<=grid[-1]:raise ValueError('Temperature outside validated HRG grid')
  return float(np.exp(bs(T)))
 model.bzero=bzero;model.r0=float(rs(50));model.s0=float(model.entropy(50))
 model.M0=mass;model.life=mass**3/(3*model.alpha)

def runpair(eos,mass,f,save=True,rtol=2e-7):
 configure(eos,mass)
 # One common initial yield, not one common physical density, for comparison
 # across thermal backgrounds. Refit only for the final-yield protocol.
 delta_common=TARGET*model.s0
 baseline,data=model.run(f,rtol=rtol,delta_initial=delta_common)
 if baseline['T_after_evap_MeV']<30:raise RuntimeError('Evaporation outlasts selected endpoint')
 delta_norm=TARGET*model.s0*baseline['Sfinal_over_Sinitial']
 normalized,dnorm=model.run(f,rtol=rtol,delta_initial=delta_norm)
 error=normalized['Ynet_final']/TARGET-1
 assert abs(error)<2e-6
 row=dict(M_initial_g=mass,f=f,S_final_over_initial=normalized['Sfinal_over_Sinitial'],
  Y_initial=normalized['Ynet_initial'],delta_initial_cm3=delta_norm,Y_final=normalized['Ynet_final'],
  crossing_common_initial_MeV=baseline['crossings_MeV'][-1],crossing_common_final_MeV=normalized['crossings_MeV'][-1],
  all_crossings_initial_MeV=json.dumps(baseline['crossings_MeV']),all_crossings_final_MeV=json.dumps(normalized['crossings_MeV']),
  target_relative_error=error,T_after_evap_MeV=normalized['T_after_evap_MeV'],max_temperature_MeV=normalized['max_T_MeV'],
  entropy_balance_error=normalized['max_entropy_balance_relative_error'])
 if save:
  name=f'M{mass:.0f}_f{f:g}'
  np.savetxt(OUT/f'{name}_inicial.csv',data,delimiter=',',header=HEADER,comments='')
  np.savetxt(OUT/f'{name}_final.csv',dnorm,delimiter=',',header=HEADER,comments='')
 return row

def main():
 prov=json.loads((P/'original_hrg/provenance_50MeV.json').read_text())
 for cat,sha in prov['catalog_sha256'].items():
  assert hashlib.sha256((P/'original_hrg/catalogs'/f'{cat}_list.dat').read_bytes()).hexdigest()==sha
 models={cat:HRG(cat) for cat in ['PDG2014','PDG2020','PDG2025']}
 thermal=[]
 for cat,h in models.items():
  for neutral in [False,True]:
   cross=brentq(lambda T:h.equilibrium(T,neutral=neutral)['R']-1,37,40,xtol=1e-9)
   for T in [30.,37.,38.2,float(cross),40.,45.,50.]:
    st=h.equilibrium(T,neutral=neutral)
    thermal.append(dict(catalog=cat,neutral=neutral,T_MeV=T,is_crossing=T==cross,
      Y=st['Y'],R=st['R'],nB=st['nB'],nanti=st['nanti'],s=st['s'],rho=st['rho'],
      alphaB=st['alpha'][0],alphaQ=st['alpha'][1],alphaS=st['alpha'][2],alphaLe=st['alpha'][3],alphaLmu=st['alpha'][4],
      charge_over_delta=st['charges'][1]/st['delta'],strangeness_over_delta=st['charges'][2]/st['delta'],
      Le_over_delta=st['charges'][3]/st['delta'],Lmu_over_delta=st['charges'][4]/st['delta']))
   print('equilibrium',cat,neutral,cross,flush=True)
 writecsv(OUT/'equilibrio_y_neutralidad.csv',thermal)
 h=models['PDG2025'];eos=h.background()
 checks=[]
 for T in [30,37.13,38.2,39.26,45,50,60]:
  rs,ps,bs=eos[1:];st=h.state(T);st128=h.state(T,kmax=128)
  checks.append(dict(T_MeV=T,rho_interp_relative=rs(T)/st['rho']-1,
   b_interp_relative=np.exp(bs(T))/st['nB']-1,
   rho_series_relative=st['rho']/st128['rho']-1,b_series_relative=st['nB']/st128['nB']-1,
   thermodynamic_identity_relative=(rs(T,1)-(rs(T,1)+ps(T,1)-(rs(T)+ps(T))/T))/rs(T,1)))
 rows=[]
 for mass in [7e7,8.5e7,1e8]:
  for f in [0,.01,.1,1]:
   row=runpair(eos,mass,f);rows.append(row);print('kinetics',json.dumps(row),flush=True)
 writecsv(OUT/'barrido_masa_abundancia.csv',rows)
 catalog_rows=[]
 for cat in ['PDG2014','PDG2020']:
  ec=models[cat].background()
  for f in [0,1]:
   row=runpair(ec,1e8,f,save=False);row['catalog']=cat;catalog_rows.append(row)
 for r in rows:
  if r['M_initial_g']==1e8 and r['f'] in [0,1]:catalog_rows.append(dict(**r,catalog='PDG2025'))
 writecsv(OUT/'sensibilidad_catalogos.csv',catalog_rows)
 tight=runpair(eos,1e8,1,save=False,rtol=2e-8)
 fine=runpair(h.background(1601),1e8,1,save=False)
 baseline=rows[-1]
 conv={name:{key:val[key]-baseline[key] for key in ['S_final_over_initial','crossing_common_initial_MeV','crossing_common_final_MeV']} for name,val in [('tolerance',tight),('grid',fine)]}
 # Finite-chemical-potential and neutrality equilibrium diagnostics of the test bath.
 chem=[]
 for T in [30,37,38.2,40,45,50]:
  st=h.equilibrium(T,neutral=True);zero=h.state(T);st128=h.equilibrium(T,neutral=True,kmax=128)
  chem.append(dict(T_MeV=T,rho_chemical_relative=st['rho']/zero['rho']-1,
   s_chemical_relative=st['s']/zero['s']-1,neutrality_error=st['neutrality_residual_over_delta'],
   nB_series_change=st['nB']/st128['nB']-1,nanti_series_change=st['nanti']/st128['nanti']-1,
   equilibrium_product_relative_to_zero_mu=st['nB']*st['nanti']/zero['nB']**2-1))
 assert max(abs(v['rho_interp_relative']) for v in checks)<1e-7
 assert max(abs(v['b_interp_relative']) for v in checks)<1e-7
 assert max(abs(v['rho_series_relative']) for v in checks)<1e-10
 assert max(v['neutrality_error'] for v in chem)<1e-7
 assert abs(conv['grid']['crossing_common_final_MeV'])<1e-4
 output=dict(catalog_commit=prov['catalog_commit'],catalog_sha256=prov['catalog_sha256'],
  target_yield=TARGET,kinetic_scope='Full zero-mu HRG background, equilibrium-product kinetic closure, pairs remain a test sector; neutrality solved as separate equilibrium control only.',
  neutrality_assumptions='Net electric charge=0, net strangeness=0, Le=Lmu=Ltau=0; massless e and neutrinos, massive muons; no tau charged lepton.',
  interpolation_checks=checks,chemical_diagnostics=chem,convergence=conv,baseline_full_hrg=baseline,
  scan=rows,catalog_sensitivity=catalog_rows)
 (OUT/'validacion_y_resumen.json').write_text(json.dumps(output,indent=2,allow_nan=False))
 print('COMPLETE',json.dumps(output),flush=True)
if __name__=='__main__':main()
