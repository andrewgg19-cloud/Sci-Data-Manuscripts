from pathlib import Path
import json
import numpy as np
from ejecutar_robustez import HRG,configure,model,OUT
P=Path(__file__).resolve().parent
r=json.loads((OUT/'validacion_y_resumen.json').read_text())
row=next(x for x in r['scan'] if x['M_initial_g']==8.5e7 and x['f']==1)
h=HRG();eos=h.background();configure(eos,8.5e7)
base,_=model.run(1,delta_initial=row['delta_initial_cm3'])
tight,_=model.run(1,rtol=2e-8,delta_initial=row['delta_initial_cm3'])
configure(h.background(1601),8.5e7)
fine,_=model.run(1,delta_initial=row['delta_initial_cm3'])
assert len(base['crossings_MeV'])==len(tight['crossings_MeV'])==len(fine['crossings_MeV'])==3
checks={key:float(np.max(abs(np.array(st['crossings_MeV'])-base['crossings_MeV']))) for key,st in [('tolerance_max_crossing_change_MeV',tight),('grid_max_crossing_change_MeV',fine)]}
assert max(checks.values())<1e-4
out=dict(case=row,events=base['crossing_events'],checks=checks,tight_events=tight['crossing_events'],fine_grid_events=fine['crossing_events'])
(OUT/'verificacion_multicruce.json').write_text(json.dumps(out,indent=2,allow_nan=False))
print(json.dumps(out,indent=2))
