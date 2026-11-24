"""Compare the new thermal implementation to the rerun original HRG audit."""
import json,csv
from pathlib import Path
from termica import HRG
P=Path(__file__).resolve().parent
rows=list(csv.DictReader((P/'original_hrg/data/resultados_50MeV_y_entorno.csv').open()))
checks=[]
for cat in ['PDG2014','PDG2020','PDG2025']:
 h=HRG(cat)
 for T in [37.,38.2,40.,45.,50.]:
  old=next(x for x in rows if x['catalog']==cat and float(x['T_MeV'])==T)
  st=h.equilibrium(T)
  checks.append(dict(catalog=cat,T_MeV=T,nB_relative=st['nB']/float(old['n_B_cm3'])-1,nanti_relative=st['nanti']/float(old['n_antiB_cm3'])-1,delta_relative=st['delta']/float(old['n_net_cm3'])-1,R_relative=st['R']/float(old['R_antibaryon_to_net'])-1))
error=max(abs(v) for row in checks for k,v in row.items() if k.endswith('_relative'))
assert error<1e-8
(P/'resultados/comparacion_independiente.json').write_text(json.dumps(dict(checks=checks,maximum_relative_error=error),indent=2,allow_nan=False))
print(error)
